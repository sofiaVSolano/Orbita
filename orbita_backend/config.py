# Configuración global del sistema ORBITA
# [CRITERIO 2] - Variables de entorno para configuración

import os
from typing import Optional

# Configuración de base de datos
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configuración de Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuración de OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de Telegram — BOT DE LEADS (público)
TELEGRAM_LEADS_BOT_TOKEN = os.getenv("TELEGRAM_LEADS_BOT_TOKEN")
TELEGRAM_LEADS_WEBHOOK_SECRET = os.getenv("TELEGRAM_LEADS_WEBHOOK_SECRET", "orbita-leads-secret-2026")
TELEGRAM_LEADS_WEBHOOK_URL = os.getenv("TELEGRAM_LEADS_WEBHOOK_URL")

# Configuración de Telegram — BOT DE ADMIN (privado)
TELEGRAM_ADMIN_BOT_TOKEN = os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")
TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET = os.getenv("TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET", "orbita-admin-secret-2026")
TELEGRAM_ADMIN_BOT_WEBHOOK_URL = os.getenv("TELEGRAM_ADMIN_BOT_WEBHOOK_URL")

# Chat IDs de administradores (separados por coma)
TELEGRAM_ADMIN_CHAT_IDS = os.getenv("TELEGRAM_ADMIN_CHAT_IDS", "")

# Configuración del servidor
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Configuración de autenticación
JWT_SECRET_KEY = os.getenv("JWT_SECRET", "orbita-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de la empresa (identidad del agente)
EMPRESA_NOMBRE = os.getenv("EMPRESA_NOMBRE", "ORBITA AI Solutions")
EMPRESA_DESCRIPCION = os.getenv("EMPRESA_DESCRIPCION", "Sistema integral de gestión de leads con IA multi-agente")
EMPRESA_SECTOR = os.getenv("EMPRESA_SECTOR", "Tecnología e Inteligencia Artificial")
EMPRESA_SERVICIOS = [
    "Desarrollo de sistemas con IA",
    "Automatización de procesos", 
    "Chatbots inteligentes",
    "Análisis predictivo",
    "Consultoría en IA"
]

# Configuración de los modelos de IA — cada agente puede tener su modelo
GROQ_MODELS = {
    "orchestrator": os.getenv("GROQ_MODEL_ORCHESTRATOR", "llama-3.1-8b-instant"),  # Modelo rápido y económico
    "captador": os.getenv("GROQ_MODEL_CAPTADOR", "llama-3.1-8b-instant"),  # Modelo rápido
    "conversacional": os.getenv("GROQ_MODEL_CONVERSACIONAL", "llama-3.1-8b-instant"),
    "identidad": os.getenv("GROQ_MODEL_IDENTIDAD", "llama-3.1-8b-instant"),
    "comunicacion": os.getenv("GROQ_MODEL_COMUNICACION", "llama-3.1-8b-instant"),
    "analitico": os.getenv("GROQ_MODEL_ANALITICO", "llama-3.1-8b-instant")
}

# Configuración para usar OpenAI en el orchestrador
USE_OPENAI_FOR_ORCHESTRATOR = os.getenv("USE_OPENAI_FOR_ORCHESTRATOR", "true").lower() == "true"
OPENAI_MODEL_ORCHESTRATOR = os.getenv("OPENAI_MODEL_ORCHESTRATOR", "gpt-4o-mini")

# Configuración de transcripción de voz
TRANSCRIPTION_MODEL = "whisper-large-v3"

def get_settings():
    """Obtiene todas las configuraciones del sistema"""
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_key": SUPABASE_KEY,
        "groq_api_key": GROQ_API_KEY,
        "openai_api_key": OPENAI_API_KEY,
        "telegram_leads_bot_token": TELEGRAM_LEADS_BOT_TOKEN,
        "telegram_leads_webhook_secret": TELEGRAM_LEADS_WEBHOOK_SECRET,
        "telegram_leads_webhook_url": TELEGRAM_LEADS_WEBHOOK_URL,
        "telegram_admin_bot_token": TELEGRAM_ADMIN_BOT_TOKEN,
        "telegram_admin_bot_webhook_secret": TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET,
        "telegram_admin_bot_webhook_url": TELEGRAM_ADMIN_BOT_WEBHOOK_URL,
        "telegram_admin_chat_ids": TELEGRAM_ADMIN_CHAT_IDS,
        "host": HOST,
        "port": PORT,
        "debug": DEBUG,
        "jwt_secret_key": JWT_SECRET_KEY,
        "jwt_algorithm": JWT_ALGORITHM,
        "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "empresa_nombre": EMPRESA_NOMBRE,
        "empresa_descripcion": EMPRESA_DESCRIPCION,
        "empresa_sector": EMPRESA_SECTOR,
        "empresa_servicios": EMPRESA_SERVICIOS,
        "groq_models": GROQ_MODELS,
        "transcription_model": TRANSCRIPTION_MODEL
    }

def get_admin_chat_ids_list() -> list:
    """
    Parsea los chat IDs de administrador desde la configuración.
    Retorna una lista de strings.
    Uso: chat_ids = get_admin_chat_ids_list()
    """
    return [
        cid.strip()
        for cid in TELEGRAM_ADMIN_CHAT_IDS.split(",")
        if cid.strip()
    ]

def validate_environment():
    """Valida que todas las variables de entorno críticas estén configuradas"""
    missing_vars = []
    
    if not SUPABASE_URL:
        missing_vars.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing_vars.append("SUPABASE_KEY")
    if not GROQ_API_KEY:
        missing_vars.append("GROQ_API_KEY")
    if not TELEGRAM_LEADS_BOT_TOKEN:
        missing_vars.append("TELEGRAM_LEADS_BOT_TOKEN")
    if not TELEGRAM_ADMIN_BOT_TOKEN:
        missing_vars.append("TELEGRAM_ADMIN_BOT_TOKEN")
        
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        return False
    
    print("✅ Todas las variables de entorno críticas están configuradas")
    return True

# Configuración específica por entorno
environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    # Configuración para producción
    DEBUG = False
    _jwt_key = os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY")
    if not _jwt_key:
        raise ValueError("JWT_SECRET debe estar configurada en .env")
    JWT_SECRET_KEY = _jwt_key
elif environment == "development":
    # Configuración para desarrollo
    DEBUG = True
    print("🔧 Modo desarrollo activado")

print(f"🌍 Entorno: {environment}")
print(f"🚀 Host configurado: {HOST}:{PORT}")