# Handler para Bot de Admin — Panel de control para el equipo
# [CRITERIO 2] Canal de control bidireccional para el equipo interno
# [CRITERIO 4] El admin puede actuar directamente desde Telegram sin abrir el dashboard

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
try:
    from telegram.constants import ParseMode
except ImportError:
    # Fallback para versiones antiguas de python-telegram-bot
    class ParseMode:
        MARKDOWN = "Markdown"
        HTML = "HTML"

from typing import Dict
from datetime import datetime, timezone

from database import get_db
from config import get_settings


class AdminBotHandler:
    """
    Maneja el bot exclusivo del administrador/equipo interno.

    Capacidades:
    - Recibir alertas automáticas del sistema (nuevo lead, cotización aceptada, etc.)
    - Comandos de consulta rápida del CRM (/leads, /stats, /alertas)
    - Acciones directas sin abrir el dashboard (responder lead, marcar reunión)
    - Autenticación: solo chat_ids autorizados en TELEGRAM_ADMIN_CHAT_IDS
    
    Comandos disponibles:
    - /start: Bienvenida al panel de control
    - /leads: Ver últimos 5 leads del CRM
    - /stats: Resumen rápido de hoy
    - /alertas: Ver alertas activas del Agente Analítico
    - /buscar <nombre>: Buscar lead por nombre
    - /lead <id>: Ver detalle completo de un lead
    - /pausa <id>: Pausar respuestas automáticas a un lead
    - /ayuda: Mostrar lista de comandos
    """

    COMANDOS = {
        "/start":   "Bienvenida al panel de control ORBITA",
        "/leads":   "Ver últimos 5 leads del CRM",
        "/stats":   "Resumen rápido de hoy",
        "/alertas": "Ver alertas activas del Agente Analítico",
        "/buscar":  "Buscar lead por nombre | Ej: /buscar Carlos",
        "/lead":    "Ver detalle de un lead | Ej: /lead abc12345",
        "/pausa":   "Pausar respuestas automáticas a un lead | Ej: /pausa abc12345",
        "/ayuda":   "Mostrar esta lista de comandos",
    }

    def __init__(self):
        self.db = get_db()
        self.settings = get_settings()
        
        # Lista de chat_ids autorizados
        admin_ids_str = self.settings.telegram_admin_chat_ids or ""
        self.admin_chat_ids = set(
            id.strip() for id in admin_ids_str.split(",") if id.strip()
        )

    # ─── VERIFICACIÓN DE ACCESO ────────────────────────────────

    def _es_admin_autorizado(self, chat_id: str) -> bool:
        """Solo los chat_ids registrados en .env pueden usar el bot admin."""
        return str(chat_id) in self.admin_chat_ids

    async def _rechazar_acceso(self, bot: Bot, chat_id: str):
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "⛔ *Acceso denegado*\n\n"
                "Este bot es exclusivo del equipo interno de ORBITA.\n"
                "Si eres del equipo, pide al administrador que agregue "
                "tu Chat ID a la configuración."
            ),
            parse_mode=ParseMode.MARKDOWN
        )

    # ─── ROUTER PRINCIPAL ──────────────────────────────────────

    async def handle_update(self, update: Update, bot: Bot):
        """Punto de entrada de todos los updates del bot admin."""
        chat_id = None

        try:
            # Callbacks de botones inline
            if update.callback_query:
                chat_id = str(update.callback_query.message.chat_id)
                if not self._es_admin_autorizado(chat_id):
                    await self._rechazar_acceso(bot, chat_id)
                    return
                await self._handle_callback(update.callback_query, bot)
                return

            # Mensajes de texto
            if not update.message:
                return

            chat_id = str(update.message.chat_id)
            if not self._es_admin_autorizado(chat_id):
                await self._rechazar_acceso(bot, chat_id)
                return

            text = update.message.text or ""

            if text.startswith("/"):
                await self._handle_command(text, chat_id, bot)
            else:
                # Texto libre: tratarlo como búsqueda de lead
                await self._cmd_buscar(f"/buscar {text}", chat_id, bot)
                
        except Exception as e:
            print(f"❌ [AdminBotHandler] Error: {e}")
            if chat_id:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"Error procesando tu solicitud: {str(e)[:100]}"
                    )
                except:
                    pass

    # ─── COMANDOS ──────────────────────────────────────────────

    async def _handle_command(self, text: str, chat_id: str, bot: Bot):
        """Enruta comandos /xxx al método correcto."""
        cmd = text.split()[0].lower()
        handlers_map = {
            "/start":   self._cmd_start,
            "/leads":   self._cmd_leads,
            "/stats":   self._cmd_stats,
            "/alertas": self._cmd_alertas,
            "/buscar":  self._cmd_buscar,
            "/lead":    self._cmd_lead_detalle,
            "/pausa":   self._cmd_pausa,
            "/ayuda":   self._cmd_ayuda,
        }
        handler_fn = handlers_map.get(cmd, self._cmd_desconocido)
        await handler_fn(text, chat_id, bot)

    async def _cmd_start(self, text: str, chat_id: str, bot: Bot):
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "🛸 *ORBITA — Panel de Control*\n\n"
                "Bienvenido al bot de administración. Desde aquí puedes:\n\n"
                "• Ver y gestionar leads en tiempo real\n"
                "• Recibir alertas automáticas del sistema\n"
                "• Actuar directamente sin abrir el dashboard\n\n"
                "Escribe /ayuda para ver todos los comandos disponibles."
            ),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _cmd_ayuda(self, text: str, chat_id: str, bot: Bot):
        lineas = ["📋 *COMANDOS DISPONIBLES*\n"]
        for cmd, desc in self.COMANDOS.items():
            lineas.append(f"`{cmd}` — {desc}")
        await bot.send_message(
            chat_id=chat_id,
            text="\n".join(lineas),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _cmd_leads(self, text: str, chat_id: str, bot: Bot):
        """Muestra los últimos 5 leads con botones de acción."""
        try:
            result = self.db.table("leads").select(
                "id, nombre, empresa_nombre, etapa_funnel, prioridad, estado, ultimo_contacto"
            ).order("created_at", desc=True).limit(5).execute()

            leads = result.data or []

            if not leads:
                await bot.send_message(
                    chat_id=chat_id,
                    text="📭 No hay leads registrados aún."
                )
                return

            await bot.send_message(
                chat_id=chat_id,
                text=f"📊 *Últimos {len(leads)} leads:*",
                parse_mode=ParseMode.MARKDOWN
            )

            for lead in leads:
                lead_id_corto = str(lead['id'])[:8]
                
                # Emojis según prioridad
                prioridad_emoji = {
                    "alta": "🔴",
                    "media": "🟡",
                    "baja": "🟢"
                }.get(lead.get("prioridad", "media"), "⚪")
                
                # Emojis según etapa del funnel
                etapa_emoji = {
                    "atencion": "👀",
                    "interes": "💡",
                    "deseo": "❤️",
                    "accion": "⚡",
                    "cliente": "✅"
                }.get(lead.get("etapa_funnel", "atencion"), "❓")

                texto = (
                    f"{prioridad_emoji} *{lead.get('nombre', 'Sin nombre')}*\n"
                    f"🏢 {lead.get('empresa_nombre', 'Sin empresa')}\n"
                    f"{etapa_emoji} Etapa: {lead.get('etapa_funnel', '?').upper()}\n"
                    f"📊 Estado: {lead.get('estado', '?')}\n"
                    f"🆔 `{lead_id_corto}`"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "💬 Ver conversación",
                            callback_data=f"admin_conv_{lead['id']}"
                        ),
                        InlineKeyboardButton(
                            "⏸ Pausar bot",
                            callback_data=f"admin_pausa_{lead['id']}"
                        )
                    ]
                ])
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=texto,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )

        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error consultando leads: {str(e)[:100]}"
            )

    async def _cmd_stats(self, text: str, chat_id: str, bot: Bot):
        """Resumen rápido del día."""
        try:
            inicio_hoy = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            ).isoformat()

            # Leads hoy
            leads_hoy = self.db.table("leads").select(
                "id", count="exact"
            ).gte("created_at", inicio_hoy).execute()

            # Cotizaciones pendientes
            cots_pendientes = self.db.table("cotizaciones").select(
                "id", count="exact"
            ).eq("estado", "pendiente").execute()

            # Reuniones hoy
            reuniones_hoy = self.db.table("reuniones").select(
                "id", count="exact"
            ).gte("fecha_hora", inicio_hoy).execute()

            # Logs de agentes hoy
            logs_hoy = self.db.table("agent_logs").select(
                "id", count="exact"
            ).gte("created_at", inicio_hoy).execute()

            texto = (
                f"📊 *RESUMEN DE HOY*\n"
                f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_\n\n"
                f"🆕 Leads nuevos: *{leads_hoy.count or 0}*\n"
                f"📄 Cotizaciones pendientes: *{cots_pendientes.count or 0}*\n"
                f"🗓️ Reuniones hoy: *{reuniones_hoy.count or 0}*\n"
                f"🤖 Acciones de agentes: *{logs_hoy.count or 0}*"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔍 Ver alertas",
                        callback_data="admin_cmd_alertas"
                    ),
                    InlineKeyboardButton(
                        "👥 Ver leads",
                        callback_data="admin_cmd_leads"
                    )
                ]
            ])
            
            await bot.send_message(
                chat_id=chat_id,
                text=texto,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )

        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error obteniendo stats: {str(e)[:100]}"
            )

    async def _cmd_alertas(self, text: str, chat_id: str, bot: Bot):
        """Corre el Agente Analítico y muestra las alertas actuales."""
        await bot.send_message(
            chat_id=chat_id,
            text="🔍 Analizando CRM... espera un momento."
        )
        
        try:
            from agents.analitico import AnaliticoAgent
            
            analitico = AnaliticoAgent()
            resultado = await analitico.process_message(
                message="Generar alertas del sistema",
                session_id="admin_bot",
                context={"tipo_analisis": "alerta_rapida"}
            )

            # Extraer alertas del resultado
            alertas = resultado.get("alertas", [])
            if not alertas:
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "✅ *Sin alertas activas*\n\n"
                        + resultado.get("response", "Todo está en orden.")
                    ),
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Enviar cada alerta
            for alerta in alertas[:5]:  # Máximo 5 alertas
                prioridad_emoji = {
                    "alta": "🚨",
                    "media": "⚠️",
                    "baja": "ℹ️"
                }.get(alerta.get("prioridad", "media"), "⚠️")
                
                texto = (
                    f"{prioridad_emoji} *[{alerta.get('prioridad', '?').upper()}]*\n"
                    f"{alerta.get('mensaje', '')}\n\n"
                    f"💡 _{alerta.get('accion_recomendada', '')}_"
                )
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=texto,
                    parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error: {str(e)[:100]}"
            )

    async def _cmd_buscar(self, text: str, chat_id: str, bot: Bot):
        """Busca leads por nombre."""
        partes = text.split(maxsplit=1)
        if len(partes) < 2 or not partes[1].strip():
            await bot.send_message(
                chat_id=chat_id,
                text="Uso: `/buscar nombre` | Ej: `/buscar Carlos`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        termino = partes[1].strip()
        try:
            result = self.db.table("leads").select(
                "id, nombre, empresa_nombre, etapa_funnel, estado, prioridad"
            ).ilike("nombre", f"%{termino}%").limit(5).execute()

            leads = result.data or []
            if not leads:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"🔍 No encontré leads con el nombre *{termino}*.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            await bot.send_message(
                chat_id=chat_id,
                text=f"🔍 Encontré *{len(leads)}* resultado(s) para _{termino}_:",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Mostrar cada resultado
            for lead in leads:
                lead_id_corto = str(lead['id'])[:8]
                texto = (
                    f"👤 *{lead.get('nombre')}*\n"
                    f"🏢 {lead.get('empresa_nombre', 'Sin empresa')}\n"
                    f"📈 {lead.get('etapa_funnel', '?').upper()} · "
                    f"{lead.get('estado', '?')} · {lead.get('prioridad', '?')}\n"
                    f"🆔 `{lead_id_corto}`"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "💬 Conversación",
                            callback_data=f"admin_conv_{lead['id']}"
                        ),
                        InlineKeyboardButton(
                            "⏸ Pausar bot",
                            callback_data=f"admin_pausa_{lead['id']}"
                        )
                    ]
                ])
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=texto,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
                
        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error buscando: {str(e)[:100]}"
            )

    async def _cmd_lead_detalle(self, text: str, chat_id: str, bot: Bot):
        """Muestra detalle completo de un lead por ID corto."""
        partes = text.split(maxsplit=1)
        if len(partes) < 2:
            await bot.send_message(
                chat_id=chat_id,
                text="Uso: `/lead abc12345`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        id_corto = partes[1].strip()
        try:
            result = self.db.table("leads").select("*").ilike(
                "id", f"{id_corto}%"
            ).limit(1).execute()

            if not result.data:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"🔍 No encontré lead con ID `{id_corto}`.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            lead = result.data[0]
            
            # Obtener cotizaciones del lead
            cotizaciones = self.db.table("cotizaciones").select(
                "plan_nombre, valor, estado"
            ).eq("lead_id", lead["id"]).execute().data or []

            cots_str = "\n".join([
                f"  • {c['plan_nombre']} — ${c['valor']:,.0f} [{c['estado']}]"
                for c in cotizaciones
            ]) or "  Sin cotizaciones"

            texto = (
                f"👤 *{lead.get('nombre', 'Sin nombre')}*\n"
                f"─────────────────────\n"
                f"🏢 Empresa: {lead.get('empresa_nombre', 'N/A')}\n"
                f"💼 Cargo: {lead.get('cargo', 'N/A')}\n"
                f"📧 Email: {lead.get('email', 'N/A')}\n"
                f"📱 Teléfono: {lead.get('telefono', 'N/A')}\n"
                f"🎯 Interés: {lead.get('servicio_interes', 'N/A')}\n"
                f"💰 Presupuesto: {lead.get('presupuesto_estimado', 'N/A')}\n"
                f"📈 Etapa: {lead.get('etapa_funnel', '?').upper()}\n"
                f"⚡ Prioridad: {lead.get('prioridad', '?').upper()}\n"
                f"🔖 Etiquetas: {', '.join(lead.get('etiquetas') or []) or 'N/A'}\n\n"
                f"📄 *Cotizaciones:*\n{cots_str}"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💬 Ver conversación",
                        callback_data=f"admin_conv_{lead['id']}"
                    ),
                    InlineKeyboardButton(
                        "⏸ Pausar bot",
                        callback_data=f"admin_pausa_{lead['id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Marcar como cliente",
                        callback_data=f"admin_convertir_{lead['id']}"
                    )
                ]
            ])
            
            await bot.send_message(
                chat_id=chat_id,
                text=texto,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error: {str(e)[:100]}"
            )

    async def _cmd_pausa(self, text: str, chat_id: str, bot: Bot):
        """Pausa las respuestas automáticas del bot de leads para un lead."""
        partes = text.split(maxsplit=1)
        if len(partes) < 2:
            await bot.send_message(
                chat_id=chat_id,
                text="Uso: `/pausa abc12345`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        id_corto = partes[1].strip()
        try:
            lead = self.db.table("leads").select(
                "id, nombre, telegram_chat_id"
            ).ilike("id", f"{id_corto}%").limit(1).execute().data
            
            if not lead:
                await bot.send_message(
                    chat_id=chat_id,
                    text="🔍 Lead no encontrado."
                )
                return
                
            lead = lead[0]
            
            # Pausar la sesión del bot de leads para este chat_id
            if lead.get("telegram_chat_id"):
                # Crear o actualizar sesión
                self.db.table("telegram_bot_sessions").upsert({
                    "telegram_chat_id": lead["telegram_chat_id"],
                    "estado_bot": "pausado",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()

            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"⏸ *Bot pausado para {lead['nombre']}*\n\n"
                    f"El bot de leads NO responderá automáticamente a este lead.\n"
                    f"Puedes retomar el control manual desde el dashboard.\n\n"
                    f"Para reactivar: escribe al lead y el sistema detectará el reinicio."
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error: {str(e)[:100]}"
            )

    async def _cmd_desconocido(self, text: str, chat_id: str, bot: Bot):
        await bot.send_message(
            chat_id=chat_id,
            text=f"❓ Comando no reconocido. Escribe /ayuda para ver opciones.",
        )

    # ─── CALLBACKS (botones inline) ────────────────────────────

    async def _handle_callback(self, callback_query, bot: Bot):
        """Procesa los botones inline del bot admin."""
        data = callback_query.data
        chat_id = str(callback_query.message.chat_id)
        await callback_query.answer()

        try:
            # Comandos rápidos desde botones
            if data == "admin_cmd_alertas":
                await self._cmd_alertas("", chat_id, bot)
                return
            
            if data == "admin_cmd_leads":
                await self._cmd_leads("", chat_id, bot)
                return

            # Acciones sobre leads
            if data.startswith("admin_conv_"):
                lead_id = data.replace("admin_conv_", "")
                await self._mostrar_ultimos_mensajes(lead_id, chat_id, bot)

            elif data.startswith("admin_pausa_"):
                lead_id = data.replace("admin_pausa_", "")
                lead = self.db.table("leads").select(
                    "nombre, telegram_chat_id"
                ).eq("id", lead_id).maybe_single().execute().data
                
                if lead and lead.get("telegram_chat_id"):
                    self.db.table("telegram_bot_sessions").upsert({
                        "telegram_chat_id": lead["telegram_chat_id"],
                        "estado_bot": "pausado",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).execute()
                    
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"⏸ Bot pausado para *{lead['nombre']}*.",
                        parse_mode=ParseMode.MARKDOWN
                    )

            elif data.startswith("admin_convertir_"):
                lead_id = data.replace("admin_convertir_", "")
                self.db.table("leads").update(
                    {"estado": "convertido", "etapa_funnel": "cliente"}
                ).eq("id", lead_id).execute()
                
                lead = self.db.table("leads").select("nombre").eq(
                    "id", lead_id
                ).maybe_single().execute().data
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *{lead.get('nombre', 'Lead')}* marcado como *CLIENTE*. 🎉",
                    parse_mode=ParseMode.MARKDOWN
                )

            elif data.startswith("admin_ver_"):
                lead_id = data.replace("admin_ver_", "")
                await self._cmd_lead_detalle(f"/lead {lead_id[:8]}", chat_id, bot)

            elif data.startswith("admin_chat_"):
                lead_id = data.replace("admin_chat_", "")
                await self._mostrar_ultimos_mensajes(lead_id, chat_id, bot)
                
        except Exception as e:
            print(f"❌ Error en callback: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text=f"Error procesando acción: {str(e)[:100]}"
            )

    async def _mostrar_ultimos_mensajes(self, lead_id: str, chat_id: str, bot: Bot):
        """Muestra los últimos 5 mensajes de la conversación con el lead."""
        try:
            msgs = self.db.table("conversations").select(
                "role, content, agente, content_type, created_at"
            ).eq("lead_id", lead_id).order(
                "created_at", desc=True
            ).limit(5).execute().data or []

            if not msgs:
                await bot.send_message(
                    chat_id=chat_id,
                    text="📭 Sin mensajes registrados para este lead."
                )
                return

            lead = self.db.table("leads").select(
                "nombre"
            ).eq("id", lead_id).maybe_single().execute().data

            header = f"💬 *Últimos mensajes — {lead.get('nombre', 'Lead') if lead else 'Lead'}*\n\n"
            lineas = [header]
            
            for msg in reversed(msgs):
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                tipo = " 🎙️" if msg.get("content_type") == "voice" else ""
                agente = f" _{msg.get('agente', '')}_" if msg["role"] == "assistant" else ""
                
                # Truncar mensaje si es muy largo
                content = msg['content'][:200]
                if len(msg['content']) > 200:
                    content += "..."
                
                lineas.append(
                    f"{role_emoji}{tipo}{agente}\n"
                    f"{content}\n"
                )

            await bot.send_message(
                chat_id=chat_id,
                text="\n".join(lineas),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error: {str(e)[:100]}"
            )
    
    # ─── NOTIFICACIONES PROACTIVAS ─────────────────────────────
    
    async def enviar_alerta_global(self, bot: Bot, mensaje: str, prioridad: str = "media"):
        """
        Envía una alerta a TODOS los administradores registrados.
        Usado por el sistema para notificaciones automáticas.
        """
        prioridad_emoji = {
            "alta": "🚨",
            "media": "⚠️",
            "baja": "ℹ️"
        }.get(prioridad, "📢")
        
        texto = f"{prioridad_emoji} *ALERTA DEL SISTEMA*\n\n{mensaje}"
        
        for admin_chat_id in self.admin_chat_ids:
            try:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=texto,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"❌ [AdminNotifier] Error enviando a {admin_chat_id}: {e}")
