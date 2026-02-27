import React from 'react'

const VoiceTranscriptBadge: React.FC<{ transcription: string }> = ({ transcription }) => (
    <div
        style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 6,
            padding: '6px 10px',
            background: 'rgba(189, 147, 249, 0.08)',
            border: '1px solid rgba(189,147,249,0.2)',
            borderRadius: 4,
        }}
    >
        <span style={{ fontSize: 14, flexShrink: 0 }}>🎙️</span>
        <p
            style={{
                color: 'var(--text-muted)',
                fontStyle: 'italic',
                fontSize: 12,
                lineHeight: 1.5,
                margin: 0,
            }}
        >
            {transcription}
        </p>
    </div>
)

export default VoiceTranscriptBadge
