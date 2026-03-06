import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import random
from io import BytesIO

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="SISTEMA MODULAR", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS BRUTALISTAS ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    
    h1 { 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        font-weight: 900; 
        color: #111; 
        margin-bottom: 0px;
        font-size: 3.5rem !important;
        text-transform: uppercase;
        letter-spacing: -2px;
    }
    .signature {
        color: #111;
        font-weight: bold;
        font-size: 16px;
        margin-top: -10px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    /* BOTON PRINCIPAL (BARRA LATERAL) */
    .stButton>button:first-child { 
        width: 100%; 
        border: 4px solid #111 !important; 
        border-radius: 0px !important;
        font-weight: 900 !important; 
        font-size: 18px !important;
        background-color: #111 !important; 
        color: #FFF !important; 
        padding: 15px 0px !important; 
        text-transform: uppercase;
        transition: all 0.2s;
    }
    .stButton>button:first-child:hover {
        background-color: #FFF !important;
        color: #111 !important;
    }

    /* BOTONES SECUNDARIOS (DESCARGAS) */
    .stDownloadButton>button {
        width: 100%;
        border: 2px solid #111 !important;
        border-radius: 0px !important;
        font-weight: bold !important;
        background-color: #FFF !important;
        color: #111 !important;
        padding: 12px 0px !important;
        text-transform: uppercase;
    }
    .stDownloadButton>button:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* ESTILOS BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 2px solid #111;
    }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO ---
if 'seed' not in st.session_state:
    st.session_state.seed = random.randint(0, 999999)

# --- PANEL DE CONTROL LATERAL (SIEMPRE VISIBLE) ---
with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    st.markdown("---")
    
    n_colores = st.slider("CANTIDAD DE TINTAS", 1, 5, 3)
    
    cols = st.columns(n_colores)
    colores_usuario = []
    defaults = ["#111111", "#E31C24", "#006BA6", "#FFD500", "#F2F2F2"]
    
    for i, col in enumerate(cols):
        with col:
            c = st.color_picker(f"C{i+1}", defaults[i])
            colores_usuario.append(c)

    st.markdown("---")
    complejidad = st.select_slider("RESOLUCION GRILLA", options=[2, 4, 6, 8, 10, 12], value=6)
    densidad = st.slider("DENSIDAD DE FORMAS", 0.1, 1.0, 0.95)
    
    st.markdown("---")
    if st.button("GENERAR NUEVA ESTRUCTURA"):
        st.session_state.seed = random.randint(0, 999999)

# --- AREA PRINCIPAL (LIENZO) ---
st.markdown("<h1>SISTEMA MODULAR</h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>by Nico.Bastida</p>", unsafe_allow_html=True)

# --- MOTOR DE FORMAS ---
def draw_bauhaus_tile(ax, x, y, tipo, rot, color_forma, color_acento):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0))
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#111111', linewidth=1.5, zorder=10))

    if tipo == 'circle':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.45, color=color_forma))
        
    elif tipo == 'quarter_circle':
        w = patches.Wedge((x, y), 1, 0, 90, color=color_forma)
        w.set_transform(tr)
        ax.add_patch(w)
        
    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=color_forma)
        p.set_transform(tr)
        ax.add_patch(p)
        
    elif tipo == 'bullseye':
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.45, color=color_forma))
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.20, color=color_acento))
        
    elif tipo == 'concentric_squares':
        ax.add_patch(patches.Rectangle((x+0.1, y+0.1), 0.8, 0.8, color=color_forma))
        ax.add_patch(patches.Rectangle((x+0.3, y+0.3), 0.4, 0.4, color=color_acento))

    elif tipo == 'truchet_lines':
        w1 = patches.Wedge((x, y), 0.6, 0, 90, width=0.2, color=color_forma)
        w2 = patches.Wedge((x+1, y+1), 0.6, 180, 270, width=0.2, color=color_forma)
        w1.set_transform(tr)
        w2.set_transform(tr)
        ax.add_patch(w1)
        ax.add_patch(w2)

    elif tipo == 'pill_cross':
        r1 = patches.FancyBboxPatch((x+0.35, y+0.1), 0.3, 0.8, boxstyle="round,pad=0.05", color=color_forma)
        r2 = patches.FancyBboxPatch((x+0.1, y+0.35), 0.8, 0.3, boxstyle="round,pad=0.05", color=color_acento)
        r1.set_transform(tr)
        r2.set_transform(tr)
        ax.add_patch(r1)
        ax.add_patch(r2)

    elif tipo == 'half_split':
        r = patches.Rectangle((x, y), 0.5, 1, color=color_forma)
        r.set_transform(tr)
        ax.add_patch(r)

def generate_grid(size, user_colors, density):
    seed_size = size // 2
    tile_types = [
        'circle', 'quarter_circle', 'triangle', 'bullseye', 
        'concentric_squares', 'truchet_lines', 'pill_cross', 'half_split', 'solid'
    ]
    
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

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=8, zorder=20)
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0,0)
    return fig

# --- EJECUCION ---
random.seed(st.session_state.seed)
grid_data = generate_grid(complejidad, colores_usuario, densidad)
figura = render_final(grid_data, complejidad)

# --- CENTRAR LA IMAGEN Y BOTONES DE DESCARGA ---
col_vacia1, col_centro, col_vacia2 = st.columns([1, 2, 1])

with col_centro:
    st.pyplot(figura, use_container_width=True)
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        buf_png = BytesIO()
        figura.savefig(buf_png, format="png", bbox_inches='tight', pad_inches=0.05, dpi=300, facecolor="#ffffff")
        st.download_button(
            label="DESCARGAR PNG",
            data=buf_png.getvalue(),
            file_name=f"modulo_{st.session_state.seed}.png",
            mime="image/png"
        )
    
    with col_d2:
        buf_svg = BytesIO()
        figura.savefig(buf_svg, format="svg", bbox_inches='tight', pad_inches=0.05, facecolor="#ffffff")
        st.download_button(
            label="DESCARGAR SVG",
            data=buf_svg.getvalue(),
            file_name=f"modulo_{st.session_state.seed}.svg",
            mime="image/svg+xml"
        )
