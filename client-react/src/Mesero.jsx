import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Mesero.css'

const API = 'http://localhost:8000/api'

const formatCOP = (n) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)

function PedidoCard({ pedido, onConfirmar }) {
  const [editando, setEditando] = useState(false)
  const [productos, setProductos] = useState(pedido.productos.map(p => ({ ...p })))
  const [guardando, setGuardando] = useState(false)
  const [confirmando, setConfirmando] = useState(false)

  function handleCantidad(idx, valor) {
    setProductos(prev => prev.map((p, i) => i === idx ? { ...p, cantidad: Math.max(1, Number(valor)) } : p))
  }

  function handleObservacion(idx, valor) {
    setProductos(prev => prev.map((p, i) => i === idx ? { ...p, observaciones: valor } : p))
  }

  async function handleGuardar() {
    setGuardando(true)
    try {
      await fetch(`${API}/pedidos/${pedido.id}/editar`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ detalles: productos.map(p => ({ id: p.id, cantidad: p.cantidad, observaciones: p.observaciones || null })) }),
      })
      setEditando(false)
    } catch {
      alert('Error al guardar cambios')
    } finally {
      setGuardando(false)
    }
  }

  async function handleConfirmar() {
    setConfirmando(true)
    try {
      await fetch(`${API}/pedidos/${pedido.id}/confirmar`, { method: 'PUT' })
      onConfirmar(pedido.id)
    } catch {
      alert('Error al confirmar pedido')
      setConfirmando(false)
    }
  }

  const total = productos.reduce((s, p) => s + (p.precio || 0) * p.cantidad, 0)

  return (
    <div className="pedido-card">
      <div className="pedido-header">
        <div className="pedido-title">
          <span className="pedido-mesa">Mesa {pedido.n_mesa}</span>
          <span className="pedido-id">Pedido #{pedido.id}</span>
        </div>
        <span className="pedido-estado">Pendiente</span>
      </div>
      <ul className="pedido-items">
        {productos.map((p, idx) => (
          <li key={p.id} className="pedido-item">
            <div className="item-info">
              <span className="item-nombre">{p.nombre}</span>
              {editando ? (
                <div className="item-edit">
                  <div className="cantidad-ctrl">
                    <button onClick={() => handleCantidad(idx, p.cantidad - 1)}>−</button>
                    <span>{p.cantidad}</span>
                    <button onClick={() => handleCantidad(idx, p.cantidad + 1)}>+</button>
                  </div>
                  <textarea className="obs-input" placeholder="Observaciones..." value={p.observaciones || ''} onChange={e => handleObservacion(idx, e.target.value)} rows={2} />
                </div>
              ) : (
                <div className="item-readonly">
                  <span className="item-cant">{p.cantidad}×</span>
                  {p.observaciones && <span className="item-obs">📝 {p.observaciones}</span>}
                </div>
              )}
            </div>
            <span className="item-precio">{formatCOP((p.precio || 0) * p.cantidad)}</span>
          </li>
        ))}
      </ul>
      <div className="pedido-footer">
        <span className="pedido-total">Total: <strong>{formatCOP(total)}</strong></span>
        <div className="pedido-acciones">
          {editando ? (
            <>
              <button className="btn-cancelar" onClick={() => setEditando(false)}>Cancelar</button>
              <button className="btn-guardar" onClick={handleGuardar} disabled={guardando}>{guardando ? 'Guardando...' : 'Guardar'}</button>
            </>
          ) : (
            <>
              <button className="btn-editar" onClick={() => setEditando(true)}>Editar</button>
              <button className="btn-confirmar-mesero" onClick={handleConfirmar} disabled={confirmando}>{confirmando ? 'Enviando...' : 'Confirmar → Cocina'}</button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Mesero() {
  const [pedidos, setPedidos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')

  useEffect(() => {
    if (!usuario) { navigate('/login'); return }
    cargarPedidos()
    const intervalo = setInterval(cargarPedidos, 10000)
    return () => clearInterval(intervalo)
  }, [])

  async function cargarPedidos() {
    try {
      const res = await fetch(`${API}/pedidos-pendientes`)
      setPedidos(await res.json())
    } catch {
      setError('No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem('usuario')
    navigate('/login')
  }

  return (
    <div className="mesero-layout">
      <header className="mesero-header">
        <div className="header-brand"><span>🍽</span><span>Panel del mesero</span></div>
        <div className="header-right">
          <span className="header-usuario">{usuario?.nombre}</span>
          <button className="btn-logout" onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </header>
      <main className="mesero-main">
        <div className="mesero-titulo">
          <h2>Pedidos pendientes</h2>
          <button className="btn-recargar" onClick={cargarPedidos}>↻ Actualizar</button>
        </div>
        {error && <div className="error-banner">{error}</div>}
        {cargando ? <p className="cargando">Cargando pedidos...</p> : pedidos.length === 0 ? (
          <div className="sin-pedidos"><span>✓</span><p>No hay pedidos pendientes</p></div>
        ) : (
          <div className="pedidos-grid">
            {pedidos.map(p => <PedidoCard key={p.id} pedido={p} onConfirmar={(id) => setPedidos(prev => prev.filter(p => p.id !== id))} />)}
          </div>
        )}
      </main>
    </div>
  )
}
