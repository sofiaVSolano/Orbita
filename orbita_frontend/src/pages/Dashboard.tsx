import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'
import MetricCard from '../components/MetricCard'
import BotStatusCard from '../components/BotStatusCard'
import AidaFunnel from '../components/AidaFunnel'

// ── Types ─────────────────────────────────────────────────────
interface AgentLog {
    id: string
    agente: string
    accion: string
    duracion_ms?: number
    exitoso: boolean
    created_at: string
    telegram_chat_id?: string
}

interface Lead {
    id: string
    nombre: string
    empresa_nombre?: string
    prioridad: string
    etapa_funnel: string
    ultimo_contacto: string
    telegram_chat_id?: string
    fuente: string
}

interface Alerta {
    tipo: string
    mensaje: string
    prioridad: 'alta' | 'media' | 'baja'
    lead_ids_afectados?: string[]
    accion_recomendada?: string
}

// ── Helpers ───────────────────────────────────────────────────
const priorityColor = (p: string) =>
    p === 'alta' ? 'var(--pink)' : p === 'media' ? '#FFA032' : 'var(--text-muted)'

// ── Component ─────────────────────────────────────────────────
const Dashboard: React.FC = () => {
    const navigate = useNavigate()
    const [agentLogs, setAgentLogs] = useState<AgentLog[]>([])
    const [alertas, setAlertas] = useState<Alerta[]>([])
    const [analyzingAlerts, setAnalyzingAlerts] = useState(false)
    const [aida, setAida] = useState({ atencion: 0, interes: 0, deseo: 0, accion: 0 })
    const [urgentLeads, setUrgentLeads] = useState<Lead[]>([])

    // Dashboard metrics from API
    const { data: dashboardData, isLoading: dashLoading } = useQuery({
        queryKey: ['dashboard'],
        queryFn: () => orbitaApi.getDashboard(),
        refetchInterval: 60_000,
    })

    // Bot info
    const { data: botInfo, isLoading: botLoading } = useQuery({
        queryKey: ['botInfo'],
        queryFn: () => orbitaApi.getBotInfo(),
        refetchInterval: 120_000,
    })

    // Telegram metrics
    const { data: tgMetrics, isLoading: tgLoading } = useQuery({
        queryKey: ['telegramMetrics'],
        queryFn: () => orbitaApi.getTelegramMetrics(),
        refetchInterval: 60_000,
    })

    // Load AIDA funnel from Supabase
    useEffect(() => {
        const fetchAida = async () => {
            const etapas = ['atencion', 'interes', 'deseo', 'accion']
            const counts = await Promise.all(
                etapas.map((e) =>
                    supabase
                        .from('leads')
                        .select('id', { count: 'exact', head: true })
                        .eq('etapa_funnel', e)
                        .then(({ count }) => count || 0)
                )
            )
            setAida({
                atencion: counts[0],
                interes: counts[1],
                deseo: counts[2],
                accion: counts[3],
            })
        }
        fetchAida()
    }, [])

    // Load urgent leads from Supabase
    useEffect(() => {
        const fetchUrgent = async () => {
            const cutoff = new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
            const { data } = await supabase
                .from('leads')
                .select('*')
                .eq('prioridad', 'alta')
                .lt('ultimo_contacto', cutoff)
                .neq('estado', 'inactivo')
                .order('ultimo_contacto', { ascending: true })
                .limit(5)
            setUrgentLeads(data || [])
        }
        fetchUrgent()
    }, [])

    // Load + realtime agent_logs
    useEffect(() => {
        const fetchLogs = async () => {
            const { data } = await supabase
                .from('agent_logs')
                .select('id,agente,accion,duracion_ms,exitoso,created_at,telegram_chat_id')
                .order('created_at', { ascending: false })
                .limit(10)
            setAgentLogs(data || [])
        }
        fetchLogs()

        const channel = supabase
            .channel('dashboard-logs')
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'agent_logs' },
                (payload) => {
                    setAgentLogs((prev) => [payload.new as AgentLog, ...prev.slice(0, 9)])
                }
            )
            .subscribe()

        return () => { supabase.removeChannel(channel) }
    }, [])

    const handleRunAnalytics = async () => {
        setAnalyzingAlerts(true)
        try {
            const res = await orbitaApi.runAnalytics('diario')
            if (res?.data?.alertas) {
                setAlertas(res.data.alertas)
                toast.success('📊 Análisis completado', { description: res.data.resumen_ejecutivo })
            } else {
                toast.info('Análisis completado. Sin alertas nuevas.')
            }
        } catch {
            toast.error('Error al conectar con el Agente Analítico')
        } finally {
            setAnalyzingAlerts(false)
        }
    }

    // Extract metrics
    const d = dashboardData?.data || {}
    const tg = tgMetrics?.data || {}
    const bot = botInfo?.data || {}

    const metrics = [
        { label: 'Leads Total', value: d.leads_total ?? '—', color: 'green' as const, icon: '👥', delay: 0 },
        { label: 'Leads Hoy', value: d.leads_hoy ?? '—', color: 'pink' as const, icon: '📅', delay: 0.05 },
        { label: 'Tasa Conversión', value: d.tasa_conversion ? `${d.tasa_conversion}%` : '—', color: 'blue' as const, icon: '📈', delay: 0.1 },
        { label: 'Cotizaciones Pendientes', value: d.cotizaciones_pendientes ?? '—', color: 'purple' as const, icon: '📄', delay: 0.15 },
        { label: 'Reuniones Próximas', value: d.reuniones_proximas ?? '—', color: 'green' as const, icon: '🗓️', delay: 0.2 },
        { label: 'Chats Telegram Hoy', value: tg.mensajes_hoy ?? '—', color: 'pink' as const, icon: '📱', delay: 0.25 },
    ]

    return (
        <div>
            {/* Page Header */}
            <div className="page-header fade-up">
                <div style={{ marginBottom: '0.5rem' }}>
                    <span className="badge badge--green">
                        ● SISTEMA ACTIVO · AI FIRST HACKATHON 2026
                    </span>
                </div>
                <h1 style={{ marginBottom: '0.25rem' }}>ORBITA Dashboard</h1>
                <p className="text-muted" style={{ fontSize: 15 }}>
                    Sistema Inteligente Autónomo para Empresas de Servicios
                </p>
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
                        loading={dashLoading && i < 5 || tgLoading && i === 5}
                        delay={m.delay}
                    />
                ))}
            </div>

            {/* Row: AIDA Funnel + Telegram Bot */}
            <div className="grid-2 mb-6" style={{ gridTemplateColumns: '1fr 1fr' }}>
                {/* AIDA Funnel */}
                <div className="card fade-up fade-up--2">
                    <div className="flex items-center justify-between mb-4">
                        <h3>Embudo AIDA</h3>
                        <span className="badge badge--muted">Supabase RT</span>
                    </div>
                    <AidaFunnel
                        atencion={aida.atencion}
                        interes={aida.interes}
                        deseo={aida.deseo}
                        accion={aida.accion}
                    />
                </div>

                {/* Telegram Bot Status */}
                <div className="fade-up fade-up--3">
                    <BotStatusCard
                        username={bot.bot_username || 'orbita_bot'}
                        nombre={bot.bot_nombre || 'ORBITA Bot'}
                        isActive={bot.activo || false}
                        leadsHoy={tg.leads_captados_telegram ?? 0}
                        mensajesHoy={tg.mensajes_hoy ?? 0}
                        vocesHoy={tg.notas_de_voz_procesadas ?? 0}
                        loading={botLoading || tgLoading}
                        onNavigate={() => navigate('/telegram')}
                    />
                </div>
            </div>

            {/* Row: Agent Activity + Urgent Leads */}
            <div className="grid-2 mb-6">
                {/* Agent Activity */}
                <div className="card fade-up fade-up--4">
                    <div className="flex items-center justify-between mb-4">
                        <h3>Actividad de Agentes</h3>
                        <span className="badge badge--blue">
                            <span className="dot-pulse dot-pulse--blue" style={{ width: 5, height: 5 }} />
                            Tiempo real
                        </span>
                    </div>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Agente</th>
                                    <th>Acción</th>
                                    <th>Duración</th>
                                    <th>✓/✗</th>
                                </tr>
                            </thead>
                            <tbody>
                                {agentLogs.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="text-muted" style={{ textAlign: 'center', padding: '1.5rem' }}>
                                            Sin actividad reciente
                                        </td>
                                    </tr>
                                ) : (
                                    agentLogs.map((log) => (
                                        <tr key={log.id}>
                                            <td>
                                                <span className="badge badge--purple">{log.agente}</span>
                                            </td>
                                            <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                <span title={log.accion}>{log.accion}</span>
                                                {log.telegram_chat_id && (
                                                    <span className="badge badge--blue" style={{ marginLeft: 4, fontSize: 8 }}>
                                                        📱
                                                    </span>
                                                )}
                                            </td>
                                            <td className="font-mono text-muted" style={{ fontSize: 11 }}>
                                                {log.duracion_ms ? `${log.duracion_ms}ms` : '—'}
                                            </td>
                                            <td>
                                                <span style={{ fontSize: 14 }}>{log.exitoso ? '✅' : '❌'}</span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Urgent Leads */}
                <div className="card fade-up fade-up--5">
                    <div className="flex items-center justify-between mb-4">
                        <h3>Leads Urgentes</h3>
                        <span className="badge badge--pink">Alta prioridad</span>
                    </div>
                    {urgentLeads.length === 0 ? (
                        <div className="text-muted" style={{ textAlign: 'center', padding: '1.5rem', fontSize: 13 }}>
                            🎉 Sin leads urgentes pendientes
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {urgentLeads.map((lead) => (
                                <div
                                    key={lead.id}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        padding: '10px 12px',
                                        background: 'rgba(255,255,255,0.03)',
                                        borderRadius: 4,
                                        border: '1px solid rgba(255,77,148,0.15)',
                                    }}
                                >
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: 13 }}>{lead.nombre}</div>
                                        <div className="text-muted" style={{ fontSize: 11 }}>
                                            {lead.empresa_nombre || 'Sin empresa'} ·{' '}
                                            {formatDistanceToNow(new Date(lead.ultimo_contacto), { addSuffix: true, locale: es })}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            className="btn btn--sm btn--secondary"
                                            onClick={() => navigate(`/conversaciones?lead=${lead.id}`)}
                                        >
                                            💬
                                        </button>
                                        {lead.telegram_chat_id && (
                                            <button
                                                className="btn btn--sm btn--blue"
                                                onClick={() => navigate(`/telegram?lead=${lead.id}`)}
                                            >
                                                📱
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Alert Panel */}
            <div className="card fade-up fade-up--6">
                <div className="flex items-center justify-between mb-4">
                    <h3>Panel de Alertas</h3>
                    <button
                        className="btn btn--secondary"
                        onClick={handleRunAnalytics}
                        disabled={analyzingAlerts}
                    >
                        {analyzingAlerts ? (
                            <>
                                <span
                                    style={{
                                        width: 12,
                                        height: 12,
                                        border: '2px solid transparent',
                                        borderTopColor: 'var(--green)',
                                        borderRadius: '50%',
                                        animation: 'spin 0.7s linear infinite',
                                        display: 'inline-block',
                                    }}
                                />
                                Analizando...
                            </>
                        ) : (
                            '🔄 Analizar con IA'
                        )}
                    </button>
                </div>

                {alertas.length === 0 ? (
                    <div className="text-muted" style={{ fontSize: 13, textAlign: 'center', padding: '1rem' }}>
                        Haz clic en "Analizar" para obtener alertas inteligentes del Agente Analítico.
                    </div>
                ) : (
                    <div className="grid-3" style={{ gap: '0.75rem' }}>
                        {alertas.map((alerta, i) => (
                            <div
                                key={i}
                                className="card"
                                style={{
                                    padding: '0.875rem',
                                    borderLeft: `3px solid ${priorityColor(alerta.prioridad)}`,
                                }}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span
                                        className="badge"
                                        style={{
                                            background:
                                                alerta.prioridad === 'alta'
                                                    ? 'rgba(255,77,148,0.15)'
                                                    : alerta.prioridad === 'media'
                                                        ? 'rgba(255,160,50,0.15)'
                                                        : 'rgba(148,163,184,0.15)',
                                            color: priorityColor(alerta.prioridad),
                                        }}
                                    >
                                        {alerta.prioridad.toUpperCase()}
                                    </span>
                                    <span className="text-muted font-mono" style={{ fontSize: 10 }}>
                                        {alerta.tipo}
                                    </span>
                                </div>
                                <p style={{ fontSize: 12, color: 'var(--text)', marginBottom: 6 }}>
                                    {alerta.mensaje}
                                </p>
                                {alerta.accion_recomendada && (
                                    <p className="text-muted" style={{ fontSize: 11, fontStyle: 'italic' }}>
                                        💡 {alerta.accion_recomendada}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default Dashboard
