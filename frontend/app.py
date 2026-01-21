# Aplicación de Streamlit (Login y Tablas)

import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Gestión Inmobiliaria", layout="wide")

st.title("🏠 Sistema de Gestión Inmobiliaria")

# --- SIMULACIÓN DE LOGIN (Luego lo conectaremos a la API) ---
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
            # Por ahora, un login de prueba
            if user == "admin" and password == "1234":
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    st.sidebar.success(f"Conectado como: {st.session_state['user_role']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- CONTENIDO SEGÚN ROL ---
    tab1, tab2 = st.tabs(["Listado", "Cargar Propiedad"])

    with tab1:
        st.write("Aquí verás la tabla de Excel convertida a Sistema.")
        # Aquí pediremos los datos a la API de FastAPI

    with tab2:
        if st.session_state['user_role'] == 'admin' or st.session_state['user_role'] == 'agente':
            st.subheader("Cargar nuevo inmueble")
            with st.form("nueva_prop"):
                dir = st.text_input("Dirección")
                pre = st.number_input("Precio", min_value=0)
                btn = st.form_submit_button("Guardar")
        else:
            st.warning("No tienes permisos para cargar propiedades. Solo lectura.")