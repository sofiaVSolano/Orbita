import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'

interface AgentStatus {
    nombre: string
    descripcion: string
    estado: 'activo' | 'procesando' | 'inactivo'
    mensajes_procesados?: number
    ultima_actividad?: string
    icon: string
    color: string
}

interface AgentLog {
    id: string
    agente: string
    accion: string
    resultado?: string
    created_at: string
}

const AGENTES_BASE: AgentStatus[] = [
    {
        nombre: 'Director ORBITA',
        descripcion: 'Orquesta todos los agentes, toma decisiones estratégicas y coordina el flujo de leads',
        estado: 'activo',
        icon: '🧠',
        color: 'var(--green)',
    },
    {
        nombre: 'Agente Telegram',
        descripcion: 'Gestiona todas las conversaciones entrantes y salientes por Telegram Bot API',
        estado: 'activo',
        icon: '📱',
        color: 'var(--blue)',
    },
    {
        nombre: 'Agente Calificador',
        descripcion: 'Analiza el perfil del lead y califica con scoring IA basado en respuestas y comportamiento',
        estado: 'activo',
        icon: '🎯',
        color: 'var(--purple)',
    },
    {
        nombre: 'Agente Cotizador',
        descripcion: 'Genera cotizaciones personalizadas automáticamente según los requerimientos del lead',
        estado: 'activo',
        icon: '📄',
        color: 'var(--pink)',
    },
    {
        nombre: 'Agente Scheduler',
        descripcion: 'Gestiona y confirma reuniones, envía recordatorios y coordina calendarios automáticamente',
        estado: 'activo',
        icon: '📅',
        color: '#FFD700',
    },
]

const statusColors = {
    activo: { dot: '#50FA7B', bg: 'rgba(80,250,123,0.12)', text: 'var(--green)' },
    procesando: { dot: '#00D1FF', bg: 'rgba(0,209,255,0.12)', text: 'var(--blue)' },
    inactivo: { dot: '#64748B', bg: 'rgba(100,116,139,0.12)', text: 'var(--text-muted)' },
}

// Pentagon SVG positions for 5 agents (centered at 200,200, r=140)
const PENTAGON_POSITIONS = [
    { x: 200, y: 60 }, // top center     — Director
    { x: 333, y: 153 }, // top right      — Telegram
    { x: 282, y: 310 }, // bottom right   — Calificador
    { x: 118, y: 310 }, // bottom left    — Cotizador
    { x: 67, y: 153 }, // top left       — Scheduler
]

const Agentes: React.FC = () => {
    const [agentes, setAgentes] = useState<AgentStatus[]>(AGENTES_BASE)
    const [logs, setLogs] = useState<AgentLog[]>([])
    const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null)

    // Live status from backend
    const { data: statusData } = useQuery({
        queryKey: ['agentStatus'],
        queryFn: () => orbitaApi.getAgentStatus(),
        refetchInterval: 15_000,
        retry: 1,
    })

    useEffect(() => {
        if (statusData?.data) {
            const backendStatuses: Record<string, Partial<AgentStatus>> = statusData.data
            setAgentes((prev) =>
                prev.map((a) => {
                    const key = a.nombre.toLowerCase().replace(/\s+/g, '_')
                    const live = backendStatuses[key]
                    return live ? { ...a, ...live } : a
                })
            )
        }
    }, [statusData])

    // Agent logs from Supabase
    useEffect(() => {
        const fetchLogs = async () => {
            const { data } = await supabase
                .from('agent_logs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(30)
            setLogs(data || [])
        }
        fetchLogs()

        const ch = supabase
            .channel('agent-logs-agentes')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'agent_logs' }, (p) =>
                setLogs((prev) => [p.new as AgentLog, ...prev].slice(0, 30))
            )
            .subscribe()
        return () => { supabase.removeChannel(ch) }
    }, [])

    const totalMsgs = agentes.reduce((s, a) => s + (a.mensajes_procesados || 0), 0)
    const activeCount = agentes.filter((a) => a.estado === 'activo').length

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <h1>🤖 Agentes IA — Arquitectura ORBITA</h1>
                <p className="text-muted">Sistema multi-agente coordinado por el Director ORBITA</p>
            </div>

            {/* Pentagon Diagram + Cards */}
            <div className="grid-2 mb-6" style={{ gridTemplateColumns: '420px 1fr', gap: '1.5rem', alignItems: 'start' }}>
                {/* SVG Pentagon */}
                <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
                    <svg width="400" height="370" viewBox="0 0 400 370">
                        {/* Pentagon border */}
                        <polygon
                            points={PENTAGON_POSITIONS.map((p) => `${p.x},${p.y}`).join(' ')}
                            fill="none"
                            stroke="rgba(80,250,123,0.15)"
                            strokeWidth="1"
                        />
                        {/* Center lines */}
                        {PENTAGON_POSITIONS.map((p, i) => (
                            <line
                                key={i}
                                x1={200} y1={200}
                                x2={p.x} y2={p.y}
                                stroke="rgba(80,250,123,0.08)"
                                strokeWidth="1"
                                strokeDasharray="4 4"
                            />
                        ))}
                        {/* Center node (admin) */}
                        <circle cx={200} cy={200} r={18} fill="rgba(80,250,123,0.1)" stroke="rgba(80,250,123,0.4)" strokeWidth="1.5" />
                        <text x={200} y={205} textAnchor="middle" fontSize="14" fill="var(--green)">👤</text>

                        {/* Agent nodes */}
                        {agentes.map((agent, i) => {
                            const pos = PENTAGON_POSITIONS[i]
                            const sc = statusColors[agent.estado]
                            const isSelected = selectedAgent?.nombre === agent.nombre
                            return (
                                <g key={agent.nombre} style={{ cursor: 'pointer' }} onClick={() => setSelectedAgent(isSelected ? null : agent)}>
                                    <circle
                                        cx={pos.x} cy={pos.y} r={28}
                                        fill={isSelected ? `rgba(${agent.color === 'var(--green)' ? '80,250,123' : agent.color === 'var(--blue)' ? '0,209,255' : agent.color === 'var(--purple)' ? '189,147,249' : agent.color === 'var(--pink)' ? '255,77,148' : '255,215,0'},0.18)` : 'rgba(13,11,20,0.9)'}
                                        stroke={isSelected ? agent.color : 'rgba(255,255,255,0.12)'}
                                        strokeWidth={isSelected ? 2 : 1}
                                    />
                                    <text x={pos.x} y={pos.y + 5} textAnchor="middle" fontSize="18">{agent.icon}</text>
                                    {/* Status dot */}
                                    <circle cx={pos.x + 20} cy={pos.y - 20} r={5} fill={sc.dot}>
                                        <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
                                    </circle>
                                    {/* Label below */}
                                    <text x={pos.x} y={pos.y + 42} textAnchor="middle" fontSize="9" fill="var(--text-muted)">
                                        {agent.nombre.split(' ')[1] || agent.nombre}
                                    </text>
                                </g>
                            )
                        })}

                        {/* Telegram Bot special node */}
                        <circle cx={200} cy={340} r={18} fill="rgba(0,209,255,0.1)" stroke="rgba(0,209,255,0.3)" strokeWidth="1.5" />
                        <text x={200} y={345} textAnchor="middle" fontSize="14" fill="var(--blue)">🤖</text>
                        <line x1={200} y1={322} x2={200} y2={225} stroke="rgba(0,209,255,0.2)" strokeWidth="1" strokeDasharray="4 4" />
                        <text x={200} y={366} textAnchor="middle" fontSize="8" fill="var(--text-muted)">Bot TG</text>
                    </svg>
                </div>

                {/* Agent Cards */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {agentes.map((agent) => {
                        const sc = statusColors[agent.estado]
                        const agentLogs = logs.filter((l) => l.agente?.toLowerCase().includes(agent.nombre.toLowerCase().split(' ')[1] || agent.nombre.toLowerCase()))
                        return (
                            <div
                                key={agent.nombre}
                                className={`card ${selectedAgent?.nombre === agent.nombre ? 'card--green' : ''}`}
                                style={{ cursor: 'pointer', borderLeft: `3px solid ${agent.color}` }}
                                onClick={() => setSelectedAgent(selectedAgent?.nombre === agent.nombre ? null : agent)}
                            >
                                <div className="flex items-center gap-3">
                                    <div style={{
                                        width: 38, height: 38, borderRadius: '50%',
                                        background: `rgba(${agent.color === 'var(--green)' ? '80,250,123' : agent.color === 'var(--blue)' ? '0,209,255' : agent.color === 'var(--purple)' ? '189,147,249' : agent.color === 'var(--pink)' ? '255,77,148' : '255,215,0'},0.15)`,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: 18, flexShrink: 0,
                                    }}>
                                        {agent.icon}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <span style={{ fontWeight: 700, fontSize: 13 }}>{agent.nombre}</span>
                                            <span className="badge" style={{ color: sc.text, background: sc.bg, fontSize: 8 }}>
                                                ● {agent.estado}
                                            </span>
                                        </div>
                                        <div className="text-muted" style={{ fontSize: 11, marginTop: 2 }}>{agent.descripcion}</div>
                                    </div>
                                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                        {agent.mensajes_procesados !== undefined && (
                                            <>
                                                <div className="font-mono" style={{ fontSize: 16, color: agent.color }}>{agent.mensajes_procesados}</div>
                                                <div className="text-muted" style={{ fontSize: 9 }}>msgs hoy</div>
                                            </>
                                        )}
                                        {agentLogs.length > 0 && (
                                            <div className="text-muted" style={{ fontSize: 9, marginTop: 2 }}>
                                                {agentLogs.length} acciones
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )
                    })}

                    {/* Summary pills */}
                    <div className="flex gap-3">
                        <div className="card" style={{ flex: 1, padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                            <div className="font-mono" style={{ color: 'var(--green)', fontSize: 18 }}>{activeCount}</div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Activos</div>
                        </div>
                        <div className="card" style={{ flex: 1, padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                            <div className="font-mono" style={{ color: 'var(--blue)', fontSize: 18 }}>{totalMsgs || '—'}</div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Msgs totales</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Hackathon Criteria */}
            <div className="card card--purple fade-up mb-6">
                <h3 style={{ marginBottom: '1rem' }}>🏆 Criterios del Hackathon — Implementación ORBITA</h3>
                <div className="grid-2" style={{ gap: '0.75rem' }}>
                    {[
                        { ok: true, label: 'Uso de agentes de IA', detail: '5 agentes especializados + orquestador Director ORBITA' },
                        { ok: true, label: 'Integración con Telegram', detail: 'Bot API + voz transcrita (Whisper) + notificaciones admin' },
                        { ok: true, label: 'CRM completo para leads', detail: 'Pipeline AIDA, scoring, cotizaciones, reuniones' },
                        { ok: true, label: 'Análisis conversacional', detail: 'IA clasifica intención y etapa AIDA en tiempo real' },
                        { ok: true, label: 'Dashboard en tiempo real', detail: 'Supabase Realtime + métricas del sistema' },
                        { ok: true, label: 'Automatización de ventas', detail: 'Cotizaciones, reuniones y seguimiento automáticos' },
                    ].map((c) => (
                        <div
                            key={c.label}
                            style={{ display: 'flex', gap: 10, padding: '0.6rem 0.75rem', background: 'rgba(80,250,123,0.04)', borderRadius: 6, border: '1px solid rgba(80,250,123,0.1)' }}
                        >
                            <span style={{ color: 'var(--green)', fontSize: 16, flexShrink: 0 }}>✅</span>
                            <div>
                                <div style={{ fontWeight: 600, fontSize: 12 }}>{c.label}</div>
                                <div className="text-muted" style={{ fontSize: 11 }}>{c.detail}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Live Agent Logs */}
            <div className="card fade-up">
                <div className="flex items-center justify-between mb-4">
                    <h3>📋 Actividad Reciente de Agentes</h3>
                    <span className="badge badge--green" style={{ fontSize: 9 }}>⚡ Tiempo real</span>
                </div>
                <div className="table-container" style={{ maxHeight: 320, overflowY: 'auto' }}>
                    <table>
                        <thead>
                            <tr>
                                <th>Agente</th>
                                <th>Acción</th>
                                <th>Resultado</th>
                                <th>Hace</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="text-muted" style={{ textAlign: 'center', padding: '1.5rem' }}>
                                        Sin actividad registrada
                                    </td>
                                </tr>
                            ) : (
                                logs.map((log) => {
                                    const agent = agentes.find((a) => log.agente?.toLowerCase().includes(a.nombre.toLowerCase().split(' ')[1] || a.nombre.toLowerCase()))
                                    return (
                                        <tr key={log.id}>
                                            <td>
                                                <span style={{ marginRight: 4 }}>{agent?.icon || '🤖'}</span>
                                                <span style={{ fontSize: 11, color: agent?.color || 'var(--text)' }}>{log.agente}</span>
                                            </td>
                                            <td style={{ fontSize: 12 }}>{log.accion}</td>
                                            <td className="text-muted" style={{ fontSize: 11, maxWidth: 180 }}>
                                                {log.resultado}
                                            </td>
                                            <td className="text-muted" style={{ fontSize: 10 }}>
                                                {formatDistanceToNow(new Date(log.created_at), { addSuffix: true, locale: es })}
                                            </td>
                                        </tr>
                                    )
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export default Agentes
