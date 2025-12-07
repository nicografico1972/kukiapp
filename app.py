import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP", layout="centered")

# --- CABECERA ---
st.markdown("<h1 style='text-align: center; color: #333;'>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666; font-style: italic;'>Patrones kukis</h3>", unsafe_allow_html=True)
st.markdown("---")

# --- PALETAS DE COLOR EXTENDIDAS ---
PALETAS = {
    "Kuki Clásica (Rojo/Verde/Azul/Oro)": ["#B83328", "#3A7D44", "#2C5490", "#D89C37", "#F2ECCE"],
    "Bauhaus (Primarios)": ["#F0F0F0", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"],
    "Retro 70s (Naranja/Café)": ["#3B2518", "#E87A25", "#F2B83D", "#8C4926", "#F0EAD6"],
    "Nórdico (Pastel/Gris)": ["#FFFFFF", "#2F3542", "#A4B0BE", "#FF7F50", "#7BED9F"],
    "Midnight Neon": ["#000000", "#FF00FF", "#00FFFF", "#FFFF00", "#333333"],
    "Tierra y Oliva": ["#F5F5DC", "#556B2F", "#8B4513", "#DAA520", "#2F4F4F"],
    "Azulejo Portugués": ["#FFFFFF", "#003399", "#FFCC00", "#000000", "#6699FF"],
    "Vitamina C": ["#FFFFFF", "#FF9900", "#FFCC00", "#FF3300", "#339900"]
}

# --- LÓGICA DE DIBUJO DE BALDOSAS (EL ALFABETO GEOMÉTRICO) ---
# Cada función dibuja una pieza básica en la coordenada (x,y) de tamaño 1x1

def draw_tile(ax, x, y, tile_type, rotation, colors):
    """
    Dibuja una baldosa específica.
    tile_type: Nombre de la forma
    rotation: 0, 1, 2, 3 (multiplicador de 90 grados)
    colors: Lista de colores [fondo, forma_principal, acento]
    """
    bg = colors[0]
    fg = colors[1]
    acc = colors[2] if len(colors) > 2 else colors[1]

    # Crear transformación para rotación alrededor del centro de la baldosa
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rotation * 90) + ax.transData

    # 1. Fondo base
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color=bg))

    # 2. Formas
    if tile_type == 'solid':
        # Cuadrado sólido (solo cambia el color base si se desea, aquí es redundante pero útil para ritmo)
        ax.add_patch(patches.Rectangle((x, y), 1, 1, color=fg))

    elif tile_type == 'half_triangle':
        # Triángulo rectángulo (mitad del cuadrado)
        # Puntos: (x,y), (x+1, y), (x, y+1) -> Triángulo inferior izquierdo
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)

    elif tile_type == 'stripes':
        # Tres franjas
        # Franja central
        r = patches.Rectangle((x+0.33, y), 0.33, 1, color=fg)
        r.set_transform(tr)
        ax.add_patch(r)
        
    elif tile_type == 'quarter_circle':
        # Cuarto de círculo (esquina)
        w = patches.Wedge((x, y), 1, 0, 90, color=fg)
        w.set_transform(tr)
        ax.add_patch(w)

    elif tile_type == 'frame':
        # Cuadrado dentro de cuadrado (Concéntrico)
        ax.add_patch(patches.Rectangle((x+0.2, y+0.2), 0.6, 0.6, color=fg))
        ax.add_patch(patches.Rectangle((x+0.4, y+0.4), 0.2, 0.2, color=acc))

    elif tile_type == 'diagonal_strip':
        # Franja diagonal (fundamental para lazos y nudos)
        # Polígono de 4 puntos formando una banda diagonal
        pts = [(x, y+0.3), (x, y+0.7), (x+0.7, y), (x+0.3, y)] # Banda inferior izq
        # Mejor hacemos banda central
        pts = [(x, y), (x+0.3, y), (x+1, y+0.7), (x+1, y+1), (x+0.7, y+1), (x, y+0.3)]
        # Simplificado: Triángulo grande - Triángulo pequeño? No, mejor polígono directo.
        # Banda diagonal de esquina a esquina con grosor
        pts = [(x, y), (x+0.4, y), (x+1, y+0.6), (x+1, y+1), (x+0.6, y+1), (x, y+0.4)]
        p = patches.Polygon(pts, color=fg)
        p.set_transform(tr)
        ax.add_patch(p)

    elif tile_type == 'checkers':
        # Ajedrez 2x2
        r1 = patches.Rectangle((x, y), 0.5, 0.5, color=fg)
        r2 = patches.Rectangle((x+0.5, y+0.5), 0.5, 0.5, color=fg)
        r1.set_transform(tr)
        r2.set_transform(tr)
        ax.add_patch(r1)
        ax.add_patch(r2)

    elif tile_type == 'triangle_center':
        # Triángulo apuntando al centro
        p = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=fg)
        p.set_transform(tr)
        ax.add_patch(p)
        
    elif tile_type == 'bow':
        # Dos triángulos opuestos (reloj de arena)
        p1 = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=fg)
        p2 = patches.Polygon([(x, y+1), (x+1, y+1), (x+0.5, y+0.5)], color=acc)
        p1.set_transform(tr)
        p2.set_transform(tr)
        ax.add_patch(p1)
        ax.add_patch(p2)

# --- GENERADOR DE PATRÓN (Cerebro) ---

def generate_mandala_grid(size, n_colors, palette):
    """
    Genera la estructura de datos para un mandala simétrico.
    Estrategia: Generar semilla (Top-Left) y reflejar.
    """
    seed_size = size // 2
    # Tipos de baldosas disponibles con pesos (algunas son más comunes en tus ejemplos)
    tile_types = ['solid', 'half_triangle', 'half_triangle', 'quarter_circle', 
                  'frame', 'stripes', 'diagonal_strip', 'checkers', 'triangle_center', 'bow']
    
    # 1. Crear Semilla (Top-Left)
    seed_grid = []
    for _ in range(seed_size):
        row = []
        for _ in range(seed_size):
            tile = random.choice(tile_types)
            rot = random.randint(0, 3)
            # Elegir colores para esta baldosa
            # Asegurar contraste: bg != fg
            cols = random.sample(palette[:n_colors], k=min(3, n_colors))
            while len(cols) < 3: cols.append(cols[0]) # Rellenar si faltan
            
            row.append({'type': tile, 'rot': rot, 'cols': cols})
        seed_grid.append(row)
        
    # 2. Construir Grid Completo mediante Reflejos
    full_grid = [[None for _ in range(size)] for _ in range(size)]
    
    # Llenar cuadrantes
    for r in range(seed_size):
        for c in range(seed_size):
            # Original (Top-Left)
            cell = seed_grid[r][c]
            full_grid[r][c] = cell
            
            # --- REFLEJO HORIZONTAL (Top-Right) ---
            # Al reflejar horizontalmente, la forma geométrica cambia de orientación.
            # En matplotlib, podemos manejar esto, pero aquí ajustamos la lógica de 'rotación'
            # para formas simples.
            
            # Copia profunda de la celda
            tr_cell = cell.copy()
            # Lógica de espejo para rotación:
            # Si rot=0 (abajo-izq) -> espejo -> abajo-der (rot=1 para half_tri)
            # Esto es complejo de calcular para cada forma, así que usaremos
            # TRANSFORMACIÓN DE ESCALA (-1, 1) en el renderizado.
            # Solo guardamos que es un espejo.
            tr_cell['mirror_x'] = True
            full_grid[r][size - 1 - c] = tr_cell
            
            # --- REFLEJO VERTICAL (Bottom-Left) ---
            bl_cell = cell.copy()
            bl_cell['mirror_y'] = True
            full_grid[size - 1 - r][c] = bl_cell
            
            # --- REFLEJO DOBLE (Bottom-Right) ---
            br_cell = cell.copy()
            br_cell['mirror_x'] = True
            br_cell['mirror_y'] = True
            full_grid[size - 1 - r][size - 1 - c] = br_cell
            
    return full_grid

# --- RENDERIZADO ---

def render_kuki_pattern(grid, size):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Fondo global (opcional, por si quedan huecos)
    # ax.add_patch(patches.Rectangle((0,0), size, size, color='#ffffff'))

    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            # Coordenadas (Y invertida para dibujar de arriba a abajo)
            x_pos = c
            y_pos = size - 1 - r
            
            # Guardamos el estado actual de transformación
            
            # Aplicar espejos si es necesario mediante escala negativa
            # Esto requiere un truco: trasladar al origen, escalar, trasladar de vuelta.
            # Para simplificar con Matplotlib patches:
            
            # Calculamos la rotación base
            rot = cell['rot']
            
            # Ajuste de rotación manual para simular espejo si no usamos escala
            # Si es espejo X: 0->1, 1->0, 2->3, 3->2 (para triangulos básicos)
            # Vamos a dibujar normal y dejar que draw_tile maneje la rotación, 
            # pero necesitamos ajustar la rotación según el cuadrante para simular simetría caleidoscópica
            
            # TRUCO: Modificar la rotación efectiva según los flags de espejo
            # Esto funciona perfecto para formas simétricas o direccionales simples
            if cell.get('mirror_x'):
                if rot == 0: rot = 1
                elif rot == 1: rot = 0
                elif rot == 2: rot = 3
                elif rot == 3: rot = 2
            
            if cell.get('mirror_y'):
                # Invertir verticalmente
                if rot == 0: rot = 3
                elif rot == 1: rot = 2
                elif rot == 2: rot = 1
                elif rot == 3: rot = 0
                
            draw_tile(ax, x_pos, y_pos, cell['type'], rot, cell['cols'])

    # Marco exterior grueso (Estilo Kuki)
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#222', linewidth=4)
    
    # Líneas de cuadrícula sutiles
    for i in range(size + 1):
        ax.plot([0, size], [i, i], color='#000', linewidth=0.5, alpha=0.1)
        ax.plot([i, i], [0, size], color='#000', linewidth=0.5, alpha=0.1)
        
    return fig

# --- INTERFAZ LATERAL ---

st.sidebar.header("Configuración de Diseño")

paleta_nombre = st.sidebar.selectbox("Selecciona Paleta", list(PALETAS.keys()))
paleta_seleccionada = PALETAS[paleta_nombre]

n_colores = st.sidebar.slider("Cantidad de Colores", 2, 5, 4)
grid_size = st.sidebar.select_slider("Complejidad (Tamaño Grid)", options=[4, 6, 8, 12], value=6)

if 'seed' not in st.session_state:
    st.session_state.seed = 0

if st.sidebar.button("🎲 GENERAR NUEVO PATRÓN", type="primary"):
    st.session_state.seed += 1

# --- EJECUCIÓN ---

random.seed(st.session_state.seed)

# Generar y mostrar
grid_data = generate_mandala_grid(grid_size, n_colores, paleta_seleccionada)
fig = render_kuki_pattern(grid_data, grid_size)

st.pyplot(fig)

# Botón de descarga
from io import BytesIO
buf = BytesIO()
fig.savefig(buf, format="png", bbox_inches='tight', dpi=300)
st.download_button(
    label="⬇️ Descargar Imagen en Alta Calidad",
    data=buf.getvalue(),
    file_name="patron_kuki.png",
    mime="image/png"
)
