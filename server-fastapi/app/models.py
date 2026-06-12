# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Mesa(Base):
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    n_mesa = Column(Integer, nullable=False)
    estado = Column(String, default="disponible")

    pedidos = relationship("Pedido", back_populates="mesa")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # empleado o administrador
    correo = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)

    pedidos = relationship("Pedido", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categoria", back_populates="productos")
    detalles = relationship("DetallePedido", back_populates="producto")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String, default="pendiente")
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow)
    id_mesa = Column(Integer, ForeignKey("mesas.id"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    mesa = relationship("Mesa", back_populates="pedidos")
    usuario = relationship("Usuario", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
    factura = relationship("Factura", back_populates="pedido")


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False)
    observaciones = Column(Text, nullable=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"))
    id_producto = Column(Integer, ForeignKey("productos.id"))

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    estado_pago = Column(String, default="pendiente")
    id_pedido = Column(Integer, ForeignKey("pedidos.id"))

    pedido = relationship("Pedido", back_populates="factura")
