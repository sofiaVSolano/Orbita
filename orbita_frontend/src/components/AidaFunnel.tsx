import React from 'react'

interface AidaFunnelProps {
    atencion?: number
    interes?: number
    deseo?: number
    accion?: number
    loading?: boolean
}

const AidaFunnel: React.FC<AidaFunnelProps> = ({
    atencion = 0,
    interes = 0,
    deseo = 0,
    accion = 0,
    loading = false,
}) => {
    const total = atencion + interes + deseo + accion || 1

    const stages = [
        { label: 'ATENCIÓN', value: atencion, color: 'var(--blue)', bg: 'rgba(0, 209, 255, 0.15)' },
        { label: 'INTERÉS', value: interes, color: 'var(--purple)', bg: 'rgba(189, 147, 249, 0.15)' },
        { label: 'DESEO', value: deseo, color: 'var(--pink)', bg: 'rgba(255, 77, 148, 0.15)' },
        { label: 'ACCIÓN', value: accion, color: 'var(--green)', bg: 'rgba(80, 250, 123, 0.15)' },
    ]

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {stages.map((stage, i) => {
                const pct = Math.round((stage.value / total) * 100)
                return (
                    <div key={stage.label}>
                        <div className="flex items-center justify-between mb-1">
                            <span
                                className="badge"
                                style={{ background: stage.bg, color: stage.color }}
                            >
                                {stage.label}
                            </span>
                            <div className="flex items-center gap-2">
                                <span
                                    style={{
                                        fontFamily: 'Space Mono',
                                        fontSize: 13,
                                        fontWeight: 700,
                                        color: stage.color,
                                    }}
                                >
                                    {loading ? '—' : stage.value}
                                </span>
                                <span className="text-muted" style={{ fontSize: 11 }}>
                                    {loading ? '' : `${pct}%`}
                                </span>
                            </div>
                        </div>
                        <div
                            style={{
                                height: 6,
                                background: 'rgba(255,255,255,0.06)',
                                borderRadius: 3,
                                overflow: 'hidden',
                            }}
                        >
                            {!loading && (
                                <div
                                    style={{
                                        height: '100%',
                                        width: `${pct}%`,
                                        background: stage.color,
                                        borderRadius: 3,
                                        transition: 'width 1s ease',
                                        opacity: 0.7 + 0.07 * i,
                                    }}
                                />
                            )}
                        </div>
                    </div>
                )
            })}
        </div>
    )
}

export default AidaFunnel
