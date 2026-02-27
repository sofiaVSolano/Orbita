import React from 'react'

const LoadingDots: React.FC = () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <span
            style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: 'var(--green)',
                animation: 'pulse 1.2s ease-in-out infinite',
                animationDelay: '0s',
            }}
        />
        <span
            style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: 'var(--green)',
                animation: 'pulse 1.2s ease-in-out infinite',
                animationDelay: '0.2s',
            }}
        />
        <span
            style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: 'var(--green)',
                animation: 'pulse 1.2s ease-in-out infinite',
                animationDelay: '0.4s',
            }}
        />
    </div>
)

export default LoadingDots
