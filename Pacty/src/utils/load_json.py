import json
from pathlib import Path

def load_json(filename):
    """
    Carga un archivo JSON desde la carpeta 'data' dado su nombre de archivo.
    Ejemplo: load_json('usuarios.json')
    """
    data_path = Path(__file__).parent.parent / "data" / filename
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(datos, json_name=None):
    """
    Guarda la lista de actividades en el archivo 'actividades.json' dentro de la carpeta 'data'.
    """
    nombre = f"{json_name}.json"
    data_path = Path(__file__).parent.parent / "data" / nombre
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
