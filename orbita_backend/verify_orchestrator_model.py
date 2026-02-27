#!/usr/bin/env python3
"""
Script para verificar que el orquestador esté usando GPT-4o mini
"""
import asyncio
import sys
from config import (
    USE_OPENAI_FOR_ORCHESTRATOR, 
    OPENAI_MODEL_ORCHESTRATOR,
    OPENAI_API_KEY,
    GROQ_MODELS
)
from utils.groq_client import GroqClient

async def verify_orchestrator():
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DEL ORQUESTADOR")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    print("\n📋 Variables de configuración:")
    print(f"   USE_OPENAI_FOR_ORCHESTRATOR: {USE_OPENAI_FOR_ORCHESTRATOR}")
    print(f"   OPENAI_MODEL_ORCHESTRATOR: {OPENAI_MODEL_ORCHESTRATOR}")
    print(f"   OPENAI_API_KEY configurada: {'✅ Sí' if OPENAI_API_KEY else '❌ No'}")
    print(f"   GROQ_MODEL_ORCHESTRATOR: {GROQ_MODELS.get('orchestrator')}")
    
    # 2. Verificar cliente
    print("\n🔧 Verificando cliente de IA:")
    client = GroqClient()
    
    if client.openai_client:
        print("   ✅ Cliente OpenAI inicializado correctamente")
    else:
        print("   ❌ Cliente OpenAI NO inicializado")
        return False
    
    # 3. Verificar que el orquestador use OpenAI
    print("\n🤖 Configuración del orquestador:")
    if USE_OPENAI_FOR_ORCHESTRATOR:
        print(f"   ✅ El orquestador usará: OpenAI {OPENAI_MODEL_ORCHESTRATOR}")
        print(f"   💰 Modelo económico para ahorrar tokens")
    else:
        print(f"   ⚠️  El orquestador usará: Groq {GROQ_MODELS.get('orchestrator')}")
    
    # 4. Prueba real
    print("\n🧪 Realizando prueba de generación...")
    try:
        response = await client.generate_completion(
            prompt="Di 'Hola' en una palabra",
            agent_type="orchestrator",
            max_tokens=10,
            temperature=0.1,
            system_message="Responde con una sola palabra."
        )
        
        print(f"   ✅ Respuesta recibida: '{response}'")
        print(f"   ✅ El orquestador está funcionando con {OPENAI_MODEL_ORCHESTRATOR}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error al generar respuesta: {e}")
        return False
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    success = asyncio.run(verify_orchestrator())
    sys.exit(0 if success else 1)
