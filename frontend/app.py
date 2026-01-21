import streamlit as st
import requests
import pandas as pd

# --- CONFIGURACIÓN ---
# Reemplaza con tu URL de Render (asegúrate de que no termine en /)
API_URL = "https://cadema-base.onrender.com"

st.set_page_config(page_title="Gestión Inmobiliaria Cadema", layout="wide")

st.title("🏠 Sistema de Gestión Inmobiliaria")

# --- FUNCIONES PARA LA API ---
def obtener_inmuebles():
    try:
        response = requests.get(f"{API_URL}/inmuebles/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

def guardar_inmueble(direccion, precio):
    try:
        # Enviamos los datos como parámetros según definimos en main.py
        params = {"direccion": direccion, "precio": precio, "estado": "Publicado"}
        response = requests.post(f"{API_URL}/inmuebles/", params=params)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- LÓGICA DE SESIÓN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None

if not st.session_state['logged_in']:
    with st.form("login"):
        st.subheader("Iniciar Sesión")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            # Login temporal (Luego lo haremos con la DB de usuarios)
            if user == "admin" and password == "1234":
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()
            elif user == "agente" and password == "agente123":
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'agente'
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL ---
    st.sidebar.success(f"Conectado como: {st.session_state['user_role'].upper()}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    tab1, tab2 = st.tabs(["📊 Listado de Propiedades", "➕ Cargar Propiedad"])

    with tab1:
        st.subheader("Inventario de Inmuebles")
        datos = obtener_inmuebles()
        
        if datos:
            # Convertimos la lista de la API en una tabla de Pandas
            df = pd.DataFrame(datos)
            # Reordenamos o limpiamos columnas si es necesario
            st.dataframe(df, use_container_width=True)
            
            # Botón para refrescar datos
            if st.button("🔄 Actualizar Tabla"):
                st.rerun()
        else:
            st.info("No hay inmuebles registrados o la base de datos está vacía.")

    with tab2:
        if st.session_state['user_role'] in ['admin', 'agente']:
            st.subheader("Registrar Nuevo Inmueble")
            with st.form("nueva_prop", clear_on_submit=True):
                dir_input = st.text_input("Dirección Completa")
                pre_input = st.number_input("Precio (USD)", min_value=0, step=500)
                
                enviar = st.form_submit_button("Guardar Propiedad")
                
                if enviar:
                    if dir_input:
                        exito = guardar_inmueble(dir_input, pre_input)
                        if exito:
                            st.success(f"✅ Inmueble en {dir_input} guardado correctamente.")
                            # No hace falta rerun aquí porque clear_on_submit limpia el form
                        else:
                            st.error("Hubo un problema al guardar en la nube.")
                    else:
                        st.warning("La dirección es obligatoria.")
        else:
            st.warning("⚠️ Tu rol de 'Visor' no permite cargar nuevas propiedades.")