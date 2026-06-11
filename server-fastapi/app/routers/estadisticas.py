from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from datetime import date

router = APIRouter()

@router.get("/estadisticas/ventas-diarias")
def ventas_diarias(db: Session = Depends(get_db)):
    hoy = date.today()
    facturas_hoy = db.query(models.Factura).filter(
        func.date(models.Factura.fecha) == hoy
    ).all()
    total_ventas = sum(f.total for f in facturas_hoy)
    return {
        "fecha": str(hoy),
        "cantidad_ventas": len(facturas_hoy),
        "total_recaudado": total_ventas
    }

@router.get("/estadisticas/ventas-producto")
def ventas_por_producto(db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    resultado = []
    for producto in productos:
        detalles = db.query(models.DetallePedido).filter(
            models.DetallePedido.id_producto == producto.id
        ).all()
        cantidad_total = sum(d.cantidad for d in detalles)
        ingresos = cantidad_total * producto.precio
        resultado.append({
            "id_producto": producto.id,
            "nombre": producto.nombre,
            "cantidad_vendida": cantidad_total,
            "ingresos_generados": ingresos
        })
    resultado.sort(key=lambda x: x["cantidad_vendida"], reverse=True)
    return resultado

@router.get("/estadisticas/ganancias-mes")
def ganancias_por_mes(mes: int, anio: int, db: Session = Depends(get_db)):
    facturas_mes = db.query(models.Factura).filter(
        func.extract("month", models.Factura.fecha) == mes,
        func.extract("year", models.Factura.fecha) == anio
    ).all()
    total_ganancias = sum(f.total for f in facturas_mes)
    return {
        "mes": mes,
        "anio": anio,
        "cantidad_ventas": len(facturas_mes),
        "total_ganancias": total_ganancias
    }
