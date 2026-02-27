"""
Utilidad para renderizar plantillas de cotización con datos reales
[CRITERIO 5] - Cotizaciones automáticas con plantillas personalizables
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import os

class CotizacionRenderer:
    """Renderiza plantillas de cotización con datos reales"""
    
    def __init__(self, template_path: str = None):
        """
        Inicializa el renderizador de plantillas.
        
        Args:
            template_path: Ruta a la plantilla base (opcional)
        """
        self.template_path = template_path or os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "docs", 
            "ORBITA_Plantilla_Cotizacion.md"
        )
    
    def render_cotizacion(
        self,
        cotizacion_data: Dict[str, Any],
        lead_data: Dict[str, Any],
        empresa_data: Dict[str, Any]
    ) -> str:
        """
        Renderiza una cotización completa en formato Markdown.
        
        Args:
            cotizacion_data: Datos de la cotización
            lead_data: Datos del lead
            empresa_data: Datos de la empresa
            
        Returns:
            String con el Markdown renderizado
        """
        
        # Si existe plantilla, cargarla y reemplazar campos
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Reemplazar campos de empresa
            template = self._replace_empresa_fields(template, empresa_data)
            
            # Reemplazar campos de lead
            template = self._replace_lead_fields(template, lead_data)
            
            # Reemplazar campos de cotización
            template = self._replace_cotizacion_fields(template, cotizacion_data)
            
            # Limpiar comentarios HTML
            template = self._clean_html_comments(template)
            
            return template
        
        # Si no hay plantilla, generar cotización simple
        return self._generate_simple_cotizacion(cotizacion_data, lead_data, empresa_data)
    
    def _replace_empresa_fields(self, template: str, empresa_data: Dict[str, Any]) -> str:
        """Reemplaza campos de empresa en la plantilla"""
        replacements = {
            "{{EMPRESA_NOMBRE}}": empresa_data.get("nombre", "ORBITA"),
            "{{EMPRESA_SLOGAN}}": empresa_data.get("slogan", "Soluciones Inteligentes"),
            "{{EMPRESA_CIUDAD}}": empresa_data.get("ciudad", "Ciudad"),
            "{{EMPRESA_PAIS}}": empresa_data.get("pais", "País"),
            "{{EMPRESA_EMAIL}}": empresa_data.get("email", "contacto@orbita.ai"),
            "{{EMPRESA_TELEFONO}}": empresa_data.get("telefono", "+1 234 567 890"),
            "{{EMPRESA_SITIO_WEB}}": empresa_data.get("sitio_web", "www.orbita.ai"),
            "{{EMPRESA_ASESOR_NOMBRE}}": empresa_data.get("asesor_nombre", "Equipo ORBITA"),
            "{{EMPRESA_PROPUESTA_VALOR}}": empresa_data.get("propuesta_valor", 
                "Soluciones de IA innovadoras y confiables"),
            "{{EMPRESA_TERMINOS_CONDICIONES}}": empresa_data.get("terminos_condiciones",
                "Esta propuesta es válida por 30 días desde su emisión.")
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        return template
    
    def _replace_lead_fields(self, template: str, lead_data: Dict[str, Any]) -> str:
        """Reemplaza campos de lead en la plantilla"""
        replacements = {
            "{{LEAD_NOMBRE}}": lead_data.get("nombre", "Cliente"),
            "{{LEAD_EMPRESA}}": lead_data.get("empresa", "Empresa"),
            "{{LEAD_CARGO}}": lead_data.get("cargo", ""),
            "{{LEAD_EMAIL}}": lead_data.get("email", ""),
            "{{LEAD_TELEFONO}}": lead_data.get("telefono", ""),
            "{{LEAD_SERVICIO_INTERES}}": lead_data.get("interes", "servicios digitales"),
            "{{LEAD_PRESUPUESTO_ESTIMADO}}": f"${lead_data.get('presupuesto', 'No especificado')}"
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        return template
    
    def _replace_cotizacion_fields(self, template: str, cotizacion_data: Dict[str, Any]) -> str:
        """Reemplaza campos de cotización en la plantilla"""
        
        # Generar código de cotización si no existe
        codigo = cotizacion_data.get("numero_cotizacion") or \
                f"COT-{datetime.now().strftime('%Y%m%d')}-{cotizacion_data.get('id', '000')}"
        
        # Fechas
        fecha_emision = cotizacion_data.get("created_at", datetime.now().isoformat())
        if isinstance(fecha_emision, str):
            try:
                fecha_emision = datetime.fromisoformat(fecha_emision.replace('Z', '+00:00'))
            except:
                fecha_emision = datetime.now()
        
        validez_dias = cotizacion_data.get("validez_dias", 30)
        fecha_vencimiento = fecha_emision + timedelta(days=validez_dias)
        
        replacements = {
            "{{COT_CODIGO}}": codigo,
            "{{COT_FECHA_EMISION}}": fecha_emision.strftime("%d/%m/%Y"),
            "{{COT_FECHA_VENCIMIENTO}}": fecha_vencimiento.strftime("%d/%m/%Y"),
            "{{COT_CANAL_ORIGEN}}": cotizacion_data.get("origen", "Telegram"),
            "{{COT_INTRODUCCION_PERSONALIZADA}}": cotizacion_data.get("descripcion", 
                "Gracias por su interés en nuestros servicios."),
            "{{COT_PLAN_NOMBRE}}": cotizacion_data.get("plan_nombre", "Plan Profesional"),
            "{{COT_DESCRIPCION_PLAN}}": cotizacion_data.get("descripcion_alcance", 
                "Plan personalizado para sus necesidades."),
            "{{COT_DESCRIPCION_ALCANCE}}": cotizacion_data.get("descripcion_alcance", ""),
            "{{COT_SUBTOTAL}}": f"{cotizacion_data.get('subtotal', 0):.2f}",
            "{{COT_DESCUENTO_PORCENTAJE}}": str(cotizacion_data.get("descuento_general", 0)),
            "{{COT_DESCUENTO_VALOR}}": f"{cotizacion_data.get('subtotal', 0) * cotizacion_data.get('descuento_general', 0) / 100:.2f}",
            "{{COT_VALOR_TOTAL}}": f"{cotizacion_data.get('total', 0):.2f}",
            "{{COT_MONEDA}}": cotizacion_data.get("moneda", "USD"),
            "{{COT_FORMA_PAGO}}": cotizacion_data.get("forma_pago", "50% al inicio, 50% a la entrega"),
            "{{COT_TIEMPO_TOTAL}}": cotizacion_data.get("tiempo_total", "6-8 semanas"),
            "{{COT_FECHA_INICIO_ESTIMADA}}": (fecha_emision + timedelta(days=7)).strftime("%d/%m/%Y"),
            "{{COT_VIGENCIA_DIAS}}": str(validez_dias)
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        # Reemplazar items (requiere lógica especial para loops)
        template = self._replace_items(template, cotizacion_data.get("items", []))
        
        # Reemplazar fases
        template = self._replace_fases(template, cotizacion_data.get("fases", []))
        
        return template
    
    def _replace_items(self, template: str, items: List[Dict[str, Any]]) -> str:
        """Reemplaza los items de la cotización"""
        if not items:
            return template
        
        # Construir tabla de items
        items_table = "| # | Entregable | Descripción | Valor |\n|---|---|---|---|\n"
        
        for idx, item in enumerate(items, 1):
            nombre = item.get("descripcion", item.get("nombre", "Item"))
            descripcion = item.get("descripcion_detallada", 
                                  item.get("descripcion", ""))[:50]
            valor = item.get("precio_unitario", 0) * item.get("cantidad", 1)
            items_table += f"| {idx} | {nombre} | {descripcion} | ${valor:.2f} |\n"
        
        # Reemplazar bloque de items
        # Buscar patrón entre comentarios <!-- INICIO BLOQUE REPETIBLE --> y <!-- FIN BLOQUE REPETIBLE -->
        import re
        pattern = r'<!-- INICIO BLOQUE REPETIBLE.*?<!-- FIN BLOQUE REPETIBLE -->'
        template = re.sub(pattern, items_table, template, flags=re.DOTALL)
        
        # También reemplazar items individuales si existen
        for i in range(1, 6):
            if i <= len(items):
                item = items[i-1]
                template = template.replace(f"{{{{ITEM_{i}_NOMBRE}}}}", 
                                          item.get("descripcion", f"Item {i}"))
                template = template.replace(f"{{{{ITEM_{i}_DESCRIPCION}}}}", 
                                          item.get("descripcion", ""))
                template = template.replace(f"{{{{ITEM_{i}_VALOR}}}}", 
                                          f"{item.get('precio_unitario', 0):.2f}")
        
        return template
    
    def _replace_fases(self, template: str, fases: List[Dict[str, Any]]) -> str:
        """Reemplaza las fases del proyecto"""
        if not fases:
            return template
        
        for idx, fase in enumerate(fases, 1):
            template = template.replace(f"{{{{FASE_{idx}_NOMBRE}}}}", 
                                      fase.get("nombre", f"Fase {idx}"))
            template = template.replace(f"{{{{FASE_{idx}_DESCRIPCION}}}}", 
                                      fase.get("descripcion", ""))
            template = template.replace(f"{{{{FASE_{idx}_DURACION}}}}", 
                                      fase.get("duracion", ""))
        
        return template
    
    def _clean_html_comments(self, template: str) -> str:
        """Elimina comentarios HTML de la plantilla"""
        import re
        return re.sub(r'<!--.*?-->', '', template, flags=re.DOTALL)
    
    def _generate_simple_cotizacion(
        self, 
        cotizacion_data: Dict[str, Any],
        lead_data: Dict[str, Any],
        empresa_data: Dict[str, Any]
    ) -> str:
        """Genera una cotización simple sin plantilla"""
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        markdown = f"""# PROPUESTA COMERCIAL
        
**De:** {empresa_data.get('nombre', 'ORBITA')}
**Para:** {lead_data.get('nombre', 'Cliente')}
**Fecha:** {fecha}

---

## Resumen

{cotizacion_data.get('descripcion', 'Propuesta personalizada para sus necesidades.')}

---

## Servicios Incluidos

"""
        
        # Agregar items
        for idx, item in enumerate(cotizacion_data.get("items", []), 1):
            markdown += f"{idx}. **{item.get('descripcion', 'Item')}** - ${item.get('precio_unitario', 0):.2f}\n"
        
        markdown += f"""
---

## Inversión Total

**${cotizacion_data.get('total', 0):.2f} {cotizacion_data.get('moneda', 'USD')}**

Forma de pago: {cotizacion_data.get('forma_pago', '50% inicio, 50% entrega')}

---

*Propuesta válida por {cotizacion_data.get('validez_dias', 30)} días*
"""
        
        return markdown

# Función helper para uso directo
def render_cotizacion_markdown(
    cotizacion_data: Dict[str, Any],
    lead_data: Dict[str, Any],
    empresa_data: Dict[str, Any]
) -> str:
    """
    Helper function para renderizar cotización rápidamente.
    
    Returns:
        String con Markdown renderizado
    """
    renderer = CotizacionRenderer()
    return renderer.render_cotizacion(cotizacion_data, lead_data, empresa_data)
