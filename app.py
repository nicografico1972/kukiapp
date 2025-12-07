import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="NICOART - MASTER", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Space Grotesk', sans-serif; }
    h1 { font-weight: 700; letter-spacing: -2px; color: #000; text-align: center; text-transform: uppercase; font-size: 3rem; margin: 0; }
    .author { text-align: center; color: #999; font-size: 0.8em; letter-spacing: 2px; margin-bottom: 40px; text-transform: uppercase;}
    .streamlit-expanderHeader { background: #fff; border: 2px solid #000; color: #000; font-weight: 700; border-radius: 0px; }
    .streamlit-expanderContent { border: 2px solid #000; border-top: 0; background: #fff; padding: 20px; }
    div.stButton > button { width: 100%; background: #000; color: #fff; border: none; border-radius: 0px; font-weight: 700; font-size: 18px; padding: 20px; letter-spacing: 1px; transition: all 0.2s; }
    div.stButton > button:hover { background: #FFD700; color: #000; transform: translateY(-4px); }
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; max-width: 800px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>NICOART</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>Generador de Nudos & Geometría</p>", unsafe_allow_html=True)

# --- PALETAS ---
PALETAS = {
    "🟡 HUEVO & NEGRO": ["#FFD700", "#000000"], 
    "🔴 CINTA ROJA (CELTIC)": ["#F2ECCE", "#D92B2B", "#111111", "#E6AF2E"], # Inspirada en tu imagen
    "🏺 ALHAMBRA": ["#F2ECCE", "#1A4780", "#8C2727", "#D9A404"],
    "⚫ ARQUITECTO": ["#FFFFFF", "#000000", "#555555", "#AAAAAA"],
    "🌊 ATLÁNTICO": ["#F0F8FF", "#001219", "#005F73", "#94D2BD"],
    "🍊 POP 70s": ["#FFF1E6", "#E85D04", "#FAA307", "#370617"],
}

# --- CONTROLES ---
with st.expander("🎛️ LABORATORIO DE DISEÑO", expanded=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        p_name = st.selectbox("PALETA", list(PALETAS.keys()), label_visibility="collapsed")
        paleta = PALETAS[p_name]
        cols = st.columns(len(paleta))
        for i, c in enumerate(cols):
            c.markdown(f"<div style='background:{paleta[i]};height:15px;width:100%'></div>", unsafe_allow_html=True)
    with c2:
        # Simplificado para asegurar calidad
        estilo = st.selectbox("ESTILO MAESTRO", ["Nudos & Lazos (Celtic)", "Estrellas Geométricas", "Bauhaus Modular"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        grid_size = st.select_slider("RESOLUCIÓN", options=[4, 8, 12, 16], value=8)
    with c4:
        modo = st.selectbox("MODO", ["Super-Módulos (Figuras)", "Tejido Infinito"])

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("GENERAR NUEVO ARTE"): st.session_state.seed += 1

# --- ALFABETO DE PIEZAS TRUCHET (SISTEMA DE CONEXIONES) ---

def draw_truchet_tile(ax, x, y, type, rot, c_bg, c_tape, c_outline):
    """
    Dibuja una loseta tipo Truchet que conecta líneas.
    type: 'arc' (curva) o 'line' (recta) o 'cross' (cruce)
    """
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    # Grosor de la cinta
    w = 0.3 # Ancho de la cinta
    
    def p(patch): 
        patch.set_antialiased(False); patch.set_linewidth(0); ax.add_patch(patch)

    # Fondo
    p(patches.Rectangle((x, y), 1, 1, color=c_bg))

    # --- DIBUJO DE CINTAS ---
    # Dibujamos primero el contorno (más grueso) y luego el relleno (más fino) para simular borde
    
    if type == 'arc_dual':
        # Dos arcos opuestos (esquinas)
        # Arco 1 (Abajo Izq)
        for color, width in [(c_outline, w+0.1), (c_tape, w)]:
            w1 = patches.Wedge((x, y), 0.5 + width/2, 0, 90, width=width, color=color)
            w1.set_transform(tr); p(w1)
        # Arco 2 (Arriba Der)
        for color, width in [(c_outline, w+0.1), (c_tape, w)]:
            w2 = patches.Wedge((x+1, y+1), 0.5 + width/2, 180, 270, width=width, color=color)
            w2.set_transform(tr); p(w2)

    elif type == 'lines_dual':
        # Dos líneas rectas paralelas
        # Línea 1 (Vertical centrada) - No, Truchet standard conecta centros de lados
        # Conectamos (0.5, 0) con (0.5, 1) ? No, en Truchet diagonal tiles son arcos.
        # En este sistema "Smith":
        # Lines conecta (0.5, 0) con (0.5, 1) y (0, 0.5) con (1, 0.5) es cruz.
        # Rectas paralelas:
        for color, width in [(c_outline, w+0.1), (c_tape, w)]:
            r1 = patches.Rectangle((x + 0.5 - width/2, y), width, 1, color=color)
            r1.set_transform(tr); p(r1)
            
    elif type == 'cross':
        # Cruce (Una pasa por encima de otra)
        # Barra Vertical (Abajo)
        for color, width in [(c_outline, w+0.1), (c_tape, w)]:
            r1 = patches.Rectangle((x + 0.5 - width/2, y), width, 1, color=color)
            r1.set_transform(tr); p(r1)
        # Barra Horizontal (Arriba) - Con hueco pequeño para efecto 3D si se quiere
        # Para estilo plano tipo quilt:
        for color, width in [(c_outline, w+0.1), (c_tape, w)]:
            r2 = patches.Rectangle((x, y + 0.5 - width/2), 1, width, color=color)
            r2.set_transform(tr); p(r2)
            
    elif type == 't_junction':
        # Una T. Recta y una que sale.
        pass # Simplificado para evitar complejidad ahora

    # Otros tipos geométricos para los otros modos
    elif type == 'triangle_full':
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_tape)
        poly.set_transform(tr); p(poly)
    elif type == 'quarter_solid':
        wd = patches.Wedge((x, y), 1, 0, 90, color=c_tape)
        wd.set_transform(tr); p(wd)

# --- GENERADOR DE SUPER-MÓDULOS DE NUDOS ---

def get_knot_module(palette):
    """
    Genera un bloque 4x4 que garantiza un nudo cerrado o entrelazado coherente.
    Usa el sistema de Wang Tiles o Truchet Tiles para consistencia.
    """
    rng = random.Random()
    
    # Colores
    c_bg = palette[0]
    c_tape = palette[1] if len(palette) > 1 else "#000"
    c_out = palette[2] if len(palette) > 2 else c_bg # Color de borde o contraste
    
    # Definimos patrones pre-diseñados que SABEMOS que funcionan (como las imagenes)
    # 0: arc_dual, 1: lines, 2: cross
    
    patterns = []
    
    # Patrón 1: El "Nudo Infinito" clásico (Círculos entrelazados)
    # Requiere alternancia de arcos
    p1 = [
        [('arc_dual', 0), ('arc_dual', 3), ('arc_dual', 0), ('arc_dual', 3)],
        [('arc_dual', 1), ('cross', 0), ('cross', 0), ('arc_dual', 2)],
        [('arc_dual', 0), ('cross', 0), ('cross', 0), ('arc_dual', 3)],
        [('arc_dual', 1), ('arc_dual', 2), ('arc_dual', 1), ('arc_dual', 2)]
    ]
    # Inyectamos colores
    patterns.append([[(t[0], t[1], c_bg, c_tape, c_out) for t in row] for row in p1])

    # Patrón 2: La "X" Gigante (Diagonal Bands)
    p2 = [
        [('arc_dual', 1), ('lines_dual', 1), ('lines_dual', 1), ('arc_dual', 2)],
        [('lines_dual', 0), ('arc_dual', 1), ('arc_dual', 2), ('lines_dual', 0)],
        [('lines_dual', 0), ('arc_dual', 0), ('arc_dual', 3), ('lines_dual', 0)],
        [('arc_dual', 0), ('lines_dual', 1), ('lines_dual', 1), ('arc_dual', 3)]
    ]
    patterns.append([[(t[0], t[1], c_bg, c_tape, c_out) for t in row] for row in p2])
    
    # Patrón 3: Cajas Concéntricas (Knot Square)
    p3 = [
        [('arc_dual', 0), ('lines_dual', 1), ('lines_dual', 1), ('arc_dual', 3)],
        [('lines_dual', 0), ('arc_dual', 0), ('arc_dual', 3), ('lines_dual', 0)],
        [('lines_dual', 0), ('arc_dual', 1), ('arc_dual', 2), ('lines_dual', 0)],
        [('arc_dual', 1), ('lines_dual', 1), ('lines_dual', 1), ('arc_dual', 2)]
    ]
    patterns.append([[(t[0], t[1], c_bg, c_tape, c_out) for t in row] for row in p3])

    # Seleccionar uno y aplicar rotación aleatoria global al bloque
    selected = rng.choice(patterns)
    
    # Rotación del bloque completo (opcional, para variar)
    # Aquí simplificamos devolviendo el bloque tal cual para asegurar conexiones
    return selected

def get_geometric_module(palette):
    """Genera patrones de estrellas/triángulos (Quilt Style)"""
    rng = random.Random()
    c_bg = palette[0]
    c_main = palette[1] if len(palette)>1 else "#000"
    c_acc = palette[2] if len(palette)>2 else c_main
    
    # Patrón Estrella 4x4
    block = [[None]*4 for _ in range(4)]
    
    # Centro
    block[1][1] = ('triangle_full', 0, c_bg, c_main, None)
    block[1][2] = ('triangle_full', 3, c_bg, c_main, None)
    block[2][1] = ('triangle_full', 1, c_bg, c_main, None)
    block[2][2] = ('triangle_full', 2, c_bg, c_main, None)
    
    # Puntas
    block[0][1] = ('triangle_full', 1, c_bg, c_acc, None)
    block[0][2] = ('triangle_full', 2, c_bg, c_acc, None)
    block[3][1] = ('triangle_full', 0, c_bg, c_acc, None)
    block[3][2] = ('triangle_full', 3, c_bg, c_acc, None)
    
    block[1][0] = ('triangle_full', 0, c_bg, c_acc, None)
    block[2][0] = ('triangle_full', 1, c_bg, c_acc, None)
    block[1][3] = ('triangle_full', 3, c_bg, c_acc, None)
    block[2][3] = ('triangle_full', 2, c_bg, c_acc, None)
    
    # Esquinas (Llenar con fondo o detalle)
    for r in [0,3]:
        for c in [0,3]:
            block[r][c] = ('quarter_solid', (r+c)%4, c_bg, c_main, None) # Decoración esquina
            
    return block

# --- GENERADOR GRID ---

def generate_grid(size, palette, style, mode):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    # 1. GENERAR EL SUPER-BLOQUE BASE (4x4)
    if style == "Nudos & Lazos (Celtic)":
        master_block = get_knot_module(palette)
    else:
        master_block = get_geometric_module(palette)
        
    # 2. REPETIR SEGÚN MODO
    if mode == "Super-Módulos (Figuras)":
        # Repetición exacta del bloque 4x4
        for r in range(size):
            for c in range(size):
                source = master_block[r % 4][c % 4]
                grid[r][c] = source
                
    elif mode == "Tejido Infinito":
        # Alternar bloque normal e invertido/rotado para continuidad
        for r_blk in range(0, size, 4):
            for c_blk in range(0, size, 4):
                # Tablero de ajedrez de bloques
                flip = ((r_blk//4) + (c_blk//4)) % 2 == 1
                
                for i in range(4):
                    for j in range(4):
                        if r_blk+i < size and c_blk+j < size:
                            if flip:
                                # Truco visual: Invertir colores para variedad
                                src = master_block[i][j]
                                # (tipo, rot, c_bg, c_tape, c_out)
                                # Intercambiamos c_bg y c_tape si no es cross
                                # grid[r_blk+i][c_blk+j] = (src[0], src[1], src[3], src[2], src[4])
                                grid[r_blk+i][c_blk+j] = src # Dejamos igual por seguridad de conexión
                            else:
                                grid[r_blk+i][c_blk+j] = master_block[i][j]

    return grid

def render_art(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell:
                # Invertir Y
                draw_truchet_tile(ax, c, size-1-r, cell[0], cell[1], cell[2], cell[3], cell[4])

    # Marco
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=8)
    
    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)

grid_data = generate_grid(grid_size, paleta, estilo, modo)
figura = render_art(grid_data, grid_size)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR IMAGEN", data=buf.getvalue(), file_name="nicoart.png", mime="image/png")
