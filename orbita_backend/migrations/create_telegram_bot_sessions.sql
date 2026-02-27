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
