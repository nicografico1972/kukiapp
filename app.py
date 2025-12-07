import streamlit as st
import random
from PIL import Image, ImageDraw
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Mosaicos Geométricos",
    page_icon="🎨",
    layout="wide"
)

# --- CLASE GENERADORA DE PATRONES ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta de colores inspirada en la imagen de referencia (Bauhaus / Retro)
        self.base_palette = [
            "#E63946",  # Rojo vivo
            "#F1FAEE",  # Blanco crema
            "#A8DADC",  # Azul claro
            "#457B9D",  # Azul medio
            "#1D3557",  # Azul oscuro / Negro
            "#2A9D8F",  # Verde azulado
            "#E9C46A",  # Amarillo ocre
            "#F4A261",  # Naranja
            "#264653"   # Verde oscuro casi negro
        ]

    def _get_random_colors(self, n, seed):
        """Selecciona n colores aleatorios de la paleta base."""
        random.seed(seed)
        return random.sample(self.base_palette, min(n, len(self.base_palette)))

    def _draw_cell_pattern(self, draw, x, y, cell_size, colors, thickness, style_seed):
        """
        Dibuja un patrón geométrico dentro de una celda específica.
        Se eligen formas abstractas basadas en la imagen de referencia.
        """
        random.seed(style_seed)
        
        # Colores para esta celda
        bg_color = random.choice(colors)
        fg_color = random.choice([c for c in colors if c != bg_color])
        accent_color = random.choice([c for c in colors if c != bg_color])

        # Fondo base de la celda
        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=bg_color)

        # Tipos de patrones geométricos
        pattern_type = random.choice(['triangle_half', 'diamond', 'cross', 'concentric', 'stripes', 'corner_triangle'])

        if pattern_type == 'triangle_half':
            # Triángulo diagonal (mitad de la celda)
            points = [(x, y), (x + cell_size, y), (x, y + cell_size)]
            draw.polygon(points, fill=fg_color)
            
        elif pattern_type == 'corner_triangle':
            # Triángulo pequeño en esquina
            offset = cell_size // 2
            points = [(x, y), (x + offset, y), (x, y + offset)]
            draw.polygon(points, fill=accent_color)

        elif pattern_type == 'diamond':
            # Rombo central
            margin = thickness // 2
            points = [
                (x + cell_size // 2, y + margin),
                (x + cell_size - margin, y + cell_size // 2),
                (x + cell_size // 2, y + cell_size - margin),
                (x + margin, y + cell_size // 2)
            ]
            draw.polygon(points, fill=fg_color)
            # Centro opcional
            if random.random() > 0.5:
                inner_margin = cell_size // 3
                draw.rectangle([x + inner_margin, y + inner_margin, x + cell_size - inner_margin, y + cell_size - inner_margin], fill=accent_color)

        elif pattern_type == 'cross':
            # Cruz gruesa
            w = thickness
            cx, cy = x + cell_size // 2, y + cell_size // 2
            # Horizontal
            draw.rectangle([x, cy - w//2, x + cell_size, cy + w//2], fill=fg_color)
            # Vertical
            draw.rectangle([cx - w//2, y, cx + w//2, y + cell_size], fill=fg_color)

        elif pattern_type == 'concentric':
            # Cuadrados concéntricos
            steps = 3
            step_size = cell_size // (steps * 2)
            for i in range(steps):
                current_color = fg_color if i % 2 == 0 else accent_color
                margin = i * step_size * (thickness / 20) # Ajuste por grosor
                draw.rectangle(
                    [x + margin, y + margin, x + cell_size - margin, y + cell_size - margin], 
                    outline=current_color, 
                    width=int(thickness/2)
                )

        elif pattern_type == 'stripes':
            # Bandas diagonales
            width_line = max(1, int(thickness / 2))
            for i in range(0, cell_size * 2, width_line * 2):
                draw.line([(x, y + i), (x + i, y)], fill=fg_color, width=width_line)

    def generate(self, num_colors=4, thickness=20, grid_divisions=4, seed=42):
        """
        Genera el mosaico completo 800x800.
        Estrategia: Generar el cuadrante superior izquierdo y reflejarlo (Simetría)
        para lograr el efecto de azulejo coherente.
        """
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        selected_colors = self._get_random_colors(num_colors, seed)
        
        # Tamaño de cada celda en la grilla
        cell_size = self.size // grid_divisions
        
        # Iteramos solo sobre la mitad de la grilla para crear simetría
        # Si grid_divisions es impar, redondeamos hacia arriba para cubrir el centro
        half_grid = (grid_divisions + 1) // 2 

        for i in range(half_grid):
            for j in range(half_grid):
                # Coordenadas base
                x = i * cell_size
                y = j * cell_size
                
                # Semilla única para esta posición para consistencia
                cell_seed = seed + (i * 100) + j
                
                # Creamos una imagen temporal pequeña para la celda
                cell_img = Image.new("RGB", (cell_size, cell_size))
                cell_draw = ImageDraw.Draw(cell_img)
                
                # Dibujamos el patrón en la celda base (0,0 relativo)
                self._draw_cell_pattern(cell_draw, 0, 0, cell_size, selected_colors, thickness, cell_seed)
                
                # --- APLICAR SIMETRÍA (Reflejar en los 4 cuadrantes) ---
                
                # 1. Top-Left (Original)
                image.paste(cell_img, (x, y))
                
                # 2. Top-Right (Espejo Horizontal)
                tr_x = self.size - cell_size - x
                image.paste(cell_img.transpose(Image.FLIP_LEFT_RIGHT), (tr_x, y))
                
                # 3. Bottom-Left (Espejo Vertical)
                bl_y = self.size - cell_size - y
                image.paste(cell_img.transpose(Image.FLIP_TOP_BOTTOM), (x, bl_y))
                
                # 4. Bottom-Right (Espejo Total)
                image.paste(cell_img.transpose(Image.ROTATE_180), (tr_x, bl_y))

        return image

# --- INTERFAZ STREAMLIT ---

st.title("🧩 Generador de Mosaicos Geométricos")
st.markdown("""
Genera patrones abstractos estilo "azulejo" listos para usar. 
Ajusta los parámetros en la barra lateral y crea composiciones únicas.
""")

# Barra Lateral de Controles
with st.sidebar:
    st.header("Parámetros del Diseño")
    
    seed_val = st.number_input("Semilla (Seed)", value=42, help="Cambia este número para obtener un diseño completamente distinto.")
    
    num_colors = st.slider("Número de Colores", min_value=2, max_value=8, value=4)
    
    thickness = st.slider("Grosor / Densidad", min_value=5, max_value=60, value=30, help="Controla el ancho de líneas y marcos.")
    
    complexity = st.select_slider("Complejidad de la Grilla", options=[2, 4, 6, 8, 10], value=4, help="Define en cuántas celdas se divide el lienzo.")
    
    if st.button("🎲 Generar Nuevo Patrón Aleatorio"):
        seed_val = random.randint(0, 10000)
        # Hack para actualizar el input number visualmente requiere rerun, 
        # pero para simplicidad solo actualizamos la generación.
    
    st.info(f"Semilla actual: {seed_val}")

# Lógica Principal
generator = PatternGenerator(size=800)

# Generar imagen
img = generator.generate(
    num_colors=num_colors, 
    thickness=thickness, 
    grid_divisions=complexity, 
    seed=seed_val
)

# Columnas para centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(img, caption=f"Patrón Generado (Seed: {seed_val})", use_container_width=True)
    
    # Preparar descarga
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="⬇️ Descargar Patrón PNG (800x800)",
        data=byte_im,
        file_name=f"patron_geometrico_{seed_val}.png",
        mime="image/png"
    )

st.markdown("---")
st.markdown("**Nota:** El algoritmo utiliza una grilla simétrica para asegurar que el patrón se sienta como un 'azulejo' completo y estético, similar a los patrones Bauhuas o hidráulicos.")
