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
    processing_times = [0] * num_machines  # Almacena el tiempo acumulado de procesamiento por máquina

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

            # Verificar si hay suficiente inventario para procesar el lote
            if inventories[i] >= lot_size:
                # Si hay suficiente inventario, calcular el tiempo de procesamiento del lote
                processing_time = machine_speeds[i] * lot_size
                operation_times[i] += processing_time
                inventories[i] -= lot_size  # Restar el lote procesado del inventario de entrada

                # Si no es la primera máquina, debe esperar a que todas las máquinas anteriores procesen el lote
                if i > 0:
                    cumulative_previous_processing = sum(processing_times[:i])
                    wait_time_for_previous = max(0, cumulative_previous_processing - elapsed_time)
                    wait_times[i] += wait_time_for_previous
                    st.write(f"Machine {i+1} waiting for {wait_time_for_previous:.2f} seconds due to previous machine processing")
                    time.sleep(wait_time_for_previous)  # Esperar el tiempo necesario

                # Procesar el lote
                st.write(f"Machine {i+1} processing for {processing_time:.2f} seconds")
                time.sleep(processing_time)  # Simular el tiempo de procesamiento
                processing_times[i] += processing_time

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
                # Incrementar el tiempo de espera si no hay suficiente inventario
                wait_times[i] += 1
                st.write(f"Machine {i+1} waiting due to insufficient inventory")
                time.sleep(1)  # Esperar un segundo por cada ciclo de espera

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
    conclusion = "La demanda fue cumplida a tiempo." if processed_units >= demand else "No se logró cumplir la demanda del cliente a tiempo."
    st.write(f"{conclusion} Tiempo total: {total_time:.2f} segundos, Lead Time Total: {lead_time:.2f} segundos")

# Configuración de la aplicación
st.title('Simulación de Proceso Productivo')

machine_speeds = [st.slider(f'Velocidad de Máquina {i+1} (segundos por lote)', 1, 10, 5) for i in range(3)]
lot_size = st.slider('Tamaño de Lote', 1, 10, 5)
setup_times = [st.slider(f'Tiempo de Alistamiento de Máquina {i+1} (segundos)', 0, 30, 10) for i in range(3)]
demand = st.number_input('Cantidad Requerida por el Cliente', min_value=1, value=100)
time_limit = st.number_input('Tiempo Requerido por el Cliente (segundos)', min_value=1, value=600)
initial_inventory = st.number_input('Inventario Inicial de Materia Prima', min_value=0, value=50)
reliability = st.slider('Confiabilidad del Equipo', 0, 100, 90)

if st.button('Iniciar Simulación'):
    simulate_process(machine_speeds, lot_size, setup_times, demand, time_limit, initial_inventory, reliability)
