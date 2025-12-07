import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="NICOART", layout="centered")

# --- ESTILOS CSS (MINIMALISMO TÉCNICO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #ffffff; font-family: 'JetBrains Mono', monospace; }
    
    h1 { 
        font-weight: 700; letter-spacing: -2px; color: #000; 
        text-align: center; text-transform: uppercase; font-size: 2.5rem; margin: 0; 
    }
    .author { 
        text-align: center; color: #666; font-size: 0.7em; 
        letter-spacing: 1px; margin-bottom: 40px; text-transform: uppercase;
    }
    
    /* Panel de Control */
    .streamlit-expanderHeader { 
        background: #f4f4f4; border: 1px solid #000; color: #000; 
        font-weight: 700; border-radius: 0px; font-family: 'JetBrains Mono', monospace;
    }
    .streamlit-expanderContent { 
        border: 1px solid #000; border-top: 0; background: #fff; padding: 20px; 
    }
    
    /* Selectores */
    div[data-baseweb="select"] > div { border-radius: 0px; border: 1px solid #000; }
    
    /* Botón */
    div.stButton > button { 
        width: 100%; background: #000; color: #fff; border: none; border-radius: 0px; 
        font-weight: 700; font-size: 16px; padding: 18px; letter-spacing: 1px;
        transition: all 0.2s; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;
    }
    div.stButton > button:hover { 
        background: #333; color: #fff; transform: translateY(-2px); 
    }
    
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; max-width: 800px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>NICOART</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>Algoritmo de Diseño Generativo</p>", unsafe_allow_html=True)

# --- PALETAS DE ALTO CONTRASTE ---
PALETAS = {
    "AMARILLO & NEGRO": ["#FFD700", "#000000"], 
    "BAUHAUS": ["#F0F0F0", "#111111", "#D92B2B", "#1A4780", "#E6AF2E"],
    "TIERRA": ["#F2ECCE", "#8C2727", "#D9A404", "#2E5936", "#1A4780"],
    "ARQUITECTO": ["#FFFFFF", "#000000", "#333333", "#999999", "#E5E5E5"],
    "ATLANTICO": ["#F0F8FF", "#001219", "#005F73", "#0A9396", "#94D2BD"],
    "POP 70s": ["#FFF1E6", "#E85D04", "#F48C06", "#FAA307", "#370617"],
    "JARDIN ZEN": ["#F7F7F7", "#2D3436", "#636E72", "#55EFC4", "#00B894"]
}

# --- CONTROLES ---
with st.expander("PANEL DE CONTROL", expanded=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        p_name = st.selectbox("PALETA", list(PALETAS.keys()), label_visibility="collapsed")
        paleta = PALETAS[p_name]
        cols = st.columns(len(paleta))
        for i, c in enumerate(cols):
            c.markdown(f"<div style='background:{paleta[i]};height:12px;width:100%'></div>", unsafe_allow_html=True)
    with c2:
        familia = st.selectbox("FAMILIA", ["Mezcla", "Diagonales", "Curvas", "Ortogonal"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        # Limitamos la resolución para asegurar que se vean las figuras
        grid_size = st.select_slider("RESOLUCION", options=[4, 8, 12, 16], value=8)
    with c4:
        modo = st.selectbox("MODO", ["Super-Modulos", "Tejido Infinito"])

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("GENERAR DISEÑO"): st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO (UNICODE) ---
# Tipos: full, circle, tri_half, arc_corner, arc_ring, strip_center, checker_4

def draw_tile(ax, x, y, type, rot, c1, c2):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def p(patch): 
        patch.set_antialiased(False)
        patch.set_linewidth(0)
        ax.add_patch(patch)

    # Fondo base (c2)
    p(patches.Rectangle((x, y), 1, 1, color=c2))

    if type == 'full': 
        p(patches.Rectangle((x, y), 1, 1, color=c1))
        
    elif type == 'circle': # CÍRCULO SÓLIDO RESTAURADO
        p(patches.Circle((x+0.5, y+0.5), 0.4, color=c1))

    elif type == 'tri_half': 
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c1)
        poly.set_transform(tr); p(poly)
        
    elif type == 'arc_corner': 
        w = patches.Wedge((x, y), 1, 0, 90, color=c1)
        w.set_transform(tr); p(w)
        
    elif type == 'arc_ring':
        w1 = patches.Wedge((x, y), 1, 0, 90, color=c1)
        w2 = patches.Wedge((x, y), 0.5, 0, 90, color=c2)
        w1.set_transform(tr); w2.set_transform(tr)
        p(w1); p(w2)

    elif type == 'strip_center': 
        r = patches.Rectangle((x+0.33, y), 0.33, 1, color=c1)
        r.set_transform(tr); p(r)
        
    elif type == 'checker_4': 
        p(patches.Rectangle((x, y), 0.5, 0.5, color=c1))
        p(patches.Rectangle((x+0.5, y+0.5), 0.5, 0.5, color=c1))

# --- MOTOR DE SUPER-MÓDULOS (2x2) ---

def get_super_module(family, palette):
    """Genera un bloque de 2x2 coherente."""
    rng = random.Random()
    
    # Colores
    c_bg = palette[0]
    # Intentar coger un color de contraste diferente al fondo
    others = [c for c in palette if c != c_bg]
    c_fg = rng.choice(others) if others else c_bg
    
    patterns = []
    
    # --- FAMILIA CURVA ---
    if family in ["Mezcla", "Curvas"]:
        # Círculo Grande (4 arcos)
        patterns.append([
            [('arc_corner', 0, c_fg, c_bg), ('arc_corner', 3, c_fg, c_bg)],
            [('arc_corner', 1, c_fg, c_bg), ('arc_corner', 2, c_fg, c_bg)]
        ])
        # Topos (4 círculos sólidos)
        patterns.append([
            [('circle', 0, c_fg, c_bg), ('circle', 0, c_fg, c_bg)],
            [('circle', 0, c_fg, c_bg), ('circle', 0, c_fg, c_bg)]
        ])
        # Topos Alternos (Ajedrez)
        patterns.append([
            [('circle', 0, c_fg, c_bg), ('full', 0, c_fg, c_bg)],
            [('full', 0, c_fg, c_bg), ('circle', 0, c_fg, c_bg)]
        ])
        # Olas
        patterns.append([
            [('arc_corner', 0, c_fg, c_bg), ('arc_corner', 1, c_bg, c_fg)],
            [('arc_corner', 3, c_bg, c_fg), ('arc_corner', 2, c_fg, c_bg)]
        ])

    # --- FAMILIA DIAGONAL ---
    if family in ["Mezcla", "Diagonales"]:
        # Diamante
        patterns.append([
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)],
            [('tri_half', 1, c_fg, c_bg), ('tri_half', 2, c_fg, c_bg)]
        ])
        # Reloj Arena
        patterns.append([
            [('tri_half', 1, c_fg, c_bg), ('tri_half', 2, c_fg, c_bg)],
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)]
        ])
        # ZigZag
        patterns.append([
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)],
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)]
        ])

    # --- FAMILIA ORTOGONAL ---
    if family in ["Mezcla", "Ortogonal"]:
        # Cruz
        patterns.append([
            [('strip_center', 1, c_fg, c_bg), ('strip_center', 1, c_fg, c_bg)],
            [('strip_center', 0, c_fg, c_bg), ('strip_center', 0, c_fg, c_bg)]
        ])
        # Marcos
        patterns.append([
            [('checker_4', 0, c_fg, c_bg), ('full', 0, c_bg, c_fg)],
            [('full', 0, c_bg, c_fg), ('checker_4', 0, c_fg, c_bg)]
        ])

    if not patterns: return [[('full', 0, c_fg, c_bg)]*2]*2
    return random.choice(patterns)

# --- GENERADOR PRINCIPAL ---

def generate_grid(size, palette, family, mode):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    # Generamos 2 Super-Módulos temáticos para todo el diseño
    mod_A = get_super_module(family, palette)
    # mod_B suele ser el negativo de A o uno complementario
    mod_B = get_super_module(family, palette) 
    
    if mode == "Super-Modulos":
        # Repetir A y B en patrón de ajedrez grande
        for r in range(0, size, 2):
            for c in range(0, size, 2):
                is_A = ((r//2) + (c//2)) % 2 == 0
                current = mod_A if is_A else mod_B
                
                # Pintar el bloque 2x2
                for i in range(2):
                    for j in range(2):
                        if r+i < size and c+j < size:
                            grid[r+i][c+j] = current[i][j]

    elif mode == "Tejido Infinito":
        # Usar un solo módulo pero rotándolo para crear flujo
        base = get_super_module(family, palette)
        for r in range(0, size, 2):
            for c in range(0, size, 2):
                # Rotación basada en posición para conectar líneas
                rot_offset = ((r//2) + (c//2)) % 4
                for i in range(2):
                    for j in range(2):
                        if r+i < size and c+j < size:
                            cell = base[i][j]
                            new_rot = (cell[1] + rot_offset) % 4
                            grid[r+i][c+j] = (cell[0], new_rot, cell[2], cell[3])

    return grid

def render_art(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell:
                # Invertir Y para dibujar ordenado
                draw_tile(ax, c, size-1-r, cell[0], cell[1], cell[2], cell[3])

    # Marco
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=8)
    
    # Retícula visible (Grosor 0.5)
    for i in range(size+1):
        ax.plot([0, size], [i, i], color='black', linewidth=0.5, alpha=0.3)
        ax.plot([i, i], [0, size], color='black', linewidth=0.5, alpha=0.3)

    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)

grid_data = generate_grid(grid_size, paleta, familia, modo)
figura = render_art(grid_data, grid_size)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR IMAGEN", data=buf.getvalue(), file_name="nicoart.png", mime="image/png")
