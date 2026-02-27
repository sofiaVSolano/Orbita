# Agente base para el sistema multi-agente ORBITA
# [CRITERIO 3] - Base común para todos los agentes con integración a Groq

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
from utils.groq_client import GroqClient
from utils.memory import MemoryManager
from database import log_agent_action

class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes del sistema ORBITA.
    Define la interfaz común que todos los agentes deben implementar.
    """
    
    def __init__(self, agent_name: str, model: str = "llama-3.3-70b-versatile"):
        self.agent_name = agent_name
        self.model = model
        self.groq_client = GroqClient()
        self.memory_manager = MemoryManager()
        self.active = True
        self.created_at = datetime.utcnow()
        
    @abstractmethod
    async def process_message(
        self, 
        message: str, 
        session_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje y devuelve una respuesta.
        
        Args:
            message: Mensaje del usuario
            session_id: ID de la sesión de conversación
            context: Contexto adicional (lead info, empresa info, etc.)
            
        Returns:
            Dict con la respuesta del agente y metadata
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Obtiene el prompt del sistema específico para este agente.
        
        Args:
            context: Contexto para personalizar el prompt
            
        Returns:
            String del prompt del sistema
        """
        pass
    
    async def generate_response(
        self, 
        user_message: str, 
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta usando Groq API con el contexto de conversación.
        
        Args:
            user_message: Mensaje del usuario
            session_id: ID de sesión para mantener contexto
            context: Contexto adicional
            
        Returns:
            Dict con respuesta y metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Obtener historial de conversación
            conversation_history = await self.memory_manager.get_conversation_context(session_id)
            
            # Construir prompt del sistema
            system_prompt = self.get_system_prompt(context)
            
            # Preparar mensajes para Groq
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Agregar historial si existe
            if conversation_history:
                messages.append({
                    "role": "system", 
                    "content": f"Contexto de conversación previa:\n{conversation_history}"
                })
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": user_message})
            
            # Construir el system message con el contexto si existe
            system_msg = self.system_prompt
            if conversation_history:
                system_msg += f"\n\nContexto de conversación previa:\n{conversation_history}"
            
            # Llamada a Groq API
            agent_response = await self.groq_client.generate_completion(
                prompt=user_message,
                agent_type=self.agent_name,
                system_message=system_msg,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Guardar en memoria
            await self.memory_manager.save_message(
                session_id=session_id,
                message=user_message,
                message_type="user"
            )
            
            await self.memory_manager.save_message(
                session_id=session_id,
                message=agent_response,
                message_type="assistant",
                agent_name=self.agent_name
            )
            
            # Log de actividad
            await log_agent_action(
                agent_name=self.agent_name,
                action="generate_response",
                session_id=session_id,
                details={
                    "message_length": len(user_message),
                    "response_length": len(agent_response),
                    "model_used": self.model,
                    "processing_time_ms": processing_time
                }
            )
            
            return {
                "success": True,
                "response": agent_response,
                "agent": self.agent_name,
                "session_id": session_id,
                "processing_time_ms": processing_time,
                "model_used": self.model,
                "timestamp": datetime.utcnow().isoformat()
            }
                
        except Exception as e:
            await self._handle_error("processing_error", str(e), session_id)
            return {
                "success": False,
                "error": f"Error procesando mensaje: {str(e)}",
                "agent": self.agent_name
            }
    
    async def _handle_error(self, error_type: str, error_message: str, session_id: str):
        """Maneja errores del agente y los registra"""
        await log_agent_action(
            agent_name=self.agent_name,
            action="error",
            session_id=session_id,
            details={
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        print(f"❌ Error en {self.agent_name}: {error_message}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Obtiene información del agente"""
        return {
            "name": self.agent_name,
            "model": self.model,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "capabilities": self.get_capabilities()
        }
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Devuelve las capacidades específicas de este agente.
        
        Returns:
            Lista de capacidades del agente
        """
        pass
    
    async def validate_input(self, message: str) -> bool:
        """
        Valida el input del usuario antes de procesarlo.
        
        Args:
            message: Mensaje a validar
            
        Returns:
            True si el input es válido, False en caso contrario
        """
        if not message or len(message.strip()) == 0:
            return False
        
        if len(message) > 10000:  # Límite de caracteres
            return False
            
        return True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del agente"""
        return {
            "agent": self.agent_name,
            "active": self.active,
            "groq_connection": await self.groq_client.health_check(),
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def activate(self):
        """Activa el agente"""
        self.active = True
        
    def deactivate(self):
        """Desactiva el agente"""
        self.active = False