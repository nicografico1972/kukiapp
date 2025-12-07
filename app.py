import streamlit as st
import random
from PIL import Image, ImageDraw
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Patrones Pro Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CLASE GENERADORA DE PATRONES ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta de colores inspirada en la imagen de referencia
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

        # Limitar el grosor para evitar errores gráficos en celdas pequeñas
        safe_thickness = min(thickness, cell_size // 3)

        if pattern_type == 'triangle_half':
            points = [(x, y), (x + cell_size, y), (x, y + cell_size)]
            draw.polygon(points, fill=fg_color)
            
        elif pattern_type == 'corner_triangle':
            offset = cell_size // 2
            points = [(x, y), (x + offset, y), (x, y + offset)]
            draw.polygon(points, fill=accent_color)

        elif pattern_type == 'diamond':
            margin = safe_thickness // 2
            # Aseguramos que el margen no colapse la figura
            if margin >= cell_size // 2: margin = (cell_size // 2) - 2
            
            points = [
                (x + cell_size // 2, y + margin),
                (x + cell_size - margin, y + cell_size // 2),
                (x + cell_size // 2, y + cell_size - margin),
                (x + margin, y + cell_size // 2)
            ]
            draw.polygon(points, fill=fg_color)
            
            if random.random() > 0.5:
                inner_margin = cell_size // 3
                if inner_margin < cell_size // 2:
                    draw.rectangle([x + inner_margin, y + inner_margin, x + cell_size - inner_margin, y + cell_size - inner_margin], fill=accent_color)

        elif pattern_type == 'cross':
            w = safe_thickness
            cx, cy = x + cell_size // 2, y + cell_size // 2
            draw.rectangle([x, cy - w//2, x + cell_size, cy + w//2], fill=fg_color)
            draw.rectangle([cx - w//2, y, cx + w//2, y + cell_size], fill=fg_color)

        elif pattern_type == 'concentric':
            steps = 3
            step_size = cell_size // (steps * 2)
            if step_size < 1: step_size = 1 # Evitar división por cero o pasos nulos

            for i in range(steps):
                current_color = fg_color if i % 2 == 0 else accent_color
                
                # --- CORRECCIÓN DEL ERROR ---
                # Calculamos el margen deseado
                raw_margin = i * step_size * (thickness / 20)
                
                # Forzamos que el margen NUNCA sea mayor que la mitad de la celda - 1 pixel
                # Esto evita el ValueError "coordinate invalid"
                max_allowed_margin = (cell_size // 2) - 2
                margin = min(int(raw_margin), max_allowed_margin)
                
                if margin < 0: margin = 0 # Seguridad extra

                # Solo dibujamos si hay espacio suficiente
                if margin < max_allowed_margin:
                    draw.rectangle(
                        [x + margin, y + margin, x + cell_size - margin, y + cell_size - margin], 
                        outline=current_color, 
                        width=max(1, int(safe_thickness/2))
                    )

        elif pattern_type == 'stripes':
            width_line = max(1, int(safe_thickness / 2))
            for i in range(0, cell_size * 2, width_line * 2):
                # Dibujar líneas diagonales excediendo los bordes para recortar después (técnica simple)
                # Aquí usamos la técnica de líneas dentro de la caja
                p1 = (x, y + i)
                p2 = (x + i, y)
                # Solo dibujar si los puntos están razonablemente cerca
                draw.line([p1, p2], fill=fg_color, width=width_line)

    def generate(self, num_colors=4, thickness=20, grid_divisions=4, seed=42):
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        selected_colors = self._get_random_colors(num_colors, seed)
        cell_size = self.size // grid_divisions
        half_grid = (grid_divisions + 1) // 2 

        for i in range(half_grid):
            for j in range(half_grid):
                x = i * cell_size
                y = j * cell_size
                cell_seed = seed + (i * 100) + j
                
                cell_img = Image.new("RGB", (cell_size, cell_size))
                cell_draw = ImageDraw.Draw(cell_img)
                
                self._draw_cell_pattern(cell_draw, 0, 0, cell_size, selected_colors, thickness, cell_seed)
                
                # Simetría (Espejos)
                image.paste(cell_img, (x, y)) # Top-Left
                
                tr_x = self.size - cell_size - x
                image.paste(cell_img.transpose(Image.FLIP_LEFT_RIGHT), (tr_x, y)) # Top-Right
                
                bl_y = self.size - cell_size - y
                image.paste(cell_img.transpose(Image.FLIP_TOP_BOTTOM), (x, bl_y)) # Bottom-Left
                
                image.paste(cell_img.transpose(Image.ROTATE_180), (tr_x, bl_y)) # Bottom-Right

        return image

# --- INTERFAZ STREAMLIT ---

# Títulos personalizados solicitados
st.title("Patrones Pro Studio")
st.markdown("**by nico.bastida**")
st.markdown("---")

st.markdown("""
Genera patrones abstractos estilo "azulejo" listos para usar. 
Ajusta los parámetros en la barra lateral y crea composiciones únicas.
""")

# Barra Lateral
with st.sidebar:
    st.header("Parámetros del Diseño")
    
    seed_val = st.number_input("Semilla (Seed)", value=42, help="Cambia este número para obtener un diseño completamente distinto.")
    num_colors = st.slider("Número de Colores", min_value=2, max_value=8, value=4)
    thickness = st.slider("Grosor / Densidad", min_value=5, max_value=60, value=30)
    complexity = st.select_slider("Complejidad de la Grilla", options=[2, 4, 6, 8, 10], value=4)
    
    if st.button("🎲 Generar Nuevo Patrón Aleatorio"):
        seed_val = random.randint(0, 10000)
    
    st.info(f"Semilla actual: {seed_val}")

# Generación
generator = PatternGenerator(size=800)

try:
    img = generator.generate(
        num_colors=num_colors, 
        thickness=thickness, 
        grid_divisions=complexity, 
        seed=seed_val
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, caption=f"Patrón Generado (Seed: {seed_val})", use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Descargar Patrón PNG",
            data=byte_im,
            file_name=f"patron_pro_{seed_val}.png",
            mime="image/png"
        )

except Exception as e:
    st.error(f"Ocurrió un error al generar el patrón: {e}")
    st.warning("Prueba a reducir un poco el 'Grosor' o la 'Complejidad'.")
