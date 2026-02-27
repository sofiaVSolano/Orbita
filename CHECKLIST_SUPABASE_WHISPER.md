# ✅ CHECKLIST: Finalizar Implementación Supabase + Whisper

## 📋 Tarea 1: Crear tabla `telegram_bot_sessions` en Supabase

**Status:** ⏳ PENDIENTE EJECUCIÓN

### Instrucciones:

1. **Abre Supabase Dashboard**
   - URL: https://app.supabase.com
   - Selecciona tu proyecto: xiblghevwgzuhytcqpyg

2. **Navega a SQL Editor**
   - Menú izquierdo → "SQL Editor"

3. **Copia el SQL completo**
   - LEE el archivo: `/orbita_backend/migrations/create_telegram_bot_sessions.sql`
   - SELECCIONA TODO el contenido

4. **Pega y ejecuta en Supabase**
   - Pega en la ventana de SQL Editor
   - Haz clic en botón azul "Run"
   - Deberías ver: ✅ "Query successful"

5. **Verifica**
   - Ve a sección "Tables" (menú izquierdo)
   - Busca: `telegram_bot_sessions`
   - Verifica que tenga 7 columnas (ver detalles abajo)

**Archivo de referencia:** [GUIA_CREAR_TABLA_SUPABASE.md](GUIA_CREAR_TABLA_SUPABASE.md)

### Estructura esperada después de ejecutar:

```
Tabla: telegram_bot_sessions
├── telegram_chat_id    (TEXT, PRIMARY KEY)
├── estado_bot          (TEXT, DEFAULT 'activo')
├── lead_id             (UUID, FK → leads)
├── paused_by           (TEXT)
├── paused_at           (TIMESTAMPTZ)
├── created_at          (TIMESTAMPTZ, DEFAULT NOW())
└── updated_at          (TIMESTAMPTZ, DEFAULT NOW())
```

---

## 📋 Tarea 2: Verificar Whisper Implementation

**Status:** ✅ **COMPLETADO**

### Cambios realizados:

✅ **Archivo:** [orbita_backend/telegram/leads_handler.py](orbita_backend/telegram/leads_handler.py)

**Imports agregados (línea 6-7):**
```python
import os
import tempfile
```

**Método `_transcribir_voz()` reescrito (líneas 378-420):**
- ❌ ANTES: Retornaba texto placeholder
- ✅ AHORA: Integrado con Groq Whisper API
- ✅ Descarga archivo de voz desde Telegram
- ✅ Crea archivo temporal .ogg
- ✅ Envía a Groq Whisper para transcripción
- ✅ Limpia archivo temporal automáticamente
- ✅ Manejo robusto de errores

### Cómo funciona ahora:

1. Usuario envía nota de voz
2. `_transcribir_voz()` es llamado
3. Descarga bytes de voz de Telegram
4. Crea archivo temp + envía a Groq Whisper
5. Obtiene texto transcrito
6. Elimina archivo temporal
7. Retorna texto (se procesa como mensaje normal)

**Documentación completa:** [IMPLEMENTACION_WHISPER_TRANSCRIPTION.md](IMPLEMENTACION_WHISPER_TRANSCRIPTION.md)

---

## 🧪 Testing Workflow

### Después de completar Tarea 1 (Supabase):

**En tu cliente Telegram:**

```
1. Abre el chat con @orbita_cliente_bot
2. Envía /start
3. Graba una NOTA DE VOZ (5-30 segundos)
4. Envía la nota
5. Espera respuesta
```

**Revisa logs del backend:**

```bash
docker logs orbita_backend -f
```

**Deberías ver algo como:**

```
✅ Nota de voz transcrita (10s, 24680 bytes)
   Texto: "Hola, estoy interesado en tus servicios"
🤖 [Orquestador] Activando agentes...
📊 [Captador] Analizando lead...
💬 [Conversacional] Generando respuesta...
```

---

## 🔄 Estado del Sistema

| Componente | Status | Detalles |
|-----------|--------|----------|
| **Backend Structure** | ✅ | Carpetas migradas, handlers creados |
| **Telegram Handlers** | ✅ | LeadsBotHandler + AdminBotHandler |
| **API Endpoints** | ✅ | `/leads/webhook`, `/admin/webhook` |
| **Frontend UI** | ✅ | Dual-bot cards y config blocks |
| **Environment Vars** | ✅ | 28 backend + 4 frontend |
| **Whisper Integration** | ✅ | Implementado en leads_handler.py |
| **DB: telegram_bot_sessions** | ⏳ | **PENDIENTE CREAR** |
| **End-to-End Testing** | ⏳ | Pendiente después de ↑ |

---

## 📝 Pasos en Orden

### 🔴 **CRÍTICO - Hacer AHORA:**
1. Ejecutar SQL en Supabase (Tarea 1)
2. Verificar tabla creada

### 🟡 **DESPUÉS - Testing:**
1. Reiniciar backend (`docker restart orbita_backend`)
2. Enviar nota de voz al bot desde Telegram
3. Revisar logs para Whisper output
4. Verificar que bot responde

### 🟢 **LUEGO - Ir a Producción:**
1. Ejecutar tests completos
2. Actualizar documentación
3. Deploy a servidor

---

## 🆘 Troubleshooting

### ❓ "Tabla no aparece en Supabase después de ejecutar SQL"

**Posibles causas:**
```bash
1. SQL tiene errores sintácticos → Revisa el erro en Supabase
2. No presionaste "Run" → ¡Presiona el botón azul!
3. Proyecto diferente → Verifica que estés en xiblghevwgzuhytcqpyg
```

**Solución:**
```sql
-- En Supabase SQL Editor, ejecuta esto para verificar:
SELECT * FROM telegram_bot_sessions LIMIT 1;
-- Si falla: tabla no existe
-- Si success pero 0 rows: tabla existe pero está vacía (normal)
```

### ❓ "Transcripción retorna NULL o error"

**Posibles causas:**
```
1. GROQ_API_KEY invalida en .env
2. Plan de Groq no incluye Whisper
3. Archivo de audio corrupto
4. Audio muy silencioso
```

**Solución:**
```bash
# Verifica API key
grep GROQ_API_KEY orbita_backend/.env
# Debería ser: GROQ_API_KEY=gsk_XXXXXXXXX...

# Revisa logs del backend
docker logs orbita_backend | grep "Error transcribiendo"
```

### ❓ "Backend no inicia después de cambios"

**Solución:**
```bash
# Limpia y reinicia
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Contactos Importantes

| Servicio | URL | Para |
|----------|-----|------|
| **Supabase** | https://app.supabase.com | Crear tabla |
| **Groq API** | https://console.groq.com | Verificar plan Whisper |
| **Telegram Bot** | @orbita_cliente_bot | Testear |

---

## 📚 Archivos Referencias

- [Guía Supabase](GUIA_CREAR_TABLA_SUPABASE.md)
- [Implementación Whisper](IMPLEMENTACION_WHISPER_TRANSCRIPTION.md)
- [SQL Migration](orbita_backend/migrations/create_telegram_bot_sessions.sql)
- [Leads Handler](orbita_backend/telegram/leads_handler.py)

---

## ✨ Siguiente Fase

Después de completar esto:

1. **Pausa/Reanuda de Bot**
   - Comando `/pausa` en admin bot
   - Guarda estado en `telegram_bot_sessions`
   - Leads bot no responde mientras está pausado

2. **Alertas en Admin Bot**
   - `/alertas` muestra activity log
   - Nuevos leads notification
   - Conversaciones sin respuesta

3. **Estadísticas**
   - `/stats` en admin bot
   - Leads convertidos, respuesta tiempo, etc.

---

**¡Éxito! 🚀**
