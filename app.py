import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Escher", layout="centered")

# --- ESTILOS CSS (UI MÓVIL MEJORADA - Estilo Grabado) ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { 
        font-family: 'Garamond', 'Times New Roman', serif; 
        font-weight: 800; 
        color: #222; 
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-style: italic;
        font-family: serif;
        margin-bottom: 20px;
    }

    /* ESTILO DEL PANEL DE CONTROL (EXPANDER) */
    .streamlit-expanderHeader {
        background-color: #eaddca; /* Color pergamino */
        border: 2px solid #5b432c; /* Marrón sepia */
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
        color: #333;
    }
    .streamlit-expanderContent {
        border: 2px solid #5b432c;
        border-top: none;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        background-color: #fffaf0;
        padding: 20px;
    }

    /* BOTONES */
    div.stButton > button { 
        width: 100%; 
        border: 3px solid #5b432c; 
        border-radius: 8px;
        font-weight: 800; 
        font-size: 16px;
        background-color: #eaddca; 
        color: #333; 
        padding: 15px 0px; /* Más alto para móvil */
        transition: all 0.2s;
        box-shadow: 4px 4px 0px #5b432c; /* Sombra dura */
    }
    div.stButton > button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #5b432c;
    }
    div.stButton > button:active {
        transform: translate(2px, 2px);
        box-shadow: 1px 1px 0px #5b432c;
        background-color: #d4c5b3;
    }
    
    /* Ajuste de columnas en móvil */
    [data-testid="column"] {
        min-width: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Generador de Teselados Escherianos</p>", unsafe_allow_html=True)

# --- PANEL DE CONTROL VISIBLE (EXPANDER) ---
with st.expander("🎛️ CONTROLES DE METAMORFOSIS (TÓCAME)", expanded=True):
    
    st.write("### 1. La Criatura")
    motif_type = st.selectbox("Elige el motivo:", ["Peces Entrelazados", "Mariposas Geométricas", "Lagartos (Reptiles)"])
    
    st.write("### 2. La Dualidad (Colores)")
    cols = st.columns(2)
    with cols[0]:
        c_figura = st.color_picker("Color Figura", "#2C3E50") # Azul oscuro sepia
    with cols[1]:
        c_fondo = st.color_picker("Color Fondo", "#EADDCA") # Crema claro

    st.write("### 3. El Infinito (Tamaño)")
    grid_size = st.select_slider("Repeticiones", options=[4, 6, 8, 12, 16], value=8)

    st.markdown("---")
    
    # Inicializar estado
    if 'seed_escher' not in st.session_state:
        st.session_state.seed_escher = 0

    # BOTÓN GRANDE
    if st.button("🎲 ¡TESELAR EL PLANO!"):
        st.session_state.seed_escher += 1

# --- GEOMETRÍA SAGRADA: DEFINICIÓN DE RUTAS (PATHS) ---
# Polígonos diseñados matemáticamente para encajar sin huecos.

def get_escher_path(motif_name):
    """Devuelve el objeto Path de Matplotlib para el motivo seleccionado."""
    vertices = []
    codes = []

    if motif_name == "Peces Entrelazados":
        # Pez que tesela por traslación (p1)
        verts = [
            (0.0, 0.0), (0.2, 0.1), (0.4, -0.1), (0.5, 0.0), # Cola a panza inferior
            (0.6, 0.2), (0.8, 0.1), (1.0, 0.3), # Panza a cabeza
            (0.9, 0.5), (1.1, 0.7), (1.0, 1.0), # Cabeza
            (0.8, 0.9), (0.6, 1.1), (0.5, 1.0), # Lomo superior (inverso del inferior)
            (0.4, 0.8), (0.2, 0.9), (0.0, 0.7), # Lomo a cola
            (-0.1, 0.5), (0.1, 0.3), (0.0, 0.0)  # Cierre cola
        ]
        vertices = verts + [(0.0, 0.0)]
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-1) + [Path.CLOSEPOLY]

    elif motif_name == "Mariposas Geométricas":
        # Basado en "El Molinillo" que rota 90 grados (p4)
        verts = [
            (0,0), (0.5, -0.2), (1,0), (1.2, 0.5), (1,1), (0.5, 1.2), (0,1), (-0.2, 0.5), (0,0)
        ]
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-2) + [Path.CLOSEPOLY]
        
    elif motif_name == "Lagartos (Reptiles)":
        # Pieza compleja que se entrelaza rotando (p4g aproximado)
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
    # Usamos DPI alto para que se vea bien en pantalla
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Color de fondo base
    fig.patch.set_facecolor(c2)
    
    path = get_escher_path(motif)
    margin = 1
    
    for row in range(-margin, size + margin):
        for col in range(-margin, size + margin):
            
            # Lógica de color alterno (tablero de ajedrez) para efecto figura/fondo
            color = c1 if (row + col) % 2 == 0 else c2
            
            if motif == "Peces Entrelazados":
                # Traslación simple
                x, y = col, row
                patch = patches.PathPatch(path, facecolor=color, edgecolor=color, linewidth=0.5)
                trans = transforms.Affine2D().translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)

            elif motif == "Mariposas Geométricas":
                # Rotación 90º alternada
                x, y = col, row
                rot_deg = 0
                if row % 2 == 0 and col % 2 == 1: rot_deg = 90
                elif row % 2 == 1 and col % 2 == 1: rot_deg = 180
                elif row % 2 == 1 and col % 2 == 0: rot_deg = 270
                
                patch = patches.PathPatch(path, facecolor=color, edgecolor='#333', linewidth=0.5)
                trans = transforms.Affine2D().rotate_deg_around(0.5, 0.5, rot_deg).translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)

            elif motif == "Lagartos (Reptiles)":
                # Rotación compleja
                x, y = col, row
                rot_deg = (row % 2 + col % 2) * 90
                if (row+col)%4 == 3: rot_deg = 270

                patch = patches.PathPatch(path, facecolor=color, zorder=2)
                trans = transforms.Affine2D().rotate_deg(rot_deg).translate(x, y) + ax.transData
                patch.set_transform(trans)
                ax.add_patch(patch)


    # Límites y marco
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#5b432c', linewidth=8)
    
    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed_escher)

figura = render_escher_tessellation(motif_type, grid_size, c_figura, c_fondo)

# Mostrar imagen
st.pyplot(figura)

# Botón de descarga HD
buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor=c_fondo)
st.download_button(
    label="⬇️ Descargar Grabado en HD",
    data=buf.getvalue(),
    file_name="escher_kuki.png",
    mime="image/png"
)
