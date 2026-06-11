from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app import models
import bcrypt

router = APIRouter()

# ─── Schemas (sin tilde para compatibilidad JSON) ───
class LoginSchema(BaseModel):
    correo: str
    contrasena: str  # sin tilde — el JSON no soporta tildes en claves

class UsuarioSchema(BaseModel):
    nombre: str
    correo: str
    contrasena: str  # sin tilde
    rol: str

@router.post("/usuarios")
def crear_usuario(datos: UsuarioSchema, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")

    if datos.rol not in ["empleado", "administrador"]:
        raise HTTPException(status_code=400, detail="El rol debe ser empleado o administrador")

    hash = bcrypt.hashpw(datos.contrasena.encode("utf-8"), bcrypt.gensalt())

    nuevo_usuario = models.Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contraseña=hash.decode("utf-8"),
        rol=datos.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"id": nuevo_usuario.id, "nombre": nuevo_usuario.nombre, "correo": nuevo_usuario.correo, "rol": nuevo_usuario.rol}

@router.post("/login")
def login(datos: LoginSchema, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    contrasena_correcta = bcrypt.checkpw(
        datos.contrasena.encode("utf-8"),
        usuario.contraseña.encode("utf-8")
    )
    if not contrasena_correcta:
        raise HTTPException(status_code=400, detail="Contrasena incorrecta")

    if usuario.rol not in ["empleado", "administrador"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder")

    return {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo, "rol": usuario.rol}
