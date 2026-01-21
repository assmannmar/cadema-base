# Rutas de la API y Seguridad
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, get_db, Base
import datetime

# 1. Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# 2. Crear la variable app
app = FastAPI(title="API Inmobiliaria Cadema")

# 3. ENDPOINTS

@app.get("/")
def home():
    return {"mensaje": "API Cadema funcionando"}

@app.get("/inmuebles/", tags=["Consultas"])
def listar_inmuebles(db: Session = Depends(get_db)):
    # Esta función es vital para que la tabla de Streamlit muestre datos
    return db.query(models.Inmueble).all()

@app.post("/inmuebles/tasar", tags=["Flujo Inmobiliario"])
def tasar_inmueble(
    ciudad: str, segmento: str, emprendimiento: str, tipo: str,
    direccion: str, sup_cubierta: float, sup_terreno: float,
    valor_tasacion: float, link_drive: str,
    db: Session = Depends(get_db)
):
    nuevo = models.Inmueble(
        estado="Tasación",
        ciudad=ciudad, segmento=segmento, emprendimiento=emprendimiento,
        tipo_inmueble=tipo, direccion=direccion,
        sup_cubierta=sup_cubierta, sup_terreno=sup_terreno,
        valor_tasacion=valor_tasacion, link_drive=link_drive,
        fecha_tasacion=datetime.date.today()
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Tasación registrada con éxito", "id": nuevo.id}

@app.put("/inmuebles/{id}/preparar-publicacion", tags=["Flujo Inmobiliario"])
def preparar_publicacion(id: int, valor_pub: float, db: Session = Depends(get_db)):
    inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    
    inmueble.estado = "Para Publicar"
    inmueble.valor_publicacion = valor_pub
    db.commit()
    return {"mensaje": "Estado actualizado: Para Publicar"}

@app.put("/inmuebles/{id}/publicar", tags=["Flujo Inmobiliario"])
def completar_publicacion(id: int, link_portal: str, db: Session = Depends(get_db)):
    inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
        
    inmueble.estado = "Publicado"
    inmueble.link_portal = link_portal
    inmueble.fecha_publicacion = datetime.date.today()
    db.commit()
    return {"mensaje": "Inmueble publicado oficialmente"}