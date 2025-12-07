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

# --- CLASE GENERADORA MAESTRA (V5 - STABLE) ---
class PatternGenerator:
    def __init__(self, size=800):
        self.size = size
        # Paleta Neo-Geo / Bauhaus expandida
        self.base_palette = [
            "#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557",
            "#2A9D8F", "#E9C46A", "#F4A261", "#264653", "#000000",
            "#D62828", "#FCBF49", "#003049", "#F77F00", "#FFFFFF"
        ]

    def _get_colors(self, n, seed, bw_mode=False):
        """Gestión segura de paletas."""
        if bw_mode:
            return ["#FFFFFF", "#000000"]
        random.seed(seed)
        # Aseguramos que siempre haya suficientes colores para evitar errores de índice
        palette = random.sample(self.base_palette, min(n, len(self.base_palette)))
        # Si la paleta es muy corta, duplicamos colores para evitar crashes
        while len(palette) < 3:
            palette.append(random.choice(palette))
        return palette

    def _safe_draw_rect(self, draw, x, y, w, h, color, fill=True):
        """Helper para evitar coordenadas negativas."""
        if w <= 0 or h <= 0: return
        if fill:
            draw.rectangle([x, y, x+w, y+h], fill=color)
        else:
            draw.rectangle([x, y, x+w, y+h], outline=color)

    def _draw_bauhaus_element(self, draw, x, y, s, colors, thickness, seed):
        """
        Motor gráfico inspirado en tus referencias (Círculos cortados, Rayas, Formas compuestas).
        """
        random.seed(seed)
        
        # 1. Selección de colores segura (evita el error 'empty sequence')
        bg = colors[0]
        fg = colors[1] if len(colors) > 1 else bg
        accent = colors[2] if len(colors) > 2 else fg
        
        # Barajamos localmente para variedad
        local_palette = [bg, fg, accent]
        random.shuffle(local_palette)
        c1, c2, c3 = local_palette

        # Grosor seguro: nunca mayor que 1/4 de la celda
        t = max(1, min(thickness, int(s * 0.25)))
        
        # FONDO BASE
        draw.rectangle([x, y, x+s, y+s], fill=c1)

        # CATÁLOGO DE FORMAS (Basado en tus imágenes)
        shape_type = random.choice([
            'quarter_leaf', 'split_circle', 'striped_circle', 
            'diagonal_split', 'eye', 'arch', 'grid_dots', 'corner_stairs'
        ])

        # --- DIBUJO DE FORMAS ---
        
        if shape_type == 'quarter_leaf':
            # Forma de hoja (dos cuartos de círculo opuestos)
            draw.pieslice([x-s, y-s, x+s, y+s], 0, 90, fill=c2)
            draw.pieslice([x, y, x+s*2, y+s*2], 180, 270, fill=c2)

        elif shape_type == 'split_circle':
            # Círculo partido en dos colores
            pad = s * 0.1
            bbox = [x+pad, y+pad, x+s-pad, y+s-pad]
            draw.pieslice(bbox, 90, 270, fill=c2)
            draw.pieslice(bbox, 270, 450, fill=c3)

        elif shape_type == 'striped_circle':
            # Círculo con rayas
            pad = s * 0.1
            # Dibujamos círculo base
            draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], fill=c2)
            # Superponemos rayas recortadas (simulado dibujando líneas dentro del box)
            # Para simplificar en PIL sin máscaras complejas, dibujamos líneas horizontales encima
            # Solo si el contraste es bueno
            line_w = max(1, int(t/2))
            for ly in range(int(y+pad), int(y+s-pad), line_w*3):
                # Cálculo simple de cuerda de círculo para no salirnos demasiado (estético)
                draw.line([(x+pad, ly), (x+s-pad, ly)], fill=c3, width=line_w)

        elif shape_type == 'diagonal_split':
            # Triángulo diagonal con círculo superpuesto
            draw.polygon([(x, y+s), (x+s, y), (x+s, y+s)], fill=c2)
            # Círculo pequeño en el centro
            r = s * 0.2
            cx, cy = x + s/2, y + s/2
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c3)

        elif shape_type == 'eye':
            # Ojo (Almendra)
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 0, 180, fill=c2)
            draw.pieslice([x-s/2, y, x+s*1.5, y+s], 180, 360, fill=c2)
            # Pupila
            r = s * 0.15
            draw.ellipse([x+s/2-r, y+s/2-r, x+s/2+r, y+s/2+r], fill=c3)

        elif shape_type == 'arch':
            # Arco estilo puerta
            margin = s * 0.2
            draw.rectangle([x+margin, y+s/2, x+s-margin, y+s], fill=c2)
            draw.pieslice([x+margin, y+margin, x+s-margin, y+s-margin + (s/2)], 180, 360, fill=c2)

        elif shape_type == 'grid_dots':
            # Rejilla de puntos (Textura Memphis)
            cols = 3
            step = s / cols
            rad = step / 4
            for i in range(cols):
                for j in range(cols):
                    cx = x + (i * step) + step/2
                    cy = y + (j * step) + step/2
                    draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c2)

        elif shape_type == 'corner_stairs':
            # Escaleras en esquina
            step_w = s / 4
            for i in range(4):
                # Rectángulos decrecientes
                self._safe_draw_rect(draw, x, y + (i*step_w), s - (i*step_w), step_w, c2)

        # 2. OVERLAY / MARCO (Opcional, añade profundidad)
        if random.random() > 0.6:
            if random.choice([True, False]):
                # Marco simple
                draw.rectangle([x, y, x+s, y+s], outline=c3, width=int(t/2))
            else:
                # Círculo hueco (Anillo)
                pad = s * 0.05
                draw.ellipse([x+pad, y+pad, x+s-pad, y+s-pad], outline=c3, width=int(t/2))

    def generate(self, num_colors, thickness, grid_divisions, seed, bw_mode):
        # Lienzo
        image = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(image)
        
        colors = self._get_colors(num_colors, seed, bw_mode)
        cell_size = self.size // grid_divisions
        
        # Generación Estilo "Mosaico Real" 
        # (En lugar de espejar 1 cuadrante, generamos cada celda individualmente 
        # pero con coherencia para lograr el efecto de tus referencias de "Grid de Iconos")
        
        for i in range(grid_divisions):
            for j in range(grid_divisions):
                x = i * cell_size
                y = j * cell_size
                
                # Semilla determinista por celda
                cell_seed = seed + (i * 999) + (j * 777)
                
                self._draw_bauhaus_element(draw, x, y, cell_size, colors, thickness, cell_seed)

        return image

# --- INTERFAZ DE USUARIO ---

st.title("Patrones Pro Studio")
st.markdown("**by nico.bastida** | *V5.0 Stable Edition*")

st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #E63946;
    color: white;
    font-size: 20px;
    border-radius: 10px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")

col_control, col_canvas = st.columns([1, 2])

with col_control:
    st.subheader("🎛️ Controles")
    
    bw_mode = st.checkbox("Modo B/N (1 Tinta)", value=False)
    
    seed_val = st.number_input("Semilla", value=101, step=1)
    
    if not bw_mode:
        num_colors = st.slider("Colores", 2, 8, 4)
    else:
        num_colors = 2
        st.info("Modo Blanco y Negro activo.")
        
    thickness = st.slider("Grosor", 5, 40, 15)
    complexity = st.slider("Resolución Grilla", 2, 12, 6)
    
    st.markdown("###")
    if st.button("🎲 GENERAR DISEÑO"):
        seed_val = random.randint(0, 9999)

# LÓGICA DE GENERACIÓN BLINDADA
generator = PatternGenerator(size=800)

try:
    with col_canvas:
        with st.spinner("Diseñando geometría..."):
            img = generator.generate(
                num_colors=num_colors, 
                thickness=thickness, 
                grid_divisions=complexity, 
                seed=seed_val,
                bw_mode=bw_mode
            )
            
            st.image(img, caption=f"Diseño Geométrico #{seed_val}", use_container_width=True)
            
            # Botón de descarga
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="⬇️ DESCARGAR PNG (800x800)",
                data=byte_im,
                file_name=f"patron_pro_v5_{seed_val}.png",
                mime="image/png"
            )

except Exception as e:
    st.error("⚠️ Error Inesperado")
    st.warning(f"Detalle técnico: {e}")
    st.info("Intenta cambiar la 'Semilla' o reducir ligeramente el 'Grosor'.")

import io # Aseguramos que io esté importado al final por si acaso
