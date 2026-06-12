from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from pydantic import BaseModel
from typing import List

router = APIRouter()

# ─── SCHEMAS ───────────────────────────────────────
class DetallePedidoSchema(BaseModel):
    id_producto: int
    cantidad: int
    observaciones: str = ""

class PedidoSchema(BaseModel):
    id_mesa: int
    productos: List[DetallePedidoSchema]

# ─── CREAR PEDIDO ──────────────────────────────────
@router.post("/pedidos")
def crear_pedido(pedido: PedidoSchema, db: Session = Depends(get_db)):
    nuevo_pedido = models.Pedido(
        estado="pendiente",
        id_mesa=pedido.id_mesa
    )
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

# ─── VER TODOS LOS PEDIDOS ─────────────────────────
@router.get("/pedidos")
def obtener_pedidos(estado: str = None, db: Session = Depends(get_db)):
    
    query = db.query(models.Pedido)
    
    # Si se manda un estado como parámetro, filtra por ese estado
    # Ejemplo: /api/pedidos?estado=entregado
    if estado:
        query = query.filter(models.Pedido.estado == estado)
    
    # Ejecuta la consulta con o sin filtro
    pedidos = query.all()

    resultado = []
    for pedido in pedidos:
        # Por cada pedido, busca sus productos en detalle_pedido
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_pedido == pedido.id
        ).all()

        # Arma la respuesta con el pedido y sus productos
        resultado.append({
            "id": pedido.id,
            "estado": pedido.estado,
            "fecha_hora": pedido.fecha_hora,
            "id_mesa": pedido.id_mesa,
            "productos": [
                {
                    "id_producto": d.id_producto,
                    "cantidad": d.cantidad,
                    "observaciones": d.observaciones
                }
                for d in detalles
            ]
        })

    return resultado

# ─── VER PEDIDO POR ID ─────────────────────────────
@router.get("/pedidos/{id}")
def obtener_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalles = db.query(models.DetallePedido).filter(
        models.DetallePedido.id_pedido == pedido.id
    ).all()

    return {
        "id": pedido.id,
        "estado": pedido.estado,
        "fecha_hora": pedido.fecha_hora,
        "id_mesa": pedido.id_mesa,
        "productos": [
            {
                "id_producto": d.id_producto,
                "cantidad": d.cantidad,
                "observaciones": d.observaciones
            }
            for d in detalles
        ]
    }

# ─── CAMBIAR ESTADO ────────────────────────────────
class EstadoSchema(BaseModel):
    estado: str

@router.put("/pedidos/{id}/estado")
def cambiar_estado(id: int, datos: EstadoSchema, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    estados_validos = ["pendiente", "confirmado", "en_cocina", "entregado"]
    if datos.estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Debe ser uno de: {estados_validos}")

    pedido.estado = datos.estado
    db.commit()
    db.refresh(pedido)

    return {"mensaje": "Estado actualizado", "id_pedido": pedido.id, "estado": pedido.estado}