-- Tabla de leads
CREATE TABLE IF NOT EXISTS leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  email TEXT NOT NULL,
  telefono TEXT,
  empresa TEXT,
  cargo TEXT,
  interes TEXT NOT NULL,
  presupuesto DECIMAL(15, 2),
  moneda TEXT DEFAULT 'USD',
  timeline TEXT,
  status TEXT DEFAULT 'nuevo' CHECK (status IN ('nuevo', 'contactado', 'calificado', 'cotizado', 'reunion_programada', 'propuesta_enviada', 'ganado', 'perdido', 'cancelado')),
  origen TEXT DEFAULT 'manual' CHECK (origen IN ('telegram', 'whatsapp', 'website', 'referido', 'manual', 'campaña', 'redes_sociales', 'email', 'telefono')),
  notas TEXT,
  qualification_score INTEGER,
  user_id INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(email)
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_origen ON leads(origen);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_leads_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER leads_update_timestamp
  BEFORE UPDATE ON leads
  FOR EACH ROW
  EXECUTE FUNCTION update_leads_timestamp();

-- Comentarios
COMMENT ON TABLE leads IS 'Tabla principal de gestión de leads/prospects para el sistema de ventas';
COMMENT ON COLUMN leads.qualification_score IS 'Score de calificación del lead (0-100)';
COMMENT ON COLUMN leads.origen IS 'Canal de origen del lead (Telegram, Email, Website, etc)';
