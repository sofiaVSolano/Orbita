#!/usr/bin/env python3
"""
VALIDADOR RÁPIDO DE AGENTES ORBITA
==================================
Script sencillo sin async para probar rápidamente cada agente.

Ejecutar:
    python validate_agents_quick.py

Salida:
    - Prueba cada agente con casos reales
    - Mide latencia
    - Verifica respuestas esperadas
    - Genera reporte en consola
"""

import time
import json
from datetime import datetime, timezone
from uuid import uuid4

# Imports del backend
from config import get_settings
from database import get_db
from agents.orchestrator import OrchestratorAgent
from agents.captador import CaptadorAgent
from agents.identidad import IdentidadAgent
from agents.conversacional import ConversacionalAgent
from agents.comunicacion import ComunicacionAgent
from agents.analitico import AnaliticoAgent


def print_header(titulo, nivel=1):
    """Imprime encabezado."""
    if nivel == 1:
        print(f"\n{'='*70}")
        print(f"  {titulo}")
        print(f"{'='*70}\n")
    elif nivel == 2:
        print(f"\n{titulo}")
        print(f"{'-'*70}\n")


def print_result(label, valor, ok=True):
    """Imprime resultado formateado."""
    icon = "✅" if ok else "❌"
    print(f"  {icon} {label}: {valor}")


def test_orchestrator():
    """Test 1: Orquestador."""
    print_header("TEST 1: ORQUESTADOR 🤖", 2)
    
    db = get_db()
    settings = get_settings()
    orch = OrchestratorAgent(db, settings)
    
    test_casos = [
        ("Hola, estoy aquí para que me cuentes sobre los servicios", "saludo"),
        ("¿Cuánto cuesta un chatbot con IA?", "cotizacion"),
        ("Quiero agendar una llamada", "agendar_reunion"),
    ]
    
    exitos = 0
    for msg, expected_intention in test_casos:
        print(f"💬 Mensaje: '{msg[:50]}...'")
        try:
            inicio = time.time()
            resultado = orch.execute({
                "mensaje": msg,
                "lead_id": None,
                "session_id": f"test-{str(uuid4())[:8]}",
                "telegram_chat_id": "999"
            })
            latencia = (time.time() - inicio) * 1000
            
            intencion = resultado.get("intencion")
            ok = intencion == expected_intention
            exitos += 1 if ok else 0
            
            print_result("Intención", intencion, ok)
            print_result("Etapa AIDA", resultado.get("etapa_aida"))
            print_result("Latencia", f"{latencia:.0f}ms", latencia < 3000)
            print()
        except Exception as e:
            print_result("Error", str(e)[:80], False)
            print()
    
    return exitos == len(test_casos)


def test_captador():
    """Test 2: Captador."""
    print_header("TEST 2: CAPTADOR 👤", 2)
    
    db = get_db()
    settings = get_settings()
    captador = CaptadorAgent(db, settings)
    
    test_casos = [
        "Hola soy Carlos Pérez de Innovatech, soy el CEO",
        "Me llamo Sofia, trabajo en marketing en XYZ Corp",
    ]
    
    test_lead_id = None
    exitos = 0
    
    for i, msg in enumerate(test_casos, 1):
        print(f"💬 Caso {i}: '{msg[:50]}...'")
        try:
            inicio = time.time()
            resultado = captador.execute({
                "mensaje": msg,
                "telegram_user_id": f"test_user_{int(time.time())}",
                "telegram_username": f"testuser{i}",
                "telegram_chat_id": f"{999 + i}",
                "session_id": f"test-{str(uuid4())[:8]}",
                "nombre_telegram": f"TestUser {i}"
            })
            latencia = (time.time() - inicio) * 1000
            
            accion = resultado.get("accion", "N/A")
            lead_id = resultado.get("lead_id")
            ok = accion in ["crear_lead", "actualizar_lead", "no_accion"]
            exitos += 1 if ok else 0
            
            if not test_lead_id and lead_id:
                test_lead_id = lead_id
            
            print_result("Acción", accion, ok)
            print_result("Lead ID", lead_id[:8] + "..." if lead_id else "NO")
            print_result("Latencia", f"{latencia:.0f}ms", latencia < 3000)
            print()
        except Exception as e:
            print_result("Error", str(e)[:80], False)
            print()
    
    return exitos > 0, test_lead_id


def test_identidad():
    """Test 3: Identidad."""
    print_header("TEST 3: IDENTIDAD 🎭", 2)
    
    db = get_db()
    settings = get_settings()
    identidad = IdentidadAgent(db, settings)
    
    test_casos = [
        ("Hola Carlos, me da mucho gusto ayudarte", True),
        ("boludo, nuestro producto es lo mejor", False),
    ]
    
    exitos = 0
    for i, (msg, should_approve) in enumerate(test_casos, 1):
        print(f"📝 Caso {i}: '{msg[:50]}...'")
        try:
            inicio = time.time()
            resultado = identidad.execute({
                "borrador": msg,
                "contexto_lead": {"nombre": "Test", "empresa": "Corp"},
                "agente_origen": "conversacional",
                "etapa_aida": "interes"
            })
            latencia = (time.time() - inicio) * 1000
            
            aprobado = resultado.get("aprobado", False)
            score = resultado.get("score_marca", 0)
            ok = aprobado == should_approve
            exitos += 1 if ok else 0
            
            print_result("Aprobado", aprobado, ok)
            print_result("Score", f"{score:.1f}/10")
            print_result("Latencia", f"{latencia:.0f}ms", latencia < 3000)
            print()
        except Exception as e:
            print_result("Error", str(e)[:80], False)
            print()
    
    return exitos == len(test_casos)


def test_conversacional(lead_id):
    """Test 4: Conversacional."""
    print_header("TEST 4: CONVERSACIONAL 💬", 2)
    
    if not lead_id:
        print("⚠️  Saltando: Necesita lead_id del Captador\n")
        return False
    
    db = get_db()
    settings = get_settings()
    conv = ConversacionalAgent(db, settings)
    
    test_casos = [
        "Me interesa automatizar mis ventas",
        "¿Tienen referencias de clientes?",
    ]
    
    exitos = 0
    for i, msg in enumerate(test_casos, 1):
        print(f"💬 Caso {i}: '{msg[:50]}...'")
        try:
            inicio = time.time()
            resultado = conv.execute({
                "mensaje": msg,
                "lead_id": lead_id,
                "session_id": f"test-{str(uuid4())[:8]}",
                "etapa_actual": "interes",
                "decision_orquestador": {"etapa_aida": "interes"}
            })
            latencia = (time.time() - inicio) * 1000
            
            respuesta = resultado.get("respuesta_final", "")
            ok = len(respuesta) > 50
            exitos += 1 if ok else 0
            
            print_result("Respuesta (chars)", len(respuesta), ok)
            print_result("Preview", f"{respuesta[:60]}..." if respuesta else "N/A")
            print_result("Latencia", f"{latencia:.0f}ms", latencia < 5000)
            print()
        except Exception as e:
            print_result("Error", str(e)[:80], False)
            print()
    
    return exitos == len(test_casos)


def test_comunicacion(lead_id):
    """Test 5: Comunicación."""
    print_header("TEST 5: COMUNICACIÓN ✉️", 2)
    
    if not lead_id:
        print("⚠️  Saltando: Necesita lead_id del Captador\n")
        return False
    
    db = get_db()
    settings = get_settings()
    comm = ComunicacionAgent(db, settings)
    
    test_casos = [
        ("propuesta", "Te ofrecemos um servicio de automatización"),
        ("urgencia", "Esta oferta vence en 3 días"),
    ]
    
    exitos = 0
    for tipo, msg in test_casos:
        print(f"📝 Tipo: {tipo} | '{msg[:50]}...'")
        try:
            inicio = time.time()
            resultado = comm.execute({
                "tipo_mensaje": tipo,
                "borrador": msg,
                "lead_id": lead_id,
                "estilo": "profesional",
                "etapa_aida": "decision"
            })
            latencia = (time.time() - inicio) * 1000
            
            personalizado = resultado.get("mensaje_personalizado", "")
            ok = len(personalizado) > 30
            exitos += 1 if ok else 0
            
            print_result("Personalizado (chars)", len(personalizado), ok)
            print_result("Preview", f"{personalizado[:60]}..." if personalizado else "N/A")
            print_result("Latencia", f"{latencia:.0f}ms", latencia < 3000)
            print()
        except Exception as e:
            print_result("Error", str(e)[:80], False)
            print()
    
    return exitos == len(test_casos)


def test_analitico():
    """Test 6: Analítico."""
    print_header("TEST 6: ANALÍTICO 📊", 2)
    
    db = get_db()
    settings = get_settings()
    analitico = AnaliticoAgent(db, settings)
    
    try:
        inicio = time.time()
        resultado = analitico.execute({"tipo_analisis": "diario"})
        latencia = (time.time() - inicio) * 1000
        
        tiene_score = "score_salud_crm" in resultado
        tiene_alertas = "alertas" in resultado
        
        print_result("Score salud CRM", resultado.get("score_salud_crm", "N/A"), tiene_score)
        print_result("Alertas", len(resultado.get("alertas", [])))
        print_result("Latencia", f"{latencia:.0f}ms", latencia < 5000)
        print()
        
        return tiene_score and tiene_alertas
    except Exception as e:
        print_result("Error", str(e)[:80], False)
        print()
        return False


def main():
    """Ejecuta todos los tests."""
    print_header("VALIDADOR DE AGENTES ORBITA CON GROQ")
    
    # Verificar configuración
    try:
        settings = get_settings()
        print("🔧 Configuración:")
        print_result("Groq API Key", settings['groq_api_key'][:20] + "...")
        print_result("Supabase URL", settings['supabase_url'])
        print()
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        return False
    
    # Ejecutar tests
    resultados = {}
    
    resultados["orchestrator"] = test_orchestrator()
    resultados["captador"], lead_id = test_captador()
    resultados["identidad"] = test_identidad()
    resultados["conversacional"] = test_conversacional(lead_id)
    resultados["comunicacion"] = test_comunicacion(lead_id)
    resultados["analitico"] = test_analitico()
    
    # Reporte final
    print_header("REPORTE FINAL", 1)
    
    agentes_ok = sum(1 for v in resultados.values() if v)
    total = len(resultados)
    
    print(f"✅ Agentes validados: {agentes_ok}/{total}\n")
    
    for agente, ok in resultados.items():
        icon = "✅" if ok else "❌"
        print(f"{icon} {agente.upper()}")
    
    print()
    success = agentes_ok >= 4  # Al menos 4 de 6 (los 2 que dependen de lead_id pueden faltar)
    
    if success:
        print("✨ VALIDACIÓN EXITOSA\n")
    else:
        print("⚠️  VALIDACIÓN CON ADVERTENCIAS\n")
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
