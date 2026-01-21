import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
API_URL = "https://cadema-base.onrender.com"

st.set_page_config(page_title="Cadema - Gestión Inmobiliaria", layout="wide")

# Estilos personalizados para los estados
def color_estado(val):
    color = '#f1f1f1'
    if val == "Tasación": color = '#FFE4E1'
    if val == "Para Publicar": color = '#FFFACD'
    if val == "Publicado": color = '#E0FFE0'
    return f'background-color: {color}'

st.title("🏠 Sistema de Gestión Inmobiliaria Cadema")

# --- LÓGICA DE SESIÓN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    with st.sidebar:
        st.subheader("Ingreso al Sistema")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user == "admin" and password == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Error de acceso")
else:
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- TABS DE TRABAJO ---
    tab_lista, tab_tasar, tab_mkt = st.tabs(["📊 Base Inmuebles", "📝 Nueva Tasación", "📢 Marketing"])

    # --- TAB 1: LISTADO GENERAL ---
    with tab_lista:
        st.subheader("Inventario General")
        try:
            res = requests.get(f"{API_URL}/inmuebles/")
            if res.status_code == 200:
                datos = res.json()
                if datos:
                    df = pd.DataFrame(datos)
                    # Mostrar solo columnas relevantes para el listado
                    cols = ["id", "estado", "ciudad", "direccion", "tipo_inmueble", "valor_tasacion", "valor_publicacion"]
                    st.dataframe(df[cols].style.applymap(color_estado, subset=['estado']), use_container_width=True)
                else:
                    st.info("No hay datos cargados.")
        except:
            st.error("No se pudo conectar con el servidor.")

    # --- TAB 2: NUEVA TASACIÓN (AGENTE) ---
    with tab_tasar:
        st.subheader("Registrar Nueva Tasación")
        with st.form("form_tasacion", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ciudad = st.selectbox("Ciudad", ["Campana", "Zarate", "Escobar", "Los Cardales"])
                segmento = st.selectbox("Segmento", ["Ciudad", "Industria", "Grandes Inmuebles", "Emprendimiento"])
                emprendimiento = st.text_input("Emprendimiento (si aplica)")
            with col2:
                tipo = st.selectbox("Tipo Inmueble", ["Casa", "Departamento", "Lote", "Local", "Galpón"])
                direccion = st.text_input("Dirección / Nro Lote")
                drive = st.text_input("Link Carpeta Google Drive (Documentación)")
            with col3:
                sup_c = st.number_input("Sup. Cubierta (m2)", min_value=0.0)
                sup_t = st.number_input("Sup. Terreno (m2)", min_value=0.0)
                valor_tas = st.number_input("Valor Tasación (USD)", min_value=0.0)

            if st.form_submit_button("Guardar Tasación"):
                payload = {
                    "ciudad": ciudad, "segmento": segmento, "emprendimiento": emprendimiento,
                    "tipo": tipo, "direccion": direccion, "sup_cubierta": sup_c,
                    "sup_terreno": sup_t, "valor_tasacion": valor_tas, "link_drive": drive
                }
                res = requests.post(f"{API_URL}/inmuebles/tasar", params=payload)
                if res.status_code == 200:
                    st.success("✅ Tasación registrada. Estado: 'Tasación'")
                else:
                    st.error("Error al guardar.")

        st.divider()
        st.subheader("➡️ Pasar a Publicación")
        st.write("Selecciona una tasación para autorizar su venta")
        # Aquí iría la lógica para pasar de 'Tasación' a 'Para Publicar'
        id_tas = st.number_input("ID del Inmueble", min_value=1, step=1)
        valor_pub = st.number_input("Valor de Publicación final (USD)", min_value=0.0)
        if st.button("Autorizar para Publicar"):
            res = requests.put(f"{API_URL}/inmuebles/{id_tas}/preparar-publicacion", params={"valor_pub": valor_pub})
            if res.status_code == 200:
                st.success("Estado actualizado a 'Para Publicar'")
                st.rerun()

    # --- TAB 3: MARKETING (PUBLICACIÓN FINAL) ---
    with tab_mkt:
        st.subheader("Pendientes de Publicación")
        try:
            res = requests.get(f"{API_URL}/inmuebles/")
            pendientes = [i for i in res.json() if i['estado'] == "Para Publicar"]
            
            if pendientes:
                for p in pendientes:
                    with st.expander(f"📌 {p['direccion']} - {p['ciudad']}"):
                        st.write(f"**Valor a publicar:** USD {p['valor_publicacion']}")
                        st.write(f"**Drive:** [Ver Documentación]({p['link_drive']})")
                        link_p = st.text_input("Link del Portal (Tokko/ZonaProp)", key=f"link_{p['id']}")
                        if st.button("Confirmar Publicación", key=f"btn_{p['id']}"):
                            if link_p:
                                res_pub = requests.put(f"{API_URL}/inmuebles/{p['id']}/publicar", params={"link_portal": link_p})
                                if res_pub.status_code == 200:
                                    st.success("¡Publicado!")
                                    st.rerun()
                            else:
                                st.warning("Debes poner el link del portal")
            else:
                st.info("No hay propiedades pendientes de publicar.")
        except:
            st.write("Esperando conexión...")