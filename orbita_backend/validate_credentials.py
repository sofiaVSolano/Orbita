#!/usr/bin/env python3
"""
Script de validación de credenciales ORBITA
Verifica que todas las variables de entorno requeridas estén configuradas
"""

import os
import sys
from pathlib import Path

# Cargar .env manualmente si existe
env_file = Path(".env")
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_var(var_name, required=True, description=""):
    """Verifica si una variable de entorno existe"""
    value = os.getenv(var_name)
    status = "✅" if value else "❌" if required else "⚠️"
    
    if value:
        # Mostrar solo primeros y últimos 10 caracteres de secretos
        if any(secret in var_name.upper() for secret in ['TOKEN', 'KEY', 'SECRET', 'PASSWORD']):
            display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
        else:
            display_value = value
        print(f"{status} {var_name:<40} = {display_value}")
    else:
        if required:
            print(f"{status} {var_name:<40} {RED}[REQUERIDO]{RESET}")
        else:
            print(f"{status} {var_name:<40} {YELLOW}[OPCIONAL]{RESET}")
    
    return bool(value)

print(f"\n{BLUE}{'='*80}{RESET}")
print(f"{BOLD}{BLUE}VALIDACIÓN DE CREDENCIALES - ORBITA{RESET}")
print(f"{BLUE}{'='*80}{RESET}\n")

# Rastrear resultado
all_required_ok = True

# 1. SUPABASE
print(f"{BOLD}1. SUPABASE DATABASE{RESET}")
all_required_ok &= check_var("SUPABASE_URL", required=True)
all_required_ok &= check_var("SUPABASE_KEY", required=True)
print()

# 2. GROQ API
print(f"{BOLD}2. GROQ AI API{RESET}")
all_required_ok &= check_var("GROQ_API_KEY", required=True)
check_var("GROQ_MODEL_ORCHESTRATOR", required=False)
check_var("GROQ_MODEL_CAPTADOR", required=False)
check_var("GROQ_MODEL_CONVERSACIONAL", required=False)
check_var("GROQ_MODEL_IDENTIDAD", required=False)
check_var("GROQ_MODEL_COMUNICACION", required=False)
check_var("GROQ_MODEL_ANALITICO", required=False)
print()

# 3. TELEGRAM - LEADS BOT
print(f"{BOLD}3. TELEGRAM - BOT DE LEADS (Público){RESET}")
all_required_ok &= check_var("TELEGRAM_LEADS_BOT_TOKEN", required=True)
check_var("TELEGRAM_LEADS_WEBHOOK_URL", required=False)
check_var("TELEGRAM_LEADS_WEBHOOK_SECRET", required=False)
print()

# 4. TELEGRAM - ADMIN BOT
print(f"{BOLD}4. TELEGRAM - BOT DE ADMIN (Privado){RESET}")
all_required_ok &= check_var("TELEGRAM_ADMIN_BOT_TOKEN", required=True)
check_var("TELEGRAM_ADMIN_BOT_WEBHOOK_URL", required=False)
check_var("TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET", required=False)
all_required_ok &= check_var("TELEGRAM_ADMIN_CHAT_IDS", required=True)
print()

# 5. JWT & AUTH
print(f"{BOLD}5. AUTENTICACIÓN JWT{RESET}")
all_required_ok &= check_var("JWT_SECRET", required=True)
check_var("JWT_ALGORITHM", required=False)
check_var("ACCESS_TOKEN_EXPIRE_MINUTES", required=False)
print()

# 6. ADMIN CREDENTIALS
print(f"{BOLD}6. CREDENCIALES DE ADMIN{RESET}")
check_var("ADMIN_EMAIL", required=False)
check_var("ADMIN_PASSWORD", required=False)
print()

# 7. APP SETTINGS
print(f"{BOLD}7. CONFIGURACIÓN DE APLICACIÓN{RESET}")
check_var("FRONTEND_URL", required=False)
check_var("ENVIRONMENT", required=False)
check_var("HOST", required=False)
check_var("PORT", required=False)
print()

# 8. COMPANY SETTINGS
print(f"{BOLD}8. CONFIGURACIÓN DE EMPRESA{RESET}")
check_var("EMPRESA_NOMBRE", required=False)
check_var("EMPRESA_SECTOR", required=False)
check_var("EMPRESA_DESCRIPCION", required=False)
print()

# RESUMEN
print(f"{BLUE}{'='*80}{RESET}")
if all_required_ok:
    print(f"{GREEN}{BOLD}✅ TODAS LAS CREDENCIALES REQUERIDAS ESTÁN CONFIGURADAS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    sys.exit(0)
else:
    print(f"{RED}{BOLD}❌ FALTAN CREDENCIALES REQUERIDAS{RESET}")
    print(f"{YELLOW}Por favor, configura los archivos .env en:{RESET}")
    print(f"  • orbita_backend/.env")
    print(f"  • orbita_frontend/.env")
    print(f"{BLUE}{'='*80}{RESET}\n")
    sys.exit(1)
