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
        _leads_bot = Bot(token=settings["telegram_leads_bot_token"])
    return _leads_bot


def get_leads_application() -> Application:
    global _leads_application
    if not _leads_application:
        settings = get_settings()
        _leads_application = (
            Application.builder()
            .token(settings["telegram_leads_bot_token"])
            .build()
        )
    return _leads_application


async def setup_leads_webhook():
    """Registra el webhook del bot de leads."""
    settings = get_settings()
    bot = get_leads_bot()
    await bot.set_webhook(
        url=settings["telegram_leads_webhook_url"],
        secret_token=settings["telegram_leads_webhook_secret"],
        allowed_updates=["message", "callback_query"]
    )
    info = await bot.get_me()
    return info.username


async def delete_leads_webhook():
    """Elimina el webhook del bot de leads."""
    await get_leads_bot().delete_webhook()


# ─── BOT DE ADMIN ─────────────────────────────────────────────

def get_admin_bot() -> Bot:
    """Bot exclusivo para el equipo interno y gerente."""
    global _admin_bot
    if not _admin_bot:
        settings = get_settings()
        _admin_bot = Bot(token=settings["telegram_admin_bot_token"])
    return _admin_bot


def get_admin_application() -> Application:
    global _admin_application
    if not _admin_application:
        settings = get_settings()
        _admin_application = (
            Application.builder()
            .token(settings["telegram_admin_bot_token"])
            .build()
        )
    return _admin_application


async def setup_admin_webhook():
    """Registra el webhook del bot de admin."""
    settings = get_settings()
    bot = get_admin_bot()
    await bot.set_webhook(
        url=settings["telegram_admin_bot_webhook_url"],
        secret_token=settings["telegram_admin_bot_webhook_secret"],
        allowed_updates=["message", "callback_query"]
    )
    info = await bot.get_me()
    return info.username


async def delete_admin_webhook():
    """Elimina el webhook del bot de admin."""
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

