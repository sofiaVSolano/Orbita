# PLANTILLA DE COTIZACIÓN — ORBITA
# Uso: El backend reemplaza todos los campos {{CAMPO}} con datos reales del lead y la empresa
# Campos de EMPRESA: se configuran una vez en Supabase (tabla empresas)
# Campos de LEAD/COTIZACIÓN: se llenan dinámicamente por el Agente Conversacional

---

<!-- ============================================================
     INSTRUCCIONES PARA EL BACKEND
     
     1. Cargar esta plantilla desde Supabase o archivo
     2. Reemplazar campos {{EMPRESA_*}} con datos de tabla empresas
     3. Reemplazar campos {{LEAD_*}} con datos de tabla leads
     4. Reemplazar campos {{COT_*}} con datos de tabla cotizaciones
     5. Reemplazar campos {{ITEM_*}} iterando sobre cotizacion.items[]
     6. Eliminar las líneas de comentarios HTML antes de enviar
     7. Convertir el Markdown resultante a PDF o enviar como texto a Telegram
     ============================================================ -->

---

# {{EMPRESA_NOMBRE}}
**{{EMPRESA_SLOGAN}}**

📍 {{EMPRESA_CIUDAD}}, {{EMPRESA_PAIS}}  
📧 {{EMPRESA_EMAIL}}  
📱 {{EMPRESA_TELEFONO}}  
🌐 {{EMPRESA_SITIO_WEB}}

---

# PROPUESTA COMERCIAL
## Ref. No. {{COT_CODIGO}}

---

**Preparada para:**

| | |
|---|---|
| **Cliente** | {{LEAD_NOMBRE}} |
| **Empresa** | {{LEAD_EMPRESA}} |
| **Cargo** | {{LEAD_CARGO}} |
| **Email** | {{LEAD_EMAIL}} |
| **Teléfono** | {{LEAD_TELEFONO}} |

**Detalles de la propuesta:**

| | |
|---|---|
| **Fecha de emisión** | {{COT_FECHA_EMISION}} |
| **Válida hasta** | {{COT_FECHA_VENCIMIENTO}} |
| **Asesor** | {{EMPRESA_ASESOR_NOMBRE}} |
| **Canal de contacto** | {{COT_CANAL_ORIGEN}} |

---

## 1. ENTENDIMIENTO DE SU NECESIDAD

Estimado/a **{{LEAD_NOMBRE}}**,

{{COT_INTRODUCCION_PERSONALIZADA}}

Basándonos en su requerimiento de **{{LEAD_SERVICIO_INTERES}}** para **{{LEAD_EMPRESA}}**, hemos preparado la siguiente propuesta que se ajusta a sus objetivos y presupuesto estimado de **{{LEAD_PRESUPUESTO_ESTIMADO}}**.

---

## 2. SOLUCIÓN PROPUESTA

### {{COT_PLAN_NOMBRE}}

{{COT_DESCRIPCION_PLAN}}

---

## 3. ALCANCE DEL SERVICIO

{{COT_DESCRIPCION_ALCANCE}}

### ¿Qué incluye esta propuesta?

<!-- INICIO BLOQUE REPETIBLE — El backend itera sobre cotizacion.items[] -->
<!-- Para cada item en items[], generar un bloque como este:           -->

| # | Entregable | Descripción | Valor |
|---|---|---|---|
| 1 | {{ITEM_1_NOMBRE}} | {{ITEM_1_DESCRIPCION}} | ${{ITEM_1_VALOR}} {{COT_MONEDA}} |
| 2 | {{ITEM_2_NOMBRE}} | {{ITEM_2_DESCRIPCION}} | ${{ITEM_2_VALOR}} {{COT_MONEDA}} |
| 3 | {{ITEM_3_NOMBRE}} | {{ITEM_3_DESCRIPCION}} | ${{ITEM_3_VALOR}} {{COT_MONEDA}} |

<!-- FIN BLOQUE REPETIBLE -->

---

## 4. INVERSIÓN

| Concepto | Valor |
|---|---|
| Subtotal | ${{COT_SUBTOTAL}} {{COT_MONEDA}} |
| Descuento | {{COT_DESCUENTO_PORCENTAJE}}% — (${{COT_DESCUENTO_VALOR}} {{COT_MONEDA}}) |
| **TOTAL** | **${{COT_VALOR_TOTAL}} {{COT_MONEDA}}** |

> 💡 *Precio especial válido hasta el **{{COT_FECHA_VENCIMIENTO}}**.*

### Forma de pago

{{COT_FORMA_PAGO}}

<!-- Ejemplo de valor: "50% al inicio del proyecto, 50% a la entrega" -->
<!-- O: "Pago único al inicio" / "3 cuotas mensuales de $X" -->

---

## 5. CRONOGRAMA ESTIMADO

| Fase | Descripción | Duración |
|---|---|---|
| {{FASE_1_NOMBRE}} | {{FASE_1_DESCRIPCION}} | {{FASE_1_DURACION}} |
| {{FASE_2_NOMBRE}} | {{FASE_2_DESCRIPCION}} | {{FASE_2_DURACION}} |
| {{FASE_3_NOMBRE}} | {{FASE_3_DESCRIPCION}} | {{FASE_3_DURACION}} |

**Tiempo total estimado:** {{COT_TIEMPO_TOTAL}}  
**Fecha estimada de inicio:** {{COT_FECHA_INICIO_ESTIMADA}}

---

## 6. ¿POR QUÉ {{EMPRESA_NOMBRE}}?

{{EMPRESA_PROPUESTA_VALOR}}

### Nuestros clientes dicen:

> *"{{EMPRESA_TESTIMONIO_1_TEXTO}}"*  
> — **{{EMPRESA_TESTIMONIO_1_NOMBRE}}**, {{EMPRESA_TESTIMONIO_1_CARGO}}

---

## 7. PRÓXIMOS PASOS

Para proceder con esta propuesta:

1.  Confirmar su aceptación respondiendo a este mensaje
2.  Firmar el acuerdo de servicios (lo enviamos en 24 horas)
3.  Realizar el primer pago según la forma acordada
4.  Agendar la reunión de inicio del proyecto

**¿Tiene preguntas?** Contáctenos directamente:  
📱 {{EMPRESA_TELEFONO}} · 📧 {{EMPRESA_EMAIL}}

---

## 8. TÉRMINOS Y CONDICIONES

{{EMPRESA_TERMINOS_CONDICIONES}}

<!-- Ejemplo de valor:
"Esta propuesta es válida por {{COT_VIGENCIA_DIAS}} días calendario desde
su fecha de emisión. Los precios están expresados en {{COT_MONEDA}} e
incluyen/excluyen IVA según aplique. Cualquier cambio en el alcance del
servicio será cotizado por separado. {{EMPRESA_NOMBRE}} se reserva el
derecho de ajustar precios para propuestas no aceptadas en el período de
vigencia." -->

---

*Propuesta generada por el sistema ORBITA · {{COT_FECHA_EMISION}}*  
*{{EMPRESA_NOMBRE}} · {{EMPRESA_EMAIL}}*

---

<!-- ============================================================
     DICCIONARIO DE CAMPOS — REFERENCIA PARA EL BACKEND
     
     CAMPOS DE EMPRESA (tabla: empresas)
     ─────────────────────────────────────────────────────
     {{EMPRESA_NOMBRE}}              → empresas.nombre
     {{EMPRESA_SLOGAN}}              → empresas.slogan
     {{EMPRESA_CIUDAD}}              → empresas.ciudad
     {{EMPRESA_PAIS}}                → empresas.pais
     {{EMPRESA_EMAIL}}               → empresas.email
     {{EMPRESA_TELEFONO}}            → empresas.telefono
     {{EMPRESA_SITIO_WEB}}           → empresas.sitio_web
     {{EMPRESA_ASESOR_NOMBRE}}       → empresas.asesor_nombre
     {{EMPRESA_PROPUESTA_VALOR}}     → empresas.propuesta_valor
     {{EMPRESA_TERMINOS_CONDICIONES}}→ empresas.terminos_condiciones
     {{EMPRESA_TESTIMONIO_1_TEXTO}}  → empresas.testimonios[0].texto
     {{EMPRESA_TESTIMONIO_1_NOMBRE}} → empresas.testimonios[0].nombre
     {{EMPRESA_TESTIMONIO_1_CARGO}}  → empresas.testimonios[0].cargo
     
     CAMPOS DE LEAD (tabla: leads)
     ─────────────────────────────────────────────────────
     {{LEAD_NOMBRE}}                 → leads.nombre
     {{LEAD_EMPRESA}}                → leads.empresa_nombre
     {{LEAD_CARGO}}                  → leads.cargo
     {{LEAD_EMAIL}}                  → leads.email
     {{LEAD_TELEFONO}}               → leads.telefono
     {{LEAD_SERVICIO_INTERES}}       → leads.servicio_interes
     {{LEAD_PRESUPUESTO_ESTIMADO}}   → leads.presupuesto_estimado
     
     CAMPOS DE COTIZACIÓN (tabla: cotizaciones)
     ─────────────────────────────────────────────────────
     {{COT_CODIGO}}                  → cot.id[:8].upper() ej: "COT-A3F2B1C9"
     {{COT_FECHA_EMISION}}           → cot.created_at formateada "DD/MM/YYYY"
     {{COT_FECHA_VENCIMIENTO}}       → created_at + vigencia_dias
     {{COT_PLAN_NOMBRE}}             → cot.plan_nombre
     {{COT_DESCRIPCION_PLAN}}        → cot.descripcion
     {{COT_DESCRIPCION_ALCANCE}}     → generado por el Agente Conversacional
     {{COT_INTRODUCCION_PERSONALIZADA}}→ generado por el Agente Conversacional
     {{COT_SUBTOTAL}}                → suma de items antes de descuento
     {{COT_DESCUENTO_PORCENTAJE}}    → cot.descuento_porcentaje (default "0")
     {{COT_DESCUENTO_VALOR}}         → subtotal * descuento / 100
     {{COT_VALOR_TOTAL}}             → cot.valor formateado con separadores
     {{COT_MONEDA}}                  → cot.moneda ej: "COP", "USD"
     {{COT_FORMA_PAGO}}              → cot.forma_pago
     {{COT_VIGENCIA_DIAS}}           → cot.vigencia_dias
     {{COT_TIEMPO_TOTAL}}            → generado por el Agente Conversacional
     {{COT_FECHA_INICIO_ESTIMADA}}   → generado o calculado
     {{COT_CANAL_ORIGEN}}            → leads.fuente ej: "Telegram", "Web"
     
     CAMPOS DE ÍTEMS (cotizaciones.items[] — iterar)
     ─────────────────────────────────────────────────────
     {{ITEM_N_NOMBRE}}               → items[n].nombre
     {{ITEM_N_DESCRIPCION}}          → items[n].descripcion
     {{ITEM_N_VALOR}}                → items[n].valor formateado
     
     CAMPOS DE FASES (cotizaciones.fases[] — iterar, opcional)
     ─────────────────────────────────────────────────────
     {{FASE_N_NOMBRE}}               → fases[n].nombre
     {{FASE_N_DESCRIPCION}}          → fases[n].descripcion
     {{FASE_N_DURACION}}             → fases[n].duracion ej: "1 semana"
     ============================================================ -->
