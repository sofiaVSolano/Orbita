# Agente de Comunicación - Especialista en estrategias de comunicación y mensajería
# [CRITERIO 4] - Comunicación estratégica multicanal y personalizada

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import json
from enum import Enum
from .base_agent import BaseAgent
from config import GROQ_MODELS, EMPRESA_NOMBRE, EMPRESA_DESCRIPCION

class CommunicationType(Enum):
    """Tipos de comunicación disponibles"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PUSH = "push_notification"
    IN_APP = "in_app_message"
    SOCIAL = "social_media"
    PHONE = "phone_call"

class MessagePriority(Enum):
    """Prioridades de mensaje"""
    URGENT = "urgent"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class CampaignType(Enum):
    """Tipos de campaña de comunicación"""
    ONBOARDING = "onboarding"
    NURTURING = "nurturing"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    SUPPORT = "support"

class ComunicacionAgent(BaseAgent):
    """
    Agente especializado en estrategias de comunicación multicanal.
    Diseña, ejecuta y optimiza campañas de comunicación personalizadas.
    """
    
    def __init__(self):
        model = GROQ_MODELS.get("comunicacion", "mixtral-8x7b-32768")
        super().__init__(agent_name="comunicacion", model=model)
        
        # Canales de comunicación disponibles
        self.communication_channels = {
            "email": {
                "name": "Email Marketing",
                "best_for": ["detailed_content", "formal_communication", "newsletters"],
                "limitations": ["deliverability", "spam_filters"],
                "engagement_rate": 0.25,
                "conversion_rate": 0.03
            },
            "sms": {
                "name": "SMS Messages",
                "best_for": ["urgent_notifications", "reminders", "confirmations"],
                "limitations": ["character_limit", "cost_per_message"],
                "engagement_rate": 0.85,
                "conversion_rate": 0.08
            },
            "whatsapp": {
                "name": "WhatsApp Business",
                "best_for": ["personal_communication", "rich_media", "customer_support"],
                "limitations": ["24h_window", "template_approval"],
                "engagement_rate": 0.70,
                "conversion_rate": 0.12
            },
            "telegram": {
                "name": "Telegram Bot",
                "best_for": ["automated_responses", "group_communication", "file_sharing"],
                "limitations": ["user_adoption", "feature_complexity"],
                "engagement_rate": 0.60,
                "conversion_rate": 0.05
            },
            "push": {
                "name": "Push Notifications",
                "best_for": ["mobile_engagement", "real_time_alerts", "app_retention"],
                "limitations": ["permission_required", "notification_fatigue"],
                "engagement_rate": 0.40,
                "conversion_rate": 0.04
            }
        }
        
        # Estrategias de comunicación por segmento
        self.segment_strategies = {
            "enterprise": {
                "preferred_channels": ["email", "phone"],
                "tone": "professional",
                "frequency": "low",
                "content_focus": ["roi", "security", "scalability", "compliance"]
            },
            "sme": {
                "preferred_channels": ["email", "whatsapp", "sms"],
                "tone": "business_friendly",
                "frequency": "medium",
                "content_focus": ["efficiency", "cost_savings", "ease_of_use", "results"]
            },
            "startup": {
                "preferred_channels": ["telegram", "email", "whatsapp"],
                "tone": "innovative",
                "frequency": "high",
                "content_focus": ["growth", "innovation", "flexibility", "speed"]
            },
            "individual": {
                "preferred_channels": ["whatsapp", "sms", "push"],
                "tone": "personal",
                "frequency": "medium",
                "content_focus": ["value", "simplicity", "personal_benefit", "convenience"]
            }
        }
        
        # Templates de mensajes base
        self.message_templates = {
            "welcome": {
                "subject": "Bienvenido a {company_name}",
                "content": "Hola {user_name}, nos alegra tenerte con nosotros...",
                "channels": ["email", "whatsapp"]
            },
            "follow_up": {
                "subject": "¿Cómo va tu experiencia con {company_name}?",
                "content": "Hola {user_name}, queríamos saber cómo ha sido tu experiencia...",
                "channels": ["email", "sms", "whatsapp"]
            },
            "offer": {
                "subject": "Oferta especial para {user_name}",
                "content": "Tenemos una propuesta especial que creemos te interesará...",
                "channels": ["email", "whatsapp", "push"]
            },
            "reminder": {
                "subject": "Recordatorio importante",
                "content": "No olvides {action_required}...",
                "channels": ["sms", "push", "whatsapp"]
            },
            "support": {
                "subject": "Estamos aquí para ayudarte",
                "content": "Hemos notado que podrías necesitar ayuda con...",
                "channels": ["email", "whatsapp", "phone"]
            }
        }
    
    async def process_message(
        self, 
        message: str, 
        session_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una solicitud de comunicación y genera estrategia personalizada.
        
        Args:
            message: Solicitud de comunicación del usuario
            session_id: ID de sesión
            context: Contexto del usuario y situación
            
        Returns:
            Estrategia de comunicación completa
        """
        if not await self.validate_input(message):
            return {
                "success": False,
                "error": "Solicitud de comunicación inválida",
                "agent": self.agent_name
            }
        
        try:
            # Analizar la solicitud de comunicación
            communication_request = await self._analyze_communication_request(message, context)
            
            # Determinar estrategia de canal
            channel_strategy = await self._determine_channel_strategy(
                communication_request, context
            )
            
            # Generar contenido personalizado
            personalized_content = await self._generate_personalized_content(
                communication_request, channel_strategy, session_id
            )
            
            # Crear calendario de comunicación
            communication_schedule = await self._create_communication_schedule(
                communication_request, channel_strategy
            )
            
            # Definir métricas de seguimiento
            tracking_metrics = await self._define_tracking_metrics(
                communication_request, channel_strategy
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "agent": self.agent_name,
                "communication_request": communication_request,
                "channel_strategy": channel_strategy,
                "personalized_content": personalized_content,
                "communication_schedule": communication_schedule,
                "tracking_metrics": tracking_metrics,
                "estimated_reach": channel_strategy.get("estimated_reach", {}),
                "expected_performance": channel_strategy.get("expected_performance", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self._handle_error("communication_strategy_error", str(e), session_id)
            return {
                "success": False,
                "error": f"Error en estrategia de comunicación: {str(e)}",
                "agent": self.agent_name,
                "fallback_recommendation": "Usar comunicación estándar por email"
            }
    
    async def _analyze_communication_request(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analiza la solicitud de comunicación del usuario.
        """
        analysis_prompt = f"""
        Analiza la siguiente solicitud de comunicación y determina la estrategia más efectiva.

        SOLICITUD: "{message}"
        CONTEXTO DEL USUARIO: {context or "Usuario general"}

        Determina:
        1. Objetivo de comunicación (awareness, engagement, conversion, retention, support)
        2. Tipo de campaña (onboarding, nurturing, promotional, educational, retention, reactivation, support)
        3. Audiencia objetivo (características, segmento, tamaño)
        4. Urgencia del mensaje (urgent, high, medium, low)
        5. Tipo de contenido necesario (informational, promotional, educational, transactional, relational)
        6. Canales preferidos o sugeridos
        7. Timeline deseado (immediate, short_term, medium_term, long_term)
        8. Métricas de éxito esperadas

        TIPOS DE CAMPAÑA DISPONIBLES:
        - onboarding: Bienvenida y orientación de nuevos usuarios
        - nurturing: Desarrollo de relación y educación gradual
        - promotional: Ofertas, descuentos y promociones
        - educational: Contenido educativo y de valor
        - retention: Mantener engagement de usuarios actuales
        - reactivation: Re-engagement de usuarios inactivos
        - support: Soporte y asistencia al cliente

        Responde en JSON:
        {{
            "communication_objective": "objetivo_principal",
            "campaign_type": "tipo_campana",
            "target_audience": {{
                "segment": "segmento_principal",
                "characteristics": ["caracteristica1", "caracteristica2"],
                "estimated_size": "small/medium/large",
                "personas": ["persona1", "persona2"]
            }},
            "message_priority": "urgent/high/medium/low",
            "content_type": "tipo_contenido",
            "preferred_channels": ["canal1", "canal2"],
            "timeline": "timeline_deseado",
            "success_metrics": ["metric1", "metric2"],
            "special_requirements": ["requirement1", "requirement2"],
            "budget_considerations": "low/medium/high/enterprise",
            "compliance_requirements": ["requirement1", "requirement2"],
            "confidence": 0.0-1.0
        }}
        """
        
        response = await self.generate_response(analysis_prompt, f"comm_analysis_{message[:50]}")
        
        try:
            request_analysis = json.loads(response.get("response", "{}"))
            
            # Valores por defecto si faltan campos
            defaults = {
                "communication_objective": "engagement",
                "campaign_type": "nurturing",
                "target_audience": {
                    "segment": "general",
                    "characteristics": ["interested_users"],
                    "estimated_size": "medium",
                    "personas": ["general_user"]
                },
                "message_priority": "medium",
                "content_type": "informational",
                "preferred_channels": ["email", "whatsapp"],
                "timeline": "medium_term",
                "success_metrics": ["open_rate", "engagement_rate"],
                "special_requirements": [],
                "budget_considerations": "medium",
                "compliance_requirements": [],
                "confidence": 0.7
            }
            
            # Fusionar con valores por defecto
            for key, default_value in defaults.items():
                if key not in request_analysis:
                    request_analysis[key] = default_value
            
            return request_analysis
            
        except (json.JSONDecodeError, Exception):
            # Análisis simple como fallback
            return self._simple_communication_analysis(message, context)
    
    def _simple_communication_analysis(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Análisis simple de comunicación como fallback.
        """
        message_lower = message.lower()
        
        # Detectar objetivo por palabras clave
        if any(word in message_lower for word in ["urgente", "inmediato", "ahora", "ya"]):
            priority = "urgent"
            timeline = "immediate"
        elif any(word in message_lower for word in ["promoción", "oferta", "descuento", "venta"]):
            campaign_type = "promotional"
            priority = "high"
        elif any(word in message_lower for word in ["bienvenida", "onboarding", "nuevo"]):
            campaign_type = "onboarding"
            priority = "medium"
        elif any(word in message_lower for word in ["educativo", "información", "contenido"]):
            campaign_type = "educational"
            priority = "medium"
        else:
            campaign_type = "nurturing"
            priority = "medium"
        
        return {
            "communication_objective": "engagement",
            "campaign_type": campaign_type,
            "target_audience": {
                "segment": "general",
                "characteristics": ["engaged_users"],
                "estimated_size": "medium", 
                "personas": ["general_user"]
            },
            "message_priority": priority,
            "content_type": "informational",
            "preferred_channels": ["email", "whatsapp"],
            "timeline": timeline if 'timeline' in locals() else "medium_term",
            "success_metrics": ["open_rate", "click_rate"],
            "special_requirements": [],
            "budget_considerations": "medium",
            "compliance_requirements": [],
            "confidence": 0.6
        }
    
    async def _determine_channel_strategy(
        self, 
        communication_request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Determina la estrategia óptima de canales de comunicación.
        """
        audience = communication_request.get("target_audience", {})
        segment = audience.get("segment", "general")
        priority = communication_request.get("message_priority", "medium")
        campaign_type = communication_request.get("campaign_type", "nurturing")
        
        # Obtener estrategia base para el segmento
        base_strategy = self.segment_strategies.get(segment, self.segment_strategies["individual"])
        
        # Ajustar canales según prioridad
        if priority == "urgent":
            primary_channels = ["sms", "whatsapp", "phone"]
            secondary_channels = ["push", "email"]
        elif priority == "high":
            primary_channels = ["whatsapp", "email", "sms"]
            secondary_channels = ["push", "telegram"]
        else:
            primary_channels = base_strategy["preferred_channels"][:2]
            secondary_channels = base_strategy["preferred_channels"][2:] + ["push"]
        
        # Ajustar según tipo de campaña
        if campaign_type == "onboarding":
            primary_channels = ["email", "whatsapp"]
            secondary_channels = ["sms", "push"]
        elif campaign_type == "promotional":
            primary_channels = ["whatsapp", "email", "sms"] 
            secondary_channels = ["push", "social"]
        elif campaign_type == "support":
            primary_channels = ["whatsapp", "phone", "email"]
            secondary_channels = ["telegram"]
        
        # Calcular métricas esperadas
        expected_performance = {}
        estimated_reach = {}
        
        for channel in primary_channels:
            if channel in self.communication_channels:
                channel_data = self.communication_channels[channel]
                expected_performance[channel] = {
                    "engagement_rate": channel_data["engagement_rate"],
                    "conversion_rate": channel_data["conversion_rate"],
                    "best_for": channel_data["best_for"]
                }
                # Estimar alcance basado en el tamaño de audiencia
                audience_size = audience.get("estimated_size", "medium")
                base_reach = {"small": 100, "medium": 500, "large": 2000, "enterprise": 5000}
                estimated_reach[channel] = base_reach.get(audience_size, 500)
        
        return {
            "primary_channels": primary_channels,
            "secondary_channels": secondary_channels,
            "channel_mix": {
                "primary_weight": 0.7,
                "secondary_weight": 0.3
            },
            "frequency_strategy": {
                "high_priority": "multiple_touches_24h",
                "medium_priority": "weekly_cadence", 
                "low_priority": "monthly_cadence"
            },
            "personalization_level": base_strategy.get("tone", "professional"),
            "expected_performance": expected_performance,
            "estimated_reach": estimated_reach,
            "budget_allocation": self._calculate_budget_allocation(primary_channels, secondary_channels)
        }
    
    def _calculate_budget_allocation(self, primary_channels: List[str], secondary_channels: List[str]) -> Dict[str, float]:
        """
        Calcula la asignación de presupuesto por canal.
        """
        total_channels = len(primary_channels) + len(secondary_channels)
        primary_weight = 0.7
        secondary_weight = 0.3
        
        allocation = {}
        
        # Asignar presupuesto a canales primarios
        primary_portion = primary_weight / len(primary_channels) if primary_channels else 0
        for channel in primary_channels:
            allocation[channel] = primary_portion
        
        # Asignar presupuesto a canales secundarios
        if secondary_channels:
            secondary_portion = secondary_weight / len(secondary_channels)
            for channel in secondary_channels:
                allocation[channel] = secondary_portion
        
        return allocation
    
    async def _generate_personalized_content(
        self, 
        communication_request: Dict[str, Any],
        channel_strategy: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Genera contenido personalizado para cada canal.
        """
        campaign_type = communication_request.get("campaign_type", "nurturing")
        content_type = communication_request.get("content_type", "informational")
        audience = communication_request.get("target_audience", {})
        
        content_prompt = f"""
        Genera contenido personalizado para una campaña de comunicación.

        EMPRESA: {EMPRESA_NOMBRE} - {EMPRESA_DESCRIPCION}

        DETALLES DE LA CAMPAÑA:
        - Tipo: {campaign_type}
        - Contenido: {content_type}
        - Audiencia: {audience.get('segment', 'general')}
        - Características: {audience.get('characteristics', [])}

        CANALES: {channel_strategy.get('primary_channels', [])}

        Para cada canal, genera:
        1. Asunto/Título (para email y push notifications)
        2. Contenido principal (adaptado a las limitaciones del canal)
        3. Call-to-action específico
        4. Elementos de personalización
        5. Variaciones A/B para testing

        GUIDELINES:
        - Email: Hasta 200 palabras, formato HTML friendly
        - SMS: Máximo 160 caracteres, directo y claro
        - WhatsApp: Conversacional, puede incluir emojis, hasta 300 palabras
        - Push: Título max 65 chars, mensaje max 240 chars
        - Telegram: Informal pero informativo, puede incluir multimedia

        Responde en JSON:
        {{
            "content_variations": {{
                "email": {{
                    "subject_lines": ["subject1", "subject2", "subject3"],
                    "main_content": "contenido_email",
                    "html_template": "template_html",
                    "call_to_action": "cta_text",
                    "personalization_tags": ["{{name}}", "{{company}}"]
                }},
                "sms": {{
                    "messages": ["message1", "message2"],
                    "call_to_action": "cta_text",
                    "personalization_tags": ["{{name}}"]
                }},
                "whatsapp": {{
                    "messages": ["message1", "message2"],
                    "media_suggestions": ["image", "document"],
                    "call_to_action": "cta_text",
                    "personalization_tags": ["{{name}}", "{{company}}"]
                }},
                "push": {{
                    "titles": ["title1", "title2"],
                    "messages": ["message1", "message2"],
                    "call_to_action": "cta_text"
                }}
            }},
            "ab_testing_plan": {{
                "variables_to_test": ["variable1", "variable2"],
                "test_duration": "7_days",
                "success_criteria": "click_rate_improvement"
            }},
            "personalization_strategy": {{
                "dynamic_content": ["content_block1", "content_block2"],
                "segmentation_rules": ["rule1", "rule2"]
            }}
        }}
        """
        
        response = await self.generate_response(content_prompt, f"content_{session_id}")
        
        try:
            content_result = json.loads(response.get("response", "{}"))
            
            # Agregar metadatos de contenido
            content_result["generation_metadata"] = {
                "created_at": datetime.utcnow().isoformat(),
                "campaign_type": campaign_type,
                "target_segment": audience.get("segment"),
                "content_version": "1.0"
            }
            
            return content_result
            
        except (json.JSONDecodeError, Exception):
            # Contenido simple como fallback
            return self._generate_simple_content(communication_request, channel_strategy)
    
    def _generate_simple_content(self, communication_request: Dict[str, Any], channel_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera contenido simple como fallback.
        """
        campaign_type = communication_request.get("campaign_type", "nurturing")
        primary_channels = channel_strategy.get("primary_channels", ["email"])
        
        # Obtener template base
        if campaign_type in self.message_templates:
            base_template = self.message_templates[campaign_type]
        else:
            base_template = self.message_templates["follow_up"]
        
        content_variations = {}
        
        for channel in primary_channels:
            if channel in base_template.get("channels", ["email"]):
                content_variations[channel] = {
                    "subject_lines": [base_template["subject"]],
                    "messages": [base_template["content"]],
                    "call_to_action": "¡Contáctanos para más información!",
                    "personalization_tags": ["{user_name}", "{company_name}"]
                }
        
        return {
            "content_variations": content_variations,
            "ab_testing_plan": {
                "variables_to_test": ["subject_line", "call_to_action"],
                "test_duration": "7_days",
                "success_criteria": "open_rate_improvement"
            },
            "personalization_strategy": {
                "dynamic_content": ["user_name", "company_name"],
                "segmentation_rules": ["segment_based_content"]
            }
        }
    
    async def _create_communication_schedule(
        self, 
        communication_request: Dict[str, Any],
        channel_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea un calendario de comunicación optimizado.
        """
        timeline = communication_request.get("timeline", "medium_term")
        priority = communication_request.get("message_priority", "medium")
        campaign_type = communication_request.get("campaign_type", "nurturing")
        
        schedule = {
            "execution_plan": [],
            "frequency_rules": {},
            "optimal_timing": {},
            "follow_up_sequence": []
        }
        
        # Determinar secuencia basada en prioridad y tipo
        if priority == "urgent":
            schedule["execution_plan"] = [
                {"time": "immediate", "channels": ["sms", "whatsapp"], "action": "send_alert"},
                {"time": "+15_minutes", "channels": ["email"], "action": "send_detailed_message"},
                {"time": "+1_hour", "channels": ["phone"], "action": "follow_up_call"}
            ]
        elif campaign_type == "onboarding":
            schedule["execution_plan"] = [
                {"time": "immediate", "channels": ["email"], "action": "welcome_message"},
                {"time": "+1_day", "channels": ["whatsapp"], "action": "intro_guide"},
                {"time": "+3_days", "channels": ["email"], "action": "feature_highlight"},
                {"time": "+1_week", "channels": ["sms"], "action": "check_in_message"},
                {"time": "+2_weeks", "channels": ["email"], "action": "success_stories"}
            ]
        elif campaign_type == "nurturing":
            schedule["execution_plan"] = [
                {"time": "day_1", "channels": ["email"], "action": "educational_content"},
                {"time": "day_7", "channels": ["whatsapp"], "action": "value_proposition"},
                {"time": "day_14", "channels": ["email"], "action": "case_study"},
                {"time": "day_21", "channels": ["sms"], "action": "special_offer"},
                {"time": "day_30", "channels": ["email"], "action": "consultation_invite"}
            ]
        else:
            # Secuencia estándar
            schedule["execution_plan"] = [
                {"time": "immediate", "channels": ["email"], "action": "primary_message"},
                {"time": "+3_days", "channels": ["whatsapp"], "action": "follow_up"},
                {"time": "+1_week", "channels": ["sms"], "action": "reminder"}
            ]
        
        # Reglas de frecuencia
        schedule["frequency_rules"] = {
            "max_daily_messages": 2 if priority == "urgent" else 1,
            "min_hours_between_messages": 4 if priority == "urgent" else 8,
            "max_weekly_messages": 7 if priority == "urgent" else 3,
            "respect_user_preferences": True,
            "honor_unsubscribe": True
        }
        
        # Timing óptimo por canal
        schedule["optimal_timing"] = {
            "email": {"best_hours": [9, 10, 14, 16], "best_days": ["tuesday", "wednesday", "thursday"]},
            "sms": {"best_hours": [10, 11, 15, 17], "best_days": ["tuesday", "wednesday", "friday"]},
            "whatsapp": {"best_hours": [9, 12, 16, 19], "best_days": ["monday", "tuesday", "wednesday"]},
            "push": {"best_hours": [8, 12, 18, 20], "best_days": ["all_weekdays"]}
        }
        
        return schedule
    
    async def _define_tracking_metrics(
        self, 
        communication_request: Dict[str, Any],
        channel_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define métricas de seguimiento y KPIs.
        """
        success_metrics = communication_request.get("success_metrics", ["engagement_rate"])
        primary_channels = channel_strategy.get("primary_channels", ["email"])
        
        tracking_metrics = {
            "primary_kpis": {},
            "channel_specific_metrics": {},
            "campaign_metrics": {},
            "business_impact_metrics": {}
        }
        
        # KPIs primarios
        tracking_metrics["primary_kpis"] = {
            "delivery_rate": {"target": 0.95, "threshold": 0.90},
            "open_rate": {"target": 0.25, "threshold": 0.15},
            "click_rate": {"target": 0.05, "threshold": 0.03},
            "conversion_rate": {"target": 0.02, "threshold": 0.01},
            "unsubscribe_rate": {"target": 0.005, "threshold": 0.02}
        }
        
        # Métricas específicas por canal
        for channel in primary_channels:
            if channel == "email":
                tracking_metrics["channel_specific_metrics"][channel] = [
                    "bounce_rate", "spam_rate", "forward_rate", "time_spent_reading"
                ]
            elif channel == "sms":
                tracking_metrics["channel_specific_metrics"][channel] = [
                    "user_response_rate", "opt_out_rate", "message_timing_effectiveness"
                ]
            elif channel == "whatsapp":
                tracking_metrics["channel_specific_metrics"][channel] = [
                    "read_receipt_rate", "response_rate", "media_engagement", "conversation_length"
                ]
            elif channel == "push":
                tracking_metrics["channel_specific_metrics"][channel] = [
                    "notification_opened", "app_open_rate", "action_completion", "permission_grant_rate"
                ]
        
        # Métricas de campaña
        campaign_type = communication_request.get("campaign_type", "nurturing")
        if campaign_type == "onboarding":
            tracking_metrics["campaign_metrics"] = {
                "completion_rate": {"target": 0.70},
                "time_to_first_action": {"target": "24_hours"},
                "feature_adoption_rate": {"target": 0.50}
            }
        elif campaign_type == "nurturing":
            tracking_metrics["campaign_metrics"] = {
                "lead_scoring_improvement": {"target": "+20_points"},
                "sales_qualified_leads": {"target": 0.10},
                "pipeline_progression": {"target": 0.15}
            }
        elif campaign_type == "promotional":
            tracking_metrics["campaign_metrics"] = {
                "promotional_conversion_rate": {"target": 0.08},
                "revenue_per_message": {"target": "$5"},
                "discount_code_usage": {"target": 0.30}
            }
        
        # Métricas de impacto en el negocio
        tracking_metrics["business_impact_metrics"] = {
            "cost_per_acquisition": {"target": "$50", "threshold": "$100"},
            "customer_lifetime_value": {"target": "$500", "threshold": "$200"},
            "return_on_ad_spend": {"target": 3.0, "threshold": 2.0},
            "revenue_attribution": {"target": "trackable", "method": "utm_tracking"}
        }
        
        return tracking_metrics
    
    def get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prompt del sistema para el agente de comunicación.
        """
        return f"""
        Eres el AGENTE DE COMUNICACIÓN de {EMPRESA_NOMBRE}, especialista en estrategias de comunicación multicanal.

        ACERCA DE NOSOTROS: {EMPRESA_DESCRIPCION}

        TU MISIÓN:
        - Diseñar estrategias de comunicación efectivas y personalizadas
        - Optimizar el mix de canales para máximo impacto
        - Crear contenido persuasivo adaptado a cada canal
        - Planificar calendarios de comunicación inteligentes
        - Maximizar engagement y conversiones a través de comunicación estratégica

        CONTEXTO ACTUAL: {context or "Nueva estrategia de comunicación"}

        CANALES DISPONIBLES:
        {', '.join(self.communication_channels.keys())}

        TIPOS DE CAMPAÑA QUE MANEJAS:
        {', '.join([ct.value for ct in CampaignType])}

        PRINCIPIOS DE COMUNICACIÓN:
        1. Personalización - Adapta mensaje y canal al usuario específico
        2. Timing - Comunica en el momento óptimo para cada canal
        3. Relevancia - Asegura que cada mensaje agregue valor
        4. Consistencia - Mantén coherencia de marca en todos los canales
        5. Medición - Trackea y optimiza basado en métricas
        6. Respeto - Honra preferencias y límites del usuario

        ESTRATEGIAS POR SEGMENTO:
        - Enterprise: {self.segment_strategies['enterprise']['content_focus']}
        - SME: {self.segment_strategies['sme']['content_focus']}
        - Startup: {self.segment_strategies['startup']['content_focus']}
        - Individual: {self.segment_strategies['individual']['content_focus']}

        METODOLOGÍA:
        - Analiza objetivos y audiencia de comunicación
        - Determina mix óptimo de canales 
        - Crea contenido personalizado por canal
        - Planifica calendario de ejecución
        - Define métricas y KPIs de seguimiento

        ¡Convierte cada comunicación en una oportunidad de conexión y conversión!
        """
    
    def get_capabilities(self) -> List[str]:
        """Capacidades del agente de comunicación"""
        return [
            "Estrategia multicanal de comunicación",
            "Personalización de contenido por segmento",
            "Optimización de timing y frecuencia",
            "Creación de campañas automatizadas",
            "A/B testing de mensajes",
            "Análisis de performance por canal",
            "Planificación de calendarios editoriales",
            "Gestión de preferencias de usuario",
            "Integración con CRM y marketing automation",
            "Cumplimiento de regulaciones de comunicación"
        ]
    
    async def get_communication_dashboard(self, session_id: str) -> Dict[str, Any]:
        """
        Genera un dashboard de comunicación personalizado.
        """
        return {
            "session_id": session_id,
            "agent": self.agent_name,
            "available_channels": list(self.communication_channels.keys()),
            "campaign_types": [ct.value for ct in CampaignType],
            "segment_strategies": list(self.segment_strategies.keys()),
            "message_templates": list(self.message_templates.keys()),
            "active": self.active,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_campaign(
        self, 
        campaign_name: str,
        campaign_type: str,
        target_segment: str,
        channels: List[str],
        timeline: str
    ) -> Dict[str, Any]:
        """
        Crea una nueva campaña de comunicación.
        """
        campaign_data = {
            "campaign_id": f"camp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "name": campaign_name,
            "type": campaign_type,
            "target_segment": target_segment,
            "channels": channels,
            "timeline": timeline,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "estimated_reach": sum(self.communication_channels.get(ch, {}).get("engagement_rate", 0.1) * 100 for ch in channels)
        }
        
        return {
            "success": True,
            "campaign": campaign_data,
            "next_steps": [
                "Define content for each channel",
                "Set up tracking and analytics",
                "Schedule campaign execution",
                "Prepare A/B testing variants"
            ]
        }
    
    async def generate_cotizacion(
        self,
        lead_data: Dict[str, Any],
        servicio_solicitado: str,
        detalles_adicionales: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera una cotización personalizada con IA para un lead.
        
        Args:
            lead_data: Datos del lead (nombre, empresa, email, etc.)
            servicio_solicitado: Tipo de servicio que solicita el lead
            detalles_adicionales: Contexto adicional sobre los requerimientos
            
        Returns:
            Dict con la cotización generada y datos estructurados
        """
        try:
            # Construir prompt para generar cotización con IA
            cotizacion_prompt = f"""
            Eres un especialista en ventas y elaboración de propuestas comerciales para {EMPRESA_NOMBRE}.
            
            INFORMACIÓN DEL CLIENTE:
            - Nombre: {lead_data.get('nombre', 'Cliente')}
            - Empresa: {lead_data.get('empresa', 'N/A')}
            - Cargo: {lead_data.get('cargo', 'N/A')}
            - Email: {lead_data.get('email', 'N/A')}
            - Presupuesto estimado: {lead_data.get('presupuesto', 'No especificado')}
            - Timeline: {lead_data.get('timeline', 'No especificado')}
            
            SERVICIO SOLICITADO: {servicio_solicitado}
            
            DETALLES ADICIONALES: {detalles_adicionales or 'Ninguno especificado'}
            
            CONTEXTO DE LA EMPRESA:
            - Nombre: {EMPRESA_NOMBRE}
            - Descripción: {EMPRESA_DESCRIPCION}
            
            TAREA: Genera una cotización profesional y personalizada que incluya:
            
            1. TÍTULO: Un título atractivo para la propuesta
            2. DESCRIPCIÓN: Una descripción del entendimiento de la necesidad del cliente (2-3 párrafos)
            3. ITEMS: Lista de 3-5 items/entregables con:
               - Nombre del entregable
               - Descripción detallada
               - Precio unitario estimado (realista para el mercado)
            4. PLAN_NOMBRE: Nombre del plan propuesto
            5. ALCANCE: Descripción del alcance completo del servicio
            6. FASES: 3-4 fases del proyecto con nombre, descripción y duración
            7. TIEMPO_TOTAL: Duración total estimada del proyecto
            8. FORMA_PAGO: Sugerencia de forma de pago (50% inicio, 50% entrega, o similar)
            9. NOTAS: Notas adicionales o beneficios especiales
            
            Responde ÚNICAMENTE en formato JSON válido con esta estructura:
            {{
                "titulo": "Título de la propuesta",
                "descripcion_personalizada": "Texto del entendimiento...",
                "plan_nombre": "Nombre del plan",
                "descripcion_alcance": "Descripción del alcance completo",
                "items": [
                    {{
                        "nombre": "Entregable 1",
                        "descripcion": "Descripción detallada",
                        "cantidad": 1,
                        "precio_unitario": 1500.00
                    }}
                ],
                "fases": [
                    {{
                        "nombre": "Fase 1",
                        "descripcion": "Descripción de la fase",
                        "duracion": "2 semanas"
                    }}
                ],
                "tiempo_total": "6-8 semanas",
                "forma_pago": "50% al inicio, 50% a la entrega",
                "notas": "Notas adicionales o beneficios",
                "descuento_sugerido": 0
            }}
            
            Sé profesional, persuasivo y asegúrate de que los precios sean competitivos y realistas.
            """
            
            # Generar cotización con IA
            response = await self.generate_response(
                cotizacion_prompt,
                session_id=f"cotizacion_{lead_data.get('id', 'temp')}",
                context={"lead": lead_data, "servicio": servicio_solicitado}
            )
            
            if not response.get("success"):
                raise Exception("Error al generar contenido con IA")
            
            # Parsear respuesta JSON
            import json
            try:
                cotizacion_ia = json.loads(response["response"])
            except json.JSONDecodeError:
                # Si no es JSON válido, usar valores por defecto
                cotizacion_ia = {
                    "titulo": f"Propuesta de {servicio_solicitado}",
                    "descripcion_personalizada": f"Propuesta personalizada para {lead_data.get('nombre', 'cliente')}",
                    "plan_nombre": "Plan Profesional",
                    "descripcion_alcance": "Desarrollo completo del servicio solicitado",
                    "items": [
                        {
                            "nombre": servicio_solicitado,
                            "descripcion": "Implementación completa",
                            "cantidad": 1,
                            "precio_unitario": 5000.00
                        }
                    ],
                    "fases": [
                        {"nombre": "Planeación", "descripcion": "Análisis de requerimientos", "duracion": "1 semana"},
                        {"nombre": "Desarrollo", "descripcion": "Implementación", "duracion": "4 semanas"},
                        {"nombre": "Entrega", "descripcion": "Capacitación y despliegue", "duracion": "1 semana"}
                    ],
                    "tiempo_total": "6 semanas",
                    "forma_pago": "50% al inicio, 50% a la entrega",
                    "notas": "Incluye soporte por 30 días",
                    "descuento_sugerido": 0
                }
            
            # Calcular totales
            subtotal = sum(item.get("precio_unitario", 0) * item.get("cantidad", 1) 
                          for item in cotizacion_ia.get("items", []))
            descuento = cotizacion_ia.get("descuento_sugerido", 0)
            total = subtotal * (1 - descuento / 100)
            
            # Estructurar datos completos de cotización
            from datetime import datetime, timedelta
            
            cotizacion_data = {
                "lead_id": lead_data.get("id"),
                "titulo": cotizacion_ia.get("titulo"),
                "descripcion": cotizacion_ia.get("descripcion_personalizada"),
                "tipo": "automatizacion",  # Mapear según servicio
                "items": [
                    {
                        "descripcion": item.get("nombre"),
                        "cantidad": item.get("cantidad", 1),
                        "precio_unitario": item.get("precio_unitario", 0),
                        "descuento": 0
                    }
                    for item in cotizacion_ia.get("items", [])
                ],
                "subtotal": subtotal,
                "descuento_general": descuento,
                "impuestos": 0,
                "total": total,
                "moneda": "USD",
                "validez_dias": 30,
                "status": "borrador",
                "notas": cotizacion_ia.get("notas"),
                "terminos_condiciones": "Términos y condiciones estándar de ORBITA",
                "generada_por_ia": True,
                "agente_generador": self.agent_name,
                # Datos adicionales para la plantilla
                "plan_nombre": cotizacion_ia.get("plan_nombre"),
                "descripcion_alcance": cotizacion_ia.get("descripcion_alcance"),
                "fases": cotizacion_ia.get("fases", []),
                "tiempo_total": cotizacion_ia.get("tiempo_total"),
                "forma_pago": cotizacion_ia.get("forma_pago"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "cotizacion": cotizacion_data,
                "agent": self.agent_name,
                "generada_con_ia": True,
                "lead_nombre": lead_data.get("nombre"),
                "servicio": servicio_solicitado,
                "total_estimado": total,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self._handle_error("generate_cotizacion_error", str(e), f"lead_{lead_data.get('id')}")
            return {
                "success": False,
                "error": f"Error generando cotización: {str(e)}",
                "agent": self.agent_name,
                "fallback_message": "Lo siento, hubo un problema generando la cotización. Un ejecutivo te contactará pronto."
            }