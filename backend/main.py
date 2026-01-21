# Rutas de la API y Seguridad

@app.post("/inmuebles/", tags=["Inmuebles"])
def cargar_inmueble(
    direccion: str, 
    precio_tasacion: float, 
    estado: str = "Tasación",
    db: Session = Depends(get_db)
):
    nuevo = models.Inmueble(
        direccion=direccion, 
        precio_tasacion=precio_tasacion, 
        estado_actual=estado,
        fecha_tasacion=datetime.date.today()
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": "Inmueble registrado en etapa de Tasación"}

# Nuevo endpoint para actualizar la etapa (Ej: de Tasación a Publicado)
@app.put("/inmuebles/{id}/avanzar", tags=["Inmuebles"])
def avanzar_etapa(id: int, nuevo_estado: str, precio: float, db: Session = Depends(get_db)):
    inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    
    inmueble.estado_actual = nuevo_estado
    hoy = datetime.date.today()

    if nuevo_estado == "Publicado":
        inmueble.fecha_publicacion = hoy
        inmueble.precio_publicacion = precio
    elif nuevo_estado == "Vendido":
        inmueble.fecha_cierre = hoy
        inmueble.precio_venta = precio
    
    db.commit()
    return {"mensaje": f"Inmueble actualizado a {nuevo_estado}"}