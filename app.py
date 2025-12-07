import streamlit as st
import random
from PIL import Image, ImageDraw, ImageOps
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="BAUHAUS PURO // GENERADOR",
    page_icon="⬛",
    layout="centered"
)

# --- CSS PARA ESTÉTICA BRUTALISTA/BAUHAUS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    h1 {
        font-family: 'Archivo Black', sans-serif;
        text-transform: uppercase;
        font-size: 3em !important;
        color: #111;
        border-bottom: 5px solid #111;
        padding-bottom: 10px;
    }
    .stButton>button {
        background-color: #111 !important;
        color: white !important;
        font-family: 'Archivo Black', sans-serif !important;
        text-transform: uppercase;
        font-size: 1.2em !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 1em 2em !important;
    }
    .stButton>button:hover {
        background-color: #E31C24 !important; /* Rojo Bauhaus al pasar el mouse */
        color: white !important;
    }
    /* Ocultar elementos extra de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DEFINICIÓN DE PALETAS SOLICITADAS ---
PALETTES = {
    "🏛️ Bauhaus Clásica": [
        "#E31C24", # Rojo
        "#006BA6", # Azul
        "#FFD500", # Amarillo
        "#111111", # Negro
        "#F2F2F2"  # Blanco roto
    ],
    "🍋 Cítricas": [
        "#D3E629", # Lima
        "#E9EA2E", # Limón fuerte
        "#F48120", # Naranja
        "#E22C26", # Pomelo rojo
        "#FFFFFF"  # Blanco
    ],
    "💊 Vitamina": [
        "#FF0055", # Rosa fuerte
        "#00C9A7", # Verde menta vibrante
        "#FFD700", # Oro
        "#8338EC", # Violeta
        "#FFFFFF"  # Blanco
    ],
    "🏢 Grises (Hormigón)": [
        "#111111", "#333333", "#555555", "#777777", "#999999", "#CCCCCC", "#E5E5E5"
    ],
    "⬛ Solo Negro (Puro)": [
        "#000000", "#FFFFFF"
    ],
    "🍂 Ocres y Mostaza": [
        "#D19526", # Mostaza
        "#A85B25", # Teja
        "#6E3C1D", # Marrón oscuro
        "#E0C28A", # Arena
        "#211E1A"  # Casi negro
    ]
}

# --- MOTOR DE GEOMETRÍA PURA ---
class BauhausEngine:
    def __init__(self, size=800):
        self.size = size

    def _draw_large_element(self, draw, colors):
        """Dibuja un elemento geométrico grande que domina la composición."""
        color = random.choice(colors)
        shape_type = random.choice(['circle', 'rect', 'triangle', 'thick_line', 'arc'])
        s = self.size
        
        # Usamos una grilla gruesa invisible (8x8) para anclar las formas
        # esto da la sensación de orden dentro del caos.
        grid_step = s // 8
        x1 = random.randint(0, 8) * grid_step
        y1 = random.randint(0, 8) * grid_step
        x2 = random.randint(0, 8) * grid_step
        y2 = random.randint(0, 8) * grid_step
        
        # Asegurar que las coordenadas no sean iguales
        if x1 == x2: x2 += grid_step * random.choice([-2, 2])
        if y1 == y2: y2 += grid_step * random.choice([-2, 2])
        
        # Normalizar coordenadas para dibujar
        lx, rx = min(x1, x2), max(x1, x2)
        ty, by = min(y1, y2), max(y1, y2)

        if shape_type == 'circle':
            # Círculos que a veces se salen del lienzo
            margin = random.randint(-s//4, s//4)
            draw.ellipse([lx-margin, ty-margin, rx+margin, by+margin], fill=color)
            
        elif shape_type == 'rect':
            # Rectángulos sólidos o marcos gruesos
            if random.random() > 0.7:
                # Marco
                thickness = random.choice([grid_step//2, grid_step])
                draw.rectangle([lx, ty, rx, by], outline=color, width=thickness)
            else:
                # Sólido
                draw.rectangle([lx, ty, rx, by], fill=color)

        elif shape_type == 'thick_line':
            # Líneas muy gruesas diagonales o rectas
            thickness = random.choice([grid_step//4, grid_step//2, grid_step])
            # A veces forzamos líneas rectas perfectas
            if random.random() > 0.5:
                if random.random() > 0.5: x2 = x1 # Vertical
                else: y2 = y1 # Horizontal
            draw.line([(x1, y1), (x2, y2)], fill=color, width=thickness)
            
        elif shape_type == 'triangle':
            # Triángulos grandes anclados a esquinas o puntos de grilla
            p3x = random.randint(0, 8) * grid_step
            p3y = random.randint(0, 8) * grid_step
            draw.polygon([(x1, y1), (x2, y2), (p3x, p3y)], fill=color)

        elif shape_type == 'arc':
             # Arcos estilo Bauhaus (cuartos de círculo grueso)
             thickness = grid_step * random.randint(1, 3)
             # Dibujamos un círculo grande y grueso sin relleno
             margin = thickness // 2
             draw.ellipse([lx, ty, rx, by], outline=color, width=thickness)


    def generate(self, palette_name, n_colors, complexity_level):
        # 1. Preparar colores
        full_palette = PALETTES[palette_name]
        
        if palette_name == "⬛ Solo Negro (Puro)":
            # Modo estricto B/N
            bg_color = "#FFFFFF"
            active_colors = ["#000000"]
        else:
            # Selección aleatoria de la paleta elegida
            current_palette = random.sample(full_palette, min(n_colors, len(full_palette)))
            # Asegurar contraste: el primer color es fondo, el resto para elementos
            bg_color = current_palette[0]
            active_colors = current_palette[1:]
            if not active_colors: active_colors = ["#000000"] # Fallback si n_colors es 1

        # 2. Lienzo
        image = Image.new("RGB", (self.size, self.size), bg_color)
        draw = ImageDraw.Draw(image)
        
        # 3. Definir número de elementos según complejidad
        # Mapeamos el slider (1-10) a una cantidad de formas (ej. 3 a 25)
        num_elements = int(complexity_level * 2.5) + random.randint(1, 3)

        # 4. Bucle de generación (Sin semilla, caos puro)
        for _ in range(num_elements):
            self._draw_large_element(draw, active_colors)
            
            # A veces (10%) invertimos los colores a mitad del proceso para efecto dramático
            if random.random() > 0.90 and palette_name != "⬛ Solo Negro (Puro)":
                 image = ImageOps.invert(image)
                 draw = ImageDraw.Draw(image)

        return image

# --- INTERFAZ DE USUARIO ---

st.title("BAUHAUS PURO // VANGUARDIA")
st.markdown("Generador de ilustraciones geométricas únicas en 1x1.")

# Controles en la barra lateral
with st.sidebar:
    st.header("CONTROL DE COMPOSICIÓN")
    
    palette_choice = st.selectbox("PALETA CROMÁTICA", list(PALETTES.keys()), index=0)
    
    # Lógica para bloquear el selector de cantidad si es B/N
    if palette_choice == "⬛ Solo Negro (Puro)":
        st.markdown("**MODO B/N ACTIVO**")
        num_colors_slider = 2 # Valor dummy
        st.caption("Colores fijados a Blanco y Negro estricto.")
    else:
        # Calculamos el máximo de colores disponibles en la paleta elegida
        max_cols = len(PALETTES[palette_choice])
        num_colors_slider = st.slider("CANTIDAD DE COLORES", min_value=2, max_value=max_cols, value=max(2, max_cols-1))

    complexity_slider = st.slider("COMPLEJIDAD GEOMÉTRICA", min_value=1, max_value=10, value=5, help="1 = Minimalista, 10 = Caos Constructivista")

    st.markdown("---")
    st.markdown("Cada clic genera una obra irrepetible.")

# Botón principal (Fuera de la sidebar para protagonismo)
if st.button("GENERAR OBRA ÚNICA AHORA"):
    
    engine = BauhausEngine(size=800)
    
    with st.spinner("CONSTRUYENDO GEOMETRÍA..."):
        # Llamada directa sin semillas
        img = engine.generate(
            palette_name=palette_choice,
            n_colors=num_colors_slider,
            complexity_level=complexity_slider
        )
        
        st.image(img, caption="Composición Geométrica 1x1", use_container_width=True)
        
        # Preparar descarga
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="DESCARGAR PNG (800x800)",
            data=byte_im,
            file_name="bauhaus_puro_obra.png",
            mime="image/png"
        )
else:
    st.info("Define los parámetros y pulsa el botón para crear tu primera obra.")
