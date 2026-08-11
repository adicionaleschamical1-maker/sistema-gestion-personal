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

# Intentar importar openpyxl para Excel formateado
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

# ========== CSS MEJORADO ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    html, body, [class*="css"] {
        font-size: 14px;
        line-height: 1.5;
    }
    
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    h2 { font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.3px; }
    h3 { font-size: 1.3rem !important; font-weight: 600 !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botón de colapso del header */
    button[data-testid="baseButton-header"] {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 8px 20px 8px 15px !important;
        margin: 10px 0 10px 15px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-testid="baseButton-header"]:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(46,204,113,0.4);
    }
    
    button[data-testid="baseButton-header"]::after {
        content: " ☰ MENÚ";
        color: white;
        font-weight: bold;
    }
    
    button[data-testid="baseButton-header"] svg {
        stroke: white !important;
        fill: white !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f2b3d 0%, #1a3a4f 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stWrite {
        color: #e8f0f7 !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46,204,113,0.3);
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
    
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
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
</style>
""", unsafe_allow_html=True)

# ========== FUNCIONES DE CARGA ==========
@st.cache_data(ttl=3600)
def cargar_datos_hoja():
    with st.spinner("🔄 Cargando datos desde Google Sheets..."):
        try:
            creds = st.secrets["gsheets"]
            gc = gspread.service_account_from_dict(creds)
            sh = gc.open_by_key("1TH32e7TkB4RYEKxxRhGRnnYxjkT9AF9TeuplxtYih1Y")
            
            # ===== HOJA PERSONAL =====
            ws_personal = sh.worksheet("Personal")
            all_values = ws_personal.get_all_values()
            if len(all_values) == 0:
                st.error("La hoja 'Personal' está vacía")
                st.stop()
            
            header = all_values[0]
            data = all_values[1:]
            
            # Limpiar encabezados
            header = [str(col).strip().upper() for col in header]
            
            # Crear DataFrame
            df_personal = pd.DataFrame(data, columns=header)
            
            # Limpiar datos
            for col in df_personal.columns:
                df_personal[col] = df_personal[col].astype(str).str.strip()
            df_personal.replace('', pd.NA, inplace=True)
            
            # ===== HOJA USUARIOS =====
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
            
            # ===== HOJA PROPUESTAS =====
            try:
                ws_propuestas = sh.worksheet("Propuestas")
                propuestas_data = ws_propuestas.get_all_values()
                if len(propuestas_data) > 1:
                    header_prop = [str(col).strip().upper() for col in propuestas_data[0]]
                    prop_data = propuestas_data[1:]
                    df_propuestas = pd.DataFrame(prop_data, columns=header_prop)
                else:
                    df_propuestas = pd.DataFrame(columns=['ID', 'FECHA', 'USUARIO_DNI', 'USUARIO_NOMBRE', 'DEPENDENCIA', 'ACCION', 'DATOS_ORIGINALES', 'DATOS_NUEVOS', 'ESTADO'])
            except gspread.exceptions.WorksheetNotFound:
                df_propuestas = pd.DataFrame(columns=['ID', 'FECHA', 'USUARIO_DNI', 'USUARIO_NOMBRE', 'DEPENDENCIA', 'ACCION', 'DATOS_ORIGINALES', 'DATOS_NUEVOS', 'ESTADO'])
                ws_propuestas = sh.add_worksheet(title="Propuestas", rows=1000, cols=20)
                ws_propuestas.update([df_propuestas.columns.tolist()])
            
            return df_personal, df_usuarios, df_propuestas
            
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            st.stop()

# ========== FUNCIÓN PARA GUARDAR PROPUESTAS ==========
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
    except Exception as e:
        st.error(f"Error al guardar propuesta: {e}")
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
            # Buscar columna DNI para identificar
            col_dni = header.index('DNI') if 'DNI' in header else None
            if col_dni is not None:
                # Verificar si ya existe
                dnis_existentes = [row[col_dni] if len(row) > col_dni else '' for row in all_data[1:]]
                if datos_nuevos.get('DNI') in dnis_existentes:
                    st.warning("⚠️ El DNI ya existe en la base de datos")
                    return False
            
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
        
        # Marcar como aprobada
        propuestas_df.loc[propuestas_df['ID'] == str(id_propuesta), 'ESTADO'] = 'APROBADO'
        ws_propuestas.clear()
        ws_propuestas.update([propuestas_df.columns.tolist()] + propuestas_df.values.tolist())
        
        # Recargar datos
        st.session_state.df_personal, st.session_state.df_usuarios, st.session_state.df_propuestas = cargar_datos_hoja()
        return True
    except Exception as e:
        st.error(f"Error al aprobar propuesta: {e}")
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
    except Exception as e:
        st.error(f"Error al rechazar propuesta: {e}")
        return False

# ========== CARGA INICIAL ==========
if 'df_personal' not in st.session_state:
    resultado = cargar_datos_hoja()
    st.session_state.df_personal = resultado[0]
    st.session_state.df_usuarios = resultado[1]
    st.session_state.df_propuestas = resultado[2]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'filtros' not in st.session_state:
    st.session_state.filtros = {}
if 'propuesta_rotacion' not in st.session_state:
    st.session_state.propuesta_rotacion = None

# ========== LOGIN ==========
if not st.session_state.logged_in:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("👮‍♂️ Sistema de Gestión de Personal")
        st.markdown("### Iniciar Sesión")
        dni_input = st.text_input("📄 DNI", placeholder="Ingrese su número de documento")
        clave_input = st.text_input("🔒 Clave", type="password", placeholder="Ingrese su contraseña")
        if st.button("🚪 Ingresar", type="primary", use_container_width=True):
            if dni_input and clave_input:
                usuario = st.session_state.df_usuarios[
                    (st.session_state.df_usuarios['DNI'].astype(str).str.lower() == dni_input.lower()) &
                    (st.session_state.df_usuarios['CLAVE'].astype(str).str.lower() == clave_input.lower())
                ]
                if not usuario.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_data = usuario.iloc[0]
                    st.rerun()
                else:
                    st.error("❌ DNI o Clave incorrectos")
            else:
                st.warning("⚠️ Por favor, complete DNI y Clave")
    with col2:
        st.markdown("### ℹ️ Información")
        st.info("""
        **Sistema de Gestión de Personal**
        
        - 🔐 Acceso restringido a personal autorizado
        - 🔄 Gestión de rotaciones por jerarquía
        - 📎 Exportación de datos
        - 📊 Resúmenes estadísticos
        
        ---
        *Si no posee credenciales, contacte al administrador.*
        """)
else:
    user = st.session_state.user_data
    
    # ========== SIDEBAR ==========
    with st.sidebar:
        st.markdown("### 👤 Panel de Usuario")
        st.markdown("---")
        st.markdown(f"**Nombre:** {user['NOMBRE']}")
        st.markdown(f"**📄 DNI:** {user['DNI']}")
        st.markdown(f"**🏢 Dependencia:** {user['DEPENDENCIA']}")
        st.markdown(f"**⭐ Jerarquía:** {user['JERARQUÍA']}")
        st.markdown("---")
        
        if st.button("🔄 REFRESCAR DATOS", use_container_width=True):
            with st.spinner("Actualizando datos..."):
                resultado = cargar_datos_hoja()
                st.session_state.df_personal = resultado[0]
                st.session_state.df_usuarios = resultado[1]
                st.session_state.df_propuestas = resultado[2]
                st.success("✅ Datos actualizados correctamente")
                time.sleep(1)
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # ========== TÍTULO PRINCIPAL ==========
    st.title("👮‍♂️ Sistema de Gestión de Personal")
    st.caption(f"📅 Última actualización: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # ========== ADMINISTRADOR ==========
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
            st.warning(f"⚠️ **¡ATENCIÓN!** Hay {propuestas_pendientes} propuestas de cambio pendientes de revisar.", icon="⚠️")
            
            with st.expander(f"📋 Ver {propuestas_pendientes} propuestas pendientes", expanded=True):
                for idx, prop in st.session_state.df_propuestas.iterrows():
                    def get_col_value(row, posibles):
                        for p in posibles:
                            if p in row.index:
                                return row[p]
                        return "No disponible"
                    
                    prop_id = get_col_value(prop, ['ID', 'id'])
                    prop_fecha = get_col_value(prop, ['FECHA', 'Fecha'])
                    prop_usuario_nombre = get_col_value(prop, ['USUARIO_NOMBRE', 'Usuario_Nombre'])
                    prop_usuario_dni = get_col_value(prop, ['USUARIO_DNI', 'Usuario_DNI'])
                    prop_dependencia = get_col_value(prop, ['DEPENDENCIA', 'Dependencia'])
                    prop_accion = get_col_value(prop, ['ACCION', 'Accion'])
                    prop_estado = get_col_value(prop, ['ESTADO', 'Estado'])
                    
                    if prop_estado.upper() != 'PENDIENTE':
                        continue
                    
                    st.markdown(f"### 📋 Propuesta #{prop_id}")
                    st.markdown(f"**Fecha:** {prop_fecha}")
                    st.markdown(f"**Usuario:** {prop_usuario_nombre} (DNI: {prop_usuario_dni})")
                    st.markdown(f"**Dependencia:** {prop_dependencia}")
                    st.markdown(f"**Acción:** {prop_accion}")
                    
                    if prop_accion == 'MODIFICAR':
                        datos_originales_col = None
                        datos_nuevos_col = None
                        for col in prop.index:
                            if 'DATOS_ORIGINALES' in col.upper():
                                datos_originales_col = col
                            if 'DATOS_NUEVOS' in col.upper():
                                datos_nuevos_col = col
                        
                        if datos_originales_col and datos_nuevos_col:
                            try:
                                datos_originales = json.loads(prop[datos_originales_col])
                                datos_nuevos = json.loads(prop[datos_nuevos_col])
                                
                                st.markdown("#### 🔄 Cambios propuestos:")
                                cambios = []
                                todas_columnas = set(datos_originales.keys()) | set(datos_nuevos.keys())
                                for columna in todas_columnas:
                                    original = datos_originales.get(columna, '')
                                    nuevo = datos_nuevos.get(columna, '')
                                    if str(original) != str(nuevo):
                                        cambios.append({
                                            'Campo': columna,
                                            'Valor actual': original if original and str(original) != 'nan' else '(vacío)',
                                            'Valor propuesto': nuevo if nuevo and str(nuevo) != 'nan' else '(vacío)'
                                        })
                                
                                if cambios:
                                    st.table(pd.DataFrame(cambios))
                                else:
                                    st.info("No se detectaron cambios visibles.")
                                
                                with st.expander("Ver JSON completo"):
                                    st.json({"Original": datos_originales, "Nuevo": datos_nuevos})
                            except Exception as e:
                                st.error(f"Error al procesar datos: {e}")
                    
                    elif prop_accion == 'AGREGAR':
                        datos_nuevos_col = None
                        for col in prop.index:
                            if 'DATOS_NUEVOS' in col.upper():
                                datos_nuevos_col = col
                                break
                        if datos_nuevos_col:
                            try:
                                datos_nuevos = json.loads(prop[datos_nuevos_col])
                                st.markdown("#### ➕ Nuevo agente a agregar:")
                                st.json(datos_nuevos)
                            except:
                                st.write("Datos:", prop[datos_nuevos_col])
                    
                    elif prop_accion == 'ELIMINAR':
                        datos_originales_col = None
                        for col in prop.index:
                            if 'DATOS_ORIGINALES' in col.upper():
                                datos_originales_col = col
                                break
                        if datos_originales_col:
                            try:
                                datos_originales = json.loads(prop[datos_originales_col])
                                st.markdown("#### ➖ Agente a eliminar:")
                                st.json(datos_originales)
                            except:
                                st.write("Datos:", prop[datos_originales_col])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Aprobar #{prop_id}", key=f"aprobar_{prop_id}", use_container_width=True):
                            if aprobar_propuesta(prop_id):
                                st.success(f"✅ Propuesta #{prop_id} aprobada")
                                st.rerun()
                            else:
                                st.error("❌ Error al aprobar")
                    with col2:
                        if st.button(f"❌ Rechazar #{prop_id}", key=f"rechazar_{prop_id}", use_container_width=True):
                            if rechazar_propuesta(prop_id):
                                st.success(f"❌ Propuesta #{prop_id} rechazada")
                                st.rerun()
                            else:
                                st.error("❌ Error al rechazar")
                    
                    st.markdown("---")
        else:
            st.info("✅ No hay propuestas de cambio pendientes.")
    
    # ========== CARGAR DATOS SEGÚN ROL ==========
    if es_admin:
        datos_completos = st.session_state.df_personal.copy()
        st.success("👑 **Modo Administrador** - Visualizando todo el personal", icon="👑")
        
        # Métricas
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("📊 Total Personal", len(datos_completos))
        with col_m2:
            deps = datos_completos['DEPENDENCIA'].nunique() if 'DEPENDENCIA' in datos_completos else 0
            st.metric("🏢 Dependencias", deps)
        with col_m3:
            jer = datos_completos['JERARQUÍA'].nunique() if 'JERARQUÍA' in datos_completos else 0
            st.metric("⭐ Jerarquías", jer)
        with col_m4:
            func = datos_completos['FUNCIÓN'].nunique() if 'FUNCIÓN' in datos_completos else 0
            st.metric("📋 Funciones", func)
    else:
        datos_completos = st.session_state.df_personal[
            st.session_state.df_personal['DEPENDENCIA'].astype(str).str.lower() == user['DEPENDENCIA'].lower()
        ].copy()
        st.info(f"👤 **Modo Usuario** - Visualizando personal de: {user['DEPENDENCIA']}", icon="ℹ️")
    
    if len(datos_completos) == 0:
        st.warning("⚠️ No hay personal para mostrar")
        st.stop()
    
    # ========== DETECCIÓN DE COLUMNAS ==========
    def encontrar_columna(df, posibles):
        for p in posibles:
            if p in df.columns:
                return p
        return None
    
    # Columnas principales
    nombre_col = encontrar_columna(datos_completos, ['APELLIDO Y NOMBRE', 'NOMBRE', 'NOMBRE COMPLETO'])
    dni_col = encontrar_columna(datos_completos, ['DNI', 'Dni', 'dni'])
    jerarquia_col = encontrar_columna(datos_completos, ['JERARQUÍA', 'Jerarquia', 'JERARQUIA', 'RANGO'])
    funcion_col = encontrar_columna(datos_completos, ['FUNCIÓN', 'Funcion', 'FUNCION', 'CARGO'])
    dependencia_col = encontrar_columna(datos_completos, ['DEPENDENCIA', 'Dependencia', 'DEPARTAMENTO'])
    sexo_col = encontrar_columna(datos_completos, ['SEXO', 'GENERO', 'GÉNERO', 'Sexo'])
    
    if not nombre_col or not jerarquia_col or not funcion_col or not dependencia_col:
        st.error("❌ Faltan columnas esenciales en la hoja de datos")
        st.stop()
    
    # ========== FILTROS ==========
    st.markdown("## 🔎 Filtros de Búsqueda")
    col1, col2, col3 = st.columns(3)
    
    # Obtener opciones únicas
    opciones_dependencia = sorted(datos_completos[dependencia_col].dropna().unique())
    opciones_jerarquia = sorted(datos_completos[jerarquia_col].dropna().unique())
    opciones_funcion = sorted(datos_completos[funcion_col].dropna().unique())
    
    with col1:
        dep_filter = st.multiselect("🏢 Dependencia", opciones_dependencia)
    with col2:
        jer_filter = st.multiselect("⭐ Jerarquía", opciones_jerarquia)
    with col3:
        fun_filter = st.multiselect("📋 Función", opciones_funcion)
    
    # Aplicar filtros
    datos_filtrados = datos_completos.copy()
    if dep_filter:
        datos_filtrados = datos_filtrados[datos_filtrados[dependencia_col].isin(dep_filter)]
    if jer_filter:
        datos_filtrados = datos_filtrados[datos_filtrados[jerarquia_col].isin(jer_filter)]
    if fun_filter:
        datos_filtrados = datos_filtrados[datos_filtrados[funcion_col].isin(fun_filter)]
    
    # Búsqueda rápida
    busqueda = st.text_input("🔍 Búsqueda rápida", placeholder="Nombre, DNI, dependencia...")
    if busqueda:
        mascara = datos_filtrados.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
        datos_filtrados = datos_filtrados[mascara]
        st.info(f"📌 {len(datos_filtrados)} resultados encontrados")
    
    # ========== GRÁFICOS (SOLO ADMIN) ==========
    if es_admin and len(datos_filtrados) > 0:
        st.markdown("## 📊 Análisis Visual de Personal")
        
        tab1, tab2 = st.tabs(["📊 Distribución", "⭐ Jerarquías"])
        
        with tab1:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### 🏆 Top 15 Dependencias")
                top_deps = datos_filtrados[dependencia_col].value_counts().head(15)
                if len(top_deps) > 0:
                    fig_bar = px.bar(
                        x=top_deps.values, 
                        y=top_deps.index,
                        orientation='h',
                        title="Cantidad de personal por dependencia",
                        labels={'x': 'Cantidad', 'y': 'Dependencia'},
                        color=top_deps.values,
                        color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(height=500, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_chart2:
                st.markdown("#### 🥧 Distribución porcentual")
                dep_counts = datos_filtrados[dependencia_col].value_counts()
                if len(dep_counts) > 0:
                    if len(dep_counts) > 15:
                        otros = dep_counts[15:].sum()
                        dep_counts = dep_counts[:15]
                        dep_counts['Otras dependencias'] = otros
                    fig_pie = px.pie(
                        values=dep_counts.values, 
                        names=dep_counts.index,
                        title="Porcentaje de personal por dependencia",
                        hole=0.3,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(height=450)
                    st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab2:
            st.markdown("#### 📊 Distribución por Jerarquía")
            jer_counts = datos_filtrados[jerarquia_col].value_counts()
            if len(jer_counts) > 0:
                fig_jer = px.bar(
                    x=jer_counts.values, 
                    y=jer_counts.index,
                    orientation='h',
                    title="Cantidad de personal por jerarquía",
                    labels={'x': 'Cantidad', 'y': 'Jerarquía'},
                    color=jer_counts.values,
                    color_continuous_scale='Greens'
                )
                fig_jer.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_jer, use_container_width=True)
    
    # ========== LISTADO DEL PERSONAL ==========
    st.markdown(f"## 📋 Listado detallado del personal")
    st.caption(f"Total de registros: {len(datos_filtrados)}")
    
    if len(datos_filtrados) > 0:
        # Columnas a mostrar (excluir algunas que no son necesarias)
        columnas_excluir = ['N°', 'N', 'Numero', 'Legajo']
        columnas_a_mostrar = [c for c in datos_filtrados.columns if c not in columnas_excluir]
        
        if es_admin:
            # Admin: visualización completa
            for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
                with st.container():
                    st.markdown(f"### 🏢 {dependencia}")
                    st.dataframe(grupo[columnas_a_mostrar], use_container_width=True, hide_index=True)
                    st.markdown("---")
        else:
            # Usuario: puede editar
            for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
                with st.container():
                    st.markdown(f"### 🏢 {dependencia}")
                    
                    edited_df = st.data_editor(
                        grupo[columnas_a_mostrar],
                        use_container_width=True,
                        hide_index=True,
                        num_rows="dynamic",
                        key=f"editor_{dependencia}"
                    )
                    
                    if st.button(f"📨 Enviar propuesta de cambios para {dependencia}", key=f"propuesta_{dependencia}"):
                        cambios_detectados = False
                        
                        # Verificar agregados
                        if len(edited_df) > len(grupo):
                            nuevas_filas = edited_df.iloc[len(grupo):]
                            for _, nueva_fila in nuevas_filas.iterrows():
                                datos_nuevos = nueva_fila.to_dict()
                                # Asegurar que tenga DNI
                                if 'DNI' in datos_nuevos and datos_nuevos['DNI']:
                                    if guardar_propuesta(
                                        user['DNI'], user['NOMBRE'], dependencia, 
                                        "AGREGAR", {}, datos_nuevos
                                    ):
                                        cambios_detectados = True
                        
                        # Verificar modificaciones
                        for idx, (_, original_row) in enumerate(grupo.iterrows()):
                            if idx < len(edited_df):
                                edited_row = edited_df.iloc[idx]
                                if not original_row[columnas_a_mostrar].equals(edited_row[columnas_a_mostrar]):
                                    datos_originales = original_row[columnas_a_mostrar].to_dict()
                                    datos_nuevos = edited_row.to_dict()
                                    if guardar_propuesta(
                                        user['DNI'], user['NOMBRE'], dependencia,
                                        "MODIFICAR", datos_originales, datos_nuevos
                                    ):
                                        cambios_detectados = True
                        
                        if cambios_detectados:
                            st.success("✅ Propuesta enviada correctamente. El administrador la revisará.")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.info("ℹ️ No se detectaron cambios para enviar.")
                    
                    st.markdown("---")
    else:
        st.warning("⚠️ No hay datos con los filtros seleccionados")
    
    # ========== EXPORTAR ==========
    st.markdown("---")
    st.markdown("## 📎 Exportar datos")
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if OPENPYXL_AVAILABLE:
            formato = st.radio("Formato:", ["CSV", "Excel (XLSX)"], horizontal=True)
        else:
            formato = "CSV"
            st.caption("💡 Para exportar a Excel, instale openpyxl")
    with col_export2:
        if st.button("📥 Exportar listado", use_container_width=True):
            if len(datos_filtrados) == 0:
                st.warning("⚠️ No hay datos para exportar")
            else:
                nombre_base = f"personal_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if formato == "CSV":
                    csv = datos_filtrados.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("✅ Descargar CSV", csv, f"{nombre_base}.csv", mime="text/csv")
                elif OPENPYXL_AVAILABLE:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        datos_filtrados.to_excel(writer, sheet_name='Personal', index=False)
                        workbook = writer.book
                        hoja = writer.sheets['Personal']
                        for col in hoja.columns:
                            max_len = 0
                            col_letter = get_column_letter(col[0].column)
                            for cell in col:
                                try:
                                    max_len = max(max_len, len(str(cell.value)))
                                except:
                                    pass
                            hoja.column_dimensions[col_letter].width = min(max_len + 2, 50)
                        for celda in hoja[1]:
                            celda.font = Font(bold=True)
                            celda.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
                            celda.alignment = Alignment(horizontal='center')
                    st.download_button("✅ Descargar Excel", output.getvalue(), f"{nombre_base}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.markdown(
        "<div class='footer'>"
        "© 2024 - Sistema de Gestión de Personal | Desarrollado para la Fuerza Policial | Versión 3.0"
        "</div>", 
        unsafe_allow_html=True
    )