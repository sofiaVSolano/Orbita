#!/usr/bin/env python3
"""
SOLUCIÓN ALTERNATIVA: Ejecutar polling sin asyncio.run()

El problema es que docker exec -it causa conflictos con asyncio.
Esta versión integra polling directamente sin necesidad de asyncio.run()

Ejecutar con:
    docker run -it ... python -c "from run_polling_simple import start_polling; start_polling()"

O mejor, desde el código FastAPI directamente.
"""

import asyncio
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram import Update

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Reducir ruido de logs
)

def get_handlers():
    """Retornar handlers comunes."""
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 ¡Hola! Bienvenido a ORBITA.\n\n"
            "Soy tu asistente de ventas inteligente.\n"
            "¿En qué puedo ayudarte hoy?"
        )

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_text = update.message.text
        user_name = update.effective_user.first_name
        
        print(f"\n✅ LEADS BOT - Mensaje:")
        print(f"   📱 {user_name}: {message_text}")
        
        await update.message.reply_text(
            f"✅ Recibí tu mensaje.\n"
            f"Procesando con agentes IA..."
        )
    
    return {
        "start": start,
        "message": handle_message
    }

def create_leads_app():
    """Crear aplicación del bot de leads."""
    from config import get_settings
    
    settings = get_settings()
    app = Application.builder().token(settings["telegram_leads_bot_token"]).build()
    
    handlers = get_handlers()
    app.add_handler(CommandHandler("start", handlers["start"]))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers["message"]))
    
    return app

# ─── PARA USAR DESDE MAIN.PY ──────────────────────────────────────

def start_leads_bot_polling():
    """
    Iniciar polling del bot de leads.
    Se ejecuta en un thread separado desde main.py
    """
    print("\n🤖 Iniciando polling del Bot de Leads...")
    app = create_leads_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)
