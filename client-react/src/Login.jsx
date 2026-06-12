import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Login.css'

const API = 'http://localhost:8000/api'

export default function Login() {
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)
  const navigate = useNavigate()

  async function handleLogin() {
    if (!correo || !contrasena) { setError('Completa todos los campos'); return }
    setCargando(true)
    setError(null)
    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, contrasena }),
      })
      if (!res.ok) { setError('Correo o contraseña incorrectos'); return }
      const usuario = await res.json()
      localStorage.setItem('usuario', JSON.stringify(usuario))
      if (usuario.rol === 'empleado') navigate('/mesero')
      else if (usuario.rol === 'administrador') navigate('/admin')
    } catch {
      setError('No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-bg">
      <div className="login-card">
        <div className="login-icon">🍽</div>
        <h1>Restaurante</h1>
        <p className="login-sub">Inicia sesión para continuar</p>
        {error && <div className="login-error">{error}</div>}
        <div className="login-form">
          <div className="input-group">
            <label>Correo</label>
            <input type="email" placeholder="correo@restaurante.com" value={correo} onChange={e => setCorreo(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleLogin()} />
          </div>
          <div className="input-group">
            <label>Contraseña</label>
            <input type="password" placeholder="••••••••" value={contrasena} onChange={e => setContrasena(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleLogin()} />
          </div>
          <button className="btn-login" onClick={handleLogin} disabled={cargando}>
            {cargando ? 'Ingresando...' : 'Ingresar'}
          </button>
        </div>
      </div>
    </div>
  )
}
