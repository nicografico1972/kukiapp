import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Bauhaus Edition", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    div.stButton > button { width: 100%; border: 2px solid black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.title("KUKIAPP")
st.markdown("### *Generador de Patrones Bauhaus*")

# --- BARRA LATERAL ---
st.sidebar.header("🎨 Paleta de Color")
st.sidebar.markdown("Selecciona 5 colores para tu composición.")

c1 = st.sidebar.color_picker("Fondo", "#F0F0F0")
c2 = st.sidebar.color_picker("Principal", "#111111")
c3 = st.sidebar.color_picker("Acento 1", "#D92B2B")
c4 = st.sidebar.color_picker("Acento 2", "#2B5CD9")
c5 = st.sidebar.color_picker("Acento 3", "#F2C84B")

PALETA_USUARIO = [c1, c2, c3, c4, c5]

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Geometría")
complejidad = st.sidebar.select_slider("Complejidad (Grid)", options=[2, 4, 6, 8, 12], value=4)
densidad = st.sidebar.slider("Densidad de Formas", 0.1, 1.0, 0.9)

if 'seed' not in st.session_state:
    st.session_state.seed = 0

if st.sidebar.button("🎲 GENERAR NUEVO DISEÑO"):
    st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO BAUHAUS (CORREGIDO) ---

def draw_bauhaus_tile(ax, x, y, tipo, rot, colors):
    """
    Dibuja una baldosa estilo Bauhaus en (x,y).
    Usa 'tipo' consistentemente para evitar errores.
    """
    bg = colors[0]
    fg = colors[1]
    acc = colors[2] if len(colors) > 2 else fg

    # Transformación para rotación centrada
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData

    # 1. Fondo
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color=bg))

    # 2. Formas Puras
    if tipo == 'circle':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.4, color=fg))

    elif tipo == 'quarter_circle':
        w = patches.Wedge((x, y), 1, 0, 90, color=fg)
        w.set_transform(tr)
        ax.add_patch(w)

    elif tipo == 'half_circle':  # <--- AQUÍ ESTABA EL ERROR, CORREGIDO A 'tipo'
        w = patches.Wedge((x+0.5, y+0.5), 0.5, 0, 180, color=fg)
        w.set_transform(tr)
        ax.add_patch(w)

    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)

    elif tipo == 'rectangles':
        r1 = patches.Rectangle((x, y), 0.5, 1, color=fg)
        r2 = patches.Rectangle((x+0.5, y+0.2), 0.5, 0.8, color=acc)
        r1.set_transform(tr)
        r2.set_transform(tr)
        ax.add_patch(r1)
        ax.add_patch(r2)
        
    elif tipo == 'arch':
        w1 = patches.Wedge((x+0.5, y), 0.5, 0, 180, color=fg)
        w1.set_transform(tr)
        ax.add_patch(w1)

    elif tipo == 'diagonal_split':
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)
        
    elif tipo == 'bullseye':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.45, color=fg))
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.25, color=acc))
        
    elif tipo == 'cross':
        r1 = patches.Rectangle((x+0.35, y), 0.3, 1, color=fg)
        r2 = patches.Rectangle((x, y+0.35), 1, 0.3, color=fg)
        ax.add_patch(r1)
        ax.add_patch(r2)

# --- MOTOR DE SIMETRÍA ---

def generate_harmonic_grid(size, palette, density):
    seed_size = size // 2
    tile_types = ['circle', 'quarter_circle', 'half_circle', 'triangle', 
                  'rectangles', 'arch', 'diagonal_split', 'bullseye', 'cross', 'solid']
    
    # 1. Generar Semilla
    seed = []
    for _ in range(seed_size):
        row = []
        for _ in range(seed_size):
            if random.random() > density:
                tipo = 'solid'
            else:
                tipo = random.choice(tile_types)
                
            rot = random.randint(0, 3)
            
            # Selección de colores inteligente
            bg_idx = 0 
            avail_colors = [c for i, c in enumerate(palette) if i != bg_idx]
            if not avail_colors: avail_colors = [palette[0]] # Fallback
            selected_cols = random.sample(avail_colors, k=min(2, len(avail_colors)))
            
            final_cols = [palette[bg_idx]] + selected_cols
            
            row.append({'type': tipo, 'rot': rot, 'cols': final_cols})
        seed.append(row)

    # 2. Reflejo (Mirroring)
    full_grid = [[None for _ in range(size)] for _ in range(size)]
    
    for r in range(seed_size):
        for c in range(seed_size):
            cell = seed[r][c]
            
            # Top-Left
            full_grid[r][c] = cell
            
            # Top-Right (Mirror X)
            tr_cell = cell.copy()
            tr_cell['mirror_x'] = True 
            full_grid[r][size - 1 - c] = tr_cell
            
            # Bottom-Left (Mirror Y)
            bl_cell = cell.copy()
            bl_cell['mirror_y'] = True
            full_grid[size - 1 - r][c] = bl_cell
            
            # Bottom-Right (Double Mirror)
            br_cell = cell.copy()
            br_cell['mirror_x'] = True
            br_cell['mirror_y'] = True
            full_grid[size - 1 - r][size - 1 - c] = br_cell
            
    return full_grid

def render_bauhaus(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Fondo global
    # ax.add_patch(patches.Rectangle((0,0), size, size, color=PALETA_USUARIO[0]))

    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            
            x = c
            y = size - 1 - r
            
            rot = cell['rot']
            
            # Ajuste de rotación para espejos
            if cell.get('mirror_x'):
                if rot == 0: rot = 1
                elif rot == 1: rot = 0
                elif rot == 2: rot = 3
                elif rot == 3: rot = 2
                
            if cell.get('mirror_y'):
                if rot == 0: rot = 3
                elif rot == 1: rot = 2
                elif rot == 2: rot = 1
                elif rot == 3: rot = 0

            draw_bauhaus_tile(ax, x, y, cell['type'], rot, cell['cols'])

    # Marco
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=5)
    
    return fig

# --- EJECUCIÓN ---

random.seed(st.session_state.seed)

grid_data = generate_harmonic_grid(complejidad, PALETA_USUARIO, densidad)
figura = render_bauhaus(grid_data, complejidad)

col_img, col_info = st.columns([3, 1])

with col_img:
    st.pyplot(figura)

with col_info:
    st.markdown("### Detalles")
    st.success("Diseño Generado")
    
    from io import BytesIO
    buf = BytesIO()
    figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#f0f2f6")
    st.download_button(
        label="⬇️ Descargar Arte",
        data=buf.getvalue(),
        file_name="bauhaus_kuki.png",
        mime="image/png"
    )
