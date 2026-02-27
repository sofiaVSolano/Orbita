#!/usr/bin/env python3
"""
Aplica la migración de Telegram a la tabla leads
"""

from database import get_db
from config import get_settings

def main():
    settings = get_settings()
    db = get_db()
    
    print("\n" + "="*70)
    print("  APLICANDO MIGRACIÓN: Agregar columnas Telegram a leads")
    print("="*70 + "\n")
    
    migration_sql = """
    -- Agregar columnas de Telegram a la tabla leads
    ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS telegram_username TEXT;
    
    -- Índice para búsquedas rápidas por telegram_chat_id
    CREATE INDEX IF NOT EXISTS idx_leads_telegram_chat_id ON leads(telegram_chat_id);
    
    -- Modificar la restricción UNIQUE de email para permitir NULL
    ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_email_key;
    ALTER TABLE leads ADD CONSTRAINT leads_email_key UNIQUE NULLS NOT DISTINCT (email);
    
    -- Modificar columna email para permitir NULL
    ALTER TABLE leads ALTER COLUMN email DROP NOT NULL;
    
    -- Modificar columna interes para permitir NULL
    ALTER TABLE leads ALTER COLUMN interes DROP NOT NULL;
    """
    
    try:
        # Ejecutar usando la API REST de Supabase con query directo
        print("⚙️  Ejecutando migración SQL...")
        
        # Como Supabase REST API no permite ALTER TABLE directamente,
        # necesitamos hacerlo desde el dashboard SQL editor o usando psycopg2
        print("\n⚠️  NOTA: Esta migración debe ejecutarse manualmente.")
        print("    Ve a tu Supabase Dashboard > SQL Editor y ejecuta:\n")
        print("-" * 70)
        print(migration_sql)
        print("-" * 70)
        
        print("\n📝 Alternativa: Copia este SQL al archivo:")
        print("   supabase/migrations/1772209200_add_telegram_to_leads.sql")
        print("   Y ejecuta desde el dashboard de Supabase\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False
    
    return True

if __name__ == "__main__":
    main()
