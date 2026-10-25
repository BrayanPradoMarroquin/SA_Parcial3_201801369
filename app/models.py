from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    activo = Column(Boolean, default=True)
    
    roles = relationship("Rol", secondary="usuarios_roles", backref="usuarios")

class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)

class Proceso(Base):
    __tablename__ = "procesos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True)
    nombre = Column(String)

class Cola(Base):
    __tablename__ = "colas"
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos.id"))
    codigo = Column(String, unique=True)
    nombre = Column(String)
    activa = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True)
    titulo = Column(String)
    descripcion = Column(Text)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"))
    proceso_id = Column(Integer, ForeignKey("procesos.id"))
    cola_id = Column(Integer, ForeignKey("colas.id"))
    asignado_a_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    estado = Column(String, default="Nuevo")
    prioridad = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)