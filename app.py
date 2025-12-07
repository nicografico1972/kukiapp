import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="NICOART - MASTER", layout="centered")

# --- ESTILOS CSS (DISEÑO PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Space Grotesk', sans-serif; }
    h1 { font-weight: 700; letter-spacing: -2px; color: #000; text-align: center; text-transform: uppercase; font-size: 3rem; margin: 0; }
    .author { text-align: center; color: #999; font-size: 0.8em; letter-spacing: 2px; margin-bottom: 40px; text-transform: uppercase;}
    
    .streamlit-expanderHeader { background: #fff; border: 2px solid #000; color: #000; font-weight: 700; border-radius: 0px; }
    .streamlit-expanderContent { border: 2px solid #000; border-top: 0; background: #fff; padding: 20px; }
    
    div.stButton > button { 
        width: 100%; background: #000; color: #fff; border: none; border-radius: 0px; 
        font-weight: 700; font-size: 18px; padding: 20px; letter-spacing: 1px;
        transition: all 0.2s;
    }
    div.stButton > button:hover { background: #FFD700; color: #000; transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; max-width: 800px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>NICOART</h1>", unsafe_allow_html=True)
st.markdown("<p class='author'>Generador de Patrones Maestros</p>", unsafe_allow_html=True)

# --- PALETAS DE ALTO DISEÑO ---
PALETAS = {
    "🟡 HUEVO & NEGRO": ["#FFD700", "#000000"], 
    "🔴 BAUHAUS PRIMARIO": ["#F0F0F0", "#111111", "#D92B2B", "#1A4780", "#E6AF2E"],
    "🏺 ALHAMBRA TIERRA": ["#F2ECCE", "#8C2727", "#D9A404", "#2E5936", "#1A4780"],
    "⚫ ARQUITECTO": ["#FFFFFF", "#000000", "#333333", "#999999", "#E5E5E5"],
    "🌊 ATLÁNTICO": ["#F0F8FF", "#001219", "#005F73", "#0A9396", "#94D2BD"],
    "🍊 POP 70s": ["#FFF1E6", "#E85D04", "#F48C06", "#FAA307", "#370617"],
    "🌿 JARDÍN ZEN": ["#F7F7F7", "#2D3436", "#636E72", "#55EFC4", "#00B894"]
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
        # Ahora seleccionamos el ESTILO DEL MASTER PROMPT
        estilo = st.selectbox("ESTILO MAESTRO", ["Mix Inteligente", "Nudos & Lazos (Celtic)", "Estrellas & Quilts", "Bauhaus Modular", "Escher Geométrico"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        # Aumentamos el mínimo para que se aprecien los patrones grandes
        grid_size = st.select_slider("RESOLUCIÓN (Densidad)", options=[4, 8, 12, 16, 24], value=8)
    with c4:
        modo = st.selectbox("MODO CONSTRUCTIVO", ["Super-Módulos (Figuras 4x4)", "Tejido Infinito"])

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("GENERAR ARTE"): st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO AVANZADO ---

def draw_tile(ax, x, y, type, rot, c1, c2):
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def p(patch): 
        patch.set_antialiased(False)
        patch.set_linewidth(0)
        ax.add_patch(patch)

    # Fondo base
    p(patches.Rectangle((x, y), 1, 1, color=c2))

    if type == 'full': # Sólido
        p(patches.Rectangle((x, y), 1, 1, color=c1))
        
    elif type == 'circle': # Círculo
        p(patches.Circle((x+0.5, y+0.5), 0.4, color=c1))

    elif type == 'tri_half': # Triángulo mitad
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c1)
        poly.set_transform(tr); p(poly)
        
    elif type == 'arc_corner': # Cuarto de círculo
        w = patches.Wedge((x, y), 1, 0, 90, color=c1)
        w.set_transform(tr); p(w)
        
    elif type == 'knot_curve': # Curva de cinta (Para nudos)
        # Un arco grueso
        w1 = patches.Wedge((x, y), 0.8, 0, 90, color=c1)
        w2 = patches.Wedge((x, y), 0.4, 0, 90, color=c2) # Hueco
        w1.set_transform(tr); w2.set_transform(tr)
        p(w1); p(w2)

    elif type == 'knot_straight': # Recta de cinta (Para nudos)
        # Banda central
        r = patches.Rectangle((x, y+0.4), 1, 0.4, color=c1)
        r.set_transform(tr); p(r)
        
    elif type == 'star_point': # Punta de estrella (Cometa)
        # Un rombo deformado o cometa que apunta a la esquina
        poly = patches.Polygon([(x, y), (x+0.5, y+0.2), (x+1, y+1), (x+0.2, y+0.5)], color=c1)
        poly.set_transform(tr); p(poly)

    elif type == 'checker_4': 
        p(patches.Rectangle((x, y), 0.5, 0.5, color=c1))
        p(patches.Rectangle((x+0.5, y+0.5), 0.5, 0.5, color=c1))

# --- MOTOR DE SUPER-MÓDULOS 4x4 (MASTER PROMPT LOGIC) ---

def get_master_block(style, palette):
    """
    Genera un bloque maestro de 4x4 (16 celdas) que forma una figura completa.
    Esto es lo que permite crear esas figuras grandes y comprensibles.
    """
    rng = random.Random()
    
    # Matriz 4x4 vacía
    block = [[None for _ in range(4)] for _ in range(4)]
    
    c_bg = palette[0]
    c_fg = rng.choice(palette[1:]) if len(palette) > 1 else c_bg
    c_acc = rng.choice(palette[2:]) if len(palette) > 2 else c_fg
    
    # --- LÓGICA DE ESTILOS ---
    
    if style in ["Mix Inteligente", "Nudos & Lazos (Celtic)"]:
        # Patrón de Nudo Cerrado (Loop)
        # Esquinas curvas, lados rectos
        # C1 C2
        # C4 C3
        # Simplificado a un anillo grande 4x4
        
        # Esquinas Exteriores (Curvas)
        block[0][0] = ('knot_curve', 0, c_fg, c_bg)
        block[0][3] = ('knot_curve', 3, c_fg, c_bg)
        block[3][0] = ('knot_curve', 1, c_fg, c_bg)
        block[3][3] = ('knot_curve', 2, c_fg, c_bg)
        
        # Lados (Rectos)
        block[0][1] = ('knot_straight', 0, c_fg, c_bg); block[0][2] = ('knot_straight', 0, c_fg, c_bg)
        block[3][1] = ('knot_straight', 0, c_fg, c_bg); block[3][2] = ('knot_straight', 0, c_fg, c_bg)
        block[1][0] = ('knot_straight', 1, c_fg, c_bg); block[2][0] = ('knot_straight', 1, c_fg, c_bg)
        block[1][3] = ('knot_straight', 1, c_fg, c_bg); block[2][3] = ('knot_straight', 1, c_fg, c_bg)
        
        # Centro (Cruce o Vacío) - Hacemos un nudo central
        # Opcional: Un diamante central
        block[1][1] = ('tri_half', 0, c_acc, c_bg); block[1][2] = ('tri_half', 3, c_acc, c_bg)
        block[2][1] = ('tri_half', 1, c_acc, c_bg); block[2][2] = ('tri_half', 2, c_acc, c_bg)

    if style in ["Mix Inteligente", "Estrellas & Quilts"]:
        # Estrella Radiante 4x4
        # Centro: 4 triángulos formando cuadrado o estrella
        block[1][1] = ('tri_half', 0, c_fg, c_bg); block[1][2] = ('tri_half', 3, c_fg, c_bg)
        block[2][1] = ('tri_half', 1, c_fg, c_bg); block[2][2] = ('tri_half', 2, c_fg, c_bg)
        
        # Puntas exteriores
        block[0][1] = ('tri_half', 1, c_acc, c_bg); block[0][2] = ('tri_half', 2, c_acc, c_bg)
        block[3][1] = ('tri_half', 0, c_acc, c_bg); block[3][2] = ('tri_half', 3, c_acc, c_bg)
        block[1][0] = ('tri_half', 0, c_acc, c_bg); block[2][0] = ('tri_half', 3, c_acc, c_bg)
        block[1][3] = ('tri_half', 1, c_acc, c_bg); block[2][3] = ('tri_half', 2, c_acc, c_bg)
        
        # Esquinas (Sólidas o Triangulos)
        corn_type = 'full'
        block[0][0] = (corn_type, 0, c_bg, c_bg)
        block[0][3] = (corn_type, 0, c_bg, c_bg)
        block[3][0] = (corn_type, 0, c_bg, c_bg)
        block[3][3] = (corn_type, 0, c_bg, c_bg)

    if style in ["Mix Inteligente", "Bauhaus Modular"]:
        # Composición Asimétrica Grande pero equilibrada
        # Un gran círculo en una esquina
        block[0][0] = ('arc_corner', 0, c_fg, c_bg); block[0][1] = ('arc_corner', 3, c_fg, c_bg)
        block[1][0] = ('arc_corner', 1, c_fg, c_bg); block[1][1] = ('arc_corner', 2, c_fg, c_bg)
        
        # Bandas en el resto
        for i in range(2, 4):
            for j in range(4):
                block[i][j] = ('knot_straight', 0, c_acc, c_bg)
        for i in range(0, 2):
            for j in range(2, 4):
                block[i][j] = ('circle', 0, c_acc, c_bg)

    if style in ["Mix Inteligente", "Escher Geométrico"]:
        # Patrón de "Molino" que tessela
        # 4 piezas rotando
        base = ('star_point', 0, c_fg, c_bg)
        # Top Left Block 2x2
        block[0][0] = ('star_point', 0, c_fg, c_bg); block[0][1] = ('star_point', 1, c_acc, c_bg)
        block[1][0] = ('star_point', 3, c_acc, c_bg); block[1][1] = ('star_point', 2, c_fg, c_bg)
        
        # Repetir este patrón 2x2 en todo el 4x4 pero rotando
        # Esto simula la complejidad de Escher
        for r in range(0,4,2):
            for c in range(0,4,2):
                # Copiar el bloque base
                block[r][c] = ('star_point', 0, c_fg, c_bg)
                block[r][c+1] = ('star_point', 1, c_acc, c_bg)
                block[r+1][c] = ('star_point', 3, c_acc, c_bg)
                block[r+1][c+1] = ('star_point', 2, c_fg, c_bg)

    # Rellenar cualquier hueco con sólido por seguridad
    for r in range(4):
        for c in range(4):
            if block[r][c] is None:
                block[r][c] = ('full', 0, c_bg, c_bg)
                
    return block

# --- GENERADOR PRINCIPAL ---

def generate_grid(size, palette, style, mode):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    # Generamos un Master Block de 4x4
    master_block = get_master_block(style, palette)
    
    if mode == "Super-Módulos (Figuras 4x4)":
        # Repetir el bloque 4x4 exactamente
        for r in range(size):
            for c in range(size):
                source = master_block[r % 4][c % 4]
                grid[r][c] = source

    elif mode == "Tejido Infinito":
        # Alternar el bloque con su versión invertida o rotada
        for r_blk in range(0, size, 4):
            for c_blk in range(0, size, 4):
                # Decidir si rotamos este bloque grande
                do_rot = ((r_blk//4) + (c_blk//4)) % 2 == 1
                
                for i in range(4):
                    for j in range(4):
                        if r_blk+i < size and c_blk+j < size:
                            src = master_block[i][j]
                            if do_rot:
                                # Intercambiar colores para efecto tablero
                                grid[r_blk+i][c_blk+j] = (src[0], src[1], src[3], src[2])
                            else:
                                grid[r_blk+i][c_blk+j] = src

    return grid

def render_art(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell:
                draw_tile(ax, c, size-1-r, cell[0], cell[1], cell[2], cell[3])

    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=8)
    
    # Retícula visible
    for i in range(size+1):
        ax.plot([0, size], [i, i], color='black', linewidth=0.5, alpha=0.3)
        ax.plot([i, i], [0, size], color='black', linewidth=0.5, alpha=0.3)

    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)

# Si el usuario elige "Mix", elegimos uno al azar para este render
estilo_efectivo = estilo if estilo != "Mix Inteligente" else random.choice(["Nudos & Lazos (Celtic)", "Estrellas & Quilts", "Bauhaus Modular"])

grid_data = generate_grid(grid_size, paleta, estilo_efectivo, modo)
figura = render_art(grid_data, grid_size)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR IMAGEN NICOART", data=buf.getvalue(), file_name="nicoart_master.png", mime="image/png")
