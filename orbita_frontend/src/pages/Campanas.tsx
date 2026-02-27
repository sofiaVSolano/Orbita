import React, { useEffect, useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'
import TelegramBubble from '../components/TelegramBubble'

interface Campaign {
    id: string
    nombre: string
    tipo: 'telegram' | 'email' | 'ambos'
    mensaje: string
    estado: string
    destinatarios_count?: number
    enviados?: number
    created_at: string
}

const TIPOS = [
    { value: 'telegram', label: '📱 Telegram', color: 'var(--blue)' },
    { value: 'email', label: '📧 Email', color: 'var(--purple)' },
    { value: 'ambos', label: '📢 Ambos', color: 'var(--pink)' },
]

const estadoConfig: Record<string, { label: string; color: string }> = {
    borrador: { label: 'borrador', color: 'var(--text-muted)' },
    activa: { label: 'activa', color: 'var(--green)' },
    enviada: { label: 'enviada', color: 'var(--blue)' },
    pausada: { label: 'pausada', color: 'var(--pink)' },
}

const INITIAL_FORM = {
    nombre: '',
    tipo: 'telegram' as Campaign['tipo'],
    mensaje: '',
    filtro_estado: 'todos',
    filtro_etapa: 'todos',
}

const MAX_CHARS = 4096

const Campanas: React.FC = () => {
    const [campaigns, setCampaigns] = useState<Campaign[]>([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState(INITIAL_FORM)
    const [previewing, setPreviewing] = useState(false)
    const [previewMsg, setPreviewMsg] = useState('')
    const [sending, setSending] = useState(false)
    const [recipients, setRecipients] = useState(0)

    const fetchCampaigns = async () => {
        setLoading(true)
        const { data } = await supabase
            .from('campanas')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(50)
        setCampaigns(data || [])
        setLoading(false)
    }

    useEffect(() => { fetchCampaigns() }, [])

    // Count recipients based on filter
    useEffect(() => {
        const count = async () => {
            let query = supabase.from('leads').select('id', { count: 'exact', head: true })
            if (form.filtro_estado !== 'todos') query = query.eq('estado', form.filtro_estado)
            if (form.filtro_etapa !== 'todos') query = query.eq('etapa_funnel', form.filtro_etapa)
            const { count: c } = await query
            setRecipients(c || 0)
        }
        count()
    }, [form.filtro_estado, form.filtro_etapa])

    const handlePreview = async () => {
        if (!form.mensaje.trim()) return
        setPreviewing(true)
        try {
            const res = await orbitaApi.previewCampaign(form.mensaje)
            setPreviewMsg(res?.data?.preview || form.mensaje)
        } catch {
            setPreviewMsg(form.mensaje)
        } finally {
            setPreviewing(false)
        }
    }

    const handleSend = async () => {
        if (!form.nombre.trim() || !form.mensaje.trim()) {
            toast.error('Completa nombre y mensaje')
            return
        }
        setSending(true)
        try {
            await orbitaApi.sendCampaign(form.tipo, form.mensaje, {
                estado: form.filtro_estado !== 'todos' ? form.filtro_estado : undefined,
                etapa: form.filtro_etapa !== 'todos' ? form.filtro_etapa : undefined,
            })
            toast.success(`📢 Campaña "${form.nombre}" enviada a ${recipients} leads`, {
                style: { color: 'var(--green)' },
            })
            setShowModal(false)
            setForm(INITIAL_FORM)
            setPreviewMsg('')
            fetchCampaigns()
        } catch {
            toast.error('Error al enviar campaña')
        } finally {
            setSending(false)
        }
    }

    const handleSaveDraft = async () => {
        const { error } = await supabase.from('campanas').insert({
            nombre: form.nombre || 'Borrador sin nombre',
            tipo: form.tipo,
            mensaje: form.mensaje,
            estado: 'borrador',
        })
        if (error) { toast.error('Error al guardar'); return }
        toast.success('✅ Borrador guardado')
        setShowModal(false)
        setForm(INITIAL_FORM)
        setPreviewMsg('')
        fetchCampaigns()
    }

    const charCount = form.mensaje.length
    const charPct = (charCount / MAX_CHARS) * 100

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <div className="flex items-center justify-between">
                    <div>
                        <h1>📢 Campañas</h1>
                        <p className="text-muted">Crea y envía campañas de marketing a tus leads</p>
                    </div>
                    <button className="btn btn--primary" onClick={() => setShowModal(true)}>
                        + Nueva Campaña
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid-4 mb-6">
                {[
                    { label: 'Total campañas', value: campaigns.length, color: 'var(--blue)' },
                    { label: 'Activas', value: campaigns.filter((c) => c.estado === 'activa').length, color: 'var(--green)' },
                    { label: 'Borradores', value: campaigns.filter((c) => c.estado === 'borrador').length, color: 'var(--text-muted)' },
                    { label: 'Enviadas', value: campaigns.filter((c) => c.estado === 'enviada').length, color: 'var(--purple)' },
                ].map((s) => (
                    <div key={s.label} className="card" style={{ textAlign: 'center' }}>
                        <div className="font-mono" style={{ fontSize: 22, color: s.color }}>{s.value}</div>
                        <div className="text-muted" style={{ fontSize: 11, marginTop: 4 }}>{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Campaigns Table */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '0.875rem 1rem', borderBottom: '1px solid var(--border)' }}>
                    <h3 style={{ fontSize: 14 }}>Historial de Campañas</h3>
                </div>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Tipo</th>
                                <th>Mensaje</th>
                                <th>Destinatarios</th>
                                <th>Estado</th>
                                <th>Fecha</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                [...Array(4)].map((_, i) => (
                                    <tr key={i}>
                                        {[...Array(6)].map((__, j) => (
                                            <td key={j}><div className="skeleton" style={{ height: 14, width: 60 }} /></td>
                                        ))}
                                    </tr>
                                ))
                            ) : campaigns.length === 0 ? (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                                        Sin campañas. Crea la primera.
                                    </td>
                                </tr>
                            ) : (
                                campaigns.map((c) => {
                                    const tipoCfg = TIPOS.find((t) => t.value === c.tipo)
                                    const estatusCfg = estadoConfig[c.estado] || estadoConfig.borrador
                                    return (
                                        <tr key={c.id}>
                                            <td style={{ fontWeight: 600, fontSize: 13 }}>{c.nombre}</td>
                                            <td>
                                                <span style={{ color: tipoCfg?.color, fontSize: 12 }}>
                                                    {tipoCfg?.label || c.tipo}
                                                </span>
                                            </td>
                                            <td style={{ maxWidth: 240 }}>
                                                <div style={{ fontSize: 12, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-muted)' }}>
                                                    {c.mensaje}
                                                </div>
                                            </td>
                                            <td className="font-mono" style={{ fontSize: 12 }}>
                                                {c.destinatarios_count ?? '—'}
                                            </td>
                                            <td>
                                                <span className="badge" style={{ color: estatusCfg.color, fontSize: 9 }}>
                                                    {estatusCfg.label}
                                                </span>
                                            </td>
                                            <td className="text-muted" style={{ fontSize: 11 }}>
                                                {formatDistanceToNow(new Date(c.created_at), { addSuffix: true, locale: es })}
                                            </td>
                                        </tr>
                                    )
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* New Campaign Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) { setShowModal(false); setPreviewMsg('') } }}>
                    <div className="modal" style={{ width: '90vw', maxWidth: 780, maxHeight: '90vh', overflowY: 'auto' }}>
                        <div className="modal-header">
                            <h2>📢 Nueva Campaña</h2>
                            <button className="btn btn--icon" onClick={() => { setShowModal(false); setPreviewMsg('') }}>✕</button>
                        </div>

                        <div className="grid-2" style={{ gap: '1.5rem', padding: '1.25rem' }}>
                            {/* Form Column */}
                            <div>
                                <div className="form-group mb-4">
                                    <label className="form-label">Nombre de la campaña *</label>
                                    <input className="input" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} placeholder="Campaña Black Friday, Lanzamiento..." />
                                </div>

                                {/* Canal */}
                                <div className="form-group mb-4">
                                    <label className="form-label">Canal de envío *</label>
                                    <div className="flex gap-2">
                                        {TIPOS.map((t) => (
                                            <button
                                                key={t.value}
                                                className="btn btn--sm"
                                                style={{
                                                    color: t.color,
                                                    background: form.tipo === t.value ? `rgba(${t.color === 'var(--blue)' ? '0,209,255' : t.color === 'var(--purple)' ? '189,147,249' : '255,77,148'},0.15)` : 'transparent',
                                                    border: `1px solid ${form.tipo === t.value ? t.color : 'var(--border)'}`,
                                                    flex: 1,
                                                }}
                                                onClick={() => setForm({ ...form, tipo: t.value as Campaign['tipo'] })}
                                            >
                                                {t.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Filters */}
                                <div className="grid-2 mb-4" style={{ gap: '0.75rem' }}>
                                    <div className="form-group">
                                        <label className="form-label">Filtro: Estado</label>
                                        <select className="input" value={form.filtro_estado} onChange={(e) => setForm({ ...form, filtro_estado: e.target.value })}>
                                            <option value="todos">Todos</option>
                                            <option value="activo">Activos</option>
                                            <option value="calificado">Calificados</option>
                                            <option value="cliente">Clientes</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Filtro: Etapa AIDA</label>
                                        <select className="input" value={form.filtro_etapa} onChange={(e) => setForm({ ...form, filtro_etapa: e.target.value })}>
                                            <option value="todos">Todas</option>
                                            <option value="atencion">Atención</option>
                                            <option value="interes">Interés</option>
                                            <option value="deseo">Deseo</option>
                                            <option value="accion">Acción</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="card" style={{ padding: '0.75rem', marginBottom: '1rem', background: 'rgba(0,209,255,0.06)', border: '1px solid rgba(0,209,255,0.2)' }}>
                                    <div className="text-muted" style={{ fontSize: 12 }}>
                                        👥 Destinatarios estimados: <span className="font-mono" style={{ color: 'var(--blue)', fontSize: 14 }}>{recipients}</span> leads
                                    </div>
                                </div>

                                {/* Message */}
                                <div className="form-group">
                                    <label className="form-label">
                                        Mensaje *{' '}
                                        <span className="font-mono" style={{ fontSize: 10, color: charPct > 90 ? 'var(--pink)' : 'var(--text-muted)' }}>
                                            {charCount}/{MAX_CHARS}
                                        </span>
                                    </label>
                                    <textarea
                                        className="input"
                                        style={{ minHeight: 120, resize: 'vertical' }}
                                        value={form.mensaje}
                                        onChange={(e) => setForm({ ...form, mensaje: e.target.value.slice(0, MAX_CHARS) })}
                                        placeholder="Hola {nombre}, te contactamos desde ORBITA para..."
                                    />
                                    {/* Char progress */}
                                    <div style={{ height: 2, background: 'var(--border)', borderRadius: 1, marginTop: 4 }}>
                                        <div style={{ height: '100%', width: `${charPct}%`, background: charPct > 90 ? 'var(--pink)' : 'var(--green)', borderRadius: 1, transition: 'width 0.2s' }} />
                                    </div>
                                    <div className="text-muted" style={{ fontSize: 10, marginTop: 4 }}>
                                        Variables: {'{nombre}'}, {'{empresa}'}, {'{agente}'}
                                    </div>
                                </div>
                            </div>

                            {/* Preview Column */}
                            <div>
                                <div className="form-label mb-2">Vista Previa</div>
                                <div className="card" style={{ minHeight: 240, padding: '1rem', background: 'rgba(255,255,255,0.02)' }}>
                                    {previewMsg ? (
                                        <TelegramBubble
                                            role="agent"
                                            content={previewMsg}
                                            agente="ORBITA"
                                            timestamp="ahora"
                                        />
                                    ) : (
                                        <div className="text-muted" style={{ textAlign: 'center', padding: '2rem 1rem', fontSize: 12 }}>
                                            Haz clic en "Vista Previa con IA" para ver cómo quedará el mensaje personalizado
                                        </div>
                                    )}
                                </div>

                                <button
                                    className="btn btn--secondary w-full mt-3"
                                    onClick={handlePreview}
                                    disabled={previewing || !form.mensaje.trim()}
                                >
                                    {previewing ? '⏳ Generando...' : '🤖 Vista Previa con IA'}
                                </button>

                                {/* Tips */}
                                <div className="card" style={{ padding: '0.75rem', marginTop: '0.75rem', background: 'rgba(80,250,123,0.04)', border: '1px solid rgba(80,250,123,0.12)' }}>
                                    <div className="form-label mb-2">💡 Tips</div>
                                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                                        {[
                                            'Usa {nombre} para personalizar',
                                            'Mensajes de < 200 chars tienen más engagement',
                                            'Incluye un llamado a la acción claro',
                                            'Telegram admite emojis 😊',
                                        ].map((tip) => (
                                            <li key={tip} className="text-muted" style={{ fontSize: 11, padding: '3px 0', paddingLeft: 12, position: 'relative' }}>
                                                <span style={{ position: 'absolute', left: 0, color: 'var(--green)' }}>·</span>
                                                {tip}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                            <button className="btn btn--secondary" onClick={handleSaveDraft} disabled={sending}>
                                💾 Guardar borrador
                            </button>
                            <button
                                className="btn btn--primary"
                                onClick={handleSend}
                                disabled={sending || !form.nombre.trim() || !form.mensaje.trim()}
                            >
                                {sending ? '⏳ Enviando...' : `📢 Enviar a ${recipients} leads`}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Campanas
