# 🚀 QUICK START - ORBITA
**Levanta el sistema completo en 5 minutos**

---

## ✅ Requisitos Previos

```bash
# Verificar que tengas:
python3 --version        # Python 3.8+
node --version           # Node.js 16+
npm --version            # npm 8+
```

---

## 📦 PASO 1: Backend (Terminal 1)

```bash
# Ir al directorio del backend
cd orbita_backend

# Crear entorno virtual (si no existe)
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# o para Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Validar credenciales
python3 validate_credentials.py

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000

🛸 ORBITA iniciado — 2 bots activos | 5 agentes | Sistema listo
```

**Accesos:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🎨 PASO 2: Frontend (Terminal 2)

```bash
# Ir al directorio del frontend
cd orbita_frontend

# Instalar dependencias
npm install

# Validar credenciales
node validate_credentials.js

# Iniciar servidor de desarrollo
npm run dev
```

**Resultado esperado:**
```
  VITE v4.x.x  build ready in xxxms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Acceso:**
- Frontend: http://localhost:5173

---

## 🔑 PASO 3: Iniciar Sesión

1. Abre http://localhost:5173
2. Login con:
   - **Email**: `admin@orbita.ai`
   - **Password**: `change-this-secure-password`

---

## ✨ Verificación de Servicios

### En la misma terminal o una nueva:

```bash
# Ver si todos los servicios están activos
curl http://localhost:8000/health | jq '.'

# Debería retornar:
{
  "status": "healthy",
  "timestamp": "2026-02-27T...",
  "services": {
    "api": "running",
    "database": "connected",
    "telegram_bots": "active",
    "groq_api": "available"
  },
  "telegram_bots": {
    "bot_leads": {
      "username": "...",
      "webhook_url": "..."
    },
    "bot_admin": {
      "username": "...",
      "webhook_url": "..."
    }
  }
}
```

---

## 🧪 Probar Características

### 1. API (Postman o curl)

```bash
# Ver documentación interactiva
open http://localhost:8000/docs

# O enviar una solicitud de prueba
curl -X GET http://localhost:8000/ | jq '.'
```

### 2. Supabase

```bash
# Backend conectado a Supabase
# Verifica en: https://app.supabase.com
# Proyecto: xiblghevwgzuhytcqpyg
```

### 3. Groq API

```bash
# Verificar que los agentes pueden usar Groq
# Ver en orbita_backend/validate_credentials.py
# 6 modelos diferentes configurados para cada agente
```

### 4. Telegram Bots

```bash
# Bot de Leads (para prospectos)
# @orbita_cliente_bot (o el tuyo)

# Bot de Admin (para equipo)
# @orbita_admin_bot (o el tuyo)

# Escribe /start en ambos para probar
```

---

## 🛑 Detener el Sistema

```bash
# Terminal con Backend:
# Presiona Ctrl+C

# Terminal con Frontend:
# Presiona Ctrl+C

# Desactivar entorno virtual (opcional):
deactivate
```

---

## 📊 Estructura de Carpetas Importante

```
ORBITA/
├── orbita_backend/
│   ├── .env                    ← CREDENCIALES SECRETAS
│   ├── main.py                 ← Punto de entrada
│   ├── config.py               ← Lee variables de .env
│   ├── telegram/               ← Soporte de 2 bots
│   ├── agents/                 ← 6 agentes IA
│   └── routers/                ← Endpoints API
│
└── orbita_frontend/
    ├── .env                    ← Variables VITE_*
    ├── src/main.tsx            ← Punto de entrada React
    ├── src/pages/              ← Dashboard, Leads, Analytics
    └── src/components/         ← Componentes React
```

---

## 🔐 Archivos Importantes (NO los toques sin saber)

| Archivo | Por qué | Acción |
|---------|---------|--------|
| `.env` | Contiene credenciales | NO subir a git ✅ `.gitignore` |
| `.env.example` | Plantilla sin secretos | SÍ subir a git |
| `config.py` | Lee las credenciales | Solo editar si necesitas nuevas vars |
| `main.py` | Punto de entrada | Solo editar si cambias estructura |

---

## ⚠️ Problemas Comunes

### Backend no inicia

```bash
# 1. Verifica que Python esté instalado
python3 --version

# 2. Verifica que .env existe
ls -la orbita_backend/.env

# 3. Valida credenciales
python3 orbita_backend/validate_credentials.py

# 4. Reinstala dependencias
pip install --upgrade -r requirements.txt
```

### Frontend no inicia

```bash
# 1. Verifica Node.js
node --version

# 2. Limpia caché de npm
rm -rf node_modules
npm install

# 3. Valida credenciales
node orbita_frontend/validate_credentials.js
```

### No puedo conectar Backend ↔ Frontend

```bash
# Verifica:
# 1. VITE_API_URL=http://localhost:8000 en .env frontend
# 2. Backend corriendo en puerto 8000
# 3. CORS habilitado en main.py

# Prueba:
curl -X GET http://localhost:8000/health
```

### Errores de credenciales

```bash
# 1. Copia las credenciales sinceras en:
# orbita_backend/.env
# orbita_frontend/.env

# 2. Verifica que no tengan espacios extras:
# ✅ GOOD: VITE_API_URL=http://localhost:8000
# ❌ BAD: VITE_API_URL = http://localhost:8000

# 3. Reinicia el servidor
```

---

## 🎯 Siguientes Pasos Después de Verificar

1. **Crear un lead de prueba**
   - Ve a http://localhost:5173/leads
   - Crea un nuevo lead manualmente

2. **Probar Telegram**
   - Escribe al bot de leads
   - Prueba comandos en bot de admin: `/start`, `/leads`, `/stats`

3. **Ver analítica**
   - Dashboard en http://localhost:5173/dashboard
   - Métricas de leads y bots

4. **Explorar API**
   - Documentación en http://localhost:8000/docs
   - Prueba endpoints en Swagger UI

---

## 📞 Soporte Rápido

```bash
# Ver logs en tiempo real
tail -f /tmp/orbita.log

# Verificar puertos en uso
lsof -i :8000    # Backend
lsof -i :5173    # Frontend

# Verificar variables de entorno (backend)
python3 orbita_backend/validate_credentials.py

# Verificar variables de entorno (frontend)
node orbita_frontend/validate_credentials.js
```

---

## ✅ Checklist Final

- ✅ Backend iniciado en puerto 8000
- ✅ Frontend iniciado en puerto 5173
- ✅ Puedo acceder a http://localhost:5173
- ✅ Puedo ver http://localhost:8000/docs
- ✅ Health check retorna status "healthy"
- ✅ Base de datos conectada (Supabase)
- ✅ Groq API disponible
- ✅ Telegram bots configurados
- ✅ Puedo hacer login con admin@orbita.ai

---

**¡Listo! Tu sistema ORBITA está funcionando. 🚀**

Para más detalles, ver:
- [CONFIGURACION_CREDENCIALES.md](./CONFIGURACION_CREDENCIALES.md) — Guía detallada de credenciales
- [RESUMEN_CREDENCIALES.md](./RESUMEN_CREDENCIALES.md) — Resumen de lo que se configuró
- [orbita_backend/README.md](./orbita_backend/README.md) — Documentación del backend
