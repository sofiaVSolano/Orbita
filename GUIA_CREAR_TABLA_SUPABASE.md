## 📋 GUÍA: Crear tabla `telegram_bot_sessions` en Supabase

### Paso 1: Acceder a Supabase
1. Ve a https://app.supabase.com
2. Selecciona tu proyecto (xiblghevwgzuhytcqpyg)
3. En el menú izquierdo, selecciona: **SQL Editor**

### Paso 2: Ejecutar el SQL

Copia y pega el siguiente código en el SQL Editor:

```sql
-- Tabla para gestionar el estado de las sesiones de los bots de Telegram
-- Permite pausar/reanudar respuestas automáticas por lead

CREATE TABLE IF NOT EXISTS telegram_bot_sessions (
  -- Identificador único: el chat_id de Telegram
  telegram_chat_id TEXT PRIMARY KEY,
  
  -- Estado del bot para este chat: 'activo' (responde) o 'pausado' (no responde)
  estado_bot TEXT NOT NULL DEFAULT 'activo'
    CHECK (estado_bot IN ('activo', 'pausado')),
  
  -- Metadatos adicionales
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  
  -- Última vez que el admin pausó/reanudó el bot
  paused_by TEXT,  -- Username del admin que pausó
  paused_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_telegram_sessions_lead 
  ON telegram_bot_sessions(lead_id);

CREATE INDEX IF NOT EXISTS idx_telegram_sessions_estado 
  ON telegram_bot_sessions(estado_bot);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_telegram_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER telegram_sessions_update_timestamp
  BEFORE UPDATE ON telegram_bot_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_telegram_session_timestamp();

-- Comentarios para documentación
COMMENT ON TABLE telegram_bot_sessions IS 
  'Gestiona el estado de las conversaciones con los bots de Telegram. Permite pausar respuestas automáticas.';

COMMENT ON COLUMN telegram_bot_sessions.estado_bot IS 
  'Estado del bot: activo (responde automáticamente) o pausado (admin toma control manual)';

COMMENT ON COLUMN telegram_bot_sessions.telegram_chat_id IS 
  'Chat ID de Telegram del usuario (formato texto de python-telegram-bot)';
```

### Paso 3: Ejecutar
1. Haz clic en el botón azul **"Run"** (o presiona Ctrl+Enter)
2. Deberías ver un mensaje de confirmación: ✅ "Query successful"

### Paso 4: Verificar
Después de ejecutar:
1. Ve a la sección **"Tables"** en el menu izquierdo
2. Deberías ver `telegram_bot_sessions` en la lista
3. Haz clic para verificar que tiene las columnas:
   - `telegram_chat_id` (TEXT, PRIMARY KEY)
   - `estado_bot` (TEXT, DEFAULT 'activo')
   - `lead_id` (UUID, FK → leads)
   - `paused_by` (TEXT)
   - `paused_at` (TIMESTAMPTZ)
   - `created_at` (TIMESTAMPTZ)
   - `updated_at` (TIMESTAMPTZ)

### Paso 5: Habilitar RLS (Row Level Security)
1. Selecciona la tabla `telegram_bot_sessions`
2. Haz clic en **"RLS"** (arriba a la derecha)
3. Habilita RLS si lo deseas (recomendado para producción)
4. Para desarrollo, puedes dejar RLS deshabilitado

---

## ✅ Resultado

Una vez completado, tendrás una tabla completamente funcional con:
- ✅ Campos para gestionar estado del bot por chat
- ✅ Índices para búsquedas rápidas
- ✅ Trigger automático para actualizar `updated_at`
- ✅ Comentarios de documentación

**Tabla lista para que el backend guarde y consulte el estado de pausas/reanuhdas del bot.**
