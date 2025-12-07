import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Azulejos", layout="centered")

st.title("Generador de Murales Geométricos 🎨")
st.write("Inspirado en la azulejería portuguesa y patrones geométricos. Cada diseño es único.")

# --- LÓGICA DEL MOTOR (Igual que antes) ---

PALETA_PORTUGUESA = [
    "#F2ECCE", "#B83328", "#2C5490", "#D89C37", 
    "#3A7D44", "#2A2A2A", "#C75B24", "#6B3A6B"
]

def generar_semilla_aleatoria(tamano_semilla, n_colores):
    semilla = []
    for _ in range(tamano_semilla):
        fila = []
        for _ in range(tamano_semilla):
            c1 = random.randint(0, n_colores - 1)
            c2 = random.randint(0, n_colores - 1)
            tipo = random.choices([0, 1, 2], weights=[20, 40, 40], k=1)[0]
            fila.append({'c1': c1, 'c2': c2, 'tipo': tipo})
        semilla.append(fila)
    return semilla

def reflejar_patron(semilla):
    filas_semilla = len(semilla)
    tamano_total = filas_semilla * 2
    patron_completo = [[None for _ in range(tamano_total)] for _ in range(tamano_total)]

    for r in range(filas_semilla):
        for c in range(filas_semilla):
            celda = semilla[r][c]
            # 1. Original
            patron_completo[r][c] = celda
            # 2. Reflejo Horizontal
            celda_hor = celda.copy()
            if celda['tipo'] == 1: celda_hor['tipo'] = 2
            elif celda['tipo'] == 2: celda_hor['tipo'] = 1
            patron_completo[r][tamano_total - 1 - c] = celda_hor
            # 3. Reflejo Vertical
            celda_ver = celda.copy()
            if celda['tipo'] == 1: celda_ver['tipo'] = 2
            elif celda['tipo'] == 2: celda_ver['tipo'] = 1
            patron_completo[tamano_total - 1 - r][c] = celda_ver
            # 4. Reflejo Doble
            patron_completo[tamano_total - 1 - r][tamano_total - 1 - c] = celda
    return patron_completo

def dibujar_figura(patron_datos, colores_activos):
    N = len(patron_datos)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.add_patch(patches.Rectangle((0,0), N, N, color=PALETA_PORTUGUESA[0]))

    for r in range(N):
        for c in range(N):
            datos = patron_datos[r][c]
            y_pos = N - 1 - r
            x_pos = c
            color1 = colores_activos[datos['c1']]
            color2 = colores_activos[datos['c2']]
            tipo = datos['tipo']

            if tipo == 0: 
                ax.add_patch(patches.Rectangle((x_pos, y_pos), 1, 1, color=color1))
                if datos['c1'] != datos['c2']:
                     ax.add_patch(patches.Rectangle((x_pos+0.25, y_pos+0.25), 0.5, 0.5, color=color2))
            elif tipo == 1: 
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos, y_pos+1), (x_pos+1, y_pos+1)], color=color1))
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos+1, y_pos), (x_pos+1, y_pos+1)], color=color2))
            elif tipo == 2: 
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos, y_pos+1), (x_pos+1, y_pos)], color=color1))
                ax.add_patch(patches.Polygon([(x_pos, y_pos+1), (x_pos+1, y_pos+1), (x_pos+1, y_pos)], color=color2))

    # Rejilla
    for k in range(N + 1):
        ax.plot([0, N], [k, k], color='#444444', linewidth=0.5)
        ax.plot([k, k], [0, N], color='#444444', linewidth=0.5)
    
    # Marco
    ax.plot([0, N, N, 0, 0], [0, 0, N, N, 0], color='#2A2A2A', linewidth=3)
    
    return fig

# --- INTERFAZ DE USUARIO (SIDEBAR) ---

st.sidebar.header("Configuración")
tamano = st.sidebar.slider("Tamaño del Grid", 4, 16, 8, step=2)
num_colores = st.sidebar.slider("Número de Colores", 2, 8, 5)

# Botón de generar (Usamos Session State para que no se borre al cambiar sliders)
if 'patron' not in st.session_state:
    st.session_state.trigger = 0

if st.sidebar.button("🎲 Generar Nuevo Patrón"):
    st.session_state.trigger += 1

# --- GENERACIÓN Y VISUALIZACIÓN ---

# Usamos el número aleatorio como semilla para que sea reproducible
colores_activos = PALETA_PORTUGUESA[:num_colores]
tamano_semilla = tamano // 2

# Generamos
semilla = generar_semilla_aleatoria(tamano_semilla, num_colores)
patron = reflejar_patron(semilla)
figura = dibujar_figura(patron, colores_activos)

# Mostramos en la web
st.pyplot(figura)

st.markdown("---")
st.caption("Creado con Python y Streamlit")