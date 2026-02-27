#!/usr/bin/env python3
"""
Script para diagnosticar problema con tabla telegram_bot_sessions
"""

import os
os.environ['ENVIRONMENT'] = 'development'

from database import get_db

db = get_db()

print("=" * 70)
print("DIAGNÓSTICO DE TABLA: telegram_bot_sessions")
print("=" * 70)

# Test 1: Intentar select con count
print("\n1️⃣  Intentando SELECT con count:")
try:
    result = db.table('telegram_bot_sessions').select('id', count='exact').limit(1).execute()
    print(f"   ✅ OK - Count: {result.count}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Intentar insert para ver qué campos espera
print("\n2️⃣  Intentando INSERT con todos los campos esperados:")
try:
    result = db.table('telegram_bot_sessions').insert({
        'telegram_chat_id': 'test_12345',
        'estado_bot': 'activo',
        'lead_id': None,
        'paused_by': None,
        'paused_at': None
    }).execute()
    print(f"   ✅ OK - Insertado: {result.data}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:200]}")

# Test 3: Intentar insert MÍNIMO (solo PK)
print("\n3️⃣  Intentando INSERT solo con telegram_chat_id:")
try:
    result = db.table('telegram_bot_sessions').insert({
        'telegram_chat_id': 'test_minimal_456'
    }).execute()
    print(f"   ✅ OK - Row data type: {type(result.data)}")
    print(f"       Contenido: {result.data}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:200]}")

# Test 4: Intentar select sin columnas específicas
print("\n4️⃣  Intentando SELECT sin especificar columnas:")
try:
    result = db.table('telegram_bot_sessions').select().limit(1).execute()
    print(f"   ✅ OK - Datos: {result.data}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:200]}")

print("\n" + "=" * 70)
print("FIN DEL DIAGNÓSTICO")
print("=" * 70)
