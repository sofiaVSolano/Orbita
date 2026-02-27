import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format, subDays } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'

// ── Types ──────────────────────────────────────────────────────
interface DayData { fecha: string; mensajes: number; leads: number }
interface TypeData { name: string; value: number; color: string }

const COLORS = {
    green: '#50FA7B',
    blue: '#00D1FF',
    purple: '#BD93F9',
    pink: '#FF4D94',
    yellow: '#FFD700',
    muted: '#64748B',
}

// ── Tooltip custom ─────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { color: string; name: string; value: number }[]; label?: string }) => {
    if (!active || !payload?.length) return null
    return (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, padding: '0.6rem 0.8rem', fontSize: 12 }}>
            <div className="text-muted" style={{ marginBottom: 4, fontSize: 11 }}>{label}</div>
            {payload.map((p) => (
                <div key={p.name} style={{ color: p.color }}>
                    {p.name}: <span className="font-mono">{p.value}</span>
                </div>
            ))}
        </div>
    )
}

// ── Component ──────────────────────────────────────────────────
const Analitica: React.FC = () => {
    const [msgData, setMsgData] = useState<DayData[]>([])
    const [typeData, setTypeData] = useState<TypeData[]>([])
    const [fuenteData, setFuenteData] = useState<TypeData[]>([])
    const [etapaData, setEtapaData] = useState<TypeData[]>([])
    const [runningIA, setRunningIA] = useState(false)
    const [iaReport, setIaReport] = useState('')

    // Backend analytics
    const { data: analyticsData, isLoading: analyticsLoading } = useQuery({
        queryKey: ['analytics'],
        queryFn: () => orbitaApi.runAnalytics(),
        retry: 1,
        staleTime: 5 * 60_000,
    })

    // Messages per day (14 days) from Supabase conversations
    useEffect(() => {
        const fetch = async () => {
            const from = subDays(new Date(), 13).toISOString()
            const { data } = await supabase
                .from('conversations')
                .select('created_at')
                .gte('created_at', from)
                .order('created_at')

            const counts: Record<string, number> = {}
            const last14 = Array.from({ length: 14 }, (_, i) => format(subDays(new Date(), 13 - i), 'yyyy-MM-dd'))
            last14.forEach((d) => { counts[d] = 0 })
            data?.forEach((msg) => {
                const d = msg.created_at.slice(0, 10)
                if (counts[d] !== undefined) counts[d]++
            })

            const { data: leadsData } = await supabase
                .from('leads')
                .select('created_at')
                .gte('created_at', from)

            const leadCounts: Record<string, number> = {}
            last14.forEach((d) => { leadCounts[d] = 0 })
            leadsData?.forEach((l) => {
                const d = l.created_at.slice(0, 10)
                if (leadCounts[d] !== undefined) leadCounts[d]++
            })

            const result = last14.map((d) => ({
                fecha: format(new Date(d), 'd/M', { locale: es }),
                mensajes: counts[d],
                leads: leadCounts[d],
            }))
            setMsgData(result)
        }
        fetch()
    }, [])

    // Message type distribution
    useEffect(() => {
        const fetch = async () => {
            const { data } = await supabase.from('conversations').select('content_type')
            const counts: Record<string, number> = {}
            data?.forEach((m) => { counts[m.content_type || 'text'] = (counts[m.content_type || 'text'] || 0) + 1 })
            setTypeData([
                { name: 'Texto', value: counts.text || 0, color: COLORS.blue },
                { name: 'Voz', value: counts.voice || 0, color: COLORS.purple },
                { name: 'Imagen', value: counts.image || 0, color: COLORS.pink },
                { name: 'Documento', value: counts.document || 0, color: COLORS.green },
            ].filter((d) => d.value > 0))
        }
        fetch()
    }, [])

    // Lead sources
    useEffect(() => {
        const fetch = async () => {
            const { data } = await supabase.from('leads').select('fuente')
            const counts: Record<string, number> = {}
            data?.forEach((l) => { counts[l.fuente || 'desconocido'] = (counts[l.fuente || 'desconocido'] || 0) + 1 })
            setFuenteData([
                { name: 'Telegram', value: counts.telegram || 0, color: COLORS.blue },
                { name: 'Manual', value: counts.manual || 0, color: COLORS.muted },
                { name: 'Formulario', value: counts.formulario || 0, color: COLORS.purple },
                { name: 'Referido', value: counts.referido || 0, color: COLORS.green },
            ].filter((d) => d.value > 0))
        }
        fetch()
    }, [])

    // Leads by AIDA stage
    useEffect(() => {
        const fetch = async () => {
            const { data } = await supabase.from('leads').select('etapa_funnel')
            const counts: Record<string, number> = {
                atencion: 0, interes: 0, deseo: 0, accion: 0,
            }
            data?.forEach((l) => {
                const k = l.etapa_funnel?.toLowerCase()
                if (k && k in counts) counts[k]++
            })
            setEtapaData([
                { name: 'Atención', value: counts.atencion, color: COLORS.blue },
                { name: 'Interés', value: counts.interes, color: COLORS.purple },
                { name: 'Deseo', value: counts.deseo, color: COLORS.pink },
                { name: 'Acción', value: counts.accion, color: COLORS.green },
            ])
        }
        fetch()
    }, [])

    const handleRunIA = async () => {
        setRunningIA(true)
        setIaReport('')
        try {
            const res = await orbitaApi.runAnalytics()
            setIaReport(res?.data?.resumen || res?.data?.report || 'Sin reporte disponible')
            toast.success('📊 Análisis IA completado')
        } catch {
            toast.error('Error al conectar con el backend')
        } finally {
            setRunningIA(false)
        }
    }

    const kpis = analyticsData?.data || {}

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <div className="flex items-center justify-between">
                    <div>
                        <h1>📊 Analítica</h1>
                        <p className="text-muted">Métricas avanzadas del sistema ORBITA</p>
                    </div>
                    <button
                        className="btn btn--primary"
                        onClick={handleRunIA}
                        disabled={runningIA}
                    >
                        {runningIA ? '⏳ Analizando...' : '🤖 Analizar con IA'}
                    </button>
                </div>
            </div>

            {/* IA Report Card */}
            {(iaReport || analyticsLoading) && (
                <div className="card card--blue mb-6 fade-up">
                    <div className="flex items-center gap-2 mb-2">
                        <span style={{ fontSize: 16 }}>🤖</span>
                        <span style={{ fontWeight: 600, fontSize: 13 }}>Reporte IA</span>
                    </div>
                    {analyticsLoading || runningIA ? (
                        <div className="text-muted" style={{ fontSize: 12 }}>Generando análisis...</div>
                    ) : (
                        <div style={{ fontSize: 12, lineHeight: 1.7, color: 'var(--text-muted)', whiteSpace: 'pre-wrap' }}>{iaReport}</div>
                    )}
                </div>
            )}

            {/* Messages per day */}
            <div className="card mb-6 fade-up">
                <h3 style={{ marginBottom: '1rem' }}>📈 Mensajes y Leads — Últimos 14 días</h3>
                <ResponsiveContainer width="100%" height={220}>
                    <AreaChart data={msgData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="gMsgs" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="gLeads" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={COLORS.green} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={COLORS.green} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                        <XAxis dataKey="fecha" tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: 11, color: '#94A3B8' }} />
                        <Area type="monotone" dataKey="mensajes" name="Mensajes" stroke={COLORS.blue} fill="url(#gMsgs)" strokeWidth={2} dot={false} />
                        <Area type="monotone" dataKey="leads" name="Leads captados" stroke={COLORS.green} fill="url(#gLeads)" strokeWidth={2} dot={false} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Row: 2 pie charts + bar chart */}
            <div className="grid-3 mb-6">
                {/* Message type donut */}
                <div className="card fade-up">
                    <h3 style={{ marginBottom: '0.75rem', fontSize: 13 }}>🎙️ Tipos de Mensaje</h3>
                    {typeData.length === 0 ? (
                        <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 12 }}>Sin datos</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={180}>
                            <PieChart>
                                <Pie data={typeData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={2} dataKey="value">
                                    {typeData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                                </Pie>
                                <Tooltip formatter={(v, n) => [v, n]} />
                                <Legend wrapperStyle={{ fontSize: 10, color: '#94A3B8' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Lead sources donut */}
                <div className="card fade-up">
                    <h3 style={{ marginBottom: '0.75rem', fontSize: 13 }}>📥 Fuentes de Leads</h3>
                    {fuenteData.length === 0 ? (
                        <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 12 }}>Sin datos</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={180}>
                            <PieChart>
                                <Pie data={fuenteData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={2} dataKey="value">
                                    {fuenteData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                                </Pie>
                                <Tooltip />
                                <Legend wrapperStyle={{ fontSize: 10, color: '#94A3B8' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* AIDA stages bar */}
                <div className="card fade-up">
                    <h3 style={{ marginBottom: '0.75rem', fontSize: 13 }}>🎯 Pipeline AIDA</h3>
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={etapaData} margin={{ top: 5, right: 5, left: -30, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 9 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#64748B', fontSize: 9 }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="value" name="Leads" radius={[3, 3, 0, 0]}>
                                {etapaData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Telegram Analyics section */}
            <div className="card card--blue fade-up">
                <h3 style={{ marginBottom: '1rem' }}>📱 Analítica de Telegram</h3>
                <div className="grid-3">
                    {[
                        { label: 'Tasa de respuesta bot', value: kpis.tasa_respuesta ? `${kpis.tasa_respuesta}%` : '—', color: COLORS.green },
                        { label: 'Tiempo promedio respuesta', value: kpis.tiempo_respuesta_promedio ? `${kpis.tiempo_respuesta_promedio}s` : '—', color: COLORS.blue },
                        { label: 'Mensajes de voz procesados', value: kpis.voces_procesadas ?? '—', color: COLORS.purple },
                        { label: 'Leads calificados via TG', value: kpis.leads_calificados_telegram ?? '—', color: COLORS.pink },
                        { label: 'Cotizaciones enviadas TG', value: kpis.cotizaciones_telegram ?? '—', color: COLORS.yellow },
                        { label: 'Reuniones confirmadas TG', value: kpis.reuniones_confirmadas_telegram ?? '—', color: COLORS.green },
                    ].map((stat) => (
                        <div key={stat.label} style={{ textAlign: 'center', padding: '0.75rem', background: 'rgba(255,255,255,0.02)', borderRadius: 6 }}>
                            <div className="font-mono" style={{ fontSize: 20, color: stat.color }}>{stat.value}</div>
                            <div className="text-muted" style={{ fontSize: 11, marginTop: 4 }}>{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Analitica
