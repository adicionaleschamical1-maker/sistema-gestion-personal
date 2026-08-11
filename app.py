# ========== LISTADO CON CHECKBOX NATIVOS DE STREAMLIT ==========
st.markdown(f"## 📋 Listado del personal")
st.caption(f"Total de registros: {len(datos_filtrados)}")

if len(datos_filtrados) > 0:
    columnas_excluir = ['N°', 'N', 'Numero', 'Legajo']
    columnas_a_mostrar = [c for c in datos_filtrados.columns if c not in columnas_excluir]
    
    for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
        with st.container():
            st.markdown(f"### 🏢 {dependencia}")
            
            # Crear un dataframe con una columna para checkboxes
            grupo_mostrar = grupo[columnas_a_mostrar].copy()
            
            # Añadir columna de selección
            grupo_mostrar.insert(0, 'Seleccionar', False)
            
            # Mostrar el dataframe con checkboxes nativos
            edited_df = st.data_editor(
                grupo_mostrar,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Seleccionar": st.column_config.CheckboxColumn(
                        "👤 Ver ficha",
                        help="Marcar para ver la ficha completa del efectivo",
                        default=False
                    )
                },
                key=f"selector_{dependencia}"
            )
            
            # Procesar la selección
            for idx, row in edited_df.iterrows():
                if row['Seleccionar']:
                    # Buscar la fila original en el grupo
                    fila_original = grupo.iloc[idx]
                    st.markdown("---")
                    mostrar_tarjeta_efectivo(fila_original, 'APELLIDO Y NOMBRE', 'DNI')
                    st.markdown("---")
                    break  # Solo mostrar una tarjeta a la vez
            
            # ===== EDITOR DE DATOS (SOLO USUARIOS COMUNES) =====
            if not es_admin:
                st.markdown("---")
                with st.expander("✏️ Editar datos y enviar propuesta de cambios", expanded=False):
                    st.caption("Modificá los valores en la tabla y enviá la propuesta para que el administrador la revise.")
                    
                    edited_df_editor = st.data_editor(
                        grupo[columnas_a_mostrar],
                        use_container_width=True,
                        hide_index=True,
                        num_rows="dynamic",
                        key=f"editor_{dependencia}"
                    )
                    
                    if st.button(f"📨 Enviar propuesta de cambios para {dependencia}", key=f"propuesta_{dependencia}"):
                        cambios_detectados = False
                        
                        if len(edited_df_editor) > len(grupo):
                            nuevas_filas = edited_df_editor.iloc[len(grupo):]
                            for _, nueva_fila in nuevas_filas.iterrows():
                                datos_nuevos = nueva_fila.to_dict()
                                if 'DNI' in datos_nuevos and datos_nuevos['DNI']:
                                    if guardar_propuesta(
                                        user['DNI'], user['NOMBRE'], dependencia, 
                                        "AGREGAR", {}, datos_nuevos
                                    ):
                                        cambios_detectados = True
                        
                        for idx, (_, original_row) in enumerate(grupo.iterrows()):
                            if idx < len(edited_df_editor):
                                edited_row = edited_df_editor.iloc[idx]
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
                            st.success("✅ Propuesta enviada correctamente. El administrador la revisará.")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.info("ℹ️ No se detectaron cambios para enviar.")
            
            st.markdown("---")
else:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
