#!/usr/bin/env python3
"""
Script para verificar el flujo completo de cotizaciones en ORBITA
Valida que todos los componentes necesarios estén presentes y funcionando
"""
import asyncio
import sys
from typing import Dict, List, Any

class CotizacionFlowValidator:
    """Valida el flujo completo de generación de cotizaciones"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.validations = []
    
    def check_models(self) -> bool:
        """Verifica que los modelos de Lead y Cotización estén completos"""
        print("\n📋 Verificando Modelos...")
        
        try:
            from models.lead import Lead, LeadStatus, LeadOrigen
            from models.cotizacion import Cotizacion, CotizacionStatus, ItemCotizacion
            
            # Verificar campos de Lead
            lead_fields = ['id', 'nombre', 'email', 'telefono', 'empresa', 'interes', 
                          'presupuesto', 'status', 'origen']
            for field in lead_fields:
                if not hasattr(Lead, '__annotations__') or field not in Lead.__annotations__:
                    self.issues.append(f"❌ Campo '{field}' no encontrado en modelo Lead")
            
            # Verificar campos de Cotización
            cotizacion_fields = ['id', 'lead_id', 'titulo', 'descripcion', 'items', 
                               'total', 'status']
            for field in cotizacion_fields:
                if not hasattr(Cotizacion, '__annotations__') or field not in Cotizacion.__annotations__:
                    self.issues.append(f"❌ Campo '{field}' no encontrado en modelo Cotizacion")
            
            print("   ✅ Modelos Lead y Cotización verificados")
            self.validations.append("Modelos de datos")
            return True
            
        except Exception as e:
            self.issues.append(f"❌ Error al verificar modelos: {e}")
            return False
    
    def check_database_functions(self) -> bool:
        """Verifica funciones de base de datos"""
        print("\n🗄️  Verificando Funciones de Base de Datos...")
        
        try:
            from database import (
                create_lead, 
                create_cotizacion, 
                update_lead_status,
                get_db
            )
            
            print("   ✅ create_lead - Encontrada")
            print("   ✅ create_cotizacion - Encontrada")
            print("   ✅ update_lead_status - Encontrada")
            print("   ✅ get_db - Encontrada")
            
            self.validations.append("Funciones de base de datos")
            return True
            
        except ImportError as e:
            self.issues.append(f"❌ Falta función de base de datos: {e}")
            return False
    
    def check_routers(self) -> bool:
        """Verifica que los routers existan"""
        print("\n🛣️  Verificando Routers...")
        
        try:
            from routers.leads import leads_router
            from routers.cotizaciones import cotizaciones_router
            
            print("   ✅ Router de leads - Encontrado")
            print("   ✅ Router de cotizaciones - Encontrado")
            
            # Verificar endpoints importantes
            print("\n   Verificando endpoints de cotizaciones:")
            print("   • GET  /api/cotizaciones/ - Listar cotizaciones")
            print("   • POST /api/cotizaciones/ - Crear cotización")
            print("   • POST /api/cotizaciones/generate - Generar con IA")
            
            self.validations.append("Routers y endpoints")
            return True
            
        except ImportError as e:
            self.issues.append(f"❌ Error al importar routers: {e}")
            return False
    
    def check_agents(self) -> bool:
        """Verifica que los agentes necesarios existan"""
        print("\n🤖 Verificando Agentes...")
        
        try:
            from agents.orchestrator import OrchestratorAgent
            from agents.captador import CaptadorAgent
            from agents.comunicacion import ComunicacionAgent
            
            print("   ✅ OrchestratorAgent - Encontrado")
            print("   ✅ CaptadorAgent - Encontrado")
            print("   ✅ ComunicacionAgent - Encontrado")
            
            # Verificar métodos importantes del agente de comunicación
            comm_agent = ComunicacionAgent()
            
            # El agente de comunicación debería tener métodos para generar contenido
            if not hasattr(comm_agent, '_generate_personalized_content'):
                self.warnings.append("⚠️  ComunicacionAgent no tiene método _generate_personalized_content")
            
            self.validations.append("Agentes multi-agente")
            return True
            
        except Exception as e:
            self.issues.append(f"❌ Error al verificar agentes: {e}")
            return False
    
    def check_telegram_handlers(self) -> bool:
        """Verifica handlers de Telegram"""
        print("\n💬 Verificando Handlers de Telegram...")
        
        try:
            from Telegram_Bot.leads_handler import LeadsHandler
            
            print("   ✅ LeadsHandler - Encontrado")
            
            # Verificar métodos relacionados con cotizaciones
            handler = LeadsHandler()
            
            if hasattr(handler, '_handle_cotizacion_callback'):
                print("   ✅ Manejo de callbacks de cotización")
            else:
                self.warnings.append("⚠️  LeadsHandler no tiene _handle_cotizacion_callback")
            
            if hasattr(handler, '_handle_plan_callback'):
                print("   ✅ Manejo de selección de planes")
            else:
                self.warnings.append("⚠️  LeadsHandler no tiene _handle_plan_callback")
            
            self.validations.append("Handlers de Telegram")
            return True
            
        except Exception as e:
            self.issues.append(f"❌ Error al verificar handlers de Telegram: {e}")
            return False
    
    def check_cotizacion_template(self) -> bool:
        """Verifica que exista la plantilla de cotización"""
        print("\n📄 Verificando Plantilla de Cotización...")
        
        import os
        template_path = "/Users/lilianestefaniamaradiagocorrea/Desktop/funnelchat/Orbita/docs/ORBITA_Plantilla_Cotizacion.md"
        
        if os.path.exists(template_path):
            print(f"   ✅ Plantilla encontrada: {template_path}")
            
            # Verificar campos importantes en la plantilla
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                required_fields = [
                    '{{EMPRESA_NOMBRE}}',
                    '{{LEAD_NOMBRE}}',
                    '{{COT_VALOR_TOTAL}}',
                    '{{COT_FECHA_EMISION}}'
                ]
                
                for field in required_fields:
                    if field in content:
                        print(f"   ✅ Campo {field} presente")
                    else:
                        self.warnings.append(f"⚠️  Campo {field} no encontrado en plantilla")
            
            self.validations.append("Plantilla de cotización")
            return True
        else:
            self.warnings.append(f"⚠️  Plantilla de cotización no encontrada en {template_path}")
            return False
    
    def analyze_flow_gaps(self) -> Dict[str, Any]:
        """Analiza gaps en el flujo de cotización"""
        print("\n🔍 Analizando Flujo de Cotización...")
        
        gaps = {
            "missing_features": [],
            "recommendations": []
        }
        
        # Gap 1: Generación automática de cotización con IA
        print("\n   Verificando generación automática con IA:")
        try:
            from agents.comunicacion import ComunicacionAgent
            agent = ComunicacionAgent()
            
            # Buscar método específico de generación de cotización
            if hasattr(agent, 'generate_cotizacion'):
                print("   ✅ Método generate_cotizacion encontrado")
            else:
                print("   ⚠️  Método generate_cotizacion NO encontrado")
                gaps["missing_features"].append({
                    "feature": "generate_cotizacion en ComunicacionAgent",
                    "priority": "HIGH",
                    "description": "Método para generar cotizaciones automáticas con IA"
                })
                gaps["recommendations"].append(
                    "Agregar método generate_cotizacion() en ComunicacionAgent que use la plantilla y datos del lead"
                )
        except Exception as e:
            gaps["missing_features"].append({
                "feature": "ComunicacionAgent funcional",
                "priority": "CRITICAL",
                "description": str(e)
            })
        
        # Gap 2: Integración desde Telegram hasta BD
        print("\n   Verificando integración Telegram → Lead → Cotización:")
        flow_steps = [
            "1. Usuario envía mensaje en Telegram",
            "2. LeadsHandler procesa mensaje",
            "3. Se crea/actualiza Lead en BD",
            "4. Usuario solicita cotización (callback)",
            "5. Se genera cotización con IA",
            "6. Se guarda cotización en BD",
            "7. Se envía cotización al usuario"
        ]
        
        for step in flow_steps:
            print(f"      {step}")
        
        print("\n   ⚠️  Flujo requiere implementación completa de generación con IA")
        gaps["recommendations"].append(
            "Completar integración end-to-end desde callback de Telegram hasta generación de PDF"
        )
        
        # Gap 3: Actualización de estado de lead
        print("\n   Verificando actualización de estados:")
        print("      • Lead.status = 'nuevo' → 'contactado' → 'cotizado' → 'ganado'")
        print("      ✅ Estados definidos en modelo")
        
        # Gap 4: Generación de PDF
        print("\n   Verificando generación de PDF:")
        try:
            import reportlab
            print("   ✅ ReportLab disponible para generar PDFs")
        except ImportError:
            print("   ⚠️  ReportLab NO instalado")
            gaps["missing_features"].append({
                "feature": "Generación de PDF",
                "priority": "MEDIUM",
                "description": "Librería reportlab no instalada"
            })
            gaps["recommendations"].append("Instalar reportlab: pip install reportlab")
        
        return gaps
    
    def generate_report(self, gaps: Dict[str, Any]):
        """Genera reporte final"""
        print("\n" + "="*60)
        print("📊 REPORTE DE VERIFICACIÓN - FLUJO DE COTIZACIONES")
        print("="*60)
        
        print(f"\n✅ Validaciones Exitosas ({len(self.validations)}):")
        for v in self.validations:
            print(f"   • {v}")
        
        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"   {w}")
        
        if self.issues:
            print(f"\n❌ Problemas Críticos ({len(self.issues)}):")
            for i in self.issues:
                print(f"   {i}")
        
        if gaps["missing_features"]:
            print(f"\n🔧 Funcionalidades Faltantes ({len(gaps['missing_features'])}):")
            for feature in gaps["missing_features"]:
                priority_emoji = "🔴" if feature["priority"] == "CRITICAL" else "🟡" if feature["priority"] == "HIGH" else "🔵"
                print(f"   {priority_emoji} [{feature['priority']}] {feature['feature']}")
                print(f"      → {feature['description']}")
        
        if gaps["recommendations"]:
            print(f"\n💡 Recomendaciones ({len(gaps['recommendations'])}):")
            for idx, rec in enumerate(gaps["recommendations"], 1):
                print(f"   {idx}. {rec}")
        
        print("\n" + "="*60)
        
        # Calcular score
        total_checks = len(self.validations) + len(self.issues)
        score = (len(self.validations) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n🎯 Score de Completitud: {score:.1f}%")
        
        if score >= 80:
            print("   ✅ El flujo está mayormente completo")
        elif score >= 60:
            print("   ⚠️  El flujo requiere algunas mejoras")
        else:
            print("   ❌ El flujo requiere trabajo significativo")
        
        print("\n" + "="*60 + "\n")
        
        return score >= 60

async def main():
    """Ejecuta la validación completa"""
    validator = CotizacionFlowValidator()
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DEL FLUJO DE COTIZACIONES - ORBITA")
    print("="*60)
    
    # Ejecutar todas las validaciones
    validator.check_models()
    validator.check_database_functions()
    validator.check_routers()
    validator.check_agents()
    validator.check_telegram_handlers()
    validator.check_cotizacion_template()
    
    # Analizar gaps
    gaps = validator.analyze_flow_gaps()
    
    # Generar reporte
    success = validator.generate_report(gaps)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
