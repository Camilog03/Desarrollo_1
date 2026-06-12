function MenuCard({ producto, onAgregar }) {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.nombre}>{producto.nombre}</h3>
        <span style={styles.precio}>${producto.precio.toLocaleString("es-CO")}</span>
      </div>
      <p style={styles.categoria}>{producto.categoria}</p>
      <ul style={styles.ingredientes}>
        {producto.ingredientes.map((ing, i) => (
          <li key={i} style={styles.ingrediente}>{ing}</li>
        ))}
      </ul>
      <button style={styles.boton} onClick={() => onAgregar(producto)}>
        Agregar al pedido
      </button>
    </div>
  );
}

const styles = {
  card: { border: "1px solid #e2e0d8", borderRadius: 12, padding: "1rem", background: "#fff", display: "flex", flexDirection: "column", gap: 8 },
  header: { display: "flex", justifyContent: "space-between", alignItems: "flex-start" },
  nombre: { fontSize: 16, fontWeight: 500, margin: 0 },
  precio: { fontSize: 15, fontWeight: 600, color: "#0F6E56", whiteSpace: "nowrap" },
  categoria: { fontSize: 12, color: "#888", margin: 0 },
  ingredientes: { paddingLeft: 16, margin: 0 },
  ingrediente: { fontSize: 12, color: "#555", lineHeight: 1.6 },
  boton: { marginTop: 8, padding: "8px 0", background: "#0F6E56", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 500 },
};

export default MenuCard;