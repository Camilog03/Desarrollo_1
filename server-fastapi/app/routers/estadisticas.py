from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from datetime import date

router = APIRouter()

# ─── GET: Ventas diarias ────────────────────────────
@router.get("/estadisticas/ventas-diarias")
def ventas_diarias(db: Session = Depends(get_db)):

    hoy = date.today()

    # Buscar facturas generadas hoy
    cantidad_ventas, total_recaudado = db.query(
        func.count(models.Factura.id),
        func.coalesce(func.sum(models.Factura.total), 0.0),
    ).filter(
        func.date(models.Factura.fecha) == hoy
    ).one()

    return {
        "fecha": str(hoy),
        "cantidad_ventas": cantidad_ventas,
        "total_recaudado": total_recaudado
    }


# ─── GET: Ventas por producto ───────────────────────
@router.get("/estadisticas/ventas-producto")
def ventas_por_producto(db: Session = Depends(get_db)):

    # Traer todos los productos
    filas = (
        db.query(
            models.Producto.id.label("id_producto"),
            models.Producto.nombre.label("nombre"),
            func.sum(models.DetallePedido.cantidad).label("cantidad_vendida"),
            func.sum(models.DetallePedido.cantidad * models.Producto.precio).label("ingresos_generados"),
        )
        .join(models.DetallePedido, models.DetallePedido.id_producto == models.Producto.id)
        .join(models.Pedido, models.Pedido.id == models.DetallePedido.id_pedido)
        .join(models.Factura, models.Factura.id_pedido == models.Pedido.id)
        .group_by(models.Producto.id, models.Producto.nombre)
        .order_by(func.sum(models.DetallePedido.cantidad).desc())
        .all()
    )

    return [
        {
            "id_producto": f.id_producto,
            "nombre": f.nombre,
            "cantidad_vendida": int(f.cantidad_vendida),
            "ingresos_generados": float(f.ingresos_generados),
        }
        for f in filas
    ]


# ─── GET: Ganancias por mes ─────────────────────────
@router.get("/estadisticas/ganancias-mes")
def ganancias_por_mes(mes: int, anio: int, db: Session = Depends(get_db)):

    # Filtrar facturas por mes y año
    cantidad_ventas, total_ganancias = db.query(
        func.count(models.Factura.id),
        func.coalesce(func.sum(models.Factura.total), 0.0),
    ).filter(
        func.extract("month", models.Factura.fecha) == mes,
        func.extract("year", models.Factura.fecha) == anio,
    ).one()

    return {
        "mes": mes,
        "anio": anio,
        "cantidad_ventas": cantidad_ventas,
        "total_ganancias": total_ganancias
    }
