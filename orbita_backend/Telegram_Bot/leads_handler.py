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

from database import get_db
from config import get_settings
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.conversacional import ConversacionalAgent
from utils.groq_client import get_groq_client


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
        2. Captador extrae datos si es un lead nuevo
        3. Conversacional genera la respuesta
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
            
            # Determinar si necesita botones especiales
            botones = await self._generar_botones_si_necesario(
                mensaje, lead_id, resultado_orchestrator
            )
            
            return {
                "respuesta": respuesta,
                "botones": botones,
                "agente": resultado_orchestrator.get("agent", "orchestrator"),
                "metadatos": resultado_orchestrator
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
        # data = "cotizacion_aceptar_<lead_id>" o "cotizacion_rechazar_<lead_id>"
        partes = data.split("_")
        if len(partes) < 3:
            return
        
        accion = partes[1]  # "aceptar" o "rechazar"
        lead_id = partes[2]
        
        if accion == "aceptar":
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "¡Excelente! 🎉\n\n"
                    "¿Cuándo te gustaría que agendemos una reunión para revisar los detalles?"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            # Actualizar status
            self.db.table("leads").update(
                {"status": "cotizado"}
            ).eq("id", lead_id).execute()
            
        else:  # rechazar
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "Entiendo. ¿Hay algo específico que no se ajusta a tus necesidades? "
                    "Puedo ajustar la propuesta."
                )
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
        """Maneja selección de planes."""
        # data = "plan_basico", "plan_profesional", "plan_enterprise"
        plan = data.replace("plan_", "")
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ Has seleccionado el plan *{plan.upper()}*.\n\nPreparando cotización...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Aquí se podría llamar al agente para generar cotización automática
        # Por ahora, mensaje simple
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"📄 Estoy preparando una cotización detallada del plan {plan}.\n\n"
                f"Te la enviaré en unos momentos con toda la información."
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
        resultado_orchestrator: dict
    ) -> Optional[list]:
        """
        Genera botones inline si el contexto lo requiere.
        Ejemplo: si se menciona cotización o reunión.
        """
        mensaje_lower = mensaje.lower()
        
        # Si menciona "precio", "cotización", "costo"
        if any(word in mensaje_lower for word in ["precio", "cotización", "costo", "cuanto"]):
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
        if any(word in mensaje_lower for word in ["reunión", "reunion", "llamada", "agenda"]):
            return [
                [
                    InlineKeyboardButton(
                        "📅 Agendar reunión",
                        callback_data=f"reunion_agendar_{lead_id}"
                    )
                ]
            ]
        
        return None
