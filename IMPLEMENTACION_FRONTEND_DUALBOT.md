# ✅ FRONTEND ACTUALIZADO PARA DUAL-BOT

## 📋 Resumen de cambios implementados

Se actualizó completamente el frontend de ORBITA para soportar la arquitectura de **2 bots independientes**:
- **Bot de Leads** (@orbita_cliente_bot) - Público para prospectos
- **Bot de Admin** (@orbita_admin_bot) - Privado para equipo interno

---

## 📦 Archivos modificados

### 1. ✅ `src/lib/api.ts`
**Cambios:**
- ❌ Eliminado: `setupWebhook()` (singular)
- ✅ Agregadas 3 nuevas funciones:
  - `setupWebhooks()` - Configura ambos bots simultáneamente
  - `setupLeadsWebhook()` - Configura solo el bot de leads
  - `setupAdminWebhook()` - Configura solo el bot de admin
- ✅ Actualizado: `getBotInfo()` ahora retorna `{ data: { bot_leads: {...}, bot_admin: {...} } }`

**Código:**
```typescript
getBotInfo: () =>
    fetch(`${API}/api/v1/telegram/info`, { headers: h() }).then((r) => r.json()),
// Ahora retorna: { success: true, data: { bot_leads: {...}, bot_admin: {...} } }

setupWebhooks: () =>
    fetch(`${API}/api/v1/telegram/setup-webhooks`, {
        method: 'POST',
        headers: h(),
    }).then((r) => r.json()),
// Configura AMBOS bots en un solo click

setupLeadsWebhook: () =>
    fetch(`${API}/api/v1/telegram/setup-leads-webhook`, {
        method: 'POST',
        headers: h(),
    }).then((r) => r.json()),

setupAdminWebhook: () =>
    fetch(`${API}/api/v1/telegram/setup-admin-webhook`, {
        method: 'POST',
        headers: h(),
    }).then((r) => r.json()),
```

---

### 2. ✅ `src/components/Layout/Sidebar.tsx`
**Cambios:**
- Estado actualizado:
  - ❌ `botUsername` y `botActivo` (variables simples)
  - ✅ `botLeads` y `botAdmin` (objetos con `username` y `webhook_url`)
- Muestra **2 indicadores** en el footer:
  - 🟢 Bot de leads con badge "leads" (cyan)
  - 🔵 Bot de admin con badge "admin" (purple)
- Cada bot muestra su propio estado (activo/pausado)

**Vista:**
```
[Sidebar Footer]
├─ 5 leads activos
├─ 🟢 @orbita_cliente_bot [leads]
├─ 🔵 @orbita_admin_bot [admin]
└─ Última actividad: hace 2 minutos
```

---

### 3. ✅ `src/pages/Telegram.tsx`
**Cambios:**
- Reemplazada **1 tarjeta grande** por **2 tarjetas paralelas** (grid-2)
- Cada tarjeta muestra:
  - Username del bot
  - Estado del webhook (activo/sin configurar)
  - Botón para configurar webhook individual
  - Enlace para abrir el bot en Telegram
- Agregado botón superior: **"🔄 Reconfigurar ambos"**
- Estado de configuración actualizado: `'leads' | 'admin' | 'ambos'`

**Funciones actualizadas:**
```typescript
const handleSetupWebhook = async (tipo: 'leads' | 'admin' | 'ambos') => {
    setConfiguringWebhook(tipo)
    
    let res
    if (tipo === 'ambos') res = await orbitaApi.setupWebhooks()
    else if (tipo === 'leads') res = await orbitaApi.setupLeadsWebhook()
    else if (tipo === 'admin') res = await orbitaApi.setupAdminWebhook()
    
    // ... resto del código
}
```

**Vista:**
```
[Página Telegram - Header]
Estado de los Bots                    [🔄 Reconfigurar ambos]

[Grid 2 columnas]
┌────────────────────┬────────────────────┐
│ Bot de Leads       │ Bot de Admin       │
│ 📱                 │ 🛸                 │
│ @orbita_lead_bot   │ @orbita_admin_bot  │
│ ● ACTIVO           │ ● ACTIVO           │
│ [🔗 Abrir][🔄]     │ [🔗 Abrir][🔄]     │
└────────────────────┴────────────────────┘
```

---

### 4. ✅ `src/pages/Configuracion.tsx`
**Cambios:**
- Sección de Telegram dividida en **2 bloques**:
  - 🟢 Tarjeta verde para bot de leads
  - 🔵 Tarjeta azul para bot de admin
- Cada tarjeta contiene:
  - Username del bot
  - Estado del webhook
  - Botón individual para configurar
  - Enlace para abrir en Telegram
- Header con botón: **"🔄 Ambos"** para configurar ambos webhooks

**Vista:**
```
[Configuración - Telegram]
📱 Configuración de Telegram             [🔄 Ambos]

┌─────────────────────────────────────┐
│ 📱 Bot de Leads                     │
│ Público para prospectos             │
│ ─────────────────────────────────── │
│ Username: @orbita_leads_bot         │
│ Webhook: ✅ Configurado             │
│ [🔄 Webhook] [🔗 Abrir]             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🛸 Bot de Admin                     │
│ Privado para equipo                 │
│ ─────────────────────────────────── │
│ Username: @orbita_admin_bot         │
│ Comandos: /leads /stats /alertas    │
│ [🔄 Webhook] [🔗 Abrir]             │
└─────────────────────────────────────┘
```

---

## 🎯 Funcionalidades implementadas

### ✅ API Client actualizado
- 3 funciones nuevas para configurar webhooks
- Soporte para nuevo formato de respuesta `{ bot_leads, bot_admin }`

### ✅ Sidebar con doble indicador
- Muestra estado de ambos bots en tiempo real
- Indicadores de color diferenciados (verde/azul)
- Labels "leads" y "admin" para claridad

### ✅ Página Telegram renovada
- 2 tarjetas paralelas con diseño consistente
- Configuración individual o conjunta de webhooks
- Estados independientes para cada bot

### ✅ Página Configuración mejorada
- Sección de bots completamente rediseñada
- Tarjetas visuales con colores distintivos
- Botones de acción individual por bot

---

## 🔄 Compatibilidad con backend

### Endpoints requeridos:
✅ `GET /api/v1/telegram/info`
  - Retorna: `{ success: true, data: { bot_leads: {...}, bot_admin: {...} } }`

✅ `POST /api/v1/telegram/setup-webhooks`
  - Configura ambos bots

✅ `POST /api/v1/telegram/setup-leads-webhook`
  - Configura solo bot de leads

✅ `POST /api/v1/telegram/setup-admin-webhook`
  - Configura solo bot de admin

---

## 🧪 Testing

### Para probar los cambios:

1. **Iniciar frontend:**
```bash
cd orbita_frontend
npm run dev
```

2. **Verificar Sidebar:**
   - Ir a cualquier página
   - Ver footer del sidebar
   - Deberías ver 2 indicadores de bots

3. **Verificar página Telegram:**
   - Ir a `/telegram`
   - Ver 2 tarjetas lado a lado
   - Probar botones de configuración

4. **Verificar página Configuración:**
   - Ir a `/configuracion`
   - Scrollear a sección "Configuración de Telegram"
   - Ver 2 bloques de configuración

---

## 📊 Resumen de líneas modificadas

| Archivo | Líneas cambiadas | Tipo de cambio |
|---------|------------------|----------------|
| `src/lib/api.ts` | ~20 | Funciones API |
| `src/components/Layout/Sidebar.tsx` | ~60 | Estado y UI |
| `src/pages/Telegram.tsx` | ~180 | UI completa |
| `src/pages/Configuracion.tsx` | ~140 | UI completa |
| **TOTAL** | **~400 líneas** | 4 archivos |

---

## ✅ Checklist de implementación

- [x] Actualizar funciones API en `api.ts`
- [x] Modificar Sidebar para mostrar 2 bots
- [x] Refactorizar página Telegram con 2 tarjetas
- [x] Refactorizar página Configuración con 2 bloques
- [x] Verificar que no hay errores de TypeScript
- [x] Documentar todos los cambios

---

## 🎉 RESULTADO FINAL

El frontend de ORBITA ahora está **completamente actualizado** para soportar la arquitectura de dual-bot:

✅ **Separación clara** entre bot público (leads) y bot privado (admin)
✅ **UI consistente** en todas las páginas
✅ **Configuración flexible** (individual o conjunta)
✅ **Estados independientes** para cada bot
✅ **Sin errores** de compilación

**El sistema está listo para trabajar con los 2 bots implementados en el backend.**

---

## 📝 Próximos pasos (opcionales)

1. **Testing de integración:**
   - Probar configuración de webhooks con backend real
   - Verificar que ambos bots se muestran correctamente
   - Testear flujos de conversación en ambos bots

2. **Mejoras futuras:**
   - Agregar indicador de "mensajes pendientes" por bot
   - Mostrar últimas 3 conversaciones en cada bot
   - Panel de estadísticas separadas por bot

3. **Documentación de usuario:**
   - Guía de uso del bot de leads
   - Guía de comandos del bot de admin
   - FAQs sobre configuración de webhooks
