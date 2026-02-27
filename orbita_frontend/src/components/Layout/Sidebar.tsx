import React, { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabase'
import { orbitaApi } from '../../lib/api'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

const navItems = [
    { path: '/dashboard', emoji: '🏠', label: 'Dashboard' },
    { path: '/leads', emoji: '👥', label: 'Leads CRM' },
    { path: '/conversaciones', emoji: '💬', label: 'Conversaciones' },
    { path: '/telegram', emoji: '📱', label: 'Telegram' },
    { path: '/cotizaciones', emoji: '📄', label: 'Cotizaciones' },
    { path: '/reuniones', emoji: '🗓️', label: 'Reuniones' },
    { path: '/campanas', emoji: '📧', label: 'Campañas' },
    { path: '/agentes', emoji: '🤖', label: 'Agentes' },
    { path: '/analitica', emoji: '📊', label: 'Analítica' },
    { path: '/configuracion', emoji: '⚙️', label: 'Configuración' },
]

const Sidebar: React.FC = () => {
    const navigate = useNavigate()
    const [leadsActivos, setLeadsActivos] = useState(0)
    const [botLeads, setBotLeads] = useState<{ username?: string; webhook_url?: string } | null>(null)
    const [botAdmin, setBotAdmin] = useState<{ username?: string; webhook_url?: string } | null>(null)
    const [ultimaActividad, setUltimaActividad] = useState<Date | null>(null)

    // Supabase Realtime — contador de leads activos
    useEffect(() => {
        const fetchLeads = async () => {
            const { count } = await supabase
                .from('leads')
                .select('id', { count: 'exact', head: true })
                .neq('estado', 'inactivo')
            setLeadsActivos(count || 0)
        }
        fetchLeads()

        const channel = supabase
            .channel('sidebar-leads')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'leads' }, fetchLeads)
            .subscribe()

        return () => { supabase.removeChannel(channel) }
    }, [])

    // Bot info — ahora retorna bot_leads y bot_admin
    useEffect(() => {
        orbitaApi.getBotInfo()
            .then((res: Record<string, unknown> & { data?: { bot_leads?: { username?: string; webhook_url?: string }; bot_admin?: { username?: string; webhook_url?: string } } }) => {
                if (res?.data) {
                    setBotLeads(res.data.bot_leads ?? null)
                    setBotAdmin(res.data.bot_admin ?? null)
                }
            })
            .catch(() => { })
    }, [])

    // Última actividad de agent_logs
    useEffect(() => {
        const fetchActividad = async () => {
            const { data } = await supabase
                .from('agent_logs')
                .select('created_at')
                .order('created_at', { ascending: false })
                .limit(1)
                .maybeSingle()
            if (data?.created_at) setUltimaActividad(new Date(data.created_at))
        }
        fetchActividad()

        const channel = supabase
            .channel('sidebar-activity')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'agent_logs' }, () => {
                setUltimaActividad(new Date())
            })
            .subscribe()

        return () => { supabase.removeChannel(channel) }
    }, [])

    const handleLogout = () => {
        localStorage.removeItem('orbita_token')
        navigate('/login')
    }

    return (
        <aside
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: 'var(--sidebar-width)',
                height: '100vh',
                background: 'var(--bg-primary)',
                borderRight: '1px solid rgba(255,255,255,0.06)',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 200,
                overflow: 'hidden',
            }}
        >
            {/* Header */}
            <div style={{ padding: '1.25rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="flex items-center gap-2" style={{ marginBottom: 8 }}>
                    {/* Animated orbit logo */}
                    <div style={{ position: 'relative', width: 28, height: 28 }}>
                        <div
                            style={{
                                position: 'absolute',
                                inset: 0,
                                borderRadius: '50%',
                                border: '2px solid var(--green)',
                                animation: 'orbit 3s linear infinite',
                            }}
                        />
                        <div
                            style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                width: 8,
                                height: 8,
                                background: 'var(--green)',
                                borderRadius: '50%',
                                transform: 'translate(-50%, -50%)',
                                boxShadow: '0 0 8px var(--green)',
                            }}
                        />
                    </div>
                    <span
                        style={{
                            fontFamily: 'Exo 2, sans-serif',
                            fontWeight: 900,
                            fontSize: 22,
                            letterSpacing: 2,
                            color: 'var(--text)',
                        }}
                    >
                        ORBITA
                    </span>
                </div>
                <div
                    className="badge badge--green"
                    style={{ animation: 'pulse 2s ease-in-out infinite' }}
                >
                    ● SISTEMA ACTIVO
                </div>
            </div>

            {/* Navigation */}
            <nav style={{ flex: 1, padding: '0.5rem 0', overflowY: 'auto' }}>
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: 10,
                            padding: '9px 1rem',
                            fontSize: 13,
                            fontWeight: isActive ? 600 : 400,
                            color: isActive ? 'var(--green)' : 'var(--text-muted)',
                            background: isActive ? 'rgba(80, 250, 123, 0.06)' : 'transparent',
                            borderLeft: isActive ? '2px solid var(--green)' : '2px solid transparent',
                            textDecoration: 'none',
                            transition: 'all 0.15s',
                        })}
                        onMouseEnter={(e) => {
                            const el = e.currentTarget as HTMLElement
                            if (!el.getAttribute('aria-current')) {
                                el.style.color = 'var(--text)'
                                el.style.background = 'rgba(255,255,255,0.03)'
                            }
                        }}
                        onMouseLeave={(e) => {
                            const el = e.currentTarget as HTMLElement
                            if (!el.getAttribute('aria-current')) {
                                el.style.color = 'var(--text-muted)'
                                el.style.background = 'transparent'
                            }
                        }}
                    >
                        <span style={{ fontSize: 15, width: 20, textAlign: 'center' }}>{item.emoji}</span>
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div
                style={{
                    padding: '0.875rem 1rem',
                    borderTop: '1px solid rgba(255,255,255,0.06)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 6,
                }}
            >
                <div className="flex items-center gap-2">
                    <span
                        style={{
                            fontFamily: 'Space Mono',
                            fontSize: 11,
                            color: 'var(--green)',
                            fontWeight: 700,
                        }}
                    >
                        {leadsActivos}
                    </span>
                    <span className="text-muted" style={{ fontSize: 11 }}>
                        leads activos
                    </span>
                </div>

                {/* Bot de leads — el que ven los prospectos */}
                {botLeads && (
                    <div className="flex items-center gap-2">
                        <span
                            className={`dot-pulse dot-pulse--${botLeads.webhook_url ? 'green' : 'red'}`}
                            style={{ width: 6, height: 6 }}
                        />
                        <span className="text-muted" style={{ fontSize: 11 }}>
                            {botLeads.username ? `@${botLeads.username}` : 'Bot leads sin config'}
                        </span>
                        <span
                            style={{
                                fontSize: 9,
                                color: 'var(--cyan)',
                                opacity: 0.6,
                                fontWeight: 600,
                            }}
                        >
                            leads
                        </span>
                    </div>
                )}

                {/* Bot de admin — indicador discreto */}
                {botAdmin && (
                    <div className="flex items-center gap-2">
                        <span
                            className={`dot-pulse dot-pulse--${botAdmin.webhook_url ? 'blue' : 'gray'}`}
                            style={{ width: 6, height: 6 }}
                        />
                        <span className="text-muted" style={{ fontSize: 11, opacity: 0.6 }}>
                            {botAdmin.username ? `@${botAdmin.username}` : 'Bot admin sin config'}
                        </span>
                        <span
                            style={{
                                fontSize: 9,
                                color: 'var(--purple)',
                                opacity: 0.5,
                                fontWeight: 600,
                            }}
                        >
                            admin
                        </span>
                    </div>
                )}

                {ultimaActividad && (
                    <div className="text-muted" style={{ fontSize: 10 }}>
                        Última act.:{' '}
                        {formatDistanceToNow(ultimaActividad, { addSuffix: true, locale: es })}
                    </div>
                )}

                <div className="divider" style={{ margin: '4px 0' }} />

                <button
                    className="btn btn--secondary"
                    style={{ fontSize: 11, padding: '5px 8px', width: '100%' }}
                    onClick={handleLogout}
                >
                    Cerrar sesión
                </button>
            </div>
        </aside>
    )
}

export default Sidebar
