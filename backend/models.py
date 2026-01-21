# Definición de Tablas (Inmuebles y Usuarios)

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from database import Base
import datetime

class Inmueble(Base):
    __tablename__ = "inmuebles"
    
    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String, index=True)
    
    # Etapa actual: 'Tasación', 'Publicado', 'Vendido', 'Baja'
    estado_actual = Column(String, default="Tasación")

    # --- ETAPA 1: TASACIÓN ---
    fecha_tasacion = Column(Date, default=datetime.date.today)
    precio_tasacion = Column(Float)
    
    # --- ETAPA 2: PUBLICACIÓN ---
    fecha_publicacion = Column(Date, nullable=True)
    precio_publicacion = Column(Float, nullable=True)
    
    # --- ETAPA 3: CIERRE (VENTA O BAJA) ---
    fecha_cierre = Column(Date, nullable=True)
    precio_venta = Column(Float, nullable=True)
    motivo_baja = Column(String, nullable=True) # Ejemplo: "Vendido por otro", "Arrepentido"