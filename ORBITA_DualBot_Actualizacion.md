# ORBITA — Actualización: Arquitectura de 2 Bots de Telegram
## Cambios sobre ORBITA_Prompts_Build.md
---

## ¿POR QUÉ DOS BOTS?

| | Bot de Leads `@orbita_cliente_bot` | Bot de Admin `@orbita_admin_bot` |
|---|---|---|
| **Audiencia** | Prospectos / leads externos | Equipo interno / gerente |
| **Tono** | Amigable, orientado a venta | Técnico, operacional |
| **Función** | Conversación AIDA, cotizaciones, reuniones | Alertas, comandos de gestión, acciones CRM |
| **Quién lo comparte** | Se publica en redes, web, tarjetas | Solo el equipo interno lo conoce |
| **Token** | `TELEGRAM_LEADS_BOT_TOKEN` | `TELEGRAM_ADMIN_BOT_TOKEN` |
| **Webhook** | `/api/v1/telegram/leads/webhook` | `/api/v1/telegram/admin/webhook` |

---

## CAMBIO 1 — .env.example

Reemplazar la sección `# Telegram` actual por:

```env
# Telegram — BOT LEADS (el que ven los prospectos)
TELEGRAM_LEADS_BOT_TOKEN=TOKEN_DEL_BOT_LEADS_DESDE_BOTFATHER
TELEGRAM_LEADS_WEBHOOK_URL=https://TU-DOMINIO.com/api/v1/telegram/leads/webhook
TELEGRAM_LEADS_WEBHOOK_SECRET=orbita-leads-secret-2026

# Telegram — BOT ADMIN (solo el equipo interno)
TELEGRAM_ADMIN_BOT_TOKEN=TOKEN_DEL_BOT_ADMIN_DESDE_BOTFATHER
TELEGRAM_ADMIN_BOT_WEBHOOK_URL=https://TU-DOMINIO.com/api/v1/telegram/admin/webhook
TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET=orbita-admin-secret-2026

# Chat IDs de administradores (separados por coma si hay varios)
# Obtener escribiendo a @userinfobot en Telegram
TELEGRAM_ADMIN_CHAT_IDS=123456789,987654321
```

---

## CAMBIO 2 — config.py

Reemplazar los campos de Telegram en `Settings`:

```python
# En la clase Settings, reemplazar los campos telegram anteriores por:

# Bot de Leads
telegram_leads_bot_token: str
telegram_leads_webhook_url: str = ""
telegram_leads_webhook_secret: str = "orbita-leads-secret-2026"

# Bot de Admin
telegram_admin_bot_token: str
telegram_admin_bot_webhook_url: str = ""
telegram_admin_bot_webhook_secret: str = "orbita-admin-secret-2026"

# Chat IDs de admins (puede ser uno o varios)
telegram_admin_chat_ids: str = ""  # "123456,789012"

@property
def admin_chat_ids_list(self) -> list[str]:
    """Retorna lista de chat IDs de admin."""
    return [
        cid.strip()
        for cid in self.telegram_admin_chat_ids.split(",")
        if cid.strip()
    ]
```

---

## CAMBIO 3 — telegram/bot.py (REEMPLAZAR COMPLETO)

```python
# telegram/bot.py
# [CRITERIO 2] — Dos bots con roles diferenciados
# [CRITERIO 4] — Separación clara: leads no ven alertas internas

from telegram import Bot
from telegram.ext import Application
from config import get_settings

# ─── Singletons ───────────────────────────────────────────────
_leads_bot: Bot | None = None
_admin_bot: Bot | None = None
_leads_application: Application | None = None
_admin_application: Application | None = None


# ─── BOT DE LEADS ─────────────────────────────────────────────

def get_leads_bot() -> Bot:
    """Bot que interactúa con los prospectos/leads."""
    global _leads_bot
    if not _leads_bot:
        settings = get_settings()
        _leads_bot = Bot(token=settings.telegram_leads_bot_token)
    return _leads_bot


def get_leads_application() -> Application:
    global _leads_application
    if not _leads_application:
        settings = get_settings()
        _leads_application = (
            Application.builder()
            .token(settings.telegram_leads_bot_token)
            .build()
        )
    return _leads_application


async def setup_leads_webhook():
    """Registra el webhook del bot de leads."""
    settings = get_settings()
    bot = get_leads_bot()
    await bot.set_webhook(
        url=settings.telegram_leads_webhook_url,
        secret_token=settings.telegram_leads_webhook_secret,
        allowed_updates=["message", "callback_query"]
    )
    info = await bot.get_me()
    return info.username


async def delete_leads_webhook():
    await get_leads_bot().delete_webhook()


# ─── BOT DE ADMIN ─────────────────────────────────────────────

def get_admin_bot() -> Bot:
    """Bot exclusivo para el equipo interno y gerente."""
    global _admin_bot
    if not _admin_bot:
        settings = get_settings()
        _admin_bot = Bot(token=settings.telegram_admin_bot_token)
    return _admin_bot


def get_admin_application() -> Application:
    global _admin_application
    if not _admin_application:
        settings = get_settings()
        _admin_application = (
            Application.builder()
            .token(settings.telegram_admin_bot_token)
            .build()
        )
    return _admin_application


async def setup_admin_webhook():
    """Registra el webhook del bot de admin."""
    settings = get_settings()
    bot = get_admin_bot()
    await bot.set_webhook(
        url=settings.telegram_admin_bot_webhook_url,
        secret_token=settings.telegram_admin_bot_webhook_secret,
        allowed_updates=["message", "callback_query"]
    )
    info = await bot.get_me()
    return info.username


async def delete_admin_webhook():
    await get_admin_bot().delete_webhook()


# ─── INFO COMBINADA ───────────────────────────────────────────

async def get_both_bots_info() -> dict:
    """Retorna info de ambos bots para el endpoint /health y /telegram/info."""
    leads_bot = get_leads_bot()
    admin_bot = get_admin_bot()

    leads_info = await leads_bot.get_me()
    admin_info = await admin_bot.get_me()
    leads_webhook = await leads_bot.get_webhook_info()
    admin_webhook = await admin_bot.get_webhook_info()

    return {
        "bot_leads": {
            "username": leads_info.username,
            "nombre": leads_info.full_name,
            "webhook_url": leads_webhook.url,
            "pending_updates": leads_webhook.pending_update_count,
            "link": f"https://t.me/{leads_info.username}"
        },
        "bot_admin": {
            "username": admin_info.username,
            "nombre": admin_info.full_name,
            "webhook_url": admin_webhook.url,
            "pending_updates": admin_webhook.pending_update_count,
            "link": f"https://t.me/{admin_info.username}"
        }
    }
```

---

## CAMBIO 4 — telegram/leads_handler.py (RENOMBRAR handlers.py)

Renombrar el archivo actual `telegram/handlers.py` a `telegram/leads_handler.py`.

Solo cambiar los imports internos que referencian `get_bot()`:

```python
# Reemplazar en leads_handler.py:
# ANTES:
from telegram.bot import get_bot
bot = get_bot()

# DESPUÉS:
from telegram.bot import get_leads_bot
bot = get_leads_bot()
```

Y la clase:
```python
# ANTES:
class TelegramHandler:

# DESPUÉS:
class LeadsBotHandler:
```

El resto del archivo `handlers.py` actual queda igual — toda la lógica de captura de leads, manejo de voz, callbacks de cotizaciones y reuniones pertenece al bot de leads.

---

## CAMBIO 5 — telegram/admin_bot_handler.py (ARCHIVO NUEVO)

```python
# telegram/admin_bot_handler.py
# [CRITERIO 1] — El admin tiene su propio flujo conversacional
# [CRITERIO 2] — Canal de control bidireccional para el equipo interno
# [CRITERIO 4] — El admin puede actuar directamente desde Telegram sin abrir el dashboard

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
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
    """

    COMANDOS = {
        "/start":   "Bienvenida al panel de control ORBITA",
        "/leads":   "Ver últimos 5 leads del CRM",
        "/stats":   "Resumen rápido de hoy",
        "/alertas": "Ver alertas activas del Agente Analítico",
        "/buscar":  "Buscar lead por nombre  Ej: /buscar Carlos",
        "/lead":    "Ver detalle de un lead  Ej: /lead abc12345",
        "/pausa":   "Pausar respuestas automáticas a un lead  Ej: /pausa abc12345",
        "/ayuda":   "Mostrar esta lista de comandos",
    }

    def __init__(self):
        self.db = get_db()
        self.settings = get_settings()
        self.admin_chat_ids = set(self.settings.admin_chat_ids_list)

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

        if update.callback_query:
            chat_id = str(update.callback_query.message.chat_id)
            if not self._es_admin_autorizado(chat_id):
                await self._rechazar_acceso(bot, chat_id)
                return
            await self._handle_callback(update.callback_query, bot)
            return

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
                await bot.send_message(chat_id=chat_id,
                                       text="No hay leads registrados aún.")
                return

            for lead in leads:
                lead_id_corto = str(lead['id'])[:8]
                prioridad_emoji = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(
                    lead.get("prioridad", "media"), "⚪"
                )
                etapa_emoji = {
                    "atencion": "👀", "interes": "💡",
                    "deseo": "❤️", "accion": "⚡", "cliente": "✅"
                }.get(lead.get("etapa_funnel", "atencion"), "❓")

                texto = (
                    f"{prioridad_emoji} *{lead.get('nombre', 'Sin nombre')}*\n"
                    f"🏢 {lead.get('empresa_nombre', 'Sin empresa')}\n"
                    f"{etapa_emoji} Etapa: {lead.get('etapa_funnel','?').upper()}\n"
                    f"📊 Estado: {lead.get('estado','?')}\n"
                    f"🆔 `{lead_id_corto}`"
                )
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "💬 Ver conversación",
                        callback_data=f"admin_conv_{lead['id']}"
                    ),
                    InlineKeyboardButton(
                        "⏸ Pausar bot",
                        callback_data=f"admin_pausa_{lead['id']}"
                    )
                ]])
                await bot.send_message(
                    chat_id=chat_id, text=texto,
                    parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )

        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error consultando leads: {str(e)[:100]}")

    async def _cmd_stats(self, text: str, chat_id: str, bot: Bot):
        """Resumen rápido del día."""
        try:
            from datetime import datetime, timezone
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
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🔍 Ver alertas", callback_data="admin_cmd_alertas"
                ),
                InlineKeyboardButton(
                    "👥 Ver leads", callback_data="admin_cmd_leads"
                )
            ]])
            await bot.send_message(
                chat_id=chat_id, text=texto,
                parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
            )

        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error obteniendo stats: {str(e)[:100]}")

    async def _cmd_alertas(self, text: str, chat_id: str, bot: Bot):
        """Corre el Agente Analítico y muestra las alertas actuales."""
        await bot.send_message(chat_id=chat_id,
                               text="🔍 Analizando CRM... espera un momento.")
        try:
            from agents.analitico import AnaliticoAgent
            from config import get_settings
            analitico = AnaliticoAgent(self.db, get_settings())
            resultado = analitico.execute({"tipo_analisis": "alerta_rapida"})

            alertas = resultado.get("alertas", [])
            if not alertas:
                await bot.send_message(
                    chat_id=chat_id,
                    text="✅ *Sin alertas activas*\n\n" + resultado.get(
                        "resumen_ejecutivo", "Todo está en orden."
                    ),
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            for alerta in alertas[:5]:
                prioridad_emoji = {"alta": "🚨", "media": "⚠️", "baja": "ℹ️"}.get(
                    alerta.get("prioridad", "media"), "⚠️"
                )
                texto = (
                    f"{prioridad_emoji} *[{alerta.get('prioridad','?').upper()}]*\n"
                    f"{alerta.get('mensaje', '')}\n\n"
                    f"💡 _{alerta.get('accion_recomendada', '')}_"
                )
                await bot.send_message(
                    chat_id=chat_id, text=texto,
                    parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error: {str(e)[:100]}")

    async def _cmd_buscar(self, text: str, chat_id: str, bot: Bot):
        """Busca leads por nombre."""
        partes = text.split(maxsplit=1)
        if len(partes) < 2 or not partes[1].strip():
            await bot.send_message(
                chat_id=chat_id,
                text="Uso: `/buscar nombre`  Ej: `/buscar Carlos`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        termino = partes[1].strip()
        try:
            result = self.db.table("leads").select(
                "id, nombre, empresa_nombre, etapa_funnel, estado, prioridad, telegram_chat_id"
            ).ilike("nombre", f"%{termino}%").limit(5).execute()

            leads = result.data or []
            if not leads:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"No encontré leads con el nombre *{termino}*.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            await bot.send_message(
                chat_id=chat_id,
                text=f"🔍 Encontré *{len(leads)}* resultado(s) para _{termino}_:",
                parse_mode=ParseMode.MARKDOWN
            )
            # Reusar _cmd_leads pero con data filtrada
            for lead in leads:
                lead_id_corto = str(lead['id'])[:8]
                texto = (
                    f"👤 *{lead.get('nombre')}*\n"
                    f"🏢 {lead.get('empresa_nombre', 'Sin empresa')}\n"
                    f"📈 {lead.get('etapa_funnel','?').upper()} · "
                    f"{lead.get('estado','?')} · {lead.get('prioridad','?')}\n"
                    f"🆔 `{lead_id_corto}`"
                )
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "💬 Conversación",
                        callback_data=f"admin_conv_{lead['id']}"
                    ),
                    InlineKeyboardButton(
                        "⏸ Pausar bot",
                        callback_data=f"admin_pausa_{lead['id']}"
                    )
                ]])
                await bot.send_message(
                    chat_id=chat_id, text=texto,
                    parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )
        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error buscando: {str(e)[:100]}")

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
                await bot.send_message(chat_id=chat_id,
                                       text=f"No encontré lead con ID `{id_corto}`.",
                                       parse_mode=ParseMode.MARKDOWN)
                return

            lead = result.data[0]
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
                f"📈 Etapa: {lead.get('etapa_funnel','?').upper()}\n"
                f"⚡ Prioridad: {lead.get('prioridad','?').upper()}\n"
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
                chat_id=chat_id, text=texto,
                parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
            )
        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error: {str(e)[:100]}")

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
                await bot.send_message(chat_id=chat_id,
                                       text="Lead no encontrado.")
                return
            lead = lead[0]
            # Pausar la sesión del bot de leads para este chat_id
            if lead.get("telegram_chat_id"):
                self.db.table("telegram_bot_sessions").update(
                    {"estado_bot": "pausado"}
                ).eq("telegram_chat_id", lead["telegram_chat_id"]).execute()

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
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error: {str(e)[:100]}")

    async def _cmd_desconocido(self, text: str, chat_id: str, bot: Bot):
        await bot.send_message(
            chat_id=chat_id,
            text=f"Comando no reconocido. Escribe /ayuda para ver opciones.",
        )

    # ─── CALLBACKS (botones inline) ────────────────────────────

    async def _handle_callback(self, callback_query, bot: Bot):
        """Procesa los botones inline del bot admin."""
        data = callback_query.data
        chat_id = str(callback_query.message.chat_id)
        await callback_query.answer()

        # Comandos rapidos desde botones
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
                self.db.table("telegram_bot_sessions").update(
                    {"estado_bot": "pausado"}
                ).eq("telegram_chat_id", lead["telegram_chat_id"]).execute()
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
                "id", lead_id).maybe_single().execute().data
            await bot.send_message(
                chat_id=chat_id,
                text=f"✅ *{lead.get('nombre','Lead')}* marcado como *CLIENTE*. 🎉",
                parse_mode=ParseMode.MARKDOWN
            )

        elif data.startswith("admin_ver_"):
            lead_id = data.replace("admin_ver_", "")
            await self._cmd_lead_detalle(f"/lead {lead_id[:8]}", chat_id, bot)

        elif data.startswith("admin_chat_"):
            lead_id = data.replace("admin_chat_", "")
            await self._mostrar_ultimos_mensajes(lead_id, chat_id, bot)

    async def _mostrar_ultimos_mensajes(self, lead_id: str, chat_id: str, bot: Bot):
        """Muestra los últimos 5 mensajes de la conversación con el lead."""
        try:
            msgs = self.db.table("conversations").select(
                "role, content, agente, content_type, created_at"
            ).eq("lead_id", lead_id).order(
                "created_at", desc=True
            ).limit(5).execute().data or []

            if not msgs:
                await bot.send_message(chat_id=chat_id,
                                       text="Sin mensajes registrados para este lead.")
                return

            lead = self.db.table("leads").select(
                "nombre"
            ).eq("id", lead_id).maybe_single().execute().data

            header = f"💬 *Últimos mensajes — {lead.get('nombre','Lead') if lead else 'Lead'}*\n\n"
            lineas = [header]
            for msg in reversed(msgs):
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                tipo = " 🎙️" if msg.get("content_type") == "voice" else ""
                agente = f" _{msg.get('agente','')}_" if msg["role"] == "assistant" else ""
                lineas.append(
                    f"{role_emoji}{tipo}{agente}\n"
                    f"{msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}\n"
                )

            await bot.send_message(
                chat_id=chat_id,
                text="\n".join(lineas),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await bot.send_message(chat_id=chat_id,
                                   text=f"Error: {str(e)[:100]}")
```

---

## CAMBIO 6 — telegram/admin_notifier.py

Reemplazar `self.bot` para que use el bot de admin, no el de leads:

```python
# En la clase AdminNotifier, cambiar el __init__:

# ANTES:
class AdminNotifier:
    def __init__(self, bot: Bot, admin_chat_id: str, db):
        self.bot = bot
        self.admin_chat_id = admin_chat_id
        self.db = db

# DESPUÉS:
from telegram.bot import get_admin_bot
from config import get_settings

class AdminNotifier:
    def __init__(self, db):
        """
        El AdminNotifier ahora usa siempre el bot de admin.
        No necesita recibir el bot ni el chat_id como parámetros
        porque los lee directamente de la configuración.
        """
        self.bot = get_admin_bot()
        self.db = db
        settings = get_settings()
        # Notificar a TODOS los admins registrados
        self.admin_chat_ids = settings.admin_chat_ids_list

    async def _send_to_all_admins(self, text: str, keyboard=None):
        """Envía un mensaje a todos los chat_ids de admin configurados."""
        for admin_chat_id in self.admin_chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_chat_id,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"[AdminNotifier] Error enviando a {admin_chat_id}: {e}")
```

Y en todos los métodos `notify_*`, reemplazar:
```python
# ANTES:
await self.bot.send_message(chat_id=self.admin_chat_id, ...)

# DESPUÉS:
await self._send_to_all_admins(texto, keyboard)
```

Y en todos los lugares donde se crea `AdminNotifier`, simplificar:
```python
# ANTES (en leads_handler.py):
notifier = AdminNotifier(bot, self.settings.telegram_admin_chat_id, self.db)

# DESPUÉS:
notifier = AdminNotifier(self.db)
```

---

## CAMBIO 7 — routers/telegram.py (REEMPLAZAR COMPLETO)

```python
# routers/telegram.py
# [CRITERIO 6] — Dos webhooks documentados independientes

from fastapi import APIRouter, Request, HTTPException, Header
from telegram import Update
from telegram.bot import (
    get_leads_bot, get_admin_bot,
    setup_leads_webhook, setup_admin_webhook,
    delete_leads_webhook, delete_admin_webhook,
    get_both_bots_info
)
from telegram.leads_handler import LeadsBotHandler
from telegram.admin_bot_handler import AdminBotHandler
from config import get_settings

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])

# Singletons de handlers
_leads_handler: LeadsBotHandler | None = None
_admin_handler: AdminBotHandler | None = None

def get_leads_handler() -> LeadsBotHandler:
    global _leads_handler
    if not _leads_handler:
        _leads_handler = LeadsBotHandler()
    return _leads_handler

def get_admin_handler() -> AdminBotHandler:
    global _admin_handler
    if not _admin_handler:
        _admin_handler = AdminBotHandler()
    return _admin_handler


# ─── WEBHOOK LEADS ─────────────────────────────────────────────

@router.post("/leads/webhook",
    summary="Webhook — Bot de Leads",
    description="""
    Recibe mensajes de prospectos/leads desde el bot público.
    Soporta texto, notas de voz (Whisper), y botones inline.

    [CRITERIO 1] Canal conversacional AIDA con memoria completa.
    [CRITERIO 3] Whisper transcribe notas de voz en tiempo real.

    Configurar en BotFather con el token TELEGRAM_LEADS_BOT_TOKEN.
    """)
async def leads_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_leads_webhook_secret:
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    update = Update.de_json(body, get_leads_bot())
    await get_leads_handler().handle_update(update, get_leads_bot())
    return {"ok": True}


# ─── WEBHOOK ADMIN ─────────────────────────────────────────────

@router.post("/admin/webhook",
    summary="Webhook — Bot de Admin",
    description="""
    Recibe comandos del equipo interno desde el bot privado de admin.
    Soporta comandos /leads, /stats, /alertas, /buscar, /pausa.

    [CRITERIO 2] Canal de control bidireccional para el equipo.
    [CRITERIO 4] El admin gestiona leads directamente desde Telegram.

    Configurar con el token TELEGRAM_ADMIN_BOT_TOKEN.
    Solo responde a chat_ids registrados en TELEGRAM_ADMIN_CHAT_IDS.
    """)
async def admin_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_admin_bot_webhook_secret:
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    update = Update.de_json(body, get_admin_bot())
    await get_admin_handler().handle_update(update, get_admin_bot())
    return {"ok": True}


# ─── SETUP ─────────────────────────────────────────────────────

@router.post("/setup-webhooks",
    summary="Configurar ambos webhooks",
    description="Registra los webhooks de AMBOS bots en Telegram.")
async def setup_both_webhooks():
    leads_username = await setup_leads_webhook()
    admin_username = await setup_admin_webhook()
    settings = get_settings()
    return {
        "success": True,
        "bot_leads": {
            "username": f"@{leads_username}",
            "webhook_url": settings.telegram_leads_webhook_url
        },
        "bot_admin": {
            "username": f"@{admin_username}",
            "webhook_url": settings.telegram_admin_bot_webhook_url
        }
    }

@router.post("/setup-leads-webhook",
    summary="Configurar solo webhook de leads")
async def setup_leads_wh():
    username = await setup_leads_webhook()
    settings = get_settings()
    return {"success": True, "username": f"@{username}",
            "webhook_url": settings.telegram_leads_webhook_url}

@router.post("/setup-admin-webhook",
    summary="Configurar solo webhook de admin")
async def setup_admin_wh():
    username = await setup_admin_webhook()
    settings = get_settings()
    return {"success": True, "username": f"@{username}",
            "webhook_url": settings.telegram_admin_bot_webhook_url}

@router.delete("/webhooks",
    summary="Eliminar ambos webhooks (usar polling en desarrollo)")
async def delete_both_webhooks():
    await delete_leads_webhook()
    await delete_admin_webhook()
    return {"success": True, "message": "Ambos webhooks eliminados"}


# ─── INFO ──────────────────────────────────────────────────────

@router.get("/info",
    summary="Estado de ambos bots",
    description="Retorna info completa del bot de leads y del bot de admin.")
async def get_bots_info():
    info = await get_both_bots_info()
    return {"success": True, "data": info}


# ─── SEND MESSAGE (Dashboard → Lead via bot de leads) ──────────

@router.post("/send-message",
    summary="Enviar mensaje a un lead desde el dashboard",
    description="El admin escribe desde el dashboard y el mensaje llega al lead vía bot de leads.")
async def send_message_to_lead(payload: dict):
    """
    El admin puede intervenir en una conversación desde el dashboard web.
    El mensaje se envía usando el bot de LEADS (no el de admin)
    para que el lead lo vea en el mismo chat donde siempre habla.
    """
    from database import get_db
    bot = get_leads_bot()
    db = get_db()
    chat_id = payload.get("chat_id")
    mensaje = payload.get("mensaje")
    lead_id = payload.get("lead_id")

    if not chat_id or not mensaje:
        raise HTTPException(status_code=400,
                            detail="chat_id y mensaje requeridos")

    await bot.send_message(
        chat_id=chat_id, text=mensaje, parse_mode="Markdown"
    )

    if lead_id:
        db.table("conversations").insert({
            "lead_id": lead_id, "role": "assistant",
            "content": mensaje, "agente": "admin_manual",
            "session_id": chat_id
        }).execute()
        from datetime import datetime, timezone
        db.table("leads").update(
            {"ultimo_contacto": datetime.now(timezone.utc).isoformat()}
        ).eq("id", lead_id).execute()

    return {"success": True, "message": "Mensaje enviado al lead vía bot de leads"}
```

---

## CAMBIO 8 — main.py (sección lifespan)

```python
# En el lifespan de FastAPI, reemplazar el setup del webhook único por:

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verificar Supabase
    try:
        db = get_db()
        db.table("empresas").select("id").limit(1).execute()
        print("✅ Supabase conectado")
    except Exception as e:
        print(f"⚠️ Supabase: {e}")

    # Configurar bots de Telegram
    if settings.ENVIRONMENT == "production":
        try:
            from telegram.bot import setup_leads_webhook, setup_admin_webhook, get_leads_bot, get_admin_bot
            leads_username = await setup_leads_webhook()
            admin_username = await setup_admin_webhook()
            print(f"✅ Bot Leads: @{leads_username} | webhook configurado")
            print(f"✅ Bot Admin: @{admin_username} | webhook configurado")
        except Exception as e:
            print(f"⚠️ Error configurando webhooks: {e}")
    else:
        try:
            from telegram.bot import delete_leads_webhook, delete_admin_webhook
            await delete_leads_webhook()
            await delete_admin_webhook()
            print("ℹ️ Modo desarrollo: webhooks eliminados (usar polling si es necesario)")
        except Exception:
            pass

    print("🛸 ORBITA iniciado — 2 bots activos | 5 agentes | Sistema listo")
    yield
```

---

## CAMBIO 9 — Estructura de archivos actualizada

```
orbita-backend/
├── telegram/
│   ├── __init__.py
│   ├── bot.py                  ← MODIFICADO: get_leads_bot() + get_admin_bot()
│   ├── leads_handler.py        ← RENOMBRADO: era handlers.py
│   ├── admin_bot_handler.py    ← NUEVO: comandos y acciones del admin
│   ├── voice_processor.py      ← SIN CAMBIOS
│   ├── message_builder.py      ← SIN CAMBIOS
│   └── admin_notifier.py       ← MODIFICADO: usa get_admin_bot(), multi-admin
```

---

## CAMBIO 10 — Frontend /configuracion y /telegram

### En /configuracion — sección "Configuración de Telegram":

Reemplazar la card única por dos cards lado a lado:

**Card 1 — Bot de Leads** (borde verde):
- Username del bot: `@bot_username`
- Badge "● ACTIVO" pulsante
- Link: `https://t.me/@bot_username`
- Descripción: "Este es el bot que compartes con tus prospectos"
- Botón "🔄 Reconfigurar Webhook leads"

**Card 2 — Bot de Admin** (borde azul):
- Username del bot: `@admin_bot_username`
- Badge "● ACTIVO"
- Descripción: "Este bot es solo para tu equipo interno"
- Lista de Chat IDs de admins registrados
- Botón "🔄 Reconfigurar Webhook admin"

### En /telegram — reemplazar sección "Estado del Bot":

Dos cards paralelas: "Bot de Leads" | "Bot de Admin"

Cada una con sus métricas independientes.

Llamar a `orbitaApi.getBotInfo()` que ahora retorna `{bot_leads: {...}, bot_admin: {...}}`

Botón único "🔄 Configurar Ambos Webhooks" → `orbitaApi.setupWebhooks()`

---

## INSTRUCCIONES DE SETUP ACTUALIZADAS

### Paso 1 — Crear los dos bots en BotFather

```
En Telegram → @BotFather:

Bot 1 (leads):
  /newbot
  Nombre: ORBITA Asistente
  Username: orbita_cliente_bot (o el que prefieras)
  → Copiar token → TELEGRAM_LEADS_BOT_TOKEN

Bot 2 (admin):
  /newbot
  Nombre: ORBITA Admin Panel
  Username: orbita_admin_bot
  → Copiar token → TELEGRAM_ADMIN_BOT_TOKEN

IMPORTANTE — Configurar privacidad del bot admin:
  /mybots → orbita_admin_bot → Bot Settings → Group Privacy → Turn OFF
  (para que no aparezca en búsquedas públicas)
```

### Paso 2 — Obtener Chat IDs de los admins

```
Cada miembro del equipo que quiera recibir alertas debe:
1. Escribir a @userinfobot en Telegram
2. Copiar el número que aparece como "Id:"
3. Agregarlos separados por coma en .env:
   TELEGRAM_ADMIN_CHAT_IDS=123456789,987654321
```

### Paso 3 — Configurar webhooks

```bash
# Con el servidor corriendo y ngrok activo:
curl -X POST http://localhost:8000/api/v1/telegram/setup-webhooks

# Respuesta esperada:
{
  "success": true,
  "bot_leads": {"username": "@orbita_cliente_bot", "webhook_url": "..."},
  "bot_admin": {"username": "@orbita_admin_bot", "webhook_url": "..."}
}
```

### Paso 4 — Probar cada bot

```
Bot de leads — escribe desde cualquier cuenta:
  "Hola, me interesa conocer sus servicios"
  → Debe responder el agente conversacional ✅

Bot de admin — escribe desde tu cuenta registrada:
  /start → debe mostrar el panel de control ✅
  /leads → debe mostrar los últimos leads ✅
  /stats → debe mostrar resumen del día ✅
  /alertas → debe correr el Agente Analítico ✅
```

---

## RESUMEN DE LO QUE CAMBIA VS LO QUE QUEDA IGUAL

| Archivo | Cambio |
|---|---|
| `.env.example` | Reemplazar sección Telegram (2 tokens, 2 secrets) |
| `config.py` | Nuevos campos para 2 bots + property `admin_chat_ids_list` |
| `telegram/bot.py` | Reemplazar completo (2 bots) |
| `telegram/handlers.py` | Renombrar a `leads_handler.py` + cambiar `get_bot()` → `get_leads_bot()` |
| `telegram/admin_bot_handler.py` | **NUEVO** — toda la lógica del bot admin |
| `telegram/admin_notifier.py` | Cambiar constructor + nuevo `_send_to_all_admins()` |
| `routers/telegram.py` | Reemplazar completo (2 webhooks) |
| `main.py` | Actualizar lifespan (setup de 2 bots) |
| `agents/*.py` | **SIN CAMBIOS** — los agentes no saben de bots |
| `database.py`, `auth.py` | **SIN CAMBIOS** |
| `models/`, `routers/` (resto) | **SIN CAMBIOS** |
| Frontend `/configuracion` | Dos cards de Telegram |
| Frontend `/telegram` | Dos cards de estado de bots |

---

*ORBITA · Sistema Inteligente de Ventas para Empresas de Servicios*
*"Un bot para captar. Otro bot para controlar."*
