# 🎯 GUÍA: Validar Agentes ORBITA con Groq

## 📋 Introducción

Este documento describe cómo validar que todos los agentes del sistema ORBITA funcionan correctamente con Groq, generan respuestas coherentes, y registran todo en `agent_logs`.

**Tiempo estimado:** 5-10 minutos

---

## ✅ Requisitos Previos

Antes de validar agentes, asegúrate que:

```bash
✓ .env está completo con GROQ_API_KEY
✓ Supabase está accesible (SUPABASE_URL, SUPABASE_KEY)
✓ BD tiene tablas: agent_logs, conversations, leads
✓ pip install groq supabase tenacity
```

---

## 🚀 DOS OPCIONES DE VALIDACIÓN

### OPCIÓN 1: Validación Rápida ⚡ (Recomendado para desarrollo)

**Archivo:** `validate_agents_quick.py`

**Ventajas:**
- ✅ Sin async (más simple)
- ✅ Síncrono y directo
- ✅ Perfecto para CI/CD
- ✅ Menos overhead

**Ejecutar:**

```bash
cd orbita_backend
python validate_agents_quick.py
```

**Salida esperada:**

```
======================================================================
  VALIDADOR DE AGENTES ORBITA CON GROQ
======================================================================

🔧 Configuración:
  ✅ Groq API Key: gsk_XXXXXXXXX...
  ✅ Supabase URL: https://xiblghevwgzuhytcqpyg.supabase.co

TEST 1: ORQUESTADOR 🤖
----------------------------------------------------------------------

💬 Mensaje: 'Hola, estoy aquí para que me cuentes sobre los servicios...'
  ✅ Intención: saludo
  ✅ Etapa AIDA: awareness
  ✅ Latencia: 1234ms

...

======================================================================
REPORTE FINAL
======================================================================

✅ Agentes validados: 6/6

✅ ORCHESTRATOR
✅ CAPTADOR
✅ IDENTIDAD
✅ CONVERSACIONAL
✅ COMUNICACION
✅ ANALITICO

✨ VALIDACIÓN EXITOSA
```

---

### OPCIÓN 2: Validación Completa 🔬 (Producción)

**Archivo:** `validate_agents_groq.py`

**Ventajas:**
- ✅ Async (mejor performance)
- ✅ Múltiples casos de prueba por agente
- ✅ Reporte JSON estructurado
- ✅ Métricas completas

**Ejecutar:**

```bash
cd orbita_backend
python validate_agents_groq.py
```

**Salida:**

- Consola con reporte detallado
- Archivo `validate_results.json` con todos los datos

**Estructura del JSON:**

```json
{
  "timestamp": "2026-02-27T10:30:45.123Z",
  "agentes": {
    "orchestrator": {
      "success": true,
      "casos": 3,
      "casos_exitosos": 3,
      "results": [
        {
          "caso": 1,
          "mensaje": "...",
          "success": true,
          "latencia_ms": 1234,
          "intencion": "saludo"
        }
      ]
    },
    "captador": { ... },
    "identidad": { ... },
    "conversacional": { ... },
    "comunicacion": { ... },
    "analitico": { ... }
  }
}
```

---

## 🧪 QUÉ VALIDA CADA TEST

### TEST 1: ORQUESTADOR 🤖

**Responsabilidad:** ¿Clasifica bien la intención del mensaje?

**Casos de prueba:**
- Saludo: "Hola, estoy aquí para que me cuentes..."
- Cotización: "¿Cuánto cuesta un chatbot?"
- Agendar: "Quiero agendar una llamada"

**Validaciones:**
- ✅ Campo `intencion` coincide con esperado
- ✅ Campo `etapa_aida` es correcto
- ✅ Latencia < 3000ms
- ✅ Logs guardados en agent_logs

**Modelo:** `llama-3.3-70b-versatile`  
**Temperatura:** 0.3 (determinista)

---

### TEST 2: CAPTADOR 👤

**Responsabilidad:** ¿Extrae datos del lead correctamente?

**Casos de prueba:**
- "Hola soy Carlos Pérez de Innovatech, soy el CEO"
- "Me llamo Sofia, trabajo en marketing en XYZ Corp"

**Validaciones:**
- ✅ Crea o actualiza lead en BD
- ✅ Extrae nombre, empresa, puesto
- ✅ Devuelve `lead_id` válido
- ✅ Latencia < 3000ms

**Modelo:** `gemma2-9b-it`  
**Temperatura:** 0.2 (extractivo, preciso)

---

### TEST 3: IDENTIDAD 🎭

**Responsabilidad:** ¿Valida que el tono sea consistente con la marca?

**Casos de prueba:**
- "Hola Carlos, me da mucho gusto ayudarte" (✅ Profesional-cercano)
- "boludo, nuestro producto es lo mejor" (❌ Inapropiado)

**Validaciones:**
- ✅ `aprobado` coincide con esperado
- ✅ `score_marca` es coherente (0-10)
- ✅ Genera `mensaje_final` si necesita mejoras
- ✅ Latencia < 3000ms

**Modelo:** `llama-3.1-8b-instant`  
**Temperatura:** 0.2 (evaluación, no creativo)

---

### TEST 4: CONVERSACIONAL 💬

**Responsabilidad:** ¿Genera respuestas contextuales y naturales?

**Casos de prueba:**
- "Me interesa automatizar mis ventas"
- "¿Tienen referencias de clientes?"

**Validaciones:**
- ✅ Retorna `respuesta_final` > 50 caracteres
- ✅ Respuesta es relevante al mensaje
- ✅ Usa contexto del lead
- ✅ Latencia < 5000ms

**Modelo:** `mixtral-8x7b-32768`  
**Temperatura:** 0.7 (creativo, conversacional)

---

### TEST 5: COMUNICACIÓN ✉️

**Responsabilidad:** ¿Personaliza mensajes según contexto?

**Casos de prueba:**
- Propuesta: "Te ofrecemos un servicio..."
- Urgencia: "Esta oferta vence en 3 días"

**Validaciones:**
- ✅ Retorna `mensaje_personalizado` > 30 caracteres
- ✅ Respeta el estilo solicitado
- ✅ Personaliza con datos del lead
- ✅ Latencia < 3000ms

**Modelo:** `llama-3.1-70b-versatile`  
**Temperatura:** 0.6 (equilibrio creativo/consistencia)

---

### TEST 6: ANALÍTICO 📊

**Responsabilidad:** ¿Genera análisis y alertas?

**Casos de prueba:**
- Análisis diario del CRM

**Validaciones:**
- ✅ Retorna `score_salud_crm` (0-100)
- ✅ Array `alertas` con problemas detectados
- ✅ Genera `resumen_ejecutivo`
- ✅ Latencia < 5000ms

**Modelo:** `llama-3.3-70b-versatile`  
**Temperatura:** 0.3 (analítico, sin creatividad)

---

## 📊 INTERPRETAR RESULTADOS

### ✅ ÉXITO

```
✨ VALIDACIÓN EXITOSA

✅ ORCHESTRATOR
✅ CAPTADOR
✅ IDENTIDAD
✅ CONVERSACIONAL
✅ COMUNICACION
✅ ANALITICO

Agentes validados: 6/6
```

**Significado:**
- ✓ Todos los agentes responden a Groq
- ✓ Las respuestas son coherentes
- ✓ Los logs se guardan correctamente

**Próximo paso:** Integrar en Telegram

---

### ⚠️ PARCIAL (Algunos agentes fallan)

```
Agentes validados: 4/6

✅ ORCHESTRATOR
✅ CAPTADOR
❌ IDENTIDAD   ← Verifica error
✅ CONVERSACIONAL
❌ COMUNICACION ← Verifica error
✅ ANALITICO
```

**Qué revisar:**
1. ¿El error está en el agente o en Groq?
   ```bash
   grep "IDENTIDAD\|COMUNICACION" validate_results.json
   ```

2. ¿La API key tiene acceso a todos los modelos?
   ```bash
   # En consola.groq.com, verifica:
   - Modelo disponible
   - Plan actual (free vs pro)
   - Rate limits
   ```

3. ¿Los datos de entrada son válidos?
   ```python
   # Revisa el JSON en validate_results.json
   # ¿Faltan campos required?
   ```

---

### ❌ FALLO

```
Agentes validados: 0/6

❌ ORCHESTRATOR
❌ CAPTADOR
❌ IDENTIDAD
❌ CONVERSACIONAL
❌ COMUNICACION
❌ ANALITICO
```

**Causas probables:**

1. **GROQ_API_KEY inválida o ausente:**
   ```bash
   grep GROQ_API_KEY orbita_backend/.env
   # Debe ser: GROQ_API_KEY=gsk_XXXXXXX...
   ```

2. **Supabase no accesible:**
   ```bash
   # Verifica credenciales
   python -c "from database import get_db; db = get_db(); print('✓ Conectado')"
   ```

3. **Tablas no existen:**
   ```bash
   # En Supabase SQL Editor, ejecuta:
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   # Debe incluir: agent_logs, conversations, leads
   ```

4. **Imports incompletos:**
   ```bash
   pip install -r requirements.txt
   # Verficicar que groq está instalado
   ```

---

## 🔍 DEBUGGING INDIVIDUAL

Si fallan algunos agentes, prueba cada uno aislado:

```python
# test_single_agent.py
from database import get_db
from config import get_settings
from agents.orchestrator import OrchestratorAgent

db = get_db()
settings = get_settings()
orch = OrchestratorAgent(db, settings)

resultado = orch.execute({
    "mensaje": "Hola, ¿cómo estás?",
    "lead_id": None,
    "session_id": "test-001",
    "telegram_chat_id": "999"
})

print(resultado)
```

Ejecuta:
```bash
python test_single_agent.py
```

---

## 📈 MONITOREAR EN TIEMPO REAL

### Ver agent_logs en Supabase

1. Abre: https://app.supabase.com
2. Proyecto: xiblghevwgzuhytcqpyg
3. Tabla: `agent_logs`
4. Filtrar por `created_at` > ahora - 10 minutos

Deberías ver:
```
| agente     | accion              | exitoso | modelo               | duracion_ms |
|------------|---------------------|---------|----------------------|-------------|
| orchestrator | clasificar_intencion | true | llama-3.3-70b-versatile | 1234   |
| captador | crear_lead          | true | gemma2-9b-it | 2100   |
| identidad | validar_tono        | true | llama-3.1-8b-instant | 1890   |
```

---

## 🔄 VALIDACIÓN AUTOMÁTICA (CI/CD)

Para integrar en pipeline:

```bash
#!/bin/bash
# validate.sh

cd orbita_backend
python validate_agents_quick.py

if [ $? -eq 0 ]; then
    echo "✅ Validación exitosa"
    exit 0
else
    echo "❌ Validación falló"
    exit 1
fi
```

Usar en GitHub Actions / GitLab CI:

```yaml
# .github/workflows/validate.yml
name: Validate Agents

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r orbita_backend/requirements.txt
      - name: Validate agents
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          cd orbita_backend
          python validate_agents_quick.py
```

---

## 📋 CHECKLIST PRE-DEMO

```
Antes de demostrar a jueces del hackathon:

□ Ejecuté: python validate_agents_quick.py
□ Resultado: ✨ VALIDACIÓN EXITOSA
□ Revisé agent_logs en Supabase
□ Vi registros de los 6 agentes
□ Duración promedio < 3000ms
□ Sin errores en logs

□ Probé end-to-end:
  □ Envié mensaje a Telegram
  □ Agentes se activaron en orden
  □ Respuesta fue coherente
  □ Logs registraron todo

□ Validé DB:
  □ agent_logs tiene 6+ registros
  □ conversations guarda mensajes
  □ leads está actualizado

✅ Sistema listo para producción
```

---

## 📞 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'groq'"

```bash
pip install groq
```

### Error: "Invalid API key"

Verifica en `.env`:
```bash
grep GROQ_API_KEY orbita_backend/.env
# Obtén nueva key en: https://console.groq.com
```

### Error: "Connection timeout Supabase"

```bash
# Verifica .env
grep SUPABASE_URL orbita_backend/.env
grep SUPABASE_KEY orbita_backend/.env

# De ser necesario, genero nueva key en Supabase:
# https://app.supabase.com → Settings → API
```

### Agente regresa respuesta vacía

Revisa `validate_results.json`:
```bash
cat validate_results.json | grep -A5 "success.*false"
```

Causa común: Input data incompleto. Verifica los campos requeridos.

---

## ✨ Éxito

Una vez ejecutado:

```bash
python validate_agents_quick.py

✨ VALIDACIÓN EXITOSA
```

**¡El sistema está listo para:**
- ✅ Producción
- ✅ Demo a jueces
- ✅ Integración con Telegram
- ✅ Escalamiento

---

**Próximo paso:** [Integración con Telegram](/docs/telegram_integration.md)
