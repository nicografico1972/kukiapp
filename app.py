import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import random
import math
from io import BytesIO

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="nico.bastida", layout="wide", initial_sidebar_state="expanded")

# --- CALLBACK PARA EL BOTON GENERAR ---
def generar_nueva_semilla():
    st.session_state.seed = random.randint(0, 999999)

# --- ESTADO INICIAL ---
if 'seed' not in st.session_state:
    st.session_state.seed = random.randint(0, 999999)

# --- ESTILOS CSS (MINIMALISTA PURO) ---
st.markdown("""
    <style>
    .main, .block-container { 
        background-color: #000000 !important; 
        padding-top: 1rem !important;
    }
    
    .signature_top {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 900;
        font-size: 20px;
        text-transform: uppercase;
        letter-spacing: -1px;
        margin-bottom: 20px;
        text-align: left;
    }

    [data-testid="stSidebar"] {
        background-color: #E5E5E5 !important;
        border-right: 2px solid #FFF;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    div.stButton > button {
        border: 4px solid #FFFFFF !important;
        border-radius: 0px !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        padding: 15px 30px !important;
        text-transform: uppercase;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .stDownloadButton>button {
        width: 100%;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        font-weight: bold !important;
        background-color: #E5E5E5 !important;
        color: #000000 !important;
        padding: 10px 0px !important;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .stDownloadButton>button:hover {
        background-color: #000000 !important;
        color: #E5E5E5 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- PANEL DE CONTROL LATERAL ---
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
    st.markdown("### DESCARGAR")
    
    random.seed(st.session_state.seed)
    buf_png = BytesIO()
    buf_svg = BytesIO()

# --- AREA PRINCIPAL ---
st.markdown("<p class='signature_top'>nico.bastida</p>", unsafe_allow_html=True)

# --- NUEVAS PRIMITIVAS MATEMATICAS AVANZADAS ---
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
        
    elif tipo == 'truchet_lines':
        w1 = patches.Wedge((x, y), 0.6, 0, 90, width=0.2, color=color_forma)
        w2 = patches.Wedge((x+1, y+1), 0.6, 180, 270, width=0.2, color=color_forma)
        w1.set_transform(tr)
        w2.set_transform(tr)
        ax.add_patch(w1)
        ax.add_patch(w2)

    # --- NUEVAS FORMAS INSPIRADAS EN LA IMAGEN DE REFERENCIA ---

    elif tipo == 'network_nodes':
        # Nodos conectados por lineas (Estilo conectividad/molecula)
        # Lineas primero para que queden debajo
        ax.plot([x+0.2, x+0.8], [y+0.2, y+0.8], color=color_forma, linewidth=8, transform=tr)
        ax.plot([x+0.2, x+0.8], [y+0.8, y+0.2], color=color_forma, linewidth=8, transform=tr)
        # Puntos en las intersecciones y centro
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.2, color=color_acento, transform=tr))
        ax.add_patch(patches.Circle((x+0.2, y+0.2), 0.1, color=color_forma, transform=tr))
        ax.add_patch(patches.Circle((x+0.8, y+0.8), 0.1, color=color_forma, transform=tr))
        ax.add_patch(patches.Circle((x+0.2, y+0.8), 0.1, color=color_forma, transform=tr))
        ax.add_patch(patches.Circle((x+0.8, y+0.2), 0.1, color=color_forma, transform=tr))

    elif tipo == 'concentric_arcs':
        # Arcos de radar / Ondas
        w1 = patches.Wedge((x+0.5, y), 0.9, 0, 180, width=0.15, color=color_forma)
        w2 = patches.Wedge((x+0.5, y), 0.6, 0, 180, width=0.15, color=color_acento)
        w3 = patches.Wedge((x+0.5, y), 0.3, 0, 180, width=0.15, color=color_forma)
        w1.set_transform(tr)
        w2.set_transform(tr)
        w3.set_transform(tr)
        ax.add_patch(w1)
        ax.add_patch(w2)
        ax.add_patch(w3)

    elif tipo == 'chain_links':
        # Eslabones o anillos entrelazados
        w1 = patches.Wedge((x+0.35, y+0.35), 0.25, 0, 360, width=0.12, color=color_forma)
        w2 = patches.Wedge((x+0.65, y+0.65), 0.25, 0, 360, width=0.12, color=color_acento)
        w1.set_transform(tr)
        w2.set_transform(tr)
        ax.add_patch(w1)
        ax.add_patch(w2)

    elif tipo == 'radial_burst':
        # Corona de puntos radiales
        cx, cy = x + 0.5, y + 0.5
        radio_anillo = 0.35
        for i in range(8):
            angulo = i * (math.pi / 4)
            px = cx + radio_anillo * math.cos(angulo)
            py = cy + radio_anillo * math.sin(angulo)
            ax.add_patch(patches.Circle((px, py), 0.08, color=color_forma, transform=tr))
        # Centro vacio o con punto de contraste
        if random.random() > 0.5:
            ax.add_patch(patches.Circle((cx, cy), 0.15, color=color_acento, transform=tr))

    elif tipo == 'split_ring':
        # Anillo partido / C (Efecto op art al girar)
        w1 = patches.Wedge((x+0.5, y+0.5), 0.4, 90, 270, width=0.2, color=color_forma)
        w2 = patches.Wedge((x+0.5, y+0.5), 0.4, 270, 450, width=0.2, color=color_acento)
        w1.set_transform(tr)
        w2.set_transform(tr)
        ax.add_patch(w1)
        ax.add_patch(w2)

    elif tipo == 'pinwheel':
        # Molinete o aspas
        p1 = patches.Wedge((x+0.5, y+0.5), 0.4, 0, 90, color=color_forma)
        p2 = patches.Wedge((x+0.5, y+0.5), 0.4, 180, 270, color=color_acento)
        p1.set_transform(tr)
        p2.set_transform(tr)
        ax.add_patch(p1)
        ax.add_patch(p2)

def generate_grid(size, user_colors, density):
    seed_size = size // 2
    # Catalogo actualizado con las nuevas topologias
    tile_types = [
        'circle', 'quarter_circle', 'triangle', 'truchet_lines', 
        'network_nodes', 'concentric_arcs', 'chain_links', 
        'radial_burst', 'split_ring', 'pinwheel', 'solid'
    ]
    
    random.seed(st.session_state.seed)
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
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#000000')
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

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111111', linewidth=12, zorder=20)
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0,0)
    return fig

# --- EJECUCION ---
random.seed(st.session_state.seed)
grid_data = generate_grid(complejidad, colores_usuario, densidad)
figura = render_final(grid_data, complejidad)

col_vacia1, col_centro, col_vacia2 = st.columns([1, 2, 1])
with col_centro:
    st.pyplot(figura, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- BOTON NUEVO (DERECHA) ---
    col_bottom_left, col_bottom_right = st.columns([3, 1])
    with col_bottom_right:
        st.button("NUEVO", on_click=generar_nueva_semilla, use_container_width=True)

# --- DESCARGAS (BARRA LATERAL) ---
with st.sidebar:
    buf_png = BytesIO()
    figura.savefig(buf_png, format="png", bbox_inches='tight', pad_inches=0.05, dpi=300, facecolor="#ffffff")
    st.download_button(
        label="DESCARGAR PNG",
        data=buf_png.getvalue(),
        file_name=f"modulo_{st.session_state.seed}.png",
        mime="image/png"
    )

    buf_svg = BytesIO()
    figura.savefig(buf_svg, format="svg", bbox_inches='tight', pad_inches=0.05, facecolor="#ffffff")
    st.download_button(
        label="DESCARGAR SVG",
        data=buf_svg.getvalue(),
        file_name=f"modulo_{st.session_state.seed}.svg",
        mime="image/svg+xml"
    )
