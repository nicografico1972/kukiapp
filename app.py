import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PATRONES INFINITOS", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    h1 { 
        font-family: 'Helvetica Neue', sans-serif;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 900; color: #000; text-align: center; margin-bottom: 0px;
    }
    .author {
        text-align: center; color: #888; font-size: 0.8em; margin-top: -10px; margin-bottom: 30px;
    }
    div.stButton > button { 
        width: 100%; border: 4px solid #000; border-radius: 0px; font-weight: 900; font-size: 18px; text-transform: uppercase;
        background-color: #fff; color: #000; padding: 20px 0px; transition: all 0.2s; box-shadow: 8px 8px 0px #000;
    }
    div.stButton > button:hover { transform: translate(-4px, -4px); box-shadow: 12px 12px 0px #000; background-color: #f0f0f0;}
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>PATRONES INFINITOS</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- PALETAS ---
PALETAS = {
    "Arquitecto (Grises)": ["#000000", "#333333", "#777777", "#BBBBBB", "#FFFFFF"],
    "Cyberpunk Fluor": ["#000000", "#FF00FF", "#00FFFF", "#CCFF00", "#791E94"],
    "Vitamina C (Naranjas)": ["#FFFFFF", "#FF9F1C", "#FFBF69", "#FF5400", "#333333"],
    "Mostaza Retro 70s": ["#3B2518", "#E87A25", "#D9A404", "#8C4926", "#F0EAD6"],
    "Pastel Nórdico": ["#FFFFFF", "#FFB7C5", "#B5EAD7", "#E2F0CB", "#FFDAC1"],
    "Alhambra Real": ["#F2ECCE", "#1A4780", "#D9A404", "#8C2727", "#2E5936"],
    "Bauhaus Puro": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "Azulejo Lisboa": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#6699FF"],
    "Océano Profundo": ["#001219", "#005F73", "#0A9396", "#94D2BD", "#E9D8A6"],
    "Bosque Místico": ["#0D1B2A", "#1B263B", "#415A77", "#778DA9", "#E0E1DD"],
    "Vino Tinto": ["#160000", "#310000", "#4C0000", "#6D0000", "#D4AF37"],
    "Caramelo Pop": ["#FFFFFF", "#FF595E", "#FFCA3A", "#8AC926", "#1982C4"],
    "Desierto Dorado": ["#283618", "#606C38", "#FEFAE0", "#DDA15E", "#BC6C25"],
    "Lavanda Digital": ["#E6E6FA", "#9370DB", "#4B0082", "#8A2BE2", "#FFFFFF"],
    "Matrix": ["#000000", "#003B00", "#008F11", "#00FF41", "#0D0208"],
    "Industrial": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"],
    "Chocolate y Crema": ["#F4F1DE", "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F"],
    "Alta Costura (B&W)": ["#000000", "#111111", "#AAAAAA", "#EEEEEE", "#FFFFFF"],
    "Atardecer Miami": ["#540D6E", "#EE4266", "#FFD23F", "#3BCEAC", "#0EAD69"],
    "Tierra Cruda": ["#582F0E", "#7F4F24", "#936639", "#A68A64", "#B6AD90"]
}

# --- CONTROLES ---
with st.expander("🎛️ CONTROLES (TÓCAME)", expanded=True):
    st.write("### 1. Atmósfera")
    p_name = st.selectbox("Paleta:", list(PALETAS.keys()))
    paleta_actual = PALETAS[p_name]
    
    # Preview
    cols = st.columns(5)
    for i, c in enumerate(cols):
        c.markdown(f"<div style='background-color:{paleta_actual[i]};height:20px;width:100%'></div>", unsafe_allow_html=True)

    st.write("### 2. Estructura")
    c1, c2 = st.columns(2)
    with c1:
        grid_size = st.select_slider("Resolución Grid", options=[4, 8, 12, 16, 20, 24], value=8)
    with c2:
        escala_formas = st.select_slider("Escala", options=["Micro", "Medio", "Macro (Gigante)"], value="Macro (Gigante)")
    
    simetria = st.selectbox("Simetría", ["Caleidoscopio", "Repetición", "Ajedrez Armónico"])
    
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("🎲 GENERAR PATRÓN"): st.session_state.seed += 1

# --- RENDERIZADO ---

def add_tile(ax, x, y, type, rot, c_main, c_acc):
    """Dibuja una celda unitaria con retícula fina."""
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def patch_hd(p):
        p.set_antialiased(False)
        p.set_linewidth(0)
        ax.add_patch(p)

    # 1. Fondo base
    patch_hd(patches.Rectangle((x, y), 1, 1, color='#FFFFFF')) 
    
    # 2. Formas
    if type == 'solid':
        patch_hd(patches.Rectangle((x, y), 1, 1, color=c_main))
    elif type == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        p.set_transform(tr); patch_hd(p)
    elif type == 'quarter_circle':
        w = patches.Wedge((x, y), 1, 0, 90, color=c_main)
        w.set_transform(tr); patch_hd(w)
    elif type == 'strip':
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=c_main)
        p2 = patches.Polygon([(x+0.5, y+0.5), (x+1.5, y+0.5), (x+0.5, y+1.5)], color=c_acc)
        p.set_transform(tr); patch_hd(p)
    elif type == 'circle':
        patch_hd(patches.Circle((x+0.5, y+0.5), 0.4, color=c_main))
    elif type == 'frame':
        patch_hd(patches.Rectangle((x, y), 1, 1, color=c_main))
        patch_hd(patches.Rectangle((x+0.25, y+0.25), 0.5, 0.5, color=c_acc))
    elif type == 'bow':
        p1 = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=c_main)
        p2 = patches.Polygon([(x, y+1), (x+1, y+1), (x+0.5, y+0.5)], color=c_main)
        p1.set_transform(tr); p2.set_transform(tr)
        patch_hd(p1); patch_hd(p2)

    # 3. RETÍCULA INTERIOR (MUY FINA)
    # Dibujamos un rectángulo sin relleno encima de todo
    grid_line = patches.Rectangle(
        (x, y), 1, 1, 
        fill=False, 
        edgecolor='#000000', # Color de la línea (negro)
        linewidth=0.15,      # Muy muy fina (0.15 es sutil en HD)
        alpha=0.2,           # Semitransparente para no molestar
        zorder=100,          # Siempre encima
        antialiased=True     # Suavizada para que se vea elegante
    )
    ax.add_patch(grid_line)

# --- LÓGICA MACRO ---

def fill_macro_block(grid, r_start, c_start, block_size, palette):
    macro_type = random.choice(['big_diamond', 'big_x', 'concentric', 'big_circle'])
    c1 = random.choice(palette)
    avail = [c for c in palette if c != c1]
    c2 = random.choice(avail) if avail else c1
    
    for r in range(block_size):
        for c in range(block_size):
            rr, cc = r, c
            cell_type, rot, color, accent = 'solid', 0, '#FFFFFF', c2
            
            if macro_type == 'big_diamond':
                if rr + cc < block_size // 2: pass
                elif rr + cc == block_size // 2: cell_type='triangle'; rot=0; color=c1
                elif rr - cc == block_size // 2: cell_type='triangle'; rot=3; color=c1
                elif cc - rr == block_size // 2: cell_type='triangle'; rot=1; color=c1
                elif rr + cc == (block_size * 2) - 2 - (block_size//2): cell_type='triangle'; rot=2; color=c1
                else:
                    mid = block_size / 2
                    if abs(rr - mid + 0.5) + abs(cc - mid + 0.5) < mid: cell_type='solid'; color=c1
            
            elif macro_type == 'big_x':
                if rr == cc: cell_type='solid'; color=c1
                elif rr + cc == block_size - 1: cell_type='solid'; color=c1
                else: cell_type='solid'; color=c2

            elif macro_type == 'concentric':
                if r == 0 or r == block_size - 1 or c == 0 or c == block_size - 1: cell_type='solid'; color=c1
                elif r == 1 or r == block_size - 2 or c == 1 or c == block_size - 2: cell_type='solid'; color=c2
            
            elif macro_type == 'big_circle':
                if r == 0 and c == 0: cell_type='quarter_circle'; rot=2; color=c1
                elif r == 0 and c == block_size-1: cell_type='quarter_circle'; rot=3; color=c1
                elif r == block_size-1 and c == 0: cell_type='quarter_circle'; rot=1; color=c1
                elif r == block_size-1 and c == block_size-1: cell_type='quarter_circle'; rot=0; color=c1
                else: cell_type='solid'; color=c2

            if r_start + r < len(grid) and c_start + c < len(grid):
                grid[r_start + r][c_start + c] = {'type': cell_type, 'rot': rot, 'c_main': color, 'c_acc': accent}

def generate_pattern(size, palette, scale_mode, symmetry_mode):
    block_size = max(4, size // 2) if "Macro" in scale_mode else (max(2, size // 4) if "Medio" in scale_mode else 1)
    grid = [[None for _ in range(size)] for _ in range(size)]
    seed_limit = size if "Repetición" in symmetry_mode or "Ajedrez" in symmetry_mode else size // 2
    
    for r in range(0, seed_limit, block_size):
        for c in range(0, seed_limit, block_size):
            if block_size > 1:
                fill_macro_block(grid, r, c, block_size, palette)
            else:
                t = random.choice(['triangle', 'quarter_circle', 'solid'])
                rot = random.randint(0,3)
                col = random.choice(palette)
                grid[r][c] = {'type': t, 'rot': rot, 'c_main': col, 'c_acc': col}

    if "Caleidoscopio" in symmetry_mode:
        half = size // 2
        for r in range(half):
            for c in range(half):
                cell = grid[r][c]
                if not cell: cell = {'type':'solid', 'rot':0, 'c_main':'#FFF', 'c_acc':'#FFF'}
                grid[r][c] = cell
                tr = cell.copy(); tr['mirror_x'] = True; grid[r][size-1-c] = tr
                bl = cell.copy(); bl['mirror_y'] = True; grid[size-1-r][c] = bl
                br = cell.copy(); br['mirror_x'] = True; br['mirror_y'] = True; grid[size-1-r][size-1-c] = br

    return grid

def render_final(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if not cell: continue
            x, y = c, size - 1 - r
            rot = cell['rot']
            if cell.get('mirror_x'): rot = {0:1, 1:0, 2:3, 3:2}.get(rot, rot)
            if cell.get('mirror_y'): rot = {0:3, 1:2, 2:1, 3:0}.get(rot, rot)
            add_tile(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=6)
    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)
grid_data = generate_pattern(grid_size, paleta_actual, escala_formas, simetria)
figura = render_final(grid_data, grid_size)
st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="⬇️ DESCARGAR", data=buf.getvalue(), file_name="patron_infinito.png", mime="image/png")
