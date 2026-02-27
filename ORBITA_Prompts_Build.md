# ORBITA — Prompts de Construcción del Sistema
## Sistema Inteligente de Ventas para Empresas de Servicios
## Hackathon AI First 2026 — Funnelchat
### Parte 1 → GitHub Copilot (Backend) | Parte 2 → Lovable (Frontend)

---

# ╔══════════════════════════════════════════════════════════════╗
# ║   PARTE 1 — BACKEND  →  Pegar en GitHub Copilot Agent Mode  ║
# ╚══════════════════════════════════════════════════════════════╝

```
Eres un senior backend developer experto en Python, FastAPI, y
arquitecturas multi-agente. Construye el backend completo para ORBITA:
sistema inteligente autónomo de gestión de leads y ventas para
empresas de servicios (consultoría, marketing, tecnología, salud,
educación privada, legal, contable — cualquier empresa que venda
servicios B2B o B2C).

ORBITA resuelve 4 problemas críticos de cualquier empresa de servicios:
1. Respuestas tardías → leads que se enfrían antes de ser atendidos
2. Pérdida de ventas → seguimiento manual inconsistente
3. Falta de seguimiento → el equipo olvida contactar leads activos
4. Saturación del equipo → tareas repetitivas consumen tiempo valioso

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITERIOS OFICIALES DEL HACKATHON — COMENTAR EN CADA ARCHIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cada archivo relevante debe tener al inicio: # [CRITERIO N - descripción]

[CRITERIO 1] DISEÑO CONVERSACIONAL
→ Flujos naturales con contexto persistente por session_id
→ Memoria completa guardada en Supabase (tabla conversations)
→ Técnica AIDA aplicada: Atención → Interés → Deseo → Acción
→ El sistema NUNCA pierde el hilo — historial completo en cada llamada
→ Telegram es el canal principal de conversación con los leads

[CRITERIO 2] ARQUITECTURA MULTI-AGENTE (mínimo 2 capas)
→ Capa 1: Agente ORBITA Orquestador (decide qué agente activar)
→ Capa 2: 5 agentes especializados con roles y modelos propios
→ Capa 3 (diferenciador): agentes se comunican entre sí
  (Conversacional → solicita validación a Identidad antes de enviar)
→ Telegram Bot actúa como canal de entrada/salida de los agentes

[CRITERIO 3] USO REAL DE IA — NUNCA MOCKUPS
→ Llamadas reales a Groq API en CADA acción de agente
→ Whisper (vía Groq) para transcribir notas de voz de Telegram
→ Respuestas 100% generadas por LLM, jamás hardcodeadas
→ Logging de modelo, tokens y latencia en cada llamada

[CRITERIO 4] APLICABILIDAD EN 30 DÍAS
→ Stack productivo desde día 1: FastAPI + Supabase + Groq + Telegram = $0
→ Cualquier empresa de servicios puede desplegar en <1 hora
→ GET /health demuestra que el sistema está operativo
→ README con despliegue completo en 10 pasos

[CRITERIO 5] ESCALABILIDAD
→ Supabase escala sin intervención manual
→ empresa_id en todas las tablas (multi-tenant: múltiples clientes)
→ Agentes como clases independientes (fácil agregar más)
→ Webhook de Telegram maneja carga alta sin bloqueo

[CRITERIO 6] CLARIDAD DE INTEGRACIÓN
→ Swagger completo en /docs
→ Contrato JSON consistente en todos los endpoints
→ Webhook Telegram documentado para configuración externa
→ Headers X-ORBITA-Agent y X-ORBITA-Version en cada respuesta

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CREDENCIALES — USAR TAL CUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPABASE_URL = https://xiblghevwgzuhytcqpyg.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYmxnaGV2d2d6dWh5dGNxcHlnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjE1NDg1NCwiZXhwIjoyMDg3NzMwODU0fQ.GtjuBJxNvl3Ovv0rFggUy3ZMdTI1Ks3pNUlyCIkT9RQ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODELOS IA — TODOS GRATUITOS EN GROQ (console.groq.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agente ORBITA Orquestador    → llama-3.3-70b-versatile
Agente 01 Captador           → gemma2-9b-it
Agente 02 Conversacional     → llama-3.3-70b-versatile
Agente 03 Identidad          → mixtral-8x7b-32768
Agente 04 Comunicación       → llama-3.1-8b-instant
Agente 05 Analítico          → llama-3.1-8b-instant
Transcripción de voz         → whisper-large-v3 (vía Groq API)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPENDENCIAS — requirements.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fastapi==0.111.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
supabase==2.5.0
groq==0.9.0
python-telegram-bot==21.3
pydantic==2.7.0
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.0
tenacity==8.3.0
aiofiles==23.2.1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VARIABLES DE ENTORNO — .env.example
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Supabase
SUPABASE_URL=https://xiblghevwgzuhytcqpyg.supabase.co
SUPABASE_KEY=TU_SERVICE_ROLE_KEY

# Groq (gratis en console.groq.com)
GROQ_API_KEY=TU_GROQ_API_KEY

# Telegram
TELEGRAM_BOT_TOKEN=TU_BOT_TOKEN_DE_BOTFATHER
TELEGRAM_ADMIN_CHAT_ID=TU_CHAT_ID_DE_ADMIN
TELEGRAM_WEBHOOK_SECRET=orbita-webhook-secret-2026
TELEGRAM_WEBHOOK_URL=https://TU-DOMINIO.com/api/v1/telegram/webhook

# Auth
JWT_SECRET=orbita-hackathon-2026-secret
JWT_ALGORITHM=HS256
ADMIN_EMAIL=admin@orbita.ai
ADMIN_PASSWORD=orbita2026

# App
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development

# Empresa (configurable por cliente)
EMPRESA_NOMBRE=Mi Empresa de Servicios
EMPRESA_SECTOR=Consultoría
EMPRESA_DESCRIPCION=Ofrecemos servicios de consultoría empresarial

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCHEMA SQL — supabase_schema.sql
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Tabla: empresas (multi-tenant)
CREATE TABLE empresas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre TEXT NOT NULL,
  sector TEXT,
  descripcion TEXT,
  telegram_bot_token TEXT,
  telegram_admin_chat_id TEXT,
  voz_de_marca TEXT DEFAULT 'Profesional, cercana y orientada a resultados',
  servicios_ofrecidos JSONB DEFAULT '[]',
  activa BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO empresas (id, nombre, sector, descripcion)
VALUES ('00000000-0000-0000-0000-000000000001',
        'Mi Empresa de Servicios', 'Servicios', 'Empresa de servicios');

-- Tabla: leads
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001'
             REFERENCES empresas(id),
  telegram_user_id TEXT,
  telegram_username TEXT,
  telegram_chat_id TEXT,
  nombre TEXT NOT NULL DEFAULT 'Lead sin nombre',
  email TEXT,
  telefono TEXT,
  empresa_nombre TEXT,
  cargo TEXT,
  servicio_interes TEXT,
  presupuesto_estimado TEXT,
  etapa_funnel TEXT DEFAULT 'atencion'
    CHECK (etapa_funnel IN ('atencion','interes','deseo','accion','cliente')),
  etiquetas JSONB DEFAULT '[]',
  estado TEXT DEFAULT 'nuevo'
    CHECK (estado IN ('nuevo','contactado','cotizado',
                      'reunion_agendada','convertido','inactivo')),
  prioridad TEXT DEFAULT 'media'
    CHECK (prioridad IN ('baja','media','alta')),
  fuente TEXT DEFAULT 'telegram'
    CHECK (fuente IN ('telegram','manual','formulario','referido')),
  ultimo_contacto TIMESTAMPTZ DEFAULT NOW(),
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  telegram_message_id TEXT,
  role TEXT CHECK (role IN ('user','assistant','system')),
  content TEXT NOT NULL,
  content_type TEXT DEFAULT 'text'
    CHECK (content_type IN ('text','voice','image','document')),
  transcripcion_voz TEXT,
  agente TEXT,
  modelo_usado TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: cotizaciones
CREATE TABLE cotizaciones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  plan_nombre TEXT NOT NULL,
  descripcion TEXT,
  items JSONB DEFAULT '[]',
  valor NUMERIC(14,2),
  moneda TEXT DEFAULT 'COP',
  vigencia_dias INTEGER DEFAULT 15,
  estado TEXT DEFAULT 'pendiente'
    CHECK (estado IN ('pendiente','enviada','aceptada','rechazada','vencida')),
  enviada_por_telegram BOOLEAN DEFAULT FALSE,
  telegram_message_id TEXT,
  pdf_url TEXT,
  contenido_json JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: reuniones
CREATE TABLE reuniones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  fecha_hora TIMESTAMPTZ NOT NULL,
  duracion_minutos INTEGER DEFAULT 30,
  tipo TEXT DEFAULT 'demo'
    CHECK (tipo IN ('demo','llamada','presencial','videollamada')),
  estado TEXT DEFAULT 'agendada'
    CHECK (estado IN ('agendada','confirmada','completada','cancelada')),
  confirmada_por_telegram BOOLEAN DEFAULT FALSE,
  asesor_nombre TEXT,
  link_reunion TEXT,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: campanas
CREATE TABLE campanas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  nombre TEXT NOT NULL,
  tipo TEXT DEFAULT 'telegram'
    CHECK (tipo IN ('telegram','email','ambos')),
  segmento_etiquetas JSONB DEFAULT '[]',
  segmento_etapa TEXT,
  asunto TEXT,
  cuerpo TEXT NOT NULL,
  estado TEXT DEFAULT 'borrador'
    CHECK (estado IN ('borrador','enviando','completada','error')),
  total_destinatarios INTEGER DEFAULT 0,
  total_enviados INTEGER DEFAULT 0,
  total_fallidos INTEGER DEFAULT 0,
  creado_por TEXT DEFAULT 'admin',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  enviado_at TIMESTAMPTZ
);

-- Tabla: telegram_bot_sessions
-- Rastrea el estado de cada conversación en Telegram
CREATE TABLE telegram_bot_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  telegram_chat_id TEXT NOT NULL UNIQUE,
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  session_id TEXT NOT NULL DEFAULT gen_random_uuid()::text,
  estado_bot TEXT DEFAULT 'activo'
    CHECK (estado_bot IN ('activo','pausado','esperando_dato','cerrado')),
  contexto_actual JSONB DEFAULT '{}',
  ultimo_mensaje_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: agent_logs
CREATE TABLE agent_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  agente TEXT NOT NULL,
  accion TEXT NOT NULL,
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  telegram_chat_id TEXT,
  input_data JSONB,
  output_data JSONB,
  duracion_ms INTEGER,
  exitoso BOOLEAN DEFAULT TRUE,
  modelo_usado TEXT,
  tokens_prompt INTEGER,
  tokens_completion INTEGER,
  error_mensaje TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: notificaciones_admin
-- Historial de alertas enviadas al admin por Telegram
CREATE TABLE notificaciones_admin (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id UUID DEFAULT '00000000-0000-0000-0000-000000000001',
  tipo TEXT NOT NULL,
  mensaje TEXT NOT NULL,
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  enviada BOOLEAN DEFAULT FALSE,
  telegram_message_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_leads_estado ON leads(estado);
CREATE INDEX idx_leads_etapa ON leads(etapa_funnel);
CREATE INDEX idx_leads_telegram_user ON leads(telegram_user_id);
CREATE INDEX idx_leads_telegram_chat ON leads(telegram_chat_id);
CREATE INDEX idx_leads_prioridad ON leads(prioridad);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_lead ON conversations(lead_id);
CREATE INDEX idx_telegram_sessions_chat ON telegram_bot_sessions(telegram_chat_id);
CREATE INDEX idx_agent_logs_agente ON agent_logs(agente);
CREATE INDEX idx_agent_logs_created ON agent_logs(created_at DESC);

-- Triggers updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_leads_updated BEFORE UPDATE ON leads
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_cotizaciones_updated BEFORE UPDATE ON cotizaciones
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_telegram_sessions_updated
BEFORE UPDATE ON telegram_bot_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTRUCTURA DE ARCHIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
orbita-backend/
├── .env.example
├── requirements.txt
├── supabase_schema.sql
├── main.py
├── config.py
├── database.py
├── auth.py
├── models/
│   ├── lead.py
│   ├── cotizacion.py
│   ├── reunion.py
│   ├── campana.py
│   ├── telegram_session.py
│   └── agent_log.py
├── routers/
│   ├── leads.py
│   ├── cotizaciones.py
│   ├── reuniones.py
│   ├── campanas.py
│   ├── analytics.py
│   ├── agents.py
│   ├── telegram.py          ← WEBHOOK ENDPOINT
│   └── auth.py
├── agents/
│   ├── base_agent.py
│   ├── orchestrator.py
│   ├── captador.py
│   ├── conversacional.py
│   ├── identidad.py
│   ├── comunicacion.py
│   └── analitico.py
├── telegram/
│   ├── __init__.py
│   ├── bot.py               ← Configuración del bot
│   ├── handlers.py          ← Lógica de manejo de mensajes
│   ├── voice_processor.py   ← Transcripción de notas de voz
│   ├── message_builder.py   ← Formateo de respuestas Telegram
│   └── admin_notifier.py    ← Notificaciones al administrador
└── utils/
    ├── groq_client.py
    └── memory.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: telegram/bot.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CRITERIO 1] — Canal principal de conversación con leads
# [CRITERIO 4] — Telegram es gratuito y universal para servicios

from telegram import Bot, Update
from telegram.ext import Application
from config import get_settings

_bot_instance = None
_application = None

def get_bot() -> Bot:
    global _bot_instance
    if not _bot_instance:
        settings = get_settings()
        _bot_instance = Bot(token=settings.telegram_bot_token)
    return _bot_instance

def get_application() -> Application:
    global _application
    if not _application:
        settings = get_settings()
        _application = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .build()
        )
    return _application

async def setup_webhook(webhook_url: str, secret_token: str):
    """Registra el webhook de Telegram apuntando a nuestro servidor."""
    bot = get_bot()
    await bot.set_webhook(
        url=f"{webhook_url}",
        secret_token=secret_token,
        allowed_updates=["message", "callback_query", "my_chat_member"]
    )

async def delete_webhook():
    bot = get_bot()
    await bot.delete_webhook()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: telegram/voice_processor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CRITERIO 3] — Uso real de IA: Whisper para transcripción de voz

import groq
import httpx
import tempfile
import os
from telegram import Bot

async def transcribe_voice_message(bot: Bot, file_id: str,
                                   groq_api_key: str) -> str:
    """
    Descarga la nota de voz de Telegram y la transcribe con Whisper vía Groq.
    Modelo: whisper-large-v3 (gratuito en Groq)
    """
    # 1. Obtener URL del archivo de Telegram
    tg_file = await bot.get_file(file_id)
    file_url = tg_file.file_path

    # 2. Descargar el archivo de audio
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)
        audio_bytes = response.content

    # 3. Guardar temporalmente
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # 4. Transcribir con Whisper vía Groq API
        client = groq.Groq(api_key=groq_api_key)
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(tmp_path), audio_file.read()),
                model="whisper-large-v3",
                language="es",
                response_format="text"
            )
        return transcription if isinstance(transcription, str) \
               else transcription.text
    finally:
        os.unlink(tmp_path)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: telegram/message_builder.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Formatea mensajes para Telegram con Markdown V2

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_cotizacion_message(cotizacion: dict, lead: dict) -> tuple:
    """Construye el mensaje de cotización con botones de acción."""
    texto = (
        f"📄 *COTIZACIÓN #{cotizacion['id'][:8].upper()}*\n\n"
        f"Estimado/a *{lead['nombre']}*,\n\n"
        f"📋 *Plan:* {cotizacion['plan_nombre']}\n"
        f"💰 *Inversión:* ${cotizacion['valor']:,.0f} {cotizacion['moneda']}\n"
        f"⏰ *Vigencia:* {cotizacion.get('vigencia_dias', 15)} días\n\n"
        f"_{cotizacion['descripcion']}_\n\n"
        f"¿Te gustaría proceder?"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Aceptar cotización",
                                 callback_data=f"aceptar_cot_{cotizacion['id']}"),
            InlineKeyboardButton("❌ Rechazar",
                                 callback_data=f"rechazar_cot_{cotizacion['id']}")
        ],
        [
            InlineKeyboardButton("📅 Agendar demostración",
                                 callback_data=f"agendar_{cotizacion['lead_id']}")
        ]
    ])
    return texto, keyboard

def build_reunion_confirmation(reunion: dict) -> tuple:
    """Construye el mensaje de confirmación de reunión."""
    from datetime import datetime
    fecha = datetime.fromisoformat(str(reunion['fecha_hora']))
    texto = (
        f"🗓️ *REUNIÓN AGENDADA*\n\n"
        f"📌 *{reunion['titulo']}*\n"
        f"📅 {fecha.strftime('%A %d de %B, %Y')}\n"
        f"🕐 {fecha.strftime('%I:%M %p')}\n"
        f"⏱️ Duración: {reunion['duracion_minutos']} minutos\n"
        f"📞 Tipo: {reunion['tipo'].capitalize()}\n\n"
        f"¿Confirmas la reunión?"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirmar",
                             callback_data=f"confirmar_reunion_{reunion['id']}"),
        InlineKeyboardButton("❌ Cancelar",
                             callback_data=f"cancelar_reunion_{reunion['id']}")
    ]])
    return texto, keyboard

def build_welcome_message(empresa_nombre: str, sector: str) -> str:
    return (
        f"👋 ¡Hola! Soy el asistente virtual de *{empresa_nombre}*.\n\n"
        f"Estoy aquí para ayudarte con información sobre nuestros servicios "
        f"de {sector} y resolver cualquier consulta que tengas.\n\n"
        f"¿En qué puedo ayudarte hoy? Puedes escribirme o enviarme "
        f"un mensaje de voz 🎙️"
    )

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: telegram/admin_notifier.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CRITERIO 4] — Alertas proactivas al gerente/admin
# El administrador recibe notificaciones por Telegram sobre eventos clave

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

class AdminNotifier:
    def __init__(self, bot: Bot, admin_chat_id: str, db):
        self.bot = bot
        self.admin_chat_id = admin_chat_id
        self.db = db

    async def notify_new_lead(self, lead: dict):
        """Notifica al admin cuando llega un nuevo lead."""
        texto = (
            f"🔔 *NUEVO LEAD CAPTADO*\n\n"
            f"👤 *Nombre:* {lead.get('nombre','Sin nombre')}\n"
            f"🏢 *Empresa:* {lead.get('empresa_nombre','No especificada')}\n"
            f"🎯 *Interés:* {lead.get('servicio_interes','Por definir')}\n"
            f"⚡ *Prioridad:* {lead.get('prioridad','media').upper()}\n"
            f"📱 *Fuente:* Telegram\n"
            f"🆔 ID: `{str(lead.get('id',''))[:8]}`"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("👁️ Ver lead",
                                 callback_data=f"admin_ver_{lead['id']}"),
            InlineKeyboardButton("💬 Chat",
                                 callback_data=f"admin_chat_{lead['id']}")
        ]])
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=texto, parse_mode="Markdown",
            reply_markup=keyboard
        )
        await self._save_notification("nuevo_lead",
                                      f"Nuevo lead: {lead.get('nombre')}",
                                      lead.get('id'))

    async def notify_quote_accepted(self, lead: dict, cotizacion: dict):
        """Notifica al admin cuando un lead acepta una cotización."""
        texto = (
            f"🎉 *¡COTIZACIÓN ACEPTADA!*\n\n"
            f"👤 *Cliente:* {lead.get('nombre')}\n"
            f"🏢 *Empresa:* {lead.get('empresa_nombre','No especificada')}\n"
            f"📋 *Plan:* {cotizacion.get('plan_nombre')}\n"
            f"💰 *Valor:* ${cotizacion.get('valor',0):,.0f} "
            f"{cotizacion.get('moneda','COP')}\n\n"
            f"El cliente está listo para proceder. ¡Contacta ahora!"
        )
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=texto, parse_mode="Markdown"
        )
        await self._save_notification("cotizacion_aceptada",
                                      f"Cotización aceptada por {lead.get('nombre')}",
                                      lead.get('id'))

    async def notify_meeting_scheduled(self, lead: dict, reunion: dict):
        """Notifica al admin cuando se agenda una reunión."""
        from datetime import datetime
        fecha = datetime.fromisoformat(str(reunion['fecha_hora']))
        texto = (
            f"📅 *REUNIÓN AGENDADA*\n\n"
            f"👤 *Con:* {lead.get('nombre')}\n"
            f"🏢 *Empresa:* {lead.get('empresa_nombre','No especificada')}\n"
            f"📅 *Fecha:* {fecha.strftime('%d/%m/%Y a las %I:%M %p')}\n"
            f"📞 *Tipo:* {reunion.get('tipo','demo').capitalize()}\n\n"
            f"Revisa tu calendario y prepárate."
        )
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=texto, parse_mode="Markdown"
        )
        await self._save_notification("reunion_agendada",
                                      f"Reunión con {lead.get('nombre')}",
                                      lead.get('id'))

    async def notify_cold_lead_alert(self, leads: list):
        """Alerta sobre leads sin contacto en más de 24 horas."""
        if not leads:
            return
        lista = "\n".join([
            f"• {l.get('nombre','?')} ({l.get('empresa_nombre','?')}) "
            f"— {l.get('prioridad','?')} prioridad"
            for l in leads[:5]
        ])
        texto = (
            f"⚠️ *LEADS SIN SEGUIMIENTO*\n\n"
            f"Los siguientes leads de alta prioridad llevan más de "
            f"24 horas sin contacto:\n\n{lista}\n\n"
            f"Revisa el dashboard para tomar acción."
        )
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=texto, parse_mode="Markdown"
        )

    async def notify_analytics_summary(self, resumen: str, alertas: list):
        """Envía el resumen diario generado por el Agente Analítico."""
        alertas_texto = ""
        if alertas:
            alertas_texto = "\n\n🚨 *Alertas detectadas:*\n" + "\n".join([
                f"• [{a.get('prioridad','?').upper()}] {a.get('mensaje','')}"
                for a in alertas[:3]
            ])
        texto = (
            f"📊 *RESUMEN DIARIO ORBITA*\n\n"
            f"{resumen}{alertas_texto}"
        )
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=texto, parse_mode="Markdown"
        )

    async def _save_notification(self, tipo: str, mensaje: str,
                                 lead_id: str = None):
        self.db.table("notificaciones_admin").insert({
            "tipo": tipo, "mensaje": mensaje,
            "lead_id": lead_id, "enviada": True
        }).execute()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: telegram/handlers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CRITERIO 1] — Diseño conversacional con Telegram
# [CRITERIO 2] — Punto de entrada de los agentes

import asyncio
from telegram import Update, Bot
from database import get_db
from config import get_settings
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.conversacional import ConversacionalAgent
from telegram.voice_processor import transcribe_voice_message
from telegram.message_builder import (build_welcome_message,
    build_cotizacion_message, build_reunion_confirmation)
from telegram.admin_notifier import AdminNotifier

class TelegramHandler:
    """
    Maneja todos los tipos de mensaje de Telegram y los enruta
    al agente correcto. Es la puerta de entrada al sistema ORBITA.
    """

    def __init__(self):
        self.db = get_db()
        self.settings = get_settings()
        self.orchestrator = OrchestratorAgent(self.db, self.settings)
        self.captador = CaptadorAgent(self.db, self.settings)
        self.conversacional = ConversacionalAgent(self.db, self.settings)

    async def handle_update(self, update: Update, bot: Bot):
        """Router principal: determina el tipo de update y lo procesa."""
        if update.callback_query:
            await self._handle_callback_query(update.callback_query, bot)
            return

        if not update.message:
            return

        message = update.message
        chat_id = str(message.chat_id)
        user = message.from_user

        # Mostrar "escribiendo..." mientras el agente procesa
        await bot.send_chat_action(chat_id=chat_id, action="typing")

        # Determinar el tipo de contenido
        if message.voice or message.audio:
            await self._handle_voice(message, chat_id, user, bot)
        elif message.text:
            await self._handle_text(message.text, chat_id, user, bot,
                                    message.message_id)
        elif message.document or message.photo:
            await bot.send_message(
                chat_id=chat_id,
                text="📎 Recibí tu archivo. Por ahora trabajo mejor con "
                     "mensajes de texto o voz. ¿En qué puedo ayudarte?"
            )

    async def _handle_text(self, text: str, chat_id: str, user,
                           bot: Bot, message_id: int):
        """Procesa mensajes de texto."""
        # 1. Obtener o crear sesión del bot
        session = await self._get_or_create_session(chat_id, user)
        lead_id = session.get("lead_id")
        session_id = session.get("session_id")

        # 2. Guardar mensaje del usuario en conversations
        if lead_id:
            await self._save_user_message(lead_id, session_id, text,
                                          str(message_id))

        # 3. Orquestador decide qué agente activar
        decision = await self.orchestrator.execute({
            "mensaje": text,
            "lead_id": lead_id,
            "session_id": session_id,
            "telegram_chat_id": chat_id,
            "historial": await self._get_recent_history(session_id)
        })

        agente_principal = decision.get("agente_principal", "conversacional")

        # 4. Si no hay lead aún, primero captar
        if not lead_id and agente_principal in ["captador", "conversacional"]:
            captacion = await self.captador.execute({
                "mensaje": text,
                "telegram_user_id": str(user.id),
                "telegram_username": user.username or "",
                "telegram_chat_id": chat_id,
                "session_id": session_id,
                "nombre_telegram": user.full_name or ""
            })
            lead_id = captacion.get("lead_id")
            # Actualizar sesión con el lead_id
            await self._update_session_lead(chat_id, lead_id)

            # Notificar al admin si es lead nuevo
            if captacion.get("accion") == "creado":
                lead_data = self.db.table("leads").select("*").eq(
                    "id", lead_id).single().execute().data
                notifier = AdminNotifier(bot, self.settings.telegram_admin_chat_id,
                                        self.db)
                asyncio.create_task(notifier.notify_new_lead(lead_data))

        # 5. Agente Conversacional genera la respuesta
        resultado = await self.conversacional.execute({
            "mensaje": text,
            "lead_id": lead_id,
            "session_id": session_id,
            "etapa_actual": decision.get("etapa_aida", "atencion"),
            "decision_orquestador": decision
        })

        respuesta = resultado.get("respuesta_final", "")
        accion = resultado.get("accion_realizada")

        # 6. Enviar respuesta al lead
        if accion == "generar_cotizacion" and resultado.get("cotizacion"):
            cotizacion = resultado["cotizacion"]
            lead = self.db.table("leads").select("nombre").eq(
                "id", lead_id).single().execute().data or {}
            texto, keyboard = build_cotizacion_message(cotizacion, lead)
            await bot.send_message(chat_id=chat_id, text=texto,
                                   parse_mode="Markdown",
                                   reply_markup=keyboard)
            # Notificar al admin
            notifier = AdminNotifier(bot, self.settings.telegram_admin_chat_id,
                                     self.db)
            asyncio.create_task(notifier.notify_new_lead({
                "id": lead_id, "nombre": lead.get("nombre"),
                "servicio_interes": "Cotización generada"
            }))
        elif accion == "agendar_reunion" and resultado.get("reunion"):
            reunion = resultado["reunion"]
            texto, keyboard = build_reunion_confirmation(reunion)
            await bot.send_message(chat_id=chat_id, text=texto,
                                   parse_mode="Markdown",
                                   reply_markup=keyboard)
        else:
            await bot.send_message(chat_id=chat_id, text=respuesta,
                                   parse_mode="Markdown")

    async def _handle_voice(self, message, chat_id: str, user, bot: Bot):
        """Procesa notas de voz con Whisper."""
        # 1. Transcribir con Whisper vía Groq
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        await bot.send_message(
            chat_id=chat_id,
            text="🎙️ Escuché tu mensaje de voz, déjame procesarlo..."
        )
        try:
            transcripcion = await transcribe_voice_message(
                bot, file_id, self.settings.groq_api_key
            )
            # 2. Guardar transcripción en conversations
            session = await self._get_or_create_session(chat_id, user)
            if session.get("lead_id"):
                self.db.table("conversations").insert({
                    "lead_id": session["lead_id"],
                    "session_id": session["session_id"],
                    "role": "user",
                    "content": transcripcion,
                    "content_type": "voice",
                    "transcripcion_voz": transcripcion
                }).execute()
            # 3. Procesar el texto transcrito como mensaje normal
            await self._handle_text(transcripcion, chat_id, user, bot,
                                    message.message_id)
        except Exception as e:
            await bot.send_message(
                chat_id=chat_id,
                text="No pude procesar tu nota de voz. "
                     "¿Puedes escribirme tu consulta?"
            )

    async def _handle_callback_query(self, callback_query, bot: Bot):
        """Maneja los botones inline de Telegram."""
        data = callback_query.data
        chat_id = str(callback_query.message.chat_id)
        lead_id = await self._get_lead_id_from_chat(chat_id)

        await callback_query.answer()

        if data.startswith("aceptar_cot_"):
            cotizacion_id = data.replace("aceptar_cot_", "")
            self.db.table("cotizaciones").update(
                {"estado": "aceptada"}
            ).eq("id", cotizacion_id).execute()
            await bot.send_message(
                chat_id=chat_id,
                text="✅ ¡Perfecto! Has aceptado la cotización.\n\n"
                     "Un asesor te contactará pronto para coordinar "
                     "los próximos pasos. ¿Te gustaría agendar "
                     "una reunión ahora?"
            )
            if lead_id:
                cotizacion = self.db.table("cotizaciones").select("*").eq(
                    "id", cotizacion_id).single().execute().data or {}
                lead = self.db.table("leads").select("*").eq(
                    "id", lead_id).single().execute().data or {}
                notifier = AdminNotifier(
                    bot, self.settings.telegram_admin_chat_id, self.db)
                asyncio.create_task(
                    notifier.notify_quote_accepted(lead, cotizacion))

        elif data.startswith("rechazar_cot_"):
            cotizacion_id = data.replace("rechazar_cot_", "")
            self.db.table("cotizaciones").update(
                {"estado": "rechazada"}
            ).eq("id", cotizacion_id).execute()
            await bot.send_message(
                chat_id=chat_id,
                text="Entendido. ¿Hay algún aspecto que podamos ajustar "
                     "para hacer la propuesta más adecuada a tus necesidades?"
            )

        elif data.startswith("agendar_"):
            await bot.send_message(
                chat_id=chat_id,
                text="📅 ¡Con gusto! ¿Qué día y hora te viene mejor "
                     "para la reunión? Tenemos disponibilidad de lunes "
                     "a viernes entre 9am y 6pm."
            )

        elif data.startswith("confirmar_reunion_"):
            reunion_id = data.replace("confirmar_reunion_", "")
            self.db.table("reuniones").update(
                {"estado": "confirmada", "confirmada_por_telegram": True}
            ).eq("id", reunion_id).execute()
            await bot.send_message(
                chat_id=chat_id,
                text="✅ ¡Reunión confirmada! Te esperamos.\n\n"
                     "Recibirás un recordatorio el día anterior."
            )
            if lead_id:
                reunion = self.db.table("reuniones").select("*").eq(
                    "id", reunion_id).single().execute().data or {}
                lead = self.db.table("leads").select("*").eq(
                    "id", lead_id).single().execute().data or {}
                notifier = AdminNotifier(
                    bot, self.settings.telegram_admin_chat_id, self.db)
                asyncio.create_task(
                    notifier.notify_meeting_scheduled(lead, reunion))

        elif data.startswith("cancelar_reunion_"):
            reunion_id = data.replace("cancelar_reunion_", "")
            self.db.table("reuniones").update(
                {"estado": "cancelada"}
            ).eq("id", reunion_id).execute()
            await bot.send_message(
                chat_id=chat_id,
                text="Entendido, cancelamos la reunión. "
                     "¿Te gustaría coordinar otra fecha?"
            )

    async def _get_or_create_session(self, chat_id: str, user) -> dict:
        """Obtiene sesión existente o crea una nueva."""
        result = self.db.table("telegram_bot_sessions").select("*").eq(
            "telegram_chat_id", chat_id).maybe_single().execute()

        if result.data:
            return result.data

        import uuid
        session_id = str(uuid.uuid4())
        new_session = {
            "telegram_chat_id": chat_id,
            "session_id": session_id,
            "estado_bot": "activo",
            "contexto_actual": {
                "telegram_username": user.username or "",
                "nombre_telegram": user.full_name or ""
            }
        }
        result = self.db.table("telegram_bot_sessions").insert(
            new_session).execute()
        return result.data[0] if result.data else new_session

    async def _update_session_lead(self, chat_id: str, lead_id: str):
        self.db.table("telegram_bot_sessions").update(
            {"lead_id": lead_id}
        ).eq("telegram_chat_id", chat_id).execute()

    async def _get_lead_id_from_chat(self, chat_id: str) -> str | None:
        result = self.db.table("telegram_bot_sessions").select(
            "lead_id").eq("telegram_chat_id", chat_id).maybe_single().execute()
        return result.data.get("lead_id") if result.data else None

    async def _get_recent_history(self, session_id: str) -> list:
        result = self.db.table("conversations").select(
            "role,content").eq("session_id", session_id).order(
            "created_at").limit(10).execute()
        return [{"role": r["role"], "content": r["content"]}
                for r in (result.data or [])]

    async def _save_user_message(self, lead_id: str, session_id: str,
                                  text: str, message_id: str):
        self.db.table("conversations").insert({
            "lead_id": lead_id, "session_id": session_id,
            "role": "user", "content": text,
            "telegram_message_id": message_id
        }).execute()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUTER: routers/telegram.py — WEBHOOK ENDPOINT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CRITERIO 6] — Endpoint documentado y seguro

from fastapi import APIRouter, Request, HTTPException, Header
from telegram import Update
from telegram.bot import get_bot
from telegram.handlers import TelegramHandler
from config import get_settings

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])
_handler = None

def get_handler() -> TelegramHandler:
    global _handler
    if not _handler:
        _handler = TelegramHandler()
    return _handler

@router.post("/webhook",
    summary="Webhook de Telegram",
    description="""
    Endpoint que recibe todos los updates de Telegram Bot API.
    Soporta: mensajes de texto, notas de voz, callbacks de botones.

    [CRITERIO 1] Canal de conversación principal con leads.
    [CRITERIO 3] Transcripción de voz con Whisper-large-v3.

    Configurar en BotFather:
    POST https://api.telegram.org/bot{TOKEN}/setWebhook
    Body: {"url": "https://tu-dominio.com/api/v1/telegram/webhook",
           "secret_token": "TU_WEBHOOK_SECRET"}
    """)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    settings = get_settings()

    # Verificar token secreto de seguridad
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    update = Update.de_json(body, get_bot())
    await get_handler().handle_update(update, get_bot())
    return {"ok": True}

@router.post("/setup-webhook",
    summary="Configurar webhook en Telegram",
    description="Registra el webhook de Telegram apuntando a este servidor.")
async def setup_telegram_webhook(request: Request):
    settings = get_settings()
    from telegram.bot import setup_webhook
    webhook_url = f"{settings.telegram_webhook_url}"
    await setup_webhook(webhook_url, settings.telegram_webhook_secret)
    return {"success": True, "webhook_url": webhook_url,
            "message": "Webhook configurado exitosamente en Telegram"}

@router.delete("/webhook",
    summary="Eliminar webhook (activar polling)",
    description="Elimina el webhook para usar polling en desarrollo.")
async def delete_telegram_webhook():
    from telegram.bot import delete_webhook
    await delete_webhook()
    return {"success": True, "message": "Webhook eliminado"}

@router.get("/info",
    summary="Información del bot",
    description="Obtiene información del bot de Telegram configurado.")
async def get_bot_info():
    bot = get_bot()
    info = await bot.get_me()
    webhook_info = await bot.get_webhook_info()
    return {
        "success": True,
        "data": {
            "bot_username": info.username,
            "bot_nombre": info.full_name,
            "webhook_url": webhook_info.url,
            "pending_updates": webhook_info.pending_update_count,
            "activo": True
        }
    }

@router.post("/send-message",
    summary="Enviar mensaje desde el dashboard",
    description="El admin puede enviar mensajes a cualquier lead desde el dashboard web.")
async def send_message_to_lead(payload: dict):
    """
    payload: {chat_id: str, mensaje: str, lead_id: str}
    Permite que el administrador intervenga en una conversación.
    """
    bot = get_bot()
    db = get_db_dependency()
    chat_id = payload.get("chat_id")
    mensaje = payload.get("mensaje")
    lead_id = payload.get("lead_id")

    if not chat_id or not mensaje:
        raise HTTPException(status_code=400, detail="chat_id y mensaje requeridos")

    await bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="Markdown")

    # Guardar en conversations como intervención del admin
    if lead_id:
        db.table("conversations").insert({
            "lead_id": lead_id, "role": "assistant",
            "content": mensaje, "agente": "admin_manual",
            "session_id": chat_id
        }).execute()
        db.table("leads").update(
            {"ultimo_contacto": "now()"}
        ).eq("id", lead_id).execute()

    return {"success": True, "message": "Mensaje enviado por Telegram"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENTES — SYSTEM PROMPTS ADAPTADOS A SERVICIOS GENÉRICOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
En agents/base_agent.py incluir el contexto de empresa:

En __init__ de cada agente, cargar de Supabase:
  empresa = db.table("empresas").select("*").eq(
      "id", "00000000-0000-0000-0000-000000000001"
  ).single().execute().data

Usar empresa["nombre"], empresa["sector"], empresa["voz_de_marca"],
empresa["servicios_ofrecidos"] en los system prompts para que el agente
sepa para qué empresa está trabajando.

--- agents/orchestrator.py ---
system_prompt = f"""
Eres ORBITA, el orquestador central de {empresa_nombre}, una empresa
de {sector}. Clasificas intenciones de leads potenciales usando AIDA.

FRAMEWORK AIDA:
- ATENCIÓN: lead acaba de llegar, desconoce los servicios → activa CAPTADOR
- INTERÉS: quiere saber más sobre los servicios → activa CONVERSACIONAL
- DESEO: pide cotización o precio → activa CONVERSACIONAL (+ valida IDENTIDAD)
- ACCIÓN: quiere agendar o cerrar → activa CONVERSACIONAL (+ crea REUNIÓN)

Si el lead envía un mensaje de voz ya transcrito, procésalo como texto normal.

Responde SIEMPRE en JSON:
{{
  "intencion": "saludo|consulta_servicio|solicitud_precio|agendar|
                queja|fuera_de_tema|otro",
  "etapa_aida": "atencion|interes|deseo|accion",
  "prioridad": "baja|media|alta",
  "agente_principal": "captador|conversacional|analitico",
  "agente_soporte": "identidad|null",
  "razon": "explicación breve",
  "accion_recomendada": "descripción de qué hacer"
}}
"""

--- agents/captador.py ---
system_prompt = f"""
Eres el Agente Captador de {empresa_nombre}. Extraes datos del
prospecto de forma natural para crear su perfil en el CRM.

Datos a extraer cuando sea posible (nunca de forma invasiva):
- nombre, email, teléfono, empresa donde trabaja, cargo
- qué servicio le interesa de {empresa_nombre}
- presupuesto aproximado o urgencia

Asigna etiquetas relevantes según el sector: {sector}
Posibles etiquetas: ["alta_intencion", "precio_sensible",
"decision_maker", "explorador", "urgente", "B2B", "B2C"]

Responde en JSON:
{{
  "nombre_detectado": str|null,
  "email_detectado": str|null,
  "telefono_detectado": str|null,
  "empresa_detectada": str|null,
  "cargo_detectado": str|null,
  "servicio_interes": str|null,
  "presupuesto_estimado": str|null,
  "etiquetas": [],
  "prioridad": "baja|media|alta",
  "es_duplicado": false,
  "mensaje_bienvenida": "mensaje cálido en nombre de {empresa_nombre}",
  "siguiente_pregunta": "pregunta natural para completar el perfil"
}}
"""

--- agents/conversacional.py ---
system_prompt = f"""
Eres el Agente Conversacional de {empresa_nombre}, empresa de {sector}.
Atiendes prospectos por Telegram 24/7 con memoria completa de la conversación.

Voz de la marca: {voz_de_marca}
Servicios que ofrece la empresa: {servicios_ofrecidos}

Según etapa AIDA del lead:
- ATENCIÓN: presenta la propuesta de valor de {empresa_nombre}, genera curiosidad
- INTERÉS: haz 1-2 preguntas inteligentes sobre su necesidad específica
- DESEO: muestra cómo los servicios resuelven su problema concreto,
         ofrece generar una cotización personalizada
- ACCIÓN: propón cotización o agenda una demostración/llamada

Reglas:
- Responde SIEMPRE en español
- Máximo 3 párrafos por respuesta (Telegram se lee en móvil)
- Si el lead da datos incompletos, haz UNA sola pregunta a la vez
- Si pide precio exacto sin datos suficientes, ofrece generar cotización
  personalizada pidiendo los datos necesarios
- NUNCA inventes precios sin datos del lead

Responde en JSON:
{{
  "respuesta": "mensaje para el lead (máximo 3 párrafos)",
  "accion_sugerida": "ninguna|generar_cotizacion|agendar_reunion|
                      escalar_admin|reactivar_lead",
  "datos_cotizacion": null | {{
    "plan": str, "descripcion": str, "valor_estimado": float,
    "items": [{{"nombre": str, "descripcion": str, "valor": float}}]
  }},
  "datos_reunion": null | {{
    "titulo": str, "tipo": "demo|llamada|videollamada|presencial",
    "fecha_sugerida": str, "duracion_minutos": int
  }},
  "actualizar_etapa_a": null | "atencion|interes|deseo|accion",
  "actualizar_prioridad_a": null | "baja|media|alta"
}}
"""

--- agents/identidad.py ---
system_prompt = f"""
Eres el Agente de Identidad de {empresa_nombre}. Eres el guardián
de la voz de la marca: {voz_de_marca}

Validas y mejoras mensajes antes de enviarlos al lead.
Criterios:
- Tono: {voz_de_marca}
- Longitud: máximo 3 párrafos (mensajes de Telegram)
- Claridad: sin jerga técnica innecesaria
- Marca: no prometer lo que no se puede cumplir
- Emojis: uso moderado y apropiado para el sector {sector}

Responde en JSON:
{{
  "aprobado": true|false,
  "mensaje_final": "versión mejorada y validada",
  "cambios_realizados": ["cambio 1", "cambio 2"],
  "score_marca": 0.0,
  "razon_rechazo": null|"motivo"
}}
Si score_marca < 0.7 → reescribir completamente en mensaje_final.
SIEMPRE devolver mensaje_final aprobado para no bloquear el flujo.
"""

--- agents/comunicacion.py ---
system_prompt = f"""
Eres el Agente de Comunicación de {empresa_nombre}. Personalizas
mensajes de campañas para cada lead según su perfil e historial.

Sector de la empresa: {sector}
Voz de la marca: {voz_de_marca}

Para cada lead personaliza:
- Usar su nombre y empresa en el saludo
- Referenciar el servicio específico que le interesa
- Adaptar el tono según etapa AIDA del lead
- Incluir CTA claro y específico

Responde en JSON:
{{
  "asunto_personalizado": str,
  "cuerpo_personalizado": str,
  "nivel_personalizacion": "bajo|medio|alto",
  "variables_usadas": ["nombre", "empresa", "servicio_interes"],
  "cta": "llamada a la acción específica"
}}
"""

--- agents/analitico.py ---
system_prompt = f"""
Eres el Agente Analítico de {empresa_nombre}, empresa de {sector}.
Analizas el CRM y detectas patrones, anomalías y oportunidades.

Métricas clave para una empresa de servicios:
- Tasa de conversión por etapa del funnel AIDA
- Tiempo promedio desde primer contacto hasta cotización
- Tasa de aceptación de cotizaciones
- Leads sin seguimiento en más de 24 horas (riesgo de perderlos)
- Servicios con más demanda

Responde en JSON:
{{
  "alertas": [
    {{"tipo": str, "mensaje": str, "prioridad": "baja|media|alta",
      "lead_ids_afectados": [], "accion_recomendada": str}}
  ],
  "insights": ["insight 1", "insight 2"],
  "recomendaciones": ["acción 1", "acción 2"],
  "resumen_ejecutivo": "1-2 oraciones con lo más importante",
  "metricas_calculadas": {{}}
}}
"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: main.py — LIFESPAN CON TELEGRAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crea main.py con lifespan que al arrancar:
1. Verifica conexión a Supabase
2. Si ENVIRONMENT == "production": registra el webhook de Telegram
3. Si ENVIRONMENT == "development": elimina webhook (usa polling manual)
4. Muestra en consola: "✅ ORBITA iniciado | Bot: @{bot_username} | Agentes: 5"

Incluir todos los routers con prefijos:
  /api/v1/leads, /api/v1/cotizaciones, /api/v1/reuniones,
  /api/v1/campanas, /api/v1/analytics, /api/v1/agents,
  /api/v1/telegram, /api/v1/auth

CORS para: http://localhost:5173, http://localhost:3000,
           https://*.lovable.app, https://*.lovableproject.com

GET /health retorna:
  {
    "status": "ok",
    "sistema": "ORBITA",
    "agentes": 5,
    "telegram": "activo",
    "version": "1.0.0",
    "empresa": settings.empresa_nombre
  }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUTERS ADICIONALES AL TELEGRAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
En routers/leads.py agregar:

POST /api/v1/leads/{id}/chat (mismo endpoint de antes +):
  → Si el lead tiene telegram_chat_id, enviar respuesta también por Telegram
  → Parámetro: send_to_telegram: bool = True

GET /api/v1/leads/telegram/{chat_id}
  → Obtener lead por telegram_chat_id

En routers/analytics.py agregar:

GET /api/v1/analytics/telegram
  → Métricas específicas de Telegram:
    * total_chats_activos
    * mensajes_hoy (desde conversations)
    * notas_de_voz_procesadas
    * cotizaciones_enviadas_telegram
    * reuniones_confirmadas_telegram

En routers/agents.py agregar:

POST /api/v1/agents/comunicacion/run
  body: {campana_id}
  → AgenteComunicacion.execute() que envía por Telegram

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTRATO DE RESPUESTA — IGUAL EN TODOS LOS ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ "success": true, "data": {...},
  "message": "descripción", "timestamp": "ISO 8601" }

{ "success": false, "error": "CODIGO",
  "message": "mensaje legible", "timestamp": "ISO 8601" }

Headers en todas las respuestas:
  X-ORBITA-Version: 1.0.0
  X-ORBITA-Agent: nombre_agente (cuando aplique)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
README.md — INSTRUCCIONES DE DESPLIEGUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generar README.md con:
1. pip install -r requirements.txt
2. cp .env.example .env y editar
3. Obtener GROQ_API_KEY en console.groq.com (gratis, sin tarjeta)
4. Crear bot en Telegram: abrir @BotFather → /newbot
   → copiar token → pegar en TELEGRAM_BOT_TOKEN
5. Obtener tu TELEGRAM_ADMIN_CHAT_ID: escribir a @userinfobot
6. Correr el schema SQL en Supabase SQL Editor
7. uvicorn main:app --reload
8. Configurar webhook: POST /api/v1/telegram/setup-webhook
   (o usar ngrok en desarrollo: ngrok http 8000)
9. Escribir al bot de Telegram para probar
10. Abrir http://localhost:8000/docs para ver la API completa
```

---
---

# ╔══════════════════════════════════════════════════════════════╗
# ║   PARTE 2 — FRONTEND  →  Pegar en lovable.dev (New Project) ║
# ╚══════════════════════════════════════════════════════════════╝

```
Construye el dashboard web completo para ORBITA: sistema inteligente
autónomo de gestión de leads para empresas de servicios
(consultoría, marketing, tecnología, salud, legal, educación privada,
contable — cualquier empresa que venda servicios B2B o B2C).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDENTIDAD VISUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Variables CSS globales:
--bg-primary:   #0D0B14
--bg-secondary: #1A1626
--green:        #50FA7B   ← acento principal
--pink:         #FF4D94   ← acento secundario
--blue:         #00D1FF
--purple:       #BD93F9
--text:         #F8F8F2
--text-muted:   #94A3B8

Tipografías (Google Fonts):
- "Exo 2" (300,400,600,700,900) → cuerpo y títulos
- "Space Mono" (400,700) → badges, código, métricas

Estilo visual:
- body: background #0D0B14
- Grid sutil: background-image con líneas rgba(80,250,123,0.04) cada 40px
- Cards: border: 1px solid rgba(255,255,255,0.07), border-radius: 6px
- Acento en card: border-left: 3px solid [color_agente]
- Glow: box-shadow: 0 0 20px rgba(80,250,123,0.12)
- Badges: font-family Space Mono, font-size 10px, letter-spacing 1px,
          UPPERCASE, border-radius 3px, padding 2px 8px
- Animaciones: fadeUp 0.6s ease para elementos al cargar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTEGRACIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instalar: @supabase/supabase-js

src/lib/supabase.ts:
import { createClient } from '@supabase/supabase-js'
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

src/lib/api.ts:
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const h = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('orbita_token') || ''}`
})
export const orbitaApi = {
  health:           () => fetch(`${API}/health`).then(r=>r.json()),
  login:      (e,p) => fetch(`${API}/api/v1/auth/login`,
                        {method:'POST',headers:h(),
                         body:JSON.stringify({email:e,password:p})}).then(r=>r.json()),
  chat:   (lid,msg,sid) => fetch(`${API}/api/v1/leads/${lid}/chat`,
                        {method:'POST',headers:h(),
                         body:JSON.stringify({mensaje:msg,session_id:sid})}).then(r=>r.json()),
  sendToTelegram: (cid,msg,lid) =>
                   fetch(`${API}/api/v1/telegram/send-message`,
                        {method:'POST',headers:h(),
                         body:JSON.stringify({chat_id:cid,mensaje:msg,lead_id:lid})}).then(r=>r.json()),
  sendCampaign: (id) => fetch(`${API}/api/v1/campanas/${id}/enviar`,
                        {method:'POST',headers:h()}).then(r=>r.json()),
  previewCampaign:(id)=> fetch(`${API}/api/v1/campanas/${id}/preview`,
                        {headers:h()}).then(r=>r.json()),
  runAnalytics: (t='diario') => fetch(`${API}/api/v1/agents/analitico/run`,
                        {method:'POST',headers:h(),
                         body:JSON.stringify({tipo_analisis:t})}).then(r=>r.json()),
  getAgentStatus: () => fetch(`${API}/api/v1/agents/status`,
                        {headers:h()}).then(r=>r.json()),
  getDashboard:   () => fetch(`${API}/api/v1/analytics/dashboard`,
                        {headers:h()}).then(r=>r.json()),
  getAlertas:     () => fetch(`${API}/api/v1/analytics/alertas`,
                        {headers:h()}).then(r=>r.json()),
  getTelegramMetrics:()=> fetch(`${API}/api/v1/analytics/telegram`,
                        {headers:h()}).then(r=>r.json()),
  getBotInfo:     () => fetch(`${API}/api/v1/telegram/info`,
                        {headers:h()}).then(r=>r.json()),
  setupWebhook:   () => fetch(`${API}/api/v1/telegram/setup-webhook`,
                        {method:'POST',headers:h()}).then(r=>r.json()),
}

Variables .env:
VITE_SUPABASE_URL=https://xiblghevwgzuhytcqpyg.supabase.co
VITE_SUPABASE_ANON_KEY=TU_ANON_KEY_DE_SUPABASE_DASHBOARD
VITE_API_URL=http://localhost:8000

REGLA: Supabase directo para LECTURA.
       orbitaApi para ACCIONES con IA y Telegram.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYOUT GLOBAL — SIDEBAR + MAIN CONTENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sidebar fijo izquierdo (240px), bg #0D0B14, border-right 1px rgba(255,255,255,0.06):

Header del sidebar:
- Logo: "ORBITA" Exo 2 900 24px + elipse verde animada
- Badge verde pulsante: "● SISTEMA ACTIVO"

Navegación:
  🏠 Dashboard          /dashboard
  👥 Leads CRM          /leads
  💬 Conversaciones     /conversaciones
  📱 Telegram           /telegram       ← NUEVA PÁGINA
  📄 Cotizaciones       /cotizaciones
  🗓️ Reuniones          /reuniones
  📧 Campañas           /campanas
  🤖 Agentes            /agentes
  📊 Analítica          /analitica
  ⚙️ Configuración      /configuracion

Pie del sidebar:
- "X leads activos" (Supabase Realtime)
- "Telegram: @bot_username" con punto verde si el bot está activo
- "Última actividad: hace X min"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /login
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Fondo #0D0B14 full screen con grid sutil
- Centro: logo ORBITA grande con glow verde (#50FA7B)
- Tagline: "No se trata de tener más leads.
           Se trata de no dejar escapar ninguno."
- Card: email + password + "Entrar al Sistema"
- orbitaApi.login() → token en localStorage → navigate('/dashboard')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Header:
- Eyebrow badge: "SISTEMA ACTIVO · AI FIRST HACKATHON 2026"
- Título: "ORBITA Dashboard"
- Subtítulo: "Sistema Inteligente Autónomo para Empresas de Servicios"

6 MetricCards (datos de orbitaApi.getDashboard()):
  [Verde]   Leads Total
  [Rosa]    Leads Hoy
  [Azul]    Tasa Conversión %
  [Púrpura] Cotizaciones Pendientes
  [Verde]   Reuniones Próximas
  [Rosa]    Chats Telegram Hoy     ← NUEVA métrica Telegram

Embudo AIDA (barras horizontales, datos Supabase):
  ATENCIÓN → INTERÉS → DESEO → ACCIÓN
  Con contadores y porcentajes del total

Card "Estado del Bot de Telegram" (prominente, borde azul):
  - Nombre del bot (@bot_username)
  - Badge "● ACTIVO" pulsante verde
  - Leads captados hoy vía Telegram
  - Mensajes procesados hoy
  - Notas de voz transcritas hoy
  - Botón "Ir a Telegram" → navega a /telegram

Actividad de Agentes en tiempo real (Supabase Realtime):
  Tabla: Agente | Canal | Acción | Duración | ✓/✗
  Actualización automática (postgres_changes en agent_logs)

Panel de Alertas:
  Botón "🔄 Analizar" → orbitaApi.runAnalytics()
  Cards de alertas con badge de prioridad

Leads Urgentes (prioridad='alta', sin contacto reciente):
  5 leads top con botón "Chat" y "Telegram"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /telegram  ← PÁGINA CLAVE — Control del bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Header: "📱 TELEGRAM — Control del Bot y Conversaciones"

Sección "Estado del Bot" (card superior):
  Datos de orbitaApi.getBotInfo():
  - Nombre y username del bot con ícono de Telegram azul
  - Badge ACTIVO / INACTIVO con punto pulsante
  - Webhook URL configurado
  - Updates pendientes en cola
  - Botón "🔄 Reconfigurar Webhook" → orbitaApi.setupWebhook()
  - Botón "🔗 Abrir en Telegram" → https://t.me/@bot_username

Métricas Telegram (datos de orbitaApi.getTelegramMetrics()):
  [Azul]  Chats Activos Hoy
  [Verde] Mensajes Procesados
  [Rosa]  Leads Captados vía Telegram
  [Púrpura] Notas de Voz Transcritas
  [Azul]  Cotizaciones Enviadas por Telegram
  [Verde] Reuniones Confirmadas por Telegram

Sección "Conversaciones Activas por Telegram" (tabla):
  Columnas: Lead | Empresa | Último mensaje | Etapa AIDA | Estado |
            Chat ID | Acciones
  Acciones por fila:
    [💬 Responder vía Telegram] → abre panel lateral de chat
    [👁️ Ver en CRM] → navega a /leads?id={lead_id}

Panel lateral "Chat vía Telegram" (se abre al hacer clic en Responder):
  - Header: nombre lead + chat_id + badge etapa
  - Historial de mensajes (tabla conversations filtrada por lead_id)
  - Mensajes de voz: mostrar 🎙️ + transcripción en cursiva
  - Mensaje del lead: burbuja izquierda, bg oscuro
  - Mensaje del agente: burbuja derecha, bg verde oscuro + badge del agente
  - Input + botón "Enviar por Telegram" → orbitaApi.sendToTelegram()
  - Toggle: "Enviar como Agente ORBITA" / "Intervención manual del admin"

Sección "Historial de Notificaciones al Admin":
  Datos desde tabla notificaciones_admin (Supabase directo)
  Tabla: Tipo | Mensaje | Lead | Enviada | Fecha
  Tipos con íconos: 🆕 nuevo_lead | 🎉 cotizacion_aceptada |
                    📅 reunion_agendada | ⚠️ alerta

Sección "Comandos del Bot" (referencia rápida):
  Cards informativas (no son botones, son docs):
  - Comandos disponibles para el lead: /start, /cotizacion, /reunión, /ayuda
  - Comandos para el admin: /stats, /leads, /alertas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /leads  ← CRM completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Header: contador total + "+ Nuevo Lead" + buscador

Filtros: Estado | Etapa AIDA | Prioridad | Fuente (Telegram/Manual/Referido)

Tabla de leads: Lead | Etapa AIDA | Estado | Prioridad | Fuente |
                Etiquetas | Último Contacto | Acciones

Acciones: [Ver] [Chat Dashboard] [Telegram] [Cotizar]

Panel lateral al seleccionar lead (tabs):
- INFO: nombre, email, teléfono, empresa, cargo, servicio de interés,
        presupuesto estimado, etiquetas editables, notas
- CONVERSACIÓN: historial con badge del agente + icono 🎙️ para voz
                Input + "Enviar vía ORBITA" (chat) +
                "Enviar por Telegram" (si tiene telegram_chat_id)
- COTIZACIONES: lista + botones aceptar/rechazar
- REUNIONES: lista + botones confirmar/cancelar
- TIMELINE: historial de acciones de agent_logs para este lead

Modal "Nuevo Lead Manual":
  nombre*, email, teléfono, empresa, cargo, servicio_interés, presupuesto,
  prioridad, fuente (select), notas
  → INSERT en Supabase (fuente="manual")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /conversaciones
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layout 2 columnas (30|70):

Lista izquierda (leads con conversaciones):
- Nombre + empresa + preview último mensaje
- Badge: 📱 Telegram | 🖥️ Dashboard
- Badge del agente que respondió último
- Badge si hay notas de voz: 🎙️

Chat derecho (igual que en /telegram pero integrado aquí):
- Historial completo
- Notas de voz con 🎙️ + transcripción
- Badge del agente por mensaje
- Input con opciones: responder por dashboard O por Telegram
- "⚡ Agente procesando..." con <LoadingDots />

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINAS: /cotizaciones, /reuniones (sin cambios del prompt anterior)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COTIZACIONES — añadir columna "Enviada por Telegram" con ícono 📱
REUNIONES — añadir columna "Confirmada por Telegram" con ícono ✅📱

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /campanas  ← Campañas vía Telegram
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Igual que antes + cambios:

Formulario nueva campaña — tipo:
  Radio: 📱 Telegram | 📧 Email | Ambos
  (Telegram es el principal para empresas de servicios)

Al elegir tipo Telegram:
  - Cuerpo del mensaje con contador de caracteres (máx 4096 para Telegram)
  - Preview en formato burbuja de Telegram (fondo oscuro, texto blanco)
  - Badge "Esta campaña se enviará por Telegram a X leads"

Botón "Vista Previa con IA":
  → orbitaApi.previewCampaign(id)
  → Muestra 3 mensajes personalizados en formato burbuja Telegram

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /agentes  ← Showcaso del hackathon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Diagrama pentagonal SVG animado con Telegram integrado:

Añadir dos nodos externos al pentágono:
  [📱 TELEGRAM BOT] → línea azul → nodo central ORBITA
  [👨‍💼 ADMIN] → línea punteada → nodo central ORBITA
  (representan los canales de entrada/salida)

Flujo visual animado del caso exitoso:
  Telegram Bot → ORBITA → Captador → Conversacional → Identidad
  → respuesta por Telegram + notificación al Admin

Cards de agentes (igual que antes) + card especial:
  Card "TELEGRAM BOT":
  - Ícono 📱 + color azul #00D1FF
  - Última actividad (desde conversations)
  - Mensajes hoy / Leads captados / Voces transcritas
  - Link al bot de Telegram

Sección "Criterios del Hackathon":
  ✅ [1] Diseño Conversacional — Telegram + memoria persistente
  ✅ [2] Arquitectura Multi-Agente — 5 agentes + orquestador + Telegram
  ✅ [3] Uso Real de IA — Groq LLM + Whisper en cada interacción
  ✅ [4] Aplicabilidad 30 días — Stack $0, configuración en 1 hora
  ✅ [5] Escalabilidad — Supabase + webhook asíncrono
  ✅ [6] Claridad de Integración — API documentada + webhook Telegram

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /analitica
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
(Igual que antes + sección Telegram)

Sección "Analítica de Telegram":
  Gráfico línea: Mensajes por Telegram por día (últimos 14 días)
    SELECT DATE(created_at), COUNT(*) FROM conversations
    WHERE content_type IN ('text','voice') GROUP BY 1

  Distribución de tipos de mensaje:
  - Texto vs Voz (dona pequeña)
    SELECT content_type, COUNT(*) FROM conversations GROUP BY 1

  Fuentes de leads (dona):
    SELECT fuente, COUNT(*) FROM leads GROUP BY 1
    Telegram / Manual / Referido

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PÁGINA: /configuracion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Secciones:

"Mi Empresa" — editar datos generales:
  Nombre, Sector, Descripción, Voz de marca
  Lista de servicios ofrecidos (agregar/quitar)
  → UPDATE en Supabase tabla empresas

"Configuración de Telegram" — la más importante:
  Card con borde azul:
  - Campo: Bot Username (solo lectura, viene de /api/v1/telegram/info)
  - Badge: Webhook activo / inactivo
  - Botón "🔄 Reconfigurar Webhook"
  - Instrucciones paso a paso:
    1. Crear bot en @BotFather con /newbot
    2. Copiar el token en el archivo .env del servidor
    3. Hacer clic en "Reconfigurar Webhook"
    4. Compartir el enlace del bot con tus leads
  - Link: https://t.me/@bot_username (copiable)

"Notificaciones Admin":
  Toggle: Recibir alertas de leads nuevos
  Toggle: Recibir cuando se acepta una cotización
  Toggle: Recibir cuando se agenda una reunión
  Toggle: Resumen diario automático (hora configurable)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPONENTES ADICIONALES PARA TELEGRAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<TelegramBubble role="user|agent" content="" agente="" isVoice={} />
  Burbuja estilo Telegram con transcripción si es voz

<BotStatusCard username="" isActive={} leadsHoy={} mensajesHoy={} />
  Card de estado del bot para el dashboard

<TelegramBadge />
  Pequeño badge azul "📱 Telegram" para indicar origen

<VoiceTranscriptBadge transcription="" />
  Muestra 🎙️ + texto de transcripción en cursiva gris

<FuenteBadge fuente="telegram|manual|formulario|referido" />
  Badge coloreado por fuente del lead

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPORTAMIENTOS TÉCNICOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Supabase Realtime en:
   - agent_logs → feed de actividad del dashboard
   - conversations → actualizar chats en tiempo real
   - leads → contador en sidebar

2. React Query para todas las queries Supabase
   + invalidación automática al mutar

3. Toast (sonner):
   - "📱 Mensaje enviado por Telegram" (azul)
   - "🎙️ Voz transcrita con Whisper" (verde)
   - "🆕 Nuevo lead captado por Telegram" (verde)

4. AuthGuard en todas las rutas excepto /login

5. Banner si /health falla:
   "⚠️ Backend desconectado — Solo lectura"

6. Persistir session_id en sessionStorage por lead:
   key: orbita_session_${leadId}

7. Formato moneda: Intl.NumberFormat para COP/USD/EUR
   (configurable por empresa)

8. Tiempo relativo: formatDistanceToNow de date-fns en español
```

---

## INSTRUCCIONES DE USO — PASO A PASO

### Paso 1 — Crear el bot de Telegram
1. Abre Telegram → busca `@BotFather` → `/newbot`
2. Dale un nombre y un username al bot
3. Copia el **Bot Token** → lo necesitas en el `.env`
4. Escribe a `@userinfobot` en Telegram → copia tu **Chat ID** (para el admin)

### Paso 2 — Supabase (base de datos)
1. Ve a `supabase.com/dashboard` → tu proyecto
2. SQL Editor → pegar y ejecutar `supabase_schema.sql` generado por Copilot
3. Settings → API → copiar la **anon/public key** (para el frontend)

### Paso 3 — Backend con GitHub Copilot
1. VS Code → carpeta nueva `orbita-backend/`
2. Copilot Chat (`Ctrl+Shift+I`) → modo **Agent** → pegar Prompt Parte 1
3. Completar `.env` con las credenciales reales
4. `pip install -r requirements.txt && uvicorn main:app --reload`
5. En desarrollo con ngrok: `ngrok http 8000`
   → copiar URL ngrok → poner en `TELEGRAM_WEBHOOK_URL` del `.env`
6. `POST http://localhost:8000/api/v1/telegram/setup-webhook`
7. **Escribir al bot de Telegram** → debe responder en menos de 3 segundos ✅

### Paso 4 — Frontend con Lovable
1. `lovable.dev` → New Project → pegar Prompt Parte 2
2. Agregar variables de entorno en Lovable con las keys de Supabase
3. El frontend se conecta a Supabase (lectura) y al backend (IA + Telegram)

### Obtener GROQ_API_KEY gratis
→ `console.groq.com` → Sign Up → API Keys → Create
Sin tarjeta. 30 req/min gratuitas — suficiente para el hackathon.

---

*ORBITA · Sistema Inteligente de Ventas para Empresas de Servicios*
*Hackathon AI First 2026 — Funnelchat*
*"No se trata de tener más leads. Se trata de no dejar escapar ninguno."*
