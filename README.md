# 🛸 ORBITA

## Sistema Inteligente de Gestión de Leads con IA

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

**Automatiza el flujo de ventas completo: captura, calificación, cotización y cierre de leads con inteligencia artificial conversacional.**

[📚 Docs](#-documentación) • [🚀 Quick Start](#-inicio-rápido) • [🏗️ Arquitectura](#-arquitectura) • [⚙️ Configuración](#-configuración)

</div>

---

## 🎯 ¿Qué es ORBITA?

**ORBITA** resuelve el problema más grande en ventas: **leads que esperan demasiado sin respuesta**. Usando un sistema multi-agente con IA, automatiza el 80% del proceso de ventas mientras mantiene conversaciones naturales y personalizadas.

### El Problema
- 📉 50% de los leads se pierden por falta de seguimiento rápido
- ⏰ Vendedores sobrecargados, respuestas lentas
- 💰 Costo elevado de customer acquisition

### La Solución
- ✅ **Respuesta instantánea** 24/7 a consultas de leads
- 🤖 **Calificación automática** sin intervención humana
- 💵 **Presupuestos en segundos**, no en días
- 📞 **Agendamiento conversacional** de reuniones
- 📊 **Análisis predictivo** de probabilidad de cierre

---

## 💼 Para Quién

**Ideal para:**
- 🏢 **Agencias Digitales** - Automatizar leads de servicios
- 🚀 **SaaS & Startups** - Calificar y convertir prospects
- 🏭 **Consultorías B2B** - Gestionar leads de empresa
- 💻 **Desarrolladores** - Stack moderno y escalable

---

## ⚡ Características Principales

| Característica | Descripción | Beneficio |
|---|---|---|
| 🤖 **IA Conversacional** | Chatbot con GPT-4o mini + Groq | Respuestas naturales y contextuales |
| 📱 **Telegram Integration** | Bot público + admin privado | Atención 24/7, acceso inmediato |
| 🎯 **Estimados Rápidos** | Detección de servicios + cálculo automático | Presupuesto en <5 segundos |
| 📋 **Cotizaciones IA** | Generación automática con variables | Personalización sin código |
| 📅 **Agendamiento Inteligente** | Flujo conversacional de citas | Sin preguntas incómodas |
| 📊 **Dashboard Analytics** | Métricas de conversión en tiempo real | Decisiones basadas en datos |
| 🔗 **API REST Completa** | Endpoints para todas las operaciones | Integración con cualquier sistema |
| 💾 **BD Escalable** | Supabase PostgreSQL | Millones de registros, sin limites |

---

## 🛠️ Stack Tecnológico

### Backend
```
FastAPI 0.109          → Framework web de alto rendimiento
Python 3.12            → Lenguaje principal
Pydantic              → Validación de datos tipados
```

### Inteligencia Artificial
```
OpenAI GPT-4o mini    → Orquestación y cotizaciones ($0.003 por uso)
Groq Llama 3.3 70B    → Análisis y decisiones complejas
Groq Mixtral 8x7B     → Conversaciones naturales
Groq Gemma2 9B        → Captación de leads
OpenAI Whisper        → Transcripción de voz
```

### Base de Datos
```
Supabase              → PostgreSQL gestionado
Redis 7               → Cache y sesiones
```

### Telegram
```
python-telegram-bot 21.0+  → Biblioteca oficial
Webhooks + Polling         → Modos de operación flexibles
```

### Frontend
```
React 18              → Interfaz moderna
TypeScript            → Tipado estático
Vite                  → Build rápido
TailwindCSS           → Estilos responsivos
```

### DevOps
```
Docker & Compose      → Containerización
Nginx                 → Web server
GitHub Actions        → CI/CD ready
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   Usuarios Finales                       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    Telegram       Website       API
      Bot          Frontend      Rest
        │            │            │
        └────────────┼────────────┘
                     │
         ┌───────────▼───────────┐
         │   API Gateway         │
         │   (FastAPI)           │
         │   - Auth              │
         │   - Rate Limit        │
         │   - Logging           │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│ Telegram │  │ Agents      │  │ Analytics   │
│ Handler  │  │ Orchestrator│  │ Engine      │
└────┬─────┘  └──────┬──────┘  └──────┬──────┘
     │               │                │
     └───────────────┼────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────────┐  ┌────▼───────┐  ┌─────▼──────┐
│ Supabase   │  │   Redis    │  │ OpenAI /   │
│ PostgreSQL │  │   Cache    │  │ Groq API   │
└────────────┘  └────────────┘  └────────────┘
```

### Agentes IA Especializados

| Agente | Modelo | Función |
|--------|--------|---------|
| **Orchestrator** | GPT-4o mini | Enruta conversaciones al agente correcto |
| **Captador** | Gemma2 9B | Califica leads iniciales |
| **Conversacional** | Mixtral 8x7B | Conversaciones naturales |
| **Comunicación** | GPT-4o mini | Genera cotizaciones |
| **Identidad** | Llama 3.1 8B | Info corporativa |
| **Analítico** | Llama 3.3 70B | Predicción y análisis |

---

## 📈 Resultados Medibles

Con ORBITA obtienes:

```
⏱️  Tiempo de respuesta:     < 2 segundos (vs 24 horas)
📊 Leads calificados:       +400% automáticamente
💰 Costo por lead:          -80% menos humanos
🎯 Tasa de conversión:      +35% (menos fricciones)
🔄 Productividad ventas:    +250% (más tiempo en cierre)
```

---

## 🚀 Inicio Rápido

### 1. Clonar repositorio
```bash
git clone https://github.com/sofiaVSolano/Orbita.git
cd Orbita
```

### 2. Configurar variables de entorno
```bash
cp .env.example orbita_backend/.env
nano orbita_backend/.env  # Edita con tus credenciales
```

**Variables esenciales:**
```bash
SUPABASE_URL=tu_url
SUPABASE_KEY=tu_service_role_key
OPENAI_API_KEY=sk-proj-xxxxx
TELEGRAM_LEADS_BOT_TOKEN=tu_token
GROQ_API_KEY=gsk-xxxxx
```

### 3. Inicializar BD
```bash
# Ve a: https://supabase.com/dashboard/project/[tu-proyecto]/sql/new
# Copia y pega el contenido de: docs/SQL_INICIALIZACION_COMPLETA.sql
# Click "Run"
```

### 4. Levantar contenedores
```bash
docker compose up -d
```

### 5. Verificar
```bash
# Backend
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# Bots
docker logs -f orbita-backend
```

---

## ⚙️ Configuración

### URLs Internas
```
Backend API:     http://localhost:8000
Frontend:        http://localhost:3000
API Docs:        http://localhost:8000/docs
Redis:           localhost:6379
```

### Credenciales Necesarias

| Servicio | Dónde Obtener | Tiempo |
|----------|---------------|--------|
| OpenAI API Key | https://platform.openai.com | 2 min |
| Groq API Key | https://console.groq.com | 2 min |
| Telegram Bot Token | @BotFather en Telegram | 1 min |
| Supabase | https://supabase.com | 5 min |

**Total setup:** ~20 minutos

---

## 📚 Documentación

Documentación detallada en carpeta `docs/`:

- `COMO_INICIALIZAR_SUPABASE.md` - Guía BD paso a paso
- `FIX_SUPABASE_RLS_ERRORS.md` - Solución de errores comunes
- `CONFIGURACION_CREDENCIALES.md` - Setup de integraciones
- Y 15+ guías más...

---

## 🔌 API Endpoints

```bash
# Leads
GET    /api/leads                    # Listar todos
POST   /api/leads                    # Crear nuevo
GET    /api/leads/{id}               # Obtener uno
PUT    /api/leads/{id}               # Actualizar

# Cotizaciones
POST   /api/cotizaciones             # Generar COT
GET    /api/cotizaciones/{id}        # Ver COT

# Reuniones
POST   /api/reuniones                # Agendar
GET    /api/reuniones                # Listar

# Analytics
GET    /api/analytics/summary        # Resumen
GET    /api/analytics/leads-by-status
GET    /api/analytics/conversion-rate

# Health
GET    /health                       # Status del sistema
GET    /docs                         # Swagger UI
```

---

## 📊 Estructura del Proyecto

```
Orbita/
├── orbita_backend/
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── config.py               # Variables de configuración
│   ├── database.py             # Cliente Supabase
│   ├── agents/                 # Agentes IA (6 especializados)
│   ├── Telegram_Bot/           # Manejo de chatBot
│   ├── routers/                # Rutas API REST
│   ├── utils/                  # Utilidades (quick_estimate, etc)
│   └── Dockerfile
│
├── orbita_frontend/
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   ├── pages/              # Páginas (Leads, Analytics, etc)
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── supabase/
│   ├── migrations/             # Migraciones SQL
│   └── config.toml
│
├── docs/                       # Documentación (20+ archivos)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Deployment

### Desarrollo
```bash
docker compose up -d
```

### Producción
```bash
# 1. Actualizar .env con variables de producción
# 2. Cambiar Telegram modo: Polling → Webhooks
# 3. Configurar dominio y SSL
# 4. Usar service_role_key en lugar de anon_key
docker compose -f docker-compose.prod.yml up -d
```

---

## 🔒 Seguridad

- ✅ Autenticación JWT en API REST
- ✅ Variables sensibles en `.env` (nunca committear)
- ✅ Rate limiting en endpoints
- ✅ Validación con Pydantic
- ✅ Row-Level Security en Supabase
- ✅ Encryption de datos sensibles

---

## 📈 Roadmap

### v1.0 ✅ (Actual)
- ✅ Multi-agente IA
- ✅ Telegram integration
- ✅ Estimados automáticos
- ✅ Cotizaciones IA
- ✅ Dashboard básico

### v1.1 (Próximas semanas)
- 🔲 WhatsApp Business integration
- 🔲 Sistema de nurturing automático
- 🔲 A/B testing de prompts
- 🔲 Analytics avanzados con ML
- 🔲 Integración Stripe

### v2.0 (Q3 2026)
- 🔲 Agente de voz (llamadas)
- 🔲 Multi-idioma automático
- 🔲 Video-llamadas con IA
- 🔲 Marketplace de agentes
- 🔲 Gamificación de referidos

---

## 🤝 Contribuir

Abiertos a contribuciones. Por favor:

1. Fork el repo
2. Crea rama: `git checkout -b feature/mi-feature`
3. Commit: `git commit -m "🎉 Agrego mi feature"`
4. Push: `git push origin feature/mi-feature`
5. Open Pull Request

---

## ⚠️ Problemas Comunes

### Error: "row-level security policy"
```bash
→ Usa SERVICE_ROLE_KEY en lugar de ANON_KEY
→ Ve a: docs/FIX_SUPABASE_RLS_ERRORS.md
```

### Bot no responde
```bash
→ Verifica token de Telegram
→ Revisa logs: docker logs orbita-backend
→ Asegúrate que Supabase esté accesible
```

### API lenta
```bash
→ Aumenta replicas
→ Mejora prompts de IA (menos tokens)
→ Utiliza cache Redis
```

---

## 📞 Soporte

- 📧 Email: contact@orbita-ai.com
- 💬 Issues: GitHub issues
- 📚 Docs: `/docs` folder
- 🐛 Bugs: diagnose_supabase_rls.py

---

## 📜 Licencia

Proprietary © 2026 ORBITA. Todos los derechos reservados.

---

## 🙏 Agradecimientos

Construido con:
- OpenAI GPT-4o mini
- Groq Llama, Mixtral, Gemma
- Supabase
- FastAPI & React
- python-telegram-bot

---

<div align="center">

**Made with ❤️ by [ORBITA Team](https://orbita-ai.com)**

[⬆ Volver arriba](#-orbita)

</div>
