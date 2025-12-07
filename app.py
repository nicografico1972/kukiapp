import streamlit as st
import random
from PIL import Image, ImageDraw, ImageOps
import io

# --- CONFIGURACIÓN TÉCNICA ---
st.set_page_config(
    page_title="GENERADOR BAUHAUS",
    layout="centered"
)

# --- ESTÉTICA BRUTALISTA (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', Helvetica, Arial, sans-serif;
    }
    h1 {
        font-weight: 900;
        text-transform: uppercase;
        font-size: 3.5em !important;
        color: #000;
        border-bottom: 6px solid #000;
        letter-spacing: -2px;
        padding-bottom: 20px;
    }
    .stButton>button {
        background-color: #000 !important;
        color: #FFF !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        font-size: 1.5em !important;
        border-radius: 0px !important;
        border: 2px solid #000 !important;
        padding: 1em 2em !important;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #FFF !important;
        color: #000 !important;
    }
    /* Ocultar decoración de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- PALETAS DE COLOR (TEXTO PLANO) ---
PALETTES = {
    "Bauhaus Clasica": [
        "#E31C24", "#006BA6", "#FFD500", "#111111", "#F2F2F2"
    ],
    "Citricas": [
        "#D3E629", "#E9EA2E", "#F48120", "#E22C26", "#FFFFFF"
    ],
    "Vitamina": [
        "#FF0055", "#00C9A7", "#FFD700", "#8338EC", "#FFFFFF"
    ],
    "Grises Hormigon": [
        "#111111", "#333333", "#555555", "#777777", "#999999", "#CCCCCC", "#E5E5E5"
    ],
    "Solo Negro": [
        "#000000", "#FFFFFF"
    ],
    "Ocres y Mostaza": [
        "#D19526", "#A85B25", "#6E3C1D", "#E0C28A", "#211E1A"
    ]
}

# --- MOTOR GRÁFICO ---
class BauhausEngine:
    def __init__(self, size=800):
        self.size = size

    def _get_safe_coords(self, x1, y1, x2, y2):
        """
        CORRECCIÓN DEL ERROR:
        Ordena las coordenadas para evitar que PIL reciba valores invertidos
        (ej: izquierda mayor que derecha) que causan el ValueError.
        """
        lx, rx = min(x1, x2), max(x1, x2)
        ty, by = min(y1, y2), max(y1, y2)
        return lx, ty, rx, by

    def _draw_large_element(self, draw, colors):
        color = random.choice(colors)
        shape_type = random.choice(['circle', 'rect', 'triangle', 'thick_line', 'arc'])
        s = self.size
        
        # Grilla base 8x8
        step = s // 8
        
        # Coordenadas aleatorias ancladas a la grilla
        x1 = random.randint(0, 8) * step
        y1 = random.randint(0, 8) * step
        x2 = random.randint(0, 8) * step
        y2 = random.randint(0, 8) * step
        
        # Evitar coordenadas idénticas (puntos invisibles)
        if x1 == x2: x2 += step * random.choice([-2, 2])
        if y1 == y2: y2 += step * random.choice([-2, 2])

        # Obtener coordenadas seguras base
        lx, ty, rx, by = self._get_safe_coords(x1, y1, x2, y2)

        if shape_type == 'circle':
            # Margen aleatorio
            margin = random.randint(-step, step)
            # Recalculamos coordenadas con margen y VOLVEMOS a asegurar el orden
            # Esto arregla el crash específico de tu captura de pantalla
            cx1, cy1 = lx - margin, ty - margin
            cx2, cy2 = rx + margin, by + margin
            final_lx, final_ty, final_rx, final_by = self._get_safe_coords(cx1, cy1, cx2, cy2)
            
            draw.ellipse([final_lx, final_ty, final_rx, final_by], fill=color)
            
        elif shape_type == 'rect':
            if random.random() > 0.7:
                # Marco grueso
                w_line = random.choice([step//2, step])
                # Dibujar rectángulo manual para controlar el borde interior
                draw.rectangle([lx, ty, rx, by], fill=None, outline=color, width=w_line)
            else:
                # Sólido
                draw.rectangle([lx, ty, rx, by], fill=color)

        elif shape_type == 'thick_line':
            w_line = random.choice([step//4, step//2, step])
            draw.line([(x1, y1), (x2, y2)], fill=color, width=w_line)
            
        elif shape_type == 'triangle':
            p3x = random.randint(0, 8) * step
            p3y = random.randint(0, 8) * step
            draw.polygon([(x1, y1), (x2, y2), (p3x, p3y)], fill=color)

        elif shape_type == 'arc':
             w_line = step * random.randint(1, 2)
             draw.arc([lx, ty, rx, by], start=0, end=random.choice([90, 180, 270, 360]), fill=color, width=w_line)

    def generate(self, palette_name, n_colors, complexity):
        # Selección segura de colores
        full_palette = PALETTES[palette_name]
        
        if palette_name == "Solo Negro":
            bg_color = "#FFFFFF"
            active_colors = ["#000000"]
        else:
            # Garantizar que n_colors no exceda la longitud de la paleta
            limit = min(n_colors, len(full_palette))
            current_palette = random.sample(full_palette, limit)
            
            bg_color = current_palette[0]
            # Si solo hay 1 color (raro, pero posible), usar negro como activo
            active_colors = current_palette[1:] if len(current_palette) > 1 else ["#000000"]

        image = Image.new("RGB", (self.size, self.size), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Cantidad de formas basada en complejidad
        count = int(complexity * 2.5) + 2

        for _ in range(count):
            self._draw_large_element(draw, active_colors)
            
            # Inversión de color ocasional (Efecto negativo)
            if random.random() > 0.92 and palette_name != "Solo Negro":
                 image = ImageOps.invert(image)
                 draw = ImageDraw.Draw(image)

        return image

# --- INTERFAZ ---

st.title("GENERADOR BAUHAUS")
st.markdown("SISTEMA DE DISEÑO GENERATIVO 1X1")

with st.sidebar:
    st.markdown("### PARAMETROS")
    
    p_name = st.selectbox("PALETA", list(PALETTES.keys()), index=0)
    
    if p_name == "Solo Negro":
        st.info("MODO MONOCROMO ACTIVO")
        n_slider = 2
    else:
        max_c = len(PALETTES[p_name])
        n_slider = st.slider("CANTIDAD COLORES", 2, max_c, max_c)

    c_slider = st.slider("COMPLEJIDAD", 1, 10, 5)

# Botón principal
if st.button("GENERAR OBRA NUEVA"):
    
    engine = BauhausEngine(size=800)
    
    # Manejo de errores silencioso (por seguridad extrema)
    try:
        img = engine.generate(p_name, n_slider, c_slider)
        st.image(img, use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="DESCARGAR PNG",
            data=byte_im,
            file_name="bauhaus_generativo.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Error en calculo de geometria: {e}")
