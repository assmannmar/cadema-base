import streamlit as st
import requests
import pandas as pd
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
API_URL = "https://cadema-base.onrender.com"

st.set_page_config(page_title="Cadema - Gestión Inmobiliaria", layout="wide")

# Inicializar manejador de cookies (SIN @st.cache_resource)
cookie_manager = stx.CookieManager()

# --- LÓGICA DE LOGIN CON COOKIES ---
def login_user(user):
    # Guardamos la cookie por 1 día (86400 segundos)
    cookie_manager.set("usuario_cadema", user, expires_at=datetime.now() + timedelta(days=1))
    st.session_state['logged_in'] = True
    st.session_state['user'] = user

# Leer cookie al iniciar
user_cookie = cookie_manager.get("usuario_cadema")

if user_cookie:
    st.session_state['logged_in'] = True
    st.session_state['user'] = user_cookie
else:
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

# --- PANTALLA DE LOGIN ---
if not st.session_state['logged_in']:
    with st.container():
        st.subheader("🔑 Acceso al Sistema")
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user_input == "admin" and pass_input == "1234":
                login_user(user_input)
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL ---
    st.sidebar.success(f"Sesión activa: {st.session_state.get('user', 'Admin')}")
    if st.sidebar.button("Log out (Cerrar Sesión)"):
        cookie_manager.delete("usuario_cadema")
        st.session_state['logged_in'] = False
        st.rerun()

    # --- TABS DE TRABAJO (Tu flujo inmobiliario) ---
    tab_lista, tab_tasar, tab_mkt = st.tabs(["📊 Base Inmuebles", "📝 Nueva Tasación", "📢 Marketing"])

    # --- TAB 1: LISTADO GENERAL ---
    with tab_lista:
        st.subheader("Inventario General")
        try:
            res = requests.get(f"{API_URL}/inmuebles/", timeout=10)
            res.raise_for_status()
            datos = res.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ El servidor tardó demasiado en responder")
        except requests.exceptions.ConnectionError:
            st.error("🔌 No se pudo conectar al servidor")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Error del servidor: {e.response.status_code}")

    # --- TAB 2: REGISTRO DE TASACIÓN ---
    with tab_tasar:
        st.subheader("Registrar Nueva Tasación")
        with st.form("form_tasacion", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ciudad = st.selectbox("Ciudad", ["Campana", "Zarate", "Escobar", "Los Cardales"])
                segmento = st.selectbox("Segmento", ["Ciudad", "Industria", "Emprendimiento"])
                emprendimiento = st.text_input("Emprendimiento")
                direccion = st.text_input("Dirección / Nro Lote")
                tipo = st.selectbox("Tipo", ["Casa", "Departamento", "Lote", "Local"])
            with col2:
                sup_c = st.number_input("Sup. Cubierta (m2)", min_value=0.0)
                sup_t = st.number_input("Sup. Terreno (m2)", min_value=0.0)
                valor_tas = st.number_input("Valor Tasación (USD)", min_value=0.0)
                drive = st.text_input("Link Drive")
            
            if st.form_submit_button("Guardar Tasación"):
                payload = {
                    "ciudad": ciudad, "segmento": segmento, "emprendimiento": emprendimiento,
                    "tipo": tipo, "direccion": direccion, "sup_cubierta": sup_c,
                    "sup_terreno": sup_t, "valor_tasacion": valor_tas, "link_drive": drive
                }
                res = requests.post(f"{API_URL}/inmuebles/tasar", params=payload)
                if res.status_code == 200:
                    st.success("✅ Tasación guardada.")

    # --- TAB 3: MARKETING ---
    with tab_mkt:
        st.subheader("Pendientes de Publicación")
        try:
            res = requests.get(f"{API_URL}/inmuebles/")
            pendientes = [i for i in res.json() if i['estado'] == "Para Publicar"]
            if pendientes:
                for p in pendientes:
                    with st.expander(f"📌 {p['direccion']}"):
                        link_p = st.text_input("Link del Portal", key=f"lk_{p['id']}")
                        if st.button("Confirmar", key=f"bt_{p['id']}"):
                            requests.put(f"{API_URL}/inmuebles/{p['id']}/publicar", params={"link_portal": link_p})
                            st.rerun()
            else:
                st.info("Nada pendiente.")
        except:
            pass