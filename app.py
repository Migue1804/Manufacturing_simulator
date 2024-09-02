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

# Datos para gráficos
tiempo_grafico = []
inventario_mp_grafico = []
inventario_proceso_m2_grafico = []
inventario_proceso_m3_grafico = []
inventario_pt_grafico = []
lead_time_grafico = []

# Funciones de Simulación
def fallo_maquina(confiabilidad):
    return random.randint(0, 100) > confiabilidad

def procesar_maquina(tiempo_ciclo, tiempo_ajuste, inventario_entrada, inventario_salida, tiempo_ajuste_total, tiempo_uso, tiempo_fallo_total, tiempo_espera_total, confiabilidad):
    global lotes_procesados
    if inventario_entrada > 0:
        if fallo_maquina(confiabilidad):
            tiempo_fallo_total += random.randint(1, 5)
            time.sleep(tiempo_fallo_total)
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
    
    # Gráfico de inventarios
    fig_inventario = go.Figure()
    fig_inventario.add_trace(go.Scatter(x=[], y=[], mode='lines', name='MP'))
    fig_inventario.add_trace(go.Scatter(x=[], y=[], mode='lines', name='M2'))
    fig_inventario.add_trace(go.Scatter(x=[], y=[], mode='lines', name='M3'))
    fig_inventario.add_trace(go.Scatter(x=[], y=[], mode='lines', name='PT'))

    # Gráfico de tiempos
    fig_tiempos = go.Figure()
    fig_tiempos.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Lead Time'))
    fig_tiempos.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Tiempo Requerido'))

    fig_inventario_placeholder = st.empty()
    fig_tiempos_placeholder = st.empty()
    
    while lotes_procesados < requerimiento_cliente:
        elapsed_time = time.time() - start_time

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
        
        # Actualización de Visualización
        st.write(f"Inventario de MP: {inventario_mp}")
        st.write(f"Inventario en Proceso M2: {inventario_proceso_m2}")
        st.write(f"Inventario en Proceso M3: {inventario_proceso_m3}")
        st.write(f"Inventario PT: {inventario_pt}")

        st.write(f"Tiempos de Máquina 1 - Ciclo: {tiempo_uso_m1}, Ajuste: {tiempo_ajuste_total_m1}, Fallo: {tiempo_fallo_total_m1}, Espera: {tiempo_espera_total_m1}")
        st.write(f"Tiempos de Máquina 2 - Ciclo: {tiempo_uso_m2}, Ajuste: {tiempo_ajuste_total_m2}, Fallo: {tiempo_fallo_total_m2}, Espera: {tiempo_espera_total_m2}")
        st.write(f"Tiempos de Máquina 3 - Ciclo: {tiempo_uso_m3}, Ajuste: {tiempo_ajuste_total_m3}, Fallo: {tiempo_fallo_total_m3}, Espera: {tiempo_espera_total_m3}")

        # Actualización de datos para gráficos
        tiempo_grafico.append(elapsed_time)
        inventario_mp_grafico.append(inventario_mp)
        inventario_proceso_m2_grafico.append(inventario_proceso_m2)
        inventario_proceso_m3_grafico.append(inventario_proceso_m3)
        inventario_pt_grafico.append(inventario_pt)
        lead_time_grafico.append(elapsed_time)

        # Actualización de gráficos
        fig_inventario.data[0].x = tiempo_grafico
        fig_inventario.data[0].y = inventario_mp_grafico
        fig_inventario.data[1].x = tiempo_grafico
        fig_inventario.data[1].y = inventario_proceso_m2_grafico
        fig_inventario.data[2].x = tiempo_grafico
        fig_inventario.data[2].y = inventario_proceso_m3_grafico
        fig_inventario.data[3].x = tiempo_grafico
        fig_inventario.data[3].y = inventario_pt_grafico

        fig_tiempos.data[0].x = tiempo_grafico
        fig_tiempos.data[0].y = lead_time_grafico
        fig_tiempos.data[1].x = tiempo_grafico
        fig_tiempos.data[1].y = [tiempo_requerido_cliente] * len(tiempo_grafico)

        fig_inventario_placeholder.plotly_chart(fig_inventario)
        fig_tiempos_placeholder.plotly_chart(fig_tiempos)

    # Resumen final
    st.write(f"Simulación completada en {time.time() - start_time:.2f} segundos")
    st.write(f"Total de productos terminados: {inventario_pt}")
    st.write(f"Tiempo total de operación: {tiempo_uso_m1 + tiempo_uso_m2 + tiempo_uso_m3}")
