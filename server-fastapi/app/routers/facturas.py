from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/facturas/{id_pedido}")
def generar_factura(id_pedido: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Acepta estado despachado para facturar
    if pedido.estado != "despachado":
        raise HTTPException(status_code=400, detail=f"El pedido no está listo para facturar, estado actual: {pedido.estado}")

    factura_existente = db.query(models.Factura).filter(models.Factura.id_pedido == id_pedido).first()
    if factura_existente:
        raise HTTPException(status_code=400, detail="Este pedido ya tiene factura")

    detalles = db.query(models.DetallePedido).filter(models.DetallePedido.id_pedido == id_pedido).all()
    total = 0
    for detalle in detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == detalle.id_producto).first()
        total += detalle.cantidad * producto.precio

    nueva_factura = models.Factura(total=total, estado_pago="pendiente", id_pedido=id_pedido)
    db.add(nueva_factura)
    pedido.estado = "facturado"
    db.commit()
    db.refresh(nueva_factura)

    return {
        "id_factura": nueva_factura.id,
        "id_pedido": id_pedido,
        "total": total,
        "estado_pago": nueva_factura.estado_pago,
        "fecha": nueva_factura.fecha
    }

@router.get("/facturas/{id}")
def obtener_factura(id: int, db: Session = Depends(get_db)):
    factura = db.query(models.Factura).filter(models.Factura.id == id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    detalles = db.query(models.DetallePedido).filter(
        models.DetallePedido.id_pedido == factura.id_pedido
    ).all()

    productos_factura = []
    for detalle in detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == detalle.id_producto).first()
        productos_factura.append({
            "nombre": producto.nombre,
            "precio_unitario": producto.precio,
            "cantidad": detalle.cantidad,
            "subtotal": detalle.cantidad * producto.precio
        })

    return {
        "id_factura": factura.id,
        "fecha": factura.fecha,
        "estado_pago": factura.estado_pago,
        "total": factura.total,
        "productos": productos_factura
    }
