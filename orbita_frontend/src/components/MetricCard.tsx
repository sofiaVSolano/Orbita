import React from 'react'

interface MetricCardProps {
    label: string
    value: string | number
    icon?: string
    color?: 'green' | 'pink' | 'blue' | 'purple'
    change?: string
    loading?: boolean
    delay?: number
}

const MetricCard: React.FC<MetricCardProps> = ({
    label,
    value,
    icon,
    color = 'green',
    change,
    loading = false,
    delay = 0,
}) => {
    return (
        <div
            className={`card card--${color} fade-up`}
            style={{ animationDelay: `${delay}s` }}
        >
            <div className="flex items-center justify-between mb-2">
                <span className="text-muted font-mono" style={{ fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>
                    {label}
                </span>
                {icon && <span style={{ fontSize: 18 }}>{icon}</span>}
            </div>
            {loading ? (
                <div
                    style={{
                        height: 32,
                        background: 'rgba(255,255,255,0.06)',
                        borderRadius: 4,
                        animation: 'pulse 1.5s infinite',
                    }}
                />
            ) : (
                <>
                    <div
                        style={{
                            fontFamily: 'Space Mono, monospace',
                            fontSize: 28,
                            fontWeight: 700,
                            color: `var(--${color})`,
                            lineHeight: 1.1,
                        }}
                    >
                        {value}
                    </div>
                    {change && (
                        <div className="text-muted mt-1" style={{ fontSize: 12 }}>
                            {change}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default MetricCard
