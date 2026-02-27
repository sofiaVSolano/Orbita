-- =========================================================
-- Migración: Configurar políticas RLS para operaciones backend
-- Propósito: Permitir que el backend inserte y actualice datos
-- sin restricciones de Row-Level Security
-- =========================================================

-- ===========================
-- CONVERSATIONS TABLE
-- ===========================

-- Deshabilitar RLS existente temporalmente para agregar políticas
ALTER TABLE conversations DISABLE ROW LEVEL SECURITY;

-- Habilitar RLS nuevamente  
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Política: Permitir todas las operaciones al service_role
CREATE POLICY "Service role tiene acceso completo a conversations"
  ON conversations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Política: Permitir inserciones desde backend (authenticated)
CREATE POLICY "Backend puede insertar conversations"
  ON conversations
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Política: Permitir actualizaciones desde backend (authenticated)
CREATE POLICY "Backend puede actualizar conversations"
  ON conversations
  FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Política: Permitir selects desde backend (authenticated)
CREATE POLICY "Backend puede leer conversations"
  ON conversations
  FOR SELECT
  TO authenticated
  USING (true);

-- Política: Permitir todas las operaciones al usuario anónimo para testing
-- ADVERTENCIA: Deshabilitar en producción
CREATE POLICY "Anon puede acceder conversations (solo desarrollo)"
  ON conversations
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);


-- ===========================
-- AGENT_LOGS TABLE
-- ===========================

-- Deshabilitar RLS existente temporalmente
ALTER TABLE agent_logs DISABLE ROW LEVEL SECURITY;

-- Habilitar RLS nuevamente
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

-- Política: Permitir todas las operaciones al service_role
CREATE POLICY "Service role tiene acceso completo a agent_logs"
  ON agent_logs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Política: Permitir inserciones desde backend (authenticated)
CREATE POLICY "Backend puede insertar agent_logs"
  ON agent_logs
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Política: Permitir selects desde backend (authenticated)
CREATE POLICY "Backend puede leer agent_logs"
  ON agent_logs
  FOR SELECT
  TO authenticated
  USING (true);

-- Política: Permitir todas las operaciones al usuario anónimo para testing
-- ADVERTENCIA: Deshabilitar en producción
CREATE POLICY "Anon puede acceder agent_logs (solo desarrollo)"
  ON agent_logs
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);


-- ===========================
-- LEADS TABLE
-- ===========================

-- Verificar si RLS está habilitado, si no lo está, habilitarlo
DO $$
BEGIN
  ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'RLS ya habilitado en leads o error: %', SQLERRM;
END $$;

-- Política: Permitir todas las operaciones al service_role
CREATE POLICY "Service role tiene acceso completo a leads"
  ON leads
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Política: Permitir todas las operaciones al usuario anónimo para testing
-- ADVERTENCIA: Deshabilitar en producción
CREATE POLICY "Anon puede acceder leads (solo desarrollo)"
  ON leads
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);


-- ===========================
-- QUOTATIONS TABLE
-- ===========================

-- Verificar si RLS está habilitado
DO $$
BEGIN
  ALTER TABLE quotations ENABLE ROW LEVEL SECURITY;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'RLS ya habilitado en quotations o error: %', SQLERRM;
END $$;

-- Política: Permitir todas las operaciones al service_role
CREATE POLICY "Service role tiene acceso completo a quotations"
  ON quotations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Política: Permitir todas las operaciones al usuario anónimo para testing
CREATE POLICY "Anon puede acceder quotations (solo desarrollo)"
  ON quotations
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);


-- ===========================
-- MEETINGS TABLE
-- ===========================

-- Verificar si RLS está habilitado
DO $$
BEGIN
  ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'RLS ya habilitado en meetings o error: %', SQLERRM;
END $$;

-- Política: Permitir todas las operaciones al service_role
CREATE POLICY "Service role tiene acceso completo a meetings"
  ON meetings
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Política: Permitir todas las operaciones al usuario anónimo para testing
CREATE POLICY "Anon puede acceder meetings (solo desarrollo)"
  ON meetings
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);


-- ===========================
-- COMENTARIOS Y LOGS
-- ===========================

COMMENT ON POLICY "Service role tiene acceso completo a conversations" ON conversations IS 
  'Permite al service_role del backend realizar todas las operaciones sin restricciones';

COMMENT ON POLICY "Anon puede acceder conversations (solo desarrollo)" ON conversations IS 
  'ADVERTENCIA: Solo para desarrollo/testing. Eliminar en producción.';

-- Log de migración exitosa
DO $$
BEGIN
  RAISE NOTICE '✅ Migración completada: Políticas RLS configuradas para conversations, agent_logs, leads, quotations, meetings';
  RAISE NOTICE '⚠️  ADVERTENCIA: Las políticas anon deben ser eliminadas en producción';
  RAISE NOTICE '📝 Recomendación: Usar SUPABASE_SERVICE_ROLE_KEY en el backend, no SUPABASE_ANON_KEY';
END $$;
