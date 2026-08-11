    # ========== LISTADO ==========
    st.markdown("## 📋 Listado del personal")
    st.caption(f"Total de registros: {len(datos_filtrados)}")
    
    if len(datos_filtrados) > 0:
        columnas_excluir = ['N°', 'N', 'Numero', 'Legajo']
        columnas_a_mostrar = [c for c in datos_filtrados.columns if c not in columnas_excluir]
        
        # ===== LISTADO EDITABLE (PRIORIDAD 1) =====
        for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
            with st.container():
                # Título de la dependencia con ícono
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1f3a6b 0%, #2c5a8c 100%); 
                            padding: 12px 20px; 
                            border-radius: 10px; 
                            margin: 10px 0 15px 0;
                            color: white;
                            font-weight: 600;
                            font-size: 1.2rem;">
                    🏢 {dependencia}
                </div>
                """, unsafe_allow_html=True)
                
                if es_admin:
                    # Admin: solo visualización
                    st.info("👑 **Modo Administrador** - Visualización de datos (solo lectura)")
                    st.dataframe(grupo[columnas_a_mostrar], use_container_width=True, hide_index=True)
                else:
                    # Usuario: editor con propuestas
                    st.markdown("""
                    <div style="background: #e8f5e9; 
                                padding: 15px 20px; 
                                border-radius: 10px; 
                                border-left: 5px solid #2ecc71;
                                margin-bottom: 15px;">
                        <strong>✏️ ¿Qué podés hacer aquí?</strong><br>
                        • <strong>Modificar</strong> cualquier campo de la tabla haciendo clic en la celda<br>
                        • <strong>Agregar</strong> nuevos efectivos usando la última fila (botón "+")<br>
                        • <strong>Eliminar</strong> filas usando el botón "🗑️" en cada fila<br>
                        • <strong>Enviar</strong> los cambios para que el administrador los revise
                    </div>
                    """, unsafe_allow_html=True)
                    
                    edited_df = st.data_editor(
                        grupo[columnas_a_mostrar],
                        use_container_width=True,
                        hide_index=True,
                        num_rows="dynamic",
                        key=f"editor_{dependencia}"
                    )
                    
                    # Botón de envío más visible
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        if st.button(f"📨 ENVIAR PROPUESTA DE CAMBIOS PARA {dependencia}", 
                                    key=f"propuesta_{dependencia}", 
                                    type="primary",
                                    use_container_width=True):
                            cambios_detectados = False
                            
                            # Verificar agregados (nuevas filas)
                            if len(edited_df) > len(grupo):
                                nuevas_filas = edited_df.iloc[len(grupo):]
                                for _, nueva_fila in nuevas_filas.iterrows():
                                    datos_nuevos = nueva_fila.to_dict()
                                    if 'DNI' in datos_nuevos and datos_nuevos['DNI']:
                                        if guardar_propuesta(
                                            user['DNI'], user['NOMBRE'], dependencia, 
                                            "AGREGAR", {}, datos_nuevos
                                        ):
                                            cambios_detectados = True
                            
                            # Verificar modificaciones (cambios en filas existentes)
                            for idx_editor in range(min(len(grupo), len(edited_df))):
                                original_row = grupo.iloc[idx_editor]
                                edited_row = edited_df.iloc[idx_editor]
                                
                                if not original_row[columnas_a_mostrar].equals(edited_row[columnas_a_mostrar]):
                                    datos_originales = {}
                                    datos_nuevos = {}
                                    for col in columnas_a_mostrar:
                                        if str(original_row[col]) != str(edited_row[col]):
                                            datos_originales[col] = original_row[col]
                                            datos_nuevos[col] = edited_row[col]
                                    
                                    if datos_originales:
                                        if guardar_propuesta(
                                            user['DNI'], user['NOMBRE'], dependencia,
                                            "MODIFICAR", datos_originales, datos_nuevos
                                        ):
                                            cambios_detectados = True
                            
                            if cambios_detectados:
                                st.success("✅ ¡Propuesta enviada correctamente! El administrador la revisará.")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.info("ℹ️ No se detectaron cambios para enviar.")
                    
                    # Mensaje informativo después del botón
                    st.caption("💡 Los cambios no se aplican automáticamente. Un administrador debe aprobarlos.")
                
                st.markdown("---")
        
        # ===== BOTÓN PARA VER TARJETAS (PRIORIDAD 2 - OCULTO) =====
        st.markdown("---")
        
        # Título llamativo para la sección de tarjetas
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%); 
                    padding: 15px 25px; 
                    border-radius: 10px; 
                    margin: 20px 0 15px 0;
                    color: white;
                    font-weight: 600;
                    font-size: 1.3rem;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    flex-wrap: wrap;">
            <span>👤 VER FICHA PERSONAL DE UN EFECTIVO</span>
            <span style="font-size: 0.8rem; font-weight: 400; opacity: 0.9;">
                📌 Hacé clic para expandir y seleccionar un efectivo
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 Hacé clic aquí para ver la ficha completa de un efectivo", expanded=False):
            st.markdown("""
            <div style="background: #f3e5f5; 
                        padding: 15px 20px; 
                        border-radius: 10px; 
                        border-left: 5px solid #8e44ad;
                        margin-bottom: 15px;">
                <strong>👤 ¿Qué podés hacer aquí?</strong><br>
                • <strong>Seleccionar</strong> un efectivo de la lista marcando el checkbox<br>
                • <strong>Ver</strong> todos sus datos personales en formato de tarjeta<br>
                • <strong>Información</strong> completa: DNI, jerarquía, función, dependencia, etc.
            </div>
            """, unsafe_allow_html=True)
            
            for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
                with st.container():
                    st.markdown(f"""
                    <div style="background: #e8eaf6; 
                                padding: 8px 15px; 
                                border-radius: 8px; 
                                margin: 10px 0;
                                font-weight: 600;
                                color: #1f3a6b;">
                        🏢 {dependencia}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, row in grupo.iterrows():
                        nombre = row.get('APELLIDO Y NOMBRE', 'Sin nombre')
                        dni = row.get('DNI', '') if dni_col else ''
                        jerarquia = row.get('JERARQUÍA', '')
                        funcion = row.get('FUNCIÓN', '')
                        
                        # Etiqueta más informativa
                        label = f"👤 {nombre}"
                        if dni:
                            label += f" (DNI: {dni})"
                        if jerarquia:
                            label += f" - ⭐ {jerarquia}"
                        if funcion:
                            label += f" - 📋 {funcion}"
                        
                        key = f"ver_{idx}_{dependencia}"
                        mostrar = st.checkbox(label, key=key, value=False)
                        
                        if mostrar:
                            st.markdown("---")
                            st.markdown("""
                            <div style="background: #e8f5e9; 
                                        padding: 5px 15px; 
                                        border-radius: 8px; 
                                        margin-bottom: 10px;
                                        font-weight: 500;
                                        color: #2e7d32;">
                                📌 Mostrando ficha completa del efectivo seleccionado
                            </div>
                            """, unsafe_allow_html=True)
                            mostrar_tarjeta_efectivo(row, 'APELLIDO Y NOMBRE', 'DNI')
                            st.markdown("---")
                    
                    st.markdown("---")
    else:
        st.warning("⚠️ No hay datos con los filtros seleccionados")
