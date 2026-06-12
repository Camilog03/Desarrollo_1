from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

# ─── POST: Generar factura ──────────────────────────
@router.post("/facturas/{id_pedido}")
def generar_factura(id_pedido: int, db: Session = Depends(get_db)):
    
    # 1. Verificar que el pedido existe
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == id_pedido
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # 2. Verificar que el pedido está listo para facturar
    if pedido.estado != "listo":
        raise HTTPException(
            status_code=400, 
            detail=f"El pedido no está listo, estado actual: {pedido.estado}"
        )
    
    # 3. Verificar que no tenga factura ya generada
    factura_existente = db.query(models.Factura).filter(
        models.Factura.id_pedido == id_pedido
    ).first()
    
    if factura_existente:
        raise HTTPException(status_code=400, detail="Este pedido ya tiene factura")
    
    # 4. Calcular el total
    detalles = (
        db.query(models.DetallePedido, models.Producto)
        .join(models.Producto, models.Producto.id == models.DetallePedido.id_producto)
        .filter(models.DetallePedido.id_pedido == id_pedido)
        .all()
    )

    total = sum(detalle.cantidad * producto.precio for detalle, producto in detalles)
    # 5. Crear la factura
    nueva_factura = models.Factura(
        total=total,
        estado_pago="pendiente",
        id_pedido=id_pedido
    )
    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)
    
    return {
        "id_factura": nueva_factura.id,
        "id_pedido": id_pedido,
        "total": total,
        "estado_pago": nueva_factura.estado_pago,
        "fecha": nueva_factura.fecha
    }


# ─── GET: Ver detalle de factura ───────────────────
@router.get("/facturas/{id}")
def obtener_factura(id: int, db: Session = Depends(get_db)):
    
    # 1. Buscar la factura
    factura = db.query(models.Factura).filter(
        models.Factura.id == id
    ).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # 2. Obtener los detalles del pedido
    detalles = (
        db.query(models.DetallePedido, models.Producto)
        .join(models.Producto, models.Producto.id == models.DetallePedido.id_producto)
        .filter(models.DetallePedido.id_pedido == factura.id_pedido)
        .all()
    )

    # 3. Armar la respuesta con nombre y precio (sin observaciones)
    productos_factura = []
    for detalle, producto in detalles:
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
