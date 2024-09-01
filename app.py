import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt

# Inicializar el estado de la sesión para almacenar los datos de cada segundo
if 'historical_data' not in st.session_state:
    st.session_state['historical_data'] = []

# Función para simular el proceso
def simulate_process(machine_speeds, lot_size, setup_times, demand, time_limit, initial_inventory):
    num_machines = len(machine_speeds)
    processed_units = 0
    inventories = [initial_inventory] + [0] * num_machines  # Inicializar inventario de materia prima y etapas
    operation_times = [0] * num_machines
    wait_times = [0] * num_machines
    fail_times = [0] * num_machines
    fail_prob = 0.05
    setup_time_total = [0] * num_machines
    fail_time_total = [0] * num_machines
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
            'setup_time_total': setup_time_total.copy(),
            'fail_time_total': fail_time_total.copy()
        })

        for i in range(num_machines):
            # Simular fallas aleatorias
            if np.random.rand() < fail_prob:
                fail_duration = np.random.uniform(5, 15)
                fail_time_total[i] += fail_duration
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

                # Simular tiempo de alistamiento específico para cada máquina
                time.sleep(setup_times[i])
                setup_time_total[i] += setup_times[i]
                st.write(f"Machine {i+1} setup time for {setup_times[i]:.2f} seconds")
            else:
                wait_times[i] += 1  # Incrementar tiempo de espera si no hay suficiente inventario

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
            times_lost = setup_time_total + fail_time_total + wait_times
            labels = [f"Setup Máquina {i+1}" for i in range(num_machines)] + [f"Fallo Máquina {i+1}" for i in range(num_machines)] + [f"Espera Máquina {i+1}" for i in range(num_machines)]
            ax.bar(labels, times_lost, color='red')
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
setup_times = [
    st.sidebar.slider("Tiempo de alistamiento de Máquina 1 (segundos)", 1, 60, 10),
    st.sidebar.slider("Tiempo de alistamiento de Máquina 2 (segundos)", 1, 60, 15),
    st.sidebar.slider("Tiempo de alistamiento de Máquina 3 (segundos)", 1, 60, 12)
]
demand = st.sidebar.slider("Cantidad requerida por el cliente", 1, 100, 20)
time_limit = st.sidebar.slider("Tiempo límite (segundos)", 1, 600, 300)
initial_inventory = st.sidebar.slider("Inventario inicial de materia prima", 1, 100, 50)

start_simulation = st.sidebar.button("Iniciar Simulación")

if start_simulation:
    st.write("Iniciando simulación...")
    st.write("Tiempo límite:", time_limit, "segundos")
    processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times = simulate_process(
        machine_speeds, lot_size, setup_times, demand, time_limit, initial_inventory)
    
    st.write(f"Unidades procesadas: {processed_units}")
    st.write(f"Inventarios entre máquinas: {inventories}")
    st.write(f"Tiempos de operación: {operation_times}")
    st.write(f"Tiempos de alistamiento total por máquina: {setup_time_total}")
    st.write(f"Tiempos de fallas total por máquina: {fail_time_total}")
    st.write(f"Tiempos de espera total por máquina: {wait_times}")
    
    if processed_units >= demand:
        st.write("¡Requerimiento cumplido!")
    else:
        st.write("No se alcanzó a cumplir el requerimiento.")
