import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="NICOART QUANTUM", layout="centered")

# --- ESTILOS CSS (TECH-MINIMAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Inter:wght@300;600&display=swap');
    
    .stApp { background-color: #0e0e0e; font-family: 'Inter', sans-serif; color: #fff; }
    
    h1 { 
        font-family: 'Syncopate', sans-serif; font-weight: 700; letter-spacing: 2px; 
        color: #fff; text-align: center; text-transform: uppercase; font-size: 2.5rem; margin: 0; 
        text-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    .author { 
        text-align: center; color: #666; font-size: 0.7em; letter-spacing: 3px; 
        margin-bottom: 40px; text-transform: uppercase; 
    }
    
    /* Panel de Control Oscuro */
    .streamlit-expanderHeader { 
        background: #1a1a1a; border: 1px solid #333; color: #fff; 
        font-weight: 600; border-radius: 4px; font-family: 'Inter', sans-serif;
    }
    .streamlit-expanderContent { 
        border: 1px solid #333; border-top: 0; background: #111; padding: 20px; 
    }
    
    /* Selectores Dark Mode */
    div[data-baseweb="select"] > div { background-color: #222; color: #fff; border-color: #444; }
    
    /* Botón Quantum */
    div.stButton > button { 
        width: 100%; background: linear-gradient(45deg, #FFD700, #FFAA00); 
        color: #000; border: none; border-radius: 4px; 
        font-weight: 800; font-size: 16px; padding: 20px; letter-spacing: 2px;
        transition: all 0.3s; text-transform: uppercase; font-family: 'Syncopate', sans-serif;
    }
    div.stButton > button:hover { 
        transform: scale(1.02); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); 
    }
    
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; max-width: 800px; }
    
    /* Textos */
    p, label { color: #ccc !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>NICOART</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>Quantum Pattern Engine</p>", unsafe_allow_html=True)

# --- PALETAS PREMIUM ---
PALETAS = {
    "GOLD & ONYX": ["#FFD700", "#080808", "#1A1A1A", "#333333"], 
    "CELTIC RED": ["#F2ECCE", "#D92B2B", "#050505", "#E6AF2E"],
    "BAUHAUS DARK": ["#E5E5E5", "#111111", "#D92B2B", "#1A4780"],
    "NEON MATRIX": ["#000000", "#00FF41", "#003B00", "#0D0208"],
    "VINTAGE QUILT": ["#F0EAD6", "#3B2518", "#E87A25", "#8C4926"],
    "OCEANIC": ["#001219", "#94D2BD", "#0A9396", "#005F73"],
}

# --- CONTROLES ---
with st.expander("SYSTEM CONTROL", expanded=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        p_name = st.selectbox("PALETTE", list(PALETAS.keys()), label_visibility="collapsed")
        paleta = PALETAS[p_name]
        cols = st.columns(len(paleta))
        for i, c in enumerate(cols):
            c.markdown(f"<div style='background:{paleta[i]};height:8px;width:100%'></div>", unsafe_allow_html=True)
    with c2:
        # Estilo visual de la línea
        estilo_linea = st.selectbox("LINE STYLE", ["Cinta Plana (Flat)", "Tubular (3D)", "Outline (Borde)"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        # Esto controla el tamaño del Grid (8x8, 16x16)
        grid_size = st.select_slider("GRID RESOLUTION", options=[4, 6, 8, 12, 16, 20], value=8)
    with c4:
        # Esto controla cuánto se "rompe" la retícula para formar curvas
        # 0 = Todo cruces (Rejilla), 1 = Todo curvas (Círculos)
        caos = st.slider("ENTROPY (Curvature)", 0.0, 1.0, 0.6)

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("MUTATE PATTERN"): st.session_state.seed += 1

# --- MOTOR DE RENDERIZADO PROCEDURAL ---

def draw_proc_tile(ax, x, y, type, rot, c_bg, c_tape, c_out, style):
    """
    Dibuja una pieza del nudo basada en su tipo lógico.
    """
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    # Configuración de grosores según estilo
    w_tape = 0.35
    w_border = 0.05
    
    def p(patch): 
        patch.set_antialiased(False) # Sharp edges
        patch.set_linewidth(0)
        ax.add_patch(patch)

    # 1. Fondo
    p(patches.Rectangle((x, y), 1, 1, color=c_bg))

    # --- GEOMETRÍA DE LA CINTA ---
    patches_list = []
    
    if type == 'cross':
        # Cruce (+)
        # Pieza vertical (Abajo)
        patches_list.append(patches.Rectangle((x + 0.5 - w_tape/2, y), w_tape, 1, color=c_tape))
        # Pieza horizontal (Arriba)
        patches_list.append(patches.Rectangle((x, y + 0.5 - w_tape/2), 1, w_tape, color=c_tape))
        
        # Si es outline, añadimos bordes negros
        if style == "Outline (Borde)":
             # Borde Vertical
             patches_list.insert(0, patches.Rectangle((x + 0.5 - w_tape/2 - w_border, y), w_tape + w_border*2, 1, color=c_out))
             # Borde Horizontal (Cortado para efecto over/under)
             # Para simular cruce, pintamos el borde horizontal encima, pero dejando hueco?
             # Simplificación: Pintamos borde horizontal completo
             patches_list.insert(2, patches.Rectangle((x, y + 0.5 - w_tape/2 - w_border), 1, w_tape + w_border*2, color=c_out))

    elif type == 'arc_dual':
        # Dos curvas )(
        # Curva 1
        patches_list.append(patches.Wedge((x, y), 0.5 + w_tape/2, 0, 90, width=w_tape, color=c_tape))
        # Curva 2
        patches_list.append(patches.Wedge((x+1, y+1), 0.5 + w_tape/2, 180, 270, width=w_tape, color=c_tape))
        
        if style == "Outline (Borde)":
            # Bordes más gruesos detrás
            patches_list.insert(0, patches.Wedge((x, y), 0.5 + w_tape/2 + w_border, 0, 90, width=w_tape + w_border*2, color=c_out))
            patches_list.insert(2, patches.Wedge((x+1, y+1), 0.5 + w_tape/2 + w_border, 180, 270, width=w_tape + w_border*2, color=c_out))

    elif type == 'line':
        # Recta simple | (Usada en bordes)
        patches_list.append(patches.Rectangle((x + 0.5 - w_tape/2, y), w_tape, 1, color=c_tape))
        if style == "Outline (Borde)":
            patches_list.insert(0, patches.Rectangle((x + 0.5 - w_tape/2 - w_border, y), w_tape + w_border*2, 1, color=c_out))

    # Aplicar transformaciones y dibujar
    for patch in patches_list:
        patch.set_transform(tr)
        p(patch)
        
    # Efecto 3D / Tubular (Sombra interior)
    if style == "Tubular (3D)" and type in ['cross', 'arc_dual', 'line']:
        # Dibujar una línea más fina y clara en el centro
        w_inner = w_tape * 0.2
        c_highlight = "#FFFFFF" if c_tape != "#FFFFFF" else "#AAAAAA"
        alpha = 0.3
        
        h_patches = []
        if type == 'cross':
            h_patches.append(patches.Rectangle((x + 0.5 - w_inner/2, y), w_inner, 1, color=c_highlight, alpha=alpha))
            h_patches.append(patches.Rectangle((x, y + 0.5 - w_inner/2), 1, w_inner, color=c_highlight, alpha=alpha))
        elif type == 'arc_dual':
            h_patches.append(patches.Wedge((x, y), 0.5 + w_inner/2, 0, 90, width=w_inner, color=c_highlight, alpha=alpha))
            h_patches.append(patches.Wedge((x+1, y+1), 0.5 + w_inner/2, 180, 270, width=w_inner, color=c_highlight, alpha=alpha))
        
        for hp in h_patches:
            hp.set_transform(tr)
            p(hp)

# --- ALGORITMO PROCEDURAL "BREAK-GRID" ---

def generate_procedural_grid(size, entropy):
    """
    Genera un grid válido de nudos usando mutación estocástica.
    No usa bloques prefabricados. Genera un patrón ÚNICO cada vez.
    """
    rng = random.Random(st.session_state.seed)
    
    # 1. Empezar con una retícula "Perfecta" (Todo conectado)
    # 0 = Cross (+), 1 = Arc tipo 1 )(, 2 = Arc tipo 2 ︵︶
    grid = np.zeros((size, size), dtype=int) 
    
    # 2. Mutación: Romper la simetría
    # Iteramos por cada celda y decidimos si la "rompemos" (convertimos cruz en curva)
    # La entropía controla cuántas cruces sobreviven.
    
    for r in range(size):
        for c in range(size):
            if rng.random() < entropy:
                # Romper el cruce.
                # Elegir aleatoriamente la orientación de la curva (0 o 1)
                # 1 = Curvas verticales )(, 2 = Curvas horizontales ︵︶
                grid[r][c] = rng.choice([1, 2])
            else:
                # Mantener cruce
                grid[r][c] = 0
                
    # 3. Pulir Bordes (Opcional, para que parezca un objeto cerrado)
    # Forzar curvas en los bordes para cerrar el nudo
    for i in range(size):
        # Borde superior (Debe rebotar hacia abajo)
        # Borde izquierdo (Debe rebotar hacia derecha)
        # Esto es complejo en lógica simple, dejaremos que sea "infinito" (se corta)
        pass

    return grid

def render_art(grid, size, palette, style):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    # Colores
    c_bg = palette[0]
    c_tape = palette[1]
    c_out = palette[2] if len(palette) > 2 else c_bg
    if len(palette) > 3: c_tape_2 = palette[3] # Opcional para alternar cintas
    
    for r in range(size):
        for c in range(size):
            val = grid[r][c]
            
            # Mapear valor lógico a visual
            # Invertimos Y para coordenada visual
            y_pos = size - 1 - r
            
            tile_type = 'cross'
            rot = 0
            
            if val == 0: # Cross
                tile_type = 'cross'
                rot = 0
            elif val == 1: # Vertical Curves )(
                tile_type = 'arc_dual'
                rot = 0 # )( es rot 0 o 2
            elif val == 2: # Horizontal Curves ︵︶
                tile_type = 'arc_dual'
                rot = 1 # Girar 90 grados para tener horizontal
            
            # Variación de color por posición (Checkerboard sutil) para dar profundidad
            color_active = c_tape
            # if (r+c)%2 == 0 and len(palette) > 3: color_active = palette[3] 

            draw_proc_tile(ax, c, y_pos, tile_type, rot, c_bg, color_active, c_out, style)

    # Marco Exterior
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color=c_bg, linewidth=0) # Limpio
    
    return fig

# --- EJECUCIÓN ---

# Generar datos lógicos
logical_grid = generate_procedural_grid(grid_size, caos)

# Renderizar
figura = render_art(logical_grid, grid_size, paleta, estilo_linea)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor=paleta[0])
st.download_button(label="DOWNLOAD HD ARTWORK", data=buf.getvalue(), file_name="nicoart_quantum.png", mime="image/png")
