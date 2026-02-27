#!/usr/bin/env python3
"""
Bot de Leads - Polling simple para MODO DESARROLLO.
Ejecutar: python run_leads_bot.py
"""

import asyncio
import logging
import sys
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import Update, Bot
from config import get_settings
from Telegram_Bot.leads_handler import LeadsBotHandler

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Inicializar el handler de leads
leads_handler = LeadsBotHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido a ORBITA.\n\n"
        "Soy tu asistente de ventas inteligente.\n"
        "¿En qué puedo ayudarte hoy?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delega el manejo del mensaje al LeadsBotHandler."""
    bot = context.bot
    await leads_handler.handle_update(update, bot)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de botones inline."""
    bot = context.bot
    await leads_handler.handle_update(update, bot)

async def cleanup_webhooks(token: str):
    """Limpiar webhooks de manera asincrónica."""
    try:
        bot = Bot(token=token)
        await bot.delete_webhook()
        print("✅ Webhooks eliminados correctamente")
    except Exception as e:
        print(f"⚠️  Error eliminando webhooks: {e}")

async def main():
    settings = get_settings()
    
    print("\n" + "="*70)
    print("🤖 BOT DE LEADS - POLLING INICIADO")
    print("="*70)
    print(f"Token: {settings['telegram_leads_bot_token'][:20]}...")
    print("="*70 + "\n")
    
    # Limpiar webhooks
    print("🔧 Limpiando configuración de webhooks...")
    await cleanup_webhooks(settings["telegram_leads_bot_token"])
    
    # Crear aplicación
    app = (
        Application.builder()
        .token(settings["telegram_leads_bot_token"])
        .build()
    )
    
    # Inicializar la aplicación explícitamente
    await app.initialize()
    
    try:
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.VOICE, handle_message))  # Soporte para notas de voz
        app.add_handler(CallbackQueryHandler(handle_callback))  # Soporte para botones inline
        
        print("✅ Bot de Leads listo para recibir mensajes\n")
        print("✅ Integración con agentes IA activada\n")
        print("Pulsa Ctrl+C para detener\n")
        
        # Iniciar polling
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Mantener el bot corriendo
        await asyncio.Event().wait()
        
    finally:
        # Cleanup apropiado
        print("\n🔧 Deteniendo bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot detenido correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
