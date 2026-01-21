# Definición de Tablas (Inmuebles y Usuarios)

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    # Roles: 'admin', 'agente', 'visor'
    role = Column(String, default="agente") 
    is_active = Column(Boolean, default=True)

class Inmueble(Base):
    __tablename__ = "inmuebles"
    
    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String, index=True)
    precio = Column(Float)
    estado = Column(String) # Tasación, Vendido, etc.
    agente_id = Column(Integer, ForeignKey("usuarios.id"))