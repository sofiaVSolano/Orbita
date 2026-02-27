#!/usr/bin/env python3
"""
VALIDADOR SIMPLE DE SISTEMA ORBITA
===================================
Verifica que todas las bases de datos y tablas están creadas y accesibles.
"""

import json
from config import get_settings
from database import get_db

def test_database_connection():
    """Verifica conexión a Supabase y tablas principales"""
    print("\n" + "="*70)
    print("  VALIDADOR DE CONEXIÓN A SUPABASE")
    print("="*70 + "\n")
    
    settings = get_settings()
    print("🔧 Configuración:")
    print(f"  ✅ Supabase URL: {settings['supabase_url']}")
    print(f"  ✅ Groq API Key: {settings['groq_api_key'][:20]}...")
    print()
    
    try:
        db = get_db()
        print("📊 Verificando tablas en Supabase:")
        
        tables_to_check = [
            "leads",
            "empresas", 
            "agent_logs",
            "conversations",
            "campaigns",
            "quotations",
            "meetings",
            "telegram_bot_sessions"
        ]
        
        # Intentar query a cada tabla
        results = {}
        for table in tables_to_check:
            try:
                # Query simple: contar registros (usar columna apropiada por tabla)
                if table == 'telegram_bot_sessions':
                    # Esta tabla usa telegram_chat_id como PRIMARY KEY
                    response = db.table(table).select('telegram_chat_id', count='exact').limit(1).execute()
                else:
                    # Resto usan id como PK estándar
                    response = db.table(table).select('id', count='exact').limit(1).execute()
                results[table] = {
                    "status": "✅",
                    "count": response.count if hasattr(response, 'count') else 0,
                    "message": f"Tabla existe"
                }
                print(f"  ✅ {table:25} → OK ({response.count} registros)")
            except Exception as e:
                results[table] = {
                    "status": "❌", 
                    "error": str(e),
                    "message": "Error al acceder"
                }
                print(f"  ❌ {table:25} → ERROR: {str(e)[:50]}")
        
        print("\n" + "="*70)
        
        # Resumen
        success = sum(1 for r in results.values() if r["status"] == "✅")
        total = len(results)
        
        print(f"\n📈 RESUMEN: {success}/{total} tablas accesibles")
        
        if success == total:
            print("\n✅ ¡SISTEMA LISTO PARA PRODUCCIÓN!")
            print("   - Base de datos configurada correctamente")
            print("   - Todas las tablas creadas y accesibles")
            print("   - Próximo paso: Ejecutar validaciones de agentes")
            return True
        else:
            print(f"\n⚠️  {total - success} tabla(s) con problemas")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("   Verifica que:")
        print("   - SUPABASE_URL está correcto en .env")
        print("   - SUPABASE_KEY está correcto en .env")
        print("   - Las migraciones fueron ejecutadas")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    exit(0 if success else 1)
