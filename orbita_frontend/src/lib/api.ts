const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const h = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('orbita_token') || ''}`,
})

export const orbitaApi = {
    health: () => fetch(`${API}/health`).then((r) => r.json()),

    login: (email: string, password: string) =>
        fetch(`${API}/api/v1/auth/login`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ email, password }),
        }).then((r) => r.json()),

    chat: (leadId: string, mensaje: string, sessionId: string) =>
        fetch(`${API}/api/v1/leads/${leadId}/chat`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ mensaje, session_id: sessionId }),
        }).then((r) => r.json()),

    sendToTelegram: (chatId: string, mensaje: string, leadId: string) =>
        fetch(`${API}/api/v1/telegram/send-message`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ chat_id: chatId, mensaje, lead_id: leadId }),
        }).then((r) => r.json()),

    sendCampaign: (tipo: string, mensaje: string, filtros?: Record<string, string | undefined>) =>
        fetch(`${API}/api/v1/campanas/enviar`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ tipo, mensaje, filtros }),
        }).then((r) => r.json()),

    previewCampaign: (mensaje: string) =>
        fetch(`${API}/api/v1/campanas/preview`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ mensaje }),
        }).then((r) => r.json()),

    runAnalytics: (tipo = 'diario') =>
        fetch(`${API}/api/v1/agents/analitico/run`, {
            method: 'POST',
            headers: h(),
            body: JSON.stringify({ tipo_analisis: tipo }),
        }).then((r) => r.json()),

    getAgentStatus: () =>
        fetch(`${API}/api/v1/agents/status`, { headers: h() }).then((r) => r.json()),

    getDashboard: () =>
        fetch(`${API}/api/v1/analytics/dashboard`, { headers: h() }).then((r) => r.json()),

    getAlertas: () =>
        fetch(`${API}/api/v1/analytics/alertas`, { headers: h() }).then((r) => r.json()),

    getTelegramMetrics: () =>
        fetch(`${API}/api/v1/analytics/telegram`, { headers: h() }).then((r) => r.json()),

    getBotInfo: () =>
        fetch(`${API}/api/v1/telegram/info`, { headers: h() }).then((r) => r.json()),
    // Ahora retorna: { success: true, data: { bot_leads: {...}, bot_admin: {...} } }

    setupWebhooks: () =>
        fetch(`${API}/api/v1/telegram/setup-webhooks`, {
            method: 'POST',
            headers: h(),
        }).then((r) => r.json()),
    // Configura AMBOS bots en un solo click

    setupLeadsWebhook: () =>
        fetch(`${API}/api/v1/telegram/setup-leads-webhook`, {
            method: 'POST',
            headers: h(),
        }).then((r) => r.json()),

    setupAdminWebhook: () =>
        fetch(`${API}/api/v1/telegram/setup-admin-webhook`, {
            method: 'POST',
            headers: h(),
        }).then((r) => r.json()),
}
