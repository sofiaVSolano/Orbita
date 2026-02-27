# ORBITA — Ajustes Frontend para Arquitectura Dual-Bot
## 4 cambios exactos con código completo

---

## CAMBIO 1 — src/lib/api.ts

Solo 2 funciones cambian. Buscar y reemplazar:

```typescript
// ANTES — líneas que dicen setupWebhook y getBotInfo:
getBotInfo: () =>
  fetch(`${API}/api/v1/telegram/info`, { headers: h() }).then(r => r.json()),

setupWebhook: () =>
  fetch(`${API}/api/v1/telegram/setup-webhook`, {
    method: 'POST', headers: h()
  }).then(r => r.json()),


// DESPUÉS — reemplazar esas dos por estas tres:
getBotInfo: () =>
  fetch(`${API}/api/v1/telegram/info`, { headers: h() }).then(r => r.json()),
  // Ahora retorna: { success: true, data: { bot_leads: {...}, bot_admin: {...} } }

setupWebhooks: () =>
  fetch(`${API}/api/v1/telegram/setup-webhooks`, {
    method: 'POST', headers: h()
  }).then(r => r.json()),
  // Configura AMBOS bots en un solo click

setupLeadsWebhook: () =>
  fetch(`${API}/api/v1/telegram/setup-leads-webhook`, {
    method: 'POST', headers: h()
  }).then(r => r.json()),

setupAdminWebhook: () =>
  fetch(`${API}/api/v1/telegram/setup-admin-webhook`, {
    method: 'POST', headers: h()
  }).then(r => r.json()),
```

---

## CAMBIO 2 — Sidebar (donde dice "Telegram: @bot_username")

Buscar el componente del sidebar donde se muestra el estado del bot.
Suele estar en `src/components/Sidebar.tsx` o `src/layouts/AppLayout.tsx`.

```tsx
// ANTES — algo como esto:
const { data: botInfo } = useQuery({
  queryKey: ['botInfo'],
  queryFn: () => orbitaApi.getBotInfo(),
  refetchInterval: 30000
})

// En el JSX:
<span className="text-xs text-muted-foreground">
  Telegram: @{botInfo?.data?.bot_username}
</span>
<span className={`w-2 h-2 rounded-full ${botInfo?.data?.activo ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />


// DESPUÉS — mostrar solo el bot de leads (el público) en el sidebar:
const { data: botInfo } = useQuery({
  queryKey: ['botInfo'],
  queryFn: () => orbitaApi.getBotInfo(),
  refetchInterval: 30000
})

// Extraer solo bot_leads del nuevo formato de respuesta
const botLeads = botInfo?.data?.bot_leads
const botAdmin = botInfo?.data?.bot_admin

// En el JSX — reemplazar el bloque anterior por:
<div className="flex flex-col gap-1">
  {/* Bot de leads — el que ven los prospectos */}
  <div className="flex items-center gap-2">
    <span
      className={`w-2 h-2 rounded-full flex-shrink-0 ${
        botLeads?.webhook_url ? 'bg-green-400 animate-pulse' : 'bg-red-400'
      }`}
    />
    <span className="text-xs text-muted-foreground truncate">
      {botLeads?.username ? `@${botLeads.username}` : 'Bot leads sin config'}
    </span>
    <span className="text-xs text-blue-400 opacity-60">leads</span>
  </div>

  {/* Bot de admin — indicador discreto */}
  <div className="flex items-center gap-2">
    <span
      className={`w-2 h-2 rounded-full flex-shrink-0 ${
        botAdmin?.webhook_url ? 'bg-blue-400' : 'bg-gray-600'
      }`}
    />
    <span className="text-xs text-muted-foreground truncate opacity-60">
      {botAdmin?.username ? `@${botAdmin.username}` : 'Bot admin sin config'}
    </span>
    <span className="text-xs text-purple-400 opacity-60">admin</span>
  </div>
</div>
```

---

## CAMBIO 3 — Página /telegram (BotStatusCard y métricas)

Buscar el archivo de la página, probablemente `src/pages/Telegram.tsx`.

```tsx
// ANTES — BotStatusCard recibía datos planos:
const { data: botInfo, refetch: refetchBot } = useQuery({
  queryKey: ['botInfo'],
  queryFn: () => orbitaApi.getBotInfo()
})

// Y se usaba así:
<BotStatusCard
  username={botInfo?.data?.bot_username}
  isActive={!!botInfo?.data?.webhook_url}
  // ...
/>

<button onClick={() => orbitaApi.setupWebhook()}>
  🔄 Reconfigurar Webhook
</button>


// DESPUÉS — separar en dos cards con datos del nuevo formato:
const { data: botInfo, refetch: refetchBot, isLoading } = useQuery({
  queryKey: ['botInfo'],
  queryFn: () => orbitaApi.getBotInfo(),
  refetchInterval: 15000
})

const botLeads = botInfo?.data?.bot_leads
const botAdmin  = botInfo?.data?.bot_admin

const [configurando, setConfigurando] = useState<'leads' | 'admin' | 'ambos' | null>(null)

const handleSetupWebhooks = async (tipo: 'leads' | 'admin' | 'ambos') => {
  setConfigurando(tipo)
  try {
    if (tipo === 'ambos')  await orbitaApi.setupWebhooks()
    if (tipo === 'leads')  await orbitaApi.setupLeadsWebhook()
    if (tipo === 'admin')  await orbitaApi.setupAdminWebhook()
    await refetchBot()
    toast.success('Webhook configurado correctamente')
  } catch {
    toast.error('Error configurando webhook')
  } finally {
    setConfigurando(null)
  }
}

// JSX — reemplazar la sección "Estado del Bot" por:
<section className="mb-8">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-lg font-semibold text-white">Estado de los Bots</h2>
    <button
      onClick={() => handleSetupWebhooks('ambos')}
      disabled={configurando === 'ambos'}
      className="text-xs px-3 py-1.5 rounded border border-white/10
                 text-muted-foreground hover:text-white hover:border-white/30
                 transition-all disabled:opacity-50"
    >
      {configurando === 'ambos' ? '⏳ Configurando...' : '🔄 Reconfigurar ambos'}
    </button>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

    {/* ── Card Bot de Leads ── */}
    <div className="rounded-md border border-green-500/20 bg-[#1A1626] p-5
                    shadow-[0_0_20px_rgba(80,250,123,0.06)]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📱</span>
          <div>
            <p className="text-sm font-semibold text-white">Bot de Leads</p>
            <p className="text-xs text-muted-foreground">Visible para prospectos</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${
            botLeads?.webhook_url
              ? 'bg-green-400 animate-pulse'
              : 'bg-red-500'
          }`} />
          <span className={`text-xs font-mono uppercase tracking-wider ${
            botLeads?.webhook_url ? 'text-green-400' : 'text-red-400'
          }`}>
            {botLeads?.webhook_url ? 'ACTIVO' : 'SIN CONFIG'}
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Username</span>
          <span className="text-white font-mono">
            {botLeads?.username ? `@${botLeads.username}` : '—'}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Updates pendientes</span>
          <span className="text-white">{botLeads?.pending_updates ?? '—'}</span>
        </div>
      </div>

      <div className="flex gap-2">
        {botLeads?.link && (
          <a
            href={botLeads.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center text-xs py-1.5 rounded border
                       border-green-500/30 text-green-400 hover:bg-green-500/10
                       transition-all"
          >
            🔗 Abrir bot
          </a>
        )}
        <button
          onClick={() => handleSetupWebhooks('leads')}
          disabled={configurando === 'leads'}
          className="flex-1 text-xs py-1.5 rounded border border-white/10
                     text-muted-foreground hover:text-white hover:border-white/30
                     transition-all disabled:opacity-50"
        >
          {configurando === 'leads' ? '⏳' : '🔄 Webhook'}
        </button>
      </div>
    </div>

    {/* ── Card Bot de Admin ── */}
    <div className="rounded-md border border-blue-500/20 bg-[#1A1626] p-5
                    shadow-[0_0_20px_rgba(0,209,255,0.06)]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🛸</span>
          <div>
            <p className="text-sm font-semibold text-white">Bot de Admin</p>
            <p className="text-xs text-muted-foreground">Solo equipo interno</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${
            botAdmin?.webhook_url
              ? 'bg-blue-400 animate-pulse'
              : 'bg-red-500'
          }`} />
          <span className={`text-xs font-mono uppercase tracking-wider ${
            botAdmin?.webhook_url ? 'text-blue-400' : 'text-red-400'
          }`}>
            {botAdmin?.webhook_url ? 'ACTIVO' : 'SIN CONFIG'}
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Username</span>
          <span className="text-white font-mono">
            {botAdmin?.username ? `@${botAdmin.username}` : '—'}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Comandos</span>
          <span className="text-white font-mono text-xs">
            /leads /stats /alertas /pausa
          </span>
        </div>
      </div>

      <div className="flex gap-2">
        {botAdmin?.link && (
          <a
            href={botAdmin.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center text-xs py-1.5 rounded border
                       border-blue-500/30 text-blue-400 hover:bg-blue-500/10
                       transition-all"
          >
            🔗 Abrir bot
          </a>
        )}
        <button
          onClick={() => handleSetupWebhooks('admin')}
          disabled={configurando === 'admin'}
          className="flex-1 text-xs py-1.5 rounded border border-white/10
                     text-muted-foreground hover:text-white hover:border-white/30
                     transition-all disabled:opacity-50"
        >
          {configurando === 'admin' ? '⏳' : '🔄 Webhook'}
        </button>
      </div>
    </div>

  </div>
</section>
```

---

## CAMBIO 4 — Página /configuracion (sección Telegram)

Buscar el archivo `src/pages/Configuracion.tsx` o similar.

```tsx
// ANTES — una sola card de Telegram:
<div className="border border-blue-500/30 rounded-md p-5 bg-[#1A1626]">
  <h3 className="font-semibold text-white mb-3">📱 Configuración de Telegram</h3>
  <div className="space-y-2 text-sm mb-4">
    <div className="flex justify-between">
      <span className="text-muted-foreground">Bot Username</span>
      <span className="text-white font-mono">@{botInfo?.data?.bot_username}</span>
    </div>
    {/* ... */}
  </div>
  <button onClick={() => orbitaApi.setupWebhook()}>
    🔄 Reconfigurar Webhook
  </button>
</div>


// DESPUÉS — dos cards separadas:
// Agregar el hook de botInfo si no estaba en esta página:
const { data: botInfo } = useQuery({
  queryKey: ['botInfo'],
  queryFn: () => orbitaApi.getBotInfo()
})
const botLeads = botInfo?.data?.bot_leads
const botAdmin  = botInfo?.data?.bot_admin

// JSX — reemplazar la card antigua por:
<div className="space-y-4">
  <h3 className="font-semibold text-white">📱 Configuración de Telegram</h3>
  <p className="text-sm text-muted-foreground">
    ORBITA usa dos bots separados. El de leads es el que compartes
    públicamente. El de admin es exclusivo de tu equipo.
  </p>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

    {/* ── Bot de Leads ── */}
    <div className="border border-green-500/20 rounded-md p-4 bg-[#0D0B14]">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-green-400">📱</span>
        <span className="text-sm font-semibold text-white">Bot de Leads</span>
        <span className="ml-auto text-xs font-mono text-green-400 bg-green-400/10
                         px-2 py-0.5 rounded">
          PÚBLICO
        </span>
      </div>

      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Username</span>
          <span className="font-mono text-white">
            {botLeads?.username ? `@${botLeads.username}` : 'Sin configurar'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Webhook</span>
          <span className={`text-xs ${botLeads?.webhook_url ? 'text-green-400' : 'text-red-400'}`}>
            {botLeads?.webhook_url ? '✓ Activo' : '✗ No configurado'}
          </span>
        </div>
      </div>

      {/* Instrucciones rápidas */}
      <div className="text-xs text-muted-foreground space-y-1 mb-4
                      border-t border-white/5 pt-3">
        <p className="font-medium text-white/70 mb-1">Cómo configurar:</p>
        <p>1. Crea el bot en @BotFather con /newbot</p>
        <p>2. Pega el token en TELEGRAM_LEADS_BOT_TOKEN del .env</p>
        <p>3. Reinicia el servidor</p>
        <p>4. Haz clic en "Configurar Webhook"</p>
      </div>

      <div className="flex gap-2">
        {botLeads?.link && (
          <a
            href={botLeads.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center text-xs py-2 rounded border
                       border-green-500/30 text-green-400
                       hover:bg-green-500/10 transition-all"
          >
            🔗 {botLeads?.username ? `@${botLeads.username}` : 'Ver bot'}
          </a>
        )}
        <button
          onClick={() => orbitaApi.setupLeadsWebhook().then(() => toast.success('Webhook leads configurado'))}
          className="flex-1 text-xs py-2 rounded border border-white/10
                     text-muted-foreground hover:text-white
                     hover:border-white/30 transition-all"
        >
          🔄 Configurar Webhook
        </button>
      </div>
    </div>

    {/* ── Bot de Admin ── */}
    <div className="border border-blue-500/20 rounded-md p-4 bg-[#0D0B14]">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-blue-400">🛸</span>
        <span className="text-sm font-semibold text-white">Bot de Admin</span>
        <span className="ml-auto text-xs font-mono text-blue-400 bg-blue-400/10
                         px-2 py-0.5 rounded">
          PRIVADO
        </span>
      </div>

      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Username</span>
          <span className="font-mono text-white">
            {botAdmin?.username ? `@${botAdmin.username}` : 'Sin configurar'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Webhook</span>
          <span className={`text-xs ${botAdmin?.webhook_url ? 'text-blue-400' : 'text-red-400'}`}>
            {botAdmin?.webhook_url ? '✓ Activo' : '✗ No configurado'}
          </span>
        </div>
      </div>

      {/* Instrucciones rápidas */}
      <div className="text-xs text-muted-foreground space-y-1 mb-4
                      border-t border-white/5 pt-3">
        <p className="font-medium text-white/70 mb-1">Cómo configurar:</p>
        <p>1. Crea otro bot en @BotFather</p>
        <p>2. Pega el token en TELEGRAM_ADMIN_BOT_TOKEN del .env</p>
        <p>3. Agrega tu Chat ID en TELEGRAM_ADMIN_CHAT_IDS</p>
        <p className="text-white/40">   (obtenlo escribiendo a @userinfobot)</p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => orbitaApi.setupAdminWebhook().then(() => toast.success('Webhook admin configurado'))}
          className="flex-1 text-xs py-2 rounded border border-white/10
                     text-muted-foreground hover:text-white
                     hover:border-white/30 transition-all"
        >
          🔄 Configurar Webhook
        </button>
      </div>
    </div>
  </div>

  {/* Admins registrados */}
  <div className="border border-white/5 rounded-md p-4 bg-[#0D0B14]">
    <p className="text-sm font-medium text-white mb-2">
      👥 Chat IDs de Admins registrados
    </p>
    <p className="text-xs text-muted-foreground mb-3">
      Estos son los usuarios que reciben alertas y pueden usar el bot de admin.
      Para agregar más, edita TELEGRAM_ADMIN_CHAT_IDS en el .env del servidor.
    </p>
    <div className="flex flex-wrap gap-2">
      {/* Mostrar los chat IDs configurados — viene del backend */}
      {botAdmin?.webhook_url ? (
        <span className="text-xs font-mono bg-white/5 border border-white/10
                         px-3 py-1 rounded text-muted-foreground">
          Configurados en .env del servidor
        </span>
      ) : (
        <span className="text-xs text-muted-foreground italic">
          Sin admins configurados aún
        </span>
      )}
    </div>
  </div>
</div>
```

---

## RESUMEN DE LOS 4 CAMBIOS

| Archivo | Qué cambia | Complejidad |
|---|---|---|
| `src/lib/api.ts` | `setupWebhook` → `setupWebhooks` + 2 nuevas funciones | ⭐ Muy fácil |
| Sidebar | Mostrar 2 indicadores (leads + admin) | ⭐⭐ Fácil |
| `/telegram` | Reemplazar `BotStatusCard` por 2 cards con datos separados | ⭐⭐⭐ Medio |
| `/configuracion` | Reemplazar card única por 2 cards + sección de admins | ⭐⭐⭐ Medio |

**Orden recomendado para implementar:**
1. `api.ts` primero — todo lo demás depende de que las funciones existan
2. `/configuracion` — más simple, sin estado complejo
3. `/telegram` — más código pero mismo patrón
4. Sidebar — al final, solo ajustar qué campo del objeto se muestra
