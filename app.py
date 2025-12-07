import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PATRONES INFINITOS", layout="centered")

# --- ESTILOS CSS (UI MODERNA & MÓVIL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    h1 { 
        font-family: 'Inter', sans-serif;
        font-weight: 800; 
        letter-spacing: -1.5px;
        color: #000; 
        text-align: center;
        font-size: 2.2rem;
        margin-bottom: 0px;
        text-transform: uppercase;
    }
    
    .author {
        text-align: center; color: #888; font-size: 0.8em; font-weight: 600; 
        margin-top: -5px; margin-bottom: 30px; letter-spacing: 1px;
    }

    /* Expander Moderno */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        font-weight: 600;
        color: #111;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .streamlit-expanderContent {
        border: 1px solid #e0e0e0;
        border-top: none;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        background-color: #fafafa;
        padding: 20px;
    }

    /* Botón Principal */
    div.stButton > button { 
        width: 100%; 
        border: none;
        border-radius: 12px; 
        font-weight: 700; 
        font-size: 16px; 
        letter-spacing: 1px;
        background: #111111; 
        color: #ffffff; 
        padding: 18px 0px; 
        box-shadow: 0 4px 14px 0 rgba(0,0,0,0.2);
        transition: transform 0.1s ease-in-out;
    }
    
    div.stButton > button:hover { 
        transform: translateY(-2px); 
        background-color: #000;
        color: #FFC300; 
    }
    
    /* Ajuste Multiselect */
    .stMultiSelect span {
        background-color: #eee;
        color: #000;
        border-radius: 4px;
    }

    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>PATRONES INFINITOS</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- DEFINICIÓN DE FORMAS (CATÁLOGO) ---
FORMAS_DISPONIBLES = {
    "◢  Triángulos": "triangle",
    "◕  Curvas": "quarter_circle",
    "●  Círculos": "circle",
    "⧈  Marcos": "frame",
    "🎀 Lazos": "bow",
    "▰  Bandas": "strip",
    "◆  Diamantes": "diamond",
    "◼  Sólidos": "solid"
}

# --- PALETAS ---
PALETAS = {
    "🟡 Amarillo Huevo & Negro": ["#FFC300", "#000000"], 
    "🏛️ Arquitecto (Grises)": ["#000000", "#333333", "#777777", "#BBBBBB", "#FFFFFF"],
    "💊 Cyberpunk Fluor": ["#000000", "#FF00FF", "#00FFFF", "#CCFF00", "#791E94"],
    "🍊 Vitamina C": ["#FFFFFF", "#FF9F1C", "#FFBF69", "#FF5400", "#333333"],
    "🏺 Mostaza Retro 70s": ["#3B2518", "#E87A25", "#D9A404", "#8C4926", "#F0EAD6"],
    "🧊 Pastel Nórdico": ["#FFFFFF", "#FFB7C5", "#B5EAD7", "#E2F0CB", "#FFDAC1"],
    "🕌 Alhambra Real": ["#F2ECCE", "#1A4780", "#D9A404", "#8C2727", "#2E5936"],
    "🔳 Bauhaus Puro": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "🌊 Azulejo Lisboa": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#6699FF"],
    "🐋 Océano Profundo": ["#001219", "#005F73", "#0A9396", "#94D2BD", "#E9D8A6"],
    "🌲 Bosque Místico": ["#0D1B2A", "#1B263B", "#415A77", "#778DA9", "#E0E1DD"],
    "🍷 Vino Tinto": ["#160000", "#310000", "#4C0000", "#6D0000", "#D4AF37"],
    "🍭 Caramelo Pop": ["#FFFFFF", "#FF595E", "#FFCA3A", "#8AC926", "#1982C4"],
    "🐪 Desierto Dorado": ["#283618", "#606C38", "#FEFAE0", "#DDA15E", "#BC6C25"],
    "👾 Matrix": ["#000000", "#003B00", "#008F11", "#00FF41", "#0D0208"],
    "🏭 Industrial": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"],
    "🍫 Chocolate y Crema": ["#F4F1DE", "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F"],
    "🕶️ Alta Costura (B&W)": ["#000000", "#111111", "#AAAAAA", "#EEEEEE", "#FFFFFF"],
    "🌴 Atardecer Miami": ["#540D6E", "#EE4266", "#FFD23F", "#3BCEAC", "#0EAD69"],
    "🏺 Tierra Cruda": ["#582F0E", "#7F4F24", "#936639", "#A68A64", "#B6AD90"]
}

# --- CONTROLES MODERNOS ---
with st.expander("🎛️ CONTROLES DE DISEÑO", expanded=True):
    
    # 1. COLOR
    st.caption("ATMÓSFERA CROMÁTICA")
    p_name = st.selectbox("Paleta", list(PALETAS.keys()), label_visibility="collapsed")
    paleta_actual = PALETAS[p_name]
    
    # Preview Color
    cols = st.columns(len(paleta_actual))
    for i, c in enumerate(cols):
        c.markdown(f"<div style='background-color:{paleta_actual[i]};height:24px;width:100%;border-radius:4px;'></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. ESTRUCTURA Y MODO
    st.caption("ESTRUCTURA")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Eliminado el Ajedrez, solo quedan los dos modos principales
        simetria = st.selectbox("Modo", ["Caleidoscopio (Mandala)", "Repetición (Papel Pintado)"])
    with col_b:
        grid_size = st.select_slider("Resolución", options=[4, 8, 12, 16, 20, 24], value=8)

    # 3. SELECTOR DE FORMAS (CONDICIONAL)
    st.markdown("---")
    formas_seleccionadas = []
    
    if simetria == "Repetición (Papel Pintado)":
        st.caption("SELECCIONA TUS POLÍGONOS (Elige al menos 1)")
        nombres_formas = list(FORMAS_DISPONIBLES.keys())
        seleccion = st.multiselect(
            "Elige las formas que compondrán tu patrón:",
            options=nombres_formas,
            default=nombres_formas[:4] # Por defecto selecciona las primeras 4
        )
        # Convertir nombres a IDs internos
        formas_seleccionadas = [FORMAS_DISPONIBLES[k] for k in seleccion]
        if not formas_seleccionadas: # Fallback si deselecciona todo
            formas_seleccionadas = ['solid']
            st.warning("⚠️ Debes elegir al menos una forma. Se usará 'Sólidos' por defecto.")
    else:
        # En Caleidoscopio usamos todas para máxima variedad, o un subconjunto rico
        formas_seleccionadas = list(FORMAS_DISPONIBLES.values())

    st.write("") 
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("✨ GENERAR NUEVA OBRA"): st.session_state.seed += 1

# --- MOTOR DE RENDERIZADO HD ---

def add_tile_hd(ax, x, y, type, rot, c_main, c_acc):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def patch(p):
        p.set_antialiased(False); p.set_linewidth(0); ax.add_patch(p)

    # 1. Fondo base (Blanco)
    patch(patches.Rectangle((x, y), 1, 1, color='#FFFFFF')) 
    
    # 2. Formas
    if type == 'solid':
        patch(patches.Rectangle((x, y), 1, 1, color=c_main))
    elif type == 'triangle': 
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        p.set_transform(tr); patch(p)
    elif type == 'quarter_circle': 
        w = patches.Wedge((x, y), 1, 0, 90, color=c_main)
        w.set_transform(tr); patch(w)
    elif type == 'strip': 
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=c_main)
        p2 = patches.Polygon([(x+0.5, y+0.5), (x+1.5, y+0.5), (x+0.5, y+1.5)], color=c_acc)
        p.set_transform(tr); patch(p); patch(p2)
    elif type == 'circle':
        patch(patches.Circle((x+0.5, y+0.5), 0.4, color=c_main))
    elif type == 'frame': 
        patch(patches.Rectangle((x, y), 1, 1, color=c_main))
        patch(patches.Rectangle((x+0.25, y+0.25), 0.5, 0.5, color=c_acc))
    elif type == 'bow': 
        p1 = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=c_main)
        p2 = patches.Polygon([(x, y+1), (x+1, y+1), (x+0.5, y+0.5)], color=c_main)
        p1.set_transform(tr); p2.set_transform(tr); patch(p1); patch(p2)
    elif type == 'diamond':
        p = patches.Polygon([(x+0.5, y), (x+1, y+0.5), (x+0.5, y+1), (x, y+0.5)], color=c_main)
        patch(p)

    # 3. RETÍCULA INTERIOR (VISIBLE)
    grid_line = patches.Rectangle(
        (x, y), 1, 1, fill=False, 
        edgecolor='#000000', linewidth=0.5, alpha=0.3, zorder=100, antialiased=True
    )
    ax.add_patch(grid_line)

# --- GENERACIÓN DE PATRONES ---

def generate_pattern(size, palette, symmetry_mode, allowed_shapes):
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    if symmetry_mode == "Repetición (Papel Pintado)":
        # 1. Crear un "Módulo Maestro" (Seed) que sea estéticamente rico
        # El tamaño del módulo depende de la resolución para que se repita bien
        module_size = 4 if size >= 8 else 2 
        
        module_grid = [[None for _ in range(module_size)] for _ in range(module_size)]
        
        # Generar el módulo usando SOLO las formas seleccionadas
        for r in range(module_size):
            for c in range(module_size):
                tipo = random.choice(allowed_shapes)
                rot = random.randint(0, 3)
                
                # Selección de color inteligente
                c1 = random.choice(palette)
                avail = [x for x in palette if x != c1]
                c2 = random.choice(avail) if avail else c1
                
                # Para evitar caos, a veces forzamos simetría dentro del propio módulo
                module_grid[r][c] = {'type': tipo, 'rot': rot, 'c_main': c1, 'c_acc': c2}

        # 2. Repetir el módulo continuamente por todo el grid
        for r in range(size):
            for c in range(size):
                # Copiamos del módulo usando módulo (%)
                source_cell = module_grid[r % module_size][c % module_size]
                grid[r][c] = source_cell

    else: 
        # MODO CALEIDOSCOPIO (Mandala)
        # Generamos cuadrante superior izquierdo y reflejamos
        seed_size = size // 2
        for r in range(seed_size):
            for c in range(seed_size):
                tipo = random.choice(allowed_shapes)
                rot = random.randint(0, 3)
                c1 = random.choice(palette)
                c2 = random.choice(palette)
                
                cell = {'type': tipo, 'rot': rot, 'c_main': c1, 'c_acc': c2}
                
                # Aplicar espejos
                grid[r][c] = cell # Top-Left
                
                tr = cell.copy(); tr['mirror_x'] = True
                grid[r][size-1-c] = tr # Top-Right
                
                bl = cell.copy(); bl['mirror_y'] = True
                grid[size-1-r][c] = bl # Bot-Left
                
                br = cell.copy(); br['mirror_x'] = True; br['mirror_y'] = True
                grid[size-1-r][size-1-c] = br # Bot-Right

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
            
            # Ajuste de rotación para espejos (Solo afecta a Caleidoscopio)
            if cell.get('mirror_x'): rot = {0:1, 1:0, 2:3, 3:2}.get(rot, rot)
            if cell.get('mirror_y'): rot = {0:3, 1:2, 2:1, 3:0}.get(rot, rot)
            
            add_tile_hd(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    # Marco Exterior
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=8)
    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)

grid_data = generate_pattern(grid_size, paleta_actual, simetria, formas_seleccionadas)
figura = render_final(grid_data, grid_size)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="⬇️ DESCARGAR IMAGEN HD", data=buf.getvalue(), file_name="patron_infinito_nb.png", mime="image/png")
