import streamlit as st
import random
import math
from PIL import Image, ImageDraw
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Patrones Pro Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CLASE GENERADORA DE PATRONES PRO ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta "Retro/Bauhaus" completa
        self.base_palette = [
            "#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557",
            "#2A9D8F", "#E9C46A", "#F4A261", "#264653", "#000000",
            "#D62828", "#FCBF49", "#EAE2B7"
        ]

    def _get_colors(self, n, seed, bw_mode=False):
        """Gestiona la paleta: Color o Blanco/Negro."""
        if bw_mode:
            return ["#FFFFFF", "#000000"]
        random.seed(seed)
        return random.sample(self.base_palette, min(n, len(self.base_palette)))

    def _draw_shape(self, draw, x, y, s, shape_type, color, outline_color, thickness):
        """
        Dibuja una primitiva geométrica específica.
        x, y: coordenadas
        s: tamaño (size) de la celda
        """
        # Ajuste de grosores seguros
        t = max(1, min(thickness, s // 4))
        
        if shape_type == 'fill':
            draw.rectangle([x, y, x+s, y+s], fill=color)

        elif shape_type == 'circle':
            pad = s * 0.1
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=color, outline=None)

        elif shape_type == 'ring':
            pad = s * 0.1
            for i in range(3):
                inset = pad + (i * t * 1.5)
                if inset < s/2:
                    draw.ellipse([x+inset, y+inset, x+s-inset, y+s-inset], outline=color, width=t)

        elif shape_type == 'quarter_circle':
            # Arco en una esquina (estilo clásico de azulejo)
            # Dibujamos un círculo grande centrado en la esquina (x, y)
            draw.pieslice([x-s, y-s, x+s, y+s], 0, 90, fill=color)

        elif shape_type == 'quarter_circle_inv':
            # Arco en esquina opuesta
            draw.pieslice([x, y, x+s*2, y+s*2], 180, 270, fill=color)

        elif shape_type == 'triangle':
            points = [(x, y), (x+s, y), (x, y+s)]
            draw.polygon(points, fill=color)

        elif shape_type == 'triangle_center':
            points = [(x, y+s), (x+s/2, y), (x+s, y+s)]
            draw.polygon(points, fill=color)

        elif shape_type == 'diamond':
            margin = 0
            points = [(x+s/2, y+margin), (x+s-margin, y+s/2), (x+s/2, y+s-margin), (x+margin, y+s/2)]
            draw.polygon(points, fill=color)

        elif shape_type == 'cross':
            # Cruz gruesa
            w = t * 1.5
            cx, cy = x + s/2, y + s/2
            draw.rectangle([x, cy-w/2, x+s, cy+w/2], fill=color)
            draw.rectangle([cx-w/2, y, cx+w/2, y+s], fill=color)

        elif shape_type == 'x_cross':
            # Cruz en X
            w = t
            draw.line([(x, y), (x+s, y+s)], fill=color, width=int(w))
            draw.line([(x+s, y), (x, y+s)], fill=color, width=int(w))

        elif shape_type == 'stripes_h':
            step = t * 2
            for i in range(0, s, int(step)):
                draw.rectangle([x, y+i, x+s, y+i+t], fill=color)
        
        elif shape_type == 'stripes_v':
            step = t * 2
            for i in range(0, s, int(step)):
                draw.rectangle([x+i, y, x+i+t, y+s], fill=color)

        elif shape_type == 'checker':
            # Tablero de ajedrez 2x2
            half = s // 2
            draw.rectangle([x, y, x+half, y+half], fill=color)
            draw.rectangle([x+half, y+half, x+s, y+s], fill=color)

        elif shape_type == 'frame':
            # Marco cuadrado
            draw.rectangle([x, y, x+s, y+s], outline=color, width=int(t))

    def _draw_cell_complex(self, draw, x, y, cell_size, colors, thickness, seed):
        """
        Sistema de CAPAS:
        En lugar de una forma, apilamos de 1 a 3 formas aleatorias.
        """
        random.seed(seed)
        
        # 1. Color de Fondo
        bg = random.choice(colors)
        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=bg)
        
        # Filtrar colores restantes para contraste
        contrast_colors = [c for c in colors if c != bg]
        if not contrast_colors: contrast_colors = [bg] # Fallback

        # 2. Decidir cuántas capas de formas tendrá esta celda (1, 2 o 3)
        # Esto aumenta la variedad exponencialmente
        num_layers = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2], k=1)[0]
        
        shapes_available = [
            'circle', 'quarter_circle', 'quarter_circle_inv', 'triangle', 
            'triangle_center', 'diamond', 'cross', 'x_cross', 
            'stripes_h', 'stripes_v', 'checker', 'ring', 'frame'
        ]

        for _ in range(num_layers):
            shape = random.choice(shapes_available)
            color = random.choice(contrast_colors)
            
            # Dibujar forma
            self._draw_shape(draw, x, y, cell_size, shape, color, bg, thickness)
            
            # A veces cambiamos el color para la siguiente capa
            if len(contrast_colors) > 1:
                contrast_colors = [c for c in contrast_colors if c != color]
                if not contrast_colors: contrast_colors = [color]

    def generate(self, num_colors=4, thickness=20, grid_divisions=4, seed=42, bw_mode=False):
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        selected_colors = self._get_colors(num_colors, seed, bw_mode)
        cell_size = self.size // grid_divisions
        half_grid = (grid_divisions + 1) // 2 

        for i in range(half_grid):
            for j in range(half_grid):
                x = i * cell_size
                y = j * cell_size
                
                # Semilla única por celda
                cell_seed = seed + (i * 999) + (j * 777)
                
                cell_img = Image.new("RGB", (cell_size, cell_size))
                cell_draw = ImageDraw.Draw(cell_img)
                
                # LLAMADA A LA FUNCIÓN COMPLEJA
                self._draw_cell_complex(cell_draw, 0, 0, cell_size, selected_colors, thickness, cell_seed)
                
                # --- SIMETRÍA CALEIDOSCÓPICA ---
                # Pegar cuadrante 1 (Top-Left)
                image.paste(cell_img, (x, y)) 
                
                # Pegar cuadrante 2 (Top-Right) -> Espejo Horizontal
                tr_x = self.size - cell_size - x
                image.paste(cell_img.transpose(Image.FLIP_LEFT_RIGHT), (tr_x, y))
                
                # Pegar cuadrante 3 (Bottom-Left) -> Espejo Vertical
                bl_y = self.size - cell_size - y
                image.paste(cell_img.transpose(Image.FLIP_TOP_BOTTOM), (x, bl_y))
                
                # Pegar cuadrante 4 (Bottom-Right) -> Rotación 180 (Espejo doble)
                image.paste(cell_img.transpose(Image.ROTATE_180), (tr_x, bl_y))

        return image

# --- INTERFAZ STREAMLIT ---

st.title("Patrones Pro Studio")
st.markdown("**by nico.bastida**")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("🎛️ Centro de Control")
    
    # Checkbox para modo B/N
    bw_mode = st.checkbox("🔲 Modo 1 Tinta (Blanco y Negro)", value=False, help="Fuerza el diseño a alto contraste puro.")
    
    seed_val = st.number_input("Semilla Genética (Seed)", value=42)
    
    # Desactivamos color slider si está en B/N
    if not bw_mode:
        num_colors = st.slider("Variedad Cromática", 2, 10, 5)
    else:
        num_colors = 2 # Dummy value
        st.caption("Modo B/N activo: Color desactivado.")

    thickness = st.slider("Grosor de Trazo", 5, 50, 20)
    complexity = st.select_slider("Resolución de Grilla", options=[2, 4, 6, 8, 10, 12, 16], value=4)
    
    st.markdown("---")
    if st.button("🎲 REGENERAR"):
        seed_val = random.randint(0, 99999)

# Lógica Principal
generator = PatternGenerator(size=800)

try:
    with st.spinner("Computando geometría..."):
        img = generator.generate(
            num_colors=num_colors, 
            thickness=thickness, 
            grid_divisions=complexity, 
            seed=seed_val,
            bw_mode=bw_mode
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image(img, caption=f"Diseño Generado #{seed_val}", use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        filename = f"patron_pro_{'BN' if bw_mode else 'color'}_{seed_val}.png"
        
        st.download_button(
            label="⬇️ DESCARGAR MASTER (PNG 800px)",
            data=byte_im,
            file_name=filename,
            mime="image/png",
            type="primary"
        )

except Exception as e:
    st.error("Error en la matriz de generación.")
    st.code(e)
