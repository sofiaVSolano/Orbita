import React from 'react'

type Fuente = 'telegram' | 'manual' | 'formulario' | 'referido'

const FuenteBadge: React.FC<{ fuente: Fuente }> = ({ fuente }) => {
    const config: Record<Fuente, { emoji: string; label: string; cls: string }> = {
        telegram: { emoji: '📱', label: 'Telegram', cls: 'badge--blue' },
        manual: { emoji: '✏️', label: 'Manual', cls: 'badge--muted' },
        formulario: { emoji: '📋', label: 'Formulario', cls: 'badge--purple' },
        referido: { emoji: '🤝', label: 'Referido', cls: 'badge--green' },
    }
    const c = config[fuente] || config.manual
    return (
        <span className={`badge ${c.cls}`}>
            {c.emoji} {c.label}
        </span>
    )
}

export default FuenteBadge
