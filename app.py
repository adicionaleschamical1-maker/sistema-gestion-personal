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
    
    # ===== TARJETA CON NUEVO DISEÑO =====
    # Iniciales para el avatar
    iniciales = ''.join([p[0] for p in nombre.split()[:2]]) if nombre else '??'
    
    st.markdown(f"""
    <div style="background: #ffffff;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.08);
                border: 1px solid #eef2f7;
                margin: 20px 0;
                position: relative;
                overflow: hidden;">
        
        <!-- Banda decorativa superior -->
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 6px; background: linear-gradient(90deg, #2ecc71, #3498db, #8e44ad);"></div>
        
        <!-- Encabezado con avatar -->
        <div style="display: flex; align-items: center; gap: 20px; margin: 10px 0 25px 0; flex-wrap: wrap; padding-top: 10px;">
            <div style="background: linear-gradient(135deg, #2ecc71, #27ae60);
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 32px;
                        font-weight: 700;
                        color: white;
                        box-shadow: 0 4px 15px rgba(46,204,113,0.3);
                        flex-shrink: 0;">
                {iniciales}
            </div>
            <div>
                <h2 style="color: #1f3a6b; margin: 0; font-size: 1.8rem; font-weight: 700;">{nombre}</h2>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px;">
                    <span style="display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #2c3e50;">🔑 {dni}</span>
                    <span style="display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #3498db;">⭐ {jerarquia}</span>
                    <span style="display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #e67e22;">📋 {funcion}</span>
                    <span style="display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #8e44ad;">🏢 {dependencia}</span>
                    {f'<span style="display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: white; background: #e74c3c;">🚻 {sexo}</span>' if sexo and sexo != 'N/A' else ''}
                </div>
            </div>
        </div>
        
        <!-- Grid de datos -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px 40px; margin-top: 20px;">
    """, unsafe_allow_html=True)
    
    # Datos principales en dos columnas
    for col in columnas_ordenadas:
        if col in row.index:
            valor = row.get(col, '')
            if valor and str(valor) != 'nan':
                if col in ['APELLIDO Y NOMBRE', 'DNI', 'JERARQUÍA', 'FUNCIÓN', 'DEPENDENCIA', 'SEXO']:
                    continue
                etiqueta = col.replace('_', ' ').title()
                # Iconos según el campo
                icono = "📌"
                if "TELEFONO" in col or "TELÉFONO" in col:
                    icono = "📞"
                elif "DOMICILIO" in col:
                    icono = "📍"
                elif "FECHA" in col and "NACIMIENTO" in col:
                    icono = "🎂"
                elif "EDAD" in col:
                    icono = "📅"
                elif "ARMA" in col:
                    icono = "🔫"
                elif "SANGUINEO" in col:
                    icono = "🩸"
                elif "LICENCIA" in col:
                    icono = "📋"
                elif "ANTIGUEDAD" in col:
                    icono = "⏳"
                
                st.markdown(f"""
                    <div style="display: flex; padding: 8px 0; border-bottom: 1px solid #f7f9fc;">
                        <span style="font-weight: 600; color: #4a5568; width: 160px; flex-shrink: 0; font-size: 0.85rem;">{icono} {etiqueta}:</span>
                        <span style="color: #1a202c; font-weight: 500; font-size: 0.9rem;">{valor}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Columnas extra
    columnas_extra = [c for c in row.index if c not in columnas_ordenadas and c not in ['N°', 'N', 'Numero', 'Legajo']]
    for col in columnas_extra:
        valor = row.get(col, '')
        if valor and str(valor) != 'nan':
            etiqueta = col.replace('_', ' ').title()
            st.markdown(f"""
                <div style="display: flex; padding: 8px 0; border-bottom: 1px solid #f7f9fc;">
                    <span style="font-weight: 600; color: #4a5568; width: 160px; flex-shrink: 0; font-size: 0.85rem;">📌 {etiqueta}:</span>
                    <span style="color: #1a202c; font-weight: 500; font-size: 0.9rem;">{valor}</span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== BOTONES DE DESCARGA =====
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px; margin: 10px 0 5px 0; padding: 10px 0; flex-wrap: wrap; border-top: 1px solid #eef2f7;">
        <span style="font-weight: 600; color: #4a5568; font-size: 0.95rem;">📥 Descargar ficha:</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        st.download_button(
            label="📄 Descargar como TXT",
            data=texto_descarga,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_download2:
        df_export = pd.DataFrame([row.to_dict()])
        csv_data = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 Descargar como CSV",
            data=csv_data,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.csv",
            mime="text/csv",
            use_container_width=True
        )
