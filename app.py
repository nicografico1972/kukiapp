import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PATRONES INFINITOS", layout="centered")

# --- ESTILOS CSS (UI MODERNA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -1.5px; color: #000; text-align: center; font-size: 2.2rem; text-transform: uppercase; margin: 0; }
    .author { text-align: center; color: #888; font-size: 0.8em; font-weight: 600; margin-bottom: 30px; letter-spacing: 1px; }
    .streamlit-expanderHeader { background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; font-weight: 600; color: #111; padding: 1rem; }
    .streamlit-expanderContent { border: 1px solid #e0e0e0; border-top: none; background-color: #fff; padding: 1.5rem; }
    div.stButton > button { width: 100%; border: none; border-radius: 8px; font-weight: 700; font-size: 16px; letter-spacing: 1px; background: #111; color: #fff; padding: 18px 0px; box-shadow: 0 4px 14px 0 rgba(0,0,0,0.2); transition: transform 0.1s ease-in-out; }
    div.stButton > button:hover { transform: translateY(-2px); background-color: #000; color: #FFC300; }
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>PATRONES INFINITOS</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- PALETAS ---
PALETAS = {
    "Amarillo & Negro": ["#FFC300", "#000000"], 
    "Bauhaus": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "Retro 70s": ["#3B2518", "#E87A25", "#D9A404", "#8C4926", "#F0EAD6"],
    "Alhambra": ["#F2ECCE", "#1A4780", "#D9A404", "#8C2727", "#2E5936"],
    "Azulejo": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#6699FF"],
    "Vitamina": ["#FFFFFF", "#FF9F1C", "#FFBF69", "#FF5400", "#333333"],
    "Nórdico": ["#FFFFFF", "#FFB7C5", "#B5EAD7", "#E2F0CB", "#FFDAC1"],
    "Matrix": ["#000000", "#003B00", "#008F11", "#00FF41", "#0D0208"],
    "Chocolate": ["#F4F1DE", "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F"],
    "Industrial": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"]
}

# --- FORMAS ---
FORMAS = {
    "△ Triángulos": "triangle", "◕ Curvas": "quarter_circle", 
    "○ Círculos": "circle", "□ Marcos": "frame", 
    "✕ Lazos": "bow", "≡ Bandas": "strip", 
    "◇ Diamantes": "diamond", "■ Sólidos": "solid"
}

# --- CONTROLES ---
with st.expander("⚙ CONFIGURACIÓN", expanded=True):
    p_name = st.selectbox("Paleta", list(PALETAS.keys()), label_visibility="collapsed")
    paleta = PALETAS[p_name]
    
    cols = st.columns(len(paleta))
    for i, c in enumerate(cols):
        c.markdown(f"<div style='background-color:{paleta[i]};height:12px;border-radius:2px;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        # AÑADIDO: Modo NicoArt
        modo = st.selectbox("Modo", ["NicoArt (Estructuras)", "Caleidoscopio", "Repetición"])
    with c2:
        grid_size = st.select_slider("Resolución", options=[4, 8, 12, 16, 20, 24], value=8)

    formas_sel = []
    if modo == "Repetición":
        st.caption("Selecciona formas:")
        sel = st.multiselect("Formas", list(FORMAS.keys()), default=list(FORMAS.keys())[:3], label_visibility="collapsed")
        formas_sel = [FORMAS[k] for k in sel] or ['solid']
    else:
        formas_sel = list(FORMAS.values())

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("GENERAR PATRÓN"): st.session_state.seed += 1

# --- RENDERIZADO HD ---
def add_tile_hd(ax, x, y, type, rot, c_main, c_acc):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    def p(patch): patch.set_antialiased(False); patch.set_linewidth(0); ax.add_patch(patch)
    
    p(patches.Rectangle((x, y), 1, 1, color='#FFFFFF')) # Fondo
    
    if type == 'solid': p(patches.Rectangle((x, y), 1, 1, color=c_main))
    elif type == 'triangle': 
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        poly.set_transform(tr); p(poly)
    elif type == 'quarter_circle': 
        w = patches.Wedge((x, y), 1, 0, 90, color=c_main); w.set_transform(tr); p(w)
    elif type == 'strip':
        r = patches.Rectangle((x, y+0.25), 1, 0.5, color=c_main); r.set_transform(tr); p(r)
    elif type == 'circle': p(patches.Circle((x+0.5, y+0.5), 0.4, color=c_main))
    elif type == 'frame': 
        p(patches.Rectangle((x, y), 1, 1, color=c_main))
        p(patches.Rectangle((x+0.25, y+0.25), 0.5, 0.5, color=c_acc))
    elif type == 'bow':
        p1 = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=c_main)
        p2 = patches.Polygon([(x, y+1), (x+1, y+1), (x+0.5, y+0.5)], color=c_main)
        p1.set_transform(tr); p2.set_transform(tr); p(p1); p(p2)
    elif type == 'diamond':
        poly = patches.Polygon([(x+0.5, y), (x+1, y+0.5), (x+0.5, y+1), (x, y+0.5)], color=c_main)
        p(poly)

    # Retícula fina
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#000', linewidth=0.25, alpha=0.15, zorder=100))

# --- LÓGICA NICOART (MACRO-ESTRUCTURAS) ---
def generate_nicoart(size, palette):
    """Genera patrones basados en estructuras grandes, no en celdas individuales."""
    grid = [[None for _ in range(size)] for _ in range(size)]
    rng = random.Random(st.session_state.seed)
    
    # 1. Definir una estructura base (Layout)
    # Puede ser: Cruz Grande, Diamante Central, Marcos Concéntricos, Damero Gigante
    layout_type = rng.choice(['big_cross', 'big_diamond', 'concentric', 'checkers_macro', 'stripes_macro'])
    
    c_bg = rng.choice(palette)
    c_fg = rng.choice([c for c in palette if c != c_bg] or [c_bg])
    c_acc = rng.choice([c for c in palette if c not in [c_bg, c_fg]] or [c_fg])

    for r in range(size):
        for c in range(size):
            # Coordenadas normalizadas (-1 a 1) para geometría matemática
            nx = (c / (size-1)) * 2 - 1
            ny = (r / (size-1)) * 2 - 1
            dist_center = max(abs(nx), abs(ny)) # Distancia Chebyshev (cuadrada)
            dist_diamond = abs(nx) + abs(ny)    # Distancia Manhattan (rombo)
            
            tipo = 'solid'
            rot = 0
            color = c_bg
            accent = c_fg

            # --- LÓGICA DE DIBUJO MACRO ---
            if layout_type == 'big_cross':
                # Cruz gigante que atraviesa el lienzo
                if abs(nx) < 0.2 or abs(ny) < 0.2:
                    tipo = 'solid'; color = c_fg
                    if abs(nx) < 0.2 and abs(ny) < 0.2: color = c_acc # Centro cruz
                else:
                    # Relleno de esquinas con triángulos mirando al centro
                    tipo = 'triangle'; color = c_bg
                    if nx < 0 and ny < 0: rot = 0
                    elif nx > 0 and ny < 0: rot = 1
                    elif nx > 0 and ny > 0: rot = 2
                    elif nx < 0 and ny > 0: rot = 3

            elif layout_type == 'big_diamond':
                # Gran rombo central
                if dist_diamond < 1.0: # Dentro del rombo
                    if dist_diamond < 0.3: # Centro del rombo
                        tipo = 'frame'; color = c_acc; accent = c_fg
                    else:
                        tipo = 'solid'; color = c_fg
                else: # Esquinas fuera del rombo
                    tipo = 'quarter_circle'; color = c_bg
                    # Orientar curvas hacia afuera
                    if nx < 0 and ny < 0: rot = 2
                    elif nx > 0 and ny < 0: rot = 3
                    elif nx > 0 and ny > 0: rot = 0
                    elif nx < 0 and ny > 0: rot = 1

            elif layout_type == 'concentric':
                # Marcos cuadrados concéntricos
                # Bandas basadas en la distancia al centro
                band = int(dist_center * (size/2)) 
                if band % 2 == 0:
                    tipo = 'solid'; color = c_fg
                else:
                    tipo = 'strip'; rot = 0 if abs(ny) > abs(nx) else 1; color = c_acc

            elif layout_type == 'checkers_macro':
                # Damero pero de bloques grandes (ej. 4x4)
                block_size = max(2, size // 4)
                is_black = ((r // block_size) + (c // block_size)) % 2 == 0
                if is_black:
                    tipo = 'bow'; color = c_fg; rot = (r+c)%2
                else:
                    tipo = 'solid'; color = c_bg

            elif layout_type == 'stripes_macro':
                # Franjas diagonales grandes
                diag_idx = (r + c) // max(2, size // 8)
                if diag_idx % 2 == 0:
                    tipo = 'solid'; color = c_fg
                else:
                    tipo = 'triangle'; color = c_acc; rot = (r+c)%4

            grid[r][c] = {'type': tipo, 'rot': rot, 'c_main': color, 'c_acc': accent}
    
    return grid

# --- GENERADORES CLÁSICOS ---
def generate_classic(size, palette, mode, allowed_shapes):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    if mode == "Repetición":
        for r in range(size):
            for c in range(size):
                idx = (r + c) % len(allowed_shapes)
                tipo = allowed_shapes[idx]
                rot = (r + c) % 2
                c1 = palette[r % len(palette)]
                c2 = palette[(r+1) % len(palette)]
                grid[r][c] = {'type': tipo, 'rot': rot, 'c_main': c1, 'c_acc': c2}
    else: # Caleidoscopio
        # Usa una semilla aleatoria pero simétrica
        current_shapes = allowed_shapes.copy(); rng.shuffle(current_shapes)
        current_palette = palette.copy(); rng.shuffle(current_palette)
        
        seed_size = size // 2
        for r in range(seed_size):
            for c in range(seed_size):
                tipo = current_shapes[(c + r) % len(current_shapes)]
                rot = (r * c) % 4
                c1 = current_palette[r % len(current_palette)]
                c2 = current_palette[(c+1) % len(current_palette)]
                
                cell = {'type': tipo, 'rot': rot, 'c_main': c1, 'c_acc': c2}
                grid[r][c] = cell
                # Espejos
                tr=cell.copy(); tr['mirror_x']=True; grid[r][size-1-c]=tr
                bl=cell.copy(); bl['mirror_y']=True; grid[size-1-r][c]=bl
                br=cell.copy(); br['mirror_x']=True; br['mirror_y']=True; grid[size-1-r][size-1-c]=br
    return grid

# --- RENDER FINAL ---
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
            add_tile_hd(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    return fig

# --- EJECUCIÓN ---
if modo == "NicoArt (Estructuras)":
    grid_data = generate_nicoart(grid_size, paleta)
else:
    grid_data = generate_classic(grid_size, paleta, modo, formas_sel)

figura = render_final(grid_data, grid_size)
st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR IMAGEN HD", data=buf.getvalue(), file_name="nicoart.png", mime="image/png")
