from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ─── Schemas ───────────────────────────────────────
class DetallePedidoSchema(BaseModel):
    id_producto: int
    cantidad: int
    observaciones: str = ""

class PedidoSchema(BaseModel):
    id_mesa: int
    productos: List[DetallePedidoSchema]

class DetalleEditSchema(BaseModel):
    id: int
    cantidad: int
    observaciones: Optional[str] = None

class PedidoEditSchema(BaseModel):
    detalles: List[DetalleEditSchema]

class EstadoSchema(BaseModel):
    estado: str

# ─── Crear pedido ───────────────────────────────────
@router.post("/pedidos")
def crear_pedido(pedido: PedidoSchema, db: Session = Depends(get_db)):
    mesa = db.query(models.Mesa).filter(models.Mesa.id == pedido.id_mesa).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    nuevo_pedido = models.Pedido(estado="pendiente", id_mesa=pedido.id_mesa)
    db.add(nuevo_pedido)
    db.flush()

    for item in pedido.productos:
        detalle = models.DetallePedido(
            id_pedido=nuevo_pedido.id,
            id_producto=item.id_producto,
            cantidad=item.cantidad,
            observaciones=item.observaciones
        )
        db.add(detalle)

    db.commit()
    db.refresh(nuevo_pedido)
    return {"mensaje": "Pedido creado", "id_pedido": nuevo_pedido.id}

# ─── Ver todos los pedidos ──────────────────────────
@router.get("/pedidos")
def obtener_pedidos(estado: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Pedido)
    if estado:
        query = query.filter(models.Pedido.estado == estado)
    pedidos = query.all()

    resultado = []
    for pedido in pedidos:
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_pedido == pedido.id
        ).all()
        resultado.append({
            "id": pedido.id,
            "estado": pedido.estado,
            "fecha_hora": pedido.fecha_hora,
            "id_mesa": pedido.id_mesa,
            "productos": [
                {"id": d.id, "id_producto": d.id_producto, "cantidad": d.cantidad, "observaciones": d.observaciones}
                for d in detalles
            ]
        })
    return resultado

# ─── Ver pedido por ID ──────────────────────────────
@router.get("/pedidos/{id}")
def obtener_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalles = db.query(models.DetallePedido).filter(
        models.DetallePedido.id_pedido == pedido.id
    ).all()

    productos_con_info = []
    for d in detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == d.id_producto).first()
        productos_con_info.append({
            "id": d.id,
            "id_producto": d.id_producto,
            "nombre": producto.nombre if producto else None,
            "precio": producto.precio if producto else None,
            "cantidad": d.cantidad,
            "observaciones": d.observaciones
        })

    return {
        "id": pedido.id,
        "estado": pedido.estado,
        "fecha_hora": pedido.fecha_hora,
        "id_mesa": pedido.id_mesa,
        "productos": productos_con_info
    }

# ─── Pedidos pendientes (mesero) ────────────────────
@router.get("/pedidos-pendientes")
def pedidos_pendientes(db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).filter(models.Pedido.estado == "pendiente").all()
    resultado = []
    for pedido in pedidos:
        mesa = db.query(models.Mesa).filter(models.Mesa.id == pedido.id_mesa).first()
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_pedido == pedido.id
        ).all()
        productos_con_info = []
        for d in detalles:
            producto = db.query(models.Producto).filter(models.Producto.id == d.id_producto).first()
            productos_con_info.append({
                "id": d.id,
                "id_producto": d.id_producto,
                "nombre": producto.nombre if producto else None,
                "precio": producto.precio if producto else None,
                "cantidad": d.cantidad,
                "observaciones": d.observaciones
            })
        resultado.append({
            "id": pedido.id,
            "estado": pedido.estado,
            "id_mesa": pedido.id_mesa,
            "n_mesa": mesa.n_mesa if mesa else pedido.id_mesa,
            "productos": productos_con_info
        })
    return resultado

# ─── Pedidos en cocina ──────────────────────────────
@router.get("/pedidos-cocina")
def pedidos_cocina(db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).filter(models.Pedido.estado == "en_cocina").all()
    resultado = []
    for pedido in pedidos:
        mesa = db.query(models.Mesa).filter(models.Mesa.id == pedido.id_mesa).first()
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_pedido == pedido.id
        ).all()
        productos_con_info = []
        for d in detalles:
            producto = db.query(models.Producto).filter(models.Producto.id == d.id_producto).first()
            productos_con_info.append({
                "id": d.id,
                "id_producto": d.id_producto,
                "nombre": producto.nombre if producto else None,
                "cantidad": d.cantidad,
                "observaciones": d.observaciones
            })
        resultado.append({
            "id": pedido.id,
            "estado": pedido.estado,
            "id_mesa": pedido.id_mesa,
            "n_mesa": mesa.n_mesa if mesa else pedido.id_mesa,
            "productos": productos_con_info
        })
    return resultado

# ─── Pedidos despachados (admin/cajero) ─────────────
@router.get("/pedidos-despachados")
def pedidos_despachados(db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).filter(models.Pedido.estado == "despachado").all()
    resultado = []
    for pedido in pedidos:
        mesa = db.query(models.Mesa).filter(models.Mesa.id == pedido.id_mesa).first()
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_pedido == pedido.id
        ).all()
        productos_con_info = []
        total = 0
        for d in detalles:
            producto = db.query(models.Producto).filter(models.Producto.id == d.id_producto).first()
            subtotal = (producto.precio if producto else 0) * d.cantidad
            total += subtotal
            productos_con_info.append({
                "nombre": producto.nombre if producto else None,
                "precio_unitario": producto.precio if producto else 0,
                "cantidad": d.cantidad,
                "subtotal": subtotal
            })
        resultado.append({
            "id": pedido.id,
            "id_mesa": pedido.id_mesa,
            "n_mesa": mesa.n_mesa if mesa else pedido.id_mesa,
            "productos": productos_con_info,
            "total": total
        })
    return resultado

# ─── Editar pedido (mesero) ─────────────────────────
@router.put("/pedidos/{id}/editar")
def editar_pedido(id: int, data: PedidoEditSchema, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    for det_data in data.detalles:
        det = db.query(models.DetallePedido).filter(models.DetallePedido.id == det_data.id).first()
        if det:
            det.cantidad = det_data.cantidad
            det.observaciones = det_data.observaciones
    db.commit()
    return {"mensaje": "Pedido actualizado"}

# ─── Confirmar pedido → cocina ──────────────────────
@router.put("/pedidos/{id}/confirmar")
def confirmar_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = "en_cocina"
    db.commit()
    return {"mensaje": "Pedido enviado a cocina"}

# ─── Despachar pedido (cocina) ──────────────────────
@router.put("/pedidos/{id}/despachar")
def despachar_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = "despachado"
    db.commit()
    return {"mensaje": "Pedido despachado"}

# ─── Cambiar estado genérico ────────────────────────
@router.put("/pedidos/{id}/estado")
def cambiar_estado(id: int, datos: EstadoSchema, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    estados_validos = ["pendiente", "en_cocina", "despachado", "facturado"]
    if datos.estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Debe ser uno de: {estados_validos}")
    pedido.estado = datos.estado
    db.commit()
    return {"mensaje": "Estado actualizado", "id_pedido": pedido.id, "estado": pedido.estado}
