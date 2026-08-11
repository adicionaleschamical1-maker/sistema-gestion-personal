    # ========== LISTADO ==========
    st.markdown(f"## 📋 Listado del personal")
    st.caption(f"Total de registros: {len(datos_filtrados)}")
    
    if len(datos_filtrados) > 0:
        columnas_excluir = ['N°', 'N', 'Numero', 'Legajo']
        columnas_a_mostrar = [c for c in datos_filtrados.columns if c not in columnas_excluir]
        
        for dependencia, grupo in datos_filtrados.groupby(dependencia_col):
            with st.container():
                st.markdown(f"### 🏢 {dependencia}")
                
                # ===== TABLA HTML CON CHECKBOX =====
                html = f"""
                <table class="tabla-unificada">
                    <thead>
                        <tr>
                            <th style="width:40px; text-align:center;">✓</th>
                            <th>APELLIDO Y NOMBRE</th>
                            <th>DNI</th>
                            <th>JERARQUÍA</th>
                            <th>FUNCIÓN</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                # Lista para guardar los datos de cada fila
                filas = []
                
                for idx, row in grupo.iterrows():
                    nombre = row.get('APELLIDO Y NOMBRE', 'Sin nombre')
                    dni = row.get('DNI', '')
                    jerarquia = row.get('JERARQUÍA', '')
                    funcion = row.get('FUNCIÓN', '')
                    
                    # ID único para este checkbox y su botón
                    checkbox_id = f"chk_{idx}_{dependencia.replace(' ', '_').replace('.', '')}"
                    btn_id = f"btn_{checkbox_id}"
                    
                    # Verificar si está marcado
                    is_checked = st.session_state.get(checkbox_id, False)
                    checked_str = "checked" if is_checked else ""
                    
                    html += f"""
                        <tr>
                            <td class="checkbox-cell">
                                <input type="checkbox" id="{checkbox_id}" 
                                       {checked_str}
                                       onchange="
                                           var btn = document.getElementById('{btn_id}');
                                           if (btn) btn.click();
                                       ">
                            </td>
                            <td class="nombre-cell">{nombre}</td>
                            <td>{dni}</td>
                            <td><span class="badge-tabla jerarquia">{jerarquia}</span></td>
                            <td><span class="badge-tabla funcion">{funcion}</span></td>
                        </tr>
                    """
                    
                    # Guardar datos de la fila para procesar después
                    filas.append({
                        'idx': idx,
                        'checkbox_id': checkbox_id,
                        'btn_id': btn_id,
                        'row': row
                    })
                
                html += """
                    </tbody>
                </table>
                """
                
                st.markdown(html, unsafe_allow_html=True)
                
                # ===== BOTONES OCULTOS PARA CADA CHECKBOX =====
                # Creamos un contenedor invisible para los botones
                with st.container():
                    for fila in filas:
                        checkbox_id = fila['checkbox_id']
                        btn_id = fila['btn_id']
                        is_checked = st.session_state.get(checkbox_id, False)
                        
                        # Botón oculto - usamos st.empty() para que no ocupe espacio
                        # El botón se dispara cuando el checkbox cambia
                        if st.button("", key=btn_id, use_container_width=False):
                            # Invertir el estado
                            st.session_state[checkbox_id] = not is_checked
                            st.rerun()
                
                # ===== MOSTRAR TARJETA DEL EFECTIVO SELECCIONADO =====
                tarjeta_mostrada = False
                for fila in filas:
                    checkbox_id = fila['checkbox_id']
                    if st.session_state.get(checkbox_id, False):
                        st.markdown("---")
                        mostrar_tarjeta_efectivo(fila['row'], 'APELLIDO Y NOMBRE', 'DNI')
                        st.markdown("---")
                        tarjeta_mostrada = True
                        break
                
                # ===== EDITOR =====
                if not es_admin:
                    st.markdown("---")
                    with st.expander("✏️ Editar datos y enviar propuesta de cambios", expanded=False):
                        st.caption("Modificá los valores en la tabla y enviá la propuesta para que el administrador la revise.")
                        
                        edited_df = st.data_editor(
                            grupo[columnas_a_mostrar],
                            use_container_width=True,
                            hide_index=True,
                            num_rows="dynamic",
                            key=f"editor_{dependencia}"
                        )
                        
                        if st.button(f"📨 Enviar propuesta de cambios para {dependencia}", key=f"propuesta_{dependencia}"):
                            cambios_detectados = False
                            
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
                            
                            for idx, (_, original_row) in enumerate(grupo.iterrows()):
                                if idx < len(edited_df):
                                    edited_row = edited_df.iloc[idx]
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
