import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Bauhaus", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; color: #111; }
    div.stButton > button { 
        width: 100%; border: 2px solid #111; font-weight: bold; background-color: #fff; color: #111; 
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #111; color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.title("BAUHANICO")
st.markdown("### *PATRONES BAUHAUS PARA NOSTÁLGICOS*")

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.header("Configuración de Tinta")

# 1. Selector de Cantidad de Colores
n_colores = st.sidebar.slider("¿Cuántos colores quieres usar?", 1, 5, 3)

# 2. Selectores de Color Dinámicos
st.sidebar.markdown("---")
st.sidebar.write(f"Elige tus {n_colores} colores:")

colores_usuario = []
defaults = ["#111111", "#D92B2B", "#2B5CD9", "#F2C84B", "#333333"] # Negro, Rojo, Azul, Amarillo, Gris

for i in range(n_colores):
    c = st.sidebar.color_picker(f"Color {i+1}", defaults[i])
    colores_usuario.append(c)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Geometría")
complejidad = st.sidebar.select_slider("Complejidad (Grid)", options=[2, 4, 6, 8, 12], value=4)
densidad = st.sidebar.slider("Densidad de Formas", 0.1, 1.0, 0.9)

if 'seed' not in st.session_state:
    st.session_state.seed = 0

if st.sidebar.button("🎲 GENERAR NUEVO DISEÑO"):
    st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO (Actualizado para Fondo Blanco) ---

def draw_bauhaus_tile(ax, x, y, tipo, rot, color_forma, color_acento):
    """
    Dibuja una baldosa sobre fondo blanco.
    """
    # Transformación para rotación centrada
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData

    # 1. FONDO SIEMPRE BLANCO
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0))
    
    # 2. BORDE FINO (El marco de la baldosa)
    # Dibujamos un rectángulo sin relleno (fill=False) con borde negro fino
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#111111', linewidth=0.5, zorder=5))

    # 3. FORMAS (Usando los colores elegidos)
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
        r1 = patches.Rectangle((x+0.35, y), 0.3, 1, color=color_forma)
        r2 = patches.Rectangle((x, y+0.35), 1, 0.3, color=color_forma)
        ax.add_patch(r1)
        ax.add_patch(r2)

# --- MOTOR DE GENERACIÓN ---

def generate_grid(size, user_colors, density):
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
                c_main = '#FFFFFF' # Transparente/Blanco
                c_acc = '#FFFFFF'
            else:
                tipo = random.choice(tile_types)
                # Elegir colores de la lista del usuario
                # Esto asegura que SIEMPRE se usen tus colores para las formas
                c_main = random.choice(user_colors)
                # Para el acento, intentamos coger uno distinto si hay más de 1 color
                if len(user_colors) > 1:
                    avail = [c for c in user_colors if c != c_main]
                    if avail:
                        c_acc = random.choice(avail)
                    else:
                        c_acc = c_main
                else:
                    c_acc = c_main

            rot = random.randint(0, 3)
            
            row.append({'type': tipo, 'rot': rot, 'c_main': c_main, 'c_acc': c_acc})
        seed.append(row)

    # 2. Reflejos (Mirroring) para crear la composición completa
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

def render_final(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Dibujar baldosas
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

            draw_bauhaus_tile(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    # Marco Exterior Grueso (Negro)
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=4)
    
    return fig

# --- EJECUCIÓN ---

random.seed(st.session_state.seed)

grid_data = generate_grid(complejidad, colores_usuario, densidad)
figura = render_final(grid_data, complejidad)

col_img, col_info = st.columns([3, 1])

with col_img:
    st.pyplot(figura)

with col_info:
    st.markdown("### Tu Diseño")
    st.info(f"Colores: {len(colores_usuario)}")
    
    from io import BytesIO
    buf = BytesIO()
    figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
    st.download_button(
        label="⬇️ Descargar",
        data=buf.getvalue(),
        file_name="bauhaus_kuki_final.png",
        mime="image/png"
    )
