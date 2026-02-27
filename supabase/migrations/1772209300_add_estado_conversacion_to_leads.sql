-- =========================================================
-- Migración: Agregar columna estado_conversacion a leads
-- Propósito: Permitir tracking de flujos conversacionales
-- multi-paso (ej: agendamiento de citas)
-- =========================================================

-- Agregar columna estado_conversacion
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS estado_conversacion TEXT DEFAULT 'normal' 
CHECK (estado_conversacion IN ('normal', 'agendando_cita', 'cita_confirmada', 'esperando_detalles', 'cotizacion_enviada'));

-- Agregar índice para búsquedas por estado de conversación
CREATE INDEX IF NOT EXISTS idx_leads_estado_conversacion ON leads(estado_conversacion);

-- Actualizar todos los leads existentes a estado normal
UPDATE leads SET estado_conversacion = 'normal' WHERE estado_conversacion IS NULL;

-- Comentario
COMMENT ON COLUMN leads.estado_conversacion IS 'Estado del flujo conversacional del lead para manejar conversaciones multi-paso';

-- Log de migración exitosa
DO $$
BEGIN
  RAISE NOTICE 'Migración completada: columna estado_conversacion agregada a tabla leads';
END $$;
