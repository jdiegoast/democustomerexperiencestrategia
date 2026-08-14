import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime
import json
import os
import unicodedata
import base64

# ==========================================
# 1. CONFIGURACIÓN E INTERFAZ DE USUARIO
# ==========================================
st.set_page_config(
    page_title="Dashboard Mystery Shopper Demo",
    page_icon="🛒",
    layout="wide"
)

if 'tienda_seleccionada' not in st.session_state: st.session_state.tienda_seleccionada = None
if 'sector_seleccionado' not in st.session_state: st.session_state.sector_seleccionado = None
if 'depto_seleccionado' not in st.session_state: st.session_state.depto_seleccionado = None

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .footer-custom { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0e1117; color: #A0A0A0; text-align: center; padding: 8px 10px; font-size: 13px; font-weight: bold; z-index: 1000; border-top: 1px solid #262730; display: flex; justify-content: center; align-items: center; gap: 10px;}
    .sticky-header { position: sticky; top: 0; background-color: #0e1117; z-index: 999; padding: 10px 0px; border-bottom: 3px solid #0A1B3F; }
    .journey-container { display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: -10px; margin-top: 5px; }
    .j-step, .c-step { flex: 1; color: #1A252C; padding: 10px 0px; text-align: center; font-size: 13px; font-weight: 800; margin-right: 4px; }
    
    /* Dinámica de Colores para Pasos Extendidos */
    .j-1, .c-1 { background-color: #D5DBDB; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%); }
    .j-2, .c-2 { background-color: #F5B7B1; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-3, .c-3 { background-color: #AED6F1; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-4, .c-4 { background-color: #A9DFBF; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-5, .c-5 { background-color: #F9E79F; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-6, .c-6 { background-color: #F5CBA7; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-7, .c-7 { background-color: #D2B4DE; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-8, .c-8 { background-color: #85C1E9; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-9, .c-9 { background-color: #F1948A; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-10, .c-10 { background-color: #82E0AA; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    .j-11, .c-11 { background-color: #F7DC6F; clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%); }
    </style>
""", unsafe_allow_html=True)

# --- LOGO FIRMA BASE64 ---
def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_strat_b64 = get_base64_img("logo_strategia.png") or get_base64_img("logo_strategia.jpg")
img_tag = f'<img src="data:image/png;base64,{logo_strat_b64}" style="height: 20px; vertical-align: middle;">' if logo_strat_b64 else ''

st.markdown(f'<div class="footer-custom">Powered by stratēgia {img_tag} | Inteligencia de Negocios</div>', unsafe_allow_html=True)

# --- ENCABEZADO PRINCIPAL ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo: 
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("**(🛒 Demo Logo)**")
        
with col_titulo: 
    st.markdown("<h1 style='margin-bottom: 0px;'>Dashboard Estratégico CX+</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: -10px; color: #888888;'>Plataforma Demo by stratēgia</h3>", unsafe_allow_html=True)

# ==========================================
# 2. CARGA DE DATOS LOCALES (DEMO)
# ==========================================
def normalizar_cadena(texto):
    s = str(texto).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

@st.cache_data(ttl=3600)
def cargar_geojson_local():
    ruta = "guatemala.geojson"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            geo = json.load(f)
            for feature in geo['features']:
                props = feature.get('properties', {})
                nom = props.get('shapeName', '') or props.get('name', '') or props.get('NAME_1', '')
                feature['id'] = normalizar_cadena(nom) 
            return geo
    return None

@st.cache_data(ttl=3600)
def cargar_datos_demo():
    if os.path.exists("Base_Simulada_Demo_CX.csv"):
        return pd.read_csv("Base_Simulada_Demo_CX.csv")
    return None

df = cargar_datos_demo()
geojson_gt = cargar_geojson_local()

if df is None:
    st.warning("⚠️ No se encontró 'Base_Simulada_Demo_CX.csv' en el repositorio.")
    st.stop()

# Ajustes de Fecha
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
df['Mes_Nombre'] = df['Fecha'].dt.month.map(meses_es)
df['Año'] = df['Fecha'].dt.year
df['Mes_Año'] = df['Mes_Nombre'] + " " + df['Año'].astype(str)
df = df.sort_values('Fecha') 

df['Depto_Clean'] = df['Departamento'].apply(normalizar_cadena)
df['Nombre_Grafica'] = df['Tienda']

TODOS_DEPTOS_CLEAN = ['GUATEMALA', 'SACATEPEQUEZ', 'CHIMALTENANGO', 'EL PROGRESO', 'ESCUINTLA', 'SANTA ROSA', 'SOLOLA', 'TOTONICAPAN', 'QUETZALTENANGO', 'SUCHITEPEQUEZ', 'RETALHULEU', 'SAN MARCOS', 'HUEHUETENANGO', 'QUICHE', 'BAJA VERAPAZ', 'ALTA VERAPAZ', 'PETEN', 'IZABAL', 'ZACAPA', 'CHIQUIMULA', 'JALAPA', 'JUTIAPA']

# --- MAPEOS DE VARIABLES GENÉRICAS ---
k_journey = {
    'Estacionamiento': ['GUARDIA', 'ATENCIÓN', 'ATENCION'],
    'Bienvenida': ['PERSONAL', 'AMABLE', 'BIENVENIDA', 'ATENCIÓN', 'ATENCION'],
    'Sector 1': ['PERSONAL', 'ATENDIÓ', 'ATENDIO', 'AMABLE', 'CONOCIMIENTO'],
    'Sector 2': ['PERSONAL', 'AMABLE', 'CONOCIMIENTO'],
    'Pasillo secundario': ['PERSONAL', 'GUIARON'],
    'Cobro': ['PERSONAL', 'SALUDÓ', 'SALUDO', 'AMABLE', 'OFRECIÓ', 'OFRECIO', 'DEJÓ', 'DEJO', 'REACCIONÓ', 'REACCIONO', 'AGRADECIÓ', 'AGRADECIO'],
    'Empaque': ['PERSONAL', 'AMABLE', 'ÁGIL', 'AGIL'],
    'Experiencia': ['PERSONAL', 'ASESORÍA', 'ASESORIA', 'ATENCIÓN', 'ATENCION']
}

k_calidad = {
    'Estacionamiento': ['ESPACIOS', 'DISPONIBLES'],
    'Bienvenida': ['ELEMENTOS', 'LIMPIOS', 'BASURA', 'DESPLAZABAN'],
    'Pasillo central': ['LIMPIO', 'BASURA', 'EXHIBICION', 'EXHIBICIÓN', 'VACIA', 'VACÍA'],
    'Sector 1': ['OLOR', 'LIMPIO', 'BASURA'],
    'Sector 2': ['LIMPIO', 'BASURA'],
    'Sector 3': ['EXHIBICION', 'EXHIBICIÓN', 'COMPLETA', 'LIMPIO', 'BASURA'],
    'Pasillo secundario': ['LIMPIO', 'BASURA', 'CAJAS', 'OBSTACULIZA'],
    'Cobro': ['PUNTO DE COBRO', 'DISPONIBLE'],
    'Empaque': ['OPCIONES', 'SUFICIENTES'],
    'Sanitarios': ['DISPONIBLE', 'SUMINISTROS', 'FUNCIONAN', 'LIMPIEZA', 'OLIA', 'OLÍA'],
    'Experiencia': ['AMBIENTE', 'ILUMINACION', 'ILUMINACIÓN', 'DISEÑO', 'MUSICA', 'MÚSICA', 'AROMA']
}

cols_preguntas = [c for c in df.columns if '[' in c and ']' in c]
preguntas_inversas = ['vacía', 'vacia', 'mal olor', 'obstaculiza', 'fuera de servicio'] 

def obtener_categoria_limpia(col_name):
    c_up = col_name.upper()
    if 'ESTACIONAMIENTO' in c_up: return '🚗 Estacionamiento'
    elif 'BIENVENIDA' in c_up: return '👋 Bienvenida'
    elif 'PASILLO CENTRAL' in c_up: return '🛤️ Pasillo central'
    elif 'SECTOR 1' in c_up: return '🎯 Sector 1'
    elif 'SECTOR 2' in c_up: return '🎯 Sector 2'
    elif 'SECTOR 3' in c_up: return '🎯 Sector 3'
    elif 'PASILLO SECUNDARIO' in c_up: return '🛣️ Pasillo secundario'
    elif 'COBRO' in c_up: return '💳 Cobro'
    elif 'EMPAQUE' in c_up: return '🛍️ Empaque'
    elif 'SANITARIO' in c_up: return '🚽 Sanitarios'
    elif 'EXPERIENCIA' in c_up: return '⭐ Experiencia'
    else: return '📌 Otros'

mapa_columnas_limpias = {}
preguntas_por_categoria = {}
categorias_limpias_list = []

for col in cols_preguntas:
    pregunta_raw = col.split('[')[1].replace(']', '').strip()
    cat_clean = obtener_categoria_limpia(col)
    col_clean = f"{cat_clean} - {pregunta_raw}"
    mapa_columnas_limpias[col] = col_clean
    if cat_clean not in categorias_limpias_list:
        categorias_limpias_list.append(cat_clean)
        preguntas_por_categoria[cat_clean] = []
    preguntas_por_categoria[cat_clean].append(col_clean)

# Procesamiento Lógico
for idx, row in df.iterrows():
    puntos_ganados, preguntas_validas = 0, 0
    desempeno_puntos = {c: {'ganados': 0, 'validos': 0} for c in categorias_limpias_list}
    j_ganados = {k: 0 for k in k_journey}; j_validos = {k: 0 for k in k_journey}
    c_ganados = {k: 0 for k in k_calidad}; c_validos = {k: 0 for k in k_calidad}
    
    for col in cols_preguntas:
        respuesta = str(row[col]).strip().upper()
        if respuesta not in ['NAN', 'N/A', 'NO APLICA', '', 'NONE']:
            preguntas_validas += 1
            cat_clean = obtener_categoria_limpia(col)
            pregunta = col.split('[')[1].replace(']', '').strip()
            
            es_inversa = any(p in col.lower() for p in preguntas_inversas)
            es_positivo = (es_inversa and respuesta == 'NO') or (not es_inversa and respuesta == 'SÍ')
            
            df.at[idx, mapa_columnas_limpias[col]] = 1 if es_positivo else 0
            
            if es_positivo:
                puntos_ganados += 1
                desempeno_puntos[cat_clean]['ganados'] += 1
            desempeno_puntos[cat_clean]['validos'] += 1
                
            pc_up = col.split('[')[0].upper()
            preg_up = pregunta.upper()
            
            # Journey
            cat_j = next((k for k in k_journey if k.upper() in pc_up), None)
            if cat_j and any(k in preg_up for k in k_journey[cat_j]):
                j_validos[cat_j] += 1
                if es_positivo: j_ganados[cat_j] += 1

            # Calidad
            cat_c = next((k for k in k_calidad if k.upper() in pc_up), None)
            if cat_c and any(k in preg_up for k in k_calidad[cat_c]):
                c_validos[cat_c] += 1
                if es_positivo: c_ganados[cat_c] += 1
                
    df.at[idx, 'Score_Operativo'] = (puntos_ganados / preguntas_validas * 100) if preguntas_validas > 0 else 0
    for cat_clean, data in desempeno_puntos.items(): df.at[idx, f'CAT_{cat_clean}'] = (data['ganados'] / data['validos']) * 100 if data['validos'] > 0 else None
    for k in k_journey: df.at[idx, f'JOURNEY_{k}'] = (j_ganados[k] / j_validos[k] * 100) if j_validos[k] > 0 else None
    for k in k_calidad: df.at[idx, f'CALIDAD_{k}'] = (c_ganados[k] / c_validos[k] * 100) if c_validos[k] > 0 else None

def color_semaforo(score):
    if pd.isna(score): return '#D3D3D3'
    if score <= 50: return '#E74C3C' 
    elif score <= 70: return '#F1C40F' 
    elif score <= 90: return '#7DCEA0' 
    else: return '#1E8449' 

def emoji_semaforo(score):
    if pd.isna(score): return '⚪'
    if score <= 50: return '😡' 
    elif score <= 70: return '😕' 
    elif score <= 90: return '🙂' 
    else: return '😃' 

df['Color'] = df['Score_Operativo'].apply(color_semaforo)

# ==========================================
# 3. FILTROS BIDIERECCIONALES
# ==========================================
st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns([0.9, 0.9, 1.1, 1.1, 1.8, 1.2])

with c1: f_mes = st.multiselect("📅 Mes", df['Mes_Nombre'].dropna().unique(), default=df['Mes_Nombre'].dropna().unique())
with c2: f_ano = st.multiselect("🗓️ Año", df['Año'].dropna().unique(), default=df['Año'].dropna().unique())
with c3: f_depto = st.multiselect("📍 Depto", sorted(df['Departamento'].dropna().unique()), default=[st.session_state.depto_seleccionado] if st.session_state.depto_seleccionado else [])
with c4: f_sector = st.multiselect("🏢 Sector", sorted(df['Sector sucursal'].dropna().unique()), default=[st.session_state.sector_seleccionado] if st.session_state.sector_seleccionado else [])
with c5: f_tiendas_sel = st.multiselect("🔍 Tiendas", sorted(df['Nombre_Grafica'].dropna().unique()), default=[st.session_state.tienda_seleccionada] if st.session_state.tienda_seleccionada else [])

if not f_tiendas_sel: st.session_state.tienda_seleccionada = None
if not f_sector: st.session_state.sector_seleccionado = None
if not f_depto: st.session_state.depto_seleccionado = None

df_f = df[df['Mes_Nombre'].isin(f_mes) & df['Año'].isin(f_ano)]
if f_depto: df_f = df_f[df_f['Departamento'].isin(f_depto)]
if f_sector: df_f = df_f[df_f['Sector sucursal'].isin(f_sector)]
if f_tiendas_sel: df_f = df_f[df_f['Nombre_Grafica'].isin(f_tiendas_sel)]

with c6:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if not df_f.empty:
        export_cols = ['Fecha', 'Marca temporal', 'Tienda', 'Departamento', 'Sector sucursal', 'Score_Operativo']
        export_cols.extend(list(mapa_columnas_limpias.values()))
        df_export = df_f[[c for c in export_cols if c in df_f.columns]].copy()
        if 'Fecha' in df_export.columns: df_export['Fecha'] = df_export['Fecha'].dt.strftime('%d/%m/%Y')
        st.download_button("📥 Exportar CSV", data=df_export.to_csv(index=False).encode('utf-8'), file_name="Demo_Data_CX.csv", mime="text/csv", use_container_width=True)

st.markdown('</div><br>', unsafe_allow_html=True)
if df_f.empty: st.info("Ajusta los filtros."); st.stop()

promedio = df_f['Score_Operativo'].mean()

# ==========================================
# 4. MACRO Y MAPA 
# ==========================================
cm1, cm2 = st.columns([1, 2])
with cm1:
    st.metric("Cumplimiento Promedio", f"{promedio:.1f}%")
    st.metric("Tiendas Evaluadas", len(df_f['Tienda'].unique()))
    fig_g = go.Figure(go.Indicator(mode="gauge+number", value=promedio, number={'suffix': "%"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color_semaforo(promedio)}}))
    fig_g.update_layout(height=240, margin=dict(l=20, r=20, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g, use_container_width=True)

with cm2:
    st.markdown("#### Cumplimiento por Departamento")
    st.markdown("<p style='color: #A0A0A0; font-size: 13px; margin-top:-10px;'><i>*Haz clic en el mapa para filtrar.</i></p>", unsafe_allow_html=True)
    if geojson_gt:
        d_activos = df_f['Depto_Clean'].unique()
        d_calc = df_f.groupby('Depto_Clean')['Score_Operativo'].mean().to_dict()
        locs, cols, txts = [], [], []
        for d in TODOS_DEPTOS_CLEAN:
            locs.append(d)
            if d in d_activos:
                sc = d_calc.get(d, 0)
                cols.append(color_semaforo(sc)); txts.append(f"<b>{d.title()}</b><br>{sc:.1f}%")
            else: cols.append('#D3D3D3'); txts.append(f"<b>{d.title()}</b><br>N/A")
            
        fig_m = go.Figure(go.Choropleth(geojson=geojson_gt, locations=locs, featureidkey="id", z=list(range(len(locs))), text=txts, hoverinfo='text', showscale=False))
        fig_m.data[0].colorscale = [[i/len(locs), c] for i, c in enumerate(cols)] + [[(i+1)/len(locs), c] for i, c in enumerate(cols)]
        fig_m.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
        fig_m.update_layout(height=310, margin={"r":0, "t":0, "l":0, "b":0}, dragmode=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        ev_m = st.plotly_chart(fig_m, use_container_width=True, on_select="rerun")
        if ev_m and ev_m.selection.get("points"):
            sel_d = ev_m.selection["points"][0]["location"].title()
            if sel_d == 'Guatemala': sel_d = 'Guatemala'
            if sel_d != st.session_state.depto_seleccionado: st.session_state.depto_seleccionado = sel_d; st.rerun()

st.markdown("---")

# ==========================================
# 5. RANKINGS Y TENDENCIAS
# ==========================================
ranking = df_f.groupby('Nombre_Grafica')['Score_Operativo'].mean().reset_index()
c_top, c_bot = st.columns(2)
with c_top:
    st.markdown("#### 🏆 Top Tiendas"); top_40 = ranking.sort_values('Score_Operativo', ascending=False).head(40)
    top_40['Color'] = top_40['Score_Operativo'].apply(color_semaforo)
    fig_t = px.bar(top_40, x='Nombre_Grafica', y='Score_Operativo', text_auto='.1f')
    fig_t.update_traces(marker_color=top_40['Color']); fig_t.update_layout(height=380, xaxis_title="", yaxis_title="%", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    ev_t = st.plotly_chart(fig_t, use_container_width=True, on_select="rerun")
with c_bot:
    st.markdown("#### ⚠️ Bottom Tiendas"); bot_40 = ranking.sort_values('Score_Operativo', ascending=True).head(40)
    bot_40['Color'] = bot_40['Score_Operativo'].apply(color_semaforo)
    fig_b = px.bar(bot_40, x='Nombre_Grafica', y='Score_Operativo', text_auto='.1f')
    fig_b.update_traces(marker_color=bot_40['Color']); fig_b.update_layout(height=380, xaxis_title="", yaxis_title="%", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    ev_b = st.plotly_chart(fig_b, use_container_width=True, on_select="rerun")

sel_s = ev_t.selection["points"][0]["x"] if ev_t and ev_t.selection.get("points") else (ev_b.selection["points"][0]["x"] if ev_b and ev_b.selection.get("points") else None)
if sel_s and sel_s != st.session_state.tienda_seleccionada: st.session_state.tienda_seleccionada = sel_s; st.rerun()

st.markdown("---")

ct1, ct2 = st.columns(2)
with ct1:
    st.subheader("Evolución Histórica (Filtros Activos)")
    df_tr = df_f.groupby('Mes_Año', sort=False)['Score_Operativo'].mean().reset_index()
    fig_tr = px.line(df_tr, x='Mes_Año', y='Score_Operativo', markers=True)
    fig_tr.update_layout(yaxis=dict(range=[0,100]), height=350, xaxis_title="", yaxis_title="%", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tr, use_container_width=True)
with ct2:
    st.markdown("#### Ranking por Sector")
    r_sec = df_f.groupby('Sector sucursal')['Score_Operativo'].mean().reset_index().sort_values('Score_Operativo')
    r_sec['Color'] = r_sec['Score_Operativo'].apply(color_semaforo)
    fig_s = px.bar(r_sec, x='Score_Operativo', y='Sector sucursal', orientation='h', text_auto='.1f')
    fig_s.update_traces(marker_color=r_sec['Color']); fig_s.update_layout(height=350, xaxis_title="%", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    ev_sec = st.plotly_chart(fig_s, use_container_width=True, on_select="rerun")
    if ev_sec and ev_sec.selection.get("points"):
        sel_sec = ev_sec.selection["points"][0]["y"]
        if sel_sec != st.session_state.sector_seleccionado: st.session_state.sector_seleccionado = sel_sec; st.rerun()

st.markdown("---")

# ==========================================
# 7. DIAGNÓSTICO
# ==========================================
st.subheader("Diagnóstico por Punto de Contacto")
cp1, cp2 = st.columns(2)
cols_cat = [f'CAT_{c}' for c in categorias_limpias_list if f'CAT_{c}' in df_f.columns]
if cols_cat:
    pareto = df_f[cols_cat].mean().sort_values(ascending=False).reset_index(); pareto.columns = ['Categoría', 'Score']
    pareto['Categoría'] = pareto['Categoría'].str.replace('CAT_', ''); pareto['Color'] = pareto['Score'].apply(color_semaforo)
    with cp1:
        fig_p = px.bar(pareto, x='Categoría', y='Score', text_auto='.1f')
        fig_p.update_traces(marker_color=pareto['Color']); fig_p.update_layout(height=420, xaxis_title="", yaxis=dict(range=[0,100]), xaxis_tickangle=-40, margin=dict(b=80), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_p, use_container_width=True)
    with cp2:
        cat_sel = st.selectbox("🔍 Diagnóstico detallado por parámetro:", pareto['Categoría'].tolist())
        if cat_sel:
            c_esp = preguntas_por_categoria.get(cat_sel, []); c_graf = [f'CAT_{cat_sel}'] + c_esp
            df_pc = df_f.groupby('Mes_Año', sort=False)[c_graf].mean().reset_index()
            for c in c_esp: df_pc[c] *= 100
            renombres = {f'CAT_{cat_sel}': f'🌟 PROMEDIO: {cat_sel}'}
            for c in c_esp: renombres[c] = c.replace(f"{cat_sel} - ", "")
            df_pc.rename(columns=renombres, inplace=True)
            fig_d = px.line(df_pc, x='Mes_Año', y=list(renombres.values()), markers=True)
            fig_d.update_layout(height=420, xaxis_title="", yaxis_title="%", yaxis=dict(range=[0,100]), legend=dict(orientation="h", y=-0.6, xanchor="center", x=0.5), margin=dict(b=100), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_d, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. JOURNEY & CALIDAD (Generación Dinámica)
# ==========================================
def render_chevrons(keys_list, class_prefix):
    n = len(keys_list)
    html = '<div class="journey-container">'
    for i, k in enumerate(keys_list):
        style = ' style="margin-right: 0;"' if i == n-1 else ''
        html += f'<div class="{class_prefix}-step {class_prefix}-{i+1}"{style}>{k}</div>'
    html += '</div>'
    return html

st.subheader("Experiencia con Personal (Customer Journey)")
j_keys = list(k_journey.keys())
j_scores = [df_f[f'JOURNEY_{k}'].mean() if f'JOURNEY_{k}' in df_f.columns else float('nan') for k in j_keys]
j_colors = [color_semaforo(s) for s in j_scores]; j_emojis = [emoji_semaforo(s) for s in j_scores]

st.markdown(render_chevrons(j_keys, 'j'), unsafe_allow_html=True)
fig_j = go.Figure()
fig_j.add_trace(go.Scatter(x=j_keys, y=[s if not pd.isna(s) else 0 for s in j_scores], mode='lines', line=dict(color='#BDC3C7', width=4), hoverinfo='none'))
for x, y, c, e in zip(j_keys, j_scores, j_colors, j_emojis):
    y_val = y if not pd.isna(y) else 0
    fig_j.add_trace(go.Scatter(x=[x], y=[y_val], mode='markers', marker=dict(size=48, color=c, line=dict(width=2, color='white')), hoverinfo='y'))
    fig_j.add_annotation(x=x, y=y_val, text=e, font=dict(size=28), showarrow=False, xanchor='center', yanchor='middle')
fig_j.update_layout(height=320, margin=dict(l=50, r=50, t=30, b=10), showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(range=[0,120], showgrid=True), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_j, use_container_width=True)

st.markdown("---")
st.subheader("Variables de Calidad por Punto de Contacto")
c_keys = list(k_calidad.keys())
c_scores = [df_f[f'CALIDAD_{k}'].mean() if f'CALIDAD_{k}' in df_f.columns else float('nan') for k in c_keys]

st.markdown(render_chevrons(c_keys, 'c'), unsafe_allow_html=True)
fig_c = go.Figure(go.Bar(x=c_keys, y=[s if not pd.isna(s) else 0 for s in c_scores], marker_color=[color_semaforo(s) for s in c_scores], text=[f"{s:.1f}%" if not pd.isna(s) else "" for s in c_scores], textposition='auto', textfont=dict(size=14, color='white')))
fig_c.update_layout(bargap=0.3, height=350, margin=dict(l=50, r=50, t=30, b=10), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(range=[0,105]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_c, use_container_width=True)

# ==========================================
# 9. FEEDBACK
# ==========================================
if st.session_state.tienda_seleccionada:
    st.markdown("---"); st.markdown("### Feedback Cualitativo")
    c_alertas, c_comentarios = st.columns(2)
    with c_alertas:
        st.markdown("#### 🚨 Alertas (Hallazgos Graves)")
        alertas = df_f[df_f['Hallazgo grave'].notna() & (df_f['Hallazgo grave'] != '')]
        if not alertas.empty:
            for _, r in alertas.iterrows(): st.error(f"**{r['Fecha'].strftime('%d/%m/%Y')}**: {r['Hallazgo grave']}")
        else: st.info("No hay hallazgos graves.")
    with c_comentarios:
        st.markdown("#### 💬 Comentarios")
        coments = df_f[df_f['Comentarios'].notna() & (df_f['Comentarios'] != '')]
        if not coments.empty:
            for _, r in coments.iterrows(): st.info(f"**{r['Fecha'].strftime('%d/%m/%Y')}**: {r['Comentarios']}")
        else: st.info("No hay comentarios.")