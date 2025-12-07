import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NICO-ESCHER", layout="centered")

# --- ESTILOS CSS (UI MÓVIL MEJORADA) ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { 
        font-family: 'Garamond', 'Times New Roman', serif; 
        font-weight: 800; color: #222; text-align: center; margin-bottom: 0px;
    }
    .subtitle {
        text-align: center; color: #555; font-style: italic; font-family: serif; margin-bottom: 20px;
    }
    .streamlit-expanderHeader {
        background-color: #eaddca; /* Color pergamino/arena */
        border: 2px solid #5b432c; /* Marrón sepia */
        border-radius: 8px; font-weight: bold; color: #333;
    }
    .streamlit-expanderContent {
        border: 2px solid #5b432c; border-top: none;
        border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;
        background-color: #fffaf0;
    }
    div.stButton > button { 
        width: 100%; border: 3px solid #5b432c; border-radius: 8px;
        font-weight: 800; font-size: 16px; background-color: #eaddca; color: #333; 
        padding: 15px 0px; transition: all 0.2s;
        box-shadow: 4px 4px 0px #5b432c;
    }
    div.stButton > button:hover {
        transform: translate(-2px, -2px); box-shadow: 6px 6px 0px #5b432c;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Generador de Teselados Escherianos</p>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.expander("🎛️ CONTROLES DE METAMORFOSIS", expanded=True):
    st.write("### 1. El Motivo (La Pieza)")
    motif_type = st.selectbox("Elige tu criatura:", ["Peces Entrelazados", "Mariposas Geométricas", "Lagartos (Reptiles)"])
    
    st.write("### 2. La Dualidad (Colores)")
    st.caption("El efecto Escher funciona mejor con alto contraste entre dos colores.")
    col1, col2 = st.columns(2)
    with col1: c_figura = st.color_picker("Color Figura A", "#2C3E50") # Azul oscuro sepia
    with col2: c_fondo = st.color_picker("Color Figura B (Fondo)", "#EADDCA") # Crema claro

    st.write("### 3. El Infinito (Tamaño)")
    grid_size = st.select_slider("Repeticiones", options=[4, 6, 8, 12, 16], value=8)

    st.markdown("---")
    if 'seed_escher' not in st.session_state: st.session_state.seed_escher = 0
    if st.button("🎲 ¡TESELAR EL PLANO!"):
        st.session_state.seed_escher += 1

# --- GEOMETRÍA SAGRADA: DEFINICIÓN DE RUTAS (PATHS) ---
# Estos son polígonos vectoriales diseñados matemáticamente para encajar.

def get_escher_path(motif_name):
    """Devuelve el objeto Path de Matplotlib para el motivo seleccionado."""
    vertices = []
    codes = []

    if motif_name == "Peces Entrelazados":
        # Un pez cuadrado diseñado para teselar por traslación simple.
        # Basado en deformar los lados de un cuadrado unitario.
        # La curva superior debe coincidir con la inferior, la izquierda con la derecha.
        verts = [
            (0.0, 0.0), (0.2, 0.1), (0.4, -0.1), (0.5, 0.0), # Cola a panza (borde inferior)
            (0.6, 0.2), (0.8, 0.1), (1.0, 0.3), # Panza a cabeza (borde derecho)
            (0.9, 0.5), (1.1, 0.7), (1.0, 1.0), # Cabeza (esquina sup der)
            (0.8, 0.9), (0.6, 1.1), (0.5, 1.0), # Lomo (borde superior - inverso del inferior)
            (0.4, 0.8), (0.2, 0.9), (0.0, 0.7), # Lomo a cola (borde izquierdo - inverso del derecho)
            (-0.1, 0.5), (0.1, 0.3), (0.0, 0.0)  # Cola (cierre)
        ]
        # Simplificamos a polígono para asegurar cierre en matplotlib
        vertices = verts + [(0.0, 0.0)]
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-1) + [Path.CLOSEPOLY]

    elif motif_name == "Mariposas Geométricas":
        # Basado en un triángulo que tesela por rotación de 60 grados (hexagonal).
        # Definimos una "cometa" que forma 1/6 de un hexágono.
        verts = [
            (0.0, 0.0), # Centro
            (0.5, 0.1), (0.8, 0.4), (1.0, 0.0), # Ala superior (borde 1)
            (0.8, -0.4), (0.5, -0.1), # Ala inferior (borde 2 - debe encajar con borde 1 rotado)
            (0.0, 0.0) # Volver al centro
        ]
        # Ajuste para que parezca mariposa: hacerla simétrica sobre su eje
        # Usaremos un rombo que tesela.
        verts = [
            (0.5, 0.0), (0.8, 0.3), (0.5, 0.8), (0.2, 0.3), (0.5, 0.0)
        ]
        # Mejor: una forma que rota 90 grados. "El Molinillo"
        verts = [
            (0,0), (0.5, -0.2), (1,0), (1.2, 0.5), (1,1), (0.5, 1.2), (0,1), (-0.2, 0.5), (0,0)
        ]
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-2) + [Path.CLOSEPOLY]
        
    elif motif_name == "Lagartos (Reptiles)":
        # El más complejo. Requiere rotación de 120º (teselado p3).
        # Aproximación poligonal de un lagarto que encaja en hexágonos.
        # Definimos los puntos clave de un hexágono deformado.
        # Centro en (0,0). Puntas del hexágono base aprox en radio 1.
        verts = [
            (0.0, 0.0), # Nariz (Centro de rotación 1)
            (0.3, 0.1), (0.5, 0.4), # Cabeza a pata delantera derecha
            (0.866, 0.5), # Pata delantera derecha (Vértice hexágono 1)
            (0.7, 0.7), (0.6, 0.9), # Cuerpo lateral derecho
            (0.0, 1.0), # Pata trasera derecha (Vértice hexágono 2)
            (-0.2, 0.8), (-0.1, 0.5), # Cola base
            (-0.5, 0.866), # Punta Cola (Vértice hexágono 3)
            (-0.4, 0.4), # Cuerpo izquierdo trasero
            (-0.866, 0.5), # Pata trasera izquierda (Vértice hexágono 4)
            (-0.6, 0.1), # Cuerpo lateral izquierdo
            (-0.866, -0.5), # Pata delantera izquierda (Vértice hexágono 5)
            (-0.4, -0.3), # Cuello izquierdo
            (0.0, -1.0), # Barbilla (Vértice hexágono 6 - debe encajar con pata trasera)
            (0.0, 0.0) # Cerrar en Nariz
        ]
        # Simplificación para asegurar teselado visual tipo p4 (cuadrado rotado)
        # Usaremos la clásica "T" deformada de Escher que rota 90º.
        verts = [
            (0,0), (0.4, 0.1), (0.5, 0.5), (0.9, 0.4), (1,1), # Borde inferior e izquierdo
            (0.6, 0.9), (0.5, 0.5), (0.1, 0.6), (0,0) # Borde superior y derecho (inversos)
        ]
        # Ajustamos para que sea una pieza única que se entrelaza
        verts = [
             (0.0, 0.0), (0.5, -0.15), (1.0, 0.0), # Base curva
             (1.15, 0.5), (1.0, 1.0), # Derecha curva
             (0.5, 1.15), (0.0, 1.0), # Arriba curva
             (-0.15, 0.5), (0.0, 0.0) # Izquierda curva
        ]
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-2) + [Path.CLOSEPOLY]

    return Path(vertices, codes)

# --- MOTOR DE RENDERIZADO ESCHER ---

def render_escher_tessellation(motif, size, c1, c2):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Color de fondo base (para los huecos si los hubiera, aunque no debería)
    fig.patch.set_facecolor(c2)
    
    path = get_escher_path(motif)
    
    # Margen para asegurar que se cubre todo el lienzo al rotar
    margin = 2 
    
    for row in range(-margin, size + margin):
        for col in range(-margin, size + margin):
            
            # --- Lógica de Teselado según el Motivo ---
            
            if motif == "Peces Entrelazados":
                # Teselado por Traslación (Grupo p1)
                # Simplemente movemos la pieza a la siguiente celda de la cuadrícula.
                # Alternamos colores tipo tablero de ajedrez para efecto figura/fondo.
                x, y = col, row
                color = c1 if (row + col) % 2 == 0 else c2
                
                patch = patches.PathPatch(path, facecolor=color, edgecolor=color, linewidth=0.5)
                # Traslación simple
                trans = transforms.Affine2D().translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)

            elif motif == "Mariposas Geométricas":
                # Teselado por Rotación 90º alternada (Grupo p4 o pgg)
                # Requiere girar la pieza según su posición en el tablero.
                x, y = col, row
                color = c1 if (row + col) % 2 == 0 else c2
                
                # Determinamos la rotación según la paridad de fila/columna
                rot_deg = 0
                if row % 2 == 0 and col % 2 == 1: rot_deg = 90
                elif row % 2 == 1 and col % 2 == 1: rot_deg = 180
                elif row % 2 == 1 and col % 2 == 0: rot_deg = 270
                
                patch = patches.PathPatch(path, facecolor=color, edgecolor='#333', linewidth=0.5)
                # Rotar alrededor del centro de la pieza (0.5, 0.5) y luego trasladar
                trans = transforms.Affine2D().rotate_deg_around(0.5, 0.5, rot_deg).translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)

            elif motif == "Lagartos (Reptiles)":
                # Teselado más complejo. Usaremos la pieza "burbuja" definida.
                # Encaja si se rota 90 grados alrededor de sus vértices.
                x, y = col, row
                color = c1 if (row + col) % 2 == 0 else c2

                # Patrón de rotación complejo para encaje p4g
                rot_deg = (row % 2 + col % 2) * 90
                if (row+col)%4 == 3: rot_deg = 270

                patch = patches.PathPatch(path, facecolor=color, zorder=2)
                # Transformación compleja: Rotar sobre sí mismo y colocar
                trans = transforms.Affine2D().rotate_deg(rot_deg).translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)


    # Establecer límites de visualización para hacer zoom en el centro del patrón
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    
    # Marco estilo grabado antiguo
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#5b432c', linewidth=8)
    
    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed_escher)

figura = render_escher_tessellation(motif_type, grid_size, c_figura, c_fondo)

# Mostrar y Descargar
st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#fcfcfc")
st.download_button(
    label="⬇️ Descargar Grabado en HD",
    data=buf.getvalue(),
    file_name="escher_kuki.png",
    mime="image/png"
)
