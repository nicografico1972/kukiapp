import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Bauhaus Edition", layout="wide")

# --- ESTILOS CSS PARA QUE SE VEA ELEGANTE ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; letter-spacing: -1px; }
    div.stButton > button { width: 100%; border-radius: 0px; font-weight: bold; border: 2px solid black; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("KUKIAPP")
    st.markdown("### *Generador de Patrones Bauhaus*")

# --- BARRA LATERAL: RUEDA DE COLOR Y CONTROLES ---
st.sidebar.header("🎨 Paleta de Color")
st.sidebar.markdown("Elige hasta 5 colores. El primero será el fondo dominante.")

color1 = st.sidebar.color_picker("Color 1 (Fondo)", "#F0F0F0") # Blanco sucio típico Bauhaus
color2 = st.sidebar.color_picker("Color 2 (Principal)", "#111111") # Negro
color3 = st.sidebar.color_picker("Color 3 (Acento 1)", "#D92B2B") # Rojo
color4 = st.sidebar.color_picker("Color 4 (Acento 2)", "#2B5CD9") # Azul
color5 = st.sidebar.color_picker("Color 5 (Acento 3)", "#F2C84B") # Amarillo

# Lista activa de colores
PALETA_USUARIO = [color1, color2, color3, color4, color5]

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Geometría")

# Control de complejidad
complejidad = st.sidebar.select_slider("Complejidad de la Retícula", options=[2, 4, 6, 8, 12], value=4)
densidad = st.sidebar.slider("Densidad de Formas", 0.1, 1.0, 0.8)

if 'seed' not in st.session_state:
    st.session_state.seed = 0

if st.sidebar.button("🎲 GENERAR NUEVO DISEÑO"):
    st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO BAUHAUS ---
# Formas puras y funcionales. Sin adornos.

def draw_bauhaus_tile(ax, x, y, tipo, rot, colors):
    """
    Dibuja una baldosa estilo Bauhaus en (x,y).
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
        # Círculo centrado (La forma perfecta)
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.4, color=fg))

    elif tipo == 'quarter_circle':
        # Cuarto de círculo (Esquina) - Clásico Bauhaus
        w = patches.Wedge((x, y), 1, 0, 90, color=fg)
        w.set_transform(tr)
        ax.add_patch(w)

    elif tile_type == 'half_circle':
        # Medio círculo
        w = patches.Wedge((x+0.5, y+0.5), 0.5, 0, 180, color=fg)
        w.set_transform(tr)
        ax.add_patch(w)

    elif tipo == 'triangle':
        # Triángulo simple
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)

    elif tipo == 'rectangles':
        # Composición de rectángulos ortogonales (Mondrian-esque)
        r1 = patches.Rectangle((x, y), 0.5, 1, color=fg)
        r2 = patches.Rectangle((x+0.5, y+0.2), 0.5, 0.8, color=acc)
        r1.set_transform(tr)
        r2.set_transform(tr)
        ax.add_patch(r1)
        ax.add_patch(r2)
        
    elif tipo == 'arch':
        # Arco (Puente)
        w1 = patches.Wedge((x+0.5, y), 0.5, 0, 180, color=fg)
        w1.set_transform(tr)
        ax.add_patch(w1)

    elif tipo == 'diagonal_split':
        # División diagonal limpia
        p = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)
        
    elif tipo == 'bullseye':
        # Círculos concéntricos
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.45, color=fg))
        ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.25, color=acc))
        
    elif tipo == 'cross':
        # Cruz suiza gruesa
        r1 = patches.Rectangle((x+0.35, y), 0.3, 1, color=fg)
        r2 = patches.Rectangle((x, y+0.35), 1, 0.3, color=fg)
        ax.add_patch(r1)
        ax.add_patch(r2)

# --- MOTOR DE SIMETRÍA ARMÓNICA ---

def generate_harmonic_grid(size, palette, density):
    """
    Genera un grid asegurando que las formas se conecten armónicamente.
    """
    seed_size = size // 2
    
    # Pesos ajustados para estética Bauhaus (más curvas y geometría sólida)
    tile_types = ['circle', 'quarter_circle', 'quarter_circle', 'triangle', 
                  'rectangles', 'arch', 'diagonal_split', 'bullseye', 'cross', 'solid']
    
    # Probabilidad de dejar un espacio "vacío" (sólido) para que respete el aire del diseño
    # Bauhaus necesita "aire" (espacio negativo).
    
    # 1. Generar Semilla (Cuadrante Superior Izquierdo)
    seed = []
    for _ in range(seed_size):
        row = []
        for _ in range(seed_size):
            # Decidir si ponemos forma o dejamos espacio (densidad)
            if random.random() > density:
                tipo = 'solid'
            else:
                tipo = random.choice(tile_types)
                
            rot = random.randint(0, 3)
            
            # Selección de colores: Fondo + 1 o 2 colores de la paleta
            # Siempre usamos el color 0 como fondo para consistencia, o variamos ligeramente
            bg_idx = 0 
            # Elegir otros 2 colores distintos al fondo
            avail_colors = [c for i, c in enumerate(palette) if i != bg_idx]
            selected_cols = random.sample(avail_colors, k=min(2, len(avail_colors)))
            
            final_cols = [palette[bg_idx]] + selected_cols
            
            row.append({'type': tipo, 'rot': rot, 'cols': final_cols})
        seed.append(row)

    # 2. Reflejo Armónico (Mirroring)
    full_grid = [[None for _ in range(size)] for _ in range(size)]
    
    for r in range(seed_size):
        for c in range(seed_size):
            cell = seed[r][c]
            
            # --- Lógica de Espejos para Conexión Visual ---
            # Para que un cuarto de círculo se convierta en medio círculo, 
            # el espejo debe invertir la orientación horizontalmente.
            
            # Top-Left
            full_grid[r][c] = cell
            
            # Top-Right (Espejo Horizontal)
            tr_cell = cell.copy()
            tr_cell['mirror_x'] = True 
            full_grid[r][size - 1 - c] = tr_cell
            
            # Bottom-Left (Espejo Vertical)
            bl_cell = cell.copy()
            bl_cell['mirror_y'] = True
            full_grid[size - 1 - r][c] = bl_cell
            
            # Bottom-Right (Espejo Doble)
            br_cell = cell.copy()
            br_cell['mirror_x'] = True
            br_cell['mirror_y'] = True
            full_grid[size - 1 - r][size - 1 - c] = br_cell
            
    return full_grid

def render_bauhaus(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Dibujar
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            
            x = c
            y = size - 1 - r
            
            rot = cell['rot']
            
            # Aplicar lógica de espejo modificando la rotación
            # Esto es clave para que los arcos se toquen
            if cell.get('mirror_x'):
                if rot == 0: rot = 1
                elif rot == 1: rot = 0
                elif rot == 2: rot = 3
                elif rot == 3: rot = 2
                # Formas específicas necesitan cambio de tipo al reflejarse? 
                # Con primitivas básicas, rotación suele bastar si están diseñadas para ello.
                
            if cell.get('mirror_y'):
                if rot == 0: rot = 3
                elif rot == 1: rot = 2
                elif rot == 2: rot = 1
                elif rot == 3: rot = 0

            draw_bauhaus_tile(ax, x, y, cell['type'], rot, cell['cols'])

    # Marco Exterior
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#111', linewidth=5)
    
    return fig

# --- EJECUCIÓN PRINCIPAL ---

random.seed(st.session_state.seed)

# Generar Grid
grid_data = generate_harmonic_grid(complejidad, PALETA_USUARIO, densidad)

# Renderizar
figura = render_bauhaus(grid_data, complejidad)

# Mostrar en Streamlit
col_img, col_info = st.columns([3, 1])

with col_img:
    st.pyplot(figura)

with col_info:
    st.markdown("### Detalles")
    st.info(f"Modo: Simetría Bauhaus")
    st.markdown(f"**Colores:** {len(PALETA_USUARIO)}")
    st.markdown("Usa la **rueda de color** en la izquierda para personalizar tu obra.")
    
    # Botón de Descarga
    from io import BytesIO
    buf = BytesIO()
    figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#f0f2f6")
    st.download_button(
        label="⬇️ Descargar Arte",
        data=buf.getvalue(),
        file_name="bauhaus_kuki.png",
        mime="image/png"
    )
