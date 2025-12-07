import streamlit as st
import random
import math
from PIL import Image, ImageDraw

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Patrones Pro Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CLASE GENERADORA (Fusión V4 Features + V5 Stability) ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta completa
        self.base_palette = [
            "#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557",
            "#2A9D8F", "#E9C46A", "#F4A261", "#264653", "#000000",
            "#D62828", "#FCBF49", "#003049", "#F77F00", "#FFFFFF"
        ]

    def _get_colors(self, n, seed, bw_mode=False):
        """Gestión de colores a prueba de fallos (V5 Logic)"""
        if bw_mode:
            return ["#FFFFFF", "#000000"]
        random.seed(seed)
        # Seleccionamos colores y si faltan, duplicamos para evitar crash
        palette = random.sample(self.base_palette, min(n, len(self.base_palette)))
        while len(palette) < 3:
            palette.append(random.choice(palette))
        return palette

    def _safe_draw_rect(self, draw, x, y, w, h, color):
        """Helper para evitar coordenadas inválidas"""
        if w <= 0 or h <= 0: return
        draw.rectangle([x, y, x+w, y+h], fill=color)

    def _draw_styled_cell(self, draw, x, y, s, colors, thickness, seed, style_mode):
        random.seed(seed)
        
        # Preparar colores (Shuffle local)
        bg = colors[0]
        fg = colors[1] if len(colors) > 1 else bg
        accent = colors[2] if len(colors) > 2 else fg
        local_colors = [bg, fg, accent]
        random.shuffle(local_colors)
        c1, c2, c3 = local_colors

        # Grosor seguro
        t = max(1, min(thickness, int(s * 0.25)))

        # --- DEFINICIÓN DE POOLS DE FORMAS SEGÚN ESTILO ---
        bauhaus_shapes = ['quarter_leaf', 'split_circle', 'striped_circle', 'eye', 'arch', 'circle_hollow']
        memphis_shapes = ['corner_stairs', 'diagonal_split', 'grid_dots', 'triangle_split', 'checker', 'frame']
        
        if style_mode == "Bauhaus (Curvas)":
            shape_type = random.choice(bauhaus_shapes)
        elif style_mode == "Memphis (Geo/Texture)":
            shape_type = random.choice(memphis_shapes)
        else: # Mix Complejo
            shape_type = random.choice(bauhaus_shapes + memphis_shapes)

        # 1. FONDO
        draw.rectangle([x, y, x+s, y+s], fill=c1)

        # 2. DIBUJO DE LA FORMA (Lógica V5 aplicada a formas V4)
        
        # --- FORMAS CURVAS (BAUHAUS) ---
        if shape_type == 'quarter_leaf':
            draw.pieslice([x-s, y-s, x+s, y+s], 0, 90, fill=c2)
            draw.pieslice([x, y, x+s*2, y+s*2], 180, 270, fill=c2)

        elif shape_type == 'split_circle':
            pad = s * 0.1
            bbox = [x+pad, y+pad, x+s-pad, y+s-pad]
            draw.pieslice(bbox, 90, 270, fill=c2)
            draw.pieslice(bbox, 270, 450, fill=c3)

        elif shape_type == 'striped_circle':
            pad = s * 0.1
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=c2)
            line_w = max(1, int(t/2))
            for ly in range(int(y+pad), int(y+s-pad), line_w*3):
                draw.line([(x+pad, ly), (x+s-pad, ly)], fill=c3, width=line_w)

        elif shape_type == 'eye':
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 0, 180, fill=c2)
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 180, 360, fill=c2)
            r = s * 0.15
            draw.ellipse([x+s/2-r, y+s/2-r, x+s/2+r, y+s/2+r], fill=c3)

        elif shape_type == 'arch':
            margin = s * 0.2
            draw.rectangle([x+margin, y+s/2, x+s-margin, y+s], fill=c2)
            draw.pieslice([x+margin, y+margin, x+s-margin, y+s-margin + (s/2)], 180, 360, fill=c2)
        
        elif shape_type == 'circle_hollow':
             pad = s * 0.15
             draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], outline=c2, width=int(t))

        # --- FORMAS RECTAS (MEMPHIS) ---
        elif shape_type == 'corner_stairs':
            step_w = s / 4
            for i in range(4):
                self._safe_draw_rect(draw, x, y + (i*step_w), s - (i*step_w), step_w, c2)

        elif shape_type == 'diagonal_split':
            draw.polygon([(x, y+s), (x+s, y), (x+s, y+s)], fill=c2)
            # Decoración extra
            if random.choice([True, False]):
                r = s * 0.2
                draw.ellipse([x+s/2-r, y+s/2-r, x+s/2+r, y+s/2+r], fill=c3)

        elif shape_type == 'grid_dots':
            cols = 3
            step = s / cols
            rad = step / 4
            for i in range(cols):
                for j in range(cols):
                    cx = x + (i * step) + step/2
                    cy = y + (j * step) + step/2
                    draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c2)

        elif shape_type == 'triangle_split':
            draw.polygon([(x,y), (x+s,y), (x,y+s)], fill=c2)
            draw.polygon([(x+s,y+s), (x+s,y), (x,y+s)], fill=c3)

        elif shape_type == 'checker':
            half = s // 2
            self._safe_draw_rect(draw, x, y, half, half, c2)
            self._safe_draw_rect(draw, x+half, y+half, s-half, s-half, c2)

        elif shape_type == 'frame':
            margin = int(t/2)
            draw.rectangle([x+margin, y+margin, x+s-margin, y+s-margin], outline=c2, width=int(t))

        # 3. OVERLAY OPCIONAL (Profundidad)
        if random.random() > 0.7:
             draw.rectangle([x, y, x+s, y+s], outline=c3, width=max(1, int(t/4)))

    def generate(self, num_colors, thickness, grid_divisions, seed, bw_mode, style_mode):
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        colors = self._get_colors(num_colors, seed, bw_mode)
        cell_size = self.size // grid_divisions
        
        # Generación Celda a Celda (Como V5, para evitar efecto espejo simple)
        for i in range(grid_divisions):
            for j in range(grid_divisions):
                x = i * cell_size
                y = j * cell_size
                cell_seed = seed + (i * 999) + (j * 777)
                
                # Pasamos el style_mode a la celda
                self._draw_styled_cell(draw, x, y, cell_size, colors, thickness, cell_seed, style_mode)

        return image

# --- INTERFAZ STREAMLIT ---

st.title("Patrones Pro Studio")
st.markdown("**by nico.bastida** | *V6.0 Final Hybrid Edition*")
st.markdown("---")

# Estilos CSS para botón
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #E63946;
    color: white;
    font-size: 20px;
    border-radius: 8px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

col_control, col_canvas = st.columns([1, 2])

with col_control:
    st.header("🎛️ Centro de Mando")
    
    # --- ¡AQUÍ ESTÁ EL SELECTOR QUE QUERÍAS! ---
    style_mode = st.selectbox(
        "Estilo de Diseño",
        ["Mix Complejo", "Bauhaus (Curvas)", "Memphis (Geo/Texture)"],
        index=0,
        help="Elige 'Bauhaus' para círculos y arcos, o 'Memphis' para geometría y patrones."
    )
    
    bw_mode = st.checkbox("Modo 1 Tinta (B/N)", value=False)
    
    seed_val = st.number_input("Semilla (Seed)", value=2024, step=1)
    
    if not bw_mode:
        num_colors = st.slider("Colores", 2, 8, 4)
    else:
        num_colors = 2
        st.info("Modo Blanco y Negro activo.")

    thickness = st.slider("Grosor Elementos", 5, 40, 15)
    complexity = st.select_slider("Resolución Grilla", options=[2, 4, 5, 6, 8, 10], value=6)
    
    st.markdown("###")
    if st.button("🎲 GENERAR DISEÑO"):
        seed_val = random.randint(0, 99999)

# GENERACIÓN SEGURA
generator = PatternGenerator(size=800)

try:
    with col_canvas:
        with st.spinner("Procesando geometría..."):
            img = generator.generate(
                num_colors=num_colors, 
                thickness=thickness, 
                grid_divisions=complexity, 
                seed=seed_val,
                bw_mode=bw_mode,
                style_mode=style_mode # Pasamos el estilo seleccionado
            )
            
            st.image(img, caption=f"Estilo: {style_mode} | Seed: {seed_val}", use_container_width=True)
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="⬇️ DESCARGAR PNG",
                data=byte_im,
                file_name=f"patron_{style_mode.split()[0]}_{seed_val}.png",
                mime="image/png"
            )

except Exception as e:
    st.error("⚠️ Error Inesperado")
    st.code(e)
    st.info("Intenta cambiar la Semilla para probar otra combinación.")

import io
