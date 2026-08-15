import streamlit as st
import gspread
import pandas as pd
import datetime

st.set_page_config(page_title="🔍 DIAGNÓSTICO FINAL", layout="wide")

st.title("🔍 DIAGNÓSTICO FINAL - ¿Por qué sigue saliendo el HTML?")

try:
    creds = st.secrets["gsheets"]
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key("1TH32e7TkB4RYEKxxRhGRnnYxjkT9AF9TeuplxtYih1Y")
    
    ws_personal = sh.worksheet("Personal")
    all_values = ws_personal.get_all_values()
    
    if len(all_values) == 0:
        st.error("La hoja 'Personal' está vacía")
        st.stop()

    header = [str(col).strip().upper() for col in all_values[0]]
    data = all_values[1:]
    
    # Mostramos los primeros 3 datos para ver qué hay en las celdas
    st.subheader("📊 PASO 1: Datos crudos de las primeras 3 filas de Google Sheets")
    st.write("¿Ves el HTML `<div class='dato'>...` aquí? Si lo ves, está en Google Sheets.")
    df_preview = pd.DataFrame(data[:3], columns=header)
    st.dataframe(df_preview, use_container_width=True)

    st.subheader("🧐 PASO 2: Búsqueda de HTML en columnas específicas")
    columnas_con_html = []
    for col in header:
        for i, row in enumerate(data):
            if '<' in str(row[header.index(col)]):
                columnas_con_html.append(col)
                st.error(f"❌ ¡ENCONTRADO! La columna **'{col}'** tiene HTML en la fila {i+1}")
                st.code(str(row[header.index(col)])[:200], language="html")
                break
        else:
            st.success(f"✅ La columna '{col}' parece limpia.")
    
    if columnas_con_html:
        st.error(f"⚠️ Conclusión: El HTML está guardado en la/s columna/s: {list(set(columnas_con_html))}. No es un error de código, es un error de datos en Google Sheets.")
    else:
        st.success("🎉 Los datos de Google Sheets están 100% limpios. No hay HTML guardado.")
        st.error("🔥 Conclusión EXTRAÑA: Si los datos están limpios, entonces el HTML se está generando en el código (probablemente en la función `mostrar_tarjeta_efectivo`).")

    st.subheader("🔎 PASO 3: Inspección del código actual")
    with open(__file__, 'r', encoding='utf-8') as f:
        code = f.read()

    if "st.write(html)" in code:
        st.error("❌ ¡ENCONTRADO! El código tiene `st.write(html)`.")
        st.code("# Busca y ELIMINA esta línea en tu archivo", language="python")
    elif "st.write(mostrar_tarjeta_efectivo" in code:
        st.error("❌ ¡ENCONTRADO! El código tiene `st.write(mostrar_tarjeta_efectivo(...))`.")
        st.code("# Busca y ELIMINA esta línea en tu archivo", language="python")
    else:
        st.success("✅ No se encontraron llamadas a `st.write` con HTML.")
        st.warning("⚠️ Si los datos están limpios y no hay `st.write`, el error podría ser un `print(html)` o un `return html` mal usado.")

except Exception as e:
    st.error(f"Error: {e}")

st.info("💡 ¿Qué hacer ahora? Mira el PASO 2. Si el PASO 2 dice que la columna tiene HTML, tendremos que limpiarla. Si el PASO 2 dice que está limpia, entonces el error está en tu código.")
