import React from 'react'

interface TelegramBubbleProps {
    role: 'user' | 'agent' | 'admin'
    content: string
    agente?: string
    isVoice?: boolean
    transcription?: string
    timestamp?: string
}

const TelegramBubble: React.FC<TelegramBubbleProps> = ({
    role,
    content,
    agente,
    isVoice = false,
    transcription,
    timestamp,
}) => {
    const isUser = role === 'user'
    const isAdmin = role === 'admin'

    const bubbleStyle: React.CSSProperties = {
        maxWidth: '75%',
        padding: '10px 14px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser
            ? 'rgba(255, 255, 255, 0.07)'
            : isAdmin
                ? 'rgba(255, 77, 148, 0.12)'
                : 'rgba(80, 250, 123, 0.1)',
        border: isUser
            ? '1px solid rgba(255,255,255,0.1)'
            : isAdmin
                ? '1px solid rgba(255, 77, 148, 0.25)'
                : '1px solid rgba(80, 250, 123, 0.2)',
        alignSelf: isUser ? 'flex-start' : 'flex-end',
    }

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-start' : 'flex-end',
                marginBottom: 12,
            }}
        >
            {!isUser && agente && (
                <span
                    className="badge badge--green"
                    style={{ marginBottom: 4, fontSize: 9 }}
                >
                    {isAdmin ? '👨‍💼 admin' : `🤖 ${agente}`}
                </span>
            )}
            <div style={bubbleStyle}>
                {isVoice && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                        <span>🎙️</span>
                        <span className="badge badge--purple" style={{ fontSize: 9 }}>
                            VOZ TRANSCRITA
                        </span>
                    </div>
                )}
                {isVoice && transcription ? (
                    <p
                        style={{
                            color: 'var(--text-muted)',
                            fontStyle: 'italic',
                            fontSize: 13,
                            lineHeight: 1.5,
                        }}
                    >
                        {transcription}
                    </p>
                ) : (
                    <p style={{ color: 'var(--text)', fontSize: 13, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                        {content}
                    </p>
                )}
            </div>
            {timestamp && (
                <span
                    className="text-muted"
                    style={{ fontSize: 10, marginTop: 3, fontFamily: 'Space Mono' }}
                >
                    {timestamp}
                </span>
            )}
        </div>
    )
}

export default TelegramBubble
