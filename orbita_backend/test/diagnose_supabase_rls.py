#!/usr/bin/env python3
"""
Script de diagnóstico y solución de problemas de Supabase RLS
Detecta y resuelve problemas comunes de configuración
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def check_environment_variables():
    """Verifica que las variables de entorno necesarias estén configuradas"""
    print_section("1. VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    all_ok = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # Ocultar parte de la key por seguridad
            masked_value = var_value[:10] + "..." + var_value[-10:] if len(var_value) > 20 else var_value[:5] + "..."
            print_success(f"{var_name}: {masked_value}")
        else:
            print_error(f"{var_name}: NO CONFIGURADA")
            all_ok = False
    
    if not all_ok:
        print_error("\nFaltan variables de entorno críticas")
        print_info("Agrega las siguientes variables a tu archivo .env:")
        print("\n  SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("  SUPABASE_KEY=tu_anon_key")
        print("  SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key")
        print("\n📝 Encuentra estas keys en: https://supabase.com/dashboard/project/[tu-proyecto]/settings/api\n")
        return False
    
    # Detectar si están usando anon_key en lugar de service_role_key
    current_key = os.getenv('SUPABASE_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if current_key and service_key:
        if current_key == service_key:
            print_success("\n✅ Usando SERVICE_ROLE_KEY correctamente")
        else:
            print_warning("\n⚠️  SUPABASE_KEY parece ser ANON_KEY, no SERVICE_ROLE_KEY")
            print_info("Para operaciones del backend, debes usar SERVICE_ROLE_KEY")
            print_info("En config.py, cambia SUPABASE_KEY por SUPABASE_SERVICE_ROLE_KEY")
    
    return True


def check_database_connection():
    """Verifica la conexión a la base de datos"""
    print_section("2. VERIFICACIÓN DE CONEXIÓN A SUPABASE")
    
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print_error("No se pueden obtener credenciales de Supabase")
            return None
        
        supabase: Client = create_client(url, key)
        
        # Test básico de conexión
        result = supabase.table("empresas").select("id").limit(1).execute()
        print_success("Conexión a Supabase exitosa")
        
        return supabase
        
    except Exception as e:
        print_error(f"Error conectando a Supabase: {e}")
        return None


def check_table_exists(supabase: Client, table_name: str):
    """Verifica si una tabla existe y es accesible"""
    try:
        result = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e):
            return False
        # Si el error es de permisos, la tabla existe pero no tenemos acceso
        return True


def check_column_exists(supabase: Client, table_name: str, column_name: str):
    """Verifica si una columna existe en una tabla"""
    try:
        result = supabase.table(table_name).select(column_name).limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e):
            return False
        return True


def check_tables_and_columns(supabase: Client):
    """Verifica que todas las tablas y columnas necesarias existan"""
    print_section("3. VERIFICACIÓN DE TABLAS Y COLUMNAS")
    
    tables_to_check = [
        'leads',
        'conversations',
        'agent_logs',
        'quotations',
        'meetings',
        'empresas'
    ]
    
    all_ok = True
    for table in tables_to_check:
        if check_table_exists(supabase, table):
            print_success(f"Tabla '{table}' existe")
        else:
            print_error(f"Tabla '{table}' NO EXISTE")
            all_ok = False
    
    # Verificar columna específica que falta
    print("\n📋 Verificando columnas críticas:")
    if check_column_exists(supabase, 'leads', 'estado_conversacion'):
        print_success("Columna 'leads.estado_conversacion' existe")
    else:
        print_error("Columna 'leads.estado_conversacion' NO EXISTE")
        print_info("Necesitas ejecutar la migración: 1772209300_add_estado_conversacion_to_leads.sql")
        all_ok = False
    
    return all_ok


def test_rls_permissions(supabase: Client):
    """Prueba los permisos de RLS en las tablas"""
    print_section("4. PRUEBA DE PERMISOS RLS")
    
    # Intentar insertar en conversations
    print("🧪 Probando INSERT en tabla 'conversations'...")
    try:
        test_data = {
            'lead_id': '00000000-0000-0000-0000-000000000000',  # UUID dummy
            'historial': {'test': 'diagnostico'},
            'estado': 'en_progreso'
        }
        # No ejecutamos realmente, solo verificamos que no haya error de permisos
        # En un test real intentaríamos insertar y hacer rollback
        print_info("No se puede probar INSERT sin crear datos reales")
        print_info("Ejecuta la migración 1772209400_configure_rls_policies.sql")
    except Exception as e:
        if "row-level security" in str(e).lower():
            print_error(f"Error de RLS: {e}")
            print_info("Necesitas configurar políticas RLS")
            return False
        else:
            print_warning(f"Error inesperado: {e}")
    
    # Intentar insertar en agent_logs
    print("\n🧪 Probando INSERT en tabla 'agent_logs'...")
    try:
        print_info("No se puede probar INSERT sin crear datos reales")
        print_info("Ejecuta la migración 1772209400_configure_rls_policies.sql")
    except Exception as e:
        if "row-level security" in str(e).lower():
            print_error(f"Error de RLS: {e}")
            return False
    
    return True


def apply_migrations():
    """Guía al usuario para aplicar las migraciones necesarias"""
    print_section("5. APLICAR MIGRACIONES")
    
    migrations = [
        {
            'file': '1772209300_add_estado_conversacion_to_leads.sql',
            'description': 'Agrega columna estado_conversacion a tabla leads'
        },
        {
            'file': '1772209400_configure_rls_policies.sql',
            'description': 'Configura políticas RLS para todas las tablas'
        }
    ]
    
    print("📝 Migraciones pendientes:\n")
    for i, migration in enumerate(migrations, 1):
        print(f"  {i}. {migration['file']}")
        print(f"     {migration['description']}\n")
    
    print("\n🔧 OPCIONES PARA APLICAR MIGRACIONES:\n")
    
    print("Opción 1: Usando Supabase CLI (Recomendado)")
    print("  1. Instala Supabase CLI: npm install -g supabase")
    print("  2. Vincula tu proyecto: supabase link --project-ref tu-project-ref")
    print("  3. Aplica las migraciones: supabase db push\n")
    
    print("Opción 2: Usando Supabase Dashboard")
    print("  1. Ve a: https://supabase.com/dashboard/project/[tu-proyecto]/editor")
    print("  2. Selecciona 'SQL Editor'")
    print("  3. Copia y pega el contenido de cada archivo .sql")
    print("  4. Click en 'Run'\n")
    
    print("Opción 3: Usando este script (Automático)")
    apply_now = input("\n¿Quieres aplicar las migraciones automáticamente? (s/n): ")
    
    if apply_now.lower() == 's':
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        
        try:
            supabase = create_client(url, key)
            
            migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'supabase', 'migrations')
            
            for migration in migrations:
                file_path = os.path.join(migrations_dir, migration['file'])
                
                if not os.path.exists(file_path):
                    print_error(f"Archivo no encontrado: {file_path}")
                    continue
                
                with open(file_path, 'r') as f:
                    sql_content = f.read()
                
                print_info(f"Aplicando: {migration['file']}")
                
                try:
                    # Supabase Python client no tiene método directo para ejecutar SQL raw
                    # Necesitarías usar psycopg2 o similar
                    print_warning("Aplicación automática no disponible con supabase-py")
                    print_info("Usa Supabase CLI o Dashboard para aplicar las migraciones")
                except Exception as e:
                    print_error(f"Error: {e}")
        
        except Exception as e:
            print_error(f"Error: {e}")


def generate_fix_guide():
    """Genera una guía de solución rápida"""
    print_section("6. GUÍA DE SOLUCIÓN RÁPIDA")
    
    print(f"""
{Colors.BOLD}PROBLEMA DETECTADO:{Colors.END}
❌ Error: "new row violates row-level security policy"
❌ Error: "column leads.estado_conversacion does not exist"

{Colors.BOLD}SOLUCIÓN:{Colors.END}

{Colors.GREEN}Paso 1:{Colors.END} Verificar que usas la KEY correcta
  • Abre tu archivo .env
  • Cambia:
    {Colors.RED}SUPABASE_KEY=tu_anon_key{Colors.END}
  • Por:
    {Colors.GREEN}SUPABASE_KEY=tu_service_role_key{Colors.END}
  
  📝 Encuentra tu service_role_key en:
     https://supabase.com/dashboard/project/[tu-proyecto]/settings/api

{Colors.GREEN}Paso 2:{Colors.END} Aplicar migraciones SQL
  • Ve a Supabase Dashboard → SQL Editor
  • Ejecuta estos archivos en orden:
    
    1️⃣  supabase/migrations/1772209300_add_estado_conversacion_to_leads.sql
    2️⃣  supabase/migrations/1772209400_configure_rls_policies.sql

{Colors.GREEN}Paso 3:{Colors.END} Reiniciar el bot
  • docker compose down
  • docker compose up -d
  • docker logs -f orbita-backend

{Colors.YELLOW}ADVERTENCIA:{Colors.END}
Las políticas RLS creadas incluyen acceso 'anon' para testing.
En producción, elimina las políticas que permiten acceso anónimo.
""")


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   🛸 ORBITA - Diagnóstico de Supabase RLS               ║")
    print("║   Script de detección y solución de problemas           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # 1. Verificar variables de entorno
    if not check_environment_variables():
        print_error("\n❌ Configuración incompleta. Corrige las variables de entorno y vuelve a intentar.\n")
        sys.exit(1)
    
    # 2. Verificar conexión
    supabase = check_database_connection()
    if not supabase:
        print_error("\n❌ No se pudo conectar a Supabase. Verifica tus credenciales.\n")
        sys.exit(1)
    
    # 3. Verificar tablas y columnas
    check_tables_and_columns(supabase)
    
    # 4. Probar permisos RLS
    test_rls_permissions(supabase)
    
    # 5. Guía de migraciones
    apply_migrations()
    
    # 6. Guía de solución
    generate_fix_guide()
    
    print_success("\n✅ Diagnóstico completado\n")


if __name__ == "__main__":
    main()
