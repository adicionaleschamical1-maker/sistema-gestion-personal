def mostrar_tarjeta_efectivo(row, nombre_col, dni_col):
    """Muestra una tarjeta tipo carnet con la información del efectivo"""
    
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
    
    # ===== TARJETA TIPO CARNET FÍSICO =====
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #ffffff, #f5f7fa);
                border-radius: 16px;
                padding: 25px 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.8);
                border: 1px solid rgba(255,255,255,0.6);
                margin: 20px 0;
                max-width: 650px;
                position: relative;">
        
        <!-- Sello decorativo -->
        <div style="position: absolute; top: 15px; right: 20px; opacity: 0.08; font-size: 60px;">👮</div>
        
        <!-- Banda superior -->
        <div style="background: linear-gradient(90deg, #1f3a6b, #2c5a8c);
                    margin: -25px -30px 20px -30px;
                    padding: 12px 30px;
                    border-radius: 16px 16px 0 0;
                    color: white;
                    font-weight: 600;
                    font-size: 0.75rem;
                    letter-spacing: 2px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;">
            <span>👮 POLICÍA DE LA PROVINCIA</span>
            <span style="font-size: 0.6rem; opacity: 0.7;">FICHA N° {dni.replace('.', '')[:6]}</span>
        </div>
        
        <!-- Encabezado con avatar -->
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
            <div style="background: linear-gradient(135deg, #1f3a6b, #2c5a8c);
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
                        flex-shrink: 0;">
                {iniciales}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #1f3a6b; line-height: 1.2;">{nombre}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                    <span style="background: #2c3e50; color: white; padding: 3px 14px; border-radius: 12px; font-size: 0.6rem; font-weight: 600;">DNI: {dni}</span>
                    <span style="background: #3498db; color: white; padding: 3px 14px; border-radius: 12px; font-size: 0.6rem; font-weight: 600;">{jerarquia}</span>
                    <span style="background: #e67e22; color: white; padding: 3px 14px; border-radius: 12px; font-size: 0.6rem; font-weight: 600;">{funcion}</span>
                    <span style="background: #8e44ad; color: white; padding: 3px 14px; border-radius: 12px; font-size: 0.6rem; font-weight: 600;">{dependencia}</span>
                    {f'<span style="background: #e74c3c; color: white; padding: 3px 14px; border-radius: 12px; font-size: 0.6rem; font-weight: 600;">{sexo}</span>' if sexo and sexo != 'N/A' else ''}
                </div>
            </div>
        </div>
        
        <!-- Línea divisoria con efecto -->
        <div style="border-top: 2px dashed #dce3ed; margin: 5px 0 15px 0;"></div>
        
        <!-- Datos en formato lista vertical -->
        <div style="display: flex; flex-direction: column; gap: 4px;">
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
                                padding: 6px 12px; 
                                background: #f8fafc;
                                border-radius: 8px;
                                align-items: center;
                                border-left: 3px solid #2ecc71;">
                        <span style="font-weight: 600; 
                                    color: #4a5568; 
                                    width: 160px; 
                                    flex-shrink: 0; 
                                    font-size: 0.78rem;">
                            {icono} {etiqueta}:
                        </span>
                        <span style="color: #1a202c; 
                                    font-weight: 500; 
                                    font-size: 0.85rem;">
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
                            padding: 6px 12px; 
                            background: #f8fafc;
                            border-radius: 8px;
                            align-items: center;
                            border-left: 3px solid #8e44ad;">
                    <span style="font-weight: 600; 
                                color: #4a5568; 
                                width: 160px; 
                                flex-shrink: 0; 
                                font-size: 0.78rem;">
                        📌 {etiqueta}:
                    </span>
                    <span style="color: #1a202c; 
                                font-weight: 500; 
                                font-size: 0.85rem;">
                        {valor}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        
        <!-- Pie de tarjeta -->
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eef2f7; display: flex; justify-content: space-between; font-size: 0.6rem; color: #a0aec0;">
            <span>📅 Emisión: """ + datetime.datetime.now().strftime('%d/%m/%Y') + """</span>
            <span>🔒 Documento oficial</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== BOTONES DE DESCARGA =====
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0; padding: 8px 0; flex-wrap: wrap; border-top: 1px solid #eef2f7;">
        <span style="font-weight: 500; color: #4a5568; font-size: 0.85rem;">📥 Descargar ficha:</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        st.download_button(
            label="📄 TXT",
            data=texto_descarga,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_download2:
        df_export = pd.DataFrame([row.to_dict()])
        csv_data = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 CSV",
            data=csv_data,
            file_name=f"ficha_{nombre.replace(' ', '_')}_{dni}.csv",
            mime="text/csv",
            use_container_width=True
        )
