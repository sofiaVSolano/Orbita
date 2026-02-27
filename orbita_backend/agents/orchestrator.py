# Agente Orquestador - Coordinador principal del sistema multi-agente
# [CRITERIO 2] - Orquestador que coordina todos los agentes

from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from config import GROQ_MODELS

class OrchestratorAgent(BaseAgent):
    """
    Agente Orquestador que coordina todos los agentes del sistema ORBITA.
    Decide qué agente debe manejar cada consulta y coordina interacciones complejas.
    """
    
    def __init__(self):
        model = GROQ_MODELS.get("orchestrator", "llama-3.3-70b-versatile")
        super().__init__(agent_name="orchestrator", model=model)
        
        # System prompt para el orquestador
        self.system_prompt = """Eres el Orquestador del sistema ORBITA, especializado en analizar consultas y coordinar respuestas.
Tu rol es comprender la intención del usuario y generar respuestas apropiadas o decidir qué agente debe manejar la consulta.
Sé conversacional, amable y profesional."""
        
        # Registro de agentes disponibles
        self.available_agents = {
            "captador": "Especialista en captura y calificación de leads",
            "conversacional": "Experto en conversaciones naturales y atención al cliente",
            "identidad": "Gestor de identidad y personalidad empresarial",
            "analitico": "Analista de datos y generador de insights"
        }
        
        # Patrones de derivación
        self.routing_patterns = {
            "lead_capture": ["contacto", "interesado", "cotización", "precio", "servicio"],
            "conversation": ["hola", "ayuda", "información", "consulta", "pregunta"],
            "identity": ["empresa", "quienes", "nosotros", "valores", "misión"],
            "analytics": ["reporte", "métricas", "análisis", "estadísticas", "dashboard"]
        }
    
    async def process_message(
        self, 
        message: str, 
        session_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje determinando qué agente debe manejarlo.
        
        Args:
            message: Mensaje del usuario
            session_id: ID de sesión
            context: Contexto adicional
            
        Returns:
            Respuesta del sistema con el agente seleccionado
        """
        if not await self.validate_input(message):
            return {
                "success": False,
                "error": "Mensaje inválido",
                "agent": self.agent_name
            }
        
        try:
            # Analizar el mensaje para determinar intención
            intention_analysis = await self._analyze_message_intention(message, session_id, context)
            
            # Seleccionar agente apropiado
            selected_agent = intention_analysis["selected_agent"]
            confidence = intention_analysis["confidence"]
            
            # Si la confianza es baja, manejar directamente
            if confidence < 0.7:
                return await self._handle_directly(message, session_id, context)
            
            # Preparar respuesta de coordinación
            coordination_result = {
                "success": True,
                "route_to_agent": selected_agent,
                "confidence": confidence,
                "reasoning": intention_analysis["reasoning"],
                "context_data": intention_analysis.get("extracted_data", {}),
                "agent": self.agent_name,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return coordination_result
            
        except Exception as e:
            await self._handle_error("orchestration_error", str(e), session_id)
            return {
                "success": False,
                "error": f"Error en orquestación: {str(e)}",
                "agent": self.agent_name
            }
    
    async def _analyze_message_intention(
        self, 
        message: str, 
        session_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analiza la intención del mensaje usando IA para determinar el agente apropiado.
        """
        analysis_prompt = f"""
        Analiza el siguiente mensaje del usuario y determina qué agente especializado debe manejarlo:

        MENSAJE: "{message}"

        AGENTES DISPONIBLES:
        - captador: Captura de leads, calificación, interés en servicios, solicitudes de cotización
        - conversacional: Conversaciones generales, preguntas informativas, soporte básico
        - identidad: Preguntas sobre la empresa, valores, servicios, equipo, historia
        - analitico: Solicitudes de reportes, métricas, análisis de datos, insights

        CONTEXTO: {context or "Sin contexto previo"}

        Responde en JSON con:
        {{
            "selected_agent": "nombre_agente",
            "confidence": 0.0-1.0,
            "reasoning": "explicación detallada",
            "extracted_data": {{"key": "value"}},
            "message_type": "tipo_mensaje"
        }}
        """
        
        response = await self.generate_response(analysis_prompt, session_id, context)
        
        if response.get("success"):
            try:
                # Intentar parsear como JSON
                import json
                analysis_result = json.loads(response["response"])
                
                # Validar que el agente seleccionado existe
                if analysis_result["selected_agent"] not in self.available_agents:
                    analysis_result["selected_agent"] = "conversacional"
                    analysis_result["confidence"] = 0.5
                
                return analysis_result
                
            except (json.JSONDecodeError, KeyError):
                # Fallback: análisis por patrones simples
                return self._simple_pattern_matching(message)
        else:
            return self._simple_pattern_matching(message)
    
    def _simple_pattern_matching(self, message: str) -> Dict[str, Any]:
        """
        Análisis de patrones simple como fallback.
        """
        message_lower = message.lower()
        
        # Calcular scores para cada tipo
        scores = {}
        for agent_type, keywords in self.routing_patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            scores[agent_type] = score / len(keywords)
        
        # Mapeo de tipos a agentes
        type_to_agent = {
            "lead_capture": "captador",
            "conversation": "conversacional", 
            "identity": "identidad",
            "analytics": "analitico"
        }
        
        # Seleccionar el mejor match
        best_type = max(scores, key=scores.get)
        selected_agent = type_to_agent[best_type]
        confidence = min(scores[best_type] * 2, 1.0)  # Normalizar
        
        # Si no hay un match claro, usar conversacional
        if confidence < 0.3:
            selected_agent = "conversacional"
            confidence = 0.6
        
        return {
            "selected_agent": selected_agent,
            "confidence": confidence,
            "reasoning": f"Análisis de patrones: mejor match con {best_type}",
            "extracted_data": {"pattern_scores": scores},
            "message_type": "pattern_matched"
        }
    
    async def _handle_directly(
        self, 
        message: str, 
        session_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Maneja el mensaje directamente cuando no hay un agente claro.
        """
        direct_response = await self.generate_response(message, session_id, context)
        
        if direct_response.get("success"):
            return {
                "success": True,
                "response": direct_response["response"],
                "agent": self.agent_name,
                "handled_directly": True,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "No se pudo procesar el mensaje",
                "agent": self.agent_name,
                "fallback_response": "Disculpa, no pude entender tu consulta. ¿Podrías reformularla?"
            }
    
    def get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prompt del sistema para el orquestador.
        """
        return f"""
        Eres el ORQUESTADOR del sistema multi-agente ORBITA, un avanzado sistema de IA para gestión de leads.

        TU MISIÓN:
        - Coordinar y dirigir consultas a los agentes especializados apropiados
        - Mantener coherencia en todas las interacciones del sistema
        - Optimizar la experiencia del usuario

        AGENTES BAJO TU COORDINACIÓN:
        {chr(10).join([f"- {name}: {desc}" for name, desc in self.available_agents.items()])}

        CONTEXTO ACTUAL: {context or "Conversación nueva"}

        INSTRUCCIONES:
        1. Analiza cada mensaje cuidadosamente
        2. Determina el agente más apropiad para la consulta
        3. Si no hay un match claro, maneja la consulta directamente
        4. Mantén un tono profesional pero amigable
        5. Siempre busca identificar oportunidades de lead

        Responde de manera natural y útil, coordinando eficientemente el sistema.
        """
    
    def get_capabilities(self) -> List[str]:
        """Capacidades del orquestador"""
        return [
            "Análisis de intención de mensajes",
            "Routing inteligente a agentes especializados",
            "Coordinación multi-agente",
            "Manejo de consultas ambiguas",
            "Optimización de flujos de conversación",
            "Análisis de contexto conversacional",
            "Fallback y recuperación de errores"
        ]
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema coordinado.
        """
        return {
            "orchestrator": self.agent_name,
            "available_agents": len(self.available_agents),
            "active_agents": list(self.available_agents.keys()),
            "routing_patterns": len(self.routing_patterns),
            "system_health": await self.get_health_status(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def coordination_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Genera un resumen de la coordinación en una sesión.
        """
        return {
            "session_id": session_id,
            "orchestrator": self.agent_name,
            "coordination_active": True,
            "agents_available": list(self.available_agents.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }