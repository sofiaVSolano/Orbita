# Integración con Telegram Bot para ORBITA
# [CRITERIO 1] - Telegram como canal principal de conversación

__version__ = "1.0.0"

from .bot import (
    get_leads_bot,
    get_admin_bot,
    setup_leads_webhook,
    setup_admin_webhook,
    delete_leads_webhook,
    delete_admin_webhook,
    get_both_bots_info
)

from .leads_handler import LeadsBotHandler
from .admin_bot_handler import AdminBotHandler

__all__ = [
    "get_leads_bot",
    "get_admin_bot",
    "setup_leads_webhook",
    "setup_admin_webhook",
    "delete_leads_webhook",
    "delete_admin_webhook",
    "get_both_bots_info",
    "LeadsBotHandler",
    "AdminBotHandler"
]
