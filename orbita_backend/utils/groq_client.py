# Cliente para Groq API
# [CRITERIO 3] — Uso real de IA con modelos de Groq

import groq
from typing import Dict, Any, List, Optional
from config import get_settings

class GroqClient:
    """
    Cliente para interactuar con Groq API.
    Maneja diferentes modelos para diferentes agentes según las especificaciones.
    """
    
    def __init__(self):
        settings = get_settings()
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.models = {
            "orchestrator": "llama-3.3-70b-versatile",
            "captador": "gemma2-9b-it", 
            "conversacional": "mixtral-8x7b-32768",
            "identidad": "llama-3.1-8b-instant",
            "analitico": "llama-3.3-70b-versatile"
        }
        
    def get_model_for_agent(self, agent_type: str) -> str:
        """Obtiene el modelo apropiado para cada tipo de agente."""
        return self.models.get(agent_type, "llama-3.1-8b-instant")
    
    async def generate_completion(
        self, 
        prompt: str, 
        agent_type: str = "conversacional",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta usando Groq API.
        
        Args:
            prompt: El prompt del usuario
            agent_type: Tipo de agente para seleccionar el modelo
            max_tokens: Máximo número de tokens en la respuesta
            temperature: Creatividad de la respuesta (0.0-2.0)
            system_message: Mensaje del sistema opcional
            
        Returns:
            Respuesta generada por el modelo
        """
        model = self.get_model_for_agent(agent_type)
        
        messages = []
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error en Groq API: {e}")
            return "Lo siento, hay un problema técnico. Por favor intenta de nuevo."

# Instancia global del cliente
_groq_client: Optional[GroqClient] = None

def get_groq_client() -> GroqClient:
    """Obtiene instancia global del cliente Groq."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client

# Funciones de conveniencia para usar en los agentes
async def generate_agent_response(
    prompt: str,
    agent_type: str,
    system_message: str = None,
    **kwargs
) -> str:
    """Función de conveniencia para generar respuestas de agentes."""
    client = get_groq_client()
    return await client.generate_completion(
        prompt=prompt,
        agent_type=agent_type, 
        system_message=system_message,
        **kwargs
    )