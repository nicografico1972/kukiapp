import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
from io import BytesIO
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PATRONES INFINITOS", layout="centered")

# --- ESTILOS CSS (UI MINIMALISTA & MODERNA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
        color: #111;
    }
    
    h1 { 
        font-family: 'Inter', sans-serif;
        font-weight: 800; 
        letter-spacing: -1px;
        color: #000; 
        text-align: center;
        font-size: 2rem;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .author {
        text-align: center; color: #666; font-size: 0.85em; font-weight: 500; 
        margin-bottom: 3rem; letter-spacing: 0.5px;
    }

    /* Expander Minimalista */
    .streamlit-expanderHeader {
        background-color: #f9f9f9;
        border: 1px solid #eee;
        border-radius: 8px;
        font-weight: 600;
        color: #333;
        padding: 1rem;
        display: flex;
        align-items: center;
    }
    .streamlit-expanderHeader svg {
        margin-right: 10px;
        fill: #333;
    }
    .streamlit-expanderContent {
        border: 1px solid #eee;
        border-top: none;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        background-color: #fff;
        padding: 1.5rem;
    }

    /* Botón Principal */
    div.stButton > button { 
        width: 100%; 
        border: none;
        border-radius: 8px; 
        font-weight: 700; 
        font-size: 15px; 
        letter-spacing: 0.5px;
        background: #111; 
        color: #fff; 
        padding: 16px 0px; 
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover { 
        background-color: #333;
        transform: translateY(-1px);
    }

    /* Ajuste de Inputs */
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        font-weight: 600;
        color: #444;
        font-size: 0.9em;
    }
    
    /* Etiquetas de formas */
    .shape-label {
        font-family: monospace;
        margin-right: 8px;
        font-size: 1.1em;
    }

    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 3rem; max-width: 700px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>PATRONES INFINITOS</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- DEFINICIÓN DE FORMAS (SIN EMOJIS, SÍMBOLOS MINIMALISTAS) ---
FORMAS_DISPONIBLES = {
    "△ Triángulos": "triangle",
    "◑ Curvas": "quarter_circle",
    "○ Círculos": "circle",
    "□ Marcos": "frame",
    "✕ Lazos": "bow",
    "≡ Bandas": "strip",
    "◇ Diamantes": "diamond",
    "■ Sólidos": "solid"
}

# --- PALETAS (SIN EMOJIS) ---
PALETAS = {
    "Amarillo & Negro": ["#FFC300", "#000000"], 
    "Arquitecto (Grises)": ["#000000", "#333333", "#777777", "#BBBBBB", "#FFFFFF"],
    "Cyberpunk": ["#000000", "#FF00FF", "#00FFFF", "#CCFF00", "#791E94"],
    "Vitamina": ["#FFFFFF", "#FF9F1C", "#FFBF69", "#FF5400", "#333333"],
    "Retro 70s": ["#3B2518", "#E87A25", "#D9A404", "#8C4926", "#F0EAD6"],
    "Nórdico": ["#FFFFFF", "#FFB7C5", "#B5EAD7", "#E2F0CB", "#FFDAC1"],
    "Alhambra": ["#F2ECCE", "#1A4780", "#D9A404", "#8C2727", "#2E5936"],
    "Bauhaus": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "Azulejo": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#6699FF"],
    "Océano": ["#001219", "#005F73", "#0A9396", "#94D2BD", "#E9D8A6"],
    "Bosque": ["#0D1B2A", "#1B263B", "#415A77", "#778DA9", "#E0E1DD"],
    "Vino": ["#160000", "#310000", "#4C0000", "#6D0000", "#D4AF37"],
    "Pop": ["#FFFFFF", "#FF595E", "#FFCA3A", "#8AC926", "#1982C4"],
    "Desierto": ["#283618", "#606C38", "#FEFAE0", "#DDA15E", "#BC6C25"],
    "Matrix": ["#000000", "#003B00", "#008F11", "#00FF41", "#0D0208"],
    "Industrial": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"],
    "Chocolate": ["#F4F1DE", "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F"],
    "B&W": ["#000000", "#111111", "#AAAAAA", "#EEEEEE", "#FFFFFF"],
    "Miami": ["#540D6E", "#EE4266", "#FFD23F", "#3BCEAC", "#0EAD69"],
    "Tierra": ["#582F0E", "#7F4F24", "#936639", "#A68A64", "#B6AD90"]
}

# --- CONTROLES ---
with st.expander("⚙ CONFIGURACIÓN", expanded=True):
    
    # 1. COLOR
    p_name = st.selectbox("Paleta de Color", list(PALETAS.keys()))
    paleta_actual = PALETAS[p_name]
    
    # Preview Color Minimalista
    cols = st.columns(len(paleta_actual))
    for i, c in enumerate(cols):
        c.markdown(f"<div style='background-color:{paleta_actual[i]};height:12px;width:100%;border-radius:2px;'></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. ESTRUCTURA
    col_a, col_b = st.columns(2)
    with col_a:
        # Nombres limpios para los modos
        modo = st.selectbox("Modo de Patrón", ["Repetición (Secuencial)", "Caleidoscopio (Reflejo)"])
    with col_b:
        # Resolución mínima cambiada a 2
        grid_size = st.select_slider("Resolución", options=[2, 4, 8, 12, 16, 20, 24], value=8)

    # 3. SELECTOR DE FORMAS
    st.markdown("---")
    st.write("Selección de Formas")
    nombres_formas = list(FORMAS_DISPONIBLES.keys())
    
    if modo == "Repetición (Secuencial)":
        st.caption("Elige las formas para crear tu secuencia lógica.")
        seleccion = st.multiselect(
            "Formas activas:",
            options=nombres_formas,
            default=nombres_formas[:3],
            label_visibility="collapsed"
        )
        formas_seleccionadas = [FORMAS_DISPONIBLES[k] for k in seleccion]
        if not formas_seleccionadas:
            formas_seleccionadas = ['solid'] # Fallback
    else:
        # En modo caleidoscopio, usamos una selección predefinida para asegurar buen resultado
        st.caption("Se utilizará una selección optimizada de formas para el caleidoscopio.")
        formas_seleccionadas = ['triangle', 'quarter_circle', 'bow', 'strip', 'diamond']

    st.write("") 
    
    # --- LOGICA DEL BOTÓN ---
    if 'seed' not in st.session_state:
        st.session_state.seed = 0
        
    if st.button("GENERAR PATRÓN"):
        st.session_state.seed += 1

# --- MOTOR DE RENDERIZADO HD ---

def add_tile_hd(ax, x, y, type, rot, c_main, c_acc):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def patch(p):
        p.set_antialiased(False); p.set_linewidth(0); ax.add_patch(p)

    # 1. Fondo base (Blanco)
    patch(patches.Rectangle((x, y), 1, 1, color='#FFFFFF')) 
    
    # 2. Formas (CORREGIDAS PARA NO SALIRSE)
    if type == 'solid':
        patch(patches.Rectangle((x, y), 1, 1, color=c_main))
    elif type == 'triangle': 
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        p.set_transform(tr); patch(p)
    elif type == 'quarter_circle': 
        w = patches.Wedge((x, y), 1, 0, 90, color=c_main)
        w.set_transform(tr); patch(w)
    elif type == 'strip': 
        # Banda horizontal centrada (se mantiene dentro)
        r = patches.Rectangle((x, y+0.25), 1, 0.5, color=c_main)
        r.set_transform(tr); patch(r)
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

    # 3. RETÍCULA INTERIOR (FINA Y SUTIL)
    grid_line = patches.Rectangle(
        (x, y), 1, 1, fill=False, 
        edgecolor='#000000', linewidth=0.25, alpha=0.2, zorder=100, antialiased=True
    )
    ax.add_patch(grid_line)

# --- GENERACIÓN DE PATRONES LÓGICOS + VARIACIÓN CONTROLADA ---

def generate_logical_pattern(size, palette, mode, allowed_shapes):
    rng = random.Random(st.session_state.seed)
    
    current_shapes = allowed_shapes.copy()
    current_palette = palette.copy()
    
    rng.shuffle(current_shapes)
    rng.shuffle(current_palette)
    
    rotation_offset = rng.randint(0, 3) 
    pattern_shift = rng.randint(0, 10)
    
    grid = [[None for _ in range(size)] for _ in range(size)]
    num_shapes = len(current_shapes)
    num_colors = len(current_palette)
    
    if mode == "Repetición (Secuencial)":
        for r in range(size):
            for c in range(size):
                shape_idx = (r + c + pattern_shift) % num_shapes
                tipo = current_shapes[shape_idx]
                rot = ((r + c) % 2 + rotation_offset) % 4
                c1_idx = r % num_colors
                c1 = current_palette[c1_idx]
                c2 = current_palette[(c1_idx + 1) % num_colors]
                grid[r][c] = {'type': tipo, 'rot': rot, 'c_main': c1, 'c_acc': c2}

    else: # Caleidoscopio con Lógica de Bloques Grandes (Coherencia a alta resolución)
        seed_size = size // 2
        
        # Definimos el tamaño del "bloque lógico" para que no sea celda a celda
        # Si la resolución es alta (ej. 16), el bloque será de 4x4, creando formas grandes.
        # Si es baja (ej. 4), el bloque será de 1x1 o 2x2.
        block_size = max(1, seed_size // 2) 

        for r_block in range(0, seed_size, block_size):
            for c_block in range(0, seed_size, block_size):
                
                # Decisiones para TODO el bloque (coherencia)
                # Usamos las coordenadas del bloque para la lógica determinista
                block_id = (r_block // block_size) + (c_block // block_size)
                
                shape_idx = (block_id + pattern_shift) % num_shapes
                block_tipo = current_shapes[shape_idx]
                
                # Rotación base para el bloque
                block_rot = (block_id + rotation_offset) % 4
                
                # Colores para el bloque
                c1_idx = (r_block // block_size) % num_colors
                c1 = current_palette[c1_idx]
                c2 = current_palette[(c1_idx + 1) % num_colors]

                # Rellenar las celdas dentro del bloque
                for r_rel in range(block_size):
                    for c_rel in range(block_size):
                        r = r_block + r_rel
                        c = c_block + c_rel
                        
                        # Si nos salimos de la semilla, parar
                        if r >= seed_size or c >= seed_size: continue
                        
                        # Lógica interna del bloque para formar figuras grandes
                        # Por ejemplo, si es un triángulo, orientarlo hacia el centro del bloque
                        cell_rot = block_rot
                        if block_tipo == 'triangle' or block_tipo == 'quarter_circle':
                            # Lógica simple para orientar esquinas hacia el centro
                            if r_rel < block_size/2 and c_rel < block_size/2: cell_rot = 0
                            elif r_rel < block_size/2: cell_rot = 1
                            elif c_rel < block_size/2: cell_rot = 3
                            else: cell_rot = 2
                            # Añadir la rotación base del bloque
                            cell_rot = (cell_rot + block_rot) % 4

                        cell = {'type': block_tipo, 'rot': cell_rot, 'c_main': c1, 'c_acc': c2}
                        
                        # Aplicar espejos
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
            
            add_tile_hd(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    # Marco Exterior Minimalista
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    return fig

# --- EJECUCIÓN ---

# Generamos usando la semilla del estado
grid_data = generate_logical_pattern(grid_size, paleta_actual, modo, formas_seleccionadas)
figura = render_final(grid_data, grid_size)

st.pyplot(figura)

# Botón de descarga
buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR IMAGEN HD", data=buf.getvalue(), file_name="patron.png", mime="image/png")
