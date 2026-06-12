import { useState, useEffect } from "react";
import { obtenerProductos } from "../services/api";
import MenuCard from "../components/MenuCard";

function Menu() {
  const [productos, setProductos] = useState([]);
  const [pedido, setPedido] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    obtenerProductos()
      .then((res) => setProductos(res.data))
      .catch(() => setError("No se pudo cargar el menú"))
      .finally(() => setCargando(false));
  }, []);

  function agregarAlPedido(producto) {
    setPedido((prev) => {
      const existe = prev.find((p) => p.id === producto.id);
      if (existe) {
        return prev.map((p) =>
          p.id === producto.id ? { ...p, cantidad: p.cantidad + 1 } : p
        );
      }
      return [...prev, { ...producto, cantidad: 1, observacion: "" }];
    });
  }

  function actualizarObservacion(id, texto) {
    setPedido((prev) =>
      prev.map((p) => (p.id === id ? { ...p, observacion: texto } : p))
    );
  }

  if (cargando) return <p style={{ padding: "2rem" }}>Cargando menú...</p>;
  if (error) return <p style={{ padding: "2rem", color: "red" }}>{error}</p>;

  return (
    <div style={styles.page}>
      <h1 style={styles.titulo}>Menú del restaurante</h1>

      <div style={styles.grid}>
        {productos.map((p) => (
          <MenuCard key={p.id} producto={p} onAgregar={agregarAlPedido} />
        ))}
      </div>

      {pedido.length > 0 && (
        <div style={styles.pedidoBox}>
          <h2 style={styles.pedidoTitulo}>Tu pedido</h2>
          {pedido.map((item) => (
            <div key={item.id} style={styles.pedidoItem}>
              <div style={styles.pedidoNombre}>
                {item.nombre} x{item.cantidad} —{" "}
                <strong>${(item.precio * item.cantidad).toLocaleString("es-CO")}</strong>
              </div>
              <input
                style={styles.obsInput}
                placeholder="Observaciones (ej: sin sal, sin cebolla...)"
                value={item.observacion}
                onChange={(e) => actualizarObservacion(item.id, e.target.value)}
              />
            </div>
          ))}
          <div style={styles.total}>
            Total: $
            {pedido
              .reduce((acc, p) => acc + p.precio * p.cantidad, 0)
              .toLocaleString("es-CO")}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  page: { maxWidth: 960, margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif", background: "#f5f4f0", minHeight: "100vh" },
  titulo: { fontSize: 24, fontWeight: 500, marginBottom: "1.5rem" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16, marginBottom: "2rem" },
  pedidoBox: { background: "#fff", border: "1px solid #e2e0d8", borderRadius: 12, padding: "1.25rem" },
  pedidoTitulo: { fontSize: 18, fontWeight: 500, marginBottom: "1rem" },
  pedidoItem: { marginBottom: "1rem" },
  pedidoNombre: { fontSize: 14, marginBottom: 4 },
  obsInput: { width: "100%", padding: "6px 10px", borderRadius: 8, border: "1px solid #d3d1c7", fontSize: 13 },
  total: { fontSize: 16, fontWeight: 600, marginTop: "1rem", textAlign: "right", color: "#0F6E56" },
};

export default Menu;