import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Función para simular el proceso
def simulate_process(machine_speeds, lot_size, setup_time, demand, time_limit):
    num_machines = len(machine_speeds)
    processed_units = 0
    inventories = [0] * (num_machines + 1)  # Añadimos un espacio para el producto terminado
    operation_times = [0] * num_machines
    wait_times = [0] * num_machines
    fail_times = [0] * num_machines
    fail_prob = 0.05
    setup_time_total = 0
    fail_time_total = 0
    start_time = time.time()
    
    while processed_units < demand and (time.time() - start_time) < time_limit:
        for i in range(num_machines):
            if inventories[i] < lot_size:
                # Simular fallas aleatorias
                if np.random.rand() < fail_prob:
                    fail_duration = np.random.uniform(5, 15)
                    fail_time_total += fail_duration
                    fail_times[i] += fail_duration
                    st.write(f"Machine {i+1} failure for {fail_duration:.2f} seconds")
                    time.sleep(fail_duration)
                    continue
                
                # Tiempo de procesamiento
                processing_time = machine_speeds[i] * lot_size
                operation_times[i] += processing_time
                inventories[i] += lot_size
                processed_units += lot_size
                
                if processed_units >= demand:
                    break
                
                # Transferencia entre máquinas
                if i < num_machines - 1:
                    inventories[i] -= lot_size
                    inventories[i+1] += lot_size
                    time.sleep(setup_time)  # Tiempo de alistamiento
                    setup_time_total += setup_time
                else:
                    inventories[i] -= lot_size

    total_time = time.time() - start_time
    return processed_units, inventories, operation_times, setup_time_total, fail_time_total, wait_times

# Interfaz de usuario
st.title("Simulación de Proceso de Producción")

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
stop_simulation = st.sidebar.button("Detener Simulación")

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
    
    # Graficar los resultados
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))

    # Inventarios
    ax[0, 0].bar(range(len(inventories)), inventories, color='blue')
    ax[0, 0].set_title("Inventarios por Máquina")
    ax[0, 0].set_xlabel("Máquinas")
    ax[0, 0].set_ylabel("Inventario")

    # Tiempos acumulados por máquina
    ax[0, 1].bar(range(len(operation_times)), operation_times, color='green')
    ax[0, 1].set_title("Tiempos Acumulados por Máquina")
    ax[0, 1].set_xlabel("Máquinas")
    ax[0, 1].set_ylabel("Tiempo (segundos)")

    # Tiempos perdidos por esperas, alistamiento y fallos
    times_lost = [setup_time_total, fail_time_total] + wait_times
    ax[1, 0].bar(["Alistamiento", "Fallos"] + [f"Espera Máquina {i+1}" for i in range(len(wait_times))], times_lost, color='red')
    ax[1, 0].set_title("Tiempos Perdidos")
    ax[1, 0].set_xlabel("Tipo de Tiempo Perdido")
    ax[1, 0].set_ylabel("Tiempo (segundos)")

    # Mostrar gráficos
    st.pyplot(fig)
              
