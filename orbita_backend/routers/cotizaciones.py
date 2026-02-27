# Router de cotizaciones para ORBITA
# [CRITERIO 5] - Cotizaciones automáticas generadas por IA

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from auth import get_current_active_user, get_current_user_empresa
from database import get_db, create_cotizacion
from utils.cotizacion_renderer import render_cotizacion_markdown

cotizaciones_router = APIRouter()

class CotizacionCreate(BaseModel):
    lead_id: int
    titulo: str
    descripcion: str
    monto: float
    moneda: str = "USD"

class CotizacionGenerateRequest(BaseModel):
    lead_id: int
    servicio: str
    detalles: str

@cotizaciones_router.get("/", summary="Obtener cotizaciones")
async def get_cotizaciones(
    current_user: dict = Depends(get_current_active_user),
    empresa: dict = Depends(get_current_user_empresa)
):
    """Obtiene todas las cotizaciones de la empresa"""
    try:
        db = get_db()
        result = db.table("cotizaciones")\
            .select("*")\
            .eq("empresa_id", empresa["id"])\
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@cotizaciones_router.post("/", summary="Crear cotización")
async def create_new_cotizacion(
    cotizacion: CotizacionCreate,
    current_user: dict = Depends(get_current_active_user),
    empresa: dict = Depends(get_current_user_empresa)
):
    """Crea una nueva cotización"""
    try:
        cotizacion_data = {
            **cotizacion.dict(),
            "empresa_id": empresa["id"],
            "user_id": current_user["id"],
            "status": "borrador",
            "created_at": datetime.utcnow().isoformat()
        }
        
        new_cotizacion = await create_cotizacion(cotizacion_data)
        return new_cotizacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@cotizaciones_router.post("/generate", summary="Generar cotización con IA")
async def generate_cotizacion_with_ai(
    request: CotizacionGenerateRequest,
    current_user: dict = Depends(get_current_active_user),
    empresa: dict = Depends(get_current_user_empresa)
):
    """
    Genera una cotización personalizada usando IA basada en los datos del lead.
    [CRITERIO 5] - Cotizaciones automáticas generadas por IA
    """
    try:
        # Obtener datos del lead
        db = get_db()
        lead_result = db.table("leads")\
            .select("*")\
            .eq("id", request.lead_id)\
            .eq("empresa_id", empresa["id"])\
            .execute()
        
        if not lead_result.data:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        lead_data = lead_result.data[0]
        
        # Usar agente de comunicación para generar cotización con IA
        from agents.comunicacion import ComunicacionAgent
        agente_comunicacion = ComunicacionAgent()
        
        resultado = await agente_comunicacion.generate_cotizacion(
            lead_data=lead_data,
            servicio_solicitado=request.servicio,
            detalles_adicionales=request.detalles
        )
        
        if not resultado.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=resultado.get("error", "Error generando cotización")
            )
        
        # Agregar datos de empresa y usuario a la cotización
        cotizacion_data = resultado["cotizacion"]
        cotizacion_data["empresa_id"] = empresa["id"]
        cotizacion_data["user_id"] = current_user["id"]
        
        # Guardar cotización en base de datos
        nueva_cotizacion = await create_cotizacion(cotizacion_data)
        
        # Actualizar estado del lead a "cotizado"
        db.table("leads")\
            .update({"status": "cotizado", "updated_at": datetime.utcnow().isoformat()})\
            .eq("id", request.lead_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Cotización generada exitosamente con IA",
            "cotizacion": nueva_cotizacion,
            "lead_id": request.lead_id,
            "total": resultado.get("total_estimado"),
            "generada_por": agente_comunicacion.agent_name,
            "status": "borrador"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando cotización: {str(e)}")

@cotizaciones_router.get("/{cotizacion_id}/render", summary="Renderizar cotización en Markdown")
async def render_cotizacion(
    cotizacion_id: int,
    current_user: dict = Depends(get_current_active_user),
    empresa: dict = Depends(get_current_user_empresa)
):
    """
    Obtiene una cotización renderizada en formato Markdown listo para enviar.
    """
    try:
        db = get_db()
        
        # Obtener cotización
        cotizacion_result = db.table("cotizaciones")\
            .select("*")\
            .eq("id", cotizacion_id)\
            .eq("empresa_id", empresa["id"])\
            .execute()
        
        if not cotizacion_result.data:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        
        cotizacion_data = cotizacion_result.data[0]
        
        # Obtener datos del lead
        lead_result = db.table("leads")\
            .select("*")\
            .eq("id", cotizacion_data["lead_id"])\
            .execute()
        
        lead_data = lead_result.data[0] if lead_result.data else {}
        
        # Renderizar cotización
        markdown_content = render_cotizacion_markdown(
            cotizacion_data=cotizacion_data,
            lead_data=lead_data,
            empresa_data=empresa
        )
        
        return {
            "success": True,
            "cotizacion_id": cotizacion_id,
            "markdown": markdown_content,
            "lead_nombre": lead_data.get("nombre"),
            "total": cotizacion_data.get("total")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renderizando cotización: {str(e)}")