import React, { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { supabase } from '../lib/supabase'
import { orbitaApi } from '../lib/api'
import TelegramBubble from '../components/TelegramBubble'
import LoadingDots from '../components/LoadingDots'
import FuenteBadge from '../components/FuenteBadge'

interface ConvLead {
    id: string
    nombre: string
    empresa_nombre?: string
    fuente: string
    telegram_chat_id?: string
    last_message?: string
    last_message_at?: string
    last_agent?: string
    has_voice?: boolean
}

interface Msg {
    id: string
    role: string
    content: string
    content_type: string
    transcripcion_voz?: string
    agente?: string
    created_at: string
}

const Conversaciones: React.FC = () => {
    const [searchParams] = useSearchParams()
    const [leads, setLeads] = useState<ConvLead[]>([])
    const [selectedLead, setSelectedLead] = useState<ConvLead | null>(null)
    const [messages, setMessages] = useState<Msg[]>([])
    const [chatMsg, setChatMsg] = useState('')
    const [sending, setSending] = useState(false)
    const [sendMode, setSendMode] = useState<'orbita' | 'telegram'>('orbita')
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const [sessionId] = useState(() => crypto.randomUUID())

    // Load leads that have conversations
    useEffect(() => {
        const fetch = async () => {
            // Get distinct lead_ids from conversations
            const { data: convData } = await supabase
                .from('conversations')
                .select('lead_id, content, content_type, agente, created_at')
                .order('created_at', { ascending: false })

            if (!convData) return

            const leadIds = [...new Set(convData.map((c: Record<string, unknown>) => c.lead_id))]
                .filter(Boolean)
                .slice(0, 30)

            if (leadIds.length === 0) return

            const { data: leadsData } = await supabase
                .from('leads')
                .select('id,nombre,empresa_nombre,fuente,telegram_chat_id')
                .in('id', leadIds)

            // Build leads with last message info
            const enriched: ConvLead[] = (leadsData || []).map((l) => {
                const lConvs = convData.filter((c) => c.lead_id === l.id)
                const last = lConvs[0]
                return {
                    ...(l as unknown as ConvLead),
                    last_message: (last?.content as string)?.slice(0, 60),
                    last_message_at: last?.created_at as string,
                    last_agent: last?.agente as string,
                    has_voice: lConvs.some((c) => c.content_type === 'voice'),
                }
            })

            setLeads(enriched)

            // Auto-select from URL param
            const leadParam = searchParams.get('lead')
            if (leadParam) {
                const found = enriched.find((l) => l.id === leadParam)
                if (found) selectLead(found)
            }
        }
        fetch()
    }, [])

    const selectLead = async (lead: ConvLead) => {
        setSelectedLead(lead)
        const { data } = await supabase
            .from('conversations')
            .select('*')
            .eq('lead_id', lead.id)
            .order('created_at')
            .limit(100)
        setMessages(data || [])
    }

    // Realtime messages
    useEffect(() => {
        if (!selectedLead) return
        const ch = supabase
            .channel(`convs-${selectedLead.id}`)
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'conversations', filter: `lead_id=eq.${selectedLead.id}` },
                (p) => setMessages((prev) => [...prev, p.new as Msg])
            )
            .subscribe()
        return () => { supabase.removeChannel(ch) }
    }, [selectedLead?.id])

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async () => {
        if (!chatMsg.trim() || !selectedLead) return
        setSending(true)
        try {
            if (sendMode === 'telegram' && selectedLead.telegram_chat_id) {
                await orbitaApi.sendToTelegram(selectedLead.telegram_chat_id, chatMsg, selectedLead.id)
                toast.success('📱 Mensaje enviado por Telegram', { style: { background: 'rgba(0,209,255,0.1)' } })
            } else {
                const res = await orbitaApi.chat(selectedLead.id, chatMsg, sessionId)
                if (res?.data?.respuesta_final) {
                    toast.success('💬 Respuesta generada')
                }
            }
            setChatMsg('')
            // Reload conversations
            const { data } = await supabase
                .from('conversations').select('*').eq('lead_id', selectedLead.id)
                .order('created_at').limit(100)
            setMessages(data || [])
        } catch {
            toast.error('Error al enviar')
        } finally {
            setSending(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <h1>💬 Conversaciones</h1>
                <p className="text-muted">Historial completo de chats con leads</p>
            </div>

            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: '300px 1fr',
                    gap: '1rem',
                    height: 'calc(100vh - 180px)',
                }}
            >
                {/* Lead List */}
                <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ padding: '0.875rem 1rem', borderBottom: '1px solid var(--border)' }}>
                        <span className="font-mono text-muted" style={{ fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>
                            {leads.length} conversaciones
                        </span>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {leads.map((lead) => (
                            <div
                                key={lead.id}
                                onClick={() => selectLead(lead)}
                                style={{
                                    padding: '0.875rem 1rem',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                                    background: selectedLead?.id === lead.id ? 'rgba(80,250,123,0.06)' : 'transparent',
                                    borderLeft: selectedLead?.id === lead.id ? '2px solid var(--green)' : '2px solid transparent',
                                    transition: 'all 0.15s',
                                }}
                            >
                                <div className="flex items-center justify-between mb-1">
                                    <span style={{ fontWeight: 600, fontSize: 13 }}>{lead.nombre}</span>
                                    <div className="flex items-center gap-1">
                                        {lead.has_voice && <span title="Tiene mensajes de voz">🎙️</span>}
                                        <FuenteBadge fuente={lead.fuente as 'telegram' | 'manual' | 'formulario' | 'referido'} />
                                    </div>
                                </div>
                                <div className="text-muted truncate" style={{ fontSize: 11 }}>
                                    {lead.last_message || 'Sin mensajes'}
                                </div>
                                <div className="flex items-center justify-between mt-1">
                                    {lead.last_agent && (
                                        <span className="badge badge--purple" style={{ fontSize: 8 }}>
                                            🤖 {lead.last_agent}
                                        </span>
                                    )}
                                    {lead.last_message_at && (
                                        <span className="text-muted" style={{ fontSize: 10 }}>
                                            {formatDistanceToNow(new Date(lead.last_message_at), { addSuffix: true, locale: es })}
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Chat Window */}
                {selectedLead ? (
                    <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        {/* Chat Header */}
                        <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
                            <div className="flex items-center justify-between">
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: 15 }}>{selectedLead.nombre}</div>
                                    <div className="text-muted" style={{ fontSize: 11 }}>
                                        {selectedLead.empresa_nombre || 'Sin empresa'}
                                        {selectedLead.telegram_chat_id && ` · Telegram: ${selectedLead.telegram_chat_id}`}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <FuenteBadge fuente={selectedLead.fuente as 'telegram' | 'manual' | 'formulario' | 'referido'} />
                                </div>
                            </div>
                        </div>

                        {/* Messages */}
                        <div
                            style={{
                                flex: 1,
                                overflowY: 'auto',
                                padding: '1rem 1.25rem',
                                display: 'flex',
                                flexDirection: 'column',
                            }}
                        >
                            {messages.length === 0 ? (
                                <div className="text-muted" style={{ textAlign: 'center', padding: '3rem', fontSize: 13 }}>
                                    Sin mensajes aún en esta conversación
                                </div>
                            ) : (
                                messages.map((msg) => (
                                    <TelegramBubble
                                        key={msg.id}
                                        role={msg.role === 'user' ? 'user' : 'agent'}
                                        content={msg.content}
                                        agente={msg.agente}
                                        isVoice={msg.content_type === 'voice'}
                                        transcription={msg.transcripcion_voz}
                                        timestamp={formatDistanceToNow(new Date(msg.created_at), { addSuffix: true, locale: es })}
                                    />
                                ))
                            )}
                            {sending && (
                                <div className="flex items-center gap-2 mt-2">
                                    <span className="text-muted" style={{ fontSize: 12 }}>⚡ Agente procesando...</span>
                                    <LoadingDots />
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div style={{ padding: '0.875rem 1.25rem', borderTop: '1px solid var(--border)', flexShrink: 0 }}>
                            {/* Mode toggle */}
                            <div className="flex items-center gap-3 mb-2">
                                <button
                                    className={`btn btn--sm ${sendMode === 'orbita' ? 'btn--primary' : 'btn--secondary'}`}
                                    onClick={() => setSendMode('orbita')}
                                >
                                    🤖 Enviar como Agente ORBITA
                                </button>
                                {selectedLead.telegram_chat_id && (
                                    <button
                                        className={`btn btn--sm ${sendMode === 'telegram' ? 'btn--blue' : 'btn--secondary'}`}
                                        onClick={() => setSendMode('telegram')}
                                    >
                                        📱 Intervención manual admin
                                    </button>
                                )}
                            </div>
                            <div className="flex gap-2">
                                <input
                                    className="input"
                                    value={chatMsg}
                                    onChange={(e) => setChatMsg(e.target.value)}
                                    placeholder={sendMode === 'telegram' ? 'Escribir mensaje para enviar por Telegram...' : 'Escribir mensaje para el agente ORBITA...'}
                                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                                    disabled={sending}
                                />
                                <button
                                    className={`btn ${sendMode === 'telegram' ? 'btn--blue' : 'btn--primary'}`}
                                    onClick={handleSend}
                                    disabled={sending || !chatMsg.trim()}
                                >
                                    {sendMode === 'telegram' ? '📱 Telegram' : 'Enviar'}
                                </button>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            <div style={{ fontSize: 40, marginBottom: 12 }}>💬</div>
                            <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Selecciona una conversación</div>
                            <div style={{ fontSize: 13 }}>Elige un lead de la lista para ver su historial completo</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Conversaciones
