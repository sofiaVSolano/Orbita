-- Agregar columnas de Telegram a la tabla leads
-- Necesarias para la integración con el bot de Telegram

ALTER TABLE leads
ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS telegram_username TEXT;

-- Índice para búsquedas rápidas por telegram_chat_id
CREATE INDEX IF NOT EXISTS idx_leads_telegram_chat_id ON leads(telegram_chat_id);

-- Modificar la restricción UNIQUE de email para permitir NULL
-- Esto es importante porque los leads de Telegram pueden no tener email inicial
ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_email_key;
ALTER TABLE leads ADD CONSTRAINT leads_email_key UNIQUE NULLS NOT DISTINCT (email);

-- Modificar columna email para permitir NULL
ALTER TABLE leads ALTER COLUMN email DROP NOT NULL;

-- Modificar columna interes para permitir NULL (se captura después en la conversación)
ALTER TABLE leads ALTER COLUMN interes DROP NOT NULL;

-- Comentarios
COMMENT ON COLUMN leads.telegram_chat_id IS 'ID del chat de Telegram del lead (único)';
COMMENT ON COLUMN leads.telegram_username IS 'Username de Telegram del lead';
