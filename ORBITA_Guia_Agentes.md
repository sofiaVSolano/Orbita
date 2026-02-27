# ORBITA — Guía de Construcción de Agentes
## Tu rol: Arquitecta de Agentes del Sistema Multi-Agente
### Hackathon AI First 2026

---

## ANTES DE EMPEZAR — Setup del entorno

```bash
# 1. Crear carpeta y entorno virtual
mkdir orbita-backend && cd orbita-backend
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 2. Instalar dependencias de agentes
pip install groq supabase python-dotenv tenacity

# 3. Crear estructura de carpetas
mkdir -p agents utils
touch agents/__init__.py utils/__init__.py

# 4. Crear .env
cat > .env << EOF
GROQ_API_KEY=tu_key_de_console.groq.com
SUPABASE_URL=https://xiblghevwgzuhytcqpyg.supabase.co
SUPABASE_KEY=eyJhbGci...
EMPRESA_NOMBRE=Mi Empresa de Servicios
EMPRESA_SECTOR=Consultoría
EMPRESA_VOZ_MARCA=Profesional, cercana y orientada a resultados
EOF
```

---

## CONCEPTOS CLAVE ANTES DE ESCRIBIR UN SOLO AGENTE

### ¿Qué es un agente en ORBITA?
Un agente es una clase Python que:
1. Recibe un `input_data` (diccionario con contexto)
2. Construye un prompt con ese contexto
3. Llama a un LLM (Groq) con ese prompt
4. Parsea la respuesta
5. Ejecuta acciones en Supabase según la respuesta
6. Registra todo en `agent_logs`
7. Retorna un `output_data` estructurado

### El flujo de un mensaje en ORBITA
```
Lead escribe en Telegram
        ↓
   TelegramHandler
        ↓
  AgenteOrquestador      ← decide quién activa
        ↓
  AgenteCaptador         ← si es lead nuevo
        ↓
  AgenteConversacional   ← genera respuesta
        ↓
  AgenteIdentidad        ← valida el tono
        ↓
  Respuesta al lead por Telegram
```

### Lo que NUNCA debe hacer un agente
- Retornar texto hardcodeado como respuesta principal
- Hacer más de una responsabilidad (cada agente hace UNA cosa)
- Ignorar errores del LLM (siempre usar try/except)
- Bloquear el flujo si falla (siempre tener fallback)

---

## ARCHIVO 1: config.py — Configuración centralizada

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    supabase_url: str
    supabase_key: str
    empresa_nombre: str = "Mi Empresa de Servicios"
    empresa_sector: str = "Servicios"
    empresa_voz_marca: str = "Profesional y cercana"
    telegram_admin_chat_id: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## ARCHIVO 2: database.py — Cliente Supabase

```python
# database.py
from supabase import create_client, Client
from config import get_settings
from functools import lru_cache

@lru_cache()
def get_db() -> Client:
    s = get_settings()
    return create_client(s.supabase_url, s.supabase_key)
```

---

## ARCHIVO 3: utils/groq_client.py — Cliente Groq con reintentos

```python
# utils/groq_client.py
# PROPÓSITO: Un único punto de contacto con la API de Groq.
# Maneja errores de red, rate limits y reintentos automáticos.

import groq
import json
import time
import re
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings

class GroqClient:
    """
    Wrapper del cliente Groq con:
    - Reintentos automáticos (3 intentos, espera exponencial)
    - Extracción robusta de JSON de la respuesta
    - Medición de latencia y tokens
    """
    
    def __init__(self):
        settings = get_settings()
        self.client = groq.Groq(api_key=settings.groq_api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> tuple[str, int, int, int]:
        """
        Llama al LLM y retorna:
        (content, prompt_tokens, completion_tokens, duracion_ms)
        
        Uso:
            content, p_tok, c_tok, ms = groq_client.call(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":"Hola"}]
            )
        """
        start = time.monotonic()
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        duracion_ms = int((time.monotonic() - start) * 1000)
        content = response.choices[0].message.content
        p_tokens = response.usage.prompt_tokens
        c_tokens = response.usage.completion_tokens
        
        return content, p_tokens, c_tokens, duracion_ms
    
    def extract_json(self, text: str) -> dict:
        """
        Extrae JSON de la respuesta del LLM de forma robusta.
        El LLM a veces envuelve el JSON en ```json ... ```,
        esta función lo limpia y parsea.
        
        SIEMPRE usar este método cuando el agente espera JSON del LLM.
        """
        # Intentar parsear directo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Buscar JSON dentro de bloques de código markdown
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if '```' in pattern 
                                      else match.group(0))
                except json.JSONDecodeError:
                    continue
        
        # No se pudo extraer JSON — retornar dict con el texto raw
        return {"raw_response": text, "parse_error": True}


# Singleton
_groq_client = None

def get_groq_client() -> GroqClient:
    global _groq_client
    if not _groq_client:
        _groq_client = GroqClient()
    return _groq_client
```

---

## ARCHIVO 4: agents/base_agent.py — Clase base (LA MÁS IMPORTANTE)

```python
# agents/base_agent.py
# PROPÓSITO: Define la estructura común de TODOS los agentes.
# Todos los agentes heredan de esta clase y deben implementar execute().
#
# ¿Qué hace esta clase por ti?
# - Conexión a Supabase lista para usar (self.db)
# - Conexión a Groq lista para usar (self.groq)
# - Logging automático en agent_logs (llama _log() después de execute)
# - Memoria conversacional (get_history / save_message)
# - Datos de la empresa cargados (self.empresa)
#
# [CRITERIO 2] Arquitectura multi-agente estandarizada
# [CRITERIO 6] Trazabilidad completa via agent_logs

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from supabase import Client
from config import Settings
from utils.groq_client import get_groq_client

class BaseAgent(ABC):
    """
    Clase abstracta base para todos los agentes de ORBITA.
    
    Para crear un nuevo agente:
        class MiAgente(BaseAgent):
            nombre = "mi_agente"
            modelo = "llama-3.3-70b-versatile"
            
            async def execute(self, input_data: dict) -> dict:
                # Tu lógica aquí
                pass
    """
    
    # Atributos que CADA agente debe definir
    nombre: str = "base_agent"
    modelo: str = "llama-3.3-70b-versatile"
    
    def __init__(self, db: Client, settings: Settings):
        self.db = db
        self.settings = settings
        self.groq = get_groq_client()
        self.empresa = self._load_empresa_context()
    
    def _load_empresa_context(self) -> dict:
        """
        Carga el contexto de la empresa desde Supabase.
        Los agentes lo usan para personalizar sus prompts.
        """
        try:
            result = self.db.table("empresas").select("*").eq(
                "id", "00000000-0000-0000-0000-000000000001"
            ).maybe_single().execute()
            
            if result.data:
                return result.data
        except Exception:
            pass
        
        # Fallback a variables de entorno si Supabase falla
        return {
            "nombre": self.settings.empresa_nombre,
            "sector": self.settings.empresa_sector,
            "voz_de_marca": self.settings.empresa_voz_marca,
            "servicios_ofrecidos": []
        }
    
    @abstractmethod
    def execute(self, input_data: dict) -> dict:
        """
        Método principal del agente. DEBE ser implementado por cada agente.
        
        Args:
            input_data: Diccionario con todo el contexto necesario
            
        Returns:
            Diccionario con el resultado del agente
        """
        pass
    
    def _call_llm(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: list = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> tuple[str, int, int, int]:
        """
        Wrapper para llamar al LLM de forma estandarizada.
        
        Args:
            system_prompt: Instrucciones del sistema para el agente
            user_message: El mensaje actual a procesar
            conversation_history: Lista de mensajes previos [{role, content}]
            temperature: Creatividad (0=determinista, 1=creativo)
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            (content, prompt_tokens, completion_tokens, duracion_ms)
            
        CUÁNDO usar temperature baja (0.2-0.4):
            - Orquestador: necesita decisiones consistentes
            - Captador: extracción precisa de datos
            - Identidad: evaluación objetiva de tono
            
        CUÁNDO usar temperature alta (0.6-0.8):
            - Conversacional: respuestas naturales y variadas
            - Comunicación: personalización creativa de mensajes
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial de conversación si existe
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return self.groq.call(
            model=self.modelo,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def _log(
        self,
        accion: str,
        input_data: dict,
        output_data: dict,
        duracion_ms: int,
        exitoso: bool,
        lead_id: str = None,
        telegram_chat_id: str = None,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        error_mensaje: str = None
    ):
        """
        Registra la ejecución del agente en Supabase (tabla agent_logs).
        
        IMPORTANTE: Llamar SIEMPRE al final de execute(), tanto en éxito
        como en error. Esto es lo que hace que los jueces del hackathon
        puedan ver el sistema funcionando en tiempo real.
        
        No lances excepciones desde aquí — el log no debe bloquear el flujo.
        """
        try:
            # Limpiar datos sensibles antes de guardar
            safe_input = {k: v for k, v in input_data.items()
                         if k not in ("password", "token", "api_key")}
            safe_output = {k: v for k, v in output_data.items()
                          if k not in ("password", "token", "api_key")}
            
            self.db.table("agent_logs").insert({
                "agente": self.nombre,
                "accion": accion,
                "lead_id": lead_id,
                "telegram_chat_id": telegram_chat_id,
                "input_data": safe_input,
                "output_data": safe_output,
                "duracion_ms": duracion_ms,
                "exitoso": exitoso,
                "modelo_usado": self.modelo,
                "tokens_prompt": tokens_prompt,
                "tokens_completion": tokens_completion,
                "error_mensaje": error_mensaje,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as log_error:
            # Nunca dejes que el logging rompa el flujo principal
            print(f"[{self.nombre}] Error al guardar log: {log_error}")
    
    def get_history(self, session_id: str, limit: int = 12) -> list:
        """
        Obtiene el historial de conversación de Supabase.
        
        Retorna el historial en el formato que espera la API de Groq:
        [{"role": "user", "content": "..."}, 
         {"role": "assistant", "content": "..."}]
        
        CUÁNDO usar limit bajo (6):  Orquestador (solo necesita contexto reciente)
        CUÁNDO usar limit alto (15): Conversacional (necesita toda la historia)
        """
        try:
            result = self.db.table("conversations").select(
                "role, content"
            ).eq("session_id", session_id).order(
                "created_at", desc=False
            ).limit(limit).execute()
            
            return [
                {"role": r["role"], "content": r["content"]}
                for r in (result.data or [])
                if r["role"] in ("user", "assistant")  # excluir mensajes system
            ]
        except Exception as e:
            print(f"[{self.nombre}] Error al cargar historial: {e}")
            return []
    
    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        lead_id: str = None,
        agente: str = None,
        content_type: str = "text",
        telegram_message_id: str = None
    ):
        """
        Guarda un mensaje en la tabla conversations de Supabase.
        
        role: "user" para mensajes del lead, "assistant" para respuestas del agente
        agente: nombre del agente que generó la respuesta (para el dashboard)
        
        CUÁNDO llamar:
        - SIEMPRE guardar el mensaje del user ANTES de llamar al LLM
        - SIEMPRE guardar la respuesta del agente DESPUÉS de generarla
        """
        try:
            self.db.table("conversations").insert({
                "session_id": session_id,
                "lead_id": lead_id,
                "role": role,
                "content": content,
                "content_type": content_type,
                "agente": agente or self.nombre,
                "modelo_usado": self.modelo if role == "assistant" else None,
                "telegram_message_id": telegram_message_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            print(f"[{self.nombre}] Error al guardar mensaje: {e}")
    
    def get_lead(self, lead_id: str) -> dict | None:
        """Utilidad para cargar un lead desde Supabase."""
        try:
            result = self.db.table("leads").select("*").eq(
                "id", lead_id
            ).maybe_single().execute()
            return result.data
        except Exception:
            return None
    
    def update_lead(self, lead_id: str, campos: dict):
        """Utilidad para actualizar campos de un lead."""
        try:
            campos["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.db.table("leads").update(campos).eq("id", lead_id).execute()
        except Exception as e:
            print(f"[{self.nombre}] Error al actualizar lead: {e}")
```

---

## AGENTE 0: agents/orchestrator.py — El Orquestador

```python
# agents/orchestrator.py
# PROPÓSITO: Es el cerebro del sistema. Lee el mensaje del lead,
#            entiende la intención y decide qué agente activar.
#
# MODELO: llama-3.3-70b-versatile
# POR QUÉ: Necesita el modelo más capaz porque una mala clasificación
#          afecta a TODA la cadena de agentes. El 70B tiene razonamiento
#          superior para detectar intención en mensajes ambiguos.
#
# TEMPERATURA: 0.3 — necesita ser consistente, no creativo
#
# [CRITERIO 1] Aplica el framework AIDA para guiar al lead
# [CRITERIO 2] Capa de orquestación del sistema multi-agente
# [CRITERIO 3] Uso real de IA para clasificación de intención

import time
from agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    
    nombre = "orquestador"
    modelo = "llama-3.3-70b-versatile"
    
    def _build_system_prompt(self) -> str:
        """
        El system prompt es la personalidad y las reglas del agente.
        Se construye dinámicamente con el contexto de la empresa.
        """
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        servicios = self.empresa.get("servicios_ofrecidos", [])
        servicios_str = ", ".join(servicios) if servicios else "servicios diversos"
        
        return f"""
Eres ORBITA, el orquestador central de {empresa}, empresa de {sector}.
Tu única función es clasificar la intención del mensaje y decidir qué agente activar.

SERVICIOS QUE OFRECE LA EMPRESA: {servicios_str}

FRAMEWORK AIDA — ETAPAS DEL LEAD:
- ATENCIÓN: Lead acaba de llegar, no conoce bien los servicios
  → Activar CAPTADOR (para registrarlo) y luego CONVERSACIONAL
- INTERÉS: Lead quiere saber más, hace preguntas sobre los servicios
  → Activar CONVERSACIONAL
- DESEO: Lead pide precio, cotización, quiere ver costos
  → Activar CONVERSACIONAL (generará cotización) + soporte IDENTIDAD
- ACCIÓN: Lead quiere agendar reunión, demo, llamada, o ya decidió comprar
  → Activar CONVERSACIONAL (agendará reunión) + soporte IDENTIDAD

CASOS ESPECIALES:
- Si el mensaje es agresivo o queja grave → prioridad ALTA, escalar admin
- Si el mensaje es spam o bot → intención "spam", no activar agentes
- Si el mensaje no tiene relación con los servicios → intención "fuera_de_tema"

REGLA CRÍTICA: Responde ÚNICAMENTE con el JSON. Sin texto adicional antes o después.

FORMATO DE RESPUESTA (JSON estricto):
{{
  "intencion": "saludo|consulta_servicio|solicitud_precio|agendar|queja|spam|fuera_de_tema|otro",
  "etapa_aida": "atencion|interes|deseo|accion",
  "prioridad": "baja|media|alta",
  "agente_principal": "captador|conversacional|analitico",
  "necesita_captacion": true,
  "agente_soporte": "identidad|null",
  "requiere_escalacion_admin": false,
  "razon": "explicación breve de la clasificación",
  "accion_recomendada": "qué debe hacer el agente principal"
}}
"""
    
    def execute(self, input_data: dict) -> dict:
        """
        Clasifica la intención del mensaje y retorna la decisión de routing.
        
        input_data esperado:
        {
            "mensaje": str,           # El mensaje del lead
            "lead_id": str | None,    # None si es lead nuevo
            "session_id": str,        # ID de sesión para historial
            "telegram_chat_id": str,  # Para referencia en logs
            "historial": list         # Historial previo (opcional)
        }
        
        Returns:
        {
            "intencion": str,
            "etapa_aida": str,
            "prioridad": str,
            "agente_principal": str,
            "necesita_captacion": bool,
            "agente_soporte": str,
            "requiere_escalacion_admin": bool,
            "razon": str,
            "accion_recomendada": str
        }
        """
        start = time.monotonic()
        lead_id = input_data.get("lead_id")
        session_id = input_data.get("session_id", "")
        mensaje = input_data.get("mensaje", "")
        telegram_chat_id = input_data.get("telegram_chat_id")
        
        # Cargar historial reciente (solo últimos 6 mensajes para el orquestador)
        historial = input_data.get("historial") or self.get_history(session_id, limit=6)
        
        try:
            # Construir el mensaje de usuario con contexto adicional
            lead_info = ""
            if lead_id:
                lead = self.get_lead(lead_id)
                if lead:
                    lead_info = (
                        f"\nCONTEXTO DEL LEAD EXISTENTE:\n"
                        f"- Nombre: {lead.get('nombre', 'Desconocido')}\n"
                        f"- Etapa actual: {lead.get('etapa_funnel', 'atencion')}\n"
                        f"- Estado: {lead.get('estado', 'nuevo')}\n"
                        f"- Servicio de interés: {lead.get('servicio_interes', 'No definido')}"
                    )
            
            user_content = f"MENSAJE DEL LEAD: {mensaje}{lead_info}"
            
            # Llamar al LLM
            content, p_tok, c_tok, duracion_ms = self._call_llm(
                system_prompt=self._build_system_prompt(),
                user_message=user_content,
                conversation_history=historial,
                temperature=0.3,   # Baja temperatura = decisiones consistentes
                max_tokens=512     # La respuesta JSON es corta
            )
            
            # Extraer JSON de la respuesta
            resultado = self.groq.extract_json(content)
            
            # Si el JSON vino malformado, usar valores por defecto seguros
            if resultado.get("parse_error"):
                resultado = {
                    "intencion": "otro",
                    "etapa_aida": "atencion",
                    "prioridad": "media",
                    "agente_principal": "conversacional",
                    "necesita_captacion": lead_id is None,
                    "agente_soporte": "identidad",
                    "requiere_escalacion_admin": False,
                    "razon": "Clasificación por defecto (error de parsing)",
                    "accion_recomendada": "Responder de forma general"
                }
            
            # Registrar en agent_logs (SIEMPRE, incluso en éxito)
            self._log(
                accion=f"clasificar_intencion:{resultado.get('intencion','?')}",
                input_data={"mensaje": mensaje[:200], "lead_id": lead_id},
                output_data=resultado,
                duracion_ms=duracion_ms,
                exitoso=True,
                lead_id=lead_id,
                telegram_chat_id=telegram_chat_id,
                tokens_prompt=p_tok,
                tokens_completion=c_tok
            )
            
            return resultado
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            
            # Registrar el error en los logs
            self._log(
                accion="clasificar_intencion:error",
                input_data={"mensaje": mensaje[:200]},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                lead_id=lead_id,
                telegram_chat_id=telegram_chat_id,
                error_mensaje=str(e)
            )
            
            # Fallback seguro — nunca dejar al lead sin respuesta
            return {
                "intencion": "otro",
                "etapa_aida": "atencion",
                "prioridad": "media",
                "agente_principal": "conversacional",
                "necesita_captacion": lead_id is None,
                "agente_soporte": "identidad",
                "requiere_escalacion_admin": False,
                "razon": f"Error en orquestador: {str(e)[:100]}",
                "accion_recomendada": "Responder de forma general"
            }
```

---

## AGENTE 1: agents/captador.py

```python
# agents/captador.py
# PROPÓSITO: Registrar y enriquecer el perfil del lead en el CRM.
#            Es el primer agente que "toca" a un lead nuevo.
#
# MODELO: gemma2-9b-it
# POR QUÉ: Tarea de extracción estructurada de información.
#          Gemma2 sobresale en seguimiento de instrucciones específicas
#          (el "it" es instruction-tuned). Rápido y preciso en extraer
#          datos de texto conversacional.
#
# TEMPERATURA: 0.2 — extracción de datos debe ser precisa, no creativa
#
# [CRITERIO 1] Captura datos de forma conversacional natural
# [CRITERIO 2] Primera capa especializada del sistema multi-agente

import time
from datetime import datetime, timezone
from agents.base_agent import BaseAgent

class CaptadorAgent(BaseAgent):
    
    nombre = "captador"
    modelo = "gemma2-9b-it"
    
    def _build_system_prompt(self) -> str:
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        
        return f"""
Eres el Agente Captador de {empresa}. Tu función es extraer información
del mensaje del prospecto para crear o actualizar su perfil en el CRM.

DATOS A EXTRAER (solo los que mencione explícitamente — no inventes):
- nombre completo o cómo quiere que lo llamen
- email (validar formato)
- teléfono (con indicativo si lo menciona)
- nombre de su empresa o negocio
- cargo o posición
- qué servicio o solución busca
- presupuesto aproximado o rango de inversión
- urgencia o plazo que mencione

ASIGNACIÓN DE ETIQUETAS (máximo 4, solo las relevantes):
- "alta_intencion": si pide precio o quiere agendar
- "decision_maker": si menciona ser gerente, director, dueño
- "B2B": si representa una empresa
- "B2C": si es persona natural
- "precio_sensible": si menciona presupuesto limitado o pide descuento
- "urgente": si necesita solución pronto (días o semanas)
- "explorador": si solo está cotizando, comparando opciones

ASIGNACIÓN DE PRIORIDAD:
- ALTA: decision_maker + alta_intencion + urgente
- MEDIA: tiene interés claro pero sin urgencia
- BAJA: solo explorando, sin datos de contacto

REGLA: Responde ÚNICAMENTE con el JSON. Sin texto adicional.

FORMATO (JSON estricto):
{{
  "nombre_detectado": "string o null",
  "email_detectado": "string o null",
  "telefono_detectado": "string o null",
  "empresa_detectada": "string o null",
  "cargo_detectado": "string o null",
  "servicio_interes": "descripción breve de lo que busca o null",
  "presupuesto_estimado": "string descriptivo o null",
  "etiquetas": ["etiqueta1", "etiqueta2"],
  "prioridad": "baja|media|alta",
  "es_duplicado": false,
  "mensaje_bienvenida": "Saludo cálido y personalizado para este lead específico",
  "siguiente_pregunta": "Una sola pregunta para completar el perfil"
}}
"""
    
    def execute(self, input_data: dict) -> dict:
        """
        Crea o actualiza un lead en Supabase basado en el mensaje.
        
        input_data esperado:
        {
            "mensaje": str,
            "telegram_user_id": str,
            "telegram_username": str,
            "telegram_chat_id": str,
            "session_id": str,
            "nombre_telegram": str   # nombre de perfil de Telegram
        }
        
        Returns:
        {
            "lead_id": str,
            "accion": "creado|actualizado",
            "respuesta_para_lead": str,
            "datos_extraidos": dict,
            "es_duplicado": bool
        }
        """
        start = time.monotonic()
        mensaje = input_data.get("mensaje", "")
        telegram_user_id = input_data.get("telegram_user_id", "")
        telegram_chat_id = input_data.get("telegram_chat_id", "")
        session_id = input_data.get("session_id", "")
        nombre_telegram = input_data.get("nombre_telegram", "")
        
        lead_existente = None
        accion = "creado"
        
        try:
            # PASO 1: Verificar si el lead ya existe por telegram_user_id
            if telegram_user_id:
                result = self.db.table("leads").select("*").eq(
                    "telegram_user_id", telegram_user_id
                ).maybe_single().execute()
                lead_existente = result.data
            
            # PASO 2: Llamar al LLM para extraer datos del mensaje
            context = f"NOMBRE EN TELEGRAM: {nombre_telegram}\n"
            if lead_existente:
                context += (
                    f"DATOS YA REGISTRADOS:\n"
                    f"- Nombre: {lead_existente.get('nombre', 'Desconocido')}\n"
                    f"- Email: {lead_existente.get('email', 'No registrado')}\n"
                    f"- Servicio interés: {lead_existente.get('servicio_interes', 'No definido')}\n"
                    f"Actualiza solo los campos que sean mencionados en el nuevo mensaje."
                )
            
            content, p_tok, c_tok, duracion_ms = self._call_llm(
                system_prompt=self._build_system_prompt(),
                user_message=f"{context}\nMENSAJE: {mensaje}",
                temperature=0.2,
                max_tokens=768
            )
            
            datos = self.groq.extract_json(content)
            
            # PASO 3: Crear o actualizar el lead en Supabase
            if lead_existente:
                # Actualizar solo campos que el LLM extrajo (no sobrescribir con None)
                actualizaciones = {}
                if datos.get("nombre_detectado"):
                    actualizaciones["nombre"] = datos["nombre_detectado"]
                if datos.get("email_detectado"):
                    actualizaciones["email"] = datos["email_detectado"]
                if datos.get("telefono_detectado"):
                    actualizaciones["telefono"] = datos["telefono_detectado"]
                if datos.get("empresa_detectada"):
                    actualizaciones["empresa_nombre"] = datos["empresa_detectada"]
                if datos.get("cargo_detectado"):
                    actualizaciones["cargo"] = datos["cargo_detectado"]
                if datos.get("servicio_interes"):
                    actualizaciones["servicio_interes"] = datos["servicio_interes"]
                if datos.get("presupuesto_estimado"):
                    actualizaciones["presupuesto_estimado"] = datos["presupuesto_estimado"]
                if datos.get("etiquetas"):
                    # Fusionar etiquetas existentes con nuevas (sin duplicar)
                    etiquetas_actuales = lead_existente.get("etiquetas", []) or []
                    etiquetas_nuevas = datos["etiquetas"]
                    actualizaciones["etiquetas"] = list(
                        set(etiquetas_actuales + etiquetas_nuevas)
                    )
                if datos.get("prioridad") and datos["prioridad"] != lead_existente.get("prioridad"):
                    actualizaciones["prioridad"] = datos["prioridad"]
                
                actualizaciones["ultimo_contacto"] = datetime.now(timezone.utc).isoformat()
                
                if actualizaciones:
                    self.db.table("leads").update(actualizaciones).eq(
                        "id", lead_existente["id"]
                    ).execute()
                
                lead_id = lead_existente["id"]
                accion = "actualizado"
                
            else:
                # Crear nuevo lead
                nuevo_lead = {
                    "telegram_user_id": telegram_user_id,
                    "telegram_username": input_data.get("telegram_username", ""),
                    "telegram_chat_id": telegram_chat_id,
                    "nombre": datos.get("nombre_detectado") or nombre_telegram or "Lead Telegram",
                    "email": datos.get("email_detectado"),
                    "telefono": datos.get("telefono_detectado"),
                    "empresa_nombre": datos.get("empresa_detectada"),
                    "cargo": datos.get("cargo_detectado"),
                    "servicio_interes": datos.get("servicio_interes"),
                    "presupuesto_estimado": datos.get("presupuesto_estimado"),
                    "etiquetas": datos.get("etiquetas", []),
                    "prioridad": datos.get("prioridad", "media"),
                    "fuente": "telegram",
                    "estado": "nuevo",
                    "etapa_funnel": "atencion",
                    "ultimo_contacto": datetime.now(timezone.utc).isoformat()
                }
                
                result = self.db.table("leads").insert(nuevo_lead).execute()
                lead_id = result.data[0]["id"]
                
                # Actualizar la sesión del bot con el lead_id
                self.db.table("telegram_bot_sessions").update(
                    {"lead_id": lead_id}
                ).eq("telegram_chat_id", telegram_chat_id).execute()
            
            # PASO 4: Determinar la respuesta para el lead
            respuesta = datos.get("mensaje_bienvenida", "")
            if datos.get("siguiente_pregunta"):
                respuesta = f"{respuesta}\n\n{datos['siguiente_pregunta']}"
            
            if not respuesta:
                nombre = datos.get("nombre_detectado") or nombre_telegram or "hola"
                respuesta = (
                    f"¡Bienvenido/a{', ' + nombre if nombre else ''}! "
                    f"Es un gusto atenderte. ¿En qué podemos ayudarte hoy?"
                )
            
            resultado = {
                "lead_id": lead_id,
                "accion": accion,
                "respuesta_para_lead": respuesta,
                "datos_extraidos": datos,
                "es_duplicado": lead_existente is not None
            }
            
            self._log(
                accion=f"captar_lead:{accion}",
                input_data={"mensaje": mensaje[:200], "telegram_user_id": telegram_user_id},
                output_data=resultado,
                duracion_ms=duracion_ms,
                exitoso=True,
                lead_id=lead_id,
                telegram_chat_id=telegram_chat_id,
                tokens_prompt=p_tok,
                tokens_completion=c_tok
            )
            
            return resultado
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            self._log(
                accion="captar_lead:error",
                input_data={"mensaje": mensaje[:200]},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                telegram_chat_id=telegram_chat_id,
                error_mensaje=str(e)
            )
            # Fallback: crear lead mínimo con datos de Telegram
            try:
                result = self.db.table("leads").insert({
                    "telegram_user_id": telegram_user_id,
                    "telegram_chat_id": telegram_chat_id,
                    "nombre": nombre_telegram or "Lead Telegram",
                    "fuente": "telegram",
                    "estado": "nuevo",
                    "etapa_funnel": "atencion"
                }).execute()
                return {
                    "lead_id": result.data[0]["id"],
                    "accion": "creado_fallback",
                    "respuesta_para_lead": "¡Hola! ¿En qué puedo ayudarte?",
                    "datos_extraidos": {},
                    "es_duplicado": False
                }
            except Exception:
                return {
                    "lead_id": None,
                    "accion": "error",
                    "respuesta_para_lead": "¡Hola! ¿En qué puedo ayudarte?",
                    "datos_extraidos": {},
                    "es_duplicado": False
                }
```

---

## AGENTE 2: agents/conversacional.py

```python
# agents/conversacional.py
# PROPÓSITO: Atender al lead 24/7. Es el agente que más interactúa
#            con el prospecto. Genera respuestas, cotizaciones y
#            agenda reuniones.
#
# MODELO: llama-3.3-70b-versatile
# POR QUÉ: Tarea de alta complejidad — mantener contexto largo,
#          adaptar tono según etapa AIDA, generar respuestas
#          persuasivas naturales. No se puede escatimar en capacidad.
#
# TEMPERATURA: 0.7 — respuestas naturales y variadas
#
# IMPORTANTE: Este agente NO envía la respuesta directo al lead.
#             Siempre pasa por AgenteIdentidad para validación de tono.
#
# [CRITERIO 1] Memoria conversacional completa — historial de 15 mensajes
# [CRITERIO 2] Comunicación inter-agente (llama a Identidad)

import time
from datetime import datetime, timezone
from agents.base_agent import BaseAgent

class ConversacionalAgent(BaseAgent):
    
    nombre = "conversacional"
    modelo = "llama-3.3-70b-versatile"
    
    def _build_system_prompt(self) -> str:
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        voz = self.empresa.get("voz_de_marca", "Profesional y cercana")
        servicios = self.empresa.get("servicios_ofrecidos", [])
        servicios_str = "\n".join([f"- {s}" for s in servicios]) if servicios else "- Servicios diversos"
        
        return f"""
Eres el Agente Conversacional de {empresa}, empresa de {sector}.
Atiendes prospectos por Telegram 24/7 con memoria completa de la conversación.

VOZ DE LA MARCA: {voz}

SERVICIOS QUE OFRECEMOS:
{servicios_str}

COMPORTAMIENTO SEGÚN ETAPA AIDA DEL LEAD:
- ATENCIÓN: Lead nuevo. Preséntate brevemente, genera curiosidad con
  una pregunta sobre su necesidad. No abrumes con información.
- INTERÉS: Quiere saber más. Haz 1-2 preguntas para entender
  exactamente qué necesita. Muestra que entiendes su situación.
- DESEO: Está convencido de la necesidad. Muestra cómo resolvemos
  su problema específico. Ofrece generar una cotización personalizada.
- ACCIÓN: Listo para decidir. Propón fecha/hora para reunión o demo.
  Sé concreto y facilita el siguiente paso.

REGLAS DE COMUNICACIÓN (Telegram se lee en móvil):
- Máximo 3 párrafos por respuesta
- Párrafos cortos, 2-3 oraciones máximo
- Si la respuesta es larga, usa emojis para separar secciones
- UNA sola pregunta al final si necesitas más información
- Nunca mencionar competidores
- Nunca inventar precios o promesas que no puedas cumplir

CUÁNDO GENERAR COTIZACIÓN:
- El lead pregunta por precio de forma directa
- El lead tiene datos suficientes (servicio + empresa o contexto)
- El lead dice "¿cuánto cuesta?" o similar

CUÁNDO AGENDAR REUNIÓN:
- El lead acepta una cotización
- El lead pide hablar con alguien
- El lead dice "quiero agendar" o "cuándo podemos hablar"

REGLA CRÍTICA: Responde ÚNICAMENTE con el JSON. Sin texto adicional.

FORMATO (JSON estricto):
{{
  "respuesta": "mensaje para el lead",
  "accion_sugerida": "ninguna|generar_cotizacion|agendar_reunion|escalar_admin",
  "datos_cotizacion": null,
  "datos_reunion": null,
  "actualizar_etapa_a": null,
  "actualizar_prioridad_a": null,
  "notas_internas": "observaciones para el admin (no se muestran al lead)"
}}

Si accion_sugerida es "generar_cotizacion", incluir datos_cotizacion:
{{
  "plan": "nombre del plan/servicio",
  "descripcion": "descripción del plan",
  "valor_estimado": 1500000,
  "moneda": "COP",
  "items": [
    {{"nombre": "Item 1", "descripcion": "detalle", "valor": 800000}},
    {{"nombre": "Item 2", "descripcion": "detalle", "valor": 700000}}
  ],
  "vigencia_dias": 15
}}

Si accion_sugerida es "agendar_reunion", incluir datos_reunion:
{{
  "titulo": "Demo de servicios para [empresa del lead]",
  "tipo": "demo|llamada|videollamada|presencial",
  "fecha_sugerida": "próxima semana o fecha que mencionó",
  "duracion_minutos": 30
}}
"""
    
    def execute(self, input_data: dict) -> dict:
        """
        Genera la respuesta al lead y ejecuta acciones (cotización, reunión).
        
        input_data esperado:
        {
            "mensaje": str,
            "lead_id": str,
            "session_id": str,
            "etapa_actual": str,           # "atencion|interes|deseo|accion"
            "decision_orquestador": dict   # La decisión del orquestador
        }
        
        Returns:
        {
            "respuesta_final": str,     # Validada por Identidad
            "respuesta_borrador": str,  # Antes de Identidad
            "accion_realizada": str,
            "cotizacion": dict | None,
            "reunion": dict | None,
            "lead_actualizado": dict
        }
        """
        start = time.monotonic()
        mensaje = input_data.get("mensaje", "")
        lead_id = input_data.get("lead_id")
        session_id = input_data.get("session_id", "")
        etapa_actual = input_data.get("etapa_actual", "atencion")
        
        try:
            # PASO 1: Cargar historial COMPLETO (15 mensajes para Conversacional)
            historial = self.get_history(session_id, limit=15)
            
            # PASO 2: Enriquecer el mensaje con contexto del lead
            lead_context = ""
            lead_data = {}
            if lead_id:
                lead_data = self.get_lead(lead_id) or {}
                lead_context = (
                    f"\nCONTEXTO DEL LEAD:\n"
                    f"- Nombre: {lead_data.get('nombre', 'Desconocido')}\n"
                    f"- Empresa: {lead_data.get('empresa_nombre', 'No especificada')}\n"
                    f"- Cargo: {lead_data.get('cargo', 'No especificado')}\n"
                    f"- Servicio de interés: {lead_data.get('servicio_interes', 'Por definir')}\n"
                    f"- Etapa AIDA actual: {etapa_actual}\n"
                    f"- Prioridad: {lead_data.get('prioridad', 'media')}\n"
                    f"- Presupuesto: {lead_data.get('presupuesto_estimado', 'No mencionado')}"
                )
            
            # PASO 3: Llamar al LLM con historial completo
            content, p_tok, c_tok, duracion_ms = self._call_llm(
                system_prompt=self._build_system_prompt(),
                user_message=f"MENSAJE ACTUAL: {mensaje}{lead_context}",
                conversation_history=historial,
                temperature=0.7,
                max_tokens=1536
            )
            
            resultado_llm = self.groq.extract_json(content)
            
            respuesta_borrador = resultado_llm.get("respuesta", "")
            accion = resultado_llm.get("accion_sugerida", "ninguna")
            
            # PASO 4: Validar tono con Agente Identidad
            # INTER-AGENTE: Conversacional → Identidad
            from agents.identidad import IdentidadAgent
            agente_identidad = IdentidadAgent(self.db, self.settings)
            
            identidad_result = agente_identidad.execute({
                "borrador": respuesta_borrador,
                "contexto_lead": lead_data,
                "agente_origen": "conversacional",
                "etapa_aida": etapa_actual
            })
            
            respuesta_final = identidad_result.get("mensaje_final", respuesta_borrador)
            
            # PASO 5: Ejecutar acciones según la decisión del LLM
            cotizacion = None
            reunion = None
            
            if accion == "generar_cotizacion" and resultado_llm.get("datos_cotizacion"):
                cotizacion = self._crear_cotizacion(
                    lead_id, resultado_llm["datos_cotizacion"]
                )
            
            if accion == "agendar_reunion" and resultado_llm.get("datos_reunion"):
                reunion = self._crear_reunion(
                    lead_id, resultado_llm["datos_reunion"], lead_data
                )
            
            # PASO 6: Actualizar etapa y prioridad del lead si cambió
            actualizaciones = {}
            if resultado_llm.get("actualizar_etapa_a") and lead_id:
                actualizaciones["etapa_funnel"] = resultado_llm["actualizar_etapa_a"]
            if resultado_llm.get("actualizar_prioridad_a") and lead_id:
                actualizaciones["prioridad"] = resultado_llm["actualizar_prioridad_a"]
            if actualizaciones and lead_id:
                actualizaciones["ultimo_contacto"] = datetime.now(timezone.utc).isoformat()
                self.update_lead(lead_id, actualizaciones)
                lead_data.update(actualizaciones)
            
            # PASO 7: Guardar mensajes en conversations
            # El mensaje del usuario
            self.save_message(
                session_id=session_id,
                role="user",
                content=mensaje,
                lead_id=lead_id,
                agente="lead"
            )
            # La respuesta del agente (validada por Identidad)
            self.save_message(
                session_id=session_id,
                role="assistant",
                content=respuesta_final,
                lead_id=lead_id,
                agente=self.nombre
            )
            
            resultado_final = {
                "respuesta_final": respuesta_final,
                "respuesta_borrador": respuesta_borrador,
                "accion_realizada": accion,
                "cotizacion": cotizacion,
                "reunion": reunion,
                "lead_actualizado": lead_data,
                "identidad_score": identidad_result.get("score_marca", 1.0)
            }
            
            self._log(
                accion=f"responder_lead:{accion}",
                input_data={"mensaje": mensaje[:200], "etapa": etapa_actual},
                output_data={
                    "accion": accion,
                    "tiene_cotizacion": cotizacion is not None,
                    "tiene_reunion": reunion is not None
                },
                duracion_ms=duracion_ms,
                exitoso=True,
                lead_id=lead_id,
                tokens_prompt=p_tok,
                tokens_completion=c_tok
            )
            
            return resultado_final
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            self._log(
                accion="responder_lead:error",
                input_data={"mensaje": mensaje[:200]},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                lead_id=lead_id,
                error_mensaje=str(e)
            )
            return {
                "respuesta_final": "Gracias por tu mensaje. Un asesor te contactará pronto.",
                "respuesta_borrador": "",
                "accion_realizada": "error",
                "cotizacion": None,
                "reunion": None,
                "lead_actualizado": {}
            }
    
    def _crear_cotizacion(self, lead_id: str, datos: dict) -> dict | None:
        """Crea el registro de cotización en Supabase."""
        try:
            nueva_cotizacion = {
                "lead_id": lead_id,
                "plan_nombre": datos.get("plan", "Plan Personalizado"),
                "descripcion": datos.get("descripcion", ""),
                "valor": datos.get("valor_estimado", 0),
                "moneda": datos.get("moneda", "COP"),
                "vigencia_dias": datos.get("vigencia_dias", 15),
                "items": datos.get("items", []),
                "estado": "pendiente",
                "enviada_por_telegram": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            result = self.db.table("cotizaciones").insert(nueva_cotizacion).execute()
            # Actualizar estado del lead
            self.update_lead(lead_id, {"estado": "cotizado"})
            return result.data[0] if result.data else nueva_cotizacion
        except Exception as e:
            print(f"[conversacional] Error creando cotización: {e}")
            return None
    
    def _crear_reunion(self, lead_id: str, datos: dict, lead_data: dict) -> dict | None:
        """Crea el registro de reunión en Supabase."""
        try:
            titulo = datos.get("titulo") or (
                f"Reunión con {lead_data.get('nombre', 'Lead')}"
            )
            nueva_reunion = {
                "lead_id": lead_id,
                "titulo": titulo,
                "fecha_hora": datos.get("fecha_sugerida",
                              datetime.now(timezone.utc).isoformat()),
                "duracion_minutos": datos.get("duracion_minutos", 30),
                "tipo": datos.get("tipo", "demo"),
                "estado": "agendada",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            result = self.db.table("reuniones").insert(nueva_reunion).execute()
            # Actualizar estado del lead
            self.update_lead(lead_id, {"estado": "reunion_agendada"})
            return result.data[0] if result.data else nueva_reunion
        except Exception as e:
            print(f"[conversacional] Error creando reunión: {e}")
            return None
```

---

## AGENTE 3: agents/identidad.py

```python
# agents/identidad.py
# PROPÓSITO: Validar que el tono de CADA mensaje refleje la voz
#            de la marca. Es el control de calidad del sistema.
#            Es llamado por otros agentes (inter-agente).
#
# MODELO: mixtral-8x7b-32768
# POR QUÉ: Tarea cualitativa de análisis semántico fino.
#          Mixtral usa Mixture of Experts (MoE): activa distintos
#          "expertos" según la naturaleza del token. Excelente para
#          evaluación contextual. 32K tokens permite revisar mensajes
#          largos con historial sin truncar.
#
# TEMPERATURA: 0.4 — evaluación objetiva pero con flexibilidad
#
# [CRITERIO 2] Comunicación inter-agente — llamado por Conversacional
# [CRITERIO 3] IA real para análisis de tono

import time
from agents.base_agent import BaseAgent

class IdentidadAgent(BaseAgent):
    
    nombre = "identidad"
    modelo = "mixtral-8x7b-32768"
    
    def _build_system_prompt(self) -> str:
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        voz = self.empresa.get("voz_de_marca", "Profesional y cercana")
        
        return f"""
Eres el Agente de Identidad de {empresa}. Eres el guardián de la
voz de la marca. Revisas CADA mensaje antes de enviarlo al cliente.

EMPRESA: {empresa}
SECTOR: {sector}
VOZ DE LA MARCA: {voz}

CRITERIOS DE EVALUACIÓN (puntuar cada uno de 0 a 1):
1. TONO (0-1): ¿Refleja la voz de la marca? ¿Es consistente?
2. CLARIDAD (0-1): ¿Es comprensible? ¿Sin jerga innecesaria?
3. LONGITUD (0-1): ¿Es apropiada para Telegram (máx 3 párrafos)?
4. CONFIANZA (0-1): ¿No promete nada que no pueda cumplirse?
5. EMPATÍA (0-1): ¿Muestra que entiende la necesidad del lead?

SCORE FINAL = promedio de los 5 criterios

ACCIÓN SEGÚN SCORE:
- >= 0.8: Aprobar sin cambios (aprobado: true)
- 0.6-0.79: Ajustes menores (aprobado: true, mejorar algunos aspectos)
- < 0.6: Reescribir completamente (aprobado: false, nueva versión en mensaje_final)

REGLA ABSOLUTA: mensaje_final SIEMPRE debe contener el mensaje listo
para enviar. NUNCA dejes mensaje_final vacío o null.
NUNCA bloquees el flujo — si no estás seguro, aprueba con ajustes menores.

REGLA CRÍTICA: Responde ÚNICAMENTE con el JSON. Sin texto adicional.

FORMATO (JSON estricto):
{{
  "aprobado": true,
  "mensaje_final": "el mensaje validado/mejorado listo para enviar",
  "cambios_realizados": ["cambio 1 aplicado", "cambio 2 aplicado"],
  "score_tono": 0.9,
  "score_claridad": 0.8,
  "score_longitud": 1.0,
  "score_confianza": 0.9,
  "score_empatia": 0.8,
  "score_marca": 0.88,
  "razon_rechazo": null
}}
"""
    
    def execute(self, input_data: dict) -> dict:
        """
        Valida y mejora un mensaje antes de enviarlo al lead.
        
        input_data esperado:
        {
            "borrador": str,           # Mensaje a validar
            "contexto_lead": dict,     # Datos del lead (para personalización)
            "agente_origen": str,      # Quién llama a Identidad
            "etapa_aida": str          # Etapa del lead
        }
        
        Returns:
        {
            "aprobado": bool,
            "mensaje_final": str,      # SIEMPRE tiene contenido
            "cambios_realizados": list,
            "score_marca": float
        }
        """
        start = time.monotonic()
        borrador = input_data.get("borrador", "")
        agente_origen = input_data.get("agente_origen", "desconocido")
        lead_data = input_data.get("contexto_lead", {})
        etapa = input_data.get("etapa_aida", "atencion")
        
        # Si el borrador está vacío, retornar directamente
        if not borrador.strip():
            return {
                "aprobado": False,
                "mensaje_final": "Gracias por tu mensaje. ¿En qué puedo ayudarte?",
                "cambios_realizados": ["Borrador vacío — mensaje genérico aplicado"],
                "score_marca": 0.0
            }
        
        try:
            contexto = (
                f"BORRADOR A REVISAR:\n{borrador}\n\n"
                f"CONTEXTO:\n"
                f"- Agente que lo generó: {agente_origen}\n"
                f"- Etapa AIDA del lead: {etapa}\n"
                f"- Nombre del lead: {lead_data.get('nombre', 'Desconocido')}\n"
                f"- Sector del lead: {lead_data.get('empresa_nombre', 'No especificado')}"
            )
            
            content, p_tok, c_tok, duracion_ms = self._call_llm(
                system_prompt=self._build_system_prompt(),
                user_message=contexto,
                temperature=0.4,
                max_tokens=1024
            )
            
            resultado = self.groq.extract_json(content)
            
            # GARANTIZAR que siempre haya un mensaje_final
            if not resultado.get("mensaje_final"):
                resultado["mensaje_final"] = borrador
                resultado["cambios_realizados"] = resultado.get("cambios_realizados", [])
                resultado["cambios_realizados"].append("Borrador original conservado")
            
            self._log(
                accion=f"validar_tono:score={resultado.get('score_marca', 0):.2f}",
                input_data={"borrador": borrador[:200], "agente_origen": agente_origen},
                output_data={
                    "aprobado": resultado.get("aprobado"),
                    "score_marca": resultado.get("score_marca"),
                    "cambios": resultado.get("cambios_realizados", [])
                },
                duracion_ms=duracion_ms,
                exitoso=True,
                tokens_prompt=p_tok,
                tokens_completion=c_tok
            )
            
            return resultado
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            self._log(
                accion="validar_tono:error",
                input_data={"borrador": borrador[:200]},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                error_mensaje=str(e)
            )
            # Fallback: devolver el borrador original sin modificar
            return {
                "aprobado": True,
                "mensaje_final": borrador,
                "cambios_realizados": [f"Error en validación: {str(e)[:100]}"],
                "score_marca": 0.5
            }
```

---

## AGENTE 4: agents/comunicacion.py

```python
# agents/comunicacion.py
# PROPÓSITO: Enviar campañas personalizadas a segmentos de leads.
#            Procesa un lead a la vez, personalizando el mensaje
#            según su perfil e historial.
#
# MODELO: llama-3.1-8b-instant
# POR QUÉ: El sufijo "instant" indica que Groq lo optimizó para
#          velocidad máxima. Si tienes 100 leads en una campaña,
#          la velocidad importa más que la complejidad de razonamiento.
#          La tarea (personalizar un template) es moderada.
#
# TEMPERATURA: 0.6 — suficiente variedad para que no suenen iguales
#
# [CRITERIO 1] Personalización conversacional de cada mensaje
# [CRITERIO 5] Procesamiento en bucle con rate limiting

import time
import asyncio
from datetime import datetime, timezone
from agents.base_agent import BaseAgent

class ComunicacionAgent(BaseAgent):
    
    nombre = "comunicacion"
    modelo = "llama-3.1-8b-instant"
    
    def _build_system_prompt(self) -> str:
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        voz = self.empresa.get("voz_de_marca", "Profesional y cercana")
        
        return f"""
Eres el Agente de Comunicación de {empresa}, empresa de {sector}.
Personalizas mensajes de campaña para cada lead según su perfil.

VOZ DE LA MARCA: {voz}

TU TAREA:
Recibir el template base de una campaña y el perfil del lead,
y generar una versión personalizada que suene genuina, no masiva.

ESTRATEGIAS DE PERSONALIZACIÓN:
- Usar el nombre del lead en el saludo
- Mencionar su empresa si la conoces
- Referir al servicio específico que le interesa
- Adaptar el tono según su etapa AIDA
- Incluir un CTA específico y accionable

RESTRICCIONES:
- Máximo 4 párrafos (es Telegram)
- No inventar información que no esté en el perfil
- El asunto personalizado debe ser llamativo (para campañas email)

REGLA CRÍTICA: Responde ÚNICAMENTE con el JSON. Sin texto adicional.

FORMATO (JSON estricto):
{{
  "asunto_personalizado": "asunto para email (vacío si es Telegram)",
  "cuerpo_personalizado": "mensaje personalizado completo",
  "nivel_personalizacion": "bajo|medio|alto",
  "variables_usadas": ["nombre", "empresa", "servicio_interes"],
  "cta": "llamada a la acción específica incluida en el mensaje"
}}
"""
    
    def execute(self, input_data: dict) -> dict:
        """
        Procesa una campaña y personaliza mensajes para cada lead del segmento.
        
        input_data esperado:
        {
            "campana_id": str,
            "preview_mode": bool    # True = solo 3 muestras, no enviar
        }
        
        Returns:
        {
            "total_procesados": int,
            "total_exito": int,
            "total_fallidos": int,
            "preview_muestra": list | None,
            "campana_id": str
        }
        """
        start = time.monotonic()
        campana_id = input_data.get("campana_id")
        preview_mode = input_data.get("preview_mode", False)
        
        try:
            # PASO 1: Cargar la campaña
            campana_result = self.db.table("campanas").select("*").eq(
                "id", campana_id
            ).maybe_single().execute()
            
            if not campana_result.data:
                return {"error": "Campaña no encontrada", "campana_id": campana_id}
            
            campana = campana_result.data
            
            # PASO 2: Cargar leads del segmento
            query = self.db.table("leads").select("*")
            
            # Filtrar por etiquetas si se especificó segmento
            if campana.get("segmento_etiquetas"):
                for etiqueta in campana["segmento_etiquetas"]:
                    query = query.contains("etiquetas", [etiqueta])
            
            # Filtrar por etapa si se especificó
            if campana.get("segmento_etapa"):
                query = query.eq("etapa_funnel", campana["segmento_etapa"])
            
            leads_result = query.execute()
            leads = leads_result.data or []
            
            if not leads:
                return {
                    "total_procesados": 0,
                    "total_exito": 0,
                    "total_fallidos": 0,
                    "preview_muestra": [],
                    "campana_id": campana_id,
                    "mensaje": "No hay leads en el segmento"
                }
            
            # PASO 3: En preview mode, procesar solo 3 leads
            leads_a_procesar = leads[:3] if preview_mode else leads
            
            # Actualizar estado a "enviando" si no es preview
            if not preview_mode:
                self.db.table("campanas").update({
                    "estado": "enviando",
                    "total_destinatarios": len(leads)
                }).eq("id", campana_id).execute()
            
            # PASO 4: Procesar cada lead
            mensajes_generados = []
            total_exito = 0
            total_fallidos = 0
            
            for lead in leads_a_procesar:
                try:
                    # Llamar al LLM para personalizar
                    contexto = (
                        f"TEMPLATE DE CAMPAÑA:\n"
                        f"Asunto: {campana.get('asunto', '')}\n"
                        f"Cuerpo: {campana['cuerpo']}\n\n"
                        f"PERFIL DEL LEAD:\n"
                        f"- Nombre: {lead.get('nombre', 'Estimado/a')}\n"
                        f"- Empresa: {lead.get('empresa_nombre', 'No especificada')}\n"
                        f"- Cargo: {lead.get('cargo', 'No especificado')}\n"
                        f"- Servicio de interés: {lead.get('servicio_interes', 'Servicios en general')}\n"
                        f"- Etapa AIDA: {lead.get('etapa_funnel', 'atencion')}\n"
                        f"- Etiquetas: {', '.join(lead.get('etiquetas', []))}"
                    )
                    
                    content, p_tok, c_tok, dur_ms = self._call_llm(
                        system_prompt=self._build_system_prompt(),
                        user_message=contexto,
                        temperature=0.6,
                        max_tokens=768
                    )
                    
                    mensaje_personalizado = self.groq.extract_json(content)
                    mensaje_personalizado["lead_id"] = lead["id"]
                    mensaje_personalizado["lead_nombre"] = lead.get("nombre")
                    mensaje_personalizado["telegram_chat_id"] = lead.get("telegram_chat_id")
                    
                    mensajes_generados.append(mensaje_personalizado)
                    total_exito += 1
                    
                    self._log(
                        accion=f"personalizar_campaña:{campana.get('nombre', '?')}",
                        input_data={"campana_id": campana_id, "lead_id": lead["id"]},
                        output_data={"nivel": mensaje_personalizado.get("nivel_personalizacion")},
                        duracion_ms=dur_ms,
                        exitoso=True,
                        lead_id=lead["id"],
                        tokens_prompt=p_tok,
                        tokens_completion=c_tok
                    )
                    
                    # Rate limiting — Groq tiene límite de 30 req/min en tier gratuito
                    # 60s / 30 req = 2 segundos entre requests
                    if not preview_mode:
                        time.sleep(2)
                    
                except Exception as lead_error:
                    total_fallidos += 1
                    print(f"[comunicacion] Error con lead {lead.get('id')}: {lead_error}")
            
            # PASO 5: Actualizar estado final de la campaña
            if not preview_mode:
                self.db.table("campanas").update({
                    "estado": "completada",
                    "total_enviados": total_exito,
                    "total_fallidos": total_fallidos,
                    "enviado_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", campana_id).execute()
            
            total_duracion = int((time.monotonic() - start) * 1000)
            
            self._log(
                accion=f"ejecutar_campaña:{'preview' if preview_mode else 'real'}",
                input_data={"campana_id": campana_id, "total_leads": len(leads)},
                output_data={"exito": total_exito, "fallidos": total_fallidos},
                duracion_ms=total_duracion,
                exitoso=True
            )
            
            return {
                "total_procesados": len(leads_a_procesar),
                "total_exito": total_exito,
                "total_fallidos": total_fallidos,
                "preview_muestra": mensajes_generados if preview_mode else None,
                "campana_id": campana_id
            }
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            self._log(
                accion="ejecutar_campaña:error",
                input_data={"campana_id": campana_id},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                error_mensaje=str(e)
            )
            if not preview_mode:
                self.db.table("campanas").update({"estado": "error"}).eq(
                    "id", campana_id).execute()
            return {"error": str(e), "campana_id": campana_id}
```

---

## AGENTE 5: agents/analitico.py

```python
# agents/analitico.py
# PROPÓSITO: Analizar las métricas del CRM, detectar anomalías
#            y generar alertas proactivas para el admin.
#            Corre en background, no interactúa directamente con leads.
#
# MODELO: llama-3.1-8b-instant
# POR QUÉ: Los datos ya vienen estructurados desde Supabase
#          (conteos, promedios). El modelo no necesita razonar
#          desde cero, solo interpretar datos y generar texto
#          analítico. Un 8B rápido es perfecto para esto.
#
# TEMPERATURA: 0.5 — balance entre análisis objetivo y lenguaje fluido
#
# [CRITERIO 3] IA para detección de anomalías (no solo reportes)
# [CRITERIO 4] Alertas proactivas = aplicabilidad real

import time
from datetime import datetime, timezone, timedelta
from agents.base_agent import BaseAgent

class AnaliticoAgent(BaseAgent):
    
    nombre = "analitico"
    modelo = "llama-3.1-8b-instant"
    
    def _build_system_prompt(self) -> str:
        empresa = self.empresa.get("nombre", "la empresa")
        sector = self.empresa.get("sector", "servicios")
        
        return f"""
Eres el Agente Analítico de {empresa}, empresa de {sector}.
Analizas métricas del CRM y detectas patrones, anomalías y oportunidades.

MÉTRICAS CLAVE PARA EMPRESAS DE SERVICIOS:
- Tasa de conversión por etapa: ¿qué % avanza de ATENCIÓN a INTERÉS, etc.?
- Velocidad del ciclo de ventas: ¿cuánto tarda un lead en convertirse?
- Tasa de aceptación de cotizaciones: benchmark ideal > 30%
- Leads sin seguimiento: riesgo de perderlos (> 24h sin contacto)
- Servicios con más demanda: dónde enfocar esfuerzos

CÓMO DETECTAR ANOMALÍAS:
- Si leads sin seguimiento > 20% del total → ALERTA ALTA
- Si tasa conversión < 5% → analizar cuello de botella
- Si hay leads de alta prioridad sin contacto > 12h → ALERTA ALTA
- Si muchas cotizaciones rechazadas → problema de precios o propuesta

REGLA CRÍTICA: Responde ÚNICAMENTE con el JSON. Sin texto adicional.

FORMATO (JSON estricto):
{{
  "alertas": [
    {{
      "tipo": "leads_frios|baja_conversion|cotizaciones_rechazadas|oportunidad",
      "mensaje": "descripción clara del problema para el admin",
      "prioridad": "baja|media|alta",
      "lead_ids_afectados": [],
      "accion_recomendada": "qué debe hacer el admin ahora mismo"
    }}
  ],
  "insights": [
    "insight 1 con dato específico",
    "insight 2 con dato específico"
  ],
  "recomendaciones": [
    "acción concreta 1",
    "acción concreta 2"
  ],
  "resumen_ejecutivo": "2-3 oraciones con lo más importante del período",
  "score_salud_crm": 0.0
}}

score_salud_crm: 0 a 1 (1 = CRM en perfecto estado, leads bien atendidos)
"""
    
    def _recopilar_metricas(self) -> dict:
        """
        Consulta Supabase y recopila todas las métricas necesarias.
        Este es el contexto que se le pasa al LLM para análisis.
        """
        ahora = datetime.now(timezone.utc)
        hace_24h = (ahora - timedelta(hours=24)).isoformat()
        hace_7d = (ahora - timedelta(days=7)).isoformat()
        inicio_hoy = ahora.replace(hour=0, minute=0, second=0).isoformat()
        
        metricas = {}
        
        try:
            # Total leads por etapa
            leads_all = self.db.table("leads").select(
                "id, etapa_funnel, estado, prioridad, ultimo_contacto, nombre, telegram_chat_id"
            ).execute().data or []
            
            metricas["total_leads"] = len(leads_all)
            
            # Por etapa
            metricas["por_etapa"] = {
                "atencion": sum(1 for l in leads_all if l.get("etapa_funnel") == "atencion"),
                "interes": sum(1 for l in leads_all if l.get("etapa_funnel") == "interes"),
                "deseo": sum(1 for l in leads_all if l.get("etapa_funnel") == "deseo"),
                "accion": sum(1 for l in leads_all if l.get("etapa_funnel") == "accion"),
                "cliente": sum(1 for l in leads_all if l.get("etapa_funnel") == "cliente"),
            }
            
            # Por estado
            metricas["por_estado"] = {
                "nuevo": sum(1 for l in leads_all if l.get("estado") == "nuevo"),
                "contactado": sum(1 for l in leads_all if l.get("estado") == "contactado"),
                "cotizado": sum(1 for l in leads_all if l.get("estado") == "cotizado"),
                "convertido": sum(1 for l in leads_all if l.get("estado") == "convertido"),
                "inactivo": sum(1 for l in leads_all if l.get("estado") == "inactivo"),
            }
            
            # Leads sin contacto en más de 24 horas (CRÍTICO)
            leads_frios = [
                {"id": l["id"], "nombre": l.get("nombre"), "prioridad": l.get("prioridad")}
                for l in leads_all
                if l.get("ultimo_contacto", "") < hace_24h
                and l.get("estado") not in ("convertido", "inactivo")
            ]
            metricas["leads_sin_contacto_24h"] = len(leads_frios)
            metricas["leads_frios_alta_prioridad"] = [
                l for l in leads_frios if l.get("prioridad") == "alta"
            ]
            
            # Leads captados hoy
            leads_hoy = self.db.table("leads").select("id").gte(
                "created_at", inicio_hoy).execute().data or []
            metricas["leads_hoy"] = len(leads_hoy)
            
            # Cotizaciones
            cotizaciones = self.db.table("cotizaciones").select(
                "id, estado, valor, created_at"
            ).execute().data or []
            metricas["cotizaciones_total"] = len(cotizaciones)
            metricas["cotizaciones_pendientes"] = sum(1 for c in cotizaciones if c.get("estado") == "pendiente")
            metricas["cotizaciones_aceptadas"] = sum(1 for c in cotizaciones if c.get("estado") == "aceptada")
            metricas["cotizaciones_rechazadas"] = sum(1 for c in cotizaciones if c.get("estado") == "rechazada")
            if cotizaciones:
                aceptadas = metricas["cotizaciones_aceptadas"]
                metricas["tasa_aceptacion_cotizaciones"] = round(
                    aceptadas / len(cotizaciones) * 100, 1
                )
            else:
                metricas["tasa_aceptacion_cotizaciones"] = 0
            
            # Reuniones
            reuniones = self.db.table("reuniones").select(
                "id, estado, tipo, fecha_hora"
            ).execute().data or []
            metricas["reuniones_agendadas"] = sum(1 for r in reuniones if r.get("estado") == "agendada")
            metricas["reuniones_confirmadas"] = sum(1 for r in reuniones if r.get("estado") == "confirmada")
            
            # Actividad de agentes (últimas 24h)
            logs = self.db.table("agent_logs").select(
                "agente, duracion_ms, exitoso, created_at"
            ).gte("created_at", hace_24h).execute().data or []
            metricas["agente_logs_24h"] = len(logs)
            metricas["tasa_exito_agentes"] = round(
                sum(1 for l in logs if l.get("exitoso")) / len(logs) * 100, 1
            ) if logs else 100
            metricas["tiempo_respuesta_promedio_ms"] = round(
                sum(l.get("duracion_ms", 0) for l in logs) / len(logs)
            ) if logs else 0
            
        except Exception as e:
            metricas["error_recopilacion"] = str(e)
        
        return metricas
    
    def execute(self, input_data: dict) -> dict:
        """
        Analiza las métricas del CRM y genera alertas con IA.
        
        input_data esperado:
        {
            "tipo_analisis": "diario|semanal|alerta_leads_frios"
        }
        
        Returns:
        {
            "alertas": list,
            "insights": list,
            "recomendaciones": list,
            "resumen_ejecutivo": str,
            "score_salud_crm": float,
            "metricas_raw": dict
        }
        """
        start = time.monotonic()
        tipo = input_data.get("tipo_analisis", "diario")
        
        try:
            # PASO 1: Recopilar métricas desde Supabase
            metricas = self._recopilar_metricas()
            
            # PASO 2: Construir el mensaje con los datos para el LLM
            import json
            datos_para_llm = (
                f"TIPO DE ANÁLISIS: {tipo}\n"
                f"FECHA Y HORA: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                f"MÉTRICAS ACTUALES DEL CRM:\n"
                f"{json.dumps(metricas, ensure_ascii=False, indent=2)}"
            )
            
            # PASO 3: LLM analiza los datos
            content, p_tok, c_tok, duracion_ms = self._call_llm(
                system_prompt=self._build_system_prompt(),
                user_message=datos_para_llm,
                temperature=0.5,
                max_tokens=1536
            )
            
            analisis = self.groq.extract_json(content)
            
            # PASO 4: Combinar análisis con métricas raw
            resultado = {
                **analisis,
                "metricas_raw": metricas,
                "tipo_analisis": tipo,
                "generado_at": datetime.now(timezone.utc).isoformat()
            }
            
            self._log(
                accion=f"analizar_crm:{tipo}",
                input_data={"tipo": tipo, "total_leads": metricas.get("total_leads", 0)},
                output_data={
                    "alertas": len(analisis.get("alertas", [])),
                    "score_salud": analisis.get("score_salud_crm", 0),
                    "resumen": analisis.get("resumen_ejecutivo", "")[:100]
                },
                duracion_ms=duracion_ms,
                exitoso=True,
                tokens_prompt=p_tok,
                tokens_completion=c_tok
            )
            
            return resultado
            
        except Exception as e:
            duracion_ms = int((time.monotonic() - start) * 1000)
            self._log(
                accion="analizar_crm:error",
                input_data={"tipo": tipo},
                output_data={},
                duracion_ms=duracion_ms,
                exitoso=False,
                error_mensaje=str(e)
            )
            return {
                "alertas": [],
                "insights": [f"Error en análisis: {str(e)[:200]}"],
                "recomendaciones": ["Revisar los logs del sistema"],
                "resumen_ejecutivo": "No se pudo completar el análisis",
                "score_salud_crm": 0,
                "metricas_raw": {},
                "error": str(e)
            }
```

---

## ARCHIVO: test_agents.py — Probar todos los agentes

```python
# test_agents.py
# Ejecutar con: python test_agents.py
# Prueba cada agente de forma aislada ANTES de integrarlo

from config import get_settings
from database import get_db
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.conversacional import ConversacionalAgent
from agents.identidad import IdentidadAgent
from agents.analitico import AnaliticoAgent

def test_todos():
    db = get_db()
    settings = get_settings()
    
    print("\n" + "="*60)
    print("PRUEBA DE AGENTES ORBITA")
    print("="*60)
    
    # TEST 1: Orquestador
    print("\n[1/5] Probando AgenteOrquestador...")
    orch = OrchestratorAgent(db, settings)
    resultado = orch.execute({
        "mensaje": "Hola, quiero saber cuánto cuesta un chatbot para mi empresa",
        "lead_id": None,
        "session_id": "test-session-001",
        "telegram_chat_id": "123456789"
    })
    print(f"  ✓ Intención: {resultado.get('intencion')}")
    print(f"  ✓ Etapa AIDA: {resultado.get('etapa_aida')}")
    print(f"  ✓ Agente principal: {resultado.get('agente_principal')}")
    print(f"  ✓ Prioridad: {resultado.get('prioridad')}")
    
    # TEST 2: Captador
    print("\n[2/5] Probando AgenteCaptador...")
    captador = CaptadorAgent(db, settings)
    resultado = captador.execute({
        "mensaje": "Hola soy Carlos Pérez de Innovatech, soy el CEO y busco automatizar ventas",
        "telegram_user_id": "test_user_999",
        "telegram_username": "carlosperez",
        "telegram_chat_id": "999999999",
        "session_id": "test-session-002",
        "nombre_telegram": "Carlos Pérez"
    })
    print(f"  ✓ Acción: {resultado.get('accion')}")
    print(f"  ✓ Lead ID: {resultado.get('lead_id')}")
    print(f"  ✓ Datos extraídos: {resultado.get('datos_extraidos', {}).get('nombre_detectado')}")
    
    LEAD_ID_TEST = resultado.get("lead_id")
    
    # TEST 3: Identidad (probar primero para no depender de otros)
    print("\n[3/5] Probando AgenteIdentidad...")
    identidad = IdentidadAgent(db, settings)
    resultado = identidad.execute({
        "borrador": "hola como estas quieres comprar nuestro producto es muy bueno y barato",
        "contexto_lead": {"nombre": "Carlos", "empresa_nombre": "Innovatech"},
        "agente_origen": "conversacional",
        "etapa_aida": "interes"
    })
    print(f"  ✓ Aprobado: {resultado.get('aprobado')}")
    print(f"  ✓ Score marca: {resultado.get('score_marca')}")
    print(f"  ✓ Cambios: {resultado.get('cambios_realizados')}")
    print(f"  ✓ Mensaje final: {resultado.get('mensaje_final', '')[:80]}...")
    
    # TEST 4: Conversacional
    print("\n[4/5] Probando AgenteConversacional...")
    if LEAD_ID_TEST:
        conv = ConversacionalAgent(db, settings)
        resultado = conv.execute({
            "mensaje": "Me interesa saber más sobre cómo pueden ayudarme a automatizar mis ventas",
            "lead_id": LEAD_ID_TEST,
            "session_id": "test-session-002",
            "etapa_actual": "interes",
            "decision_orquestador": {"etapa_aida": "interes"}
        })
        print(f"  ✓ Respuesta (primeros 80 chars): {resultado.get('respuesta_final','')[:80]}...")
        print(f"  ✓ Acción realizada: {resultado.get('accion_realizada')}")
        print(f"  ✓ Score Identidad: {resultado.get('identidad_score')}")
    else:
        print("  ⚠ Saltando (necesita lead_id del test anterior)")
    
    # TEST 5: Analítico
    print("\n[5/5] Probando AgenteAnalitico...")
    analitico = AnaliticoAgent(db, settings)
    resultado = analitico.execute({"tipo_analisis": "diario"})
    print(f"  ✓ Score salud CRM: {resultado.get('score_salud_crm')}")
    print(f"  ✓ Alertas generadas: {len(resultado.get('alertas', []))}")
    print(f"  ✓ Resumen: {resultado.get('resumen_ejecutivo','')[:80]}...")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS AGENTES FUNCIONANDO")
    print("Revisa Supabase → tabla agent_logs para ver los registros")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_todos()
```

---

## CHECKLIST — Antes de presentar al hackathon

```
AGENTES
□ base_agent.py tiene _log(), get_history(), save_message()
□ Cada agente hereda de BaseAgent
□ Cada agente tiene nombre y modelo definidos
□ Cada agente tiene execute() implementado
□ Cada agente tiene fallback si el LLM falla
□ Cada agente llama _log() en éxito Y en error
□ python test_agents.py pasa sin errores

BASE DE DATOS
□ Tabla agent_logs tiene registros de cada test
□ Tabla conversations guarda los mensajes
□ Tabla leads tiene los leads de prueba

INTEGRACIÓN
□ OrchestratorAgent clasifica correctamente saludo/cotizacion/agendar
□ ConversacionalAgent llama a IdentidadAgent (inter-agente visible en logs)
□ CaptadorAgent crea lead en Supabase
□ AnaliticoAgent genera alertas cuando hay leads sin contacto
□ El sistema funciona end-to-end: mensaje → agentes → respuesta

HACKATHON
□ Comentarios # [CRITERIO N] visibles en cada archivo
□ Swagger /docs documenta los endpoints de agentes
□ Dashboard muestra agent_logs en tiempo real
□ Se puede demostrar Whisper transcribiendo una nota de voz
```

---

*"No se trata de tener más agentes. Se trata de que cada uno haga su trabajo perfecto."*
