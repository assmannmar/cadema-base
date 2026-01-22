# Reglas de validación de datos
# Reglas de validación de datos con Pydantic

from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import date

class InmuebleBase(BaseModel):
    """Esquema base para validar datos de inmuebles"""
    ciudad: str = Field(..., min_length=1, description="Ciudad donde se encuentra el inmueble")
    segmento: str = Field(..., min_length=1, description="Segmento del inmueble")
    emprendimiento: str = Field(..., min_length=1, description="Nombre del emprendimiento")
    tipo_inmueble: str = Field(..., min_length=1, description="Tipo de inmueble")
    direccion: str = Field(..., min_length=1, description="Dirección del inmueble")
    sup_cubierta: float = Field(..., ge=0, description="Superficie cubierta en m2")
    sup_terreno: float = Field(..., ge=0, description="Superficie del terreno en m2")
    valor_tasacion: float = Field(..., gt=0, description="Valor de tasación en USD")
    link_drive: str = Field(..., description="Link a carpeta de Google Drive")

    @validator('valor_tasacion')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El valor de tasación debe ser mayor a 0')
        if v > 100000000:  # 100 millones USD como límite razonable
            raise ValueError('El valor de tasación parece excesivo, verifique')
        return v

    @validator('sup_cubierta', 'sup_terreno')
    def validar_superficies(cls, v):
        if v < 0:
            raise ValueError('Las superficies no pueden ser negativas')
        if v > 1000000:  # 1 millón m2 como límite razonable
            raise ValueError('La superficie parece excesiva, verifique')
        return v

    @validator('ciudad', 'segmento', 'emprendimiento', 'tipo_inmueble', 'direccion')
    def validar_texto_no_vacio(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Este campo no puede estar vacío')
        return v.strip()

class InmuebleCreate(InmuebleBase):
    """Esquema para crear un nuevo inmueble"""
    pass

class InmuebleUpdate(BaseModel):
    """Esquema para actualizar un inmueble"""
    valor_publicacion: Optional[float] = Field(None, gt=0, description="Valor de publicación")
    link_portal: Optional[str] = Field(None, description="Link al portal inmobiliario")

    @validator('valor_publicacion')
    def validar_valor_publicacion(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor de publicación debe ser mayor a 0')
        return v

class InmuebleResponse(InmuebleBase):
    """Esquema de respuesta con todos los datos del inmueble"""
    id: int
    estado: str
    fecha_tasacion: Optional[date]
    valor_publicacion: Optional[float]
    link_portal: Optional[str]
    fecha_publicacion: Optional[date]

    class Config:
        from_attributes = True  # Permite trabajar con objetos SQLAlchemy

class EstadisticasResponse(BaseModel):
    """Esquema para respuesta de estadísticas"""
    total_inmuebles: int
    por_estado: dict

class BusquedaParams(BaseModel):
    """Parámetros de búsqueda"""
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    precio_min: Optional[float] = Field(None, ge=0)
    precio_max: Optional[float] = Field(None, ge=0)

    @validator('precio_max')
    def validar_rango_precios(cls, v, values):
        if v is not None and 'precio_min' in values and values['precio_min'] is not None:
            if v < values['precio_min']:
                raise ValueError('El precio máximo debe ser mayor al precio mínimo')
        return v