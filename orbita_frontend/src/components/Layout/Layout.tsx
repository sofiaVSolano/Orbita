import React, { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { orbitaApi } from '../../lib/api'

const Layout: React.FC = () => {
    const [backendOk, setBackendOk] = useState<boolean | null>(null)

    useEffect(() => {
        orbitaApi.health()
            .then(() => setBackendOk(true))
            .catch(() => setBackendOk(false))
    }, [])

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            <Sidebar />
            <main className="page-content">
                {backendOk === false && (
                    <div
                        style={{
                            background: 'rgba(255, 160, 50, 0.12)',
                            border: '1px solid rgba(255, 160, 50, 0.3)',
                            borderRadius: 0,
                            padding: '8px 2rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            position: 'sticky',
                            top: 0,
                            zIndex: 100,
                        }}
                    >
                        <span>⚠️</span>
                        <span style={{ fontSize: 13, color: '#FFA032' }}>
                            Backend desconectado — Solo lectura (conecta el servidor en{' '}
                            <code style={{ fontFamily: 'Space Mono', fontSize: 11 }}>localhost:8000</code>)
                        </span>
                    </div>
                )}
                <div className="page-inner">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}

export default Layout
