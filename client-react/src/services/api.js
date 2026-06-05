import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const obtenerProductos = () => api.get("/productos/");
export const obtenerProducto = (id) => api.get(`/productos/${id}`);