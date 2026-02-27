#!/usr/bin/env python3
"""
Bot de Leads - Polling simple para MODO DESARROLLO.
Ejecutar: python run_leads_bot.py
"""

import asyncio
import logging
import sys
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram import Update, Bot
from config import get_settings

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    
    print(f"\n✅ LEADS BOT - Mensaje recibido:")
    print(f"   Chat ID: {chat_id}")
    print(f"   Usuario: {user_name}")
    print(f"   Texto: {message_text}\n")
    
    await update.message.reply_text(
        f"👍 Hola {user_name}!\n\n"
        f"Recibí tu mensaje: '{message_text}'\n\n"
        f"El sistema está procesando tu solicitud con nuestros agentes IA...\n\n"
        f"⏳ Respuesta en progreso..."
    )

if __name__ == "__main__":
    settings = get_settings()
    
    print("\n" + "="*70)
    print("🤖 BOT DE LEADS - POLLING INICIADO")
    print("="*70)
    print(f"Token: {settings['telegram_leads_bot_token'][:20]}...")
    print("="*70 + "\n")
    
    # Crear instancia del bot
    bot = Bot(token=settings["telegram_leads_bot_token"])
    
    # Limpiar webhooks SINCRONAMENTE (bloqueante)
    print("🔧 Limpiando configuración de webhooks...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.delete_webhook())
        loop.close()
        print("✅ Webhooks eliminados correctamente")
    except Exception as e:
        print(f"⚠️  Error eliminando webhooks: {e}")
    
    # Dar un momento a Telegram para procesar
    import time
    time.sleep(2)
    
    # Ahora iniciar polling
    app = (
        Application.builder()
        .token(settings["telegram_leads_bot_token"])
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot de Leads listo para recibir mensajes\n")
    print("Pulsa Ctrl+C para detener\n")
    
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
