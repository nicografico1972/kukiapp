import streamlit as st
import random
import math
from PIL import Image, ImageDraw

# --- CONFIGURACIÓN DE LA PÁGINA (MODO FULL) ---
st.set_page_config(
    page_title="Patrones Pro Studio - CHAOS",
    page_icon="⚡",
    layout="wide"
)

# --- PALETAS DE COLORES (NUEVAS) ---
PALETTES = {
    "Clásica (Bauhaus)": [
        "#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557",
        "#2A9D8F", "#E9C46A", "#F4A261", "#264653"
    ],
    "Industrial (Cemento & Peligro)": [
        "#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429", 
        "#FFD700", "#14213D", "#E5E5E5", "#000000"
    ],
    "Fluorescente (Neon/Cyber)": [
        "#FF00FF", "#00FF00", "#00FFFF", "#FFFF00", "#FF0099", 
        "#7900FF", "#FF3300", "#121212", "#FFFFFF"
    ],
    "Vitaminas (Cítricos & Fruta)": [
        "#FF7D00", "#FFD000", "#C1FF00", "#00C9A7", "#FF0055", 
        "#FF9900", "#FFE600", "#8338EC", "#3A86FF"
    ],
    "1 Tinta (Blanco y Negro)": ["#FFFFFF", "#000000"]
}

# --- CLASE GENERADORA ---
class ChaosGenerator:
    def __init__(self, size=800):
        self.size = size

    def _get_colors(self, palette_name, n, seed):
        """Devuelve colores de la paleta seleccionada."""
        random.seed(seed)
        base_colors = PALETTES[palette_name]
        
        # Selección segura
        palette = random.sample(base_colors, min(n, len(base_colors)))
        while len(palette) < 3:
            palette.append(random.choice(palette))
        return palette

    def _safe_draw_rect(self, draw, x, y, w, h, color):
        if w <= 0 or h <= 0: return
        draw.rectangle([x, y, x+w, y+h], fill=color)

    def _draw_element(self, draw, x, y, s, colors, thickness, seed, style_mode):
        random.seed(seed)
        
        # Mezclar colores para esta celda
        c_bg, c_fg, c_acc = random.sample(colors, 3) if len(colors) >= 3 else (colors[0], colors[1], colors[0])
        
        t = max(1, min(thickness, int(s * 0.25)))

        # Pools de formas
        bauhaus = ['quarter_leaf', 'split_circle', 'striped_circle', 'eye', 'arch', 'circle_hollow']
        memphis = ['corner_stairs', 'diagonal_split', 'grid_dots', 'triangle_split', 'checker', 'frame']
        
        if style_mode == "Bauhaus (Curvas)":
            shape = random.choice(bauhaus)
        elif style_mode == "Memphis (Geo/Texture)":
            shape = random.choice(memphis)
        else:
            shape = random.choice(bauhaus + memphis)

        # FONDO
        draw.rectangle([x, y, x+s, y+s], fill=c_bg)

        # FORMAS
        if shape == 'quarter_leaf':
            draw.pieslice([x-s, y-s, x+s, y+s], 0, 90, fill=c_fg)
            draw.pieslice([x, y, x+s*2, y+s*2], 180, 270, fill=c_fg)

        elif shape == 'split_circle':
            pad = s * 0.1
            bbox = [x+pad, y+pad, x+s-pad, y+s-pad]
            draw.pieslice(bbox, 90, 270, fill=c_fg)
            draw.pieslice(bbox, 270, 450, fill=c_acc)

        elif shape == 'striped_circle':
            pad = s * 0.1
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=c_fg)
            lw = max(1, int(t/2))
            for ly in range(int(y+pad), int(y+s-pad), lw*3):
                draw.line([(x+pad, ly), (x+s-pad, ly)], fill=c_acc, width=lw)

        elif shape == 'eye':
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 0, 180, fill=c_fg)
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 180, 360, fill=c_fg)
            r = s * 0.15
            draw.ellipse([x+s/2-r, y+s/2-r, x+s/2+r, y+s/2+r], fill=c_acc)

        elif shape == 'arch':
            m = s * 0.2
            draw.rectangle([x+m, y+s/2, x+s-m, y+s], fill=c_fg)
            draw.pieslice([x+m, y+m, x+s-m, y+s-m + (s/2)], 180, 360, fill=c_fg)
        
        elif shape == 'circle_hollow':
             pad = s * 0.15
             draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], outline=c_fg, width=int(t))

        elif shape == 'corner_stairs':
            step_w = s / 4
            for i in range(4):
                self._safe_draw_rect(draw, x, y + (i*step_w), s - (i*step_w), step_w, c_fg)

        elif shape == 'diagonal_split':
            draw.polygon([(x, y+s), (x+s, y), (x+s, y+s)], fill=c_fg)
            if random.random() > 0.5:
                r = s * 0.2
                draw.ellipse([x+s/2-r, y+s/2-r, x+s/2+r, y+s/2+r], fill=c_acc)

        elif shape == 'grid_dots':
            cols = 3
            step = s / cols
            rad = step / 4
            for i in range(cols):
                for j in range(cols):
                    cx = x + (i * step) + step/2
                    cy = y + (j * step) + step/2
                    draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c_fg)

        elif shape == 'triangle_split':
            draw.polygon([(x,y), (x+s,y), (x,y+s)], fill=c_fg)
            draw.polygon([(x+s,y+s), (x+s,y), (x,y+s)], fill=c_acc)

        elif shape == 'checker':
            half = s // 2
            self._safe_draw_rect(draw, x, y, half, half, c_fg)
            self._safe_draw_rect(draw, x+half, y+half, s-half, s-half, c_fg)

        elif shape == 'frame':
            margin = int(t/2)
            draw.rectangle([x+margin, y+margin, x+s-margin, y+s-margin], outline=c_fg, width=int(t))

    def generate(self, palette, num_colors, thickness, grid, seed, style):
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        colors = self._get_colors(palette, num_colors, seed)
        cell_size = self.size // grid
        
        for i in range(grid):
            for j in range(grid):
                x = i * cell_size
                y = j * cell_size
                # Semilla única y caótica
                cell_seed = seed + (i * 9999) + (j * 7777)
                self._draw_element(draw, x, y, cell_size, colors, thickness, cell_seed, style)

        return image

# --- INTERFAZ DE USUARIO ---

st.title("⚡ Patrones Pro Studio")
st.caption("by nico.bastida | CHAOS EDITION")

# Estilos CSS para el botón gigante
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #111;
    color: #00FF00;
    font-size: 24px;
    font-weight: bold;
    border: 2px solid #00FF00;
    border-radius: 0px;
    height: 4em;
    width: 100%;
    text-transform: uppercase;
    transition: all 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: #00FF00;
    color: #111;
    box-shadow: 0 0 20px #00FF00;
}
</style>
""", unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.markdown("### 🎛️ Controles")
    
    # Selector de Paleta
    palette_choice = st.selectbox(
        "🎨 Paleta de Colores",
        list(PALETTES.keys()),
        index=0
    )
    
    # Controles físicos
    style_mode = st.selectbox("Estilo", ["Mix Complejo", "Bauhaus (Curvas)", "Memphis (Geo)"])
    
    if palette_choice != "1 Tinta (Blanco y Negro)":
        num_colors = st.slider("Cantidad de Colores", 2, 8, 4)
    else:
        num_colors = 2
        st.info("Modo B/N Activo")

    thickness = st.slider("Grosor", 5, 50, 15)
    complexity = st.select_slider("Resolución Grilla", options=[2, 4, 5, 6, 8, 10], value=6)
    
    st.markdown("---")
    
    # GESTIÓN DEL CAOS (SEMILLA OCULTA)
    # Inicializamos una semilla random en la sesión si no existe
    if 'chaos_seed' not in st.session_state:
        st.session_state.chaos_seed = random.randint(0, 999999)

    # BOTÓN GIGANTE
    if st.button("🎲 GENERAR NUEVO CAOS"):
        st.session_state.chaos_seed = random.randint(0, 999999)

with col_der:
    generator = ChaosGenerator(size=800)
    
    # Usamos la semilla de la sesión (oculta al usuario)
    img = generator.generate(
        palette=palette_choice,
        num_colors=num_colors,
        thickness=thickness,
        grid=complexity,
        seed=st.session_state.chaos_seed,
        style=style_mode
    )
    
    st.image(img, use_container_width=True)
    
    # Descarga
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="⬇️ DESCARGAR PNG",
        data=byte_im,
        file_name=f"patron_chaos_{st.session_state.chaos_seed}.png",
        mime="image/png"
    )
