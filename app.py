import streamlit as st
import time
import random
import plotly.graph_objects as go

# Parámetros de Simulación
tiempo_ciclo_m1 = st.sidebar.number_input('Tiempo de ciclo Máquina 1 (s)', min_value=1, value=5)
tiempo_ajuste_m1 = st.sidebar.number_input('Tiempo de ajuste Máquina 1 (s)', min_value=0, value=2)
tiempo_ciclo_m2 = st.sidebar.number_input('Tiempo de ciclo Máquina 2 (s)', min_value=1, value=6)
tiempo_ajuste_m2 = st.sidebar.number_input('Tiempo de ajuste Máquina 2 (s)', min_value=0, value=3)
tiempo_ciclo_m3 = st.sidebar.number_input('Tiempo de ciclo Máquina 3 (s)', min_value=1, value=7)
tiempo_ajuste_m3 = st.sidebar.number_input('Tiempo de ajuste Máquina 3 (s)', min_value=0, value=4)
confiabilidad_m1 = st.sidebar.slider('Confiabilidad Máquina 1 (%)', 0, 100, 90)
confiabilidad_m2 = st.sidebar.slider('Confiabilidad Máquina 2 (%)', 0, 100, 85)
confiabilidad_m3 = st.sidebar.slider('Confiabilidad Máquina 3 (%)', 0, 100, 80)
inventario_inicial_mp = st.sidebar.number_input('Inventario Inicial Materia Prima', min_value=0, value=20)
requerimiento_cliente = st.sidebar.number_input('Requerimiento del Cliente', min_value=1, value=50)
tiempo_requerido_cliente = st.sidebar.number_input('Tiempo Requerido por el Cliente (s)', min_value=1, value=300)
tamano_lote = st.sidebar.slider('Tamaño del Lote', 1, 10, 5)

# Variables de Estado
inventario_mp = inventario_inicial_mp
inventario_proceso_m2 = 0
inventario_proceso_m3 = 0
inventario_pt = 0

tiempo_uso_m1 = 0
tiempo_uso_m2 = 0
tiempo_uso_m3 = 0
tiempo_ajuste_total_m1 = 0
tiempo_ajuste_total_m2 = 0
tiempo_ajuste_total_m3 = 0
tiempo_fallo_total_m1 = 0
tiempo_fallo_total_m2 = 0
tiempo_fallo_total_m3 = 0
tiempo_espera_total_m1 = 0
tiempo_espera_total_m2 = 0
tiempo_espera_total_m3 = 0

lotes_procesados = 0
tiempo_simulacion = 0

# Funciones de Simulación
def fallo_maquina(confiabilidad):
    return random.randint(0, 100) > confiabilidad

def procesar_maquina(tiempo_ciclo, tiempo_ajuste, inventario_entrada, inventario_salida, tiempo_ajuste_total, tiempo_uso, tiempo_fallo_total, tiempo_espera_total, confiabilidad):
    global lotes_procesados
    if inventario_entrada > 0:
        if fallo_maquina(confiabilidad):
            tiempo_fallo = random.randint(1, 5)
            tiempo_fallo_total += tiempo_fallo
            time.sleep(tiempo_fallo)
        else:
            if tiempo_ajuste > 0:
                tiempo_ajuste_total += tiempo_ajuste
                time.sleep(tiempo_ajuste)
            
            tiempo_uso += tiempo_ciclo
            time.sleep(tiempo_ciclo)
            inventario_entrada -= 1
            inventario_salida += 1
            lotes_procesados += 1
    else:
        tiempo_espera_total += 1
        time.sleep(1)
    return inventario_entrada, inventario_salida, tiempo_ajuste_total, tiempo_uso, tiempo_fallo_total, tiempo_espera_total

# Iniciar Simulación
st.title("Simulación de Proceso de Producción")

if st.button("Iniciar Simulación"):
    start_time = time.time()
    
    # Datos para gráficos
    tiempos = {'Tiempo': [], 'Tiempos de Máquina 1': [], 'Tiempos de Máquina 2': [], 'Tiempos de Máquina 3': []}
    inventarios = {'Tiempo': [], 'Inventario MP': [], 'Inventario en Proceso M2': [], 'Inventario en Proceso M3': [], 'Inventario PT': []}
    lead_times = {'Tiempo': [], 'Lead Time': [], 'Tiempo Requerido': [tiempo_requerido_cliente] * 1000}
    
    while lotes_procesados < requerimiento_cliente:
        # Máquina 1
        inventario_mp, inventario_proceso_m2, tiempo_ajuste_total_m1, tiempo_uso_m1, tiempo_fallo_total_m1, tiempo_espera_total_m1 = procesar_maquina(
            tiempo_ciclo_m1, tiempo_ajuste_m1, inventario_mp, inventario_proceso_m2, tiempo_ajuste_total_m1, tiempo_uso_m1, tiempo_fallo_total_m1, tiempo_espera_total_m1, confiabilidad_m1
        )

        # Máquina 2
        inventario_proceso_m2, inventario_proceso_m3, tiempo_ajuste_total_m2, tiempo_uso_m2, tiempo_fallo_total_m2, tiempo_espera_total_m2 = procesar_maquina(
            tiempo_ciclo_m2, tiempo_ajuste_m2, inventario_proceso_m2, inventario_proceso_m3, tiempo_ajuste_total_m2, tiempo_uso_m2, tiempo_fallo_total_m2, tiempo_espera_total_m2, confiabilidad_m2
        )

        # Máquina 3
        inventario_proceso_m3, inventario_pt, tiempo_ajuste_total_m3, tiempo_uso_m3, tiempo_fallo_total_m3, tiempo_espera_total_m3 = procesar_maquina(
            tiempo_ciclo_m3, tiempo_ajuste_m3, inventario_proceso_m3, inventario_pt, tiempo_ajuste_total_m3, tiempo_uso_m3, tiempo_fallo_total_m3, tiempo_espera_total_m3, confiabilidad_m3
        )
        
        # Actualización de tiempos y estados
        tiempo_simulacion = time.time() - start_time
        tiempos['Tiempo'].append(tiempo_simulacion)
        tiempos['Tiempos de Máquina 1'].append(tiempo_uso_m1)
        tiempos['Tiempos de Máquina 2'].append(tiempo_uso_m2)
        tiempos['Tiempos de Máquina 3'].append(tiempo_uso_m3)
        
        inventarios['Tiempo'].append(tiempo_simulacion)
        inventarios['Inventario MP'].append(inventario_mp)
        inventarios['Inventario en Proceso M2'].append(inventario_proceso_m2)
        inventarios['Inventario en Proceso M3'].append(inventario_proceso_m3)
        inventarios['Inventario PT'].append(inventario_pt)
        
        lead_times['Tiempo'].append(tiempo_simulacion)
        lead_times['Lead Time'].append(tiempo_ajuste_total_m1 + tiempo_ajuste_total_m2 + tiempo_ajuste_total_m3 + tiempo_fallo_total_m1 + tiempo_fallo_total_m2 + tiempo_fallo_total_m3 + tiempo_espera_total_m1 + tiempo_espera_total_m2 + tiempo_espera_total_m3)
        
        # Mostrar datos en tiempo real
        st.write(f"Inventario de MP: {inventario_mp}")
        st.write(f"Inventario en Proceso M2: {inventario_proceso_m2}")
        st.write(f"Inventario en Proceso M3: {inventario_proceso_m3}")
        st.write(f"Inventario PT: {inventario_pt}")

        st.write(f"Tiempos de Máquina 1 - Ciclo: {tiempo_uso_m1}, Ajuste: {tiempo_ajuste_total_m1}, Fallo: {tiempo_fallo_total_m1}, Espera: {tiempo_espera_total_m1}")
        st.write(f"Tiempos de Máquina 2 - Ciclo: {tiempo_uso_m2}, Ajuste: {tiempo_ajuste_total_m2}, Fallo: {tiempo_fallo_total_m2}, Espera: {tiempo_espera_total_m2}")
        st.write(f"Tiempos de Máquina 3 - Ciclo: {tiempo_uso_m3}, Ajuste: {tiempo_ajuste_total_m3}, Fallo: {tiempo_fallo_total_m3}, Espera: {tiempo_espera_total_m3}")

        # Graficar
        if len(tiempos['Tiempo']) > 1:
            fig_inventarios = go.Figure()
            fig_inventarios.add_trace(go.Scatter(x=inventarios['Tiempo'], y=inventarios['Inventario MP'], mode='lines', name='Inventario MP'))
            fig_inventarios.add_trace(go.Scatter(x=inventarios['Tiempo'], y=inventarios['Inventario en Proceso M2'], mode='lines', name='Inventario en Proceso M2'))
            fig_inventarios.add_trace(go.Scatter(x=inventarios['Tiempo'], y=inventarios['Inventario en Proceso M3'], mode='lines', name='Inventario en Proceso M3'))
            fig_inventarios.add_trace(go.Scatter(x=inventarios['Tiempo'], y=inventarios['Inventario PT'], mode='lines', name='Inventario PT'))
            st.plotly_chart(fig_inventarios, use_container_width=True)

            fig_tiempos = go.Figure()
            fig_tiempos.add_trace(go.Scatter(x=tiempos['Tiempo'], y=tiempos['Tiempos de Máquina 1'], mode='lines', name='Tiempos Máquina 1'))
            fig_tiempos.add_trace(go.Scatter(x=tiempos['Tiempo'], y=tiempos['Tiempos de Máquina 2'], mode='lines', name='Tiempos Máquina 2'))
            fig_tiempos.add_trace(go.Scatter(x=tiempos['Tiempo'], y=tiempos['Tiempos de Máquina 3'], mode='lines', name='Tiempos Máquina 3'))
            st.plotly_chart(fig_tiempos, use_container_width=True)

            fig_lead_time = go.Figure()
            fig_lead_time.add_trace(go.Scatter(x=lead_times['Tiempo'], y=lead_times['Lead Time'], mode='lines', name='Lead Time'))
            fig_lead_time.add_trace(go.Scatter(x=lead_times['Tiempo'], y=lead_times['Tiempo Requerido'], mode='lines', name='Tiempo Requerido', line=dict(dash='dash')))
            st.plotly_chart(fig_lead_time, use_container_width=True)
        
        # Verificación de tiempo
        elapsed_time = time.time() - start_time
        if elapsed_time > tiempo_requerido_cliente:
            st.write("No se pudo cumplir con el requerimiento del cliente en el tiempo requerido.")
            break
        
    st.write("Simulación completada.")

