# 🔐 CONFIGURACIÓN DE CREDENCIALES - ORBITA
**Última actualización**: 27 de febrero de 2026

---

## 📍 UBICACIÓN DE ARCHIVOS DE CONFIGURACIÓN

| Ruta | Propósito | Estado |
|------|-----------|--------|
| `orbita_backend/.env` | Backend - Credenciales reales | ✅ Creado |
| `orbita_backend/.env.example` | Backend - Plantilla (sin secretos) | ✅ Actualizado |
| `orbita_frontend/.env` | Frontend - Variables de cliente | ✅ Creado |
| `orbita_frontend/.env.example` | Frontend - Plantilla (sin secretos) | ✅ Creado |

---

## 🔒 CREDENCIALES CONFIGURADAS

### Backend (`orbita_backend/.env`)

#### Supabase
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
```
- **Base de datos PostgreSQL**
- URL: https://your-project.supabase.co

#### Groq AI API
```env
GROQ_API_KEY=your-groq-api-key-here
```
- **6 Modelos configurados por agente:**
  - ORCHESTRATOR: `llama-3.3-70b-versatile`
  - CAPTADOR: `llama-3.3-70b-versatile`
  - CONVERSACIONAL: `llama-3.1-8b-instant`
  - IDENTIDAD: `mixtral-8x7b-32768`
  - COMUNICACION: `llama-3.1-70b-versatile`
  - ANALITICO: `gemma2-9b-it`

#### Telegram - Bot de Leads (Público)
```env
TELEGRAM_LEADS_BOT_TOKEN=8314936455:AAEM4UpXUCXJQJ89u8IiscHZw7K88PCAoSs
TELEGRAM_LEADS_WEBHOOK_URL=http://localhost:8000/api/v1/telegram/leads/webhook
TELEGRAM_LEADS_WEBHOOK_SECRET=orbita-leads-secret-2026
```
- **Uso**: Chat con prospectos
- **Visibilidad**: Pública (visible en redes)
- **Username**: Obtenido de BotFather

#### Telegram - Bot de Admin (Privado)
```env
TELEGRAM_ADMIN_BOT_TOKEN=8726441442:AAHk-dPnL7iwIrAhXInNs4yc-Nvk3pvHqlc
TELEGRAM_ADMIN_BOT_WEBHOOK_URL=http://localhost:8000/api/v1/telegram/admin/webhook
TELEGRAM_ADMIN_BOT_WEBHOOK_SECRET=orbita-admin-secret-2026
```
- **Uso**: Control de sistema para equipo interno
- **Visibilidad**: Privada (solo para admins)
- **Chat ID Registrado**: `8519120077`

#### Autenticación JWT
```env
JWT_SECRET=Zx91kslQp29slKXl_82mslQp29sKXlaPpQ91KXlqPpQ91KXlqPpQ91
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
- **Duración del token**: 24 horas
- Cambiar `JWT_SECRET` en producción

#### Credenciales Admin
```env
ADMIN_EMAIL=admin@orbita.ai
ADMIN_PASSWORD=change-this-secure-password
```
- Cambiar contraseña en producción

#### Settings
```env
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

#### Empresa
```env
EMPRESA_NOMBRE=ORBITA
EMPRESA_SECTOR=Consultoría
EMPRESA_DESCRIPCION=Ofrecemos servicios de consultoría empresarial
```

---

### Frontend (`orbita_frontend/.env`)

#### Supabase (Cliente)
```env
VITE_SUPABASE_URL=https://xiblghevwgzuhytcqpyg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- Anon Key: Clave pública para cliente (segura)
- Límites RLS (Row Level Security) en Supabase

#### Backend API
```env
VITE_API_URL=http://localhost:8000
```
- Proxies requests al backend
- Cambia a URL de producción al desplegar

#### Environment
```env
VITE_ENV=development
```
- `development` o `production`

---

## ✅ VERIFICACIÓN DE CONFIGURACIÓN

### Backend
```bash
# Entrar a la carpeta
cd orbita_backend

# Verificar variables
source .env && echo "✅ Variables cargadas"

# Probar conexión a Supabase
python3 -c "from database import get_db; db = get_db(); print('✅ Supabase conectado')"

# Probar API de Groq
python3 -c "from utils.groq_client import GroqClient; g = GroqClient(); print('✅ Groq conectado')"

# Iniciar servidor
uvicorn main:app --reload
```

### Frontend
```bash
# Entrar a la carpeta
cd orbita_frontend

# Verificar variables
cat .env | grep VITE

# Instalar dependencias
npm install

# Iniciar dev server
npm run dev
```

---

## 🚀 USAR LAS CREDENCIALES POR PRIMERA VEZ

### Paso 1: Verificar Backend
```bash
cd orbita_backend
python3 main.py
# Debería mostrar:
# ✅ Base de datos inicializada
# ✅ Bot de Leads: @... | webhook configurado
# ✅ Bot de Admin: @... | webhook configurado
```

### Paso 2: Verificar Frontend
```bash
cd orbita_frontend
npm run dev
# Acceder a: http://localhost:5173
# Login: admin@orbita.ai / change-this-secure-password
```

### Paso 3: Probar Telegram Bots
```bash
# Enviar GET a:
curl http://localhost:8000/health

# Debería retornar info de ambos bots
```

---

## ⚠️ SEGURIDAD - CHECKLIST

- ✅ Archivos `.env` están en `.gitignore` (no se suben a git)
- ✅ `.env.example` existe sin credenciales reales (para cola boradores)
- ⚠️ **ANTES DE PRODUCCIÓN:**
  - [ ] Cambiar `JWT_SECRET` a valor aleatorio fuerte
  - [ ] Cambiar `ADMIN_PASSWORD`
  - [ ] Cambiar webhook URLs a dominio de producción
  - [ ] Cambiar `ENVIRONMENT=production`
  - [ ] Usar variables de entorno del servidor (no .env local)
  - [ ] Rotar API keys cada 90 días

---

## 📖 REFERENCIAS

- **Supabase**: https://app.supabase.com
- **Groq Console**: https://console.groq.com
- **Telegram BotFather**: https://t.me/BotFather
- **Usuario Info Bot**: https://t.me/userinfobot (para obtener Chat ID)

---

## 🔄 PRÓXIMAS ACCIONES

Si las credenciales cambien o necesites actualizar:

1. Edita `.env` (no `.env.example`)
2. Reinicia el servidor backend: `uvicorn main:app --reload`
3. Recarga el frontend: presiona `Ctrl+R`
4. Verifica `/health` endpoint en postman o navegador

---

*Sistema ORBITA - Gestión Segura de Credenciales*
