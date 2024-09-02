import streamlit as st
import time
import numpy as np
import plotly.graph_objects as go

# Inicializar el estado de la sesión para almacenar los datos de cada segundo
if 'historical_data' not in st.session_state:
    st.session_state['historical_data'] = []

# Función para calcular la probabilidad de fallas basada en la confiabilidad
def calculate_fail_prob(reliability):
    return (1 - reliability / 100) * 0.5  # Ajusta el factor 0.5 según sea necesario

# Función para simular el proceso
def simulate_process(machine_speeds, lot_size, setup_times, demand, time_limit, initial_inventory, reliability):
    num_machines = len(machine_speeds)
    processed_units = 0
    inventories = [initial_inventory] + [0] * num_machines  # Inicializar inventario de materia prima y etapas
    operation_times = [0] * num_machines
    wait_times = [0] * num_machines
    fail_times = [0] * num_machines
    fail_prob = calculate_fail_prob(reliability)  # Ajustar la probabilidad de fallas según la confiabilidad
    setup_time_total = [0] * num_machines
    fail_time_total = [0] * num_machines
    start_time = time.time()

    # Variable para rastrear el tiempo transcurrido en la simulación
    elapsed_time = 0

    # Crear contenedores para gráficos
    inventory_chart = st.empty()
    times_chart = st.empty()
    lead_time_chart = st.empty()
    customer_time_chart = st.empty()

    while elapsed_time < time_limit:
        # Actualizar inventarios y tiempos en cada segundo
        elapsed_time = time.time() - start_time
        st.session_state['historical_data'].append({
            'elapsed_time': elapsed_time,
            'inventories': inventories.copy(),
            'operation_times': operation_times.copy(),
            'wait_times': wait_times.copy(),
            'fail_times': fail_times.copy(),
            'setup_time_total': setup_time_total.copy(),
            'fail_time_total': fail_time_total.copy()
        })

        for i in range(num_machines):
            # Simular fallas aleatorias
            if np.random.rand() < fail_prob:
                fail_duration = np.random.uniform(1, 10)  # Ajuste del rango de duración de fallas
                fail_time_total[i] += fail_duration
                fail_times[i] += fail_duration
                st.write(f"Machine {i+1} failure for {fail_duration:.2f} seconds")
                time.sleep(fail_duration)
                continue

            # Procesar el lote si hay suficiente inventario de entrada
            if i == 0 or inventories[i] >= lot_size:
                # Tiempo de procesamiento
                processing_time = machine_speeds[i] * lot_size
                operation_times[i] += processing_time
                inventories[i] -= lot_size  # Restar el lote procesado del inventario de entrada
                st.write(f"Machine {i+1} processing for {processing_time:.2f} seconds")
                time.sleep(processing_time)  # Simular el tiempo de procesamiento

                # Agregar el lote procesado al inventario de salida
                if i + 1 < len(inventories):
                    inventories[i + 1] += lot_size  # Transferir el lote procesado a la siguiente etapa

                # Simular tiempo de alistamiento específico para cada máquina
                if i < len(setup_times):
                    setup_time = setup_times[i]
                    time.sleep(setup_time)
                    setup_time_total[i] += setup_time
                    st.write(f"Machine {i+1} setup time for {setup_time:.2f} seconds")
            else:
                # Si no hay suficiente inventario, incrementar el tiempo de espera
                wait_times[i] += 1
                st.write(f"Machine {i+1} waiting due to insufficient inventory")

        # Verificar si ya se cumplió la demanda
        processed_units = inventories[-1]  # El inventario de productos terminados es la última posición
        if processed_units >= demand:
            break

        # Actualizar gráficos en tiempo real
        with inventory_chart.container():
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)] + ['Producto Terminado'], y=inventories, name='Inventario'))
            fig.add_trace(go.Scatter(x=['Producto Terminado'], y=[demand], mode='lines+markers', name='Demanda Requerida', line=dict(color='red', width=2)))
            fig.update_layout(title='Inventarios por Máquina', xaxis_title='Máquinas/Producto Terminado', yaxis_title='Inventario')
            st.plotly_chart(fig, use_container_width=True)

        with times_chart.container():
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)], y=operation_times, name='Operación', marker_color='green'))
            fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)], y=setup_time_total, name='Alistamiento', marker_color='blue'))
            fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)], y=fail_time_total, name='Fallas', marker_color='red'))
            fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)], y=wait_times, name='Esperas', marker_color='orange'))
            fig.update_layout(title='Tiempos Acumulados por Máquina', xaxis_title='Máquinas', yaxis_title='Tiempo (segundos)', barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

        # Calcular el Lead Time y mostrar en un gráfico
        total_operation_time = sum(operation_times)
        total_setup_time = sum(setup_time_total)
        total_fail_time = sum(fail_time_total)
        total_wait_time = sum(wait_times)
        lead_time = total_operation_time + total_setup_time + total_fail_time + total_wait_time

        with lead_time_chart.container():
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Operación', 'Alistamiento', 'Fallas', 'Esperas'], y=[total_operation_time, total_setup_time, total_fail_time, total_wait_time], name='Tiempos'))
            fig.add_trace(go.Bar(x=['Lead Time'], y=[lead_time], name='Lead Time', marker_color='purple'))
            st.plotly_chart(fig, use_container_width=True)

        # Calcular tiempo requerido por el cliente y mostrar en un gráfico
        with customer_time_chart.container():
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Tiempo Requerido por Cliente'], y=[time_limit], name='Tiempo Requerido', marker_color='cyan'))
            fig.add_trace(go.Bar(x=['Lead Time Total'], y=[lead_time], name='Lead Time', marker_color='magenta'))
            st.plotly_chart(fig, use_container_width=True)

        # Pausar un segundo antes de la próxima actualización
        time.sleep(1)

    # Asegurarse de que se grafique el inventario final de productos terminados
    with inventory_chart.container():
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[f'Máquina {i+1}' for i in range(num_machines)] + ['Producto Terminado'], y=inventories, name='Inventario'))
        fig.add_trace(go.Scatter(x=['Producto Terminado'], y=[demand], mode='lines+markers', name='Demanda Requerida', line=dict(color='red', width=2)))
        fig.update_layout(title='Inventarios por Máquina', xaxis_title='Máquinas/Producto Terminado', yaxis_title='Inventario')
        st.plotly_chart(fig, use_container_width=True)

    total_time = time.time() - start_time
    if processed_units >= demand and lead_time <= time_limit:
        conclusion = "¡Requerimiento cumplido!"
    else:
        conclusion = "No se alcanzó a cumplir el requerimiento."

    return processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times, lead_time, conclusion

# Interfaz de usuario
st.title("Simulación de Proceso de Producción en Tiempo Real")

# Parámetros de entrada
st.sidebar.header("Configuración del Proceso")
machine_speeds = [
    st.sidebar.slider("Velocidad de la Máquina 1 (segundos por unidad)", 1, 20, 5),
    st.sidebar.slider("Velocidad de la Máquina 2 (segundos por unidad)", 1, 20, 10),
    st.sidebar.slider("Velocidad de la Máquina 3 (segundos por unidad)", 1, 20, 7)
]
lot_size = st.sidebar.slider("Tamaño del lote", 1, 10, 6)
setup_times = [
    st.sidebar.slider("Tiempo de alistamiento de Máquina 1 (segundos)", 0, 5, 1),
    st.sidebar.slider("Tiempo de alistamiento de Máquina 2 (segundos)", 0, 5, 1),
    st.sidebar.slider("Tiempo de alistamiento de Máquina 3 (segundos)", 0, 5, 1)
]
demand = st.sidebar.slider("Cantidad requerida por el cliente", 1, 50, 10)
time_limit = st.sidebar.slider("Tiempo límite (segundos)", 1, 600, 350)
initial_inventory = st.sidebar.slider("Inventario inicial de materia prima", 1, 50, 20)
reliability = st.sidebar.slider("OEE del equipo (%)", 0, 100, 85)

start_simulation = st.sidebar.button("Iniciar Simulación")

if start_simulation:
    st.write("Iniciando simulación...")
    st.write("Tiempo límite:", time_limit, "segundos")
    processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times, lead_time, conclusion = simulate_process(
        machine_speeds, lot_size, setup_times, demand, time_limit, initial_inventory, reliability)
    
    st.write(f"Unidades procesadas: {processed_units}")
    st.write(f"Inventarios entre máquinas: {inventories}")
    st.write(f"Tiempos de operación: {operation_times}")
    st.write(f"Tiempos de alistamiento total por máquina: {setup_time_total}")
    st.write(f"Tiempos de fallos total por máquina: {fail_time_total}")
    st.write(f"Tiempos de espera: {wait_times}")
    st.write(f"Lead Time Total: {lead_time:.2f} segundos")
    st.write(f"Conclusión: {conclusion}")
