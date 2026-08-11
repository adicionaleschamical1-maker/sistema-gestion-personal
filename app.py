def mostrar_tarjeta_efectivo(row, nombre_col, dni_col):
    """Muestra una tarjeta con la información completa de un efectivo con opción de descarga"""
    
    nombre = row.get(nombre_col, 'Sin nombre')
    dni = row.get(dni_col, 'N/A') if dni_col else 'N/A'
    jerarquia = row.get('JERARQUÍA', 'Sin jerarquía')
    funcion = row.get('FUNCIÓN', 'Sin función')
    dependencia = row.get('DEPENDENCIA', 'Sin dependencia')
    sexo = row.get('SEXO', 'N/A')
    
    # ===== CONSTRUIR TEXTO PARA DESCARGA =====
    texto_descarga = f"""
    ========================================
    FICHA PERSONAL DEL EFECTIVO
    ========================================
    
    👮‍♂️ NOMBRE: {nombre}
    🔑 DNI: {dni}
    ⭐ JERARQUÍA: {jerarquia}
    📋 FUNCIÓN: {funcion}
    🏢 DEPENDENCIA: {dependencia}
    🚻 SEXO: {sexo}
    
    ========================================
    DATOS COMPLETOS
    ========================================
    """
    
    # Agregar todas las columnas disponibles
    columnas_ordenadas = [
        'APELLIDO Y NOMBRE', 'DNI', 'JERARQUÍA', 'FUNCIÓN', 'DEPENDENCIA',
        'SEXO', 'MARCA DE ARMA', 'N° DE ARMA', 'OBS', 'SITUACION',
        'GRUPO SANGUINEO', 'N° DE TELEFONO', 'DOMICILIO REAL (DONDE VIVE)',
        'FECHA DE NACIMIENTO', 'EDAD', 'ANTIGUEDAD',
        'DIAS DE LICENCIA DISPONIBLE', 'DIAS DE LICENCIA TOMADA',
        'DIAS DE PROXIMA LICENCIA', 'LEGAJO PERSONAL', 'FECHA DE ULTIMO ASCENSO'
    ]
    
    for col in columnas_ordenadas:
        if col in row.index:
            valor = row.get(col, '')
            if valor and str(valor) != 'nan':
                etiqueta = col.replace('_', ' ').title()
                texto_descarga += f"{etiqueta}: {valor}\n"
    
    # Agregar columnas extra
    columnas_extra = [c for c in row.index if c not in columnas_ordenadas and c not in ['N°', 'N', 'Numero', 'Legajo']]
    for col in columnas_extra:
        valor = row.get(col, '')
        if valor and str(valor) != 'nan':
            etiqueta = col.replace('_', ' ').title()
            texto_descarga += f"{etiqueta}: {valor}\n"
    
    texto_descarga += """
    ========================================
    Fecha de descarga: """ + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """
    ========================================
    """
    
    # ===== MOSTRAR TARJETA CON BOTÓN DE DESCARGA =====
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                border-radius: 16px;
                padding: 25px 30px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
                border: 1px solid #e8edf3;
                margin: 15px 0 20px 0;
                position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center;
                    border-bottom: 3px solid #2ecc71; padding-bottom: 12px; margin-bottom: 18px;
                    flex-wrap: wrap; gap: 10px;">
            <h3 style="color: #1f3a6b; margin: 0; font-size: 1.5rem;">👮‍♂️ {nombre}</h3>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #2c3e50;">🔑 {dni}</span>
                <span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #3498db;">⭐ {jerarquia}</span>
                <span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #e67e22;">📋 {funcion}</span>
                <span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #8e44ad;">🏢 {dependencia}</span>
                {f'<span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #e74c3c;">🚻 {sexo}</span>' if sexo and sexo != 'N/A' else ''}
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px 40px;">
    """, unsafe_allow_html=True)
    
    for col in columnas_ordenadas:
        if col in row.index:
            valor = row.get(col, '')
            if valor and str(valor) != 'nan':
                if col in ['APELLIDO Y NOMBRE', 'DNI', 'JERARQUÍA', 'FUNCIÓN', 'DEPENDENCIA', 'SEXO']:
                    continue
                etiqueta = col.replace('_', ' ').title()
                st.markdown(f"""
                    <div style="display: flex; padding: 6px 0; border-bottom: 1px solid #f0f2f5;">
                        <span style="font-weight: 600; color: #4a5568; width: 180px; flex-shrink: 0; font-size: 0.85rem;">{etiqueta}:</span>
                        <span style="color: #1a202c; font-weight: 500; font-size: 0.9rem;">{valor}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    columnas_extra = [c for c in row.index if c not in columnas_ordenadas and c not in ['N°', 'N', 'Numero', 'Legajo']]
    for col in columnas_extra:
        valor = row.get(col, '')
        if valor and str(valor) != 'nan':
            etiqueta = col.replace('_', ' ').title()
            st.markdown(f"""
                <div style="display: flex; padding: 6px 0; border-bottom: 1px solid #f0f2f5;">
                    <span style="font-weight: 600; color: #4a5568; width: 180px; flex-shrink: 0; font-size: 0.85rem;">{etiqueta}:</span>
                    <span style="color: #1a202c; font-weight: 500; font-size: 0.9rem;">{valor}</span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== BOTONES DE DESCARGA =====
    st.markdown("""
    <div style="display: flex; gap: 10px; margin-top: 15px; padding-top: 15px; border-top: 1px solid #e8edf3; flex-wrap: wrap;">
        <span style="font-weight: 500; color: #4a5568; margin-right: 10px;">📥 Descargar ficha:</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón para descargar como TXT
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        st.download_button(
            label="📄 Descargar como TXT",
            data=texto_descarga,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Botón para descargar como CSV
    with col_download2:
        # Crear un DataFrame con una sola fila para exportar
        df_export = pd.DataFrame([row.to_dict()])
        csv_data = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 Descargar como CSV",
            data=csv_data,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
