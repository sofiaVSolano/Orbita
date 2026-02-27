# 🤖 GUÍA COMPLETA — Testing de Bots Telegram en ORBITA

**Fecha:** 27 de febrero de 2026  
**Bots activos:** 2 (Leads + Admin)  
**Status:** ✅ Listos para testing

---

## 📱 ACCESO A LOS BOTS

### Bot de Leads (Público - Para Prospectos)

```
Nombre:  OrbitaBot
Usuario: @OrbitaOficialBot
Link:    https://t.me/OrbitaOficialBot
Función: Captura leads públicos, interacción con prospects
```

**Pasos para usar:**
1. Abre Telegram en tu celular o web
2. Busca: `@OrbitaOficialBot`
3. Toca "Start" o escribe `/start`
4. Envía un mensaje de prueba

---

### Bot Admin (Privado - Para Equipo)

```
Nombre:  ORBITA
Usuario: @Orbita_hack_bot
Link:    https://t.me/Orbita_hack_bot
Función: Control administrativo, análisis, métricas
```

**Pasos para usar:**
1. Abre Telegram en tu celular o web
2. Busca: `@Orbita_hack_bot`
3. Toca "Start" o escribe `/start`
4. Envía un comando admin

**⚠️ Nota:** Este bot solo responde a chat IDs específicos (configurar en `.env`)

---

## 🧪 CASOS DE PRUEBA

### Test 1: Lead Capture (Bot Leads)

**Objetivo:** Verificar que el bot captura leads correctamente

```
1. Envía al bot:
   "Hola, me interesa contratar desarrollo de software"

2. Respuesta esperada:
   ✅ Bot responde con introducción de ORBITA
   ✅ Pide información de contacto
   ✅ Solicita detalles del proyecto

3. Verifica en BD:
   docker exec orbita-backend python3 << 'EOF'
   from database import get_db
   db = get_db()
   result = db.table('leads').select('*').order('created_at', desc=True).limit(1).execute()
   print(result.data)
   EOF
```

---

### Test 2: Conversación Multi-turno

**Objetivo:** Verificar que mantiene contexto de conversación

```
1. Envía secuencialmente:
   Usuario: "Hola"
   Usuario: "Quiero una cotización"
   Usuario: "Es para mi empresa XYZ"
   Usuario: "Presupuesto: $10,000"

2. Verificaciones:
   ✅ Cada mensaje genera una respuesta
   ✅ El bot mantiene contexto (sabe que es sobre cotización)
   ✅ Los mensajes se guardan en conversations table

3. Ver conversación en BD:
   docker exec orbita-backend python3 << 'EOF'
   from database import get_db
   db = get_db()
   # El conversation_id debería ser el session_id
   result = db.table('conversations').select('*').limit(1).execute()
   print(result.data)
   EOF
```

---

### Test 3: Transcripción de Voz

**Objetivo:** Verificar que entiende mensajes de voz

```
1. Envía un mensaje de voz diciendo:
   "Necesito desarrollo de una aplicación móvil"

2. Respuesta esperada:
   ✅ Bot transcribe el audio usando Groq Whisper
   ✅ Responde como si fuera texto
   ✅ Se guarda la transcripción

3. Ver logs:
   docker logs orbita-backend -f
   # Buscar línea con "Transcripción completada" o similar
```

---

### Test 4: Routing a Agentes

**Objetivo:** Verificar que el bot delega a agentes especializados

```
1. Envía diferentes tipos de consultas:

   a) "Cuéntame quién es ORBITA"
      → Debe ir al agente de Identidad
   
   b) "¿Cuál es el precio de..."
      → Debe ir al agente Captador (lead capture)
   
   c) "Necesito ayuda"
      → Debe ir al agente Conversacional
   
   d) "Muéstrame mis métricas"
      → Debe ir al agente Analítico

2. Verifica routing en logs:
   docker logs orbita-backend -f | grep "routing\|agent\|delegating"
```

---

### Test 5: Admin Bot Commands

**Objetivo:** Verificar comandos administrativos

```
Envía al @Orbita_hack_bot:

1. Comando help:
   /help
   Respuesta esperada: Lista de comandos disponibles

2. Ver leads:
   /leads
   Respuesta esperada: Estadísticas de leads

3. Ver agentes:
   /agents status
   Respuesta esperada: Estado de todos los agentes

4. Pausar bot:
   /pause [telegram_chat_id]
   Respuesta esperada: Bot lead pausado

5. Reanudar bot:
   /resume [telegram_chat_id]
   Respuesta esperada: Bot lead reanudado lineItem
```

---

## 📊 MONITOREO EN TIEMPO REAL

### Ver Logs del Backend

**Terminal 1: Logs de todos los eventos**
```bash
docker logs orbita-backend -f
```

**Salida esperada:**
```
INFO:     127.0.0.1:45436 - "POST /api/v1/telegram/leads/webhook HTTP/1.1" 200 OK
🔔 Mensaje recibido de Telegram (leads bot)
   Chat ID: 12345678
   Usuario: TestUser
   Mensaje: "Hola, necesito una cotización"
🤖 Delegando al agente: orchestrator
⏱️ Latencia: 1250ms
✅ Respuesta enviada exitosamente
```

---

### Ver Cambios en Base de Datos en Tiempo Real

**Terminal 2: Monitor de BD**
```bash
watch -n 2 'docker exec orbita-backend python3 << "EOF"
from database import get_db
db = get_db()
print("=" * 60)
print("📊 ESTADO EN TIEMPO REAL")
print("=" * 60)
leads = db.table("leads").select("id", count="exact").execute()
conversations = db.table("conversations").select("id", count="exact").execute()
logs = db.table("agent_logs").select("id", count="exact").execute()
print(f"👥 Leads: {leads.count}")
print(f"💬 Conversations: {conversations.count}")
print(f"📝 Agent Logs: {logs.count}")
EOF'
```

**Salida esperada:**
```
============================================================
📊 ESTADO EN TIEMPO REAL
============================================================
👥 Leads: 1
💬 Conversations: 1
📝 Agent Logs: 3
```

---

### Ver Historial Completo de Conversación

```bash
docker exec orbita-backend python3 << 'EOF'
from database import get_db
import json

db = get_db()

# Obtener la conversación más reciente
result = db.table('conversations') \
    .select('*') \
    .order('created_at', desc=True) \
    .limit(1) \
    .execute()

if result.data:
    conv = result.data[0]
    print("=" * 70)
    print(f"📝 CONVERSACIÓN {conv['id']}")
    print("=" * 70)
    print(f"Lead: {conv['lead_id']}")
    print(f"Session: {conv['session_id']}")
    print(f"Estado: {conv['estado']}")
    print(f"\nHistorial:")
    
    if conv['historial']:
        historial = conv['historial']
        for i, msg in enumerate(historial, 1):
            print(f"\n  {i}. {msg['role'].upper()}")
            print(f"     {msg['content'][:100]}...")
else:
    print("No hay conversaciones aún")
EOF
```

---

## 🔍 VALIDACIÓN DETALLADA

### Verificar que un Lead se Creó Correctamente

```bash
docker exec orbita-backend python3 << 'EOF'
from database import get_db

db = get_db()

# Último lead creado
leads = db.table('leads') \
    .select('*') \
    .order('created_at', desc=True) \
    .limit(1) \
    .execute()

if leads.data:
    lead = leads.data[0]
    print("=" * 70)
    print("✅ LEAD CREADO")
    print("=" * 70)
    print(f"ID:          {lead['id']}")
    print(f"Nombre:      {lead['nombre']}")
    print(f"Email:       {lead['email']}")
    print(f"Empresa:     {lead['empresa']}")
    print(f"Status:      {lead['status']}")
    print(f"Origen:      {lead['origen']}")
    print(f"Score:       {lead['qualification_score']}")
    print(f"Creado:      {lead['created_at']}")
    
    # Obtener conversación asociada
    conv = db.table('conversations') \
        .select('*') \
        .eq('lead_id', lead['id']) \
        .execute()
    
    if conv.data:
        print(f"\nConversación asociada: {len(conv.data[0]['historial'])} mensajes")
        for msg in conv.data[0]['historial']:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
else:
    print("❌ No hay leads")
EOF
```

---

### Ver Ejecución de Agentes

```bash
docker exec orbita-backend python3 << 'EOF'
from database import get_db

db = get_db()

# Últimos logs de agentes
logs = db.table('agent_logs') \
    .select('*') \
    .order('timestamp', desc=True) \
    .limit(10) \
    .execute()

print("=" * 70)
print("📝 ÚLTIMAS EJECUCIONES DE AGENTES")
print("=" * 70)

for log in logs.data:
    status = "✅" if log['success'] else "❌"
    print(f"\n{status} {log['agent_name'].upper()} - {log['action']}")
    print(f"   Timestamp: {log['timestamp']}")
    print(f"   Duración: {log['duration_ms']}ms")
    if log['error_message']:
        print(f"   Error: {log['error_message']}")
    if log['details']:
        import json
        print(f"   Detalles: {json.dumps(log['details'], indent=2)[:200]}...")
EOF
```

---

## 🐛 TROUBLESHOOTING

### El bot no responde

**Problema:** Envío un mensaje pero el bot no contesta

**Soluciones:**

```bash
# 1. Verificar que el webhook está configurado
curl -s http://localhost:8000/health | python3 -m json.tool | grep -A20 telegram_bots

# 2. Ver si hay errores en los logs
docker logs orbita-backend --tail=50 | grep -i "error\|webhook\|telegram"

# 3. Verificar que el token de Telegram es válido
docker exec orbita-backend python3 << 'EOF'
import os
from config import TELEGRAM_LEADS_BOT_TOKEN, TELEGRAM_ADMIN_BOT_TOKEN
print(f"Leads token: {TELEGRAM_LEADS_BOT_TOKEN[:20]}...")
print(f"Admin token: {TELEGRAM_ADMIN_BOT_TOKEN[:20]}...")
EOF

# 4. Reiniciar los bots
docker restart orbita-backend
```

---

### El lead no se guarda en la BD

**Problema:** El bot responde pero no aparece el lead en Supabase

**Soluciones:**

```bash
# 1. Verificar conexión a Supabase
docker exec orbita-backend python validate_database.py

# 2. Ver si hay errores en la inserción
docker logs orbita-backend -f | grep -i "insert\|create\|lead"

# 3. Verificar que la tabla exists y está accesible
docker exec orbita-backend python3 << 'EOF'
from database import get_db
db = get_db()
result = db.table('leads').select('*', count='exact').limit(1).execute()
print(f"Total leads: {result.count}")
EOF

# 4. Revisar credenciales de Supabase
docker exec orbita-backend grep SUPABASE /app/.env
```

---

### Los logs de agentes no aparecen

**Problema:** El bot funciona pero no hay registros en agent_logs

**Soluciones:**

```bash
# 1. Verificar que agent_logs tabla existe
docker exec orbita-backend python validate_database.py | grep agent_logs

# 2. Ver si hay errores en logging
docker logs orbita-backend -f | grep -i "log_agent_action\|agent_logs"

# 3. Forzar un log manual
docker exec orbita-backend python3 << 'EOF'
from database import get_db, log_agent_action
db = get_db()

# Crear un log de prueba
log_agent_action(
    agent_name="test_agent",
    action="test_action",
    details={"test": "data"},
    success=True
)

print("✅ Log de prueba creado")
EOF
```

---

## 📈 FLUJO COMPLETE DE UN MENSAJE

### Step-by-Step de lo que sucede

```
1. 👤 USUARIO ENVÍA MENSAJE
   └─ Escribes en Telegram: "Hola, quiero una cotización"

2. 📱 TELEGRAM ENVÍA WEBHOOK
   └─ POST /api/v1/telegram/leads/webhook
   └─ Body: { chat_id, user_id, message_text, ... }

3. 🛡️ VALIDACIÓN
   └─ Verificar token secreto
   └─ Verificar que chat_id no está pausado
   └─ Extraer datos del mensaje

4. 💾 GUARDAR SESIÓN
   └─ Crear/actualizar row en telegram_bot_sessions
   └─ Estado: "activo"

5. 🤖 PROCESAR CON AGENTES
   ├─ Orchestrator: ¿A qué agente delego?
   ├─ Captador: Es una consulta sobre presupuesto
   └─ Conversacional: Generar respuesta natural

6. 📝 GUARDAR EN BD
   ├─ CREATE lead (nombre, email, empresa, etc)
   ├─ CREATE conversation (session_id, historial)
   ├─ CREATE agent_logs (quién procesó, latencia, éxito)
   └─ UPDATE lead (status = "contactado")

7. 🔄 ENVIAR RESPUESTA
   └─ POST /api/v1/telegram/sendMessage
   └─ Reply: "Gracias por tu interés..."

8. ✅ VERIFICACION
   └─ Marca como enviado ✓
   └─ Guarda timestamp
   └─ Actualiza métricas
```

---

## 📊 DASHBOARD DE MONITOREO

**Script all-in-one para monitorear todo:**

```bash
#!/bin/bash
# guardar como: monitor_telegram.sh
# ejecutar: chmod +x monitor_telegram.sh && ./monitor_telegram.sh

while true; do
  clear
  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║           🤖 ORBITA TELEGRAM MONITORING                   ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  echo ""
  
  echo "📊 ESTADÍSTICAS:"
  docker exec orbita-backend python3 << 'EOF'
from database import get_db
db = get_db()
leads = db.table('leads').select('id', count='exact').execute()
conversations = db.table('conversations').select('id', count='exact').execute()
sessions = db.table('telegram_bot_sessions').select('id', count='exact').execute()
logs = db.table('agent_logs').select('id', count='exact').execute()

print(f"  👥 Leads: {leads.count}")
print(f"  💬 Conversations: {conversations.count}")
print(f"  🔄 Bot Sessions: {sessions.count}")
print(f"  📝 Agent Logs: {logs.count}")
EOF
  
  echo ""
  echo "🔴 ÚLTIMOS EVENTOS:"
  docker logs orbita-backend --tail=5 2>/dev/null | grep -E "Mensaje recibido|respuesta|error" | tail -3
  
  echo ""
  echo "⏱️ LATENCIA (últimamente):"
  docker logs orbita-backend --tail=20 2>/dev/null | grep "Latencia" | tail -1
  
  echo ""
  echo "Actualizando en 5 segundos... (Ctrl+C para salir)"
  sleep 5
done
```

---

## ✅ CHECKLIST DE VALIDACIÓN

Después de cada prueba, verifica:

```
[ ] Lead aparece en tabla leads
[ ] Email del lead está completo y válido
[ ] Conversation se crea con historial
[ ] Cada mensaje está guardado en agent_logs
[ ] Status del lead cambia (nuevo → contactado)
[ ] Timestamps están correctos
[ ] Agentes correctos fueron invocados
[ ] No hay errores en los logs
[ ] Response time es < 3 segundos
[ ] El bot responde en español (si aplica)
```

---

## 🎯 RESULTADO EXITOSO

Cuando todo funciona correctamente, deberías ver:

```
✅ Envías mensaje a Telegram
✅ Bot responde en 1-3 segundos
✅ Aparece nuevo lead en Supabase
✅ Conversation con historial completo
✅ Agent logs muestran qué agentes intervinieron
✅ Status del lead cambió de "nuevo" a "contactado"
✅ No hay errores en los logs del backend
```

---

**Sigue esta guía paso a paso y tu sistema Telegram estará 100% validado.** 🚀
