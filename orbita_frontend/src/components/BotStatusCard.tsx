import React from 'react'

interface BotStatusCardProps {
    username?: string
    nombre?: string
    isActive?: boolean
    leadsHoy?: number
    mensajesHoy?: number
    vocesHoy?: number
    onNavigate?: () => void
    loading?: boolean
}

const BotStatusCard: React.FC<BotStatusCardProps> = ({
    username = 'orbita_bot',
    nombre = 'ORBITA Bot',
    isActive = false,
    leadsHoy = 0,
    mensajesHoy = 0,
    vocesHoy = 0,
    onNavigate,
    loading = false,
}) => {
    return (
        <div className="card card--blue fade-up">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            background: 'rgba(0, 209, 255, 0.15)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 20,
                            border: '1px solid rgba(0, 209, 255, 0.3)',
                        }}
                    >
                        📱
                    </div>
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 15 }}>{nombre}</div>
                        <div className="text-muted" style={{ fontSize: 12 }}>
                            @{username}
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`dot-pulse dot-pulse--${isActive ? 'green' : 'red'}`} />
                    <span
                        className="badge"
                        style={{
                            background: isActive ? 'rgba(80,250,123,0.15)' : 'rgba(255,80,80,0.15)',
                            color: isActive ? 'var(--green)' : '#FF5050',
                        }}
                    >
                        {isActive ? '● ACTIVO' : '○ INACTIVO'}
                    </span>
                </div>
            </div>

            {loading ? (
                <div style={{ height: 60, background: 'rgba(255,255,255,0.04)', borderRadius: 4, animation: 'pulse 1.5s infinite' }} />
            ) : (
                <div
                    style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr 1fr',
                        gap: '0.75rem',
                        marginBottom: '1rem',
                    }}
                >
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontFamily: 'Space Mono', fontSize: 20, fontWeight: 700, color: 'var(--blue)' }}>
                            {leadsHoy}
                        </div>
                        <div className="text-muted" style={{ fontSize: 10, marginTop: 2 }}>
                            Leads hoy
                        </div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontFamily: 'Space Mono', fontSize: 20, fontWeight: 700, color: 'var(--blue)' }}>
                            {mensajesHoy}
                        </div>
                        <div className="text-muted" style={{ fontSize: 10, marginTop: 2 }}>
                            Mensajes
                        </div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontFamily: 'Space Mono', fontSize: 20, fontWeight: 700, color: 'var(--purple)' }}>
                            {vocesHoy}
                        </div>
                        <div className="text-muted" style={{ fontSize: 10, marginTop: 2 }}>
                            🎙️ Voces
                        </div>
                    </div>
                </div>
            )}

            {onNavigate && (
                <button className="btn btn--blue w-full" onClick={onNavigate}>
                    📱 Ir a Telegram
                </button>
            )}
        </div>
    )
}

export default BotStatusCard
