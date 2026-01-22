import streamlit as st
import requests
import pandas as pd
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import os

# --- CONFIGURACIÓN ---
API_URL = os.getenv("API_URL", "https://cadema-base.onrender.com")

st.set_page_config(
    page_title="Cadema - Gestión Inmobiliaria", 
    layout="wide",
    page_icon="🏠"
)

# --- FUNCIONES AUXILIARES ---

@st.cache_resource
def get_cookie_manager():
    """Inicializa el manejador de cookies una sola vez"""
    return stx.CookieManager()

def mostrar_estado(estado):
    """Muestra el estado con emoji y color"""
    estados_config = {
        "Tasación": {"emoji": "🟡", "color": "orange"},
        "Para Publicar": {"emoji": "🟠", "color": "blue"},
        "Publicado": {"emoji": "🟢", "color": "green"}
    }
    config = estados_config.get(estado, {"emoji": "⚪", "color": "gray"})
    return f"{config['emoji']} {estado}"

def hacer_request(metodo, endpoint, **kwargs):
    """Función centralizada para hacer requests con manejo de errores"""
    url = f"{API_URL}{endpoint}"
    try:
        if metodo == "GET":
            response = requests.get(url, timeout=10, **kwargs)
        elif metodo == "POST":
            response = requests.post(url, timeout=10, **kwargs)
        elif metodo == "PUT":
            response = requests.put(url, timeout=10, **kwargs)
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "⏱️ El servidor tardó demasiado en responder. Intenta nuevamente."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "🔌 No se pudo conectar al servidor. Verifica tu conexión."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "❌ Recurso no encontrado"}
        elif e.response.status_code == 400:
            detalle = e.response.json().get("detail", "Datos inválidos")
            return {"success": False, "error": f"⚠️ {detalle}"}
        else:
            return {"success": False, "error": f"❌ Error del servidor ({e.response.status_code})"}
    except Exception as e:
        return {"success": False, "error": f"❌ Error inesperado: {str(e)}"}

# --- INICIALIZACIÓN ---
cookie_manager = get_cookie_manager()

def login_user(user):
    """Guarda la sesión del usuario"""
    cookie_manager.set("usuario_cadema", user, expires_at=datetime.now() + timedelta(days=1))
    st.session_state['logged_in'] = True
    st.session_state['user'] = user

# Verificar cookie existente
user_cookie = cookie_manager.get("usuario_cadema")

if user_cookie:
    st.session_state['logged_in'] = True
    st.session_state['user'] = user_cookie
else:
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

# --- PANTALLA DE LOGIN ---
if not st.session_state['logged_in']:
    st.title("🏠 Sistema Cadema")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("🔑 Acceso al Sistema")
            
            with st.form("login_form"):
                user_input = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                pass_input = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    # TODO: Implementar validación real con hash de contraseñas
                    if user_input == "admin" and pass_input == "1234":
                        login_user(user_input)
                        st.success("✅ Ingreso exitoso")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
            
            st.info("💡 Usuario demo: admin / 1234")
else:
    # --- INTERFAZ PRINCIPAL ---
    
    # Encabezado
    st.title("🏠 Cadema - Sistema de Gestión Inmobiliaria")
    
    # Barra lateral
    with st.sidebar:
        st.success(f"👤 Sesión: **{st.session_state.get('user', 'Admin')}**")
        
        # Estadísticas rápidas
        st.subheader("📊 Resumen")
        resultado = hacer_request("GET", "/estadisticas/resumen")
        if resultado["success"]:
            stats = resultado["data"]
            st.metric("Total Inmuebles", stats["total_inmuebles"])
            for estado, cantidad in stats["por_estado"].items():
                st.metric(mostrar_estado(estado), cantidad)
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            cookie_manager.delete("usuario_cadema")
            st.session_state['logged_in'] = False
            st.session_state['user'] = None
            st.rerun()

    # --- TABS PRINCIPALES ---
    tab_lista, tab_tasar, tab_publicar, tab_buscar = st.tabs([
        "📊 Inventario", 
        "📝 Nueva Tasación", 
        "📢 Publicar",
        "🔍 Búsqueda"
    ])

    # --- TAB 1: INVENTARIO ---
    with tab_lista:
        st.subheader("Inventario General de Propiedades")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Actualizar", use_container_width=True):
                st.rerun()
        
        resultado = hacer_request("GET", "/inmuebles/")
        
        if resultado["success"]:
            datos = resultado["data"]
            if datos:
                df = pd.DataFrame(datos)
                
                # Formatear columnas
                df['estado_visual'] = df['estado'].apply(mostrar_estado)
                
                # Seleccionar y ordenar columnas para mostrar
                columnas_mostrar = ['id', 'estado_visual', 'ciudad', 'direccion', 
                                   'tipo_inmueble', 'valor_tasacion', 'valor_publicacion', 
                                   'fecha_tasacion', 'fecha_publicacion']
                
                df_display = df[[col for col in columnas_mostrar if col in df.columns]]
                
                st.dataframe(
                    df_display, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "estado_visual": "Estado",
                        "valor_tasacion": st.column_config.NumberColumn(
                            "Tasación (USD)",
                            format="$%.2f"
                        ),
                        "valor_publicacion": st.column_config.NumberColumn(
                            "Publicación (USD)",
                            format="$%.2f"
                        )
                    }
                )
                
                # Opción de descarga
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"inventario_cadema_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("📭 No hay propiedades registradas aún")
        else:
            st.error(resultado["error"])

    # --- TAB 2: NUEVA TASACIÓN ---
    with tab_tasar:
        st.subheader("Registrar Nueva Tasación")
        
        with st.form("form_tasacion", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                ciudad = st.selectbox(
                    "Ciudad *", 
                    ["Campana", "Zarate", "Escobar", "Los Cardales"],
                    index=0
                )
                segmento = st.selectbox(
                    "Segmento *", 
                    ["Ciudad", "Industria", "Emprendimiento"],
                    index=0
                )
                emprendimiento = st.text_input(
                    "Emprendimiento *",
                    placeholder="Ej: Barrio Cerrado Las Acacias"
                )
                direccion = st.text_input(
                    "Dirección / Nro Lote *",
                    placeholder="Ej: Lote 45 o Calle 123"
                )
                tipo = st.selectbox(
                    "Tipo de Inmueble *", 
                    ["Casa", "Departamento", "Lote", "Local", "Oficina"],
                    index=0
                )
            
            with col2:
                sup_c = st.number_input(
                    "Superficie Cubierta (m²) *", 
                    min_value=0.0,
                    step=0.1,
                    format="%.2f"
                )
                sup_t = st.number_input(
                    "Superficie Terreno (m²) *", 
                    min_value=0.0,
                    step=0.1,
                    format="%.2f"
                )
                valor_tas = st.number_input(
                    "Valor Tasación (USD) *", 
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f"
                )
                drive = st.text_input(
                    "Link Google Drive *",
                    placeholder="https://drive.google.com/..."
                )
            
            st.caption("* Campos obligatorios")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn2:
                submitted = st.form_submit_button("💾 Guardar Tasación", use_container_width=True)
            
            if submitted:
                # Validación básica
                if not all([ciudad, segmento, emprendimiento, direccion, tipo, drive]):
                    st.error("⚠️ Por favor completa todos los campos obligatorios")
                elif valor_tas <= 0:
                    st.error("⚠️ El valor de tasación debe ser mayor a 0")
                else:
                    payload = {
                        "ciudad": ciudad,
                        "segmento": segmento,
                        "emprendimiento": emprendimiento,
                        "tipo": tipo,
                        "direccion": direccion,
                        "sup_cubierta": sup_c,
                        "sup_terreno": sup_t,
                        "valor_tasacion": valor_tas,
                        "link_drive": drive
                    }
                    
                    resultado = hacer_request("POST", "/inmuebles/tasar", params=payload)
                    
                    if resultado["success"]:
                        st.success(f"✅ {resultado['data']['mensaje']}")
                        st.balloons()
                    else:
                        st.error(resultado["error"])

    # --- TAB 3: PUBLICACIÓN ---
    with tab_publicar:
        st.subheader("Gestión de Publicaciones")
        
        resultado = hacer_request("GET", "/inmuebles/")
        
        if resultado["success"]:
            # Filtrar los que están "Para Publicar"
            pendientes = [i for i in resultado["data"] if i['estado'] == "Para Publicar"]
            
            if pendientes:
                st.info(f"📋 Hay {len(pendientes)} propiedades pendientes de publicación")
                
                for prop in pendientes:
                    with st.expander(f"📌 {prop['direccion']} - {prop['ciudad']} (${prop.get('valor_publicacion', 'N/A'):,.2f})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Detalles:**")
                            st.write(f"- Tipo: {prop['tipo_inmueble']}")
                            st.write(f"- Emprendimiento: {prop['emprendimiento']}")
                            st.write(f"- Sup. Cubierta: {prop['sup_cubierta']} m²")
                            st.write(f"- Sup. Terreno: {prop['sup_terreno']} m²")
                        
                        with col2:
                            link_portal = st.text_input(
                                "Link del Portal Inmobiliario",
                                key=f"link_{prop['id']}",
                                placeholder="https://tokko.com/... o https://zonaprop.com/..."
                            )
                            
                            if st.button("✅ Confirmar Publicación", key=f"btn_{prop['id']}"):
                                if not link_portal or link_portal.strip() == "":
                                    st.error("⚠️ Debes ingresar el link del portal")
                                else:
                                    resultado_pub = hacer_request(
                                        "PUT", 
                                        f"/inmuebles/{prop['id']}/publicar",
                                        params={"link_portal": link_portal}
                                    )
                                    
                                    if resultado_pub["success"]:
                                        st.success("✅ Propiedad publicada exitosamente")
                                        st.rerun()
                                    else:
                                        st.error(resultado_pub["error"])
            else:
                st.success("✨ No hay propiedades pendientes de publicación")
        else:
            st.error(resultado["error"])

    # --- TAB 4: BÚSQUEDA AVANZADA ---
    with tab_buscar:
        st.subheader("🔍 Búsqueda Avanzada")
        
        with st.form("form_busqueda"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ciudad_busq = st.selectbox(
                    "Ciudad",
                    ["Todas", "Campana", "Zarate", "Escobar", "Los Cardales"]
                )
                estado_busq = st.selectbox(
                    "Estado",
                    ["Todos", "Tasación", "Para Publicar", "Publicado"]
                )
            
            with col2:
                precio_min = st.number_input(
                    "Precio Mínimo (USD)",
                    min_value=0.0,
                    step=10000.0
                )
            
            with col3:
                precio_max = st.number_input(
                    "Precio Máximo (USD)",
                    min_value=0.0,
                    step=10000.0
                )
            
            buscar = st.form_submit_button("🔍 Buscar", use_container_width=True)
            
            if buscar:
                params = {}
                if ciudad_busq != "Todas":
                    params["ciudad"] = ciudad_busq
                if estado_busq != "Todos":
                    params["estado"] = estado_busq
                if precio_min > 0:
                    params["precio_min"] = precio_min
                if precio_max > 0:
                    params["precio_max"] = precio_max
                
                resultado = hacer_request("GET", "/inmuebles/buscar", params=params)
                
                if resultado["success"]:
                    datos = resultado["data"]
                    if datos:
                        st.success(f"✅ Se encontraron {len(datos)} resultados")
                        df = pd.DataFrame(datos)
                        df['estado_visual'] = df['estado'].apply(mostrar_estado)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No se encontraron resultados con esos criterios")
                else:
                    st.error(resultado["error"])