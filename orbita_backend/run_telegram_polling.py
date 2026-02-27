#!/usr/bin/env python3
"""
Script para iniciar polling de los bots Telegram en MODO DESARROLLO.

En desarrollo es preferible usar polling (long-polling) en lugar de webhooks,
porque permite testear localmente sin exponer un URL público.

Ejecutar:
    python run_telegram_polling.py
"""

import asyncio
import logging
import threading
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram import Update
from config import get_settings

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start para el bot de leads."""
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido a ORBITA.\n\n"
        "Soy tu asistente de ventas inteligente.\n"
        "¿En qué puedo ayudarte hoy?"
    )

async def handle_leads_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar mensajes de texto del bot de leads."""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message_text = update.message.text
        
        print(f"\n📱 Mensaje recibido (Leads Bot):")
        print(f"   Chat ID: {chat_id}")
        print(f"   Usuario: {update.effective_user.first_name}")
        print(f"   Mensaje: {message_text}\n")
        
        # Responder de inmediato
        await update.message.reply_text(
            "👍 Mensaje recibido. El sistema está procesando tu solicitud...\n"
            "Respuesta pendiente de agentes IA."
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text(f"❌ Error al procesar: {str(e)[:100]}")

async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start para el bot admin."""
    await update.message.reply_text(
        "🔐 Panel Administrativo\n\n"
        "Comandos disponibles:\n"
        "/help - Ver todos los comandos\n"
        "/leads - Ver estadísticas de leads\n"
        "/agents - Estado de agentes"
    )

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar mensajes del bot admin."""
    print(f"\n🔐 Comando Admin:")
    print(f"   Chat ID: {update.effective_chat.id}")
    print(f"   Mensaje: {update.message.text}\n")
    
    await update.message.reply_text(
        "✅ Comando recibido.\n"
        "Panel admin disponible."
    )

def run_leads_polling(app):
    """Ejecutar polling del bot de leads en thread separado."""
    asyncio.run(app.run_polling(allowed_updates=Update.ALL_TYPES))

def run_admin_polling(app):
    """Ejecutar polling del bot admin en thread separado."""
    asyncio.run(app.run_polling(allowed_updates=Update.ALL_TYPES))

async def main():
    """Iniciar polling para ambos bots en threads separados."""
    settings = get_settings()
    
    print("\n" + "="*70)
    print("🚀 INICIANDO TELEGRAM POLLING (MODO DESARROLLO)")
    print("="*70 + "\n")
    
    # ─── BOT DE LEADS ───────────────────────────────────────────────────
    print("📱 Inicializando Bot de Leads (@OrbitaOficialBot)...")
    leads_app = (
        Application.builder()
        .token(settings["telegram_leads_bot_token"])
        .build()
    )
    
    # Handlers para el bot de leads
    leads_app.add_handler(CommandHandler("start", start_leads))
    leads_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_leads_text))
    
    # ─── BOT DE ADMIN ────────────────────────────────────────────────────
    print("📱 Inicializando Bot Admin (@Orbita_hack_bot)...")
    admin_app = (
        Application.builder()
        .token(settings["telegram_admin_bot_token"])
        .build()
    )
    
    # Handlers para el bot admin
    admin_app.add_handler(CommandHandler("start", start_admin))
    admin_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))
    
    # ─── INICIAR POLLING EN THREADS SEPARADOS ──────────────────────────
    print("✅ Bots configurados correctamente\n")
    print("🔄 Iniciando polling en threads separados...\n")
    print("="*70)
    print("📌 LISTO PARA RECIBIR MENSAJES")
    print("="*70 + "\n")
    
    # Crear threads para cada bot
    leads_thread = threading.Thread(target=run_leads_polling, args=(leads_app,), daemon=True)
    admin_thread = threading.Thread(target=run_admin_polling, args=(admin_app,), daemon=True)
    
    # Iniciar threads
    leads_thread.start()
    admin_thread.start()
    
    # Mantener el programa corriendo
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Polling detenido")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Telegram Polling cerrado")
