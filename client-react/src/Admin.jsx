import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Admin.css'

const API = 'http://localhost:8000/api'

const formatCOP = (n) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)

function TabFacturas() {
  const [pedidos, setPedidos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [facturando, setFacturando] = useState(null)
  const [facturaVista, setFacturaVista] = useState(null)

  useEffect(() => { cargarPedidos() }, [])

  async function cargarPedidos() {
    setCargando(true)
    try {
      const res = await fetch(`${API}/pedidos-despachados`)
      setPedidos(await res.json())
    } finally {
      setCargando(false)
    }
  }

  async function handleFacturar(idPedido) {
    setFacturando(idPedido)
    try {
      const res = await fetch(`${API}/facturas/${idPedido}`, { method: 'POST' })
      const data = await res.json()
      // Traer detalle completo de la factura
      const detalle = await fetch(`${API}/facturas/${data.id_factura}`)
      setFacturaVista(await detalle.json())
      cargarPedidos()
    } catch {
      alert('Error al generar factura')
    } finally {
      setFacturando(null)
    }
  }

  if (facturaVista) {
    return (
      <div className="factura-vista">
        <div className="factura-header">
          <h3>Factura #{facturaVista.id_factura}</h3>
          <span className="factura-fecha">{new Date(facturaVista.fecha).toLocaleString('es-CO')}</span>
        </div>
        <p className="factura-pedido">Pedido #{facturaVista.id_pedido}</p>

        <ul className="factura-items" style={{marginBottom: '16px'}}>
          {facturaVista.productos?.map((p, idx) => (
            <li key={idx} className="factura-item">
              <span>{p.cantidad}× {p.nombre}</span>
              <span>{formatCOP(p.subtotal)}</span>
            </li>
          ))}
        </ul>

        <div className="factura-total-box">
          <span>Total</span>
          <strong>{formatCOP(facturaVista.total)}</strong>
        </div>
        <button className="btn-volver" onClick={() => setFacturaVista(null)}>← Volver a pedidos</button>
      </div>
    )
  }

  return (
    <div>
      <div className="tab-titulo">
        <h3>Pedidos listos para facturar</h3>
        <button className="btn-recargar-admin" onClick={cargarPedidos}>↻ Actualizar</button>
      </div>
      {cargando ? <p className="admin-cargando">Cargando...</p> : pedidos.length === 0 ? (
        <div className="admin-vacio"><span>✓</span><p>No hay pedidos despachados pendientes de factura</p></div>
      ) : (
        <div className="facturas-lista">
          {pedidos.map(p => (
            <div key={p.id} className="factura-card">
              <div className="factura-card-header">
                <span className="factura-mesa">Mesa {p.n_mesa}</span>
                <span className="factura-id">Pedido #{p.id}</span>
              </div>
              <ul className="factura-items">
                {p.productos.map((prod, idx) => (
                  <li key={idx} className="factura-item">
                    <span>{prod.cantidad}× {prod.nombre}</span>
                    <span>{formatCOP(prod.subtotal)}</span>
                  </li>
                ))}
              </ul>
              <div className="factura-footer">
                <span className="factura-total">Total: <strong>{formatCOP(p.total)}</strong></span>
                <button
                  className="btn-facturar"
                  onClick={() => handleFacturar(p.id)}
                  disabled={facturando === p.id}
                >
                  {facturando === p.id ? 'Generando...' : '🧾 Generar factura'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TabEstadisticas() {
  const [diarias, setDiarias] = useState(null)
  const [productos, setProductos] = useState([])
  const [mes, setMes] = useState(new Date().getMonth() + 1)
  const [anio, setAnio] = useState(new Date().getFullYear())
  const [mensual, setMensual] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => { cargarDiarias(); cargarProductos() }, [])

  async function cargarDiarias() {
    const res = await fetch(`${API}/estadisticas/ventas-diarias`)
    setDiarias(await res.json())
    setCargando(false)
  }

  async function cargarProductos() {
    const res = await fetch(`${API}/estadisticas/ventas-producto`)
    setProductos(await res.json())
  }

  async function cargarMensual() {
    const res = await fetch(`${API}/estadisticas/ganancias-mes?mes=${mes}&anio=${anio}`)
    setMensual(await res.json())
  }

  const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

  return (
    <div className="estadisticas">
      {/* Ventas del día */}
      <div className="stat-card">
        <h3>Ventas de hoy</h3>
        {cargando ? <p>Cargando...</p> : diarias && (
          <div className="stat-valores">
            <div className="stat-valor">
              <span className="stat-num">{diarias.cantidad_ventas}</span>
              <span className="stat-label">facturas emitidas</span>
            </div>
            <div className="stat-valor destacado">
              <span className="stat-num">{formatCOP(diarias.total_recaudado)}</span>
              <span className="stat-label">total recaudado</span>
            </div>
          </div>
        )}
      </div>

      {/* Ganancias por mes */}
      <div className="stat-card">
        <h3>Ganancias por mes</h3>
        <div className="mes-selector">
          <select value={mes} onChange={e => setMes(Number(e.target.value))}>
            {meses.map((m, i) => <option key={i+1} value={i+1}>{m}</option>)}
          </select>
          <input type="number" value={anio} onChange={e => setAnio(Number(e.target.value))} min="2020" max="2099" />
          <button className="btn-consultar" onClick={cargarMensual}>Consultar</button>
        </div>
        {mensual && (
          <div className="stat-valores">
            <div className="stat-valor">
              <span className="stat-num">{mensual.cantidad_ventas}</span>
              <span className="stat-label">ventas en el mes</span>
            </div>
            <div className="stat-valor destacado">
              <span className="stat-num">{formatCOP(mensual.total_ganancias)}</span>
              <span className="stat-label">total ganancias</span>
            </div>
          </div>
        )}
      </div>

      {/* Ventas por producto */}
      <div className="stat-card full">
        <h3>Productos más vendidos</h3>
        {productos.length === 0 ? <p className="admin-cargando">Cargando...</p> : (
          <table className="productos-tabla">
            <thead>
              <tr><th>Producto</th><th>Cantidad vendida</th><th>Ingresos generados</th></tr>
            </thead>
            <tbody>
              {productos.map(p => (
                <tr key={p.id_producto}>
                  <td>{p.nombre}</td>
                  <td className="text-center">{p.cantidad_vendida}</td>
                  <td className="text-right">{formatCOP(p.ingresos_generados)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default function Admin() {
  const [tab, setTab] = useState('facturas')
  const navigate = useNavigate()
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')

  useEffect(() => {
    if (!usuario || usuario.rol !== 'administrador') navigate('/login')
  }, [])

  function handleLogout() {
    localStorage.removeItem('usuario')
    navigate('/login')
  }

  return (
    <div className="admin-layout">
      <header className="admin-header">
        <div className="admin-brand"><span>💼</span><span>Panel administrativo</span></div>
        <div className="admin-header-right">
          <span className="admin-usuario">{usuario?.nombre}</span>
          <button className="btn-logout-admin" onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </header>

      <div className="admin-tabs">
        <button className={`tab-btn ${tab === 'facturas' ? 'activa' : ''}`} onClick={() => setTab('facturas')}>
          🧾 Facturación
        </button>
        <button className={`tab-btn ${tab === 'estadisticas' ? 'activa' : ''}`} onClick={() => setTab('estadisticas')}>
          📊 Estadísticas
        </button>
      </div>

      <main className="admin-main">
        {tab === 'facturas' ? <TabFacturas /> : <TabEstadisticas />}
      </main>
    </div>
  )
}
