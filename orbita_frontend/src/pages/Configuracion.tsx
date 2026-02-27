import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'

interface Empresa {
    id: string
    nombre: string
    sector?: string
    descripcion?: string
    telefono?: string
    email?: string
    sitio_web?: string
}

interface NotifToggle {
    label: string
    key: string
    description: string
    color: string
}

const NOTIF_TOGGLES: NotifToggle[] = [
    { key: 'nuevo_lead', label: 'Nuevo lead captado', description: 'Notificar cuando un lead nuevo contacte al bot', color: 'var(--blue)' },
    { key: 'cotizacion_enviada', label: 'Cotización enviada', description: 'Notificar cuando el bot envíe una cotización', color: 'var(--purple)' },
    { key: 'reunion_agendada', label: 'Reunión agendada', description: 'Notificar cuando el bot agende una reunión', color: 'var(--green)' },
    { key: 'lead_calificado', label: 'Lead calificado IA', description: 'Notificar cuando un lead pasa score de calificación', color: 'var(--pink)' },
    { key: 'alerta_sistema', label: 'Alertas del sistema', description: 'Errores críticos y advertencias del sistema', color: '#FF5050' },
]

const Configuracion: React.FC = () => {
    const [empresa, setEmpresa] = useState<Empresa | null>(null)
    const [formEmpresa, setFormEmpresa] = useState<Partial<Empresa>>({})
    const [saving, setSaving] = useState(false)
    const [notifs, setNotifs] = useState<Record<string, boolean>>({})
    const [configuringWebhook, setConfiguringWebhook] = useState<'leads' | 'admin' | 'ambos' | null>(null)

    // Bot info
    const { data: botData, refetch: refetchBot } = useQuery({
        queryKey: ['botInfoConfig'],
        queryFn: () => orbitaApi.getBotInfo(),
        retry: 1,
    })
    const bot = botData?.data || {}
    const botLeads = bot.bot_leads || {}
    const botAdmin = bot.bot_admin || {}

    // Load empresa
    useEffect(() => {
        const fetch = async () => {
            const { data } = await supabase.from('empresas').select('*').limit(1).single()
            if (data) {
                setEmpresa(data)
                setFormEmpresa(data)
            }
        }
        fetch()
    }, [])

    // Load notification preferences from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('orbita_notif_prefs')
        if (saved) {
            try { setNotifs(JSON.parse(saved)) } catch { /* ignore */ }
        } else {
            const defaults: Record<string, boolean> = {}
            NOTIF_TOGGLES.forEach((t) => { defaults[t.key] = true })
            setNotifs(defaults)
        }
    }, [])

    const handleSaveEmpresa = async () => {
        setSaving(true)
        const { error } = await supabase
            .from('empresas')
            .update(formEmpresa)
            .eq('id', empresa?.id || '')
        if (error) { toast.error('Error al guardar'); setSaving(false); return }
        setEmpresa({ ...empresa, ...formEmpresa } as Empresa)
        toast.success('✅ Configuración de empresa guardada')
        setSaving(false)
    }

    const toggleNotif = (key: string) => {
        const updated = { ...notifs, [key]: !notifs[key] }
        setNotifs(updated)
        localStorage.setItem('orbita_notif_prefs', JSON.stringify(updated))
        toast.success(updated[key] ? `🔔 Activada: ${key}` : `🔕 Desactivada: ${key}`, { duration: 1500 })
    }

    const handleSetupWebhook = async (tipo: 'leads' | 'admin' | 'ambos') => {
        setConfiguringWebhook(tipo)
        try {
            let res
            if (tipo === 'ambos') res = await orbitaApi.setupWebhooks()
            else if (tipo === 'leads') res = await orbitaApi.setupLeadsWebhook()
            else if (tipo === 'admin') res = await orbitaApi.setupAdminWebhook()
            
            if (res?.success) {
                toast.success(`🔗 Webhook ${tipo === 'ambos' ? 'de ambos bots' : `del bot de ${tipo}`} configurado`)
                refetchBot()
            } else {
                toast.error('Error al configurar webhook')
            }
        } catch {
            toast.error('No se pudo conectar al backend')
        } finally {
            setConfiguringWebhook(null)
        }
    }

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <h1>⚙️ Configuración</h1>
                <p className="text-muted">Ajustes de la empresa, Telegram y notificaciones</p>
            </div>

            <div className="grid-2" style={{ gap: '1.5rem', alignItems: 'start' }}>
                {/* Left column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    {/* Empresa Form */}
                    <div className="card card--green fade-up">
                        <h3 style={{ marginBottom: '1.25rem' }}>🏢 Mi empresa</h3>
                        <div className="form-group mb-3">
                            <label className="form-label">Nombre de la empresa</label>
                            <input className="input" value={formEmpresa.nombre || ''} onChange={(e) => setFormEmpresa({ ...formEmpresa, nombre: e.target.value })} />
                        </div>
                        <div className="grid-2 mb-3" style={{ gap: '0.75rem' }}>
                            <div className="form-group">
                                <label className="form-label">Sector</label>
                                <select className="input" value={formEmpresa.sector || ''} onChange={(e) => setFormEmpresa({ ...formEmpresa, sector: e.target.value })}>
                                    <option value="">Seleccionar...</option>
                                    {['SaaS', 'Tecnología', 'Consultoría', 'Manufactura', 'Servicios', 'E-commerce', 'Salud', 'Educación', 'Otro'].map((s) => (
                                        <option key={s} value={s.toLowerCase()}>{s}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Teléfono</label>
                                <input className="input" value={formEmpresa.telefono || ''} onChange={(e) => setFormEmpresa({ ...formEmpresa, telefono: e.target.value })} placeholder="+57 300 000 0000" />
                            </div>
                        </div>
                        <div className="form-group mb-3">
                            <label className="form-label">Email corporativo</label>
                            <input className="input" type="email" value={formEmpresa.email || ''} onChange={(e) => setFormEmpresa({ ...formEmpresa, email: e.target.value })} placeholder="contacto@empresa.com" />
                        </div>
                        <div className="form-group mb-3">
                            <label className="form-label">Sitio web</label>
                            <input className="input" value={formEmpresa.sitio_web || ''} onChange={(e) => setFormEmpresa({ ...formEmpresa, sitio_web: e.target.value })} placeholder="https://empresa.com" />
                        </div>
                        <div className="form-group mb-4">
                            <label className="form-label">Descripción del negocio</label>
                            <textarea
                                className="input"
                                style={{ minHeight: 90, resize: 'vertical' }}
                                value={formEmpresa.descripcion || ''}
                                onChange={(e) => setFormEmpresa({ ...formEmpresa, descripcion: e.target.value })}
                                placeholder="Describe brevemente tu empresa y qué ofrece..."
                            />
                        </div>
                        <button className="btn btn--primary w-full" onClick={handleSaveEmpresa} disabled={saving}>
                            {saving ? '⏳ Guardando...' : '💾 Guardar cambios'}
                        </button>
                    </div>

                    {/* Notification toggles */}
                    <div className="card fade-up">
                        <h3 style={{ marginBottom: '1.25rem' }}>🔔 Notificaciones al Admin</h3>
                        <p className="text-muted" style={{ fontSize: 12, marginBottom: '1rem' }}>
                            Configura qué eventos generan notificaciones vía Telegram al administrador
                        </p>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {NOTIF_TOGGLES.map((t) => (
                                <div
                                    key={t.key}
                                    style={{
                                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                        padding: '0.7rem 0.9rem', background: 'rgba(255,255,255,0.02)',
                                        borderRadius: 6, border: '1px solid var(--border)',
                                    }}
                                >
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 600, fontSize: 12, color: notifs[t.key] ? t.color : 'var(--text-muted)' }}>
                                            {t.label}
                                        </div>
                                        <div className="text-muted" style={{ fontSize: 11 }}>{t.description}</div>
                                    </div>
                                    {/* Toggle switch */}
                                    <button
                                        onClick={() => toggleNotif(t.key)}
                                        style={{
                                            width: 40, height: 22, borderRadius: 11,
                                            background: notifs[t.key] ? 'var(--green)' : 'rgba(255,255,255,0.1)',
                                            border: 'none', cursor: 'pointer', position: 'relative',
                                            transition: 'background 0.2s', flexShrink: 0,
                                        }}
                                    >
                                        <span style={{
                                            display: 'block', width: 16, height: 16, borderRadius: '50%',
                                            background: 'var(--bg-primary)', position: 'absolute',
                                            top: 3, left: notifs[t.key] ? 21 : 3, transition: 'left 0.2s',
                                        }} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    {/* Telegram config — Dual Bot */}
                    <div className="card card--blue fade-up">
                        <div className="flex items-center justify-between mb-4">
                            <h3>📱 Configuración de Telegram</h3>
                            <button
                                className="btn btn--sm btn--secondary"
                                onClick={() => handleSetupWebhook('ambos')}
                                disabled={configuringWebhook === 'ambos'}
                                style={{ fontSize: 11 }}
                            >
                                {configuringWebhook === 'ambos' ? '⏳' : '🔄'} Ambos
                            </button>
                        </div>

                        {/* Bot de Leads */}
                        <div style={{
                            padding: '0.875rem',
                            background: 'rgba(80,250,123,0.06)',
                            borderRadius: 6,
                            marginBottom: '1rem',
                            border: '1px solid rgba(80,250,123,0.15)'
                        }}>
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <span style={{ fontSize: 18 }}>📱</span>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: 13 }}>Bot de Leads</div>
                                        <div className="text-muted" style={{ fontSize: 10 }}>Público para prospectos</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`dot-pulse dot-pulse--${botLeads.webhook_url ? 'green' : 'red'}`} style={{ width: 6, height: 6 }} />
                                    <span style={{ fontSize: 10, color: botLeads.webhook_url ? 'var(--green)' : '#FF5050' }}>
                                        {botLeads.webhook_url ? 'ACTIVO' : 'SIN CONFIG'}
                                    </span>
                                </div>
                            </div>

                            <div className="grid-2" style={{ gap: '0.5rem', marginBottom: '0.75rem' }}>
                                <div>
                                    <div className="form-label" style={{ fontSize: 10 }}>Username</div>
                                    <div className="font-mono" style={{ fontSize: 11, color: 'var(--green)' }}>
                                        @{botLeads.username || 'orbita_leads_bot'}
                                    </div>
                                </div>
                                <div>
                                    <div className="form-label" style={{ fontSize: 10 }}>Webhook</div>
                                    <div style={{ fontSize: 10 }}>
                                        {botLeads.webhook_url ? '✅ Configurado' : '⚠️ No configurado'}
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    className="btn btn--sm btn--green"
                                    onClick={() => handleSetupWebhook('leads')}
                                    disabled={configuringWebhook === 'leads'}
                                    style={{ flex: 1, fontSize: 10 }}
                                >
                                    {configuringWebhook === 'leads' ? '⏳' : '🔄 Webhook'}
                                </button>
                                {botLeads.username && (
                                    <a
                                        href={`https://t.me/${botLeads.username}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn--sm btn--secondary"
                                        style={{ flex: 1, fontSize: 10, textAlign: 'center', textDecoration: 'none' }}
                                    >
                                        🔗 Abrir
                                    </a>
                                )}
                            </div>
                        </div>

                        {/* Bot de Admin */}
                        <div style={{
                            padding: '0.875rem',
                            background: 'rgba(0,209,255,0.06)',
                            borderRadius: 6,
                            marginBottom: '1rem',
                            border: '1px solid rgba(0,209,255,0.15)'
                        }}>
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <span style={{ fontSize: 18 }}>🛸</span>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: 13 }}>Bot de Admin</div>
                                        <div className="text-muted" style={{ fontSize: 10 }}>Privado para equipo</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`dot-pulse dot-pulse--${botAdmin.webhook_url ? 'blue' : 'gray'}`} style={{ width: 6, height: 6 }} />
                                    <span style={{ fontSize: 10, color: botAdmin.webhook_url ? 'var(--blue)' : '#8B949E' }}>
                                        {botAdmin.webhook_url ? 'ACTIVO' : 'SIN CONFIG'}
                                    </span>
                                </div>
                            </div>

                            <div className="grid-2" style={{ gap: '0.5rem', marginBottom: '0.75rem' }}>
                                <div>
                                    <div className="form-label" style={{ fontSize: 10 }}>Username</div>
                                    <div className="font-mono" style={{ fontSize: 11, color: 'var(--blue)' }}>
                                        @{botAdmin.username || 'orbita_admin_bot'}
                                    </div>
                                </div>
                                <div>
                                    <div className="form-label" style={{ fontSize: 10 }}>Comandos</div>
                                    <div className="font-mono" style={{ fontSize: 9, color: 'var(--text-muted)' }}>
                                        /leads /stats /alertas
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    className="btn btn--sm btn--blue"
                                    onClick={() => handleSetupWebhook('admin')}
                                    disabled={configuringWebhook === 'admin'}
                                    style={{ flex: 1, fontSize: 10 }}
                                >
                                    {configuringWebhook === 'admin' ? '⏳' : '🔄 Webhook'}
                                </button>
                                {botAdmin.username && (
                                    <a
                                        href={`https://t.me/${botAdmin.username}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn--sm btn--secondary"
                                        style={{ flex: 1, fontSize: 10, textAlign: 'center', textDecoration: 'none' }}
                                    >
                                        🔗 Abrir
                                    </a>
                                )}
                            </div>
                        </div>

                        {/* Setup instructions */}
                        <div style={{ marginTop: '1.25rem', padding: '0.875rem', background: 'rgba(255,255,255,0.02)', borderRadius: 6, border: '1px solid var(--border)' }}>
                            <div className="form-label mb-2">📋 Instrucciones de configuración</div>
                            <ol style={{ listStyle: 'none', padding: 0, margin: 0, counterReset: 'steps' }}>
                                {[
                                    'Asegúrate de que el backend esté corriendo en ' + (import.meta.env.VITE_API_URL || 'http://localhost:8000'),
                                    'Haz clic en "Reconfigurar Webhook" para registrar la URL con BotFather',
                                    'Envía /start al bot desde Telegram para verificar la conexión',
                                    'Comparte el enlace del bot con tus leads para empezar a captar',
                                ].map((step, i) => (
                                    <li key={i} style={{ fontSize: 11, color: 'var(--text-muted)', padding: '4px 0', display: 'flex', gap: 8 }}>
                                        <span style={{ color: 'var(--blue)', fontWeight: 700, flexShrink: 0 }}>{i + 1}.</span>
                                        {step}
                                    </li>
                                ))}
                            </ol>
                        </div>
                    </div>

                    {/* System info */}
                    <div className="card fade-up">
                        <h3 style={{ marginBottom: '1rem' }}>ℹ️ Información del Sistema</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            {[
                                { label: 'Versión ORBITA', value: 'v1.0.0' },
                                { label: 'Backend URL', value: import.meta.env.VITE_API_URL || 'http://localhost:8000' },
                                { label: 'Supabase', value: import.meta.env.VITE_SUPABASE_URL ? '✅ Conectado' : '⚠️ No configurado' },
                                { label: 'Modo', value: import.meta.env.PROD ? 'Producción' : 'Desarrollo' },
                            ].map((row) => (
                                <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
                                    <span className="text-muted">{row.label}</span>
                                    <span className="font-mono" style={{ fontSize: 11 }}>{row.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Danger zone */}
                    <div className="card" style={{ border: '1px solid rgba(255,80,80,0.2)' }}>
                        <h3 style={{ marginBottom: '0.75rem', color: '#FF5050', fontSize: 13 }}>⚠️ Zona de peligro</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            <button
                                className="btn btn--secondary"
                                style={{ color: '#FF5050', borderColor: 'rgba(255,80,80,0.3)', fontSize: 12 }}
                                onClick={() => {
                                    localStorage.removeItem('orbita_token')
                                    window.location.href = '/login'
                                }}
                            >
                                🚪 Cerrar sesión
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Configuracion
