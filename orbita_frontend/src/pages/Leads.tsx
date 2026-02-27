import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'
import FuenteBadge from '../components/FuenteBadge'
import TelegramBubble from '../components/TelegramBubble'
import LoadingDots from '../components/LoadingDots'

// ── Types ─────────────────────────────────────────────────────
interface Lead {
    id: string
    nombre: string
    email?: string
    telefono?: string
    empresa_nombre?: string
    cargo?: string
    servicio_interes?: string
    presupuesto_estimado?: string
    etapa_funnel: string
    estado: string
    prioridad: string
    fuente: string
    etiquetas?: string[]
    notas?: string
    ultimo_contacto: string
    created_at: string
    telegram_chat_id?: string
    telegram_username?: string
}

interface Conversation {
    id: string
    role: string
    content: string
    content_type: string
    transcripcion_voz?: string
    agente?: string
    created_at: string
}

const ETAPAS = ['atencion', 'interes', 'deseo', 'accion', 'cliente']
const ESTADOS = ['nuevo', 'contactado', 'cotizado', 'reunion_agendada', 'convertido', 'inactivo']
const PRIORIDADES = ['alta', 'media', 'baja']
const FUENTES = ['telegram', 'manual', 'formulario', 'referido']

const etapaBadgeColor: Record<string, string> = {
    atencion: 'badge--blue', interes: 'badge--purple',
    deseo: 'badge--pink', accion: 'badge--green', cliente: 'badge--green',
}

const prioColor: Record<string, string> = {
    alta: 'var(--pink)', media: '#FFA032', baja: 'var(--text-muted)',
}

// ── Modal Nuevo Lead ──────────────────────────────────────────
const NuevoLeadModal: React.FC<{ onClose: () => void; onCreated: () => void }> = ({
    onClose,
    onCreated,
}) => {
    const [form, setForm] = useState({
        nombre: '', email: '', telefono: '', empresa_nombre: '', cargo: '',
        servicio_interes: '', presupuesto_estimado: '', prioridad: 'media',
        fuente: 'manual', notas: '',
    })
    const [saving, setSaving] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)
        try {
            const { error } = await supabase.from('leads').insert({
                ...form,
                etapa_funnel: 'atencion',
                estado: 'nuevo',
            })
            if (error) throw error
            toast.success('✅ Lead creado exitosamente')
            onCreated()
            onClose()
        } catch (err: unknown) {
            toast.error('Error al crear lead: ' + (err instanceof Error ? err.message : 'desconocido'))
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>➕ Nuevo Lead Manual</h3>
                    <button className="btn btn--secondary btn--icon" onClick={onClose}>✕</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="grid-2">
                        <div className="form-group">
                            <label className="form-label">Nombre *</label>
                            <input className="input" required value={form.nombre}
                                onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email</label>
                            <input className="input" type="email" value={form.email}
                                onChange={(e) => setForm({ ...form, email: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Teléfono</label>
                            <input className="input" value={form.telefono}
                                onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Empresa</label>
                            <input className="input" value={form.empresa_nombre}
                                onChange={(e) => setForm({ ...form, empresa_nombre: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Cargo</label>
                            <input className="input" value={form.cargo}
                                onChange={(e) => setForm({ ...form, cargo: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Servicio de Interés</label>
                            <input className="input" value={form.servicio_interes}
                                onChange={(e) => setForm({ ...form, servicio_interes: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Presupuesto estimado</label>
                            <input className="input" value={form.presupuesto_estimado}
                                onChange={(e) => setForm({ ...form, presupuesto_estimado: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Prioridad</label>
                            <select className="input" value={form.prioridad}
                                onChange={(e) => setForm({ ...form, prioridad: e.target.value })}>
                                {PRIORIDADES.map((p) => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Fuente</label>
                            <select className="input" value={form.fuente}
                                onChange={(e) => setForm({ ...form, fuente: e.target.value })}>
                                {FUENTES.map((f) => <option key={f} value={f}>{f}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Notas</label>
                        <textarea className="input" value={form.notas} rows={3}
                            onChange={(e) => setForm({ ...form, notas: e.target.value })} />
                    </div>
                    <div className="flex gap-3">
                        <button type="submit" className="btn btn--primary" style={{ flex: 1 }} disabled={saving}>
                            {saving ? 'Guardando...' : 'Crear Lead'}
                        </button>
                        <button type="button" className="btn btn--secondary" onClick={onClose}>Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    )
}

// ── Lead Side Panel ───────────────────────────────────────────
const LeadPanel: React.FC<{ lead: Lead; onClose: () => void; onUpdated: () => void }> = ({
    lead,
    onClose,
    onUpdated: _onUpdated,
}) => {
    const [tab, setTab] = useState<'info' | 'conv' | 'cot' | 'reunion' | 'timeline'>('info')
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [cotizaciones, setCotizaciones] = useState<unknown[]>([])
    const [reuniones, setReuniones] = useState<unknown[]>([])
    const [timeline, setTimeline] = useState<unknown[]>([])
    const [chatMsg, setChatMsg] = useState('')
    const [sendingChat, setSendingChat] = useState(false)
    const [sessionId] = useState(() => {
        const key = `orbita_session_${lead.id}`
        let sid = sessionStorage.getItem(key)
        if (!sid) { sid = crypto.randomUUID(); sessionStorage.setItem(key, sid) }
        return sid
    })

    useEffect(() => {
        if (tab === 'conv') loadConversations()
        if (tab === 'cot') loadCotizaciones()
        if (tab === 'reunion') loadReuniones()
        if (tab === 'timeline') loadTimeline()
    }, [tab])

    // Realtime conversations
    useEffect(() => {
        const ch = supabase.channel(`lead-conv-${lead.id}`)
            .on('postgres_changes', {
                event: 'INSERT', schema: 'public', table: 'conversations',
                filter: `lead_id=eq.${lead.id}`
            },
                (p) => setConversations((prev) => [...prev, p.new as Conversation]))
            .subscribe()
        return () => { supabase.removeChannel(ch) }
    }, [lead.id])

    const loadConversations = async () => {
        const { data } = await supabase.from('conversations')
            .select('*').eq('lead_id', lead.id).order('created_at').limit(50)
        setConversations(data || [])
    }
    const loadCotizaciones = async () => {
        const { data } = await supabase.from('cotizaciones')
            .select('*').eq('lead_id', lead.id).order('created_at', { ascending: false })
        setCotizaciones(data || [])
    }
    const loadReuniones = async () => {
        const { data } = await supabase.from('reuniones')
            .select('*').eq('lead_id', lead.id).order('fecha_hora')
        setReuniones(data || [])
    }
    const loadTimeline = async () => {
        const { data } = await supabase.from('agent_logs')
            .select('*').eq('lead_id', lead.id).order('created_at', { ascending: false }).limit(20)
        setTimeline(data || [])
    }

    const handleSendChat = async () => {
        if (!chatMsg.trim()) return
        setSendingChat(true)
        try {
            const res = await orbitaApi.chat(lead.id, chatMsg, sessionId)
            if (res?.data?.respuesta_final) {
                toast.success('💬 Respuesta generada por ORBITA')
            }
            setChatMsg('')
            loadConversations()
        } catch {
            toast.error('Error al enviar mensaje')
        } finally {
            setSendingChat(false)
        }
    }

    const handleSendTelegram = async () => {
        if (!chatMsg.trim() || !lead.telegram_chat_id) return
        setSendingChat(true)
        try {
            await orbitaApi.sendToTelegram(lead.telegram_chat_id, chatMsg, lead.id)
            toast.success('📱 Mensaje enviado por Telegram')
            setChatMsg('')
            loadConversations()
        } catch {
            toast.error('Error al enviar por Telegram')
        } finally {
            setSendingChat(false)
        }
    }

    return (
        <div className="side-panel" style={{ width: 480 }}>
            <div className="side-panel-header">
                <div>
                    <div style={{ fontWeight: 700, fontSize: 15 }}>{lead.nombre}</div>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={`badge ${etapaBadgeColor[lead.etapa_funnel]}`}>
                            {lead.etapa_funnel.toUpperCase()}
                        </span>
                        <span className="badge" style={{ background: 'transparent', color: prioColor[lead.prioridad], border: `1px solid ${prioColor[lead.prioridad]}33` }}>
                            ↑ {lead.prioridad}
                        </span>
                        <FuenteBadge fuente={lead.fuente as 'telegram' | 'manual' | 'formulario' | 'referido'} />
                    </div>
                </div>
                <button className="btn btn--secondary btn--icon" onClick={onClose}>✕</button>
            </div>

            {/* Tabs */}
            <div className="tabs" style={{ padding: '0 1.25rem', margin: 0 }}>
                {[
                    { key: 'info', label: 'Info' },
                    { key: 'conv', label: 'Conversación' },
                    { key: 'cot', label: 'Cotizaciones' },
                    { key: 'reunion', label: 'Reuniones' },
                    { key: 'timeline', label: 'Timeline' },
                ].map((t) => (
                    <button key={t.key} className={`tab ${tab === t.key ? 'tab--active' : ''}`}
                        onClick={() => setTab(t.key as typeof tab)}>
                        {t.label}
                    </button>
                ))}
            </div>

            <div className="side-panel-body">
                {/* ── INFO ── */}
                {tab === 'info' && (
                    <div>
                        <div className="grid-2" style={{ gap: '0.625rem' }}>
                            {[
                                { label: 'Email', value: lead.email },
                                { label: 'Teléfono', value: lead.telefono },
                                { label: 'Empresa', value: lead.empresa_nombre },
                                { label: 'Cargo', value: lead.cargo },
                                { label: 'Servicio interés', value: lead.servicio_interes },
                                { label: 'Presupuesto', value: lead.presupuesto_estimado },
                                { label: 'Telegram', value: lead.telegram_username ? `@${lead.telegram_username}` : lead.telegram_chat_id },
                                { label: 'Estado', value: lead.estado },
                            ].map(({ label, value }) => (
                                <div key={label}>
                                    <div className="form-label" style={{ marginBottom: 2 }}>{label}</div>
                                    <div style={{ fontSize: 13, color: value ? 'var(--text)' : 'var(--text-muted)' }}>
                                        {value || '—'}
                                    </div>
                                </div>
                            ))}
                        </div>
                        {lead.etiquetas && lead.etiquetas.length > 0 && (
                            <div className="mt-4">
                                <div className="form-label mb-2">Etiquetas</div>
                                <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                                    {lead.etiquetas.map((tag) => (
                                        <span key={tag} className="badge badge--purple">{tag}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {lead.notas && (
                            <div className="mt-4">
                                <div className="form-label mb-2">Notas</div>
                                <p style={{ fontSize: 13, lineHeight: 1.5 }}>{lead.notas}</p>
                            </div>
                        )}
                    </div>
                )}

                {/* ── CONVERSACIÓN ── */}
                {tab === 'conv' && (
                    <div>
                        <div
                            style={{
                                minHeight: 300,
                                maxHeight: 360,
                                overflowY: 'auto',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 4,
                                marginBottom: 12,
                                padding: '4px 0',
                            }}
                        >
                            {conversations.length === 0 ? (
                                <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 13 }}>
                                    Sin conversaciones aún
                                </div>
                            ) : (
                                conversations.map((msg) => (
                                    <TelegramBubble
                                        key={msg.id}
                                        role={msg.role === 'user' ? 'user' : 'agent'}
                                        content={msg.content}
                                        agente={msg.agente}
                                        isVoice={msg.content_type === 'voice'}
                                        transcription={msg.transcripcion_voz}
                                        timestamp={formatDistanceToNow(new Date(msg.created_at), { addSuffix: true, locale: es })}
                                    />
                                ))
                            )}
                            {sendingChat && (
                                <div className="flex items-center gap-2 mt-2">
                                    <span className="text-muted" style={{ fontSize: 12 }}>⚡ Agente procesando...</span>
                                    <LoadingDots />
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* ── COTIZACIONES ── */}
                {tab === 'cot' && (
                    <div>
                        {cotizaciones.length === 0 ? (
                            <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 13 }}>Sin cotizaciones</div>
                        ) : (
                            (cotizaciones as Record<string, unknown>[]).map((c) => (
                                <div key={c.id as string} className="card" style={{ padding: '0.875rem', marginBottom: 8 }}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span style={{ fontWeight: 600 }}>{c.plan_nombre as string}</span>
                                        <span className={`badge ${c.estado === 'aceptada' ? 'badge--green' : c.estado === 'rechazada' ? 'badge--red' : 'badge--muted'}`}>
                                            {c.estado as string}
                                        </span>
                                    </div>
                                    <div style={{ fontFamily: 'Space Mono', fontSize: 16, color: 'var(--green)' }}>
                                        ${(c.valor as number)?.toLocaleString()} {c.moneda as string}
                                    </div>
                                    {Boolean(c.enviada_por_telegram) && <span className="badge badge--blue mt-2">📱 Enviado por Telegram</span>}
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* ── REUNIONES ── */}
                {tab === 'reunion' && (
                    <div>
                        {reuniones.length === 0 ? (
                            <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 13 }}>Sin reuniones</div>
                        ) : (
                            (reuniones as Record<string, unknown>[]).map((r) => (
                                <div key={r.id as string} className="card" style={{ padding: '0.875rem', marginBottom: 8 }}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span style={{ fontWeight: 600 }}>{r.titulo as string}</span>
                                        <span className={`badge ${r.estado === 'confirmada' ? 'badge--green' : r.estado === 'cancelada' ? 'badge--red' : 'badge--muted'}`}>
                                            {r.estado as string}
                                        </span>
                                    </div>
                                    <div className="text-muted" style={{ fontSize: 12 }}>
                                        📅 {new Date(r.fecha_hora as string).toLocaleString('es-CO')} · {r.tipo as string}
                                    </div>
                                    {Boolean(r.confirmada_por_telegram) && <span className="badge badge--blue mt-2">✅📱 Confirmada por Telegram</span>}
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* ── TIMELINE ── */}
                {tab === 'timeline' && (
                    <div>
                        {timeline.length === 0 ? (
                            <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', fontSize: 13 }}>Sin actividad registrada</div>
                        ) : (
                            (timeline as Record<string, unknown>[]).map((log) => (
                                <div key={log.id as string} style={{ display: 'flex', gap: 10, marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>
                                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: (log.exitoso as boolean) ? 'var(--green)' : 'var(--pink)', marginTop: 4, flexShrink: 0 }} />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: 12, fontWeight: 600 }}>
                                            <span className="badge badge--purple" style={{ marginRight: 6 }}>{log.agente as string}</span>
                                            {log.accion as string}
                                        </div>
                                        <div className="text-muted" style={{ fontSize: 10, marginTop: 2 }}>
                                            {formatDistanceToNow(new Date(log.created_at as string), { addSuffix: true, locale: es })}
                                            {log.duracion_ms ? ` · ${log.duracion_ms}ms` : ''}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* Footer with chat input (only in conv tab) */}
            {tab === 'conv' && (
                <div className="side-panel-footer">
                    <div className="flex gap-2">
                        <input
                            className="input"
                            value={chatMsg}
                            onChange={(e) => setChatMsg(e.target.value)}
                            placeholder="Escribe un mensaje..."
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChat() } }}
                            disabled={sendingChat}
                        />
                        <button className="btn btn--primary btn--sm" onClick={handleSendChat} disabled={sendingChat || !chatMsg.trim()}>
                            Enviar
                        </button>
                        {lead.telegram_chat_id && (
                            <button className="btn btn--blue btn--sm" onClick={handleSendTelegram} disabled={sendingChat || !chatMsg.trim()}>
                                📱
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

// ── Main Page ─────────────────────────────────────────────────
const Leads: React.FC = () => {
    const [searchParams] = useSearchParams()
    const [leads, setLeads] = useState<Lead[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [filterEstado, setFilterEstado] = useState('')
    const [filterEtapa, setFilterEtapa] = useState(searchParams.get('etapa') || '')
    const [filterPrioridad, setFilterPrioridad] = useState('')
    const [filterFuente, setFilterFuente] = useState('')
    const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
    const [showModal, setShowModal] = useState(false)
    const [total, setTotal] = useState(0)

    const fetchLeads = async () => {
        setLoading(true)
        let q = supabase.from('leads').select('*', { count: 'exact' })
        if (filterEstado) q = q.eq('estado', filterEstado)
        if (filterEtapa) q = q.eq('etapa_funnel', filterEtapa)
        if (filterPrioridad) q = q.eq('prioridad', filterPrioridad)
        if (filterFuente) q = q.eq('fuente', filterFuente)
        if (search) q = q.ilike('nombre', `%${search}%`)
        q = q.order('created_at', { ascending: false }).limit(100)
        const { data, count } = await q
        setLeads(data || [])
        setTotal(count || 0)
        setLoading(false)
    }

    useEffect(() => { fetchLeads() }, [filterEstado, filterEtapa, filterPrioridad, filterFuente, search])

    // Open lead from URL param
    useEffect(() => {
        const leadId = searchParams.get('id')
        if (leadId && leads.length > 0) {
            const found = leads.find((l) => l.id === leadId)
            if (found) setSelectedLead(found)
        }
    }, [leads, searchParams])

    return (
        <div>
            {/* Header */}
            <div className="page-header flex items-center justify-between">
                <div>
                    <h1 style={{ marginBottom: '0.25rem' }}>👥 Leads CRM</h1>
                    <p className="text-muted">
                        <span className="font-mono" style={{ color: 'var(--green)', fontSize: 15 }}>{total}</span> leads en total
                    </p>
                </div>
                <button className="btn btn--primary" onClick={() => setShowModal(true)}>
                    ➕ Nuevo Lead
                </button>
            </div>

            {/* Filters */}
            <div className="card mb-4" style={{ padding: '0.75rem 1rem' }}>
                <div className="flex gap-3" style={{ flexWrap: 'wrap', alignItems: 'center' }}>
                    <input
                        className="input"
                        style={{ maxWidth: 220 }}
                        placeholder="🔍 Buscar por nombre..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <select className="input" style={{ maxWidth: 140 }} value={filterEstado}
                        onChange={(e) => setFilterEstado(e.target.value)}>
                        <option value="">Estado</option>
                        {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                    </select>
                    <select className="input" style={{ maxWidth: 140 }} value={filterEtapa}
                        onChange={(e) => setFilterEtapa(e.target.value)}>
                        <option value="">Etapa AIDA</option>
                        {ETAPAS.map((e) => <option key={e} value={e}>{e}</option>)}
                    </select>
                    <select className="input" style={{ maxWidth: 130 }} value={filterPrioridad}
                        onChange={(e) => setFilterPrioridad(e.target.value)}>
                        <option value="">Prioridad</option>
                        {PRIORIDADES.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <select className="input" style={{ maxWidth: 130 }} value={filterFuente}
                        onChange={(e) => setFilterFuente(e.target.value)}>
                        <option value="">Fuente</option>
                        {FUENTES.map((f) => <option key={f} value={f}>{f}</option>)}
                    </select>
                    {(filterEstado || filterEtapa || filterPrioridad || filterFuente || search) && (
                        <button className="btn btn--secondary btn--sm" onClick={() => {
                            setFilterEstado(''); setFilterEtapa(''); setFilterPrioridad(''); setFilterFuente(''); setSearch('')
                        }}>
                            ✕ Limpiar
                        </button>
                    )}
                </div>
            </div>

            {/* Table */}
            <div className="card fade-up" style={{ padding: 0, overflow: 'hidden' }}>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Lead</th>
                                <th>Etapa AIDA</th>
                                <th>Estado</th>
                                <th>Prioridad</th>
                                <th>Fuente</th>
                                <th>Etiquetas</th>
                                <th>Último Contacto</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <tr key={i}>
                                        {Array.from({ length: 8 }).map((_, j) => (
                                            <td key={j}>
                                                <div style={{ height: 14, background: 'rgba(255,255,255,0.06)', borderRadius: 3, animation: 'pulse 1.5s infinite' }} />
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : leads.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="text-muted" style={{ textAlign: 'center', padding: '2.5rem' }}>
                                        Sin leads que coincidan con los filtros
                                    </td>
                                </tr>
                            ) : (
                                leads.map((lead) => (
                                    <tr
                                        key={lead.id}
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => setSelectedLead(lead)}
                                    >
                                        <td>
                                            <div style={{ fontWeight: 600, fontSize: 13 }}>{lead.nombre}</div>
                                            <div className="text-muted" style={{ fontSize: 11 }}>{lead.empresa_nombre || '—'}</div>
                                        </td>
                                        <td>
                                            <span className={`badge ${etapaBadgeColor[lead.etapa_funnel]}`}>
                                                {lead.etapa_funnel.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="badge badge--muted">{lead.estado}</span>
                                        </td>
                                        <td>
                                            <span style={{ color: prioColor[lead.prioridad], fontWeight: 600, fontSize: 12 }}>
                                                ● {lead.prioridad}
                                            </span>
                                        </td>
                                        <td>
                                            <FuenteBadge fuente={lead.fuente as 'telegram' | 'manual' | 'formulario' | 'referido'} />
                                        </td>
                                        <td>
                                            <div className="flex gap-1" style={{ flexWrap: 'wrap', maxWidth: 140 }}>
                                                {(lead.etiquetas || []).slice(0, 2).map((tag) => (
                                                    <span key={tag} className="badge badge--purple" style={{ fontSize: 8 }}>{tag}</span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="text-muted" style={{ fontSize: 11 }}>
                                            {formatDistanceToNow(new Date(lead.ultimo_contacto), { addSuffix: true, locale: es })}
                                        </td>
                                        <td onClick={(e) => e.stopPropagation()}>
                                            <div className="flex gap-1">
                                                <button className="btn btn--sm btn--secondary" title="Ver"
                                                    onClick={() => setSelectedLead(lead)}>👁️</button>
                                                <button className="btn btn--sm btn--secondary" title="Chat"
                                                    onClick={() => { setSelectedLead(lead) }}>💬</button>
                                                {lead.telegram_chat_id && (
                                                    <button className="btn btn--sm btn--blue" title="Telegram">📱</button>
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

            {/* Side Panel */}
            {selectedLead && (
                <>
                    <div
                        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', zIndex: 499 }}
                        onClick={() => setSelectedLead(null)}
                    />
                    <LeadPanel
                        lead={selectedLead}
                        onClose={() => setSelectedLead(null)}
                        onUpdated={fetchLeads}
                    />
                </>
            )}

            {/* New Lead Modal */}
            {showModal && (
                <NuevoLeadModal
                    onClose={() => setShowModal(false)}
                    onCreated={fetchLeads}
                />
            )}
        </div>
    )
}

export default Leads
