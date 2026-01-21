# Rutas de la API y Seguridad

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
    return {"mensaje": "Tasación registrada con éxito"}

@app.put("/inmuebles/{id}/preparar-publicacion")
def preparar_publicacion(id: int, valor_pub: float, db: Session = Depends(get_db)):
    inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
    inmueble.estado = "Para Publicar"
    inmueble.valor_publicacion = valor_pub
    db.commit()
    return {"mensaje": "Estado actualizado: Para Publicar"}

@app.put("/inmuebles/{id}/publicar")
def completar_publicacion(id: int, link_portal: str, db: Session = Depends(get_db)):
    inmueble = db.query(models.Inmueble).filter(models.Inmueble.id == id).first()
    inmueble.estado = "Publicado"
    inmueble.link_portal = link_portal
    inmueble.fecha_publicacion = datetime.date.today()
    db.commit()
    return {"mensaje": "Inmueble publicado oficialmente"}