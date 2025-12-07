import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="NICOART GENERATOR", layout="centered")

# --- ESTILOS CSS (DISEÑO PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Space Grotesk', sans-serif; }
    h1 { font-weight: 700; letter-spacing: -2px; color: #000; text-align: center; text-transform: uppercase; font-size: 3rem; margin: 0; }
    .author { text-align: center; color: #999; font-size: 0.8em; letter-spacing: 2px; margin-bottom: 40px; text-transform: uppercase;}
    
    /* Panel de Control */
    .streamlit-expanderHeader { background: #fff; border: 2px solid #000; color: #000; font-weight: 700; border-radius: 0px; }
    .streamlit-expanderContent { border: 2px solid #000; border-top: 0; background: #fff; padding: 20px; }
    
    /* Botón */
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
st.markdown("<p class='author'>Algoritmo de Geometría Emergente</p>", unsafe_allow_html=True)

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
        # Preview
        cols = st.columns(len(paleta))
        for i, c in enumerate(cols):
            c.markdown(f"<div style='background:{paleta[i]};height:15px;width:100%'></div>", unsafe_allow_html=True)
    with c2:
        # Aquí está la clave: FAMILIAS DE FORMAS
        familia = st.selectbox("FAMILIA GEOMÉTRICA", ["Mezcla Inteligente", "Solo Diagonales (Estrellas)", "Solo Curvas (Retro)", "Ortogonal (Laberinto)"])

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        grid_size = st.select_slider("RESOLUCIÓN (Densidad)", options=[4, 8, 12, 16, 20], value=8)
    with c4:
        # El modo Super-Módulo es el que crea las figuras grandes
        modo = st.selectbox("MODO CONSTRUCTIVO", ["Super-Módulos (Figuras Grandes)", "Tejido Infinito (Interlaced)"])

    st.write("")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("GENERAR ARTE"): st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO PURO (SIN LAZOS NI EMOJIS) ---
# Definimos vectores exactos para que encajen matemáticamente

def draw_tile(ax, x, y, type, rot, c1, c2):
    # Transformación base (rotación alrededor del centro)
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData
    
    def p(patch): 
        patch.set_antialiased(False)
        patch.set_linewidth(0)
        ax.add_patch(patch)

    # Fondo base (siempre c2 para contraste, o blanco si se prefiere aire)
    # Usaremos c2 como base y c1 como figura
    p(patches.Rectangle((x, y), 1, 1, color=c2))

    if type == 'full': # Bloque sólido
        p(patches.Rectangle((x, y), 1, 1, color=c1))
        
    elif type == 'tri_half': # Triángulo mitad perfecta (Diagonal)
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c1)
        poly.set_transform(tr); p(poly)
        
    elif type == 'tri_corner': # Triángulo pequeño en esquina (1/4)
        poly = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=c1)
        # Ajuste para que sea esquina real:
        poly = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c1) # Esto es half
        # Corner real:
        poly = patches.Polygon([(x, y), (x+0.5, y), (x, y+0.5)], color=c1)
        poly.set_transform(tr); p(poly)

    elif type == 'arc_corner': # Cuarto de círculo (Retro)
        w = patches.Wedge((x, y), 1, 0, 90, color=c1)
        w.set_transform(tr); p(w)
        
    elif type == 'arc_ring': # Anillo curvo
        w1 = patches.Wedge((x, y), 1, 0, 90, color=c1)
        w2 = patches.Wedge((x, y), 0.5, 0, 90, color=c2) # Hueco
        w1.set_transform(tr); w2.set_transform(tr)
        p(w1); p(w2)

    elif type == 'strip_diag': # Banda diagonal (Cruce)
        # Creamos un polígono que va de esq a esq con grosor
        pts = [(x, y), (x+0.3, y), (x+1, y+0.7), (x+1, y+1), (x+0.7, y+1), (x, y+0.3)]
        # Simplificado para geometría perfecta de quilt:
        # Triangulo grande menos triangulo pequeño
        p1 = patches.Polygon([(x, y), (x+1, y), (x+1, y+1), (x, y+1)], color=c2) # Fondo
        p2 = patches.Polygon([(x, y), (x+1, y+1), (x+0.3, y+1), (x, y+0.3)], color=c1) # Banda no, mejor simple
        # Triangulo mitad color 1
        t1 = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=c1)
        t1.set_transform(tr); p(t1)
        
    elif type == 'stripe_center': # Banda recta
        r = patches.Rectangle((x+0.33, y), 0.33, 1, color=c1)
        r.set_transform(tr); p(r)
        
    elif type == 'checker_4': # 4 cuadraditos
        p(patches.Rectangle((x, y), 0.5, 0.5, color=c1))
        p(patches.Rectangle((x+0.5, y+0.5), 0.5, 0.5, color=c1))

# --- MOTOR LÓGICO DE SUPER-MÓDULOS ---
# Aquí está la inteligencia. Define cómo se agrupan las celdas para formar figuras.

def get_super_module(family, palette):
    """Devuelve un bloque de 2x2 celdas que forman una figura coherente."""
    # Estructura del super módulo: 2 filas, 2 columnas. 
    # Cada celda: (tipo, rotación, color_figura, color_fondo)
    
    rng = random.Random() # Usaremos el global seed después
    
    c_bg = palette[0] # Fondo dominante
    # Elegir color figura contrastante
    c_fg = rng.choice(palette[1:]) if len(palette) > 1 else c_bg
    
    # Definir patrones lógicos (La "Receta")
    patterns = []
    
    # 1. DIAMANTE / ESTRELLA (Requiere familia Diagonal o Mezcla)
    if family in ["Mezcla Inteligente", "Solo Diagonales (Estrellas)"]:
        # Diamante Central (4 triángulos mirando al centro)
        patterns.append([
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)], # Fila 1
            [('tri_half', 1, c_fg, c_bg), ('tri_half', 2, c_fg, c_bg)]  # Fila 2
        ])
        # Reloj de Arena (X)
        patterns.append([
            [('tri_half', 1, c_fg, c_bg), ('tri_half', 2, c_fg, c_bg)],
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)]
        ])
        # Chevron (Flechas)
        patterns.append([
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)],
            [('tri_half', 0, c_fg, c_bg), ('tri_half', 3, c_fg, c_bg)]
        ])

    # 2. CURVAS / RETRO (Requiere familia Curva o Mezcla)
    if family in ["Mezcla Inteligente", "Solo Curvas (Retro)"]:
        # Círculo completo (4 cuartos mirando al centro)
        patterns.append([
            [('arc_corner', 0, c_fg, c_bg), ('arc_corner', 3, c_fg, c_bg)],
            [('arc_corner', 1, c_fg, c_bg), ('arc_corner', 2, c_fg, c_bg)]
        ])
        # Pétalos opuestos
        patterns.append([
            [('arc_corner', 0, c_fg, c_bg), ('arc_corner', 2, c_fg, c_bg)],
            [('arc_corner', 2, c_fg, c_bg), ('arc_corner', 0, c_fg, c_bg)]
        ])
        # Olas (S)
        patterns.append([
            [('arc_corner', 0, c_fg, c_bg), ('arc_corner', 1, c_bg, c_fg)], # Invertido
            [('arc_corner', 3, c_bg, c_fg), ('arc_corner', 2, c_fg, c_bg)]
        ])

    # 3. ORTOGONAL (Laberinto)
    if family in ["Mezcla Inteligente", "Ortogonal (Laberinto)"]:
        # Cruz
        patterns.append([
            [('stripe_center', 0, c_fg, c_bg), ('stripe_center', 0, c_fg, c_bg)],
            [('stripe_center', 1, c_fg, c_bg), ('stripe_center', 1, c_fg, c_bg)] # Rotado mal para cruz, corregir
        ])
        # Ajuste manual cruz:
        patterns.append([
            [('stripe_center', 90, c_fg, c_bg), ('stripe_center', 0, c_fg, c_bg)], # Truco: rotacion no va por grados aqui, va por indice 0..3
            # stripe_center rot 0 es vertical? rot 1 es horizontal.
            # Vamos a asumir stripe_center: 0=vert, 1=horiz
            [('stripe_center', 1, c_fg, c_bg), ('stripe_center', 0, c_fg, c_bg)] # T shape
        ])
        patterns.append([
            [('checker_4', 0, c_fg, c_bg), ('full', 0, c_bg, c_fg)],
            [('full', 0, c_bg, c_fg), ('checker_4', 0, c_fg, c_bg)]
        ])

    # Si no hay patrones (seguridad), devolver sólido
    if not patterns: return [[('full', 0, c_fg, c_bg)]*2]*2
    
    return random.choice(patterns)

# --- GENERADOR PRINCIPAL ---

def generate_grid(size, palette, family, mode):
    rng = random.Random(st.session_state.seed)
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    # Tamaño del super módulo (2x2 celdas)
    mod_w, mod_h = 2, 2
    
    if mode == "Super-Módulos (Figuras Grandes)":
        # Generamos una retícula de super-módulos
        # Si la resolución es 16, tenemos 8x8 super módulos.
        # Para que sea "bonito", no ponemos uno al azar en cada sitio.
        # Creamos un ritmo: A B A B
        
        # 1. Elegir 2 Módulos "Tema" para este diseño
        module_A = get_super_module(family, palette)
        module_B = get_super_module(family, palette)
        
        # A veces module_B es simplemente el A con colores invertidos
        if rng.random() > 0.5:
            # Invertir colores de A para crear B
            module_B = []
            for row in module_A:
                new_row = []
                for cell in row:
                    new_row.append((cell[0], cell[1], cell[3], cell[2])) # Swap colors
                module_B.append(new_row)

        for r in range(0, size, 2):
            for c in range(0, size, 2):
                # Damero de módulos
                is_A = ((r//2) + (c//2)) % 2 == 0
                current_mod = module_A if is_A else module_B
                
                # Copiar el módulo 2x2 al grid
                for i in range(2):
                    for j in range(2):
                        if r+i < size and c+j < size:
                            grid[r+i][c+j] = current_mod[i][j]

    elif mode == "Tejido Infinito (Interlaced)":
        # Aquí usamos un solo módulo complejo y lo repetimos con rotaciones
        # para simular un tejido continuo
        base_mod = get_super_module(family, palette)
        
        for r in range(0, size, 2):
            for c in range(0, size, 2):
                # Rotar el módulo según posición para que "fluyan" las líneas
                rotation_offset = ((r//2) + (c//2)) % 4
                
                # Aplicar módulo rotado
                for i in range(2):
                    for j in range(2):
                        if r+i < size and c+j < size:
                            cell = base_mod[i][j]
                            # Sumar rotación
                            new_rot = (cell[1] + rotation_offset) % 4
                            grid[r+i][c+j] = (cell[0], new_rot, cell[2], cell[3])

    return grid

def render_art(grid, size):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal'); ax.axis('off')
    
    # Dibujar
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell:
                # cell = (tipo, rot, color1, color2)
                # Invertimos Y para dibujar de arriba a abajo visualmente
                draw_tile(ax, c, size-1-r, cell[0], cell[1], cell[2], cell[3])

    # Marco Exterior Fuerte
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#000', linewidth=12)
    
    # Retícula sutil (Opcional, la pediste muy fina)
    for i in range(size+1):
        ax.plot([0, size], [i, i], color='black', linewidth=0.1, alpha=0.2)
        ax.plot([i, i], [0, size], color='black', linewidth=0.1, alpha=0.2)

    return fig

# --- EJECUCIÓN ---
random.seed(st.session_state.seed)

grid_data = generate_grid(grid_size, paleta, familia, modo)
figura = render_art(grid_data, grid_size)

st.pyplot(figura)

buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(label="DESCARGAR OBRA NICOART", data=buf.getvalue(), file_name="nicoart.png", mime="image/png")
