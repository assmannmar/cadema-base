# Definición de Tablas (Inmuebles y Usuarios)

from sqlalchemy import Column, Integer, String, Float, Date
from database import Base
import datetime

class Inmueble(Base):
    __tablename__ = "inmuebles"
    
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String, default="Tasación") # Tasación, Para Publicar, Publicado
    
    # Datos de la Planilla
    ciudad = Column(String)
    segmento = Column(String)
    emprendimiento = Column(String)
    tipo_inmueble = Column(String)
    direccion = Column(String)
    sup_cubierta = Column(Float)
    sup_terreno = Column(Float)
    
    # Etapa Tasación
    fecha_tasacion = Column(Date, default=datetime.date.today)
    valor_tasacion = Column(Float)
    link_drive = Column(String) # Carpeta Google Drive
    
    # Etapa Publicación
    valor_publicacion = Column(Float, nullable=True)
    link_portal = Column(String, nullable=True) # Link de Tokko/ZonaProp
    fecha_publicacion = Column(Date, nullable=True)