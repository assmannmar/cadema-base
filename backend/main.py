# Rutas de la API y Seguridad
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import models
from database import engine, get_db, Base
import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# 2. Crear la variable app
app = FastAPI(title="API Inmobiliaria Cadema")

# 3. ENDPOINTS

@app.get("/")
def home():
    return {"mensaje": "API Cadema funcionando", "version": "1.0"}

@app.get("/inmuebles/", tags=["Consultas"])
def listar_inmuebles(db: Session = Depends(get_db)):
    """Lista todos los inmuebles en la base de datos"""
    try:
        inmuebles = db.query(models.Inmueble).all()
        logger.info(f"Se recuperaron {len(inmuebles)} inmuebles")
        return inmuebles
    except Exception as e:
        logger.error(f"Error al listar inmuebles: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al recuperar inmuebles")

@app.get("/inmuebles/buscar", tags=["Consultas"])
def buscar_inmuebles(
    ciudad: Optional[str] = None,
    estado: Optional[str] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Busca inmuebles con filtros opcionales"""
    try:
        query = db.query(models.Inmueble)
        
        if ciudad:
            query = query.filter(models.Inmueble.ciudad == ciudad)
        if estado:
            query = query.filter(models.Inmueble.estado == estado)
        if precio_min:
            query = query.filter(models.Inmueble.valor_tasacion >= precio_min)
        if precio_max:
            query = query.filter(models.Inmueble.valor_tasacion <= precio_max)
        
        resultados = query.all()
        logger.info(f"Búsqueda retornó {len(resultados)} resultados")
        return resultados
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la búsqueda")

@app.post("/inmuebles/tasar", tags=["Flujo Inmobiliario"])
def tasar_inmueble(
    ciudad: str, 
    segmento: str, 
    emprendimiento: str, 
    tipo: str,
    direccion: str, 
    sup_cubierta: float, 
    sup_terreno: float,
    valor_tasacion: float, 
    link_drive: str,
    db: Session = Depends(get_db)
):
    """Registra una nueva tasación"""
    try:
        # Validaciones básicas
        if valor_tasacion <= 0:
            raise HTTPException(status_code=400, detail="El valor de tasación debe ser positivo")
        if sup_cubierta < 0 or sup_terreno < 0:
            raise HTTPException(status_code=400, detail="Las superficies no pueden ser negativas")
        
        nuevo = models.Inmueble(
            estado="Tasación",
            ciudad=ciudad, 
            segmento=segmento, 
            emprendimiento=emprendimiento,
            tipo_inmueble=tipo, 
            direccion=direccion,
            sup_cubierta=sup_cubierta, 
            sup_terreno=sup_terreno,
            valor_tasacion=valor_tasacion, 
            link_drive=link_drive,
            fecha_tasacion=datetime.date.today()
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        logger.info(f"Nueva tasación registrada - ID: {nuevo.id}, Dirección: {direccion}")
        return {"mensaje": "Tasación registrada con éxito", "id": nuevo.id, "direccion": direccion}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar tasación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al registrar tasación")

@app.put("/inmuebles/{id}/preparar-publicacion", tags=["Flujo Inmobiliario"])
def preparar_publicacion(id: int, valor_pub: float, db: Session = Depends(get_db)):
    """Prepara un inmueble para publicación"""
    try:
        inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
        if not inmueble:
            raise HTTPException(status_code=404, detail="Inmueble no encontrado")
        
        if valor_pub <= 0:
            raise HTTPException(status_code=400, detail="El valor de publicación debe ser positivo")
        
        inmueble.estado = "Para Publicar"
        inmueble.valor_publicacion = valor_pub
        db.commit()
        
        logger.info(f"Inmueble {id} preparado para publicación - Valor: ${valor_pub}")
        return {"mensaje": "Estado actualizado: Para Publicar", "id": id, "valor_publicacion": valor_pub}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al preparar publicación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar estado")

@app.put("/inmuebles/{id}/publicar", tags=["Flujo Inmobiliario"])
def completar_publicacion(id: int, link_portal: str, db: Session = Depends(get_db)):
    """Marca un inmueble como publicado"""
    try:
        inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
        if not inmueble:
            raise HTTPException(status_code=404, detail="Inmueble no encontrado")
        
        if not link_portal or link_portal.strip() == "":
            raise HTTPException(status_code=400, detail="Debe proporcionar un link del portal")
        
        inmueble.estado = "Publicado"
        inmueble.link_portal = link_portal
        inmueble.fecha_publicacion = datetime.date.today()
        db.commit()
        
        logger.info(f"Inmueble {id} publicado oficialmente")
        return {"mensaje": "Inmueble publicado oficialmente", "id": id, "link_portal": link_portal}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al publicar inmueble: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al publicar")

@app.get("/estadisticas/resumen", tags=["Reportes"])
def resumen_estadisticas(db: Session = Depends(get_db)):
    """Retorna estadísticas generales del inventario"""
    try:
        total = db.query(models.Inmueble).count()
        por_estado = {}
        for estado in ["Tasación", "Para Publicar", "Publicado"]:
            count = db.query(models.Inmueble).filter(models.Inmueble.estado == estado).count()
            por_estado[estado] = count
        
        return {
            "total_inmuebles": total,
            "por_estado": por_estado
        }
    except Exception as e:
        logger.error(f"Error al generar estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al generar estadísticas")