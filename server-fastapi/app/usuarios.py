from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app import models
import bcrypt

router = APIRouter()

# ─── Schemas ────────────────────────────────────────
class LoginSchema(BaseModel):
    correo: str
    contraseña: str

class UsuarioSchema(BaseModel):
    nombre: str
    correo: str
    contraseña: str
    rol: str

# ─── POST: Crear usuario ────────────────────────────
@router.post("/usuarios")
def crear_usuario(datos: UsuarioSchema, db: Session = Depends(get_db)):

    # 1. Verificar que el correo no exista ya
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con ese correo"
        )

    # 2. Verificar que el rol sea válido
    if datos.rol not in ["empleado", "administrador"]:
        raise HTTPException(
            status_code=400,
            detail="El rol debe ser empleado o administrador"
        )

    # 3. Hashear la contraseña
    hash = bcrypt.hashpw(
        datos.contraseña.encode("utf-8"),
        bcrypt.gensalt()
    )

    # 4. Crear el usuario
    nuevo_usuario = models.Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contraseña=hash.decode("utf-8"),  # guardar como string en BD
        rol=datos.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }


# ─── POST: Login ────────────────────────────────────
@router.post("/login")
def login(datos: LoginSchema, db: Session = Depends(get_db)):

    # 1. Buscar el usuario por correo
    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    # 2. Verificar que existe
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    # 3. Verificar la contraseña con bcrypt
    contraseña_correcta = bcrypt.checkpw(
        datos.contraseña.encode("utf-8"),
        usuario.contraseña.encode("utf-8")
    )

    if not contraseña_correcta:
        raise HTTPException(
            status_code=400,
            detail="Contraseña incorrecta"
        )

    # 4. Verificar rol
    if usuario.rol not in ["empleado", "administrador"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para acceder"
        )

    # 5. Retornar usuario
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    }
