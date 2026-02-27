import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const location = useLocation()
    const token = localStorage.getItem('orbita_token')

    if (!token) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return <>{children}</>
}

export default AuthGuard
