import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { orbitaApi } from '../lib/api'

const Login: React.FC = () => {
    const navigate = useNavigate()
    const [email, setEmail] = useState('admin@orbita.ai')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            const res = await orbitaApi.login(email, password)
            if (res?.access_token || res?.token) {
                localStorage.setItem('orbita_token', res.access_token || res.token)
                toast.success('✅ Acceso concedido. Bienvenido a ORBITA.')
                navigate('/dashboard')
            } else if (res?.success === false) {
                toast.error(res.message || 'Credenciales incorrectas')
            } else {
                // Backend not available — demo mode
                localStorage.setItem('orbita_token', 'demo-token-orbita-2026')
                toast.success('✅ Modo demo activo. Bienvenido a ORBITA.')
                navigate('/dashboard')
            }
        } catch {
            // Allow demo login if backend is down
            localStorage.setItem('orbita_token', 'demo-token-orbita-2026')
            toast.info('🔌 Backend no disponible. Modo demostración activo.')
            navigate('/dashboard')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div
            style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--bg-primary)',
                backgroundImage:
                    'linear-gradient(rgba(80,250,123,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(80,250,123,0.04) 1px, transparent 1px)',
                backgroundSize: '40px 40px',
                padding: '1rem',
            }}
        >
            <div
                className="fade-up"
                style={{
                    width: '100%',
                    maxWidth: 420,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '2rem',
                }}
            >
                {/* Logo */}
                <div style={{ textAlign: 'center' }}>
                    <div
                        style={{
                            position: 'relative',
                            width: 80,
                            height: 80,
                            margin: '0 auto 1rem',
                        }}
                    >
                        {/* Orbiting ring */}
                        <div
                            style={{
                                position: 'absolute',
                                inset: 0,
                                borderRadius: '50%',
                                border: '2px solid var(--green)',
                                opacity: 0.6,
                                animation: 'orbit 4s linear infinite',
                            }}
                        />
                        <div
                            style={{
                                position: 'absolute',
                                inset: 8,
                                borderRadius: '50%',
                                border: '1.5px solid var(--blue)',
                                opacity: 0.4,
                                animation: 'orbit 6s linear infinite reverse',
                            }}
                        />
                        <div
                            style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                width: 20,
                                height: 20,
                                background: 'var(--green)',
                                borderRadius: '50%',
                                transform: 'translate(-50%, -50%)',
                                boxShadow: '0 0 30px rgba(80,250,123,0.8), 0 0 60px rgba(80,250,123,0.3)',
                                animation: 'glow-pulse 2s ease-in-out infinite',
                            }}
                        />
                    </div>

                    <h1
                        style={{
                            fontFamily: 'Exo 2, sans-serif',
                            fontWeight: 900,
                            fontSize: 48,
                            letterSpacing: 6,
                            color: 'var(--text)',
                            textShadow: '0 0 40px rgba(80,250,123,0.3)',
                            marginBottom: '0.5rem',
                        }}
                    >
                        ORBITA
                    </h1>

                    <p
                        style={{
                            color: 'var(--text-muted)',
                            fontSize: 13,
                            lineHeight: 1.6,
                            textAlign: 'center',
                            maxWidth: 300,
                            margin: '0 auto',
                        }}
                    >
                        No se trata de tener más leads.
                        <br />
                        <em style={{ color: 'var(--green)' }}>
                            Se trata de no dejar escapar ninguno.
                        </em>
                    </p>
                </div>

                {/* Card */}
                <div
                    className="card"
                    style={{
                        width: '100%',
                        padding: '2rem',
                        boxShadow: 'var(--glow-green)',
                        borderColor: 'rgba(80,250,123,0.2)',
                    }}
                >
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div className="form-group" style={{ margin: 0 }}>
                            <label className="form-label">Email</label>
                            <input
                                type="email"
                                className="input"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="admin@orbita.ai"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div className="form-group" style={{ margin: 0 }}>
                            <label className="form-label">Contraseña</label>
                            <input
                                type="password"
                                className="input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                autoComplete="current-password"
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn--primary w-full"
                            style={{ padding: '12px', fontSize: 14, marginTop: 4 }}
                            disabled={loading}
                        >
                            {loading ? (
                                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span
                                        style={{
                                            width: 14,
                                            height: 14,
                                            border: '2px solid transparent',
                                            borderTopColor: 'var(--bg-primary)',
                                            borderRadius: '50%',
                                            animation: 'spin 0.7s linear infinite',
                                            display: 'inline-block',
                                        }}
                                    />
                                    Accediendo...
                                </span>
                            ) : (
                                'Entrar al Sistema'
                            )}
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <div style={{ textAlign: 'center' }}>
                    <span
                        className="badge badge--muted"
                        style={{ fontSize: 9 }}
                    >
                        AI FIRST HACKATHON 2026 · FUNNELCHAT
                    </span>
                </div>
            </div>
        </div>
    )
}

export default Login
