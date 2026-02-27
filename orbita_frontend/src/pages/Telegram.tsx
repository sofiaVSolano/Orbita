import React, { useEffect, useRef, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'
import MetricCard from '../components/MetricCard'
import TelegramBubble from '../components/TelegramBubble'
import LoadingDots from '../components/LoadingDots'

// ── Types ─────────────────────────────────────────────────────
interface TelegramSession {
    id: string
    telegram_chat_id: string
    lead_id?: string
    estado_bot: string
    ultimo_mensaje_at: string
    lead?: {
        nombre: string
        empresa_nombre?: string
        etapa_funnel: string
    }
}

interface Msg {
    id: string
    role: string
    content: string
    content_type: string
    transcripcion_voz?: string
    agente?: string
    created_at: string
}

interface Notif {
    id: string
    tipo: string
    mensaje: string
    enviada: boolean
    created_at: string
    lead_id?: string
}

// ── Notif type icons ──────────────────────────────────────────
const notifTypeIcon: Record<string, string> = {
    nuevo_lead: '🆕',
    cotizacion_aceptada: '🎉',
    reunion_agendada: '📅',
    alerta: '⚠️',
}

// ── Component ─────────────────────────────────────────────────
const Telegram: React.FC = () => {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const [sessions, setSessions] = useState<TelegramSession[]>([])
    const [selectedSession, setSelectedSession] = useState<TelegramSession | null>(null)
    const [messages, setMessages] = useState<Msg[]>([])
    const [chatMsg, setChatMsg] = useState('')
    const [sending, setSending] = useState(false)
    const [configuringWebhook, setConfiguringWebhook] = useState(false)
    const [notificaciones, setNotificaciones] = useState<Notif[]>([])
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // Bot info
    const { data: botData, isLoading: botLoading, refetch: refetchBot } = useQuery({
        queryKey: ['botInfo'],
        queryFn: () => orbitaApi.getBotInfo(),
        retry: 1,
    })

    // TG metrics
    const { data: tgData, isLoading: tgLoading } = useQuery({
        queryKey: ['tgMetrics'],
        queryFn: () => orbitaApi.getTelegramMetrics(),
        refetchInterval: 60_000,
        retry: 1,
    })

    const bot = botData?.data || {}
    const tg = tgData?.data || {}

    // Load sessions with lead info
    useEffect(() => {
        const fetchSessions = async () => {
            const { data } = await supabase
                .from('telegram_bot_sessions')
                .select('*, lead:leads(nombre,empresa_nombre,etapa_funnel)')
                .eq('estado_bot', 'activo')
                .order('ultimo_mensaje_at', { ascending: false })
                .limit(50)
            setSessions(data || [])

            // Auto-select lead from URL
            const leadParam = searchParams.get('lead')
            if (leadParam && data) {
                const found = data.find((s: TelegramSession) => s.lead_id === leadParam)
                if (found) selectSession(found)
            }
        }
        fetchSessions()

        const ch = supabase
            .channel('tg-sessions')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'telegram_bot_sessions' }, fetchSessions)
            .subscribe()
        return () => { supabase.removeChannel(ch) }
    }, [])

    // Load notifications
    useEffect(() => {
        const fetch = async () => {
            const { data } = await supabase
                .from('notificaciones_admin')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(20)
            setNotificaciones(data || [])
        }
        fetch()
    }, [])

    const selectSession = async (session: TelegramSession) => {
        setSelectedSession(session)
        if (session.lead_id) {
            const { data } = await supabase
                .from('conversations')
                .select('*')
                .eq('lead_id', session.lead_id)
                .order('created_at')
                .limit(80)
            setMessages(data || [])
        }
    }

    // Realtime messages for selected session
    useEffect(() => {
        if (!selectedSession?.lead_id) return
        const ch = supabase
            .channel(`tg-msgs-${selectedSession.lead_id}`)
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'conversations', filter: `lead_id=eq.${selectedSession.lead_id}` },
                (p) => setMessages((prev) => [...prev, p.new as Msg])
            )
            .subscribe()
        return () => { supabase.removeChannel(ch) }
    }, [selectedSession?.lead_id])

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSendTelegram = async () => {
        if (!chatMsg.trim() || !selectedSession) return
        setSending(true)
        try {
            await orbitaApi.sendToTelegram(
                selectedSession.telegram_chat_id,
                chatMsg,
                selectedSession.lead_id || ''
            )
            toast.success('📱 Mensaje enviado por Telegram', { style: { color: 'var(--blue)' } })
            setChatMsg('')
        } catch {
            toast.error('Error al enviar por Telegram')
        } finally {
            setSending(false)
        }
    }

    const handleSetupWebhook = async () => {
        setConfiguringWebhook(true)
        try {
            const res = await orbitaApi.setupWebhook()
            if (res?.success) {
                toast.success('🔗 Webhook configurado exitosamente', { description: res.webhook_url })
                refetchBot()
            } else {
                toast.error('Error al configurar webhook')
            }
        } catch {
            toast.error('No se pudo conectar al backend')
        } finally {
            setConfiguringWebhook(false)
        }
    }

    const metrics = [
        { label: 'Chats Activos Hoy', value: tg.total_chats_activos ?? '—', color: 'blue' as const, icon: '💬' },
        { label: 'Mensajes Procesados', value: tg.mensajes_hoy ?? '—', color: 'green' as const, icon: '✉️' },
        { label: 'Leads Captados', value: tg.leads_captados_telegram ?? '—', color: 'pink' as const, icon: '👤' },
        { label: 'Voces Transcritas', value: tg.notas_de_voz_procesadas ?? '—', color: 'purple' as const, icon: '🎙️' },
        { label: 'Cotizaciones TG', value: tg.cotizaciones_enviadas_telegram ?? '—', color: 'blue' as const, icon: '📄' },
        { label: 'Reuniones TG', value: tg.reuniones_confirmadas_telegram ?? '—', color: 'green' as const, icon: '📅' },
    ]

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <h1>📱 Telegram — Control del Bot y Conversaciones</h1>
                <p className="text-muted">Gestiona el bot, responde desde el dashboard y monitorea métricas en tiempo real</p>
            </div>

            {/* Bot Status Card */}
            <div className="card card--blue fade-up mb-6">
                <div className="flex items-center justify-between" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                    <div className="flex items-center gap-4">
                        <div
                            style={{
                                width: 52,
                                height: 52,
                                borderRadius: '50%',
                                background: 'rgba(0,209,255,0.15)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 24,
                                border: '1px solid rgba(0,209,255,0.3)',
                                flexShrink: 0,
                            }}
                        >
                            📱
                        </div>
                        <div>
                            <div style={{ fontWeight: 700, fontSize: 16 }}>
                                {botLoading ? '...' : (bot.bot_nombre || 'ORBITA Bot')}
                            </div>
                            <div className="text-muted" style={{ fontSize: 13 }}>
                                @{botLoading ? '...' : (bot.bot_username || 'orbita_bot')}
                            </div>
                            {bot.webhook_url && (
                                <div className="text-muted" style={{ fontSize: 11, marginTop: 2 }}>
                                    Webhook: <span className="font-mono">{bot.webhook_url}</span>
                                </div>
                            )}
                            {bot.pending_updates !== undefined && (
                                <div className="text-muted" style={{ fontSize: 11 }}>
                                    Updates en cola: <span className="font-mono text-blue">{bot.pending_updates}</span>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center gap-3" style={{ flexWrap: 'wrap' }}>
                        <div className="flex items-center gap-2">
                            <span className={`dot-pulse dot-pulse--${bot.activo ? 'green' : 'red'}`} />
                            <span className="badge" style={{
                                background: bot.activo ? 'rgba(80,250,123,0.15)' : 'rgba(255,80,80,0.15)',
                                color: bot.activo ? 'var(--green)' : '#FF5050',
                            }}>
                                {botLoading ? '...' : (bot.activo ? '● ACTIVO' : '○ INACTIVO')}
                            </span>
                        </div>
                        <button
                            className="btn btn--blue"
                            onClick={handleSetupWebhook}
                            disabled={configuringWebhook}
                        >
                            {configuringWebhook ? (
                                <span
                                    style={{ width: 12, height: 12, border: '2px solid transparent', borderTopColor: 'var(--blue)', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block' }}
                                />
                            ) : '🔄'} Reconfigurar Webhook
                        </button>
                        {bot.bot_username && (
                            <a
                                href={`https://t.me/${bot.bot_username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn--secondary"
                            >
                                🔗 Abrir en Telegram
                            </a>
                        )}
                    </div>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid-6 mb-6">
                {metrics.map((m, i) => (
                    <MetricCard
                        key={m.label}
                        label={m.label}
                        value={m.value}
                        color={m.color}
                        icon={m.icon}
                        loading={tgLoading}
                        delay={i * 0.05}
                    />
                ))}
            </div>

            {/* Conversations table + Panel */}
            <div className="grid-2 mb-6" style={{ gridTemplateColumns: '1fr 1.4fr', gap: '1rem' }}>
                {/* Sessions Table */}
                <div className="card fade-up" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '0.875rem 1rem', borderBottom: '1px solid var(--border)' }}>
                        <h3 style={{ fontSize: 14 }}>Conversaciones Activas por Telegram</h3>
                    </div>
                    <div className="table-container" style={{ maxHeight: 400, overflowY: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>Lead</th>
                                    <th>Etapa</th>
                                    <th>Chat ID</th>
                                    <th>Últ. mensaje</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="text-muted" style={{ textAlign: 'center', padding: '2rem' }}>
                                            Sin sesiones activas
                                        </td>
                                    </tr>
                                ) : (
                                    sessions.map((session) => (
                                        <tr
                                            key={session.id}
                                            style={{
                                                cursor: 'pointer',
                                                background: selectedSession?.id === session.id ? 'rgba(0,209,255,0.06)' : 'transparent',
                                            }}
                                            onClick={() => selectSession(session)}
                                        >
                                            <td>
                                                <div style={{ fontWeight: 600, fontSize: 12 }}>
                                                    {session.lead?.nombre || 'Sin nombre'}
                                                </div>
                                                <div className="text-muted" style={{ fontSize: 10 }}>
                                                    {session.lead?.empresa_nombre || '—'}
                                                </div>
                                            </td>
                                            <td>
                                                {session.lead?.etapa_funnel && (
                                                    <span className="badge badge--blue" style={{ fontSize: 8 }}>
                                                        {session.lead.etapa_funnel.toUpperCase()}
                                                    </span>
                                                )}
                                            </td>
                                            <td className="font-mono text-muted" style={{ fontSize: 10 }}>
                                                {session.telegram_chat_id}
                                            </td>
                                            <td className="text-muted" style={{ fontSize: 10 }}>
                                                {formatDistanceToNow(new Date(session.ultimo_mensaje_at), { addSuffix: true, locale: es })}
                                            </td>
                                            <td onClick={(e) => e.stopPropagation()}>
                                                <div className="flex gap-1">
                                                    <button
                                                        className="btn btn--sm btn--blue"
                                                        title="Responder vía Telegram"
                                                        onClick={() => selectSession(session)}
                                                    >
                                                        💬
                                                    </button>
                                                    {session.lead_id && (
                                                        <button
                                                            className="btn btn--sm btn--secondary"
                                                            title="Ver en CRM"
                                                            onClick={() => navigate(`/leads?id=${session.lead_id}`)}
                                                        >
                                                            👁️
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Chat Panel */}
                {selectedSession ? (
                    <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden', maxHeight: 500 }}>
                        {/* Chat Header */}
                        <div style={{ padding: '0.875rem 1rem', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
                            <div className="flex items-center justify-between">
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: 14 }}>
                                        {selectedSession.lead?.nombre || 'Lead desconocido'}
                                    </div>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="font-mono text-muted" style={{ fontSize: 10 }}>
                                            {selectedSession.telegram_chat_id}
                                        </span>
                                        {selectedSession.lead?.etapa_funnel && (
                                            <span className="badge badge--blue" style={{ fontSize: 8 }}>
                                                {selectedSession.lead.etapa_funnel.toUpperCase()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    className="btn btn--sm btn--secondary"
                                    onClick={() => setSelectedSession(null)}
                                >✕</button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
                            {messages.length === 0 ? (
                                <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 12 }}>
                                    Sin mensajes en este chat
                                </div>
                            ) : (
                                messages.map((msg) => (
                                    <TelegramBubble
                                        key={msg.id}
                                        role={msg.role === 'user' ? 'user' : msg.agente === 'admin_manual' ? 'admin' : 'agent'}
                                        content={msg.content}
                                        agente={msg.agente}
                                        isVoice={msg.content_type === 'voice'}
                                        transcription={msg.transcripcion_voz}
                                        timestamp={formatDistanceToNow(new Date(msg.created_at), { addSuffix: true, locale: es })}
                                    />
                                ))
                            )}
                            {sending && (
                                <div className="flex items-center gap-2">
                                    <span className="text-muted" style={{ fontSize: 12 }}>Enviando...</span>
                                    <LoadingDots />
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div style={{ padding: '0.875rem 1rem', borderTop: '1px solid var(--border)', flexShrink: 0 }}>
                            <div className="flex gap-2">
                                <input
                                    className="input"
                                    value={chatMsg}
                                    onChange={(e) => setChatMsg(e.target.value)}
                                    placeholder="Enviar mensaje por Telegram..."
                                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleSendTelegram() } }}
                                    disabled={sending}
                                />
                                <button
                                    className="btn btn--blue"
                                    onClick={handleSendTelegram}
                                    disabled={sending || !chatMsg.trim()}
                                >
                                    📱 Enviar
                                </button>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            <div style={{ fontSize: 36, marginBottom: 12 }}>📱</div>
                            <div style={{ fontSize: 14, fontWeight: 600 }}>Selecciona una conversación</div>
                            <div style={{ fontSize: 12, marginTop: 4 }}>Haz clic en 💬 para responder via Telegram</div>
                        </div>
                    </div>
                )}
            </div>

            {/* Notifications History */}
            <div className="card fade-up mb-6">
                <h3 style={{ marginBottom: '1rem' }}>Historial de Notificaciones al Admin</h3>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Tipo</th>
                                <th>Mensaje</th>
                                <th>Estado</th>
                                <th>Fecha</th>
                            </tr>
                        </thead>
                        <tbody>
                            {notificaciones.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="text-muted" style={{ textAlign: 'center', padding: '1.5rem' }}>
                                        Sin notificaciones
                                    </td>
                                </tr>
                            ) : (
                                notificaciones.map((n) => (
                                    <tr key={n.id}>
                                        <td>
                                            <span style={{ fontSize: 14, marginRight: 4 }}>
                                                {notifTypeIcon[n.tipo] || '🔔'}
                                            </span>
                                            <span className="badge badge--muted" style={{ fontSize: 9 }}>{n.tipo}</span>
                                        </td>
                                        <td style={{ maxWidth: 300, fontSize: 12 }} className="truncate">{n.mensaje}</td>
                                        <td>
                                            <span className={`badge ${n.enviada ? 'badge--green' : 'badge--muted'}`}>
                                                {n.enviada ? '✓ enviada' : '⏳ pendiente'}
                                            </span>
                                        </td>
                                        <td className="text-muted" style={{ fontSize: 11 }}>
                                            {formatDistanceToNow(new Date(n.created_at), { addSuffix: true, locale: es })}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Bot Commands Reference */}
            <div className="card fade-up">
                <h3 style={{ marginBottom: '1rem' }}>📋 Comandos del Bot</h3>
                <div className="grid-2">
                    <div>
                        <div className="form-label mb-2">Para el Lead</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            {[
                                { cmd: '/start', desc: 'Iniciar conversación con el bot' },
                                { cmd: '/cotizacion', desc: 'Solicitar una cotización personalizada' },
                                { cmd: '/reunion', desc: 'Agendar una reunión de demostración' },
                                { cmd: '/ayuda', desc: 'Ver opciones disponibles' },
                            ].map((c) => (
                                <div key={c.cmd} style={{ display: 'flex', gap: 8, padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 4 }}>
                                    <code className="font-mono" style={{ color: 'var(--green)', fontSize: 12, flexShrink: 0 }}>{c.cmd}</code>
                                    <span className="text-muted" style={{ fontSize: 12 }}>{c.desc}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <div className="form-label mb-2">Para el Admin</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            {[
                                { cmd: '/stats', desc: 'Ver estadísticas del día' },
                                { cmd: '/leads', desc: 'Ver leads activos' },
                                { cmd: '/alertas', desc: 'Ver alertas del sistema' },
                            ].map((c) => (
                                <div key={c.cmd} style={{ display: 'flex', gap: 8, padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 4 }}>
                                    <code className="font-mono" style={{ color: 'var(--pink)', fontSize: 12, flexShrink: 0 }}>{c.cmd}</code>
                                    <span className="text-muted" style={{ fontSize: 12 }}>{c.desc}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Telegram
