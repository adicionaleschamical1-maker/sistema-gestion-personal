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
    
    # ===== INICIALES PARA AVATAR =====
    palabras = nombre.split()
    if len(palabras) >= 2:
        iniciales = palabras[0][0] + palabras[1][0]
    else:
        iniciales = nombre[:2].upper() if nombre else '??'
    
    # ===== TARJETA CON DISEÑO MEJORADO =====
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
        <div style="display: flex; align-items: center; gap: 25px; margin: 10px 0 25px 0; flex-wrap: wrap; padding-top: 10px;">
            <div style="background: linear-gradient(135deg, #2ecc71, #27ae60);
                        width: 90px;
                        height: 90px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 36px;
                        font-weight: 700;
                        color: white;
                        box-shadow: 0 6px 25px rgba(46,204,113,0.35);
                        flex-shrink: 0;
                        border: 3px solid rgba(255,255,255,0.8);">
                {iniciales}
            </div>
            <div style="flex: 1;">
                <h2 style="color: #1f3a6b; margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.5px;">{nombre}</h2>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px;">
                    <span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; color: white; background: #2c3e50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">🔑 DNI: {dni}</span>
                    <span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; color: white; background: #3498db; box-shadow: 0 2px 8px rgba(52,152,219,0.2);">⭐ Jerarquía: {jerarquia}</span>
                    <span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; color: white; background: #e67e22; box-shadow: 0 2px 8px rgba(230,126,34,0.2);">📋 Función: {funcion}</span>
                    <span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; color: white; background: #8e44ad; box-shadow: 0 2px 8px rgba(142,68,173,0.2);">🏢 Dependencia: {dependencia}</span>
                    {f'<span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; color: white; background: #e74c3c; box-shadow: 0 2px 8px rgba(231,76,60,0.2);">🚻 Sexo: {sexo}</span>' if sexo and sexo != 'N/A' else ''}
                </div>
            </div>
        </div>
        
        <!-- Datos en formato lista vertical -->
        <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 15px; padding-top: 15px; border-top: 2px solid #f0f2f5;">
    """, unsafe_allow_html=True)
    
    # Datos principales en formato lista vertical
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
                elif "OBS" in col:
                    icono = "📝"
                
                st.markdown(f"""
                    <div style="display: flex; 
                                padding: 10px 18px; 
                                background: #f8fafc;
                                border-radius: 12px;
                                align-items: center;
                                border-left: 4px solid #2ecc71;
                                transition: all 0.2s ease;">
                        <span style="font-weight: 600; 
                                    color: #1f3a6b; 
                                    width: 200px; 
                                    flex-shrink: 0; 
                                    font-size: 0.85rem;">
                            {icono} {etiqueta}:
                        </span>
                        <span style="color: #1a202c; 
                                    font-weight: 500; 
                                    font-size: 0.95rem;">
                            {valor}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Columnas extra
    for col in columnas_extra:
        valor = row.get(col, '')
        if valor and str(valor) != 'nan':
            etiqueta = col.replace('_', ' ').title()
            st.markdown(f"""
                <div style="display: flex; 
                            padding: 10px 18px; 
                            background: #f8fafc;
                            border-radius: 12px;
                            align-items: center;
                            border-left: 4px solid #8e44ad;
                            transition: all 0.2s ease;">
                    <span style="font-weight: 600; 
                                color: #1f3a6b; 
                                width: 200px; 
                                flex-shrink: 0; 
                                font-size: 0.85rem;">
                        📌 {etiqueta}:
                    </span>
                    <span style="color: #1a202c; 
                                font-weight: 500; 
                                font-size: 0.95rem;">
                        {valor}
                    </span>
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
