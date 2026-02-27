import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatDistanceToNow, format } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'

interface Cotizacion {
    id: string
    lead_id: string
    titulo: string
    descripcion?: string
    monto: number
    estado: string
    enviada_por_telegram: boolean
    fecha_envio?: string
    created_at: string
    lead?: { nombre: string; empresa_nombre?: string }
}

const ESTADOS = ['todos', 'pendiente', 'enviada', 'aceptada', 'rechazada', 'vencida']

const estadoConfig: Record<string, { label: string; color: string; bg: string }> = {
    pendiente: { label: 'pendiente', color: 'var(--text-muted)', bg: 'rgba(255,255,255,0.06)' },
    enviada: { label: 'enviada', color: 'var(--blue)', bg: 'rgba(0,209,255,0.12)' },
    aceptada: { label: 'aceptada', color: 'var(--green)', bg: 'rgba(80,250,123,0.12)' },
    rechazada: { label: 'rechazada', color: '#FF5050', bg: 'rgba(255,80,80,0.12)' },
    vencida: { label: 'vencida', color: 'var(--pink)', bg: 'rgba(255,77,148,0.12)' },
}

const formatCOP = (n: number) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(n)

const Cotizaciones: React.FC = () => {
    const navigate = useNavigate()
    const [cotizaciones, setCotizaciones] = useState<Cotizacion[]>([])
    const [loading, setLoading] = useState(true)
    const [estadoFilter, setEstadoFilter] = useState('todos')
    const [search, setSearch] = useState('')
    const [selected, setSelected] = useState<Cotizacion | null>(null)

    const fetchCotizaciones = async () => {
        setLoading(true)
        const query = supabase
            .from('cotizaciones')
            .select('*, lead:leads(nombre,empresa_nombre)')
            .order('created_at', { ascending: false })
            .limit(100)

        if (estadoFilter !== 'todos') query.eq('estado', estadoFilter)
        const { data } = await query
        setCotizaciones(data || [])
        setLoading(false)
    }

    useEffect(() => { fetchCotizaciones() }, [estadoFilter])

    const filtered = cotizaciones.filter((c) => {
        const q = search.toLowerCase()
        return (
            c.titulo?.toLowerCase().includes(q) ||
            c.lead?.nombre?.toLowerCase().includes(q) ||
            c.lead?.empresa_nombre?.toLowerCase().includes(q)
        )
    })

    const totalValor = filtered.reduce((s, c) => s + (c.monto || 0), 0)
    const totalAceptadas = filtered.filter((c) => c.estado === 'aceptada').reduce((s, c) => s + (c.monto || 0), 0)

    const handleUpdateEstado = async (id: string, estado: string) => {
        const { error } = await supabase.from('cotizaciones').update({ estado }).eq('id', id)
        if (error) { toast.error('Error al actualizar'); return }
        toast.success('Estado actualizado')
        fetchCotizaciones()
        if (selected?.id === id) setSelected((prev) => prev ? { ...prev, estado } : prev)
    }

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <div className="flex items-center justify-between">
                    <div>
                        <h1>📄 Cotizaciones</h1>
                        <p className="text-muted">Gestiona propuestas y cotizaciones enviadas a leads</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="card" style={{ padding: '0.5rem 1rem', textAlign: 'center', minWidth: 120 }}>
                            <div className="font-mono" style={{ fontSize: 16, color: 'var(--green)' }}>
                                {formatCOP(totalAceptadas)}
                            </div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Aceptadas</div>
                        </div>
                        <div className="card" style={{ padding: '0.5rem 1rem', textAlign: 'center', minWidth: 120 }}>
                            <div className="font-mono" style={{ fontSize: 16, color: 'var(--blue)' }}>
                                {formatCOP(totalValor)}
                            </div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Total pipeline</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="card mb-4" style={{ padding: '0.75rem 1rem' }}>
                <div className="flex gap-3" style={{ flexWrap: 'wrap', alignItems: 'center' }}>
                    <input
                        className="input"
                        style={{ maxWidth: 240 }}
                        placeholder="🔍 Buscar cotización o lead..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <select className="input" style={{ maxWidth: 160 }} value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)}>
                        {ESTADOS.map((e) => <option key={e} value={e}>{e === 'todos' ? 'Todos los estados' : e.charAt(0).toUpperCase() + e.slice(1)}</option>)}
                    </select>
                    <span className="text-muted" style={{ fontSize: 12, marginLeft: 'auto' }}>
                        {filtered.length} cotizaciones
                    </span>
                </div>
            </div>

            <div className="grid-2" style={{ gridTemplateColumns: selected ? '1fr 380px' : '1fr', gap: '1rem', alignItems: 'start' }}>
                {/* Table */}
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Lead</th>
                                    <th>Título</th>
                                    <th>Monto</th>
                                    <th>Estado</th>
                                    <th>Telegram</th>
                                    <th>Fecha</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    [...Array(6)].map((_, i) => (
                                        <tr key={i}>
                                            {[...Array(7)].map((__, j) => (
                                                <td key={j}><div className="skeleton" style={{ height: 14, width: 60 }} /></td>
                                            ))}
                                        </tr>
                                    ))
                                ) : filtered.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                            Sin cotizaciones
                                        </td>
                                    </tr>
                                ) : (
                                    filtered.map((c) => {
                                        const cfg = estadoConfig[c.estado] || estadoConfig.pendiente
                                        return (
                                            <tr
                                                key={c.id}
                                                style={{ cursor: 'pointer', background: selected?.id === c.id ? 'rgba(80,250,123,0.04)' : 'transparent' }}
                                                onClick={() => setSelected(c)}
                                            >
                                                <td>
                                                    <div style={{ fontWeight: 600, fontSize: 12 }}>{c.lead?.nombre || '—'}</div>
                                                    <div className="text-muted" style={{ fontSize: 10 }}>{c.lead?.empresa_nombre}</div>
                                                </td>
                                                <td style={{ maxWidth: 160 }}>
                                                    <div style={{ fontSize: 12, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.titulo}</div>
                                                </td>
                                                <td className="font-mono" style={{ color: 'var(--green)', fontSize: 12 }}>
                                                    {formatCOP(c.monto || 0)}
                                                </td>
                                                <td>
                                                    <span className="badge" style={{ color: cfg.color, background: cfg.bg, fontSize: 9 }}>
                                                        {cfg.label}
                                                    </span>
                                                </td>
                                                <td>
                                                    {c.enviada_por_telegram && <span style={{ fontSize: 16 }} title="Enviada por Telegram">📱</span>}
                                                </td>
                                                <td className="text-muted" style={{ fontSize: 10 }}>
                                                    {formatDistanceToNow(new Date(c.created_at), { addSuffix: true, locale: es })}
                                                </td>
                                                <td onClick={(e) => e.stopPropagation()}>
                                                    <div className="flex gap-1">
                                                        <button
                                                            className="btn btn--sm btn--secondary"
                                                            onClick={() => navigate(`/leads?id=${c.lead_id}`)}
                                                            title="Ver lead"
                                                        >👤</button>
                                                    </div>
                                                </td>
                                            </tr>
                                        )
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Side Panel */}
                {selected && (
                    <div className="card card--green fade-up" style={{ position: 'sticky', top: '1rem' }}>
                        <div className="flex items-center justify-between mb-4">
                            <h3 style={{ fontSize: 14 }}>Detalle Cotización</h3>
                            <button className="btn btn--sm btn--secondary" onClick={() => setSelected(null)}>✕</button>
                        </div>

                        <div className="form-group">
                            <div className="form-label">Título</div>
                            <div style={{ fontSize: 14, fontWeight: 600 }}>{selected.titulo}</div>
                        </div>

                        <div className="grid-2 mb-3" style={{ gap: '0.75rem' }}>
                            <div className="form-group">
                                <div className="form-label">Lead</div>
                                <div style={{ fontSize: 12 }}>{selected.lead?.nombre || '—'}</div>
                                <div className="text-muted" style={{ fontSize: 11 }}>{selected.lead?.empresa_nombre}</div>
                            </div>
                            <div className="form-group">
                                <div className="form-label">Monto</div>
                                <div className="font-mono" style={{ fontSize: 16, color: 'var(--green)' }}>
                                    {formatCOP(selected.monto || 0)}
                                </div>
                            </div>
                        </div>

                        {selected.descripcion && (
                            <div className="form-group mb-3">
                                <div className="form-label">Descripción</div>
                                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>{selected.descripcion}</div>
                            </div>
                        )}

                        <div className="form-group mb-3">
                            <div className="form-label">Enviada por Telegram</div>
                            <div>{selected.enviada_por_telegram ? '📱 Sí' : '— No'}</div>
                        </div>

                        {selected.fecha_envio && (
                            <div className="form-group mb-3">
                                <div className="form-label">Fecha de envío</div>
                                <div className="font-mono" style={{ fontSize: 11 }}>
                                    {format(new Date(selected.fecha_envio), 'dd/MM/yyyy HH:mm')}
                                </div>
                            </div>
                        )}

                        <div className="form-group mb-4">
                            <div className="form-label mb-2">Cambiar estado</div>
                            <div className="flex gap-1" style={{ flexWrap: 'wrap' }}>
                                {Object.entries(estadoConfig).map(([key, cfg]) => (
                                    <button
                                        key={key}
                                        className="btn btn--sm"
                                        style={{
                                            color: cfg.color,
                                            background: selected.estado === key ? cfg.bg : 'transparent',
                                            border: `1px solid ${selected.estado === key ? cfg.color : 'var(--border)'}`,
                                        }}
                                        onClick={() => handleUpdateEstado(selected.id, key)}
                                    >
                                        {cfg.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            className="btn btn--primary w-full"
                            onClick={() => navigate(`/leads?id=${selected.lead_id}`)}
                        >
                            👤 Ver Lead en CRM
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Cotizaciones
