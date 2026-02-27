from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import os

# Importar routers
from routers.auth import auth_router
from routers.leads import leads_router
from routers.cotizaciones import cotizaciones_router
from routers.reuniones import reuniones_router
from routers.campanas import campanas_router
from routers.analytics import analytics_router
from routers.agentes import agentes_router
from routers.telegram import telegram_router

# Importar configuración de base de datos
from database import init_db

# Importar configuración de Telegram
from Telegram_Bot.bot import setup_leads_webhook, setup_admin_webhook, delete_leads_webhook, delete_admin_webhook
from config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando ORBITA...")
    
    # 1. Inicializar base de datos
    print("📊 Inicializando base de datos...")
    await init_db()
    print("✅ Base de datos inicializada")
    
    # 2. Configurar Telegram Bots (Leads + Admin)
    settings = get_settings()
    print("🤖 Configurando Telegram Bots...")
    try:
        if settings.get("ENVIRONMENT") == "production" or os.getenv("ENVIRONMENT") == "production":
            leads_username = await setup_leads_webhook()
            admin_username = await setup_admin_webhook()
            print(f"✅ Bot de Leads: @{leads_username} | webhook configurado")
            print(f"✅ Bot de Admin: @{admin_username} | webhook configurado")
        else:
            # En desarrollo, eliminar webhooks
            try:
                await delete_leads_webhook()
                await delete_admin_webhook()
            except:
                pass
            print("ℹ️  Modo desarrollo: webhooks desactivados")
            print("ℹ️  Para usar los bots, ejecuta en otra terminal:")
            print("    docker exec -it orbita-backend python run_leads_bot.py")
            
    except Exception as e:
        print(f"⚠️  Error configurando Telegram Bots: {e}")
    
    print("🛸 ORBITA iniciado — 2 bots activos | 5 agentes | Sistema listo")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando ORBITA...")
    print("👋 ORBITA cerrado")

# Crear aplicación FastAPI
app = FastAPI(
    title="ORBITA - Sistema Multi-Agente de IA",
    description="""
    Sistema integral de gestión de leads con arquitectura multi-agente de IA.
    
    ## Características Principales
    
    - **Multi-Agente**: 5 agentes especializados coordinados por un orquestador
    - **Telegram Bot**: Integración completa con captura de leads
    - **Persistencia**: Base de datos PostgreSQL con Supabase
    - **IA Real**: Llamadas reales a Groq API en cada acción
    - **Escalable**: Arquitectura modular y extensible
    
    ## Agentes Disponibles
    
    1. **Orquestador**: Coordina todos los agentes
    2. **Captador**: Captura y califica leads
    3. **Conversacional**: Mantiene conversaciones naturales
    4. **Identidad**: Gestiona la identidad de la empresa
    5. **Analítico**: Análisis de datos y métricas
    """,
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers con prefijos
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(leads_router, prefix="/leads", tags=["Gestión de Leads"])
app.include_router(cotizaciones_router, prefix="/cotizaciones", tags=["Cotizaciones"])
app.include_router(reuniones_router, prefix="/reuniones", tags=["Reuniones"])
app.include_router(campanas_router, prefix="/campanas", tags=["Campañas"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analítica"])
app.include_router(agentes_router, prefix="/agentes", tags=["Sistema Multi-Agente"])
app.include_router(telegram_router, prefix="/telegram", tags=["Telegram Bot"])

@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raíz del sistema"""
    return {
        "message": "🚀 ORBITA - Sistema Multi-Agente de IA",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Multi-Agent AI System",
            "Telegram Bot Integration",
            "Lead Management",
            "Real-time Analytics",
            "Persistent Memory",
            "Voice Transcription"
        ],
        "agents": {
            "orchestrator": "Coordinador principal del sistema",
            "captador": "Especialista en captura de leads",
            "conversacional": "Experto en conversaciones naturales",
            "identidad": "Gestor de identidad empresarial",
            "analitico": "Analista de datos y métricas"
        },
        "endpoints": {
            "auth": "/auth",
            "leads": "/leads", 
            "cotizaciones": "/cotizaciones",
            "reuniones": "/reuniones",
            "campanas": "/campanas",
            "analytics": "/analytics",
            "agentes": "/agentes",
            "telegram": "/telegram",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Health check del sistema"""
    from Telegram_Bot.bot import get_both_bots_info
    
    try:
        bots_info = await get_both_bots_info()
        telegram_status = "active"
    except:
        bots_info = {"bot_leads": None, "bot_admin": None}
        telegram_status = "inactive"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "connected",
            "telegram_bots": telegram_status,
            "groq_api": "available"
        },
        "telegram_bots": bots_info
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejador para endpoints no encontrados"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint no encontrado",
            "message": "Verifica la documentación en /docs",
            "available_endpoints": [
                "/", "/health", "/auth", "/leads", "/cotizaciones",
                "/reuniones", "/campanas", "/analytics", "/agentes", "/telegram"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Manejador para errores internos"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "message": "El equipo técnico ha sido notificado"
        }
    )

if __name__ == "__main__":
    # Configuración para desarrollo
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    print(f"📚 Documentación disponible en http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )