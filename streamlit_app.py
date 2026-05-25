import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configuración de la página optimizada para dispositivos móviles y escritorio
st.set_page_config(
    page_title="Calculadora LDM",
    page_icon="🚚",
    layout="centered"
)

# Constantes logísticas
MAX_PESO = 25780
LARGO_MAX_CAMION = 1360  # cm

def calcular_precio(zona, peso):
    if peso == 0 or zona == "Seleccionar Tarifa..." or not zona:
        return 0.0
    toneladas = peso / 1000.0
    
    if zona == "Alicante":
        if peso <= 4000: return 150.0
        elif peso <= 7500: return toneladas * 33.0
        elif peso <= 14000: return toneladas * 30.0
        elif peso <= 21000: return toneladas * 27.0
        else: return toneladas * 24.0
            
    elif zona == "Murcia":
        if peso <= 4000: return 180.0
        elif peso <= 7500: return toneladas * 35.0
        elif peso <= 14000: return toneladas * 32.0
        elif peso <= 21000: return toneladas * 30.0
        else: return toneladas * 28.0

    elif zona == "Valencia":
        if peso <= 5500: return 120.0
        elif peso <= 12000: return toneladas * 21.0
        elif peso <= 18000: return toneladas * 18.0
        elif peso <= 24000: return 360.0
        else: return toneladas * 24.0
        
    return 0.0

st.title("🚚 Calculadora Logística Comercial")
st.write("Planificación de plano de carga, cubicaje y tarifas.")

# --- SECCIÓN DE ENTRADA DE DATOS PRINCIPAL ---
st.subheader("1. Datos de la Carga (Palets)")
st.caption("Modifica la tabla. Puedes añadir filas al final presionando el botón '+' de la tabla.")

# DataFrame inicial vacío con la estructura correcta
df_inicial = pd.DataFrame(
    [[1, 120, 80, 0, 0]], 
    columns=["Cantidad", "Largo (cm)", "Ancho (cm)", "Peso/Palet (kg)", "Peso Total (kg)"]
)

# Editor de datos interactivo adaptado a móvil
edited_df = st.data_editor(
    df_inicial,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Cantidad": st.column_config.NumberColumn(min_value=0, step=1, default=1),
        "Largo (cm)": st.column_config.NumberColumn(min_value=0, step=1, default=120),
        "Ancho (cm)": st.column_config.NumberColumn(min_value=0, step=1, default=80),
        "Peso/Palet (kg)": st.column_config.NumberColumn(min_value=0, step=1, default=0),
        "Peso Total (kg)": st.column_config.NumberColumn(min_value=0, step=1, default=0),
    }
)

# --- SECCIÓN EXCLUSIVA DE CAJONES ---
st.subheader("2. Fila Especial: Cajones")
col_cj1, col_cj2, col_cj3, col_cj4, col_cj5 = st.columns(5)
with col_cj1: cj_cant = st.number_input("Cant. CJ", min_value=0, step=1, value=0)
with col_cj2: cj_largo = st.number_input("Largo CJ", min_value=0.0, step=5.0, value=0.0)
with col_cj3: cj_ancho = st.number_input("Ancho CJ", min_value=0.0, step=5.0, value=0.0)
with col_cj4: cj_peso_u = st.number_input("Peso/CJ", min_value=0.0, step=10.0, value=0.0)
with col_cj5: cj_peso_t = st.number_input("P. Tot CJ", min_value=0.0, step=10.0, value=0.0)

# --- CONTROLES DE DESTINO Y GASOIL ---
st.subheader("3. Parámetros Comerciales")
col_com1, col_com2 = st.columns(2)
with col_com1:
    zona_seleccionada = st.selectbox("Destino / Tarifa", ["Seleccionar Tarifa...", "Alicante", "Murcia", "Valencia"])
with col_com2:
    gasoil_porcentaje = st.number_input("Variación Gasoil (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

# --- PROCESAMIENTO Y CÁLCULOS LOGÍSTICOS ---
grand_total_ldm = 0.0
grand_total_palets = 0
grand_total_peso_real = 0.0
items_a_colocar = []
ancho_advertencia = False

# Procesar filas del editor
for idx, row in edited_df.iterrows():
    try:
        cant = int(row["Cantidad"])
        largo = float(row["Largo (cm)"])
        ancho = float(row["Ancho (cm)"])
        peso_u = float(row["Peso/Palet (kg)"])
        peso_t = float(row["Peso Total (kg)"])
        
        if cant <= 0 or largo <= 0 or ancho <= 0:
            continue
            
        if ancho > 120:
            ancho_advertencia = True
            
        if peso_t > 0:
            grand_total_peso_real += peso_t
        else:
            grand_total_peso_real += (cant * peso_u)
            
        # Cálculo de LDM estándar
        palets_ancho = int(240 // ancho)
        row_ldm = ((largo / 100.0) / palets_ancho if palets_ancho > 0 else (largo / 100.0)) * cant
        grand_total_ldm += row_ldm
        grand_total_palets += cant
        
        # Preparar para el plano de carga
        cap_A = max(1, int(240 // ancho))
        len_A = ((cant + cap_A - 1) // cap_A) * largo
        cap_B = max(1, int(240 // largo))
        len_B = ((cant + cap_B - 1) // cap_B) * ancho
        w_elegido, h_elegido = (ancho, largo) if len_B < len_A else (largo, ancho)
        
        for _ in range(cant):
            items_a_colocar.append({"largo": w_elegido, "ancho": h_elegido, "text": f"F{idx+1}", "es_cajon": False})
    except:
        pass

if ancho_advertencia:
    st.warning("⚠️ ¡Detectadas medidas superiores a 120cm de ancho en palets estándar! Recuerda usar la fila de Cajones si corresponde.")

# Procesar Cajones
if cj_cant > 0 and cj_largo > 0 and cj_ancho > 0:
    if cj_peso_t > 0:
        grand_total_peso_real += cj_peso_t
    else:
        grand_total_peso_real += (cj_cant * cj_peso_u)
        
    if (240 - cj_ancho) < 80:
        cap_filas = int(240 // cj_ancho)
        cj_ldm = ((cj_largo / 100.0) / cap_filas if cap_filas > 0 else (cj_largo / 100.0)) * cj_cant
    else:
        cj_ldm = ((cj_largo * cj_ancho) / 24000.0) * cj_cant
        
    grand_total_ldm += cj_ldm
    grand_total_palets += cj_cant
    
    for _ in range(cj_cant):
        items_a_colocar.append({"largo": cj_largo, "ancho": cj_ancho, "text": "CJ", "es_cajon": True})

# Peso volumétrico
grand_total_peso_vol = grand_total_ldm * 2000

# Precios base
precio_real = calcular_precio(zona_seleccionada, grand_total_peso_real)
precio_vol = calcular_precio(zona_seleccionada, grand_total_peso_vol)
precio_base_maximo = max(precio_real, precio_vol)

# Gasoil e Importe Final
importe_gasoil = precio_base_maximo * (gasoil_porcentaje / 100.0)
total_comercial = precio_base_maximo + importe_gasoil

# --- RENDERIZADO DE RESULTADOS ---
st.subheader("4. Resumen de Totales")

metric1, metric2 = st.columns(2)
metric1.metric("Total Bultos", f"{grand_total_palets} palets")
metric2.metric("Total LDM", f"{grand_total_ldm:.2f} m")

# Alertas visuales de sobrepeso
col_p1, col_p2 = st.columns(2)
with col_p1:
    if grand_total_peso_real > MAX_PESO:
        st.error(f"Peso Real: {grand_total_peso_real:,.0f} kg 🚨 Excede límite")
    else:
        st.success(f"Peso Real: {grand_total_peso_real:,.0f} kg")
with col_p2:
    if grand_total_peso_vol > MAX_PESO:
        st.error(f"Peso Volumétrico: {grand_total_peso_vol:,.0f} kg 🚨 Excede límite")
    else:
        st.info(f"Peso Volumétrico: {grand_total_peso_vol:,.0f} kg")

# Cuadro de Precios Comerciales
st.markdown("---")
col_pre1, col_pre2 = st.columns(2)
col_pre1.write(f"**Precio por Peso Real:** {precio_real:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
col_pre2.write(f"**Precio por Volumen (LDM):** {precio_vol:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown(f"**Importe Variación Gasoil:** {importe_gasoil:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

# Destacar la tarifa aplicada (la mayor) imitando el parpadeo original
clase_precio = "🔥" if precio_real != precio_vol and precio_base_maximo > 0 else "💰"
st.success(f"### {clase_precio} TOTAL COMERCIAL (+ GASOIL): {total_comercial:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

# --- PLANO DE CARGA (MATPLOTLIB) ---
st.subheader("5. Distribución en Semirremolque (Vista Superior)")

if items_a_colocar:
    items_a_colocar.sort(key=lambda x: (x["largo"], x["ancho"]), reverse=True)
    placed_rects = []
    carga_superada = False
    
    for item in items_a_colocar:
        w = item["largo"]
        h = item["ancho"]
        best_x, best_y = None, None
        min_score = float('inf')
        
        puntos_evaluacion = [(0.0, 0.0)]
        for rx1, ry1, rx2, ry2, _ in placed_rects:
            puntos_evaluacion.extend([(rx2, ry1), (rx1, ry2), (rx2, ry2)])
        puntos_evaluacion = sorted(list(set(puntos_evaluacion)), key=lambda p: (p[0], p[1]))
        
        for px, py in puntos_evaluacion:
            if py + h <= 240.0:
                solapa = False
                for rx1, ry1, rx2, ry2, _ in placed_rects:
                    if not (px + w <= rx1 or px >= rx2 or py + h <= ry1 or py >= ry2):
                        solapa = True
                        break
                if not solapa:
                    score = px + w
                    if score < min_score:
                        min_score = score
                        best_x, best_y = px, py
                    break
        
        if best_x is None:
            best_x = max([r[2] for r in placed_rects]) if placed_rects else 0.0
            best_y = 0.0
            
        placed_rects.append((best_x, best_y, best_x + w, best_y + h, item))
        if (best_x + w) > LARGO_MAX_CAMION:
            carga_superada = True

    # Dibujar plano con Matplotlib
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.set_xlim(-80, LARGO_MAX_CAMION + 80)
    ax.set_ylim(-20, 260)
    ax.axis('off')
    
    # Contenedor del camión
    ax.add_patch(patches.Rectangle((0, 0), LARGO_MAX_CAMION, 240, edgecolor='#334155', facecolor='#f1f5f9', lw=2))
    ax.text(-40, 120, "FRONTAL\n(Cabina)", va='center', ha='center', fontsize=8, color='#64748b', weight='bold')
    ax.text(LARGO_MAX_CAMION + 40, 120, "TRASERA\n(Puertas)", va='center', ha='center', fontsize=8, color='#64748b', weight='bold')
    
    colores = ["#93c5fd", "#a7f3d0", "#fde68a", "#fca5a5", "#c084fc", "#fed7aa", "#fef08a", "#bfdbfe", "#bbf7d0"]
    
    for rx1, ry1, rx2, ry2, item in placed_rects:
        w_box = rx2 - rx1
        h_box = ry2 - ry1
        color_idx = hash(item["text"]) % len(colores)
        color = "#cbd5e1" if item["es_cajon"] else colores[color_idx]
        
        ax.add_patch(patches.Rectangle((rx1, ry1), w_box, h_box, edgecolor='#1e293b', facecolor=color, lw=0.8))
        
        if item["es_cajon"]:
            ax.plot([rx1, rx2], [ry1, ry2], color="#94a3b8", linestyle="--", lw=0.5)
            ax.plot([rx1, rx2], [ry2, ry1], color="#94a3b8", linestyle="--", lw=0.5)
            
        if w_box >= 30 and h_box >= 20:
            ax.text(rx1 + w_box/2, ry1 + h_box/2, item["text"], va='center', ha='center', fontsize=6, weight='bold', color='#0f172a')

    st.pyplot(fig)
    
    if carga_superada:
        st.error("🚨 ¡ALERTA! La distribución geométrica excede los 13.6 metros reales del semirremolque.")
else:
    st.info("Introduce datos en la tabla para simular el plano de carga.")
