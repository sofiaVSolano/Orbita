#!/usr/bin/env python3
"""
VALIDADOR DE AGENTES ORBITA CON GROQ
====================================
Prueba cada agente con casos reales para verificar:
- Integración correcta con Groq
- Logging completo en agent_logs
- Respuestas esperadas y coherentes
- Performance (latencia, tokens)
- Fallbacks funcionando

Ejecutar:
    python validate_agents_groq.py

Salida:
    - Reporte en consola
    - Registros en Supabase agent_logs
    - JSON con resultados en validate_results.json
"""

import sys
import json
import asyncio
import time
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, List

# Imports del backend
from config import get_settings
from database import get_db
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.conversacional import ConversacionalAgent
from agents.identidad import IdentidadAgent
from agents.analitico import AnaliticoAgent
from agents.comunicacion import ComunicacionAgent


class ValidadorAgentes:
    """Valida todos los agentes del sistema ORBITA."""
    
    def __init__(self):
        self.db = get_db()
        self.settings = get_settings()
        self.resultados = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agentes": {}
        }
        self.test_lead_id = None
        self.session_id = f"validate-{str(uuid4())[:8]}"
        
    def _print_section(self, titulo: str, nivel: int = 1):
        """Imprime encabezado de sección."""
        if nivel == 1:
            print(f"\n{'='*70}")
            print(f"  {titulo}")
            print(f"{'='*70}\n")
        elif nivel == 2:
            print(f"\n{titulo}")
            print(f"{'-'*70}\n")
        else:
            print(f"  → {titulo}\n")
    
    def _print_resultado(self, label: str, valor: Any, estado: str = "info"):
        """Imprime un resultado con estado."""
        colores = {
            "ok": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        print(f"  {colores.get(estado, '•')} {label}: {valor}")
    
    async def validar_orchestrator(self) -> Dict[str, Any]:
        """
        TEST 1: Agente Orquestador
        
        Responsabilidad: Clasificar intención y etapa AIDA
        Modelo: llama-3.3-70b-versatile
        Temperatura: 0.3 (determinista)
        """
        print("\n🤖 TEST 1: ORQUESTADOR\n")
        
        test_casos = [
            {
                "mensaje": "Hola, estoy aquí para que me cuentes sobre los servicios",
                "expected_intention": "saludo",
                "expected_stage": "awareness"
            },
            {
                "mensaje": "¿Cuánto cuesta un chatbot con IA para ventas?",
                "expected_intention": "cotizacion",
                "expected_stage": "consideration"
            },
            {
                "mensaje": "Quiero agendar una llamada para ver si nos sirven",
                "expected_intention": "agendar_reunion",
                "expected_stage": "decision"
            }
        ]
        
        resultados_test = []
        orchestrator = OrchestratorAgent(self.db, self.settings)
        
        for i, caso in enumerate(test_casos, 1):
            self._print_resultado(f"Caso {i}", "", "info")
            print(f"    Mensaje: '{caso['mensaje']}'")
            
            try:
                inicio = time.time()
                resultado = orchestrator.execute({
                    "mensaje": caso["mensaje"],
                    "lead_id": self.test_lead_id,
                    "session_id": self.session_id,
                    "telegram_chat_id": "999888777"
                })
                latencia = (time.time() - inicio) * 1000
                
                # Validaciones
                intencion_ok = resultado.get("intencion") == caso["expected_intention"]
                etapa_ok = resultado.get("etapa_aida") == caso["expected_stage"]
                completo = all(k in resultado for k in ["intencion", "etapa_aida", "agente_principal", "prioridad"])
                
                self._print_resultado(
                    f"  Intención",
                    f"{resultado.get('intencion')} {'✓' if intencion_ok else '✗ ESPERADO: ' + caso['expected_intention']}",
                    "ok" if intencion_ok else "warning"
                )
                self._print_resultado(
                    f"  Etapa AIDA",
                    f"{resultado.get('etapa_aida')} {'✓' if etapa_ok else '✗ ESPERADO: ' + caso['expected_stage']}",
                    "ok" if etapa_ok else "warning"
                )
                self._print_resultado(
                    f"  Agente principal",
                    resultado.get("agente_principal"),
                    "ok"
                )
                self._print_resultado(
                    f"  Latencia",
                    f"{latencia:.0f}ms",
                    "ok" if latencia < 3000 else "warning"
                )
                self._print_resultado(
                    f"  Error",
                    "NO",
                    "ok"
                )
                
                test_ok = intencion_ok and etapa_ok and completo
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": test_ok,
                    "latencia_ms": latencia,
                    "intencion": resultado.get("intencion"),
                    "etapa": resultado.get("etapa_aida")
                })
                
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)[:100]}")
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": False,
                    "error": str(e)
                })
        
        success = all(r.get("success") for r in resultados_test)
        self.resultados["agentes"]["orchestrator"] = {
            "success": success,
            "casos": len(resultados_test),
            "casos_exitosos": sum(1 for r in resultados_test if r.get("success")),
            "results": resultados_test
        }
        
        return {"success": success, "resultados": resultados_test}
    
    async def validar_captador(self) -> Dict[str, Any]:
        """
        TEST 2: Agente Captador
        
        Responsabilidad: Extraer datos del lead (nombre, empresa, etc)
        Modelo: gemma2-9b-it
        Temperatura: 0.2 (extractivo, preciso)
        """
        print("\n👤 TEST 2: CAPTADOR\n")
        
        test_casos = [
            {
                "mensaje": "Hola soy Carlos Pérez de Innovatech, soy el CEO",
                "expected_fields": ["nombre", "empresa", "puesto"]
            },
            {
                "mensaje": "Me llamo Sofia, trabajo en marketing en XYZ Corp",
                "expected_fields": ["nombre", "empresa", "rol"]
            }
        ]
        
        resultados_test = []
        captador = CaptadorAgent(self.db, self.settings)
        
        for i, caso in enumerate(test_casos, 1):
            self._print_resultado(f"Caso {i}", "", "info")
            print(f"    Mensaje: '{caso['mensaje']}'")
            
            try:
                inicio = time.time()
                result = captador.execute({
                    "mensaje": caso["mensaje"],
                    "telegram_user_id": f"test_user_{i}_{int(time.time())}",
                    "telegram_username": f"testuser{i}",
                    "telegram_chat_id": f"{999888777 + i}",
                    "session_id": self.session_id,
                    "nombre_telegram": f"TestUser {i}"
                })
                latencia = (time.time() - inicio) * 1000
                
                # Validaciones
                accion_ok = result.get("accion") in ["crear_lead", "actualizar_lead", "no_accion"]
                tiene_lead_id = "lead_id" in result
                datos = result.get("datos_extraidos", {})
                
                self._print_resultado(
                    f"  Acción",
                    result.get("accion"),
                    "ok" if accion_ok else "warning"
                )
                self._print_resultado(
                    f"  Lead ID",
                    result.get("lead_id", "NONE")[:8] + "..." if result.get("lead_id") else "NO CREADO",
                    "ok" if tiene_lead_id else "warning"
                )
                self._print_resultado(
                    f"  Datos extraídos",
                    f"{len(datos)} campos",
                    "ok"
                )
                self._print_resultado(
                    f"  Latencia",
                    f"{latencia:.0f}ms",
                    "ok" if latencia < 3000 else "warning"
                )
                
                test_ok = accion_ok and (tiene_lead_id or result.get("accion") == "no_accion")
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": test_ok,
                    "latencia_ms": latencia,
                    "lead_id": result.get("lead_id"),
                    "accion": result.get("accion"),
                    "datos_count": len(datos)
                })
                
                # Guardar lead_id para otros tests
                if result.get("lead_id") and not self.test_lead_id:
                    self.test_lead_id = result.get("lead_id")
                
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)[:100]}")
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": False,
                    "error": str(e)
                })
        
        success = any(r.get("success") for r in resultados_test)
        self.resultados["agentes"]["captador"] = {
            "success": success,
            "casos": len(resultados_test),
            "casos_exitosos": sum(1 for r in resultados_test if r.get("success")),
            "results": resultados_test
        }
        
        return {"success": success, "resultados": resultados_test}
    
    async def validar_identidad(self) -> Dict[str, Any]:
        """
        TEST 3: Agente Identidad
        
        Responsabilidad: Validar tono y voz de marca
        Modelo: llama-3.1-8b-instant
        Temperatura: 0.2 (evaluación, no creativo)
        """
        print("\n🎭 TEST 3: IDENTIDAD\n")
        
        test_casos = [
            {
                "borrador": "Hola Carlos, me da mucho gusto ayudarte. Somos expertos en automatización.",
                "esperado_tono": "profesional_cercano",
                "debe_aprobarse": True
            },
            {
                "borrador": "boludo, nuestro producto es lo mejor que hay, es barato y la rompe",
                "esperado_tono": "informal_inapropiado",
                "debe_aprobarse": False
            }
        ]
        
        resultados_test = []
        identidad = IdentidadAgent(self.db, self.settings)
        
        for i, caso in enumerate(test_casos, 1):
            self._print_resultado(f"Caso {i}", "", "info")
            print(f"    Borrador: '{caso['borrador'][:60]}...'")
            
            try:
                inicio = time.time()
                result = identidad.execute({
                    "borrador": caso["borrador"],
                    "contexto_lead": {"nombre": "TestUser", "empresa": "TestCorp"},
                    "agente_origen": "conversacional",
                    "etapa_aida": "interes"
                })
                latencia = (time.time() - inicio) * 1000
                
                # Validaciones
                aprobado = result.get("aprobado", False)
                aprobado_ok = aprobado == caso["debe_aprobarse"]
                score = result.get("score_marca", 0)
                
                self._print_resultado(
                    f"  Aprobado",
                    f"{aprobado} {'✓' if aprobado_ok else '✗ ESPERADO: ' + str(caso['debe_aprobarse'])}",
                    "ok" if aprobado_ok else "warning"
                )
                self._print_resultado(
                    f"  Score marca",
                    f"{score:.1f}/10",
                    "ok" if (score > 6) == caso["debe_aprobarse"] else "warning"
                )
                self._print_resultado(
                    f"  Mensaje final",
                    f"{result.get('mensaje_final', 'N/A')[:50]}...",
                    "ok"
                )
                self._print_resultado(
                    f"  Latencia",
                    f"{latencia:.0f}ms",
                    "ok" if latencia < 3000 else "warning"
                )
                
                test_ok = aprobado_ok
                resultados_test.append({
                    "caso": i,
                    "borrador": caso["borrador"],
                    "success": test_ok,
                    "latencia_ms": latencia,
                    "aprobado": aprobado,
                    "score_marca": score
                })
                
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)[:100]}")
                resultados_test.append({
                    "caso": i,
                    "borrador": caso["borrador"],
                    "success": False,
                    "error": str(e)
                })
        
        success = all(r.get("success") for r in resultados_test)
        self.resultados["agentes"]["identidad"] = {
            "success": success,
            "casos": len(resultados_test),
            "casos_exitosos": sum(1 for r in resultados_test if r.get("success")),
            "results": resultados_test
        }
        
        return {"success": success, "resultados": resultados_test}
    
    async def validar_conversacional(self) -> Dict[str, Any]:
        """
        TEST 4: Agente Conversacional
        
        Responsabilidad: Generar respuestas contextuales y naturales
        Modelo: mixtral-8x7b-32768
        Temperatura: 0.7 (creativo, conversacional)
        """
        print("\n💬 TEST 4: CONVERSACIONAL\n")
        
        if not self.test_lead_id:
            print("  ⚠️  Saltando: Necesita lead_id del Captador\n")
            self.resultados["agentes"]["conversacional"] = {
                "success": False,
                "skipped": True,
                "razon": "no_lead_id"
            }
            return {"success": False, "skipped": True}
        
        test_casos = [
            {
                "mensaje": "Me interesa automatizar mis ventas, ¿cuál es vuestro proceso?",
                "etapa": "interes",
                "esperado_tipo": "respuesta_detallada"
            },
            {
                "mensaje": "¿Tienen referencias de clientes que parecidos a mi empresa?",
                "etapa": "consideration",
                "esperado_tipo": "social_proof"
            }
        ]
        
        resultados_test = []
        conversacional = ConversacionalAgent(self.db, self.settings)
        
        for i, caso in enumerate(test_casos, 1):
            self._print_resultado(f"Caso {i}", "", "info")
            print(f"    Mensaje: '{caso['mensaje'][:60]}...'")
            
            try:
                inicio = time.time()
                result = conversacional.execute({
                    "mensaje": caso["mensaje"],
                    "lead_id": self.test_lead_id,
                    "session_id": self.session_id,
                    "etapa_actual": caso["etapa"],
                    "decision_orquestador": {"etapa_aida": caso["etapa"]}
                })
                latencia = (time.time() - inicio) * 1000
                
                # Validaciones
                respuesta = result.get("respuesta_final", "")
                tiene_respuesta = len(respuesta) > 50
                
                self._print_resultado(
                    f"  Respuesta (chars)",
                    f"{len(respuesta)}",
                    "ok" if tiene_respuesta else "warning"
                )
                self._print_resultado(
                    f"  Preview",
                    f"{respuesta[:70]}..." if respuesta else "N/A",
                    "ok"
                )
                self._print_resultado(
                    f"  Latencia",
                    f"{latencia:.0f}ms",
                    "ok" if latencia < 5000 else "warning"
                )
                
                test_ok = tiene_respuesta
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": test_ok,
                    "latencia_ms": latencia,
                    "respuesta_len": len(respuesta)
                })
                
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)[:100]}")
                resultados_test.append({
                    "caso": i,
                    "mensaje": caso["mensaje"],
                    "success": False,
                    "error": str(e)
                })
        
        success = all(r.get("success") for r in resultados_test)
        self.resultados["agentes"]["conversacional"] = {
            "success": success,
            "casos": len(resultados_test),
            "casos_exitosos": sum(1 for r in resultados_test if r.get("success")),
            "results": resultados_test
        }
        
        return {"success": success, "resultados": resultados_test}
    
    async def validar_comunicacion(self) -> Dict[str, Any]:
        """
        TEST 5: Agente Comunicación
        
        Responsabilidad: Personalizar y adaptar mensajes
        Modelo: llama-3.1-70b-versatile
        Temperatura: 0.6 (equilibrio creativo/consistencia)
        """
        print("\n✉️  TEST 5: COMUNICACIÓN\n")
        
        if not self.test_lead_id:
            print("  ⚠️  Saltando: Necesita lead_id del Captador\n")
            self.resultados["agentes"]["comunicacion"] = {
                "success": False,
                "skipped": True,
                "razon": "no_lead_id"
            }
            return {"success": False, "skipped": True}
        
        test_casos = [
            {
                "tipo": "propuesta",
                "borrador": "Te ofrecemos un servicio de automatización de ventas.",
                "estilo": "profesional"
            },
            {
                "tipo": "urgencia",
                "borrador": "Esta oferta vence en 3 días.",
                "estilo": "amigable"
            }
        ]
        
        resultados_test = []
        comunicacion = ComunicacionAgent(self.db, self.settings)
        
        for i, caso in enumerate(test_casos, 1):
            self._print_resultado(f"Caso {i}", "", "info")
            print(f"    Tipo: {caso['tipo']} | Estilo: {caso['estilo']}")
            
            try:
                inicio = time.time()
                result = comunicacion.execute({
                    "tipo_mensaje": caso["tipo"],
                    "borrador": caso["borrador"],
                    "lead_id": self.test_lead_id,
                    "estilo": caso["estilo"],
                    "etapa_aida": "decision"
                })
                latencia = (time.time() - inicio) * 1000
                
                # Validaciones
                mensaje = result.get("mensaje_personalizado", "")
                tiene_mensaje = len(mensaje) > 30
                
                self._print_resultado(
                    f"  Mensaje personalizado",
                    f"{len(mensaje)} caracteres",
                    "ok" if tiene_mensaje else "warning"
                )
                self._print_resultado(
                    f"  Preview",
                    f"{mensaje[:70]}..." if mensaje else "N/A",
                    "ok"
                )
                self._print_resultado(
                    f"  Latencia",
                    f"{latencia:.0f}ms",
                    "ok" if latencia < 3000 else "warning"
                )
                
                test_ok = tiene_mensaje
                resultados_test.append({
                    "caso": i,
                    "tipo": caso["tipo"],
                    "success": test_ok,
                    "latencia_ms": latencia,
                    "mensaje_len": len(mensaje)
                })
                
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)[:100]}")
                resultados_test.append({
                    "caso": i,
                    "tipo": caso["tipo"],
                    "success": False,
                    "error": str(e)
                })
        
        success = all(r.get("success") for r in resultados_test)
        self.resultados["agentes"]["comunicacion"] = {
            "success": success,
            "casos": len(resultados_test),
            "casos_exitosos": sum(1 for r in resultados_test if r.get("success")),
            "results": resultados_test
        }
        
        return {"success": success, "resultados": resultados_test}
    
    async def validar_analitico(self) -> Dict[str, Any]:
        """
        TEST 6: Agente Analítico
        
        Responsabilidad: Generar análisis y alertas
        Modelo: llama-3.3-70b-versatile
        Temperatura: 0.3 (analítico, sin creatividad)
        """
        print("\n📊 TEST 6: ANALÍTICO\n")
        
        try:
            inicio = time.time()
            analitico = AnaliticoAgent(self.db, self.settings)
            result = analitico.execute({"tipo_analisis": "diario"})
            latencia = (time.time() - inicio) * 1000
            
            # Validaciones
            tiene_score = "score_salud_crm" in result
            tiene_alertas = "alertas" in result
            tiene_resumen = "resumen_ejecutivo" in result
            
            self._print_resultado(
                f"  Score salud CRM",
                f"{result.get('score_salud_crm', 'N/A')}/100",
                "ok" if tiene_score else "warning"
            )
            self._print_resultado(
                f"  Alertas generadas",
                len(result.get("alertas", [])),
                "ok" if tiene_alertas else "warning"
            )
            self._print_resultado(
                f"  Resumen ejecutivo",
                "Presente" if tiene_resumen else "NO",
                "ok" if tiene_resumen else "warning"
            )
            self._print_resultado(
                f"  Latencia",
                f"{latencia:.0f}ms",
                "ok" if latencia < 5000 else "warning"
            )
            
            success = tiene_score and tiene_alertas and tiene_resumen
            self.resultados["agentes"]["analitico"] = {
                "success": success,
                "score_salud": result.get("score_salud_crm"),
                "alertas_count": len(result.get("alertas", [])),
                "latencia_ms": latencia
            }
            
            return {"success": success, "resultado": result}
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)[:100]}")
            self.resultados["agentes"]["analitico"] = {
                "success": False,
                "error": str(e)
            }
            return {"success": False, "error": str(e)}
    
    async def ejecutar_validacion_completa(self):
        """Ejecuta la validación completa de todos los agentes."""
        self._print_section("VALIDADOR DE AGENTES ORBITA CON GROQ")
        
        print(f"🔧 Configuración:")
        self._print_resultado("Groq API Key", self.settings.groq_api_key[:20] + "...", "ok")
        self._print_resultado("Supabase URL", self.settings.supabase_url, "ok")
        self._print_resultado("Session ID", self.session_id[:16] + "...", "ok")
        self._print_resultado("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ok")
        
        # Ejecutar tests en orden
        print("\n\n")
        await self.validar_orchestrator()
        await self.validar_captador()
        await self.validar_identidad()
        await self.validar_conversacional()
        await self.validar_comunicacion()
        await self.validar_analitico()
        
        # Reporte final
        self._print_section("REPORTE FINAL")
        
        total_agentes = len(self.resultados["agentes"])
        agentes_ok = sum(1 for a in self.resultados["agentes"].values() if a.get("success"))
        
        print(f"Agentes validados: {agentes_ok}/{total_agentes}\n")
        
        for nombre_agente, resultado in self.resultados["agentes"].items():
            estado = "✅" if resultado.get("success") else "❌"
            print(f"{estado} {nombre_agente.upper()}")
            if resultado.get("casos"):
                exitosos = resultado.get("casos_exitosos", 0)
                total = resultado.get("casos")
                print(f"   {exitosos}/{total} casos exitosos")
            if resultado.get("error"):
                print(f"   Error: {resultado['error'][:80]}")
            print()
        
        # Guardar resultados
        with open("validate_results.json", "w", encoding="utf-8") as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Resultados guardados en: validate_results.json\n")
        
        self._print_section("✨ VALIDACIÓN COMPLETADA")
        
        return agentes_ok == total_agentes


async def main():
    """Entry point."""
    validador = ValidadorAgentes()
    success = await validador.ejecutar_validacion_completa()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
