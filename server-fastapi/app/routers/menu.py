from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/menu")
def obtener_menu(db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()

    resultado = []
    for categoria in categorias:
        productos = db.query(models.Producto).filter(
            models.Producto.id_categoria == categoria.id
        ).all()

        resultado.append({
            "id": categoria.id,
            "nombre": categoria.nombre,
            "productos": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": p.precio
                }
                for p in productos
            ]
        })

    return resultado