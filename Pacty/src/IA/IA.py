import requests
import sqlite3
import os

 # Cómo idea para producción, esta información le llegará por la API
 # Aquí estamos utilizando un modelo local del PC


#Ollama en local
url = "http://localhost:11434/v1/completions"

import sqlite3
import os


def get_distinct_gustos(db_path="src/data/pacty.db"):
    conn = None
    gustos = ""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_db_path = os.path.join(script_dir, db_path)

    try:
        conn = sqlite3.connect(full_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT GROUP_CONCAT(DISTINCT gustos, ', ')
            FROM usuarios
            WHERE activo = 1;
        """)
        result = cursor.fetchone()
        if result and result[0]:
            gustos = result[0]
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
    finally:
        if conn:
            conn.close()
    return gustos


gustos_activos = get_distinct_gustos()

# Prompt: lo que necesitamos + ejemplo + estrctura de respuesta + contexto
promptBase = (
    "Eres un asistente de hotel. Sugiere 5 actividades generales que un hotel puede ofrecer. "
    "Para cada actividad, proporciona un 'id' único (número entero), un 'nombre' (string), "
    "una 'descripcion' (string breve), una 'fecha' (formato 'YYYY-MM-DD'), "
    "una 'hora' (formato 'HH:MM'), un 'lugar' (string), 'plazas' (número entero), "
    "una 'categoria' (e.g., 'Entretenimiento', 'Deporte', 'Gastronomía', 'Cultura'), "
    "y 'activo' (booleano, siempre 'true'). "
    "Devuelve la información como una lista de objetos JSON, donde cada objeto representa una actividad. "
    "Por ejemplo: "
    "[{'id': 1, 'nombre': 'Noche de Karaoke', 'descripcion': 'Canta tus canciones favoritas.', "
    "'fecha': '2025-06-15', 'hora': '21:00', 'lugar': 'Salón Principal', 'plazas': 50, "
    "'categoria': 'Entretenimiento', 'activo': true}]"
)

prompt = promptBase + "Quiero que la respuesta esté más personalizada, "
"teniendo en cuenta los gustos de los usuarios que van a asistir: "+ gustos_activos 


data = {
    "model": "phi",
    "prompt": prompt,
    "max_tokens": 50,
    "temperature": 0.5  # para menos creatividad y respuestas más directas
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print("Respuesta del modelo:")
    print(result.get("choices")[0].get("text") if "choices" in result else result)
else:
    print(f"Error {response.status_code}: {response.text}")
