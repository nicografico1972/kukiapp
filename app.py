import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PATRONES INFINITOS", layout="centered")

# --- ESTILOS CSS (UI MÓVIL OPTIMIZADA & BRANDING) ---
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    h1 { 
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        letter-spacing: 4px;
        font-weight: 900; color: #111; text-align: center; margin-bottom: 0px;
    }
    .subtitle {
        text-align: center; color: #666; font-weight: 300; letter-spacing: 2px;
        margin-bottom: 30px; font-family: 'Montserrat', sans-serif; font-size: 1.2em;
    }
    .author {
        text-align: center; color: #999; font-size: 0.9em; margin-top: -20px; margin-bottom: 30px;
    }
    .streamlit-expanderHeader {
        background-color: #fff; border: 2px solid #111; border-radius: 0px; font-weight: 700; color: #111; text-transform: uppercase;
    }
    .streamlit-expanderContent {
        border: 2px solid #111; border-top: none; background-color: #fff; padding: 20px;
    }
    div.stButton > button { 
        width: 100%; border: 3px solid #111; border-radius: 0px; font-weight: 900; font-size: 18px; text-transform: uppercase;
        background-color: #fff; color: #111; padding: 18px 0px; transition: all 0.3s; box-shadow: 6px 6px 0px #111;
    }
    div.stButton > button:hover { transform: translate(-3px, -3px); box-shadow: 9px 9px 0px #111; background-color: #f0f0f0;}
    div.stButton > button:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0px #111; background-color: #ddd; }
    [data-testid="column"] { min-width: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>PATRONES INFINITOS</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- COLECCIÓN DE 20 PALETAS ARMÓNICAS ---
PALETAS_PREDEFINIDAS = {
    "Alhambra Clásica": ["#1A4780", "#D9A404", "#8C2727", "#2E5936", "#F2ECCE"],
    "Escala de Grises (Arquitecto)": ["#111111", "#333333", "#666666", "#999999", "#CCCCCC"],
    "Vitamina C (Cítricos)": ["#FF9F1C", "#FFBF69", "#FFFF9F", "#CBF3F0", "#2EC4B6"],
    "Mostazas & Retros 70s": ["#D9A404", "#8C4926", "#3B2518", "#E87A25", "#F0EAD6"],
    "Fluorescente Cyberpunk": ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF00", "#111111"],
    "Pasteles Suaves (Nórdico)": ["#FFB7C5", "#B5EAD7", "#E2F0CB", "#FFDAC1", "#F7F4E3"],
    "Bauhaus Primarios": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "Océano Profundo": ["#002642", "#023E8A", "#0077B6", "#0096C7", "#ADE8F4"],
    "Bosque Encantado": ["#2D3E40", "#3A5F5F", "#4A7C59", "#74A57F", "#A3C9A8"],
    "Atardecer Desierto": ["#5E3023", "#895737", "#C08552", "#F3C969", "#EDF6F9"],
    "Vino y Oro": ["#4A0404", "#720909", "#A4161A", "#BA181B", "#D4AF37"],
    "Tierra Mineral": ["#556B2F", "#8B4513", "#DAA520", "#CD853F", "#F5F5DC"],
    "Azulejo Portugués": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#4D79FF"],
    "Neón Medianoche": ["#0A0A0A", "#FF1493", "#00BFFF", "#7FFF00", "#FF4500"],
    "Crema y Carbón": ["#F8F9FA", "#E9ECEF", "#DEE2E6", "#343A40", "#212529"],
    "Especias Marroquíes": ["#C0392B", "#D35400", "#F39C12", "#27AE60", "#8E44AD"],
    "Industrial Chic": ["#2C3E50", "#95A5A6", "#BDC3C7", "#E74C3C", "#ECF0F1"],
    "Aurora Boreal": ["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1", "#45A29E"],
    "Candy Pop": ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#F7F7F7"],
    "Elegancia Monocroma": ["#000000", "#222222", "#FFFFFF", "#EEEEEE", "#444444"]
}

# --- PANEL DE CONTROL ---
with st.expander("🎛️ CONTROLES DE DISEÑO (TÓCAME)", expanded=True):
    
    st.write("### 1. Paleta de Color")
    nombre_paleta = st.selectbox("Selecciona una atmósfera:", list(PALETAS_PREDEFINIDAS.keys()))
    paleta_actual = PALETAS_PREDEFINIDAS[nombre_paleta]

    # Muestra visual de la paleta
    cols_preview = st.columns(5)
    for i, col in enumerate(cols_preview):
        col.markdown(f'<div style="background-color: {paleta_actual[i]}; height: 30px; border-radius: 5px;"></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.write("### 2. Estructura y Armonía")
    simetria = st.selectbox("Modo de Composición", ["Caleidoscopio (Mandala)", "Repetición (Papel Pintado)", "Ajedrez (Ritmo Alterno)"])
    
    c_geo1, c_geo2 = st.columns(2)
    with c_geo1:
        complejidad = st.select_slider("Tamaño del Grid", options=[2, 4, 6, 8, 12, 16], value=6)
    with c_geo2:
        densidad = st.slider("Densidad (Aire vs Forma)", 0.1, 1.0, 0.9)

    st.markdown("---")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("🎲 GENERAR ARMONÍA"): st.session_state.seed += 1

# --- MOTOR GRÁFICO HD ---

def add_patch_hd(ax, patch):
    """Renderizado HD sin bordes borrosos"""
    patch.set_antialiased(False)
    patch.set_linewidth(0)
    ax.add_patch(patch)

def draw_tile_hd(ax, x, y, tipo, rot, c_main, c_acc):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData

    # 1. FONDO BLANCO BASE (Siempre limpio)
    bg = patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0)
    add_patch_hd(ax, bg)
    
    # 2. MARCO FINO (Sutil)
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#111111', linewidth=0.5, zorder=10, antialiased=True, alpha=0.3))

    # --- CATÁLOGO DE FORMAS (GEOMETRÍA SAGRADA) ---
    if tipo == 'star_8':
        r1 = patches.Rectangle((x+0.2, y+0.2), 0.6, 0.6, color=c_main); r1.set_transform(tr)
        r2 = patches.Rectangle((x+0.2, y+0.2), 0.6, 0.6, color=c_main)
        r2.set_transform(transforms.Affine2D().rotate_deg_around(x+0.5, y+0.5, 45) + tr)
        add_patch_hd(ax, r1); add_patch_hd(ax, r2)
        add_patch_hd(ax, patches.Circle((x+0.5, y+0.5), 0.15, color=c_acc))
    elif tipo == 'lantern':
        p = patches.Polygon([(x+0.2, y+0.2), (x+0.8, y+0.2), (x+0.5, y+0.5)], color=c_main); p.set_transform(tr)
        w = patches.Wedge((x+0.5, y+0.5), 0.35, 0, 180, color=c_acc); w.set_transform(tr)
        add_patch_hd(ax, p); add_patch_hd(ax, w)
    elif tipo == 'petal':
        w1 = patches.Wedge((x, y+0.5), 0.8, -30, 30, color=c_main); w1.set_transform(tr)
        add_patch_hd(ax, w1)
    elif tipo == 'weave':
        r1 = patches.Rectangle((x+0.4, y), 0.2, 1, color=c_main); r1.set_transform(tr)
        r2 = patches.Rectangle((x, y+0.4), 1, 0.2, color=c_acc); r2.set_transform(tr)
        add_patch_hd(ax, r1); add_patch_hd(ax, r2)
    elif tipo == 'quarter_sun':
        w1 = patches.Wedge((x, y), 1, 0, 90, color=c_main); w1.set_transform(tr)
        w2 = patches.Wedge((x, y), 0.7, 0, 90, color='#FFFFFF'); w2.set_transform(tr)
        w3 = patches.Wedge((x, y), 0.4, 0, 90, color=c_acc); w3.set_transform(tr)
        add_patch_hd(ax, w1); add_patch_hd(ax, w2); add_patch_hd(ax, w3)
    elif tipo == 'diamond_split':
        p1 = patches.Polygon([(x, y+0.5), (x+0.5, y+1), (x+0.5, y+0.5)], color=c_main); p1.set_transform(tr)
        p2 = patches.Polygon([(x+0.5, y+0.5), (x+1, y+0.5), (x+0.5, y)], color=c_acc); p2.set_transform(tr)
        add_patch_hd(ax, p1); add_patch_hd(ax, p2)
    elif tipo == 'circle':
        add_patch_hd(ax, patches.Circle((x+0.5, y+0.5), 0.4, color=c_main))
    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main); p.set_transform(tr)
        add_patch_hd(ax, p)
    elif tipo == 'arch':
        w = patches.Wedge((x+0.5, y), 0.5, 0, 180, color=c_main); w.set_transform(tr)
        add_patch_hd(ax, w)
    elif tipo == 'solid':
        add_patch_hd(ax, patches.Rectangle((x, y), 1, 1, color=c_main))

# --- MOTOR DE GENERACIÓN ARMÓNICA (El secreto de la armonía) ---

def generate_harmonic_grid(size, palette, density, mode):
    
    # 1. Establecer el "Tema Armónico" de esta generación.
    # En lugar de elegir al azar en cada celda, elegimos un subconjunto
    # de formas y colores que dominarán este diseño específico.
    
    all_shapes = ['star_8', 'lantern', 'petal', 'weave', 'quarter_sun', 'diamond_split', 'circle', 'triangle', 'arch']
    # Elegimos 2 formas dominantes y 2 de acento para este patrón
    dominant_shapes = random.sample(all_shapes, k=2)
    accent_shapes = random.sample([s for s in all_shapes if s not in dominant_shapes], k=2)
    
    # Elegimos 2 colores dominantes de la paleta actual
    dominant_colors = random.sample(palette, k=min(2, len(palette)))
    if len(palette) > 2:
        accent_colors = [c for c in palette if c not in dominant_colors]
    else:
        accent_colors = dominant_colors

    def get_harmonic_cell():
        if random.random() > density: return {'type': 'solid', 'rot': 0, 'c_main': '#FFFFFF', 'c_acc': '#FFFFFF'}
        
        # 80% de probabilidad de usar el tema dominante (Armonía)
        if random.random() < 0.8:
            tipo = random.choice(dominant_shapes)
            c_main = random.choice(dominant_colors)
            c_acc = random.choice(dominant_colors) if random.random() < 0.7 else random.choice(accent_colors)
        else: # 20% de variación (Acento)
            tipo = random.choice(accent_shapes)
            c_main = random.choice(accent_colors) if accent_colors else random.choice(dominant_colors)
            c_acc = random.choice(dominant_colors)
            
        rot = random.randint(0, 3)
        return {'type': tipo, 'rot': rot, 'c_main': c_main, 'c_acc': c_acc}

    # 2. Generar la Semilla según el modo
    seed_size = size if mode == "Repetición (Papel Pintado)" else size // 2
    if mode == "Ajedrez (Ritmo Alterno)": seed_size = size
    if mode == "Caleidoscopio (Mandala)": seed_size = size // 2
    
    base_data = [[get_harmonic_cell() for _ in range(size)] for _ in range(size)]

    # 3. Aplicar Simetría
    final_grid = [[None for _ in range(size)] for _ in range(size)]
    
    if mode == "Caleidoscopio (Mandala)":
        for r in range(seed_size):
            for c in range(seed_size):
                cell = base_data[r][c]
                final_grid[r][c] = cell
                tr = cell.copy(); tr['mirror_x'] = True; final_grid[r][size-1-c] = tr
                bl = cell.copy(); bl['mirror_y'] = True; final_grid[size-1-r][c] = bl
                br = cell.copy(); br['mirror_x'] = True; br['mirror_y'] = True; final_grid[size-1-r][size-1-c] = br
                
    elif mode == "Repetición (Papel Pintado)":
        block_size = max(2, size // 2) # Bloques más grandes para más armonía
        block = [[base_data[r][c] for c in range(block_size)] for r in range(block_size)]
        for r in range(size):
            for c in range(size):
                final_grid[r][c] = block[r % block_size][c % block_size]
                
    elif mode == "Ajedrez (Ritmo Alterno)":
        # Usamos la base armónica y rotamos. Al ser la base armónica, el resultado ya no es anárquico.
        for r in range(size):
            for c in range(size):
                cell = base_data[r][c].copy()
                if (r + c) % 2 == 1:
                    cell['rot'] = (cell['rot'] + 1) % 4
                final_grid[r][c] = cell

    return final_grid

def render_final(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell is None: continue
            x, y = c, size - 1 - r
            rot = cell['rot']
            if cell.get('mirror_x'): rot = {0:1, 1:0, 2:3, 3:2}[rot]
            if cell.get('mirror_y'): rot = {0:3, 1:2, 2:1, 3:0}[rot]
            draw_tile_hd(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    return fig

# --- EJECUCIÓN ---

random.seed(st.session_state.seed)

# Usamos el nuevo generador armónico
grid_data = generate_harmonic_grid(complejidad, paleta_actual, densidad, simetria)
figura = render_final(grid_data, complejidad)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(
    label="⬇️ DESCARGAR OBRA EN HD",
    data=buf.getvalue(),
    file_name="patrones_infinitos_nico.png",
    mime="image/png"
)
