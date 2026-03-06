import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Bauhaus", layout="centered", initial_sidebar_state="collapsed")

# --- CSS EXTREMO PARA MÓVIL ---
st.markdown("""
    <style>
    /* 1. ELIMINAR MÁRGENES MUERTOS DE STREAMLIT EN MÓVIL */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* 2. TÍTULOS COMPACTOS */
    h1 { 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        font-weight: 900; 
        color: #111; 
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
        font-size: 2.5rem !important;
    }
    .signature {
        text-align: center;
        color: #111;
        font-weight: bold;
        font-size: 14px;
        margin-top: -5px;
        margin-bottom: 15px;
    }

    /* 3. BOTÓN GIGANTE PRINCIPAL */
    .stButton>button:first-child { 
        width: 100%; 
        border: 4px solid #111 !important; 
        border-radius: 12px !important;
        font-weight: 900 !important; 
        font-size: 20px !important;
        background-color: #E31C24 !important; /* Rojo Bauhaus que llama a la acción */
        color: #FFF !important; 
        padding: 20px 0px !important; /* Altura ideal para el pulgar */
        box-shadow: 4px 4px 0px #111 !important;
        margin-bottom: 10px;
    }
    .stButton>button:active {
        transform: translate(4px, 4px);
        box-shadow: 0px 0px 0px #111 !important;
    }

    /* 4. BOTONES DE DESCARGA (Secundarios) */
    .stDownloadButton>button {
        width: 100%;
        border: 2px solid #111 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        background-color: #FFF !important;
        color: #111 !important;
        padding: 12px 0px !important;
        margin-top: 5px;
    }

    /* 5. ACORDEÓN DE AJUSTES COMPACTO */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 2px solid #111;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- INICIALIZAR ESTADO (SEMILLA CAÓTICA) ---
if 'seed' not in st.session_state:
    st.session_state.seed = random.randint(0, 999999)

# --- MENÚ DE AJUSTES (CERRADO POR DEFECTO PARA NO MOLESTAR EN MÓVIL) ---
with st.expander("⚙️ AJUSTES DE DISEÑO (Toca para abrir)", expanded=False):
    st.write("Configura la geometría y luego pulsa generar.")
    
    n_colores = st.slider("Colores de tinta", 1, 5, 3)
    
    # En móvil, dejamos que Streamlit apile los colores o los ponga en fila si caben
    cols = st.columns(n_colores)
    colores_usuario = []
    defaults = ["#111111", "#D92B2B", "#2B5CD9", "#F2C84B", "#333333"]
    
    for i, col in enumerate(cols):
        with col:
            c = st.color_picker(f"C{i+1}", defaults[i])
            colores_usuario.append(c)

    complejidad = st.select_slider("Complejidad de Grilla", options=[2, 4, 6, 8, 12], value=4)
    densidad = st.slider("Densidad de Formas", 0.1, 1.0, 0.9)

# --- BOTÓN DE ACCIÓN PRINCIPAL ---
# Lo ponemos arriba de la imagen para que el dedo no tenga que bajar haciendo scroll
if st.button("🎲 GENERAR NUEVA OBRA"):
    st.session_state.seed = random.randint(0, 999999)

# --- ALFABETO GEOMÉTRICO ---
def draw_bauhaus_tile(ax, x, y, tipo, rot, color_forma, color_acento):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0))
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#111111', linewidth=0.5, zorder=5))

    if tipo == 'circle':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.4, color=color_forma))
    elif tipo == 'quarter_circle':
        w = patches.Wedge((x, y), 1, 0, 90, color=color_forma)
        w.set_transform(tr)
        ax.add_patch(w)
    elif tipo == 'half_circle':
        w = patches.Wedge((x+0.5, y+0.5), 0.5, 0, 180, color=color_forma)
        w.set_transform(tr)
        ax.add_patch(w)
    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=color_forma)
        p.set_transform(tr)
        ax.add_patch(p)
    elif tipo == 'rectangles':
        r1 = patches.Rectangle((x, y), 0.5, 1, color=color_forma)
        r2 = patches.Rectangle((x+0.5, y+0.2), 0.5, 0.8, color=color_acento)
        r1.set_transform(tr)
        r2.set_transform(tr)
        ax.add_patch(r1)
        ax.add_patch(r2)
    elif tipo == 'arch':
        w1 = patches.Wedge((x+0.5, y), 0.5, 0, 180, color=color_forma)
        w1.set_transform(tr)
        ax.add_patch(w1)
    elif tipo == 'diagonal_split':
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=color_forma)
        p.set_transform(tr)
        ax.add_patch(p)
    elif tipo == 'bullseye':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.45, color=color_forma))
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.25, color=color_acento))
    elif tipo == 'cross':
        ax.add_patch(patches.Rectangle((x+0.35, y), 0.3, 1, color=color_forma))
        ax.add_patch(patches.Rectangle((x, y+0.35), 1, 0.3, color=color_forma))

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
                c_main = c_acc = '#FFFFFF'
            else:
                tipo = random.choice(tile_types)
                c_main = random.choice(user_colors)
                avail = [c for c in user_colors if c != c_main] if len(user_colors) > 1 else []
                c_acc = random.choice(avail) if avail else c_main

            rot = random.randint(0, 3)
            row.append({'type': tipo, 'rot': rot, 'c_main': c_main, 'c_acc': c_acc})
        seed.append(row)

    full_grid = [[None for _ in range(size)] for _ in range(size)]
    for r in range(seed_size):
        for c in range(seed_size):
            cell = seed[r][c]
            full_grid[r][c] = cell 
            
            tr_cell = cell.copy()
            tr_cell['mirror_x'] = True 
            full_grid[r][size - 1 - c] = tr_cell 
            
            bl_cell = cell.copy()
            bl_cell['mirror_y'] = True
            full_grid[size - 1 - r][c] = bl_cell 
            
            br_cell = cell.copy()
            br_cell['mirror_x'] = True
            br_cell['mirror_y'] = True
            full_grid[size - 1 - r][size - 1 - c] = br_cell 
            
    return full_grid

def render_final(grid, size):
    # Reducimos un poco el figsize para que renderice más rápido en móviles
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            x, y = c, size - 1 - r
            rot = cell['rot']
            
            if cell.get('mirror_x'): rot = {0:1, 1:0, 2:3, 3:2}[rot]
            if cell.get('mirror_y'): rot = {0:3, 1:2, 2:1, 3:0}[rot]

            draw_bauhaus_tile(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    # Ajustamos márgenes del plot al mínimo
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0,0)
    return fig

# --- RENDERIZADO ---
random.seed(st.session_state.seed)
grid_data = generate_grid(complejidad, colores_usuario, densidad)
figura = render_final(grid_data, complejidad)

# Mostrar imagen ocupando el ancho máximo posible
st.pyplot(figura, use_container_width=True)

# --- DESCARGAS APILADAS (Mejor para pulgares en móvil) ---
buf_png = BytesIO()
figura.savefig(buf_png, format="png", bbox_inches='tight', pad_inches=0.1, dpi=300, facecolor="#ffffff")
st.download_button(
    label="⬇️ Descargar en PNG",
    data=buf_png.getvalue(),
    file_name=f"kuki_{st.session_state.seed}.png",
    mime="image/png"
)

buf_svg = BytesIO()
figura.savefig(buf_svg, format="svg", bbox_inches='tight', pad_inches=0.1, facecolor="#ffffff")
st.download_button(
    label="⬇️ Descargar en Vector (SVG)",
    data=buf_svg.getvalue(),
    file_name=f"kuki_{st.session_state.seed}.svg",
    mime="image/svg+xml"
)
