import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NICOESCHER", layout="centered")

# --- ESTILOS CSS (UI MÓVIL MEJORADA) ---
st.markdown("""
    <style>
    /* Fondo general */
    .main { background-color: #ffffff; }
    
    /* Títulos */
    h1 { 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        font-weight: 800; 
        color: #111; 
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-bottom: 20px;
    }

    /* ESTILO DEL PANEL DE CONTROL (EXPANDER) */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border: 2px solid #111;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
        color: #111;
    }
    .streamlit-expanderContent {
        border: 2px solid #111;
        border-top: none;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        background-color: #ffffff;
        padding: 20px;
    }

    /* BOTONES */
    div.stButton > button { 
        width: 100%; 
        border: 3px solid #111; 
        border-radius: 8px;
        font-weight: 800; 
        font-size: 16px;
        background-color: #fff; 
        color: #111; 
        padding: 15px 0px; /* Más alto para dedos en móvil */
        transition: all 0.2s;
        box-shadow: 4px 4px 0px #111; /* Sombra dura estilo Bauhaus */
    }
    div.stButton > button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #111;
    }
    div.stButton > button:active {
        transform: translate(2px, 2px);
        box-shadow: 1px 1px 0px #111;
        background-color: #f0f0f0;
    }
    
    /* Ajuste de columnas en móvil */
    [data-testid="column"] {
        min-width: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Generador Bauhaus Puro (HD)</p>", unsafe_allow_html=True)

# --- PANEL DE CONTROL VISIBLE ---
with st.expander("🎛️ TOCAME PARA EDITAR (CONTROLES)", expanded=True):
    
    st.write("### 1. Tinta y Color")
    n_colores = st.slider("¿Cuántos colores de tinta?", 1, 5, 3)
    
    cols = st.columns(n_colores)
    colores_usuario = []
    # Colores por defecto inspirados en tu imagen de referencia
    defaults = ["#111111", "#D92B2B", "#2B5CD9", "#F2C84B", "#3A7D44"]
    
    for i, col in enumerate(cols):
        with col:
            c = st.color_picker(f"C{i+1}", defaults[i])
            colores_usuario.append(c)

    st.markdown("---")
    st.write("### 2. Geometría")
    
    c_geo1, c_geo2 = st.columns(2)
    with c_geo1:
        complejidad = st.select_slider("Complejidad", options=[2, 4, 6, 8, 12], value=4)
    with c_geo2:
        densidad = st.slider("Densidad", 0.1, 1.0, 0.9)

    st.markdown("---")
    
    if 'seed' not in st.session_state:
        st.session_state.seed = 0

    if st.button("🎲 ¡GENERAR DISEÑO NUEVO!"):
        st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO (RENDERIZADO HD) ---

def add_patch_hd(ax, patch):
    """Helper para añadir parches con renderizado nítido."""
    # Desactiva el antialiasing para bordes perfectos
    patch.set_antialiased(False)
    # Asegura que no haya borde invisible que cause artefactos
    patch.set_linewidth(0)
    ax.add_patch(patch)

def draw_bauhaus_tile(ax, x, y, tipo, rot, color_forma, color_acento):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData

    # 1. FONDO BLANCO (HD)
    bg = patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0)
    add_patch_hd(ax, bg)
    
    # 2. BORDE FINO (El único que sí queremos con antialiasing para que se vea bien)
    # Usamos un truco: dibujar un rectángulo ligeramente más pequeño con borde
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#111111', linewidth=0.5, zorder=5, antialiased=True))

    # 3. FORMAS (HD)
    if tipo == 'circle':
        p = patches.Circle((x+0.5, y+0.5), 0.4, color=color_forma)
        add_patch_hd(ax, p)
    elif tipo == 'quarter_circle':
        w = patches.Wedge((x, y), 1, 0, 90, color=color_forma)
        w.set_transform(tr)
        add_patch_hd(ax, w)
    elif tipo == 'half_circle':
        w = patches.Wedge((x+0.5, y+0.5), 0.5, 0, 180, color=color_forma)
        w.set_transform(tr)
        add_patch_hd(ax, w)
    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=color_forma)
        p.set_transform(tr)
        add_patch_hd(ax, p)
    elif tipo == 'rectangles':
        r1 = patches.Rectangle((x, y), 0.5, 1, color=color_forma)
        r2 = patches.Rectangle((x+0.5, y+0.2), 0.5, 0.8, color=color_acento)
        r1.set_transform(tr)
        r2.set_transform(tr)
        add_patch_hd(ax, r1)
        add_patch_hd(ax, r2)
    elif tipo == 'arch':
        w1 = patches.Wedge((x+0.5, y), 0.5, 0, 180, color=color_forma)
        w1.set_transform(tr)
        add_patch_hd(ax, w1)
    elif tipo == 'diagonal_split':
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=color_forma)
        p.set_transform(tr)
        add_patch_hd(ax, p)
    elif tipo == 'bullseye':
        c1 = patches.Circle((x+0.5, y+0.5), 0.45, color=color_forma)
        c2 = patches.Circle((x+0.5, y+0.5), 0.25, color=color_acento)
        add_patch_hd(ax, c1)
        add_patch_hd(ax, c2)
    elif tipo == 'cross':
        r1 = patches.Rectangle((x+0.35, y), 0.3, 1, color=color_forma)
        r2 = patches.Rectangle((x, y+0.35), 1, 0.3, color=color_forma)
        add_patch_hd(ax, r1)
        add_patch_hd(ax, r2)

# --- MOTOR DE GENERACIÓN ---

def generate_grid(size, user_colors, density):
    seed_size = size // 2
    tile_types = ['circle', 'quarter_circle', 'half_circle', 'triangle', 
                  'rectangles', 'arch', 'diagonal_split', 'bullseye', 'cross', 'solid']
    
    seed = []
    for _ in range(seed_size):
        row = []
        for _ in range(seed_size):
            if random.random() > density:
                tipo = 'solid'
                c_main = '#FFFFFF'
                c_acc = '#FFFFFF'
            else:
                tipo = random.choice(tile_types)
                c_main = random.choice(user_colors)
                if len(user_colors) > 1:
                    avail = [c for c in user_colors if c != c_main]
                    c_acc = random.choice(avail) if avail else c_main
                else:
                    c_acc = c_main

            rot = random.randint(0, 3)
            row.append({'type': tipo, 'rot': rot, 'c_main': c_main, 'c_acc': c_acc})
        seed.append(row)

    full_grid = [[None for _ in range(size)] for _ in range(size)]
    for r in range(seed_size):
        for c in range(seed_size):
            cell = seed[r][c]
            full_grid[r][c] = cell # Top-Left
            
            tr_cell = cell.copy()
            tr_cell['mirror_x'] = True 
            full_grid[r][size - 1 - c] = tr_cell # Top-Right
            
            bl_cell = cell.copy()
            bl_cell['mirror_y'] = True
            full_grid[size - 1 - r][c] = bl_cell # Bot-Left
            
            br_cell = cell.copy()
            br_cell['mirror_x'] = True
            br_cell['mirror_y'] = True
            full_grid[size - 1 - r][size - 1 - c] = br_cell # Bot-Right
            
    return full_grid

def render_final(grid, size):
    # Aumentamos el DPI de la figura base para mayor resolución
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            x, y = c, size - 1 - r
            rot = cell['rot']
            
            if cell.get('mirror_x'):
                rot = {0:1, 1:0, 2:3, 3:2}[rot]
            if cell.get('mirror_y'):
                rot = {0:3, 1:2, 2:1, 3:0}[rot]

            draw_bauhaus_tile(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    # Marco Exterior Grueso (Negro)
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    
    return fig

# --- RENDERIZADO VISUAL ---

random.seed(st.session_state.seed)

grid_data = generate_grid(complejidad, colores_usuario, densidad)
figura = render_final(grid_data, complejidad)

st.pyplot(figura)

# Botón de descarga (Alta Resolución real)
buf = BytesIO()
# Guardamos con DPI muy alto y sin antialiasing en el guardado
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(
    label="⬇️ Descargar Imagen en HD (Nítida)",
    data=buf.getvalue(),
    file_name="bauhaus_kuki_hd.png",
    mime="image/png"
)
