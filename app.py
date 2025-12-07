import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACION ---
st.set_page_config(page_title="NICOART SYSTEMIC", layout="centered")

# --- ESTILOS CSS (TECH-NOIR / SIN EMOJIS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #f0f0f0; font-family: 'JetBrains Mono', monospace; color: #111; }
    
    h1 { 
        font-weight: 700; letter-spacing: -2px; color: #000; 
        text-align: center; text-transform: uppercase; font-size: 3rem; margin: 0; 
    }
    .author { 
        text-align: center; color: #666; font-size: 0.7em; 
        letter-spacing: 2px; margin-bottom: 40px; text-transform: uppercase;
    }
    
    /* Panel de Control */
    .streamlit-expanderHeader { 
        background: #fff; border: 1px solid #000; color: #000; 
        font-weight: 700; border-radius: 0px; font-family: 'JetBrains Mono', monospace;
    }
    .streamlit-expanderContent { 
        border: 1px solid #000; border-top: 0; background: #fff; padding: 20px; 
    }
    
    /* Boton */
    div.stButton > button { 
        width: 100%; background: #000; color: #fff; border: none; border-radius: 0px; 
        font-weight: 700; font-size: 16px; padding: 20px; letter-spacing: 2px;
        transition: all 0.2s; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;
    }
    div.stButton > button:hover { 
        background: #333; transform: translateY(-2px); 
    }
    
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; max-width: 800px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>NICOART</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>Systemic Pattern Generator</p>", unsafe_allow_html=True)

# --- PALETAS ---
PALETAS = {
    "AMARILLO & NEGRO": ["#FFD700", "#000000"], 
    "CELTA ROJO": ["#F2ECCE", "#D92B2B", "#111111", "#E6AF2E"],
    "BAUHAUS": ["#F0F0F0", "#111111", "#D92B2B", "#1A4780", "#E6AF2E"],
    "MATRIX": ["#000000", "#00FF41", "#003B00", "#0D0208"],
    "QUILT VINTAGE": ["#F0EAD6", "#3B2518", "#E87A25", "#8C4926"],
    "OCEANICO": ["#001219", "#94D2BD", "#0A9396", "#005F73"],
}

# --- CONTROLES ---
with st.expander("SISTEMA DE CONTROL", expanded=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        p_name = st.selectbox("PALETA", list(PALETAS.keys()), label_visibility="collapsed")
        paleta = PALETAS[p_name]
        cols = st.columns(len(paleta))
        for i, c in enumerate(cols):
            c.markdown(f"<div style='background:{paleta[i]};height:10px;width:100%'></div>", unsafe_allow_html=True)
    with c2:
        # Selector de motor
        motor = st.selectbox("ALGORITMO", ["Nudos Procedurales (Infinito)", "Geometria Modular (Quilt)"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        grid_size = st.select_slider("RESOLUCION DE RETICULA", options=[4, 6, 8, 12, 16, 20], value=8)
    with c4:
        if motor == "Nudos Procedurales (Infinito)":
            # Control de entropía para los nudos
            caos = st.slider("COMPLEJIDAD DE TRAMA", 0.0, 1.0, 0.6)
        else:
            modo_geo = st.selectbox("PATRON", ["Secuencia Logica", "Super-Modulo 4x4"])

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("EJECUTAR GENERACION"): st.session_state.seed += 1

# --- ALFABETO VISUAL PARA NUDOS (TRUCHET TILES) ---

def draw_proc_tile(ax, x, y, type, rot, c_bg, c_tape, c_out):
    """
    Dibuja una pieza del nudo basada en su tipo logico.
    """
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    w_tape = 0.35 # Ancho cinta
    w_border = 0.05 # Ancho borde
    
    def p(patch): 
        patch.set_antialiased(False) # Bordes duros
        patch.set_linewidth(0)
        ax.add_patch(patch)

    # 1. Fondo
    p(patches.Rectangle((x, y), 1, 1, color=c_bg))

    # --- GEOMETRIA ---
    patches_list = []
    
    if type == 'cross':
        # Cruce (+)
        # Borde Vertical
        patches_list.append(patches.Rectangle((x + 0.5 - w_tape/2 - w_border, y), w_tape + w_border*2, 1, color=c_out))
        # Cinta Vertical
        patches_list.append(patches.Rectangle((x + 0.5 - w_tape/2, y), w_tape, 1, color=c_tape))
        
        # Borde Horizontal (Cruce)
        patches_list.append(patches.Rectangle((x, y + 0.5 - w_tape/2 - w_border), 1, w_tape + w_border*2, color=c_out))
        # Cinta Horizontal
        patches_list.append(patches.Rectangle((x, y + 0.5 - w_tape/2), 1, w_tape, color=c_tape))

    elif type == 'arc_dual':
        # Dos curvas )(
        # Bordes
        patches_list.append(patches.Wedge((x, y), 0.5 + w_tape/2 + w_border, 0, 90, width=w_tape + w_border*2, color=c_out))
        patches_list.append(patches.Wedge((x+1, y+1), 0.5 + w_tape/2 + w_border, 180, 270, width=w_tape + w_border*2, color=c_out))
        # Cintas
        patches_list.append(patches.Wedge((x, y), 0.5 + w_tape/2, 0, 90, width=w_tape, color=c_tape))
        patches_list.append(patches.Wedge((x+1, y+1), 0.5 + w_tape/2, 180, 270, width=w_tape, color=c_tape))

    # Dibujar
    for patch in patches_list:
        patch.set_transform(tr)
        p(patch)

def draw_geo_tile(ax, x, y, type, rot, c_main, c_acc):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    def p(patch): patch.set_antialiased(False); patch.set_linewidth(0); ax.add_patch(patch)
    
    # Fondo blanco siempre para geometria
    p(patches.Rectangle((x, y), 1, 1, color='#FFFFFF'))
    
    if type == 'triangle':
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        poly.set_transform(tr); p(poly)
    elif type == 'quarter':
        w = patches.Wedge((x, y), 1, 0, 90, color=c_main)
        w.set_transform(tr); p(w)
    elif type == 'circle':
        p(patches.Circle((x+0.5, y+0.5), 0.4, color=c_main))
    elif type == 'full':
        p(patches.Rectangle((x, y), 1, 1, color=c_main))
    elif type == 'strip':
        r = patches.Rectangle((x, y+0.25), 1, 0.5, color=c_main)
        r.set_transform(tr); p(r)

# --- ALGORITMOS GENERATIVOS ---

def generate_knot_grid(size, entropy):
    """
    Algoritmo de 'Romper la Reticula'.
    Empieza con todo cruces y rompe aleatoriamente para crear curvas.
    Garantiza continuidad perfecta.
    """
    rng = random.Random(st.session_state.seed)
    
    # 0 = Cross (+), 1 = Arc tipo 1 )(, 2 = Arc tipo 2 (arriba/abajo)
    grid = np.zeros((size, size), dtype=int) 
    
    for r in range(size):
        for c in range(size):
            if rng.random() < entropy:
                # Romper el cruce. Elegir orientacion de la curva
                grid[r][c] = rng.choice([1, 2])
            else:
                # Mantener cruce
                grid[r][c] = 0
                
    return grid

def generate_geo_grid(size, palette, mode):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    shapes = ['triangle', 'quarter', 'circle', 'strip']
    
    if mode == "Super-Modulo 4x4":
        # Generar un bloque maestro y repetirlo
        block = [[None]*4 for _ in range(4)]
        # Definir tema del bloque
        theme_shape = rng.choice(shapes)
        c1 = rng.choice(palette)
        c2 = rng.choice([c for c in palette if c!=c1] or [c1])
        
        for r in range(4):
            for c in range(4):
                # Logica simetrica simple para el bloque
                rot = 0
                # Si es triangulo/cuarto, orientar al centro del 4x4
                if r < 2 and c < 2: rot = 0
                elif r < 2: rot = 3
                elif c < 2: rot = 1
                else: rot = 2
                
                block[r][c] = {'type': theme_shape, 'rot': rot, 'c1': c1, 'c2': c2}
        
        for r in range(size):
            for c in range(size):
                grid[r][c] = block[r%4][c%4]
                
    else: # Secuencia Logica
        c1 = rng.choice(palette)
        c2 = rng.choice([c for c in palette if c!=c1] or [c1])
        shape = rng.choice(shapes)
        
        for r in range(size):
            for c in range(size):
                # Patron diagonal
                rot = (r + c) % 4
                is_alt = ((r//2) + (c//2)) % 2 == 0
                color = c1 if is_alt else c2
                grid[r][c] = {'type': shape, 'rot': rot, 'c1': color, 'c2': '#FFF'}

    return grid

# --- RENDERIZADO ---

def render_art(grid, size, palette, motor):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    c_bg = palette[0]
    c_tape = palette[1]
    c_out = palette[2] if len(palette) > 2 else c_bg
    
    for r in range(size):
        for c in range(size):
            y_pos = size - 1 - r
            
            if motor == "Nudos Procedurales (Infinito)":
                val = grid[r][c]
                tile = 'cross'; rot = 0
                if val == 1: tile='arc_dual'; rot=0
                elif val == 2: tile='arc_dual'; rot=1
                
                draw_proc_tile(ax, c, y_pos, tile, rot, c_bg, c_tape, c_out)
                
            else:
                cell = grid[r][c]
                draw_geo_tile(ax, c, y_pos, cell['type'], cell['rot'], cell['c1'], cell['c2'])

    # Marco
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color=c_bg if motor=="Nudos..." else '#000', linewidth=8)
    
    return fig

# --- EJECUCION ---

if motor == "Nudos Procedurales (Infinito)":
    data_grid = generate_knot_grid(grid_size, caos if 'caos' in locals() else 0.6)
else:
    data_grid = generate_geo_grid(grid_size, paleta, modo_geo)

figura = render_art(data_grid, grid_size, paleta, motor)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor=paleta[0] if motor.startswith("Nudos") else "#FFFFFF")
st.download_button(label="DESCARGAR IMAGEN HD", data=buf.getvalue(), file_name="nicoart_systemic.png", mime="image/png")
