import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatDistanceToNow, format } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'

interface Reunion {
    id: string
    lead_id: string
    titulo: string
    descripcion?: string
    fecha_hora: string
    duracion_minutos?: number
    tipo: string
    estado: string
    confirmada_por_telegram: boolean
    created_at: string
    lead?: { nombre: string; empresa_nombre?: string }
}

const ESTADOS = ['todos', 'pendiente', 'confirmada', 'realizada', 'cancelada', 'no_show']
const TIPOS = ['todos', 'discovery', 'demo', 'seguimiento', 'cierre']

const estadoConfig: Record<string, { label: string; color: string; bg: string }> = {
    pendiente: { label: 'pendiente', color: 'var(--text-muted)', bg: 'rgba(255,255,255,0.06)' },
    confirmada: { label: '✓ confirmada', color: 'var(--green)', bg: 'rgba(80,250,123,0.12)' },
    realizada: { label: '✓ realizada', color: 'var(--blue)', bg: 'rgba(0,209,255,0.12)' },
    cancelada: { label: '✕ cancelada', color: '#FF5050', bg: 'rgba(255,80,80,0.12)' },
    no_show: { label: '? no show', color: 'var(--pink)', bg: 'rgba(255,77,148,0.12)' },
}

const tipoIcon: Record<string, string> = {
    discovery: '🔍',
    demo: '💻',
    seguimiento: '📞',
    cierre: '🤝',
}

const Reuniones: React.FC = () => {
    const navigate = useNavigate()
    const [reuniones, setReuniones] = useState<Reunion[]>([])
    const [loading, setLoading] = useState(true)
    const [estadoFilter, setEstadoFilter] = useState('todos')
    const [tipoFilter, setTipoFilter] = useState('todos')
    const [search, setSearch] = useState('')
    const [selected, setSelected] = useState<Reunion | null>(null)

    const fetchReuniones = async () => {
        setLoading(true)
        const query = supabase
            .from('reuniones')
            .select('*, lead:leads(nombre,empresa_nombre)')
            .order('fecha_hora', { ascending: true })
            .limit(100)

        if (estadoFilter !== 'todos') query.eq('estado', estadoFilter)
        if (tipoFilter !== 'todos') query.eq('tipo', tipoFilter)
        const { data } = await query
        setReuniones(data || [])
        setLoading(false)
    }

    useEffect(() => { fetchReuniones() }, [estadoFilter, tipoFilter])

    const filtered = reuniones.filter((r) => {
        const q = search.toLowerCase()
        return (
            r.titulo?.toLowerCase().includes(q) ||
            r.lead?.nombre?.toLowerCase().includes(q) ||
            r.lead?.empresa_nombre?.toLowerCase().includes(q)
        )
    })

    const upcoming = filtered.filter((r) => new Date(r.fecha_hora) > new Date()).length
    const today = filtered.filter((r) => {
        const d = new Date(r.fecha_hora)
        const now = new Date()
        return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()
    }).length

    const handleUpdateEstado = async (id: string, estado: string) => {
        const { error } = await supabase.from('reuniones').update({ estado }).eq('id', id)
        if (error) { toast.error('Error al actualizar'); return }
        toast.success('Estado actualizado')
        fetchReuniones()
        if (selected?.id === id) setSelected((prev) => prev ? { ...prev, estado } : prev)
    }

    const isOverdue = (r: Reunion) =>
        new Date(r.fecha_hora) < new Date() && r.estado === 'pendiente'

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <div className="flex items-center justify-between">
                    <div>
                        <h1>📅 Reuniones</h1>
                        <p className="text-muted">Agenda y seguimiento de reuniones con leads</p>
                    </div>
                    {/* Counter Pills */}
                    <div className="flex items-center gap-3">
                        <div className="card" style={{ padding: '0.5rem 1rem', textAlign: 'center', minWidth: 80 }}>
                            <div className="font-mono" style={{ fontSize: 20, color: 'var(--pink)' }}>{today}</div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Hoy</div>
                        </div>
                        <div className="card" style={{ padding: '0.5rem 1rem', textAlign: 'center', minWidth: 80 }}>
                            <div className="font-mono" style={{ fontSize: 20, color: 'var(--blue)' }}>{upcoming}</div>
                            <div className="text-muted" style={{ fontSize: 10 }}>Próximas</div>
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
                        placeholder="🔍 Buscar reunión o lead..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <select className="input" style={{ maxWidth: 170 }} value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)}>
                        {ESTADOS.map((e) => <option key={e} value={e}>{e === 'todos' ? 'Todos los estados' : e.charAt(0).toUpperCase() + e.slice(1)}</option>)}
                    </select>
                    <select className="input" style={{ maxWidth: 150 }} value={tipoFilter} onChange={(e) => setTipoFilter(e.target.value)}>
                        {TIPOS.map((t) => <option key={t} value={t}>{t === 'todos' ? 'Todos los tipos' : tipoIcon[t] + ' ' + t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                    </select>
                    <span className="text-muted" style={{ fontSize: 12, marginLeft: 'auto' }}>
                        {filtered.length} reuniones
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
                                    <th>Reunión</th>
                                    <th>Tipo</th>
                                    <th>Fecha y hora</th>
                                    <th>Duración</th>
                                    <th>Estado</th>
                                    <th>TG</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    [...Array(6)].map((_, i) => (
                                        <tr key={i}>
                                            {[...Array(8)].map((__, j) => (
                                                <td key={j}><div className="skeleton" style={{ height: 14, width: 60 }} /></td>
                                            ))}
                                        </tr>
                                    ))
                                ) : filtered.length === 0 ? (
                                    <tr>
                                        <td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                            Sin reuniones
                                        </td>
                                    </tr>
                                ) : (
                                    filtered.map((r) => {
                                        const cfg = estadoConfig[r.estado] || estadoConfig.pendiente
                                        const overdue = isOverdue(r)
                                        return (
                                            <tr
                                                key={r.id}
                                                style={{
                                                    cursor: 'pointer',
                                                    background: selected?.id === r.id
                                                        ? 'rgba(80,250,123,0.04)'
                                                        : overdue
                                                            ? 'rgba(255,80,80,0.03)'
                                                            : 'transparent',
                                                }}
                                                onClick={() => setSelected(r)}
                                            >
                                                <td>
                                                    <div style={{ fontWeight: 600, fontSize: 12 }}>{r.lead?.nombre || '—'}</div>
                                                    <div className="text-muted" style={{ fontSize: 10 }}>{r.lead?.empresa_nombre}</div>
                                                </td>
                                                <td style={{ maxWidth: 140 }}>
                                                    <div style={{ fontSize: 12, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.titulo}</div>
                                                </td>
                                                <td>
                                                    <span style={{ fontSize: 14 }} title={r.tipo}>{tipoIcon[r.tipo] || '📅'}</span>
                                                    <span className="text-muted" style={{ fontSize: 10, marginLeft: 4 }}>{r.tipo}</span>
                                                </td>
                                                <td>
                                                    <div className="font-mono" style={{ fontSize: 11, color: overdue ? '#FF5050' : 'var(--text)' }}>
                                                        {format(new Date(r.fecha_hora), 'dd/MM HH:mm')}
                                                    </div>
                                                    {overdue && (
                                                        <div style={{ fontSize: 9, color: '#FF5050' }}>⚠ vencida</div>
                                                    )}
                                                </td>
                                                <td className="text-muted" style={{ fontSize: 11 }}>
                                                    {r.duracion_minutos ? `${r.duracion_minutos} min` : '—'}
                                                </td>
                                                <td>
                                                    <span className="badge" style={{ color: cfg.color, background: cfg.bg, fontSize: 9 }}>
                                                        {cfg.label}
                                                    </span>
                                                </td>
                                                <td>
                                                    {r.confirmada_por_telegram && (
                                                        <span title="Confirmada por Telegram">✅📱</span>
                                                    )}
                                                </td>
                                                <td onClick={(e) => e.stopPropagation()}>
                                                    <div className="flex gap-1">
                                                        <button
                                                            className="btn btn--sm btn--secondary"
                                                            onClick={() => navigate(`/leads?id=${r.lead_id}`)}
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
                            <h3 style={{ fontSize: 14 }}>Detalle Reunión</h3>
                            <button className="btn btn--sm btn--secondary" onClick={() => setSelected(null)}>✕</button>
                        </div>

                        <div className="form-group mb-3">
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
                                <div className="form-label">Tipo</div>
                                <div style={{ fontSize: 13 }}>{tipoIcon[selected.tipo] || '📅'} {selected.tipo}</div>
                            </div>
                        </div>

                        <div className="grid-2 mb-3" style={{ gap: '0.75rem' }}>
                            <div className="form-group">
                                <div className="form-label">Fecha y hora</div>
                                <div className="font-mono" style={{ fontSize: 12, color: 'var(--blue)' }}>
                                    {format(new Date(selected.fecha_hora), 'dd/MM/yyyy HH:mm')}
                                </div>
                                <div className="text-muted" style={{ fontSize: 10 }}>
                                    {formatDistanceToNow(new Date(selected.fecha_hora), { addSuffix: true, locale: es })}
                                </div>
                            </div>
                            <div className="form-group">
                                <div className="form-label">Duración</div>
                                <div style={{ fontSize: 12 }}>
                                    {selected.duracion_minutos ? `${selected.duracion_minutos} minutos` : 'No especificada'}
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
                            <div className="form-label">Confirmada por Telegram</div>
                            <div>{selected.confirmada_por_telegram ? '✅📱 Sí' : '— No'}</div>
                        </div>

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
                                        {key === 'confirmada' ? '✓' : key === 'cancelada' ? '✕' : ''} {key}
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

export default Reuniones
