import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Archivo de datos
ARCHIVO_EXCEL = "datos_escolares.xlsx"

# --- Cargar datos del Excel ---
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        xls = pd.ExcelFile(ARCHIVO_EXCEL)
        df_ninos = pd.read_excel(xls, "Ninos")
        df_calificaciones = pd.read_excel(xls, "Calificaciones")
        df_tareas = pd.read_excel(xls, "Tareas")
        df_circulares = pd.read_excel(xls, "Circulares")
    except Exception as e:
        st.error("Error al cargar los datos: " + str(e))
        df_ninos = pd.DataFrame(columns=["id", "nombre", "foto_url"])
        df_calificaciones = pd.DataFrame(columns=["id_nino", "materia", "calificacion"])
        df_tareas = pd.DataFrame(columns=["id_nino", "tarea", "fecha_entrega"])
        df_circulares = pd.DataFrame(columns=["titulo", "contenido", "fecha"])
    return df_ninos, df_calificaciones, df_tareas, df_circulares

# --- Guardar datos en el Excel ---
def guardar_datos(df_ninos, df_calificaciones, df_tareas, df_circulares):
    with pd.ExcelWriter(ARCHIVO_EXCEL, engine="openpyxl", mode="w") as writer:
        df_ninos.to_excel(writer, sheet_name="Ninos", index=False)
        df_calificaciones.to_excel(writer, sheet_name="Calificaciones", index=False)
        df_tareas.to_excel(writer, sheet_name="Tareas", index=False)
        df_circulares.to_excel(writer, sheet_name="Circulares", index=False)

# --- Estado de sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None

# --- Login ---
def login():
    st.image("https://via.placeholder.com/250x80?text=Mi+Escuela", width=250)
    st.title("🔐 Iniciar Sesión")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario == "maestro" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.user_type = "maestro"
            st.rerun()
        elif usuario == "padre" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.user_type = "padre"
            st.session_state.hijos_padre = [1, 2]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# --- Logout ---
def logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.rerun()

# --- Tarjeta visual ---
import os

def card(nombre, id_nino, foto_archivo, content=""):
    st.markdown(f"""
    <div style='
        background: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    '>
        <h4>{nombre}</h4>
        <p>ID: {id_nino}</p>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar imagen local o placeholder
    if foto_archivo.startswith("http"):
        st.image(foto_archivo, width=120)
    else:
        ruta = os.path.join(os.getcwd(), foto_archivo)
        if os.path.exists(ruta):
            st.image(ruta, width=120)
        else:
            st.image("https://via.placeholder.com/120", width=120)
            st.caption("📷 Foto no encontrada")

    if content:
        st.markdown(content)
# --- App Principal ---
if not st.session_state.logged_in:
    login()
    st.stop()

# Cargar datos
df_ninos, df_calificaciones, df_tareas, df_circulares = cargar_datos()

# --- Menú lateral ---
with st.sidebar:
    if st.session_state.user_type == "maestro":
        seleccion = option_menu(
            "Menú Maestro",
            ["Inicio", "Niños", "Calificaciones", "Tareas", "Circulares", "Cerrar sesión"],
            icons=["house", "people-fill", "journal-check", "book", "megaphone", "box-arrow-left"],
            default_index=0
        )
    else:
        seleccion = option_menu(
            "Menú Padre",
            ["Mis hijos", "Calificaciones", "Tareas", "Circulares", "Cerrar sesión"],
            icons=["people", "journal-check", "book", "megaphone", "box-arrow-left"],
            default_index=0
        )

# --- Menú Maestro ---
if seleccion == "Cerrar sesión":
    logout()

elif seleccion in ["Inicio", "Mis hijos"]:
    st.title("👨‍👩‍👧‍👦 Mis Hijos" if st.session_state.user_type == "padre" else "🏠 Bienvenido Maestro")
    if st.session_state.user_type == "padre":
        ids = st.session_state.get("hijos_padre", [])
        hijos = df_ninos[df_ninos["id"].isin(ids)]
    else:
        hijos = df_ninos
    for _, row in hijos.iterrows():
        card(row["nombre"], row["id"], row["foto_url"])

elif seleccion == "Niños":
    st.title("👶 Gestión de Niños")
    st.dataframe(df_ninos)

    st.subheader("Agregar nuevo niño")
    with st.form("form_nino", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        foto = st.text_input("Foto URL (opcional)")
        if st.form_submit_button("Agregar Niño"):
            if nombre.strip():
                nuevo_id = df_ninos["id"].max() + 1 if not df_ninos.empty else 1
                df_ninos.loc[len(df_ninos)] = [nuevo_id, nombre.strip(), foto.strip()]
                guardar_datos(df_ninos, df_calificaciones, df_tareas, df_circulares)
                st.success(f"Niño '{nombre}' agregado.")
                st.rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

elif seleccion == "Calificaciones":
    st.title("📚 Calificaciones")
    if st.session_state.user_type == "padre":
        califs = df_calificaciones[df_calificaciones["id_nino"].isin(st.session_state["hijos_padre"])]
    else:
        califs = df_calificaciones
    st.dataframe(califs)

elif seleccion == "Tareas":
    st.title("📝 Tareas")
    if st.session_state.user_type == "padre":
        tareas = df_tareas[df_tareas["id_nino"].isin(st.session_state["hijos_padre"])]
    else:
        tareas = df_tareas
    st.dataframe(tareas)

elif seleccion == "Circulares":
    st.title("📢 Circulares")
    for _, row in df_circulares.iterrows():
        st.info(f"**{row['titulo']}**\n\n{row['contenido']}")
