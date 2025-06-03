import requests
from src.utils.database import Database
import copy

API_BASE = "http://127.0.0.1:8000/api/v1/"

def fetch_remote(endpoint):
    url = f"{API_BASE}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def post_or_put(endpoint, key, data, exists):
    url = f"{API_BASE}{endpoint}{key}/" if exists else f"{API_BASE}{endpoint}"
    if exists:
        r = requests.put(url, json=data)
    else:
        r = requests.post(url, json=data)
    r.raise_for_status()
    return r.json()

def sync_usuarios(db):
    print("Sincronizando usuarios...")
    locales = db.get_all_usuarios()
    remotos = {u["email"]: u for u in fetch_remote("usuarios/")}
    for email, local in locales.items():
        remoto = remotos.get(email)
        if not remoto:
            print(f"Nuevo usuario: {email}")
            post_or_put("usuarios/", "", local, exists=False)
        else:
            # Comparar todos los campos
            if any(local.get(k) != remoto.get(k) for k in local):
                print(f"Actualizando usuario: {email}")
                post_or_put("usuarios/", email, local, exists=True)

def sync_actividades(db):
    print("Sincronizando actividades...")
    locales = db.get_all_actividades()
    remotos = {a["id"]: a for a in fetch_remote("actividades/")}
    for local in locales:
        act_id = local["id"]
        remoto = remotos.get(act_id)
        actividad_copia = copy.deepcopy(local)
        # Eliminar campos que no están en el modelo remoto si es necesario
        if not remoto:
            print(f"Nueva actividad: {act_id}")
            post_or_put("actividades/", "", actividad_copia, exists=False)
        else:
            # Comparar todos los campos
            if any(actividad_copia.get(k) != remoto.get(k) for k in actividad_copia):
                print(f"Actualizando actividad: {act_id}")
                post_or_put("actividades/", act_id, actividad_copia, exists=True)

def sync_inscripciones(db):
    print("Sincronizando inscripciones...")
    locales = []
    for act in db.get_all_actividades():
        for email in act.get("inscritos", []):
            locales.append({"actividad": act["id"], "usuario": email})
    remotos = [ (i["actividad"], i["usuario"]) for i in fetch_remote("inscripcion/") ]
    for local in locales:
        key = (local["actividad"], local["usuario"])
        if key not in remotos:
            print(f"Nueva inscripción: {key}")
            post_or_put("inscripciones/", "", local, exists=False)
        # No se actualizan inscripciones, solo se crean si no existen

def main():
    db = Database()
    sync_usuarios(db)
    sync_actividades(db)
    sync_inscripciones(db)
    db.close()
    print("¡Sincronización completada!")

if __name__ == "__main__":
    main() 