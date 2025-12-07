import streamlit as st
import random
import math
from PIL import Image, ImageDraw, ImageOps

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Patrones Pro Studio - Ultra",
    page_icon="🎨",
    layout="wide"
)

# --- CLASE GENERADORA MAESTRA ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta Pop / Neo-Geo sofisticada
        self.base_palette = [
            "#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557",
            "#2A9D8F", "#E9C46A", "#F4A261", "#264653", "#000000",
            "#D62828", "#FCBF49", "#003049", "#D62828", "#F77F00"
        ]

    def _get_colors(self, n, seed, bw_mode=False):
        if bw_mode:
            return ["#FFFFFF", "#000000"]
        random.seed(seed)
        return random.sample(self.base_palette, min(n, len(self.base_palette)))

    # --- NUEVAS PRIMITIVAS SOFISTICADAS ---
    def _draw_complex_shape(self, draw, x, y, s, shape_type, fg, bg, accent, thickness):
        """
        Dibuja formas compuestas de alto nivel (estilo Swiss/Bauhaus).
        """
        t = max(2, min(thickness, s // 6)) # Grosor seguro
        cx, cy = x + s/2, y + s/2
        
        # 1. ARCOS Y CURVAS (BAUHAUS)
        if shape_type == 'quarter_arc_thick':
            # Arco grueso en esquina
            draw.pieslice([x-s/2, y-s/2, x+s/2, y+s/2], 0, 90, fill=fg)
            draw.pieslice([x, y, x+s, y+s], 180, 270, fill=accent)
            
        elif shape_type == 'semi_circle_mix':
            # Semicírculo con mitad cuadrada
            draw.rectangle([x, y, x+s, y+s/2], fill=bg)
            draw.pieslice([x, y, x+s, y+s], 180, 360, fill=fg)
            
        elif shape_type == 'circle_hollow':
            # Donut / Anillo grueso
            pad = s * 0.15
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=fg)
            inner_pad = s * 0.35
            draw.ellipse([x+inner_pad, y+inner_pad, x+s-inner_pad, y+s-inner_pad], fill=bg)

        elif shape_type == 'eye':
            # Forma de ojo
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 0, 180, fill=fg) # Párpado superior (aprox)
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 180, 360, fill=fg) # Párpado inferior
            # Iris
            pad = s * 0.25
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=bg)
            # Pupila
            pad2 = s * 0.4
            draw.ellipse([x+pad2, y+pad2, x+s-pad2, y+s-pad2], fill=accent)

        # 2. GEOMETRÍA RECTILÍNEA (MEMPHIS)
        elif shape_type == 'stairs':
            # Escalera
            step = s / 4
            points = [
                (x, y+s), (x+step, y+s), (x+step, y+s-step), 
                (x+step*2, y+s-step), (x+step*2, y+s-step*2),
                (x+step*3, y+s-step*2), (x+step*3, y),
                (x, y)
            ]
            draw.polygon(points, fill=fg)

        elif shape_type == 'triangle_split':
            # Dos triángulos formando cuadrado
            draw.polygon([(x,y), (x+s,y), (x,y+s)], fill=fg)
            draw.polygon([(x+s,y+s), (x+s,y), (x,y+s)], fill=accent)

        elif shape_type == 'stripes_diagonal':
            # Relleno de rayas diagonales (Textura)
            draw.rectangle([x,y,x+s,y+s], fill=bg)
            width_line = int(t / 2)
            step = width_line * 3
            for i in range(-s, s*2, step):
                draw.line([(x+i, y), (x+i+s, y+s)], fill=fg, width=width_line)

        elif shape_type == 'checker_circle':
            # Círculo sobre ajedrez
            half = s/2
            draw.rectangle([x,y, x+half, y+half], fill=fg)
            draw.rectangle([x+half, y+half, x+s, y+s], fill=fg)
            draw.rectangle([x+half, y, x+s, y+half], fill=bg)
            draw.rectangle([x, y+half, x+half, y+s], fill=bg)
            # Círculo encima
            pad = s * 0.2
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=accent)

        elif shape_type == 'sunburst':
            # Rayos de sol desde una esquina
            draw.rectangle([x,y,x+s,y+s], fill=bg)
            cx, cy = x + s/2, y + s/2
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                end_x = cx + (s * 0.8) * math.cos(rad)
                end_y = cy + (s * 0.8) * math.sin(rad)
                draw.line([(cx, cy), (end_x, end_y)], fill=fg, width=int(t))

        # 3. FORMAS BÁSICAS (Relleno)
        elif shape_type == 'solid':
            draw.rectangle([x, y, x+s, y+s], fill=fg)
        
        elif shape_type == 'frame':
            draw.rectangle([x, y, x+s, y+s], outline=fg, width=int(t))

    def generate(self, num_colors, thickness, grid_divisions, seed, bw_mode, style_mode):
        # Lienzo principal
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        selected_colors = self._get_colors(num_colors, seed, bw_mode)
        cell_size = self.size // grid_divisions
        half_grid = (grid_divisions + 1) // 2 

        # Definir el pool de formas según el estilo elegido
        if style_mode == "Bauhaus (Curvas)":
            shapes_pool = ['quarter_arc_thick', 'semi_circle_mix', 'circle_hollow', 'solid', 'eye']
        elif style_mode == "Memphis (Geo/Texture)":
            shapes_pool = ['stairs', 'triangle_split', 'stripes_diagonal', 'checker_circle', 'frame', 'solid']
        else: # "Mix Complejo"
            shapes_pool = ['quarter_arc_thick', 'semi_circle_mix', 'circle_hollow', 'eye', 
                           'stairs', 'triangle_split', 'stripes_diagonal', 'checker_circle', 'sunburst', 'solid']

        for i in range(half_grid):
            for j in range(half_grid):
                # Coordenadas
                x = i * cell_size
                y = j * cell_size
                
                # Semilla local
                local_seed = seed + (i * 123) + (j * 456)
                random.seed(local_seed)
                
                # Crear celda
                cell_img = Image.new("RGB", (cell_size, cell_size))
                cell_draw = ImageDraw.Draw(cell_img)
                
                # Selección de colores locales
                bg = random.choice(selected_colors)
                fg = random.choice([c for c in selected_colors if c != bg])
                accent = random.choice([c for c in selected_colors if c not in [bg, fg]])
                if not accent: accent = fg # Fallback si hay pocos colores
                
                # 1. PINTAR FONDO
                cell_draw.rectangle([0, 0, cell_size, cell_size], fill=bg)
                
                # 2. PINTAR FORMA COMPLEJA
                # A veces superponemos 2 formas para más complejidad
                shape1 = random.choice(shapes_pool)
                self._draw_complex_shape(cell_draw, 0, 0, cell_size, shape1, fg, bg, accent, thickness)
                
                # 30% de probabilidad de segunda capa (Overlay)
                if random.random() > 0.7:
                    shape2 = random.choice(['frame', 'circle_hollow', 'stripes_diagonal'])
                    # Usamos color de acento para la capa superior
                    self._draw_complex_shape(cell_draw, 0, 0, cell_size, shape2, accent, bg, fg, thickness)

                # --- SIMETRÍA Y PEGADO ---
                image.paste(cell_img, (x, y)) 
                
                # Espejos para formar el mosaico
                tr_x = self.size - cell_size - x
                image.paste(cell_img.transpose(Image.FLIP_LEFT_RIGHT), (tr_x, y))
                
                bl_y = self.size - cell_size - y
                image.paste(cell_img.transpose(Image.FLIP_TOP_BOTTOM), (x, bl_y))
                
                image.paste(cell_img.transpose(Image.ROTATE_180), (tr_x, bl_y))

        return image

# --- INTERFAZ STREAMLIT ---

st.title("Patrones Pro Studio")
st.markdown("**by nico.bastida** | *V4.0 Ultra-Complex Edition*")
st.markdown("---")

with st.sidebar:
    st.header("🎛️ Centro de Mando")
    
    # Modo de Estilo (NUEVO)
    style_mode = st.selectbox(
        "Estilo de Diseño",
        ["Mix Complejo", "Bauhaus (Curvas)", "Memphis (Geo/Texture)"],
        index=0,
        help="Define qué tipo de geometría predomina en el diseño."
    )
    
    bw_mode = st.checkbox("🔲 Modo 1 Tinta (B/N)", value=False)
    
    seed_val = st.number_input("Semilla (Seed)", value=99)
    
    if not bw_mode:
        num_colors = st.slider("Paleta de Colores", 2, 8, 4)
    else:
        num_colors = 2
        
    thickness = st.slider("Grosor de Elementos", 5, 40, 15)
    complexity = st.select_slider("Resolución de Grilla", options=[2, 4, 6, 8, 10, 12], value=6)
    
    st.markdown("---")
    if st.button("🎲 GENERAR DISEÑO", type="primary"):
        seed_val = random.randint(0, 99999)

# Ejecución
generator = PatternGenerator(size=800)

try:
    with st.spinner("Renderizando geometría compleja..."):
        img = generator.generate(
            num_colors=num_colors, 
            thickness=thickness, 
            grid_divisions=complexity, 
            seed=seed_val,
            bw_mode=bw_mode,
            style_mode=style_mode
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image(img, caption=f"Diseño: {style_mode} | Seed: {seed_val}", use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ DESCARGAR ARTE FINAL (PNG)",
            data=byte_im,
            file_name=f"patron_ultra_{seed_val}.png",
            mime="image/png",
            type="primary"
        )

except Exception as e:
    st.error("Error en el renderizado.")
    st.warning(f"Detalle: {e}")
