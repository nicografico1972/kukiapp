import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="KUKIAPP, layout="centered")

st.title("KUKIAPP")
st.write("CREA PATRONES CON KUKIESTILO")

# --- PALETA DE COLORES VIBRANTE ---
PALETA_RICA = [
    "#E74C3C", # Rojo
    "#3498DB", # Azul
    "#F1C40F", # Amarillo
    "#2ECC71", # Verde
    "#9B59B6", # Morado
    "#1ABC9C", # Cian
    "#E67E22", # Naranja
    "#34495E", # Azul Oscuro
    "#FFFFFF", # Blanco
    "#BDC3C7", # Gris Claro
    "#7F8C8D", # Gris Medio
    "#000000"  # Negro
]

# --- FUNCIONES DE GENERACIÓN DE PATRONES ---
def crear_celda_aleatoria(n_colores):
    """Crea una celda con una forma aleatoria y colores aleatorios."""
    tipo_forma = random.choices(['cuadrado', 'triangulo_1', 'triangulo_2', 'estrella'], weights=[30, 30, 30, 10], k=1)[0]
    c1 = random.randint(0, n_colores - 1)
    c2 = random.randint(0, n_colores - 1)
    return {'tipo': tipo_forma, 'c1': c1, 'c2': c2}

def generar_semilla_rica(tamano_semilla, n_colores):
    """Genera una semilla con celdas aleatorias."""
    semilla = []
    for _ in range(tamano_semilla):
        fila = []
        for _ in range(tamano_semilla):
            fila.append(crear_celda_aleatoria(n_colores))
        semilla.append(fila)
    return semilla

def reflejar_patron_rico(semilla):
    """Refleja la semilla para crear un patrón simétrico más grande."""
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
            if celda['tipo'] == 'triangulo_1': celda_hor['tipo'] = 'triangulo_2'
            elif celda['tipo'] == 'triangulo_2': celda_hor['tipo'] = 'triangulo_1'
            patron_completo[r][tamano_total - 1 - c] = celda_hor
            # 3. Reflejo Vertical
            celda_ver = celda.copy()
            if celda['tipo'] == 'triangulo_1': celda_ver['tipo'] = 'triangulo_2'
            elif celda['tipo'] == 'triangulo_2': celda_ver['tipo'] = 'triangulo_1'
            patron_completo[tamano_total - 1 - r][c] = celda_ver
            # 4. Reflejo Doble
            patron_completo[tamano_total - 1 - r][tamano_total - 1 - c] = celda
    return patron_completo

# --- FUNCIÓN DE DIBUJO ---
def dibujar_patron_rico(patron_datos, colores_activos):
    """Dibuja el patrón con matplotlib."""
    N = len(patron_datos)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    # Fondo aleatorio de la paleta
    color_fondo = random.choice(colores_activos)
    ax.add_patch(patches.Rectangle((0,0), N, N, color=color_fondo))

    for r in range(N):
        for c in range(N):
            datos = patron_datos[r][c]
            y_pos = N - 1 - r
            x_pos = c
            color1 = colores_activos[datos['c1']]
            color2 = colores_activos[datos['c2']]
            tipo = datos['tipo']

            if tipo == 'cuadrado':
                ax.add_patch(patches.Rectangle((x_pos, y_pos), 1, 1, color=color1))
                if datos['c1'] != datos['c2']:
                     # Cuadrado interior más pequeño
                     ax.add_patch(patches.Rectangle((x_pos+0.2, y_pos+0.2), 0.6, 0.6, color=color2))
            elif tipo == 'triangulo_1': # Diagonal /
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos, y_pos+1), (x_pos+1, y_pos+1)], color=color1))
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos+1, y_pos), (x_pos+1, y_pos+1)], color=color2))
            elif tipo == 'triangulo_2': # Diagonal \
                ax.add_patch(patches.Polygon([(x_pos, y_pos), (x_pos, y_pos+1), (x_pos+1, y_pos)], color=color1))
                ax.add_patch(patches.Polygon([(x_pos, y_pos+1), (x_pos+1, y_pos+1), (x_pos+1, y_pos)], color=color2))
            elif tipo == 'estrella':
                # Dibujamos una estrella simple
                cx, cy = x_pos + 0.5, y_pos + 0.5
                radio_ext = 0.4
                radio_int = 0.2
                puntos = []
                for i in range(16): # 8 puntas
                    angulo = np.deg2rad(i * 360 / 16)
                    radio = radio_ext if i % 2 == 0 else radio_int
                    puntos.append((cx + radio * np.cos(angulo), cy + radio * np.sin(angulo)))
                ax.add_patch(patches.Polygon(puntos, color=color1))
                # Círculo central
                ax.add_patch(patches.Circle((cx, cy), radio_int/1.5, color=color2))

    # Rejilla
    for k in range(N + 1):
        ax.plot([0, N], [k, k], color='#2A2A2A', linewidth=0.5)
        ax.plot([k, k], [0, N], color='#2A2A2A', linewidth=0.5)
    
    # Marco
    ax.plot([0, N, N, 0, 0], [0, 0, N, N, 0], color='#000000', linewidth=3)
    
    return fig

# --- INTERFAZ DE USUARIO (SIDEBAR) ---

st.sidebar.header("Configuración")
tamano = st.sidebar.slider("Tamaño del Grid", 4, 16, 8, step=2)
num_colores = st.sidebar.slider("Número de Colores", 2, len(PALETA_RICA), 6)

# Botón de generar
if 'patron' not in st.session_state:
    st.session_state.trigger = 0

if st.sidebar.button("🎲 Generar Nuevo Patrón"):
    st.session_state.trigger += 1

# --- GENERACIÓN Y VISUALIZACIÓN ---

# Usamos el número aleatorio como semilla para que sea reproducible
colores_activos = PALETA_RICA[:num_colores]
tamano_semilla = tamano // 2

# Generamos
semilla = generar_semilla_rica(tamano_semilla, num_colores)
patron = reflejar_patron_rico(semilla)
figura = dibujar_patron_rico(patron, colores_activos)

# Mostramos en la web
st.pyplot(figura)

st.markdown("---")
st.caption("Creado con Python y Streamlit")
