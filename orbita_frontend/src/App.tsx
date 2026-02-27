import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'

// Layout
import Layout from './components/Layout/Layout'
import AuthGuard from './components/AuthGuard'

// Pages
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Conversaciones from './pages/Conversaciones'
import Telegram from './pages/Telegram'
import Cotizaciones from './pages/Cotizaciones'
import Reuniones from './pages/Reuniones'
import Campanas from './pages/Campanas'
import Agentes from './pages/Agentes'
import Analitica from './pages/Analitica'
import Configuracion from './pages/Configuracion'

// ── QueryClient ──────────────────────────────────────────────
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
})

// ── App ───────────────────────────────────────────────────────
const App: React.FC = () => {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                {/* Sonner toast container */}
                <Toaster
                    position="bottom-right"
                    theme="dark"
                    toastOptions={{
                        style: {
                            background: 'var(--bg-card)',
                            border: '1px solid var(--border)',
                            color: 'var(--text)',
                            fontFamily: "'Exo 2', sans-serif",
                            fontSize: 13,
                        },
                    }}
                />

                <Routes>
                    {/* Public */}
                    <Route path="/login" element={<Login />} />

                    {/* Protected — wrapped in AuthGuard > Layout */}
                    <Route
                        element={
                            <AuthGuard>
                                <Layout />
                            </AuthGuard>
                        }
                    >
                        {/* Redirect root → dashboard */}
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />

                        {/* Main pages */}
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/leads" element={<Leads />} />
                        <Route path="/conversaciones" element={<Conversaciones />} />
                        <Route path="/telegram" element={<Telegram />} />
                        <Route path="/cotizaciones" element={<Cotizaciones />} />
                        <Route path="/reuniones" element={<Reuniones />} />
                        <Route path="/campanas" element={<Campanas />} />
                        <Route path="/agentes" element={<Agentes />} />
                        <Route path="/analitica" element={<Analitica />} />
                        <Route path="/configuracion" element={<Configuracion />} />
                    </Route>

                    {/* Catch-all */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </BrowserRouter>
        </QueryClientProvider>
    )
}

export default App
