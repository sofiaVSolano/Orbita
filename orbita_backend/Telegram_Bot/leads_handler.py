# Handler para Bot de Leads — Conversaciones con prospectos
# [CRITERIO 1] Canal conversacional AIDA con memoria completa
# [CRITERIO 3] Whisper transcribe notas de voz en tiempo real

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json
import os
import tempfile
import httpx
import asyncio

from database import get_db, create_cotizacion, update_lead_status
from config import get_settings
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.conversacional import ConversacionalAgent
from agents.comunicacion import ComunicacionAgent
from utils.groq_client import get_groq_client
from utils.cotizacion_renderer import render_cotizacion_markdown
from utils.quick_estimate import get_quick_estimator


class LeadsBotHandler:
    """
    Maneja el bot público de leads (prospectos).
    
    Flujo principal:
    1. Usuario escribe al bot (texto o audio)
    2. Se identifica/crea el lead en la BD
    3. Se pasa el mensaje al Orquestador
    4. El Orquestador activa los agentes necesarios (Captador, Conversacional, etc.)
    5. Se genera y envía la respuesta
    6. Se registra todo en BD (conversations, agent_logs)
    
    Soporta:
    - Mensajes de texto
    - Notas de voz (Whisper transcription)
    - Botones inline (cotizaciones, reuniones)
    - Estados del bot (activo, pausado)
    """
    
    def __init__(self):
        self.db = get_db()
        self.settings = get_settings()
        self.groq_client = get_groq_client()
        
        # Agentes principales
        self.orchestrator = OrchestratorAgent()
        self.captador = CaptadorAgent()
        self.conversacional = ConversacionalAgent()
        self.comunicacion = ComunicacionAgent()
        
        # Estimador de precios rápido
        self.quick_estimator = get_quick_estimator()
    
    # ─── ROUTER PRINCIPAL ──────────────────────────────────────
    
    async def handle_update(self, update: Update, bot: Bot):
        """
        Punto de entrada de todos los updates del bot de leads.
        Distribuye según el tipo de update.
        """
        try:
            # Callbacks de botones inline
            if update.callback_query:
                await self._handle_callback(update.callback_query, bot)
                return
            
            # Mensajes de texto o voz
            if update.message:
                await self._handle_message(update.message, bot)
                return
                
        except Exception as e:
            print(f"❌ [LeadsBotHandler] Error: {e}")
            # Intentar enviar mensaje de error al usuario
            if update.message:
                try:
                    await bot.send_message(
                        chat_id=update.message.chat_id,
                        text="Disculpa, hubo un problema técnico. Por favor intenta de nuevo en un momento."
                    )
                except:
                    pass
    
    # ─── MANEJO DE MENSAJES ────────────────────────────────────
    
    async def _handle_message(self, message, bot: Bot):
        """Procesa mensajes de texto o voz."""
        chat_id = str(message.chat_id)
        user = message.from_user
        
        # Verificar si el bot está pausado para este lead
        if await self._esta_pausado(chat_id):
            # No responder automáticamente si está pausado
            return
        
        # Determinar el contenido
        texto = None
        content_type = "text"
        
        if message.text:
            texto = message.text
            content_type = "text"
        elif message.voice:
            # Transcribir nota de voz con Whisper
            texto = await self._transcribir_voz(message.voice, bot)
            content_type = "voice"
            if not texto:
                await bot.send_message(
                    chat_id=chat_id,
                    text="No pude procesar tu nota de voz. ¿Podrías escribir tu mensaje?"
                )
                return
        else:
            # Otro tipo de mensaje no soportado
            await bot.send_message(
                chat_id=chat_id,
                text="Por ahora solo puedo procesar mensajes de texto y notas de voz. 😊"
            )
            return
        
        # Comandos especiales
        if texto.startswith("/"):
            await self._handle_command(texto, chat_id, user, bot)
            return
        
        # Obtener o crear lead
        lead = await self._get_or_create_lead(chat_id, user)
        if not lead:
            await bot.send_message(
                chat_id=chat_id,
                text="Hubo un problema registrando tu información. Por favor intenta de nuevo."
            )
            return
        
        lead_id = lead["id"]
        
        # Guardar mensaje del usuario en conversaciones
        await self._guardar_mensaje(lead_id, "user", texto, content_type)
        
        # Obtener contexto de conversación
        contexto = await self._obtener_contexto(lead_id)
        
        # Procesar con el Orquestador
        typing_task = None
        try:
            # Indicar que el bot está escribiendo
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Llamar al orquestador con el mensaje y contexto
            resultado = await self._procesar_con_agentes(
                mensaje=texto,
                lead_id=lead_id,
                chat_id=chat_id,
                contexto=contexto,
                content_type=content_type
            )
            
            respuesta = resultado.get("respuesta", "¿En qué más puedo ayudarte?")
            botones = resultado.get("botones", None)
            
            # Guardar respuesta del bot
            agente_usado = resultado.get("agente", "conversacional")
            await self._guardar_mensaje(lead_id, "assistant", respuesta, "text", agente_usado)
            
            # Enviar respuesta (intentar con Markdown, si falla enviar como texto plano)
            try:
                if botones:
                    keyboard = InlineKeyboardMarkup(botones)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=respuesta,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
                else:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=respuesta,
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as markdown_error:
                # Si falla el Markdown, enviar como texto plano
                print(f"⚠️ Error con Markdown, enviando como texto plano: {markdown_error}")
                if botones:
                    keyboard = InlineKeyboardMarkup(botones)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=respuesta,
                        reply_markup=keyboard
                    )
                else:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=respuesta
                    )
            
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text="Disculpa, tuve un problema procesando tu mensaje. ¿Podrías reformularlo?"
            )
    
    # ─── PROCESAMIENTO CON AGENTES ─────────────────────────────
    
    async def _procesar_con_agentes(
        self,
        mensaje: str,
        lead_id: str,
        chat_id: str,
        contexto: list,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Procesa el mensaje usando el sistema de agentes.
        
        1. Orquestador decide qué hacer
        2. Detecta automáticamente si el usuario está pidiendo un servicio
        3. Si hay servicio detectado, genera estimado de precio
        4. Genera botones apropiados basados en contexto
        """
        try:
            # Construir el input para el orquestador
            input_data = {
                "mensaje": mensaje,
                "lead_id": lead_id,
                "chat_id": chat_id,
                "contexto": contexto[-10:] if contexto else [],  # Últimos 10 mensajes
                "content_type": content_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # El orquestador decide qué agentes activar
            # y coordina la respuesta
            resultado_orchestrator = await self.orchestrator.process_message(
                message=mensaje,
                session_id=lead_id,
                context=input_data
            )
            
            # Extraer la respuesta generada
            respuesta = resultado_orchestrator.get(
                "response", 
                "Gracias por tu mensaje. ¿En qué puedo ayudarte?"
            )
            
            # ★ NUEVO: Detectar automáticamente servicios solicitados
            servicio_detectado, confianza = self.quick_estimator.detectar_servicio(mensaje)
            estimado = None
            respuesta_con_estimado = respuesta
            
            if servicio_detectado and confianza > 0.5:
                # Generar estimado rápido
                estimado = self.quick_estimator.generar_estimado(
                    servicio=servicio_detectado,
                    detalles_adicionales=mensaje,
                    nivel_complejidad=self._detectar_complejidad(mensaje)
                )
                
                if estimado:
                    # Agregar el estimado a la respuesta
                    mensaje_estimado = self.quick_estimator.formatear_estimado(estimado)
                    respuesta_con_estimado = f"{respuesta}\n\n{mensaje_estimado}"
                    
                    print(f"✅ Servicio detectado: {estimado['nombre_servicio']} (confianza: {confianza:.2%})")
            
            # Determinar si necesita botones especiales
            botones = await self._generar_botones_si_necesario(
                mensaje, lead_id, resultado_orchestrator, 
                servicio_detectado=servicio_detectado,
                estimado=estimado
            )
            
            return {
                "respuesta": respuesta_con_estimado,
                "botones": botones,
                "agente": resultado_orchestrator.get("agent", "orchestrator"),
                "metadatos": {
                    **resultado_orchestrator,
                    "servicio_detectado": servicio_detectado,
                    "confianza_deteccion": confianza,
                    "estimado": estimado
                }
            }
            
        except Exception as e:
            print(f"❌ Error en procesamiento con agentes: {e}")
            # Fallback: respuesta simple sin IA
            return {
                "respuesta": (
                    "Gracias por tu mensaje. En este momento tengo problemas técnicos, "
                    "pero he registrado tu consulta. Te contactaré pronto."
                ),
                "botones": None,
                "agente": "fallback",
                "metadatos": {"error": str(e)}
            }
    
    def _detectar_complejidad(self, mensaje: str) -> str:
        """Detecta el nivel de complejidad basado en el mensaje."""
        mensaje_lower = mensaje.lower()
        
        # Palabras de baja complejidad
        if any(w in mensaje_lower for w in ["simple", "básico", "sencillo", "pequeño"]):
            return "simple"
        
        # Palabras de alta complejidad
        if any(w in mensaje_lower for w in ["complejo", "avanzado", "múltiples", "integraciones", "customizado"]):
            return "complejo"
        
        return "standard"
    
    # ─── COMANDOS ──────────────────────────────────────────────
    
    async def _handle_command(self, texto: str, chat_id: str, user, bot: Bot):
        """Maneja comandos como /start."""
        cmd = texto.split()[0].lower()
        
        if cmd == "/start":
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"👋 ¡Hola {user.first_name}!\n\n"
                    f"Soy el asistente virtual de *{self.settings.empresa_nombre}*.\n\n"
                    f"Estoy aquí para ayudarte con:\n"
                    f"• Información sobre nuestros servicios\n"
                    f"• Cotizaciones personalizadas\n"
                    f"• Agendar reuniones\n\n"
                    f"Escribe tu consulta o envíame una nota de voz. 🎤"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Tratar otros comandos como mensaje normal
            await self._handle_message_text(texto, chat_id, user, bot)
    
    # ─── CALLBACKS (BOTONES INLINE) ────────────────────────────
    
    async def _handle_callback(self, callback_query, bot: Bot):
        """Procesa clicks en botones inline."""
        data = callback_query.data
        chat_id = str(callback_query.message.chat_id)
        message_id = callback_query.message.message_id
        
        await callback_query.answer()
        
        try:
            if data.startswith("cotizacion_"):
                await self._handle_cotizacion_callback(data, chat_id, bot)
            
            elif data.startswith("reunion_"):
                await self._handle_reunion_callback(data, chat_id, bot)
            
            elif data.startswith("plan_"):
                await self._handle_plan_callback(data, chat_id, message_id, bot)
            
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Opción no reconocida. Por favor intenta de nuevo."
                )
                
        except Exception as e:
            print(f"❌ Error en callback: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text="Hubo un problema procesando tu solicitud."
            )
    
    async def _handle_cotizacion_callback(self, data: str, chat_id: str, bot: Bot):
        """Maneja solicitudes de cotización desde botones."""
        # Formatos cortos para cumplir límite Telegram (64 chars):
        # - "cot_int_<lead_id>" → cotización interes (NUEVO)
        # - "cot_env_<lead_id>" → cotización enviar (NUEVO)
        # - "cotizacion_aceptar_<lead_id>" → aceptar (legacy)
        # - "cotizacion_rechazar_<lead_id>" → rechazar (legacy)
        
        partes = data.split("_")
        if len(partes) < 2:
            return
        
        accion_corta = "_".join(partes[0:2])  # "cot_int", "cot_env", "cotizacion_aceptar", etc.
        
        # Extraer lead_id (puede estar en diferentes posiciones)
        lead_id = None
        if len(partes) >= 3 and partes[0].startswith("cot"):  # Formato corto
            try:
                lead_id = int(partes[2])
            except (ValueError, IndexError):
                pass
        elif len(partes) >= 3:  # Formato legacy
            try:
                lead_id = int(partes[2])
            except (ValueError, IndexError):
                pass
        
        if not lead_id:
            return
        
        # ★ NUEVO: Manejo del callback "cot_int" (cotización interes)
        if accion_corta == "cot_int":
            print(f"✅ Usuario interesado en cotización (lead {lead_id})")
            
            # Recuperar servicio guardado en BD
            try:
                lead_result = self.db.table("leads").select("interes").eq("id", lead_id).execute()
                servicio = None
                if lead_result.data:
                    servicio = lead_result.data[0].get("interes")
                
                # Generar cotización automática
                await self._generar_cotizacion_interes(
                    lead_id=str(lead_id),
                    servicio=servicio or "sitio_web",  # default
                    chat_id=chat_id,
                    bot=bot
                )
            except Exception as e:
                print(f"❌ Error en cot_int: {e}")
                await bot.send_message(
                    chat_id=chat_id,
                    text="Hubo un error procesando tu solicitud. Por favor intenta de nuevo."
                )
            return
        
        # ★ NUEVO: Manejo del callback "cot_env" (cotización enviar)
        if accion_corta == "cot_env":
            print(f"⭐ Usuario solicita enviar detalles (lead {lead_id})")
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "📧 ¿A qué correo quieres que envíe los detalles?\\n\\n"
                    "Por favor proporciona tu correo electrónico."
                )
            )
            return
        
        # Legacy: formatos antiguos
        if "aceptar" in data:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "¡Excelente! 🎉\\n\\n"
                    "¿Cuándo te gustaría que agendemos una reunión para revisar los detalles?"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            self.db.table("leads").update(
                {"status": "cotizado"}
            ).eq("id", lead_id).execute()
        
        elif "rechazar" in data:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "Entiendo. ¿Hay algo específico que no se ajusta a tus necesidades? "
                    "Puedo ajustar la propuesta."
                )
            )
    
    async def _generar_cotizacion_interes(
        self,
        lead_id: str,
        servicio: str,
        chat_id: str,
        bot: Bot
    ):
        """
        Genera una cotización cuando el usuario hace clic en "Me interesa"
        basada en el servicio detectado automáticamente.
        """
        try:
            # Mostra estado "escribiendo"
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Obtener lead del chat_id
            lead = await self._get_or_create_lead(chat_id, None)
            if not lead:
                await bot.send_message(
                    chat_id=chat_id,
                    text="❌ No pude identificar tu información. Por favor intenta de nuevo."
                )
                return
            
            # Obtener datos del lead
            lead_id_int = lead.get("id") or int(lead_id)
            lead_result = self.db.table("leads").select("*").eq("id", lead_id_int).execute()
            if not lead_result.data:
                await bot.send_message(
                    chat_id=chat_id,
                    text="❌ No encontré tu información. Por favor intenta de nuevo."
                )
                return
            
            lead_data = lead_result.data[0]
            
            # Obtener información del servicio del quick_estimator
            estimado = self.quick_estimator.generar_estimado(
                servicio=servicio,
                detalles_adicionales=""
            )
            
            if not estimado:
                await bot.send_message(
                    chat_id=chat_id,
                    text="❌ No pude procesar tu solicitud. Por favor intenta de nuevo."
                )
                return
            
            # Enviar estimado al usuario
            mensaje_estimado = self.quick_estimator.formatear_estimado(estimado)
            
            await bot.send_message(
                chat_id=chat_id,
                text=mensaje_estimado,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Agregar botones de acciones siguientes
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Aceptar estimado", callback_data=f"cotizacion_aceptar_{lead_id_int}"),
                    InlineKeyboardButton("❌ Ajustar propuesta", callback_data=f"cotizacion_rechazar_{lead_id_int}")
                ],
                [
                    InlineKeyboardButton("📅 Agendar reunión", callback_data=f"reunion_agendar_{lead_id_int}")
                ]
            ])
            
            await bot.send_message(
                chat_id=chat_id,
                text="¿Qué te gustaría hacer?",
                reply_markup=keyboard
            )
            
            # Actualizar status del lead
            await update_lead_status(lead_id_int, "cotizado")
            print(f"✅ Cotización rápida enviada a lead {lead_id_int}")
            
        except Exception as e:
            print(f"❌ Error generando cotización de interés: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text="Hubo un problema. Un asesor te contactará pronto."
            )
    
    async def _handle_reunion_callback(self, data: str, chat_id: str, bot: Bot):
        """Maneja solicitudes de reunión."""
        # data = "reunion_agendar_<lead_id>"
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "📅 Perfecto, vamos a agendar una reunión.\n\n"
                "¿Qué día y hora te viene mejor?\n"
                "Ejemplo: _Lunes 3 de marzo a las 10:00_"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_plan_callback(self, data: str, chat_id: str, message_id: int, bot: Bot):
        """
        Maneja selección de planes y genera cotización automática.
        [CRITERIO 5] - Cotizaciones automáticas generadas por IA
        """
        # data = "plan_basico", "plan_profesional", "plan_enterprise"
        plan = data.replace("plan_", "")
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ Has seleccionado el plan *{plan.upper()}*.\n\nPreparando cotización con IA...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Mostrar estado de "escribiendo"
        await bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Obtener lead del chat_id
        lead = await self._get_or_create_lead(chat_id, None)
        if not lead:
            await bot.send_message(
                chat_id=chat_id,
                text="❌ No pude identificar tu información. Por favor intenta de nuevo."
            )
            return
        
        lead_id = lead["id"]
        
        # Generar cotización y enviarla
        await self._generar_cotizacion_y_enviar(
            lead_id=lead_id,
            plan=plan,
            chat_id=chat_id,
            bot=bot
        )
    
    async def _generar_cotizacion_y_enviar(
        self,
        lead_id: int,
        plan: str,
        chat_id: str,
        bot: Bot
    ):
        """
        Genera una cotización automática con IA y la envía al lead vía Telegram.
        [CRITERIO 5] - Cotizaciones automáticas generadas por IA
        """
        try:
            # Obtener datos del lead de la BD
            lead_result = self.db.table("leads").select("*").eq("id", lead_id).execute()
            if not lead_result.data:
                await bot.send_message(
                    chat_id=chat_id,
                    text="❌ No encontré tu información. Por favor intenta de nuevo."
                )
                return
            
            lead_data = lead_result.data[0]
            
            # Mapear plan a descripción de servicio
            plan_descriptions = {
                "basico": "Plan Básico - Solución inicial",
                "profesional": "Plan Profesional - Solución completa",
                "enterprise": "Plan Enterprise - Solución personalizada"
            }
            
            servicio = plan_descriptions.get(plan.lower(), f"Plan {plan}")
            
            # Generar cotización con el agente de comunicación
            print(f"🤖 Generando cotización para lead {lead_id} - {servicio}")
            
            resultado_cotizacion = await self.comunicacion.generate_cotizacion(
                lead_data=lead_data,
                servicio_solicitado=servicio,
                detalles_adicionales=f"Plan seleccionado: {plan}"
            )
            
            if not resultado_cotizacion.get("success"):
                await bot.send_message(
                    chat_id=chat_id,
                    text=resultado_cotizacion.get("fallback_message", 
                        "Hubo un problema generando la cotización. Un asesor te contactará pronto.")
                )
                return
            
            # Guardar cotización en BD
            cotizacion_data = resultado_cotizacion["cotizacion"]
            cotizacion_data["empresa_id"] = 1  # ID default de empresa
            cotizacion_data["user_id"] = 1     # ID default de usuario
            
            nueva_cotizacion = await create_cotizacion(cotizacion_data)
            
            if not nueva_cotizacion.get("id"):
                print("❌ Error al guardar cotización en BD")
                await bot.send_message(
                    chat_id=chat_id,
                    text="Hubo un problema guardando la cotización. Por favor intenta de nuevo."
                )
                return
            
            cotizacion_id = nueva_cotizacion.get("id")
            
            # Actualizar estado del lead a "cotizado"
            await update_lead_status(lead_id, "cotizado")
            print(f"✅ Lead {lead_id} actualizado a status 'cotizado'")
            
            # Renderizar cotización en Markdown
            # Obtener datos de empresa (dummy para demo)
            empresa_data = {
                "nombre": "ORBITA",
                "slogan": "Soluciones Inteligentes de IA",
                "email": "contacto@orbita.ai",
                "telefono": "+1 234 567 890",
                "ciudad": "Virtual",
                "pais": "Global"
            }
            
            markdown_content = render_cotizacion_markdown(
                cotizacion_data=nueva_cotizacion,
                lead_data=lead_data,
                empresa_data=empresa_data
            )
            
            # Enviar cotización al usuario
            print(f"📤 Enviando cotización a chat {chat_id}")
            
            # Dividir en mensajes si es muy largo
            if len(markdown_content) > 4096:
                # Telegram tiene límite de 4096 caracteres por mensaje
                chunks = [markdown_content[i:i+4000] for i in range(0, len(markdown_content), 4000)]
                for chunk in chunks:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(0.5)  # Pequeña pausa entre mensajes
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=markdown_content,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Enviar botones de acción
            keyboard = [
                [
                    InlineKeyboardButton("✅ Aceptar", callback_data=f"cotizacion_aceptar_{lead_id}"),
                    InlineKeyboardButton("❌ Rechazar", callback_data=f"cotizacion_rechazar_{lead_id}")
                ],
                [
                    InlineKeyboardButton("📞 Hablar con asesor", callback_data=f"reunion_agendar_{lead_id}")
                ]
            ]
            
            await bot.send_message(
                chat_id=chat_id,
                text="¿Qué te parece la propuesta?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            print(f"✅ Cotización enviada exitosamente a lead {lead_id}")
            
        except Exception as e:
            print(f"❌ Error generando cotización: {e}")
            import traceback
            traceback.print_exc()
            
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "Disculpa, tuve un problema generando la cotización automáticamente. "
                    "Un asesor se comunicará contigo en las próximas horas. 📞"
                )
            )
    
    # ─── TRANSCRIPCIÓN DE VOZ ──────────────────────────────────
    
    async def _transcribir_voz(self, voice, bot: Bot) -> Optional[str]:
        """
        Transcribe nota de voz usando Whisper de Groq.
        [CRITERIO 3] Whisper transcribe notas de voz en tiempo real.
        """
        temp_file = None
        try:
            # Descargar el archivo de voz desde Telegram
            file = await bot.get_file(voice.file_id)
            file_bytes = await file.download_as_bytearray()
            
            # Crear archivo temporal con extensión .ogg (formato de Telegram)
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                tmp.write(file_bytes)
                temp_file = tmp.name
            
            # Transcribir con Whisper API de Groq
            with open(temp_file, "rb") as audio_file:
                transcript = self.groq_client.client.audio.transcriptions.create(
                    file=(os.path.basename(temp_file), audio_file, "audio/ogg"),
                    model="whisper-large-v3-turbo",
                    language="es"  # Detecta español automáticamente
                )
            
            texto = transcript.text
            duracion = voice.duration or "desconocida"
            tam_bytes = len(file_bytes)
            
            print(f"✅ Nota de voz transcrita ({duracion}s, {tam_bytes} bytes)")
            print(f"   Texto: {texto[:100]}...")
            
            return texto
            
        except Exception as e:
            print(f"❌ Error transcribiendo voz: {e}")
            return None
            
        finally:
            # Limpiar archivo temporal
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"⚠️ No se pudo borrar archivo temporal: {e}")
    
    # ─── GESTIÓN DE LEADS ──────────────────────────────────────
    
    async def _get_or_create_lead(self, chat_id: str, user) -> Optional[Dict]:
        """Obtiene o crea un lead basado en el chat_id de Telegram."""
        try:
            # Buscar lead existente
            result = self.db.table("leads").select("*").eq(
                "telegram_chat_id", chat_id
            ).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # Crear nuevo lead
            nombre = user.first_name
            if user.last_name:
                nombre += f" {user.last_name}"
            
            username = user.username or f"user_{chat_id[:8]}"
            
            # Generar email temporal único para evitar conflicts
            temp_email = f"telegram_{chat_id}@temp.orbita.local"
            
            nuevo_lead = {
                "nombre": nombre,
                "email": temp_email,  # Email temporal único
                "telegram_chat_id": chat_id,
                "telegram_username": username,
                "origen": "telegram",
                "status": "nuevo",
                "interes": "inicial"
            }
            
            result = self.db.table("leads").insert(nuevo_lead).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Error gestionando lead: {e}")
            return None
    
    # ─── MEMORIA Y CONTEXTO ────────────────────────────────────
    
    async def _guardar_mensaje(
        self,
        lead_id: str,
        role: str,
        content: str,
        content_type: str = "text",
        agente: str = None
    ):
        """Guarda un mensaje en el historial de la conversación."""
        try:
            # Buscar conversación activa o crear una nueva
            result = self.db.table("conversations").select("*").eq(
                "lead_id", lead_id
            ).eq("estado", "en_progreso").execute()
            
            mensaje_nuevo = {
                "role": role,
                "content": content,
                "content_type": content_type,
                "agente": agente,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if result.data and len(result.data) > 0:
                # Actualizar conversación existente
                conversation = result.data[0]
                historial = conversation.get("historial", []) or []
                historial.append(mensaje_nuevo)
                
                # Actualizar agentes intervenidos
                agentes_intervenidos = conversation.get("agentes_intervenidos", []) or []
                if agente and agente not in agentes_intervenidos:
                    agentes_intervenidos.append(agente)
                
                self.db.table("conversations").update({
                    "historial": historial,
                    "agentes_intervenidos": agentes_intervenidos
                }).eq("id", conversation["id"]).execute()
            else:
                # Crear nueva conversación
                self.db.table("conversations").insert({
                    "lead_id": lead_id,
                    "session_id": lead_id,
                    "tipo_comunicacion": "telegram",
                    "historial": [mensaje_nuevo],
                    "agentes_intervenidos": [agente] if agente else [],
                    "estado": "en_progreso"
                }).execute()
        except Exception as e:
            print(f"❌ Error guardando mensaje: {e}")
    
    async def _obtener_contexto(self, lead_id: str) -> list:
        """Obtiene el historial de conversación."""
        try:
            result = self.db.table("conversations").select(
                "historial"
            ).eq("lead_id", lead_id).eq(
                "estado", "en_progreso"
            ).order("created_at", desc=True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                historial = result.data[0].get("historial", [])
                return historial[-20:] if historial else []  # Últimos 20 mensajes
            return []
        except Exception as e:
            print(f"❌ Error obteniendo contexto: {e}")
            return []
    
    async def _esta_pausado(self, chat_id: str) -> bool:
        """Verifica si el bot está pausado para este chat."""
        try:
            result = self.db.table("telegram_bot_sessions").select(
                "estado_bot"
            ).eq("telegram_chat_id", chat_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0].get("estado_bot") == "pausado"
            return False
        except Exception as e:
            print(f"⚠️ Error verificando estado pausado: {e}")
            return False
    
    # ─── BOTONES INTELIGENTES ──────────────────────────────────
    
    async def _generar_botones_si_necesario(
        self,
        mensaje: str,
        lead_id: str,
        resultado_orchestrator: dict,
        servicio_detectado: Optional[str] = None,
        estimado: Optional[Dict] = None
    ) -> Optional[list]:
        """
        Genera botones inline si el contexto lo requiere.
        
        Ahora también genera botones automáticamente si:
        - Se detectó un servicio solicitado
        - O si el usuario menciona explícitamente precio/cotización
        """
        mensaje_lower = mensaje.lower()
        
        # ★ NUEVO: Si se detectó un servicio, mostrar botones de cotización
        # NOTA: Usar callback_data cortos para cumplir límite Telegram (64 chars)
        if servicio_detectado and estimado:
            # Guardar servicio detectado en la BD para recuperarlo después
            try:
                self.db.table("leads").update(
                    {"interes": servicio_detectado}
                ).eq("id", lead_id).execute()
            except Exception as e:
                print(f"⚠️ No se pudo guardar servicio en BD: {e}")
            
            # Callback data cortos (máx 64 chars)
            return [
                [
                    InlineKeyboardButton(
                        "✅ Me interesa",
                        callback_data=f"cot_int_{lead_id}"
                    ),
                    InlineKeyboardButton(
                        "📧 Enviar detalles",
                        callback_data=f"cot_env_{lead_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📞 Hablar con asesor",
                        callback_data=f"reu_age_{lead_id}"
                    )
                ]
            ]
        
        # Si menciona "precio", "cotización", "costo"
        if any(word in mensaje_lower for word in ["precio", "cotización", "costo", "cuanto", "cuánto"]):
            return [
                [
                    InlineKeyboardButton(
                        "📄 Ver planes",
                        callback_data=f"cotizacion_ver_{lead_id}"
                    ),
                    InlineKeyboardButton(
                        "📞 Hablar con asesor",
                        callback_data=f"reunion_agendar_{lead_id}"
                    )
                ]
            ]
        
        # Si menciona "reunión", "llamada", "agenda"
        if any(word in mensaje_lower for word in ["reunión", "reunion", "llamada", "agenda", "agendar"]):
            return [
                [
                    InlineKeyboardButton(
                        "📅 Agendar reunión",
                        callback_data=f"reunion_agendar_{lead_id}"
                    )
                ]
            ]
        
        return None
