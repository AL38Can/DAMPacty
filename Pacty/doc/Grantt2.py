import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates


# Leer el archivo Excel especificando el nombre
df = pd.read_excel("Tiempos2.xlsx")

# Asegurarse de que las columnas de fecha sean datetime
if 'Fecha Inicio' in df.columns:
    df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'], format='%d/%m/%Y', errors='coerce')
if 'Fecha Fin' in df.columns:
    df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'], format='%d/%m/%Y', errors='coerce')
if 'Duración (Días)' in df.columns and 'Fecha Fin' not in df.columns and 'Fecha Inicio' in df.columns:
    df['Fecha Fin'] = df['Fecha Inicio'] + pd.to_timedelta(df['Duración (Días)'], unit='D')
elif 'Duración (Días)' in df.columns and 'Fecha Inicio' not in df.columns and 'Fecha Fin' in df.columns:
    df['Fecha Inicio'] = df['Fecha Fin'] - pd.to_timedelta(df['Duración (Días)'], unit='D')

# Verificar si las columnas necesarias existen
if 'Fase' not in df.columns or 'Fecha Inicio' not in df.columns or 'Fecha Fin' not in df.columns:
    print("Error: El archivo Excel debe contener las columnas 'Fase', 'Fecha Inicio' y 'Fecha Fin'.")
else:
    fig, ax = plt.subplots(figsize=(12, 7))
    y_ticks = []
    y_labels = []

    for i, row in df.iterrows():
        start_date = row['Fecha Inicio']
        end_date = row['Fecha Fin']
        phase = row['Fase']

        # Verificar si las fechas son válidas
        if pd.notna(start_date) and pd.notna(end_date):
            duration = (end_date - start_date).days
            y_ticks.append(i)
            y_labels.append(phase)
            ax.barh(i, duration, left=start_date, height=0.8, label=phase)
        else:
            print(f"Advertencia: Fechas inválidas para la fase '{phase}'. Omitiendo barra.")

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Fase del Proyecto')
    ax.set_title('Diagrama de Gantt del Proyecto App Móvil - Pacty')
    # ax.grid(True)

    # Formatear el eje x para mostrar fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    fig.autofmt_xdate()  # Rotar las etiquetas del eje x para evitar superposición

    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()