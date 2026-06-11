import { useState, useEffect } from 'react'
import './Cocina.css'

const API = 'http://localhost:8000/api'

function PedidoCocinaCard({ pedido, onDespachar }) {
  const [despachando, setDespachando] = useState(false)

  async function handleDespachar() {
    setDespachando(true)
    try {
      await fetch(`${API}/pedidos/${pedido.id}/despachar`, { method: 'PUT' })
      onDespachar(pedido.id)
    } catch {
      alert('Error al despachar pedido')
      setDespachando(false)
    }
  }

  return (
    <div className="cocina-card">
      <div className="cocina-card-header">
        <div>
          <span className="cocina-mesa">Mesa {pedido.n_mesa}</span>
          <span className="cocina-pedido-id">Pedido #{pedido.id}</span>
        </div>
        <span className="cocina-badge">En cocina</span>
      </div>
      <ul className="cocina-items">
        {pedido.productos.map((p, idx) => (
          <li key={idx} className="cocina-item">
            <div className="cocina-item-top">
              <span className="cocina-cantidad">{p.cantidad}×</span>
              <span className="cocina-nombre">{p.nombre}</span>
            </div>
            {p.observaciones && (
              <div className="cocina-obs"><span className="obs-icon">⚠</span>{p.observaciones}</div>
            )}
          </li>
        ))}
      </ul>
      <button className="btn-despachar" onClick={handleDespachar} disabled={despachando}>
        {despachando ? 'Despachando...' : '✓ Despachar'}
      </button>
    </div>
  )
}

export default function Cocina() {
  const [pedidos, setPedidos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    cargarPedidos()
    const intervalo = setInterval(cargarPedidos, 8000)
    return () => clearInterval(intervalo)
  }, [])

  async function cargarPedidos() {
    try {
      const res = await fetch(`${API}/pedidos-cocina`)
      setPedidos(await res.json())
      setError(null)
    } catch {
      setError('No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="cocina-layout">
      <header className="cocina-header">
        <div className="cocina-header-brand"><span>👨‍🍳</span><span>Cocina</span></div>
        <div className="cocina-header-right">
          <span className="cocina-count">{pedidos.length} {pedidos.length === 1 ? 'pedido' : 'pedidos'} pendientes</span>
          <button className="btn-recargar-cocina" onClick={cargarPedidos}>↻</button>
        </div>
      </header>
      <main className="cocina-main">
        {error && <div className="cocina-error">{error}</div>}
        {cargando ? <p className="cocina-cargando">Cargando pedidos...</p> : pedidos.length === 0 ? (
          <div className="cocina-vacia"><span>✓</span><p>No hay pedidos en cocina</p></div>
        ) : (
          <div className="cocina-grid">
            {pedidos.map(p => <PedidoCocinaCard key={p.id} pedido={p} onDespachar={(id) => setPedidos(prev => prev.filter(p => p.id !== id))} />)}
          </div>
        )}
      </main>
    </div>
  )
}
