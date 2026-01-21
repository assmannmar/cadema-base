# Rutas de la API y Seguridad

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Importamos lo que creamos antes
from database import engine, get_db, Base
import models

# Esto crea las tablas en la base de datos automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Inmobiliario API")

@app.get("/")
def home():
    return {"mensaje": "API Inmobiliaria Funcionando"}

# --- LÓGICA DE USUARIOS Y ROLES (Básico) ---

@app.post("/usuarios/", tags=["Usuarios"])
def crear_usuario(email: str, clave: str, rol: str, db: Session = Depends(get_db)):
    # Aquí luego agregaremos encriptación real, por ahora es para probar
    nuevo_usuario = models.User(email=email, hashed_password=clave, role=rol)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario creado con éxito", "usuario": nuevo_usuario.email}

# --- LÓGICA DE INMUEBLES ---

@app.get("/inmuebles/", tags=["Inmuebles"])
def listar_inmuebles(db: Session = Depends(get_db)):
    return db.query(models.Inmueble).all()

@app.post("/inmuebles/", tags=["Inmuebles"])
def cargar_inmueble(direccion: str, precio: float, estado: str, db: Session = Depends(get_db)):
    # Aquí podrías validar: si el usuario no es 'admin' o 'agente', no dejarlo pasar
    nuevo = models.Inmueble(direccion=direccion, precio=precio, estado=estado)
    db.add(nuevo)
    db.commit()
    return {"mensaje": "Inmueble cargado"}