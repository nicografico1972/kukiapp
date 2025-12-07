import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np
import random
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="KUKIAPP - Alhambra", layout="centered")

# --- ESTILOS CSS (UI MÓVIL OPTIMIZADA) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1 { 
        font-family: 'Georgia', serif; 
        font-weight: 800; color: #111; text-align: center; margin-bottom: 0px;
    }
    .subtitle {
        text-align: center; color: #666; font-style: italic; margin-bottom: 20px; font-family: sans-serif;
    }
    .streamlit-expanderHeader {
        background-color: #f4f4f4; border: 2px solid #333; border-radius: 8px; font-weight: bold; color: #333;
    }
    .streamlit-expanderContent {
        border: 2px solid #333; border-top: none; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; background-color: #fff; padding: 20px;
    }
    div.stButton > button { 
        width: 100%; border: 3px solid #333; border-radius: 8px; font-weight: 800; font-size: 16px;
        background-color: #fff; color: #333; padding: 15px 0px; transition: all 0.2s; box-shadow: 4px 4px 0px #333;
    }
    div.stButton > button:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0px #333; }
    div.stButton > button:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0px #333; background-color: #eee; }
    [data-testid="column"] { min-width: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1>KUKIAPP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Edición Alhambra & Simetría Total</p>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.expander("🎛️ CONTROLES DE DISEÑO (TÓCAME)", expanded=True):
    
    st.write("### 1. Simetría y Estructura")
    # NUEVO: Control de Simetría
    simetria = st.selectbox("Tipo de Simetría", ["Caleidoscopio (Espejo Central)", "Repetición (Papel Pintado)", "Ajedrez (Rotación Alterna)"])
    
    c_geo1, c_geo2 = st.columns(2)
    with c_geo1:
        complejidad = st.select_slider("Tamaño Grid", options=[2, 4, 6, 8, 12, 16], value=4)
    with c_geo2:
        densidad = st.slider("Riqueza visual", 0.1, 1.0, 1.0)

    st.markdown("---")
    st.write("### 2. Paleta Nazarí")
    n_colores = st.slider("Nº Tintas", 1, 5, 4)
    cols = st.columns(n_colores)
    colores_usuario = []
    # Colores por defecto estilo Alhambra (Azul cobalto, Ocre, Rojo arcilla, Verde)
    defaults = ["#1A4780", "#D9A404", "#8C2727", "#2E5936", "#F2ECCE"]
    
    for i, col in enumerate(cols):
        with col:
            c = st.color_picker(f"C{i+1}", defaults[i])
            colores_usuario.append(c)

    st.markdown("---")
    if 'seed' not in st.session_state: st.session_state.seed = 0
    if st.button("🎲 GENERAR MOSAICO"): st.session_state.seed += 1

# --- ALFABETO GEOMÉTRICO EXTENDIDO (ALHAMBRA) ---

def add_patch_hd(ax, patch):
    """Renderizado HD sin bordes borrosos"""
    patch.set_antialiased(False)
    patch.set_linewidth(0)
    ax.add_patch(patch)

def draw_alhambra_tile(ax, x, y, tipo, rot, c_main, c_acc):
    # Transformación de rotación
    tr = transforms.Affine2D().rotate_deg_around(x + 0.5, y + 0.5, rot * 90) + ax.transData

    # 1. FONDO BLANCO BASE
    bg = patches.Rectangle((x, y), 1, 1, color='#FFFFFF', zorder=0)
    add_patch_hd(ax, bg)
    
    # 2. MARCO FINO (Opcional, estilo azulejo)
    ax.add_patch(patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='#222', linewidth=0.5, zorder=10, antialiased=True))

    # --- CATÁLOGO DE FORMAS ---
    
    if tipo == 'star_8': # Estrella de 8 puntas (Khatam)
        # Cuadrado 1
        r1 = patches.Rectangle((x+0.2, y+0.2), 0.6, 0.6, color=c_main)
        # Cuadrado 2 rotado 45 grados manualmente con transformacion
        r2 = patches.Rectangle((x+0.2, y+0.2), 0.6, 0.6, color=c_main)
        t_rot45 = transforms.Affine2D().rotate_deg_around(x+0.5, y+0.5, 45) + tr
        r2.set_transform(t_rot45)
        
        r1.set_transform(tr)
        add_patch_hd(ax, r1)
        add_patch_hd(ax, r2)
        # Centro
        c = patches.Circle((x+0.5, y+0.5), 0.15, color=c_acc)
        add_patch_hd(ax, c)

    elif tipo == 'lantern': # Forma de linterna/escudo
        # Un círculo arriba y un cuadrado abajo fusionados
        # Triangulo base
        p = patches.Polygon([(x+0.2, y+0.2), (x+0.8, y+0.2), (x+0.5, y+0.5)], color=c_main)
        p.set_transform(tr)
        add_patch_hd(ax, p)
        # Semicírculo arriba
        w = patches.Wedge((x+0.5, y+0.5), 0.35, 0, 180, color=c_acc)
        w.set_transform(tr)
        add_patch_hd(ax, w)

    elif tipo == 'petal': # Pétalo de flor
        # Dos arcos que se cruzan
        # Simplificado: Un rombo curvado
        # Usaremos dos wedges opuestos superpuestos
        w1 = patches.Wedge((x, y+0.5), 0.8, -30, 30, color=c_main)
        w1.set_transform(tr)
        add_patch_hd(ax, w1)
        
    elif tipo == 'propeller': # Hélice Zellige
        # Cuatro triángulos finos girando
        p = patches.Polygon([(x+0.5, y+0.5), (x+1, y+0.8), (x+1, y+0.2)], color=c_main)
        p.set_transform(tr)
        add_patch_hd(ax, p)
        # Acento central
        c = patches.Circle((x+0.5, y+0.5), 0.1, color=c_acc)
        add_patch_hd(ax, c)

    elif tipo == 'weave': # Entrelazado
        # Banda cruzada
        r1 = patches.Rectangle((x+0.4, y), 0.2, 1, color=c_main)
        r2 = patches.Rectangle((x, y+0.4), 1, 0.2, color=c_acc)
        r1.set_transform(tr)
        r2.set_transform(tr)
        add_patch_hd(ax, r1)
        add_patch_hd(ax, r2)

    elif tipo == 'bowtie': # Lazo / Nudo
        p = patches.Polygon([(x, y), (x+1, y+1), (x+1, y), (x, y+1)], color=c_main)
        p.set_transform(tr)
        add_patch_hd(ax, p)

    elif tipo == 'quarter_sun': # Cuarto de sol radiante
        w1 = patches.Wedge((x, y), 1, 0, 90, color=c_main)
        w2 = patches.Wedge((x, y), 0.7, 0, 90, color='#FFF') # Espacio negativo
        w3 = patches.Wedge((x, y), 0.4, 0, 90, color=c_acc)
        w1.set_transform(tr)
        w2.set_transform(tr)
        w3.set_transform(tr)
        add_patch_hd(ax, w1)
        add_patch_hd(ax, w2)
        add_patch_hd(ax, w3)

    elif tipo == 'arrow_head': # Punta de flecha
        p = patches.Polygon([(x+0.2, y+0.2), (x+0.5, y+0.8), (x+0.8, y+0.2), (x+0.5, y+0.4)], color=c_main)
        p.set_transform(tr)
        add_patch_hd(ax, p)
    
    elif tipo == 'diamond_split': # Diamante dividido
        p1 = patches.Polygon([(x, y+0.5), (x+0.5, y+1), (x+0.5, y+0.5)], color=c_main)
        p2 = patches.Polygon([(x+0.5, y+0.5), (x+1, y+0.5), (x+0.5, y)], color=c_acc)
        p1.set_transform(tr)
        p2.set_transform(tr)
        add_patch_hd(ax, p1)
        add_patch_hd(ax, p2)

    # --- FORMAS BAUHAUS BÁSICAS (Para rellenar) ---
    elif tipo == 'circle':
        c = patches.Circle((x+0.5, y+0.5), 0.4, color=c_main)
        add_patch_hd(ax, c)
    elif tipo == 'triangle':
        p = patches.Polygon([(x, y), (x+1, y), (x, y+1)], color=c_main)
        p.set_transform(tr)
        add_patch_hd(ax, p)
    elif tipo == 'solid':
        r = patches.Rectangle((x, y), 1, 1, color=c_main)
        add_patch_hd(ax, r)

# --- MOTOR DE SIMETRÍA AVANZADO ---

def generate_grid_advanced(size, user_colors, density, mode):
    
    # 1. Definir la "Unidad Mínima" (Seed)
    # Dependiendo del modo, la semilla es diferente.
    # Caleidoscopio -> Semilla es 1/4 del grid (Top-Left)
    # Repetición -> Semilla es 1 celda que se repite, o un bloque aleatorio completo.
    # Para máxima variedad, usaremos lógica de bloque 4x4 o size//2 como base.
    
    seed_size = size if mode == "Repetición (Papel Pintado)" else size // 2
    if mode == "Ajedrez (Rotación Alterna)": seed_size = size # Generamos todo y luego rotamos
    if mode == "Caleidoscopio (Espejo Central)": seed_size = size // 2
    
    # Lista ampliada de formas
    tile_types = ['star_8', 'lantern', 'petal', 'propeller', 'weave', 'bowtie', 
                  'quarter_sun', 'arrow_head', 'diamond_split', 'circle', 'triangle']
    
    # Generar datos base
    base_data = [[None for _ in range(size)] for _ in range(size)]
    
    # Generamos una pasada completa inicial (ruido base)
    for r in range(size):
        for c in range(size):
            if random.random() > density:
                tipo = 'solid'
                c_main = '#FFFFFF'
                c_acc = '#FFFFFF'
            else:
                tipo = random.choice(tile_types)
                c_main = random.choice(user_colors)
                avail = [x for x in user_colors if x != c_main]
                c_acc = random.choice(avail) if avail else c_main
            
            rot = random.randint(0, 3)
            base_data[r][c] = {'type': tipo, 'rot': rot, 'c_main': c_main, 'c_acc': c_acc}

    # 2. Aplicar Reglas de Simetría (Sobrescribir datos base)
    final_grid = [[None for _ in range(size)] for _ in range(size)]
    
    if mode == "Caleidoscopio (Espejo Central)":
        # Usamos solo el cuadrante superior izquierdo de base_data
        for r in range(seed_size):
            for c in range(seed_size):
                cell = base_data[r][c]
                # Top-Left
                final_grid[r][c] = cell
                # Top-Right (Mirror X)
                tr = cell.copy(); tr['mirror_x'] = True
                final_grid[r][size-1-c] = tr
                # Bot-Left (Mirror Y)
                bl = cell.copy(); bl['mirror_y'] = True
                final_grid[size-1-r][c] = bl
                # Bot-Right (Mirror XY)
                br = cell.copy(); br['mirror_x'] = True; br['mirror_y'] = True
                final_grid[size-1-r][size-1-c] = br
                
    elif mode == "Repetición (Papel Pintado)":
        # Generamos un bloque pequeño (ej 2x2) y lo repetimos
        block_size = 2
        block = [[base_data[r][c] for c in range(block_size)] for r in range(block_size)]
        
        for r in range(size):
            for c in range(size):
                # Copiar del bloque base repitiendo
                cell = block[r % block_size][c % block_size]
                final_grid[r][c] = cell
                
    elif mode == "Ajedrez (Rotación Alterna)":
        # Usamos base_data pero rotamos según posición (i+j)
        for r in range(size):
            for c in range(size):
                cell = base_data[r][c].copy()
                # Si es casilla negra del ajedrez, rotamos 90 extra
                if (r + c) % 2 == 1:
                    cell['rot'] = (cell['rot'] + 1) % 4
                final_grid[r][c] = cell

    return final_grid

def render_final(grid, size):
    # Alta resolución (DPI 100 en visualización, 300 en descarga)
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell is None: continue # Seguridad
            
            x, y = c, size - 1 - r
            rot = cell['rot']
            
            # Lógica de Espejos para Caleidoscopio
            if cell.get('mirror_x'): rot = {0:1, 1:0, 2:3, 3:2}[rot]
            if cell.get('mirror_y'): rot = {0:3, 1:2, 2:1, 3:0}[rot]

            draw_alhambra_tile(ax, x, y, cell['type'], rot, cell['c_main'], cell['c_acc'])

    # Marco Exterior Grueso
    ax.plot([0, size, size, 0, 0], [0, 0, size, size, 0], color='#222', linewidth=5)
    
    return fig

# --- EJECUCIÓN ---

random.seed(st.session_state.seed)

grid_data = generate_grid_advanced(complejidad, colores_usuario, densidad, simetria)
figura = render_final(grid_data, complejidad)

st.pyplot(figura)

# Botón descarga
buf = BytesIO()
figura.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor="#ffffff")
st.download_button(
    label="⬇️ Descargar Imagen HD",
    data=buf.getvalue(),
    file_name="kuki_alhambra.png",
    mime="image/png"
)
