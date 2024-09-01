import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt

# Inicializar el estado de la sesión para almacenar los datos de cada segundo
if 'historical_data' not in st.session_state:
    st.session_state['historical_data'] = []

# Función para simular el proceso
def simulate_process(machine_speeds, lot_size, setup_time, demand, time_limit):
    num_machines = len(machine_speeds)
    processed_units = 0
    inventories = [lot_size] * (num_machines + 1)  # Inicializar inventario de materia prima
    operation_times = [0] * num_machines
    wait_times = [0] * num_machines
    fail_times = [0] * num_machines
    fail_prob = 0.05
    setup_time_total = 0
    fail_time_total = 0
    start_time = time.time()

    # Variable para rastrear el tiempo transcurrido en la simulación
    elapsed_time = 0

    # Crear contenedores para gráficos
    inventory_chart = st.empty()
    times_chart = st.empty()

    while processed_units < demand and elapsed_time < time_limit:
        # Actualizar inventarios y tiempos en cada segundo
        elapsed_time = time.time() - start_time
        st.session_state['historical_data'].append({
            'elapsed_time': elapsed_time,
            'inventories': inventories.copy(),
            'operation_times': operation_times.copy(),
            'wait_times': wait_times.copy(),
            'fail_times': fail_times.copy(),
            'setup_time_total': setup_time_total,
            'fail_time_total': fail_time_total
        })

        for i in range(num_machines):
            # Simular fallas aleatorias
            if np.random.rand() < fail_prob:
                fail_duration = np.random.uniform(5, 15)
                fail_time_total += fail_duration
                fail_times[i] += fail_duration
                st.write(f"Machine {i+1} failure for {fail_duration:.2f} seconds")
                time.sleep(fail_duration)
                continue

            # Procesar el lote si hay suficiente inventario de entrada
            if inventories[i] >= lot_size:
                # Tiempo de procesamiento
                processing_time = machine_speeds[i] * lot_size
                operation_times[i] += processing_time
                inventories[i] -= lot_size  # Restar el lote procesado del inventario de entrada
                st.write(f"Machine {i+1} processing for {processing_time:.2f} seconds")
                time.sleep(processing_time)  # Simular el tiempo de procesamiento

                # Agregar el lote procesado al inventario de salida
                inventories[i + 1] += lot_size  # Transferir el lote procesado a la siguiente etapa

                # Simular tiempo de alistamiento
                time.sleep(setup_time)
                setup_time_total += setup_time
                st.write(f"Machine {i+1} setup time for {setup_time:.2f} seconds")

        # Verificar si ya se cumplió la demanda
        processed_units = inventories[-1]  # El inventario de productos terminados es la última posición
        if processed_units >= demand:
            break

        # Actualizar gráficos en tiempo real
        with inventory_chart.container():
            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            # Inventarios en tiempo real
            ax[0].bar(range(len(inventories)), inventories, color='blue')
            ax[0].set_title("Inventarios por Máquina")
            ax[0].set_xlabel("Máquinas")
            ax[0].set_ylabel("Inventario")

            # Tiempos acumulados por máquina en tiempo real
            ax[1].bar(range(len(operation_times)), operation_times, color='green')
            ax[1].set_title("Tiempos Acumulados por Máquina")
            ax[1].set_xlabel("Máquinas")
            ax[1].set_ylabel("Tiempo (segundos)")

            st.pyplot(fig)

        with times_chart.container():
            fig, ax = plt.subplots()

            # Tiempos perdidos por esperas, alistamiento y fallos en tiempo real
            times_lost = [setup_time_total, fail_time_total] + wait_times
            ax.bar(["Alistamiento", "Fallos"] + [f"Espera Máquina {i+1}" for i in range(len(wait_times))], times_lost, color='red')
            ax.set_title("Tiempos Perdidos")
            ax.set_xlabel("Tipo de Tiempo Perdido")
            ax.set_ylabel("Tiempo (segundos)")

            st.pyplot(fig)

        # Pausar un segundo antes de la próxima actualización
        time.sleep(1)

    total_time = time.time() - start_time
    return processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times

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
setup_time = st.sidebar.slider("Tiempo de alistamiento (segundos)", 1, 60, 10)
demand = st.sidebar.slider("Cantidad requerida por el cliente", 1, 100, 20)
time_limit = st.sidebar.slider("Tiempo límite (segundos)", 1, 600, 300)

start_simulation = st.sidebar.button("Iniciar Simulación")

if start_simulation:
    st.write("Iniciando simulación...")
    st.write("Tiempo límite:", time_limit, "segundos")
    processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times = simulate_process(
        machine_speeds, lot_size, setup_time, demand, time_limit)
    
    st.write(f"Unidades procesadas: {processed_units}")
    st.write(f"Inventarios entre máquinas: {inventories}")
    st.write(f"Tiempos de operación: {operation_times}")
    st.write(f"Tiempos de alistamiento total: {setup_time_total:.2f} segundos")
    st.write(f"Tiempos de fallas total: {fail_time_total:.2f} segundos")
    
    if processed_units >= demand:
        st.write("¡Requerimiento cumplido!")
    else:
        st.write("No se alcanzó a cumplir el requerimiento.")
