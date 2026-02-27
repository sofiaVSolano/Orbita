"""
Gestión de memoria y contexto de conversaciones para ORBITA
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict


class ConversationMemory:
    """
    Maneja la memoria de conversaciones para mantener contexto y continuidad
    en las interacciones con los usuarios.
    """
    
    def __init__(self):
        self.conversations: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'messages': [],
            'context': {},
            'last_interaction': None,
            'agent_state': {},
            'lead_info': {},
            'session_data': {}
        })
        
        # Configuración de limpieza automática (24 horas por defecto)
        self.cleanup_interval = 24 * 60 * 60  # segundos
        self.max_messages_per_conversation = 100
        
    def add_message(self, conversation_id: str, message: Dict[str, Any]):
        """
        Añade un mensaje a la conversación.
        
        Args:
            conversation_id: Identificador único de la conversación
            message: Diccionario con el mensaje
        """
        conversation = self.conversations[conversation_id]
        
        # Añadir timestamp si no existe
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
            
        conversation['messages'].append(message)
        conversation['last_interaction'] = datetime.now().isoformat()
        
        # Limitar número de mensajes
        if len(conversation['messages']) > self.max_messages_per_conversation:
            conversation['messages'] = conversation['messages'][-self.max_messages_per_conversation:]
            
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de conversación.
        
        Args:
            conversation_id: Identificador de la conversación
            limit: Número máximo de mensajes a retornar
        
        Returns:
            Lista de mensajes
        """
        messages = self.conversations[conversation_id]['messages']
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def update_context(self, conversation_id: str, context_update: Dict[str, Any]):
        """
        Actualiza el contexto de la conversación.
        
        Args:
            conversation_id: Identificador de la conversación
            context_update: Diccionario con actualizaciones del contexto
        """
        self.conversations[conversation_id]['context'].update(context_update)
        
    def get_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene el contexto actual de la conversación.
        
        Args:
            conversation_id: Identificador de la conversación
        
        Returns:
            Diccionario con el contexto
        """
        return self.conversations[conversation_id]['context']
    
    def set_agent_state(self, conversation_id: str, agent_name: str, state: Dict[str, Any]):
        """
        Establece el estado de un agente específico para la conversación.
        
        Args:
            conversation_id: Identificador de la conversación
            agent_name: Nombre del agente
            state: Estado del agente
        """
        self.conversations[conversation_id]['agent_state'][agent_name] = state
        
    def get_agent_state(self, conversation_id: str, agent_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un agente específico.
        
        Args:
            conversation_id: Identificador de la conversación
            agent_name: Nombre del agente
        
        Returns:
            Estado del agente
        """
        return self.conversations[conversation_id]['agent_state'].get(agent_name, {})
    
    def set_lead_info(self, conversation_id: str, lead_data: Dict[str, Any]):
        """
        Establece información del lead para la conversación.
        
        Args:
            conversation_id: Identificador de la conversación
            lead_data: Datos del lead
        """
        self.conversations[conversation_id]['lead_info'].update(lead_data)
        
    def get_lead_info(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene información del lead.
        
        Args:
            conversation_id: Identificador de la conversación
        
        Returns:
            Información del lead
        """
        return self.conversations[conversation_id]['lead_info']
    
    def set_session_data(self, conversation_id: str, key: str, value: Any):
        """
        Establece datos de sesión específicos.
        
        Args:
            conversation_id: Identificador de la conversación
            key: Clave del dato
            value: Valor del dato
        """
        self.conversations[conversation_id]['session_data'][key] = value
        
    def get_session_data(self, conversation_id: str, key: str, default: Any = None) -> Any:
        """
        Obtiene un dato de sesión específico.
        
        Args:
            conversation_id: Identificador de la conversación
            key: Clave del dato
            default: Valor por defecto si no existe la clave
        
        Returns:
            Valor del dato o default
        """
        return self.conversations[conversation_id]['session_data'].get(key, default)
    
    def clear_conversation(self, conversation_id: str):
        """
        Limpia una conversación específica.
        
        Args:
            conversation_id: Identificador de la conversación
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """
        Limpia conversaciones antiguas.
        
        Args:
            max_age_hours: Máximo número de horas antes de limpiar
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        conversations_to_remove = []
        
        for conv_id, conv_data in self.conversations.items():
            last_interaction = conv_data.get('last_interaction')
            if last_interaction:
                last_time = datetime.fromisoformat(last_interaction)
                if last_time < cutoff_time:
                    conversations_to_remove.append(conv_id)
                    
        for conv_id in conversations_to_remove:
            del self.conversations[conv_id]
            
        return len(conversations_to_remove)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de la conversación.
        
        Args:
            conversation_id: Identificador de la conversación
        
        Returns:
            Resumen de la conversación
        """
        if conversation_id not in self.conversations:
            return {}
            
        conv = self.conversations[conversation_id]
        
        return {
            'conversation_id': conversation_id,
            'message_count': len(conv['messages']),
            'last_interaction': conv['last_interaction'],
            'has_lead_info': bool(conv['lead_info']),
            'active_agents': list(conv['agent_state'].keys()),
            'context_keys': list(conv['context'].keys()),
            'session_keys': list(conv['session_data'].keys())
        }
    
    def export_conversation(self, conversation_id: str) -> Optional[str]:
        """
        Exporta una conversación a JSON.
        
        Args:
            conversation_id: Identificador de la conversación
        
        Returns:
            JSON string de la conversación o None
        """
        if conversation_id not in self.conversations:
            return None
            
        return json.dumps(self.conversations[conversation_id], indent=2, default=str)
    
    def import_conversation(self, conversation_id: str, conversation_json: str) -> bool:
        """
        Importa una conversación desde JSON.
        
        Args:
            conversation_id: Identificador de la conversación
            conversation_json: JSON string de la conversación
        
        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            conversation_data = json.loads(conversation_json)
            self.conversations[conversation_id] = conversation_data
            return True
        except json.JSONDecodeError:
            return False
    
    def get_all_conversation_ids(self) -> List[str]:
        """
        Obtiene todos los IDs de conversaciones activas.
        
        Returns:
            Lista de IDs de conversaciones
        """
        return list(self.conversations.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de memoria.
        
        Returns:
            Diccionario con estadísticas
        """
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv['messages']) for conv in self.conversations.values())
        
        conversations_with_leads = sum(1 for conv in self.conversations.values() if conv['lead_info'])
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'conversations_with_leads': conversations_with_leads,
            'average_messages_per_conversation': total_messages / total_conversations if total_conversations > 0 else 0
        }


class MemoryManager:
    """
    Clase de compatibilidad para el sistema de agentes existente.
    Encapsula ConversationMemory con la interfaz esperada.
    """
    
    def __init__(self):
        self.conversation_memory = ConversationMemory()
        
    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """
        Obtiene el contexto de conversación para un session_id.
        
        Args:
            session_id: Identificador de la sesión
        
        Returns:
            Contexto de la conversación
        """
        return {
            'messages': self.conversation_memory.get_conversation_history(session_id),
            'context': self.conversation_memory.get_context(session_id),
            'lead_info': self.conversation_memory.get_lead_info(session_id),
            'agent_state': self.conversation_memory.conversations[session_id]['agent_state']
        }
    
    async def save_message(self, session_id: str, message: str, message_type: str = "user", agent_name: str = None, **kwargs):
        """
        Guarda un mensaje en la conversación.
        
        Args:
            session_id: Identificador de la sesión
            message: Contenido del mensaje
            message_type: Tipo de mensaje (user, agent, system)
            agent_name: Nombre del agente (si aplica)
            **kwargs: Metadatos adicionales
        """
        message_data = {
            'content': message,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        if agent_name:
            message_data['agent_name'] = agent_name
            
        self.conversation_memory.add_message(session_id, message_data)
    
    def clear_conversation(self, session_id: str):
        """
        Limpia una conversación específica.
        
        Args:
            session_id: Identificador de la sesión
        """
        self.conversation_memory.clear_conversation(session_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la memoria.
        
        Returns:
            Estadísticas de memoria
        """
        return self.conversation_memory.get_stats()


# Instancia global de memoria de conversaciones
conversation_memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    """
    Obtiene la instancia global de memoria de conversaciones.
    
    Returns:
        Instancia de ConversationMemory
    """
    return conversation_memory


# Funciones de conveniencia para uso directo
def add_user_message(conversation_id: str, user_id: str, message: str, message_type: str = "text"):
    """
    Añade un mensaje de usuario a la conversación.
    """
    message_data = {
        'type': 'user',
        'user_id': user_id,
        'content': message,
        'message_type': message_type,
        'timestamp': datetime.now().isoformat()
    }
    conversation_memory.add_message(conversation_id, message_data)


def add_agent_message(conversation_id: str, agent_name: str, message: str, metadata: Optional[Dict] = None):
    """
    Añade un mensaje de agente a la conversación.
    """
    message_data = {
        'type': 'agent',
        'agent_name': agent_name,
        'content': message,
        'metadata': metadata or {},
        'timestamp': datetime.now().isoformat()
    }
    conversation_memory.add_message(conversation_id, message_data)


def get_recent_messages(conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Obtiene los mensajes más recientes de una conversación.
    """
    return conversation_memory.get_conversation_history(conversation_id, limit)


def update_lead_context(conversation_id: str, lead_data: Dict[str, Any]):
    """
    Actualiza el contexto del lead en la conversación.
    """
    conversation_memory.set_lead_info(conversation_id, lead_data)


def get_conversation_context(conversation_id: str) -> Dict[str, Any]:
    """
    Obtiene el contexto completo de una conversación.
    """
    return {
        'messages': conversation_memory.get_conversation_history(conversation_id),
        'context': conversation_memory.get_context(conversation_id),
        'lead_info': conversation_memory.get_lead_info(conversation_id),
        'summary': conversation_memory.get_conversation_summary(conversation_id)
    }


async def cleanup_memory_periodically():
    """
    Tarea asíncrona para limpieza periódica de memoria.
    """
    while True:
        try:
            cleaned = conversation_memory.cleanup_old_conversations()
            if cleaned > 0:
                print(f"Limpiadas {cleaned} conversaciones antiguas")
        except Exception as e:
            print(f"Error en limpieza de memoria: {e}")
        
        # Esperar 1 hora antes de la siguiente limpieza
        await asyncio.sleep(3600)