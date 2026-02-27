# 🤖 SOLUCIÓN: Bot no Responde — Activar Polling

El problema es que en **modo desarrollo**, los webhooks están desactivados. Los bots necesitan usar **polling** (sondeo continuo) en lugar de webhooks.

---

## ⚡ SOLUCIÓN RÁPIDA (2 min)

### Opción 1: Ejecutar Polling en una Terminal Separada (Recomendado)

**Paso 1:** Abre una nueva terminal

**Paso 2:** Ejecuta polling dentro del contenedor
```bash
docker exec -it orbita-backend python run_telegram_polling.py
```

**Salida esperada:**
```
======================================================================
🚀 INICIANDO TELEGRAM POLLING (MODO DESARROLLO)
======================================================================

📱 Inicializando Bot de Leads (@OrbitaOficialBot)...
📱 Inicializando Bot Admin (@Orbita_hack_bot)...
✅ Bots configurados correctamente

🔄 Iniciando polling (escuchando mensajes)...

======================================================================
📌 LISTO PARA RECIBIR MENSAJES
======================================================================
```

**Paso 3:** Ahora abre otra terminal y envía un mensaje de prueba:
```bash
# En Telegram busca @OrbitaOficialBot y escribe: "Hola"
```

**Paso 4:** Deberías ver en la terminal de polling:
```
📱 Mensaje recibido (Leads Bot):
   Chat ID: 123456789
   Usuario: TuNombre
   Mensaje: Hola
```

---

### Opción 2: Ejecutar en Background (Sin Terminal Separada)

```bash
# Abrir polling en background
docker exec orbita-backend python run_telegram_polling.py > /tmp/telegram_polling.log 2>&1 &

# Ver logs en tiempo real
tail -f /tmp/telegram_polling.log
```

---

## 🧪 TEST DESPUÉS DE ACTIVAR POLLING

### Test 1: Mensaje Simple (30 seg)

```
1. En Telegram: @OrbitaOficialBot
2. Escribe: "Hola"
3. Deberías recibir respuesta en 1-3 segundos

Terminal polling debe mostrar:
   📱 Mensaje recibido (Leads Bot)
   Chat ID: ...
```

### Test 2: Conversación Completa (2 min)

```
1. Escribe: "Hola, necesito una cotización de desarrollo web"
2. Espera respuesta
3. Verifica en BD:
   docker exec orbita-backend python3 << 'EOF'
   from database import get_db
   db = get_db()
   leads = db.table('leads').select('*').execute()
   print(f"✅ Total leads: {leads.count}")
   EOF
```

---

## 📊 DIFERENCIAS: Webhooks vs Polling

| Aspecto | Webhooks | Polling |
|---------|----------|---------|
| **Uso** | Producción (HTTPS público) | Desarrollo/Testing |
| **Como funciona** | Telegram envía mensaje al servidor | Servidor pregunta constantemente a Telegram |
| **Requisitos** | URL público HTTPS | Ninguno (funciona localhost) |
| **Latencia** | Inmediato (ms) | 1-5 segundos |
| **Para Testing** | ❌ No | ✅ Sí |
| **Status en ORBITA** | Desactivado en desarrollo | ✅ Activado ahora |

---

## 🔧 TROUBLESHOOTING

### Polling no inicia
```bash
# Verificar que el script existe
ls -la /Users/.../orbita_backend/run_telegram_polling.py

# Chequear que los tokens de Telegram son válidos
docker exec orbita-backend python3 << 'EOF'
from config import get_settings
s = get_settings()
print(f"Leads token: {s['telegram_leads_bot_token'][:20]}...")
print(f"Admin token: {s['telegram_admin_bot_token'][:20]}...")
EOF
```

### Polling está corriendo pero no recibe mensajes
```bash
# Verificar que estés escribiendo al bot correcto
# - Bot Leads: @OrbitaOficialBot (público)
# - Bot Admin: @Orbita_hack_bot (privado)

# Ver logs detallados
docker logs orbita-backend -f | grep -i "mensaje\|error"
```

### Mensaje recibido pero bot no responde
```bash
# Ver logs de backend API
docker logs orbita-backend --tail=50 | grep -i "error\|response"

# Verificar que DB está conectada
docker exec orbita-backend python validate_database.py
```

---

## 📝 PRÓXIMOS PASOS

Una vez que polling esté corriendo y recibas respuestas:

1. ✅ Polling está corriendo
2. ✅ Bots reciben mensajes
3. ✅ Bots envían respuestas
4. ⏳ Próximo: Implementar lógica completa de agentes (conectar handlers)

---

## 💾 AUTOMATIZAR POLLING EN DOCKER

Para que polling se inicie automáticamente, voy a crear una versión mejorada que se integre con el servidor FastAPI:

```bash
# Modificar main.py para iniciar polling automáticamente en modo desarrollo
# (requiere cambios en la arquitectura)
```

---

**Instrucción inmediata:**

```bash
# Terminal 1: Ver logs
docker logs orbita-backend -f

# Terminal 2: Iniciar polling
docker exec -it orbita-backend python run_telegram_polling.py

# Terminal 3: Enviar mensaje de prueba en Telegram
# Abre: https://t.me/OrbitaOficialBot
# Escribe: "Hola"
```

**¿Lista la respuesta? ✅ Polling está funcionando!**
