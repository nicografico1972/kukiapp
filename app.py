import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Generador Geométrico Pro", layout="wide")

# --- PALETAS DE COLOR CURADAS (Armonía garantizada) ---
PALETAS = {
    "Clásica Portuguesa": ["#F2F2F2", "#1E4078", "#D9A404", "#8C2727"], # Blanco, Azul, Oro, Rojo oscuro
    "Bauhaus": ["#F2F2F2", "#111111", "#D92B2B", "#2B5CD9", "#F2C84B"], # Blanco, Negro, Primarios
    "Tierra & Oliva": ["#F0EAD6", "#556B2F", "#8B4513", "#DAA520", "#2F4F4F"],
    "Vibrante Geométrica": ["#111111", "#FF0055", "#00DDFF", "#FFEE00", "#FFFFFF"],
    "Monocromo Elegante": ["#FFFFFF", "#CCCCCC", "#666666", "#333333", "#000000"],
}

# --- MOTOR DE RENDERIZADO (El corazón del dibujo) ---

def dibujar_modulo(ax, x, y, tipo, rotacion, colores_celda):
    """
    Dibuja un módulo geométrico en la posición (x,y).
    NO dibuja estrellas. Dibuja piezas básicas que FORMAN estrellas al unirse.
    """
    # Fondo base de la celda
    bg_color = colores_celda[0]
    fg_color = colores_celda[1]
    acc_color = colores_celda[2] if len(colores_celda) > 2 else fg_color
    
    # Dibujar fondo
    ax.add_patch(patches.Rectangle((x, y), 1, 1, color=bg_color, zorder=1))
    
    # Centro de rotación
    cx, cy = x + 0.5, y + 0.5
    trans =  plt.matplotlib.transforms.Affine2D().rotate_deg_around(cx, cy, rotacion) + ax.transData

    # --- TIPOS DE MÓDULOS (Ladrillos de construcción) ---
    
    if tipo == 'diagonal_simple': 
        # Triángulo simple (mitad del cuadrado)
        poly = patches.Polygon([(x, y), (x+1, y+1), (x, y+1)], color=fg_color)
        poly.set_transform(trans)
        ax.add_patch(poly)

    elif tipo == 'diagonal_doble': 
        # Dos triángulos formando una flecha o punta
        # Base
        p1 = patches.Polygon([(x, y), (x+1, y), (x+0.5, y+0.5)], color=fg_color)
        # Punta opuesta
        p2 = patches.Polygon([(x, y+1), (x+1, y+1), (x+0.5, y+0.5)], color=acc_color)
        p1.set_transform(trans)
        p2.set_transform(trans)
        ax.add_patch(p1)
        ax.add_patch(p2)

    elif tipo == 'arco': 
        # Cuarto de círculo (Esencial para azulejo portugués)
        wedge = patches.Wedge((x, y), 1, 0, 90, color=fg_color)
        wedge.set_transform(trans)
        ax.add_patch(wedge)
        
    elif tipo == 'arco_doble':
        # Dos arcos opuestos (crea formas de hoja/ojo al juntarse)
        w1 = patches.Wedge((x, y), 1, 0, 90, color=fg_color)
        w2 = patches.Wedge((x+1, y+1), 1, 180, 270, color=acc_color)
        w1.set_transform(trans)
        w2.set_transform(trans)
        ax.add_patch(w1)
        ax.add_patch(w2)

    elif tipo == 'diamante_centro':
        # Rombo en el centro (o cuadrado girado)
        poly = patches.Polygon([(x+0.5, y), (x+1, y+0.5), (x+0.5, y+1), (x, y+0.5)], color=fg_color)
        # Si rotamos esto, sigue siendo un rombo, pero añade variedad si se combina
        # Añadimos un centro pequeño
        rect = patches.Rectangle((x+0.4, y+0.4), 0.2, 0.2, color=acc_color)
        ax.add_patch(poly)
        ax.add_patch(rect)

    elif tipo == 'rayas':
        # Geometría lineal
        r1 = patches.Rectangle((x, y), 0.33, 1, color=fg_color)
        r2 = patches.Rectangle((x+0.66, y), 0.33, 1, color=fg_color)
        r1.set_transform(trans)
        r2.set_transform(trans)
        ax.add_patch(r1)
        ax.add_patch(r2)

    elif tipo == 'cruz_suiza':
        # Cruz gruesa
        r1 = patches.Rectangle((x+0.33, y), 0.33, 1, color=fg_color)
        r2 = patches.Rectangle((x, y+0.33), 1, 0.33, color=fg_color)
        ax.add_patch(r1)
        ax.add_patch(r2)

# --- LÓGICA DE GENERACIÓN ---

def generar_semilla(tamano_semilla, paleta_actual):
    """Genera el bloque base (cuadrante superior izquierdo)"""
    semilla = []
    # Definimos pesos para que haya más formas curvas y diagonales (más rico)
    tipos_disponibles = ['diagonal_simple', 'diagonal_doble', 'arco', 'arco_doble', 'diamante_centro', 'rayas', 'cruz_suiza']
    pesos = [25, 20, 20, 15, 10, 5, 5] 
    
    for _ in range(tamano_semilla):
        fila = []
        for _ in range(tamano_semilla):
            tipo = random.choices(tipos_disponibles, weights=pesos, k=1)[0]
            rot = random.choice([0, 90, 180, 270])
            # Elegir 3 colores aleatorios de la paleta para esta celda
            cols = random.sample(paleta_actual, k=min(3, len(paleta_actual)))
            # Rellenar si faltan colores
            while len(cols) < 3: cols.append(cols[0])
            
            fila.append({'tipo': tipo, 'rot': rot, 'cols': cols})
        semilla.append(fila)
    return semilla

def aplicar_simetria_completa(semilla):
    """Crea el efecto 'Figura Completa' reflejando la semilla"""
    N_semilla = len(semilla)
    N_total = N_semilla * 2
    grid = [[None]*N_total for _ in range(N_total)]

    for r in range(N_semilla):
        for c in range(N_semilla):
            celda = semilla[r][c]
            
            # --- Lógica de Espejos ---
            # 1. Top-Left (Original)
            grid[r][c] = celda
            
            # 2. Top-Right (Reflejo Horizontal)
            # Al reflejar horizontalmente, la rotación cambia:
            # 0->90 (si es diagonal), o lógica de espejo visual.
            # Simplificación efectiva para patches: Flip geométrico = Cambio de rotación + Tipo
            # Para mantener la continuidad visual perfecta, simplemente rotamos "hacia adentro"
            
            # TRUCO PRO: Para hacer formas cerradas (estrellas centrales), rotamos alrededor del centro del mural
            c_tr = celda.copy()
            c_tr['rot'] = (celda['rot'] + 90) % 360 # Rotación simple para caleidoscopio
            grid[r][N_total - 1 - c] = c_tr # Esta posición es espejo, pero rotamos la pieza
            
            # Ajuste Fino para "Espejo Real" vs "Rotación":
            # Si queremos que las líneas se toquen, a veces es mejor reflejar la geometría.
            # Aquí usaremos ROTACIÓN CALEIDOSCÓPICA que garantiza simetría central (mandala)
            
            # Recalculamos usando lógica de mandala (rotar la semilla 4 veces)
            pass 

    # RE-HACEMOS LA LÓGICA MANDALA (Más robusta para "Figuras Completas")
    # Cuadrante 1: Semilla
    # Cuadrante 2: Semilla rotada 90 grados
    # Cuadrante 3: Semilla rotada 180 grados
    # Cuadrante 4: Semilla rotada 270 grados
    
    # Pero cuidado, para que conecten los bordes internos, hay que reflejar, no solo rotar.
    
    # 1. Top-Left: Semilla
    for r in range(N_semilla):
        for c in range(N_semilla):
            grid[r][c] = semilla[r][c]
    
    # 2. Top-Right: Espejo Horizontal de Top-Left
    for r in range(N_semilla):
        for c in range(N_semilla):
            orig = grid[r][c]
            nuevo = orig.copy()
            # Ajuste de rotación para efecto espejo horizontal
            if orig['tipo'] in ['diagonal_simple', 'arco']:
                 if orig['rot'] == 0: nuevo['rot'] = 90
                 elif orig['rot'] == 90: nuevo['rot'] = 0
                 elif orig['rot'] == 180: nuevo['rot'] = 270
                 elif orig['rot'] == 270: nuevo['rot'] = 180
            elif orig['tipo'] == 'diagonal_doble':
                 if orig['rot'] == 0: nuevo['rot'] = 270 # Ajuste visual
                 # ... simplificamos:
                 nuevo['rot'] = (orig['rot'] + 90) % 360 # Fallback
            
            grid[r][N_total - 1 - c] = nuevo

    # 3. Bottom: Espejo Vertical de Top
    for r in range(N_semilla):
        for c in range(N_total):
            orig = grid[r][c]
            nuevo = orig.copy()
            # Ajuste rotación vertical
            if orig['tipo'] in ['diagonal_simple', 'arco']:
                if orig['rot'] == 0: nuevo['rot'] = 270
                elif orig['rot'] == 90: nuevo['rot'] = 180
                elif orig['rot'] == 180: nuevo['rot'] = 90
                elif orig['rot'] == 270: nuevo['rot'] = 0
            
            grid[N_total - 1 - r][c] = nuevo
            
    return grid

def generar_abstraccion(tamano, paleta):
    """Genera un patrón sin centro único, pero con ritmo armónico"""
    grid = [[None]*tamano for _ in range(tamano)]
    
    # Elegir 2 o 3 módulos "tema" para que no sea un caos
    temas = random.sample(['arco', 'diagonal_doble', 'diagonal_simple', 'rayas'], k=2)
    
    for r in range(tamano):
        for c in range(tamano):
            tipo = random.choice(temas)
            # Rotación: A veces aleatoria, a veces basada en paridad (tablero de ajedrez) para dar orden
            if random.random() > 0.3:
                rot = ((r + c) % 2) * 90 # Orden latente
            else:
                rot = random.choice([0, 90, 180, 270]) # Variación
            
            cols = random.sample(paleta, k=2)
            cols.append(cols[0])
            grid[r][c] = {'tipo': tipo, 'rot': rot, 'cols': cols}
            
    return grid

# --- INTERFAZ UI ---

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Control Creativo")
    modo = st.radio("Modo de Diseño", ["Gran Figura (Mandala)", "Abstracción Armónica"])
    
    paleta_nombre = st.selectbox("Paleta de Color", list(PALETAS.keys()))
    paleta_actual = PALETAS[paleta_nombre]
    
    tamano = st.slider("Complejidad (Tamaño Grid)", 4, 16, 8, step=2)
    
    if "seed" not in st.session_state: st.session_state.seed = 0
    
    if st.button("🎲 GENERAR NUEVO DISEÑO", type="primary"):
        st.session_state.seed += 1

with col2:
    # Generar datos
    random.seed(st.session_state.seed)
    
    if modo == "Gran Figura (Mandala)":
        semilla = generar_semilla(tamano // 2, paleta_actual)
        grid_final = aplicar_simetria_completa(semilla)
        titulo = "Composición Simétrica Central"
    else:
        grid_final = generar_abstraccion(tamano, paleta_actual)
        titulo = "Abstracción Modular Rítmica"

    # DIBUJAR
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    
    N = len(grid_final)
    # Fondo del lienzo
    fig.patch.set_facecolor('#222222')
    ax.add_patch(patches.Rectangle((0, 0), N, N, color=paleta_actual[0])) # Fondo base

    for r in range(N):
        for c in range(N):
            celda = grid_final[r][c]
            # Invertimos Y para dibujar de arriba a abajo
            dibujar_modulo(ax, c, N-1-r, celda['tipo'], celda['rot'], celda['cols'])
    
    # Líneas de rejilla sutiles
    for i in range(N+1):
        ax.plot([0, N], [i, i], color='black', linewidth=0.5, alpha=0.3)
        ax.plot([i, i], [0, N], color='black', linewidth=0.5, alpha=0.3)
        
    # Marco exterior
    ax.plot([0, N, N, 0, 0], [0, 0, N, N, 0], color='black', linewidth=5)

    st.pyplot(fig)
    
    st.caption(f"🎨 {titulo} | Paleta: {paleta_nombre}")
