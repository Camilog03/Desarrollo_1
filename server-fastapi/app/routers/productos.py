from fastapi import APIRouter, HTTPException
from app.data.productos import productos

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/")
def obtener_productos():
    return productos

@router.get("/{producto_id}")
def obtener_producto(producto_id: int):
    producto = next((p for p in productos if p["id"] == producto_id), None)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto