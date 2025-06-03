import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates

# Leer el archivo Excel
df = pd.read_excel("Tiempos2.xlsx")

# Convertir columnas de fecha a datetime
if 'Fecha Inicio' in df.columns:
    df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'], format='%d/%m/%Y', errors='coerce')
if 'Fecha Fin' in df.columns:
    df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'], format='%d/%m/%Y', errors='coerce')
if 'Duración (Días)' in df.columns and 'Fecha Fin' not in df.columns and 'Fecha Inicio' in df.columns:
    df['Fecha Fin'] = df['Fecha Inicio'] + pd.to_timedelta(df['Duración (Días)'], unit='D')
elif 'Duración (Días)' in df.columns and 'Fecha Inicio' not in df.columns and 'Fecha Fin' in df.columns:
    df['Fecha Inicio'] = df['Fecha Fin'] - pd.to_timedelta(df['Duración (Días)'], unit='D')

# Verificar columnas necesarias
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

        if pd.notna(start_date) and pd.notna(end_date):
            duration = (end_date - start_date).days
            y_ticks.append(i)
            y_labels.append(phase)
            ax.barh(i, duration, left=start_date, height=0.8)
        else:
            print(f"Advertencia: Fechas inválidas para la fase '{phase}'. Omitiendo barra.")

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Fase del Proyecto')
    ax.set_title('Diagrama de Gantt del Proyecto App Móvil - Pacty')

    # Formato de fechas en el eje x
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    fig.autofmt_xdate()
    plt.gca().invert_yaxis()

    # Líneas verticales y anotaciones
    fecha_min = df['Fecha Inicio'].min()
    fecha_max = df['Fecha Fin'].max()
    ax.axvline(fecha_min, color='green', linestyle='--', linewidth=2, label='Inicio Proyecto')
    ax.axvline(fecha_max, color='red', linestyle='--', linewidth=2, label='Fin Proyecto')

    # Anotación inicio
    ax.annotate(
        f'Inicio: {fecha_min.strftime("%d-%b-%Y")}',
        xy=(fecha_min, -0.5),
        xytext=(-60, 20),
        textcoords='offset points',
        arrowprops=dict(arrowstyle='->', color='green'),
        color='green',
        fontsize=10,
        fontweight='bold'
    )

    # Anotación fin
    ax.annotate(
        f'Fin: {fecha_max.strftime("%d-%b-%Y")}',
        xy=(fecha_max, len(df) - 0.5),
        xytext=(10, 20),
        textcoords='offset points',
        arrowprops=dict(arrowstyle='->', color='red'),
        color='red',
        fontsize=10,
        fontweight='bold'
    )

    ax.legend()
    plt.tight_layout()
    plt.show()
