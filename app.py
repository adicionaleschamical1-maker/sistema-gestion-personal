import streamlit as st
import gspread
import pandas as pd
import datetime
import random
import time
import json
from collections import defaultdict
import io
import plotly.express as px
import plotly.graph_objects as go
import re

try:
    from openpyxl import load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

st.set_page_config(
    page_title="Sistema de Gestión de Personal",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="collapsed"
)

# ========== CSS ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    html, body, [class*="css"] { font-size: 14px; line-height: 1.5; }
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.6rem !important; font-weight: 600 !important; }
    h3 { font-size: 1.3rem !important; font-weight: 600 !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f2b3d 0%, #1a3a4f 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stWrite {
        color: #e8f0f7 !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border: none;
    }
    h1 {
        background: linear-gradient(135deg, #1f3a6b 0%, #2c5a8c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    h2 {
        color: #1f3a6b;
        border-left: 4px solid #2ecc71;
        padding-left: 15px;
        margin: 20px 0;
    }
    .stButton button {
        border-radius: 10px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(52,152,219,0.3);
    }
    div[data-testid="stButton"] { display: block !important; }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 10px 30px !important;
        border-radius: 30px !important;
        border: none !important;
        font-size: 16px !important;
        width: 100% !important;
    }
    .stButton button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(46,204,113,0.4);
    }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eef2f7;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1f3a6b 0%, #2c5a8c 100%);
        color: white;
        text-align: center;
        padding: 12px;
        z-index: 999;
        font-size: 0.75rem;
    }
    /* Tarjeta carnet */
    .tarjeta-carnet {
        background: linear-gradient(145deg, #ffffff, #f5f7fa);
        border-radius: 16px;
        padding: 25px 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.6);
        margin: 20px 0;
        max-width: 650px;
        position: relative;
    }
    .tarjeta-carnet .banda-superior {
        background: linear-gradient(90deg, #1f3a6b, #2c5a8c);
        margin: -25px -30px 20px -30px;
        padding: 12px 30px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 2px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .tarjeta-carnet .avatar {
        background: linear-gradient(135deg, #1f3a6b, #2c5a8c);
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 15px rgba(31,58,107,0.3);
        border: 3px solid white;
        flex-shrink: 0;
    }
    .tarjeta-carnet .badge {
        display: inline-block;
        padding: 3px 14px;
        border-radius: 12px;
        font-size: 0.6rem;
        font-weight: 600;
        color: white;
    }
    .tarjeta-carnet .dato {
        display: flex;
        padding: 6px 12px;
        background: #f8fafc;
        border-radius: 8px;
        align-items: center;
        border-left: 3px solid #2ecc71;
        margin-bottom: 4px;
    }
    .tarjeta-carnet .dato-extra {
        border-left-color: #8e44ad;
    }
    .tarjeta-carnet .pie {
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #eef2f7;
        display: flex;
        justify-content: space-between;
        font-size: 0.6rem;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

# =================================================================
# 🧹 NUEVA FUNCIÓN DE LIMPIEZA DE HTML EN DATOS
# =================================================================
def limpiar_html_celdas(df):
    """
    Elimina todas las etiquetas HTML (como <div class='dato'>) de todas
    las celdas del DataFrame, dejando solo el texto limpio.
    """
    df_limpio = df.copy()
    for col in df_limpio.columns:
        df_limpio[col] = df_limpio[col].astype(str).str.replace(r'<[^>]+>', '', regex=True)
        df_limpio[col] = df_limpio[col].str.replace(r'&nbsp;', ' ', regex=True)
        df_limpio[col] = df_limpio[col].str.strip()
    return df_limpio

# ========== FUNCIONES ==========
@st.cache_data(ttl=60)
def cargar_datos_hoja():
    with st.spinner("🔄 Cargando y limpiando datos..."):
        try:
            creds = st.secrets["gsheets"]
            gc = gspread.service_account_from_dict(creds)
            sh = gc.open_by_key("1TH32e7TkB4RYEKxxRhGRnnYxjkT9AF9TeuplxtYih1Y")
            
            ws_personal = sh.worksheet("Personal")
            all_values = ws_personal.get_all_values()
            if len(all_values) == 0:
                st.error("La hoja 'Personal' está vacía")
                st.stop()
            
            header = all_values[0]
            data = all_values[1:]
            header = [str(col).strip().upper() for col in header]
            df_personal = pd.DataFrame(data, columns=header)
            
            # Limpiamos el HTML de todas las columnas al cargar
            df_personal = limpiar_html_celdas(df_personal)
            
            for col in df_personal.columns:
                df_personal[col] = df_personal[col].astype(str).str.strip()
            df_personal.replace('', pd.NA, inplace=True)
            
            ws_usuarios = sh.worksheet("Usuarios")
            all_users = ws_usuarios.get_all_values()
            if len(all_users) == 0:
                st.error("La hoja 'Usuarios' está vacía")
                st.stop()
            header_users = all_users[0]
            header_users = [str(col).strip().upper() for col in header_users]
            data_users = all_users[1:]
            df_usuarios = pd.DataFrame(data_users, columns=header_users)
            for col in df_usuarios.columns:
                df_usuarios[col] = df_usuarios[col].astype(str).str.strip()
            df_usuarios.replace('', pd.NA, inplace=True)
            
            try:
                ws_propuestas = sh.worksheet("Propuestas")
                propuestas_data = ws_propuestas.get_all_values()
                if len(propuestas_data) > 1:
                    header_prop = [str(col).strip().upper() for col in propuestas_data[0]]
                    prop_data = propuestas_data[1:]
                    df_propuestas = pd.DataFrame(prop_data, columns=header_prop)
                else:
                    df_propuestas = pd.DataFrame(columns=['ID', 'FECHA', 'USUARIO_DNI', 'USUARIO_NOMBRE', 'DEPENDENCIA', 'ACCION', 'DATOS_ORIGINALES', 'DATOS_NUEVOS', 'ESTADO'])
            except:
                df_propuestas = pd.DataFrame(columns=['ID', 'FECHA', 'USUARIO_DNI', 'USUARIO_NOMBRE', 'DEPENDENCIA', 'ACCION', 'DATOS_ORIGINALES', 'DATOS_NUEVOS', 'ESTADO'])
                ws_propuestas = sh.add_worksheet(title="Propuestas", rows=1000, cols=20)
                ws_propuestas.update([df_propuestas.columns.tolist()])
            
            return df_personal, df_usuarios, df_propuestas
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

def get_new_connection():
    creds = st.secrets["gsheets"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1TH32e7TkB4RYEKxxRhGRnnYxjkT9AF9TeuplxtYih1Y")

def guardar_propuesta(usuario_dni, usuario_nombre, dependencia, accion, datos_originales, datos_nuevos):
    try:
        sh = get_new_connection()
        ws = sh.worksheet("Propuestas")
        propuestas_data = ws.get_all_values()
        if len(propuestas_data) > 1:
            header_prop = [str(col).strip().upper() for col in propuestas_data[0]]
            prop_data = propuestas_data[1:]
            propuestas_df = pd.DataFrame(prop_data, columns=header_prop)
        else:
            propuestas_df = pd.DataFrame(columns=['ID', 'FECHA', 'USUARIO_DNI', 'USUARIO_NOMBRE', 'DEPENDENCIA', 'ACCION', 'DATOS_ORIGINALES', 'DATOS_NUEVOS', 'ESTADO'])
        
        nuevo_id = len(propuestas_df) + 1 if not propuestas_df.empty else 1
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nueva_propuesta = pd.DataFrame([{
            'ID': nuevo_id,
            'FECHA': fecha,
            'USUARIO_DNI': usuario_dni,
            'USUARIO_NOMBRE': usuario_nombre,
            'DEPENDENCIA': dependencia,
            'ACCION': accion,
            'DATOS_ORIGINALES': json.dumps(datos_originales, ensure_ascii=False),
            'DATOS_NUEVOS': json.dumps(datos_nuevos, ensure_ascii=False),
            'ESTADO': 'PENDIENTE'
        }])
        
        propuestas_df = pd.concat([propuestas_df, nueva_propuesta], ignore_index=True)
        ws.clear()
        ws.update([propuestas_df.columns.tolist()] + propuestas_df.values.tolist())
        st.session_state.df_propuestas = propuestas_df
        return True
    except:
        return False

def aprobar_propuesta(id_propuesta):
    try:
        sh = get_new_connection()
        ws_propuestas = sh.worksheet("Propuestas")
        propuestas_data = ws_propuestas.get_all_values()
        if len(propuestas_data) <= 1:
            return False
        header_prop = [str(col).strip().upper() for col in propuestas_data[0]]
        prop_data = propuestas_data[1:]
        propuestas_df = pd.DataFrame(prop_data, columns=header_prop)
        propuesta = propuestas_df[propuestas_df['ID'] == str(id_propuesta)].iloc[0]
        if propuesta['ESTADO'] != 'PENDIENTE':
            return False
        accion = propuesta['ACCION']
        datos_nuevos = json.loads(propuesta['DATOS_NUEVOS'])
        ws_personal = sh.worksheet("Personal")
        all_data = ws_personal.get_all_values()
        header = [str(col).strip().upper() for col in all_data[0]]
        if accion == 'AGREGAR':
            nueva_fila = [datos_nuevos.get(col, '') for col in header]
            ws_personal.append_row(nueva_fila)
        elif accion == 'MODIFICAR':
            dni_modificar = datos_nuevos.get('DNI')
            if dni_modificar:
                col_dni_idx = header.index('DNI') if 'DNI' in header else None
                if col_dni_idx is not None:
                    for i, row in enumerate(all_data[1:], start=2):
                        if len(row) > col_dni_idx and row[col_dni_idx] == str(dni_modificar):
                            for col_idx, col_name in enumerate(header):
                                if col_name in datos_nuevos:
                                    ws_personal.update_cell(i, col_idx+1, str(datos_nuevos[col_name]))
                            break
        elif accion == 'ELIMINAR':
            dni_eliminar = datos_nuevos.get('DNI')
            if dni_eliminar:
                col_dni_idx = header.index('DNI') if 'DNI' in header else None
                if col_dni_idx is not None:
                    for i, row in enumerate(all_data[1:], start=2):
                        if len(row) > col_dni_idx and row[col_dni_idx] == str(dni_eliminar):
                            ws_personal.delete_rows(i)
                            break
        propuestas_df.loc[propuestas_df['ID'] == str(id_propuesta), 'ESTADO'] = 'APROBADO'
        ws_propuestas.clear()
        ws_propuestas.update([propuestas_df.columns.tolist()] + propuestas_df.values.tolist())
        st.session_state.df_personal, st.session_state.df_usuarios, st.session_state.df_propuestas = cargar_datos_hoja()
        return True
    except:
        return False

def rechazar_propuesta(id_propuesta):
    try:
        sh = get_new_connection()
        ws_propuestas = sh.worksheet("Propuestas")
        propuestas_data = ws_propuestas.get_all_values()
        if len(propuestas_data) <= 1:
            return False
        header_prop = [str(col).strip().upper() for col in propuestas_data[0]]
        prop_data = propuestas_data[1:]
        propuestas_df = pd.DataFrame(prop_data, columns=header_prop)
        propuestas_df.loc[propuestas_df['ID'] == str(id_propuesta), 'ESTADO'] = 'RECHAZADO'
        ws_propuestas.clear()
        ws_propuestas.update([propuestas_df.columns.tolist()] + propuestas_df.values.tolist())
        st.session_state.df_propuestas = propuestas_df
        return True
    except:
        return False

# ========== TARJETA ==========
def mostrar_tarjeta_efectivo(row, nombre_col, dni_col):
    nombre = row.get(nombre_col, 'Sin nombre')
    dni = row.get(dni_col, 'N/A') if dni_col else 'N/A'
    jerarquia = row.get('JERARQUÍA', 'Sin jerarquía')
    funcion = row.get('FUNCIÓN', 'Sin función')
    dependencia = row.get('DEPENDENCIA', 'Sin dependencia')
    sexo = row.get('SEXO', 'N/A')
    
    palabras = nombre.split()
    iniciales = (palabras[0][0] + palabras[1][0]) if len(palabras) >= 2 else nombre[:2].upper()
    
    html = f'''
    <div class="tarjeta-carnet">
        <div class="banda-superior">
            <span>👮 POLICÍA DE LA PROVINCIA</span>
            <span style="font-size:0.6rem;opacity:0.7;">FICHA N° {dni.replace(".","")[:6]}</span>
        </div>
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:20px;">
            <div class="avatar">{iniciales}</div>
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#1f3a6b;">{nombre}</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                    <span class="badge" style="background:#2c3e50;">DNI: {dni}</span>
                    <span class="badge" style="background:#3498db;">{jerarquia}</span>
                    <span class="badge" style="background:#e67e22;">{funcion}</span>
                    <span class="badge" style="background:#8e44ad;">{dependencia}</span>
                    {f'<span class="badge" style="background:#e74c3c;">{sexo}</span>' if sexo and sexo != 'N/A' else ''}
                </div>
            </div>
        </div>
        <div style="border-top:2px dashed #dce3ed;margin:5px 0 15px 0;"></div>
        <div>
    '''
    
    columnas = [
        'MARCA DE ARMA', 'N° DE ARMA', 'OBS', 'SITUACION',
        'GRUPO SANGUINEO', 'N° DE TELEFONO', 'DOMICILIO REAL (DONDE VIVE)',
        'FECHA DE NACIMIENTO', 'EDAD', 'ANTIGUEDAD',
        'DIAS DE LICENCIA DISPONIBLE', 'DIAS DE LICENCIA TOMADA',
        'DIAS DE PROXIMA LICENCIA', 'LEGAJO PERSONAL', 'FECHA DE ULTIMO ASCENSO'
    ]
    
    for col in columnas:
        if col in row.index:
            valor = row.get(col, '')
            if valor and str(valor) != 'nan':
                etiqueta = col.replace('_', ' ').title()
                icono = "📌"
                if "TELEFONO" in col: icono = "📞"
                elif "DOMICILIO" in col: icono = "📍"
                elif "FECHA" in col and "NACIMIENTO" in col: icono = "🎂"
                elif "EDAD" in col: icono = "📅"
                elif "ARMA" in col: icono = "🔫"
                elif "SANGUINEO" in col: icono = "🩸"
                elif "LICENCIA" in col: icono = "📋"
                elif "ANTIGUEDAD" in col: icono = "⏳"
                
                html += f'''
                <div class="dato">
                    <span style="font-weight:600;color:#4a5568;width:160px;flex-shrink:0;font-size:0.78rem;">{icono} {etiqueta}:</span>
                    <span style="color:#1a202c;font-weight:500;font-size:0.85rem;">{valor}</span>
                </div>
                '''
    
    columnas_extra = [c for c in row.index if c not in columnas and c not in ['APELLIDO Y NOMBRE', 'DNI', 'JERARQUÍA', 'FUNCIÓN', 'DEPENDENCIA', 'SEXO', 'N°', 'N', 'Numero', 'Legajo']]
    for col in columnas_extra:
        valor = row.get(col, '')
        if valor and str(valor) != 'nan':
            etiqueta = col.replace('_', ' ').title()
            html += f'''
            <div class="dato dato-extra">
                <span style="font-weight:600;color:#4a5568;width:160px;flex-shrink:0;font-size:0.78rem;">📌 {etiqueta}:</span>
                <span style="color:#1a202c;font-weight:500;font-size:0.85rem;">{valor}</span>
            </div>
            '''
    
    html += '''
        </div>
        <div class="pie">
            <span>📅 Emisión: ''' + datetime.datetime.now().strftime('%d/%m/%Y') + '''</span>
            <span>🔒 Documento oficial</span>
        </div>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)

# ========== CARGA INICIAL ==========
if 'df_personal' not in st.session_state:
    resultado = cargar_datos_hoja()
    st.session_state.df_personal = resultado[0]
    st.session_state.df_usuarios = resultado[1]
    st.session_state.df_propuestas = resultado[2]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ========== LOGIN ==========
if st.session_state.logged_in:
    user = st.session_state.user_data
    
    with st.sidebar:
        st.markdown("### 👤 Panel de Usuario")
        st.markdown("---")
        st.markdown(f"**Nombre:** {user['NOMBRE']}")
        st.markdown(f"**📄 DNI:** {user['DNI']}")
        st.markdown(f"**🏢 Dependencia:** {user['DEPENDENCIA']}")
        st.markdown(f"**⭐ Jerarquía:** {user['JERARQUÍA']}")
        st.markdown("---")
        if st.button("🔄 REFRESCAR DATOS", use_container_width=True):
            with st.spinner("Actualizando..."):
                resultado = cargar_datos_hoja()
                st.session_state.df_personal = resultado[0]
                st.session_state.df_usuarios = resultado[1]
                st.session_state.df_propuestas = resultado[2]
                st.success("✅ Datos actualizados")
                time.sleep(1)
                st.rerun()
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    st.title("👮‍♂️ Sistema de Gestión de Personal")
    st.caption(f"📅 Última actualización: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    es_admin = user['FUNCIÓN'].upper() == "ADMINISTRADOR"
    
    # ========== PROPUESTAS PENDIENTES ==========
    if es_admin:
        if not st.session_state.df_propuestas.empty:
            estado_col = None
            for col in st.session_state.df_propuestas.columns:
                if col.upper() == 'ESTADO':
                    estado_col = col
                    break
            if estado_col:
                propuestas_pendientes = len(st.session_state.df_propuestas[st.session_state.df_propuestas[estado_col].str.upper() == 'PENDIENTE'])
            else:
                propuestas_pendientes = 0
        else:
            propuestas_pendientes = 0
        
        if propuestas_pendientes > 0:
            st.warning(f"⚠️ **¡ATENCIÓN!** Hay {propuestas_pendientes} propuestas pendientes", icon="⚠️")
    
    # ========== CARGAR DATOS ==========
    if es_admin:
        datos_completos = st.session_state.df_personal.copy()
        st.success("👑 **Modo Administrador**", icon="👑")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📊 Total", len(datos_completos))
        with c2: st.metric("🏢 Dependencias", datos_completos['DEPENDENCIA'].nunique() if 'DEPENDENCIA' in datos_completos else 0)
        with c3: st.metric("⭐ Jerarquías", datos_completos['JERARQUÍA'].nunique() if 'JERARQUÍA' in datos_completos else 0)
        with c4: st.metric("📋 Funciones", datos_completos['FUNCIÓN'].nunique() if 'FUNCIÓN' in datos_completos else 0)
    else:
        datos_completos = st.session_state.df_personal[st.session_state.df_personal['DEPENDENCIA'].astype(str).str.lower() == user['DEPENDENCIA'].lower()].copy()
        st.info(f"👤 **Modo Usuario** - {user['DEPENDENCIA']}", icon="ℹ️")
    
    if len(datos_completos) == 0:
        st.warning("⚠️ No hay personal para mostrar")
        st.stop()
    
    # ========== COLUMNAS ==========
    def find_col(df, posibles):
        for p in posibles:
            if p in df.columns:
                return p
        return None
    
    nombre_col = find_col(datos_completos, ['APELLIDO Y NOMBRE', 'NOMBRE', 'NOMBRE COMPLETO'])
    dni_col = find_col(datos_completos, ['DNI', 'Dni', 'dni'])
    jerarquia_col = find_col(datos_completos, ['JERARQUÍA', 'Jerarquia', 'JERARQUIA', 'RANGO'])
    funcion_col = find_col(datos_completos, ['FUNCIÓN', 'Funcion', 'FUNCION', 'CARGO'])
    dependencia_col = find_col(datos_completos, ['DEPENDENCIA', 'Dependencia', 'DEPARTAMENTO'])
    
    if not nombre_col or not jerarquia_col or not funcion_col or not dependencia_col:
        st.error("❌ Faltan columnas esenciales")
        st.stop()
    
    # ========== FILTROS ==========
    st.markdown("## 🔎 Filtros")
    col1, col2, col3 = st.columns(3)
    with col1: dep_filter = st.multiselect("🏢 Dependencia", sorted(datos_completos[dependencia_col].dropna().unique()))
    with col2: jer_filter = st.multiselect("⭐ Jerarquía", sorted(datos_completos[jerarquia_col].dropna().unique()))
    with col3: fun_filter = st.multiselect("📋 Función", sorted(datos_completos[funcion_col].dropna().unique()))
    
    datos_filtrados = datos_completos.copy()
    if dep_filter: datos_filtrados = datos_filtrados[datos_filtrados[dependencia_col].isin(dep_filter)]
    if jer_filter: datos_filtrados = datos_filtrados[datos_filtrados[jerarquia_col].isin(jer_filter)]
    if fun_filter: datos_filtrados = datos_filtrados[datos_filtrados[funcion_col].isin(fun_filter)]
    
    busqueda = st.text_input("🔍 Búsqueda", placeholder="Nombre, DNI...")
    if busqueda:
        mascara = datos_filtrados.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
        datos_filtrados = datos_filtrados[mascara]
        st.info(f"📌 {len(datos_filtrados)} resultados")
    
    # ========== LISTADO ==========
    st.markdown("## 📋 Listado del personal")
    st.caption(f"Total: {len(datos_filtrados)}")
    
    if len(datos_filtrados) > 0:
        columnas_excluir = ['N°', 'N', 'Numero', 'Legajo']
        columnas_a_mostrar = [c for c in datos_filtrados.columns if c not in columnas_excluir]
        
        for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
            with st.container():
                st.markdown(f"### 🏢 {dependencia}")
                
                if es_admin:
                    st.info("👑 **Administrador** - Solo lectura")
                    st.dataframe(grupo[columnas_a_mostrar], use_container_width=True, hide_index=True)
                else:
                    st.markdown("""
                    <div style="background: #e8f5e9; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #2ecc71; margin-bottom: 10px; font-size: 0.85rem;">
                        ✏️ Modificá los valores y enviá la propuesta de cambios
                    </div>
                    """, unsafe_allow_html=True)
                    
                    edited_df = st.data_editor(
                        grupo[columnas_a_mostrar],
                        use_container_width=True,
                        hide_index=True,
                        num_rows="dynamic",
                        key=f"editor_{dependencia}"
                    )
                    
                    if st.button(f"📨 Enviar propuesta para {dependencia}", key=f"propuesta_{dependencia}", type="primary"):
                        cambios = False
                        if len(edited_df) > len(grupo):
                            for _, row in edited_df.iloc[len(grupo):].iterrows():
                                if guardar_propuesta(user['DNI'], user['NOMBRE'], dependencia, "AGREGAR", {}, row.to_dict()):
                                    cambios = True
                        for i in range(min(len(grupo), len(edited_df))):
                            if not grupo.iloc[i][columnas_a_mostrar].equals(edited_df.iloc[i][columnas_a_mostrar]):
                                orig = {}
                                new = {}
                                for col in columnas_a_mostrar:
                                    if str(grupo.iloc[i][col]) != str(edited_df.iloc[i][col]):
                                        orig[col] = grupo.iloc[i][col]
                                        new[col] = edited_df.iloc[i][col]
                                if orig and guardar_propuesta(user['DNI'], user['NOMBRE'], dependencia, "MODIFICAR", orig, new):
                                    cambios = True
                        if cambios:
                            st.success("✅ Propuesta enviada. El administrador la revisará.")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.info("ℹ️ No se detectaron cambios")
                
                st.markdown("---")
        
        # ===== TARJETAS =====
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%); padding: 12px 20px; border-radius: 10px; margin: 20px 0 15px 0; color: white; font-weight: 600; font-size: 1.2rem;">
            👤 VER FICHA PERSONAL
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 Seleccioná un efectivo", expanded=False):
            st.markdown("Marcá el checkbox para ver la ficha completa")
            for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
                st.markdown(f"**🏢 {dependencia}**")
                for idx, row in grupo.iterrows():
                    nombre = row.get(nombre_col, 'Sin nombre')
                    dni = row.get(dni_col, '')
                    label = f"{nombre} (DNI: {dni})" if dni else nombre
                    if st.checkbox(label, key=f"ver_{idx}_{dependencia}"):
                        st.markdown("---")
                        mostrar_tarjeta_efectivo(row, nombre_col, dni_col)
                        st.markdown("---")
                st.markdown("---")
    else:
        st.warning("⚠️ No hay datos con los filtros seleccionados")

else:
    # ========== LOGIN ==========
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("👮‍♂️ Sistema de Gestión de Personal")
        st.markdown("### Iniciar Sesión")
        dni_input = st.text_input("📄 DNI", placeholder="Ingrese su DNI", key="login_dni")
        clave_input = st.text_input("🔒 Clave", type="password", placeholder="Ingrese su contraseña", key="login_clave")
        if st.button("🚪 Ingresar", type="primary", use_container_width=True, key="login_button"):
            if dni_input and clave_input:
                df_usuarios = st.session_state.df_usuarios
                usuario = df_usuarios[
                    (df_usuarios['DNI'].astype(str).str.lower() == dni_input.lower()) &
                    (df_usuarios['CLAVE'].astype(str).str.lower() == clave_input.lower())
                ]
                if not usuario.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_data = usuario.iloc[0]
                    st.rerun()
                else:
                    st.error("❌ DNI o Clave incorrectos")
            else:
                st.warning("⚠️ Complete ambos campos")
    with col2:
        st.markdown("### ℹ️ Información")
        st.info("""
        **Sistema de Gestión de Personal**
        - 🔐 Acceso restringido
        - 🔄 Gestión de rotaciones
        - 📎 Exportación de datos
        - 📊 Resúmenes estadísticos
        """)
