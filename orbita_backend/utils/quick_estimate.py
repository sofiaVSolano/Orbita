# Utilidad para generar estimados rápidos de precio
# Detecta el servicio solicitado y genera un estimado al instante

import json
import re
import unicodedata
from typing import Dict, Optional, Tuple
from datetime import datetime

class QuickEstimateGenerator:
    """Genera estimados rápidos de precio based on user request."""
    
    # Servicios y precios estimados base
    SERVICIOS = {
        "sitio_web": {
            "nombre": "Desarrollo de Sitio Web",
            "precio_base": 2000,
            "descripcion": "Página web profesional con diseño responsive y mantenimiento"
        },
        "app_movil": {
            "nombre": "Aplicación Móvil",
            "precio_base": 5000,
            "descripcion": "Desarrollo de app iOS/Android con funcionalidades personalizadas"
        },
        "ecommerce": {
            "nombre": "Tienda Online",
            "precio_base": 4000,
            "descripcion": "Plataforma de comercio electrónico con pasarela de pago"
        },
        "marketing_digital": {
            "nombre": "Estrategia Marketing Digital",
            "precio_base": 1500,
            "descripcion": "Gestión de redes sociales y campañas digitales"
        },
        "automatizacion_ia": {
            "nombre": "Automatización con IA",
            "precio_base": 3000,
            "descripcion": "Chatbots, procesamiento de datos, y automatización inteligente"
        },
        "consultoria": {
            "nombre": "Consultoría Tecnológica",
            "precio_base": 1000,
            "descripcion": "Asesoría y análisis de necesidades tecnológicas"
        },
        "mantenimiento": {
            "nombre": "Mantenimiento y Soporte",
            "precio_base": 500,
            "descripcion": "Soporte técnico, actualizaciones y mantenimiento periódico"
        },
        "seo": {
            "nombre": "SEO y Posicionamiento",
            "precio_base": 1200,
            "descripcion": "Optimización para buscadores y posicionamiento orgánico"
        }
    }
    
    # Palabras clave para detectar servicios
    KEYWORDS = {
        "sitio_web": ["sitio web", "página web", "website", "landing page", "portal web"],
        "app_movil": ["app", "aplicación", "movil", "mobile", "ios", "android", "app móvil", "aplicativo"],
        "ecommerce": ["tienda online", "ecommerce", "comercio electrónico", "tienda virtual", "vender online"],
        "marketing_digital": ["marketing", "redes sociales", "instagram", "facebook", "publicidad digital", "campañas", "social media"],
        "automatizacion_ia": ["chatbot", "automatización", "ia", "inteligencia artificial", "bot", "automatizar"],
        "consultoria": ["consultoría", "consultor", "asesoría", "diagnóstico", "evaluación", "análisis"],
        "mantenimiento": ["mantenimiento", "soporte técnico", "mantencion", "servidor", "hosting"],
        "seo": ["seo", "posicionamiento", "buscador", "organico", "google", "ranking"]
    }
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza el texto eliminando acentos y convirtiendo a minúsculas."""
        # Convertir a minúsculas
        texto = texto.lower()
        # Usar NFD para descomponer acentos en caracteres base + combinaciones
        texto_nfd = unicodedata.normalize('NFD', texto)
        # Eliminar los acentos (caracteres de combinación)
        sin_acentos = ''.join(char for char in texto_nfd if unicodedata.category(char) != 'Mn')
        return sin_acentos
    
    def detectar_servicio(self, mensaje: str) -> Tuple[Optional[str], float]:
        """
        Detecta qué servicio está pidiendo el usuario usando búsqueda de palabras clave.
        
        Returns:
            (tipo_servicio, confianza)
        """
        # Normalizar el mensaje para evitar problemas con acentos
        mensaje_normalizado = self._normalizar_texto(mensaje)
        
        # Búsqueda por keywords
        mejores_matches = []
        
        for servicio, keywords in self.KEYWORDS.items():
            # Normalizar cada keyword también
            keywords_normalizados = [self._normalizar_texto(kw) for kw in keywords]
            num_matches = sum(1 for kw in keywords_normalizados if kw in mensaje_normalizado)
            
            if num_matches > 0:
                # Calcular confianza basada en matches
                # 1 match = 0.5 (50%), 2 matches = 0.8 (80%), etc.
                confianza_base = min(0.5 + (num_matches - 1) * 0.25, 1.0)
                mejores_matches.append((servicio, confianza_base, num_matches))
        
        if mejores_matches:
            # Ordenar por confianza (descendente)
            mejores_matches.sort(key=lambda x: x[1], reverse=True)
            servicio_detectado, confianza, _ = mejores_matches[0]
            
            # Retornar si confianza es suficiente
            if confianza >= 0.5:
                return servicio_detectado, confianza
        
        return None, 0.0
    
    def generar_estimado(self, 
                        servicio: str, 
                        detalles_adicionales: str = "",
                        nivel_complejidad: str = "standard") -> Dict:
        """
        Genera un estimado de precio para el servicio detectado.
        
        Args:
            servicio: Tipo de servicio (ver SERVICIOS)
            detalles_adicionales: Descripción adicional de lo que necesita
            nivel_complejidad: "simple", "standard", "complejo"
        """
        if servicio not in self.SERVICIOS:
            return None
        
        info_servicio = self.SERVICIOS[servicio]
        precio_base = info_servicio["precio_base"]
        
        # Ajustar precio por complejidad
        multiplicadores = {
            "simple": 0.7,
            "standard": 1.0,
            "complejo": 1.5
        }
        
        multiplicador = multiplicadores.get(nivel_complejidad, 1.0)
        precio_estimado = int(precio_base * multiplicador)
        
        # Detectar si hay menciones de complejidad adicional
        if detalles_adicionales:
            detalles_lower = detalles_adicionales.lower()
            
            # Palabras que indican mayor complejidad
            palabras_complejas = ["múltiples", "integraciones", "apis", "complejas", "avanzado", "personalizado"]
            if any(palabra in detalles_lower for palabra in palabras_complejas):
                precio_estimado = int(precio_estimado * 1.3)
            
            # Palabras que indican menor complejidad
            palabras_simples = ["básico", "simple", "sencillo", "estándar"]
            if any(palabra in detalles_lower for palabra in palabras_simples):
                precio_estimado = int(precio_estimado * 0.8)
        
        return {
            "servicio": servicio,
            "nombre_servicio": info_servicio["nombre"],
            "descripcion": info_servicio["descripcion"],
            "precio_estimado": precio_estimado,
            "precio_base": precio_base,
            "nivel_complejidad": nivel_complejidad,
            "moneda": "USD",
            "rango_duracion": self._get_rango_duracion(servicio),
            "incluye": self._get_includes(servicio),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_rango_duracion(self, servicio: str) -> str:
        """Retorna el rango estimado de duración del proyecto."""
        duraciones = {
            "sitio_web": "2-4 semanas",
            "app_movil": "6-12 semanas",
            "ecommerce": "4-6 semanas",
            "marketing_digital": "Continuo",
            "automatizacion_ia": "3-6 semanas",
            "consultoria": "1-2 semanas",
            "mantenimiento": "Mensual",
            "seo": "Continuo (3-6 meses para resultados)"
        }
        return duraciones.get(servicio, "A definir")
    
    def _get_includes(self, servicio: str) -> list:
        """Retorna qué incluye típicamente cada servicio."""
        includes = {
            "sitio_web": [
                "Diseño responsivo",
                "Carrusel de imágenes",
                "Formulario de contacto",
                "Integración SEO basic",
                "1 mes de soporte gratis"
            ],
            "app_movil": [
                "Desarrollo nativo",
                "Diseño UI/UX profesional",
                "1 año de mantenimiento",
                "Publicación en tiendas",
                "Documentación técnica"
            ],
            "ecommerce": [
                "Pasarela de pago",
                "Gestión de inventario",
                "Sistema de carrito",
                "Email marketing integrado",
                "3 meses de soporte"
            ],
            "marketing_digital": [
                "Estrategia mensual",
                "Creación de contenido",
                "Gestión de campañas",
                "Reportes mensuales",
                "Asesoría permanente"
            ],
            "automatizacion_ia": [
                "Chatbot inteligente",
                "Entrenamiento de modelos",
                "Integración con CRM",
                "Dashboard de análisis",
                "Soporte técnico"
            ],
            "consultoria": [
                "Análisis de situación",
                "Propuesta de soluciones",
                "Documento ejecutivo",
                "Recomendaciones",
                "Seguimiento 1 mes"
            ],
            "mantenimiento": [
                "Actualizaciones mensuales",
                "Monitoreo 24/7",
                "Backups automáticos",
                "Soporte técnico",
                "Reportes mensuales"
            ],
            "seo": [
                "Auditoría SEO",
                "Palabras clave",
                "Optimización on-page",
                "Link building",
                "Reportes mensuales"
            ]
        }
        return includes.get(servicio, [])
    
    def formatear_estimado(self, estimado: Dict) -> str:
        """Formatea el estimado en un mensaje amigable."""
        if not estimado:
            return "No pude detectar qué servicio necesitas. ¿Podrías describir más?"
        
        msg = f"""
💰 *ESTIMADO DE PRECIO*

📌 Servicio: {estimado['nombre_servicio']}
📝 Descripción: {estimado['descripcion']}
💵 Precio estimado: ${estimado['precio_estimado']} {estimado['moneda']}
⏱️ Duración: {estimado['rango_duracion']}

*Incluye:*
"""
        for item in estimado['incluye'][:5]:  # Mostrar máximo 5 items
            msg += f"\n✓ {item}"
        
        msg += f"""

_*Nota: Este es un estimado basado en funcionalidades estándar. El precio final puede variar según tus necesidades específicas._

¿Te gustaría más información o agendar una consulta?"""
        
        return msg


# Instancia global
_estimator = None

def get_quick_estimator() -> QuickEstimateGenerator:
    global _estimator
    if _estimator is None:
        _estimator = QuickEstimateGenerator()
    return _estimator
