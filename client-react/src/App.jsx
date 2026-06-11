import { useState, useEffect } from 'react'
import './App.css'

const API = 'http://localhost:8000/api'

const formatCOP = (n) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)

function ProductoCard({ producto, onAgregar }) {
  const [expandido, setExpandido] = useState(false)
  const [observacion, setObservacion] = useState('')
  const [cantidad, setCantidad] = useState(1)

  function handleAgregar() {
    onAgregar({ ...producto, cantidad, observaciones: observacion.trim() || null })
    setExpandido(false)
    setObservacion('')
    setCantidad(1)
  }

  return (
    <div className={`producto-card ${expandido ? 'expandido' : ''}`}>
      <div className="producto-header" onClick={() => setExpandido(!expandido)}>
        <div className="producto-info">
          <span className="producto-nombre">{producto.nombre}</span>
          {producto.descripcion && <span className="producto-desc">{producto.descripcion}</span>}
        </div>
        <div className="producto-precio-col">
          <span className="producto-precio">{formatCOP(producto.precio)}</span>
          <span className="ver-mas">{expandido ? '▲' : '▼'}</span>
        </div>
      </div>
      {expandido && (
        <div className="producto-detalle">
          <div className="cantidad-row">
            <label>Cantidad</label>
            <div className="cantidad-ctrl">
              <button onClick={() => setCantidad(c => Math.max(1, c - 1))}>−</button>
              <span>{cantidad}</span>
              <button onClick={() => setCantidad(c => c + 1)}>+</button>
            </div>
          </div>
          <div className="obs-row">
            <label htmlFor={`obs-${producto.id}`}>
              Observaciones <span className="opcional">(opcional)</span>
            </label>
            <textarea
              id={`obs-${producto.id}`}
              placeholder="Ej: sin sal, sin cebolla, término 3/4..."
              value={observacion}
              onChange={e => setObservacion(e.target.value)}
              rows={2}
            />
          </div>
          <button className="btn-agregar" onClick={handleAgregar}>
            Agregar al pedido — {formatCOP(producto.precio * cantidad)}
          </button>
        </div>
      )}
    </div>
  )
}

function Carrito({ items, onEliminar, onConfirmar, enviando }) {
  const total = items.reduce((s, i) => s + i.precio * i.cantidad, 0)
  if (items.length === 0) {
    return (
      <aside className="carrito vacio">
        <h2>Tu pedido</h2>
        <p className="carrito-vacio-msg">Aún no has seleccionado ningún plato.</p>
      </aside>
    )
  }
  return (
    <aside className="carrito">
      <h2>Tu pedido</h2>
      <ul className="carrito-lista">
        {items.map((item, idx) => (
          <li key={idx} className="carrito-item">
            <div className="carrito-item-info">
              <span className="carrito-nombre">{item.cantidad}× {item.nombre}</span>
              {item.observaciones && <span className="carrito-obs">📝 {item.observaciones}</span>}
            </div>
            <div className="carrito-item-right">
              <span className="carrito-subtotal">{formatCOP(item.precio * item.cantidad)}</span>
              <button className="btn-eliminar" onClick={() => onEliminar(idx)}>✕</button>
            </div>
          </li>
        ))}
      </ul>
      <div className="carrito-total">
        <span>Total</span>
        <strong>{formatCOP(total)}</strong>
      </div>
      <button className="btn-confirmar" onClick={onConfirmar} disabled={enviando}>
        {enviando ? 'Enviando...' : 'Confirmar pedido →'}
      </button>
      <p className="carrito-nota">Un mesero revisará tu pedido antes de enviarlo a cocina.</p>
    </aside>
  )
}

function PedidoExitoso({ pedidoId, onNuevoPedido }) {
  return (
    <div className="exito-screen">
      <div className="exito-icono">✓</div>
      <h1>¡Pedido enviado!</h1>
      <p>Tu pedido <strong>#{pedidoId}</strong> fue recibido y está siendo revisado por el mesero.</p>
      <p className="exito-sub">En breve llegará a cocina.</p>
      <button className="btn-confirmar" onClick={onNuevoPedido}>Hacer otro pedido</button>
    </div>
  )
}

export default function App() {
  const params = new URLSearchParams(window.location.search)
  const ID_MESA = parseInt(params.get('mesa')) || 1

  const [menu, setMenu] = useState([])
  const [categoriaActiva, setCategoriaActiva] = useState(null)
  const [carrito, setCarrito] = useState([])
  const [enviando, setEnviando] = useState(false)
  const [pedidoExitoso, setPedidoExitoso] = useState(null)
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    fetch(`${API}/menu`)
      .then(r => r.json())
      .then(data => {
        setMenu(data)
        if (data.length > 0) setCategoriaActiva(data[0].id)
      })
      .catch(() => setError('No se pudo conectar con el servidor. Verifica que el backend esté activo.'))
      .finally(() => setCargando(false))
  }, [])

  const categoriaSeleccionada = menu.find(c => c.id === categoriaActiva)
  const productosFiltrados = categoriaSeleccionada?.productos || []

  function agregarAlCarrito(producto) {
    setCarrito(prev => [...prev, producto])
  }

  function eliminarDelCarrito(idx) {
    setCarrito(prev => prev.filter((_, i) => i !== idx))
  }

  async function confirmarPedido() {
    if (carrito.length === 0) return
    setEnviando(true)
    setError(null)
    try {
      const body = {
        id_mesa: ID_MESA,
        productos: carrito.map(item => ({
          id_producto: item.id,
          cantidad: item.cantidad,
          observaciones: item.observaciones || '',
        })),
      }
      const res = await fetch(`${API}/pedidos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error()
      const data = await res.json()
      setPedidoExitoso(data.id_pedido)
      setCarrito([])
    } catch {
      setError('No se pudo enviar el pedido. Intenta de nuevo.')
    } finally {
      setEnviando(false)
    }
  }

  if (pedidoExitoso) {
    return <PedidoExitoso pedidoId={pedidoExitoso} onNuevoPedido={() => setPedidoExitoso(null)} />
  }

  return (
    <div className="layout">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-icon">🍽</span>
          <span className="header-title">Menú</span>
        </div>
        <span className="header-mesa">Mesa {ID_MESA}</span>
      </header>
      <div className="contenido">
        <main className="menu-panel">
          {error && <div className="error-banner">{error}</div>}
          {cargando ? (
            <div className="cargando">Cargando menú...</div>
          ) : (
            <>
              <nav className="categorias-nav">
                {menu.map(cat => (
                  <button
                    key={cat.id}
                    className={`cat-btn ${categoriaActiva === cat.id ? 'activa' : ''}`}
                    onClick={() => setCategoriaActiva(cat.id)}
                  >
                    {cat.nombre}
                  </button>
                ))}
              </nav>
              <section className="productos-lista">
                {productosFiltrados.length === 0 ? (
                  <p className="sin-productos">No hay productos en esta categoría.</p>
                ) : (
                  productosFiltrados.map(p => (
                    <ProductoCard key={p.id} producto={p} onAgregar={agregarAlCarrito} />
                  ))
                )}
              </section>
            </>
          )}
        </main>
        <Carrito items={carrito} onEliminar={eliminarDelCarrito} onConfirmar={confirmarPedido} enviando={enviando} />
      </div>
    </div>
  )
}
