-- Tabla de empresas/companies
CREATE TABLE IF NOT EXISTS empresas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  ruc TEXT UNIQUE,
  email TEXT UNIQUE,
  telefono TEXT,
  website TEXT,
  direccion TEXT,
  ciudad TEXT,
  pais TEXT,
  industria TEXT,
  tamaño_empleados INTEGER,
  presupuesto_anual DECIMAL(15, 2),
  estado TEXT DEFAULT 'activa' CHECK (estado IN ('activa', 'inactiva', 'suspendida')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_empresas_email ON empresas(email);
CREATE INDEX idx_empresas_ruc ON empresas(ruc);

-- Tabla de logs de agentes
CREATE TABLE IF NOT EXISTS agent_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_name TEXT NOT NULL,
  action TEXT NOT NULL,
  session_id TEXT,
  user_id INTEGER,
  empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
  details JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  duration_ms INTEGER,
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_agent ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_timestamp ON agent_logs(timestamp DESC);
CREATE INDEX idx_agent_logs_session ON agent_logs(session_id);

-- Tabla de conversaciones
CREATE TABLE IF NOT EXISTS conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  session_id TEXT,
  tipo_comunicacion TEXT DEFAULT 'telegram' CHECK (tipo_comunicacion IN ('telegram', 'whatsapp', 'email', 'telefono')),
  agentes_intervenidos TEXT[] DEFAULT ARRAY[]::TEXT[],
  historial JSONB,
  estado TEXT DEFAULT 'en_progreso' CHECK (estado IN ('en_progreso', 'completada', 'pausada', 'cancelada')),
  proxima_accion TEXT,
  fecha_proxima_accion TIMESTAMPTZ,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_lead ON conversations(lead_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);

-- Tabla de campanas
CREATE TABLE IF NOT EXISTS campaigns (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  tipo TEXT NOT NULL CHECK (tipo IN ('email', 'telegram', 'whatsapp', 'sms', 'redes_sociales', 'webinar', 'contenido', 'nurturing')),
  segmentacion TEXT DEFAULT 'todos' CHECK (segmentacion IN ('todos', 'leads_nuevos', 'leads_calificados', 'leads_cotizados', 'leads_perdidos', 'clientes_actuales', 'leads_inactivos')),
  estado TEXT DEFAULT 'borrador' CHECK (estado IN ('borrador', 'programada', 'activa', 'pausada', 'completada', 'cancelada', 'fallida')),
  fecha_inicio TIMESTAMPTZ,
  fecha_fin TIMESTAMPTZ,
  mensaje_asunto TEXT,
  mensaje_contenido TEXT,
  audiencia_total INTEGER DEFAULT 0,
  enviados INTEGER DEFAULT 0,
  entregados INTEGER DEFAULT 0,
  abiertos INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversiones INTEGER DEFAULT 0,
  tasa_apertura DECIMAL(5, 2),
  tasa_click DECIMAL(5, 2),
  tasa_conversion DECIMAL(5, 2),
  generada_por_ia BOOLEAN DEFAULT false,
  agente_generador TEXT,
  empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
  user_id INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  executed_at TIMESTAMPTZ
);

CREATE INDEX idx_campaigns_empresa ON campaigns(empresa_id);
CREATE INDEX idx_campaigns_estado ON campaigns(estado);

-- Tabla de cotizaciones
CREATE TABLE IF NOT EXISTS quotations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_cotizacion TEXT NOT NULL UNIQUE,
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
  descripcion_producto TEXT NOT NULL,
  cantidad DECIMAL(10, 2),
  precio_unitario DECIMAL(15, 2),
  subtotal DECIMAL(15, 2),
  impuesto DECIMAL(15, 2) DEFAULT 0,
  total DECIMAL(15, 2),
  moneda TEXT DEFAULT 'USD',
  valida_hasta TIMESTAMPTZ,
  condiciones_pago TEXT,
  notas TEXT,
  estado TEXT DEFAULT 'borrador' CHECK (estado IN ('borrador', 'enviada', 'aceptada', 'rechazada', 'expirada')),
  agente_generador TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  responded_at TIMESTAMPTZ
);

CREATE INDEX idx_quotations_lead ON quotations(lead_id);
CREATE INDEX idx_quotations_numero ON quotations(numero_cotizacion);
CREATE INDEX idx_quotations_estado ON quotations(estado);

-- Tabla de reuniones
CREATE TABLE IF NOT EXISTS meetings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  fecha_hora TIMESTAMPTZ NOT NULL,
  duracion_minutos INTEGER DEFAULT 30,
  tipo_reunon TEXT DEFAULT 'videoconferencia' CHECK (tipo_reunon IN ('presencial', 'telefonica', 'videoconferencia', 'email')),
  ubicacion TEXT,
  enlace_videoconferencia TEXT,
  asistentes TEXT[],
  estado TEXT DEFAULT 'programada' CHECK (estado IN ('programada', 'confirmada', 'realizada', 'cancelada', 'posergada')),
  agente_que_programo TEXT,
  notas_previas TEXT,
  notas_posteriores TEXT,
  resultado TEXT,
  proxima_accion TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  cancelled_at TIMESTAMPTZ
);

CREATE INDEX idx_meetings_lead ON meetings(lead_id);
CREATE INDEX idx_meetings_fecha ON meetings(fecha_hora);
CREATE INDEX idx_meetings_estado ON meetings(estado);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER empresas_update_timestamp BEFORE UPDATE ON empresas FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER conversations_update_timestamp BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER campaigns_update_timestamp BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER quotations_update_timestamp BEFORE UPDATE ON quotations FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER meetings_update_timestamp BEFORE UPDATE ON meetings FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Comentarios
COMMENT ON TABLE agent_logs IS 'Registra la actividad de todos los agentes IA del sistema';
COMMENT ON TABLE conversations IS 'Historial de conversaciones con leads por diferentes canales';
COMMENT ON TABLE campaigns IS 'Campañas de marketing automatizadas';
COMMENT ON TABLE quotations IS 'Cotizaciones generadas para leads';
COMMENT ON TABLE meetings IS 'Reuniones programadas con leads y clientes';
COMMENT ON TABLE empresas IS 'Datos de empresas/clientes del sistema';
