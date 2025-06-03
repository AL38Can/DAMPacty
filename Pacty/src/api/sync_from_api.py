import requests
from src.utils.database import Database

API_BASE = "http://127.0.0.1:8000/api/v1/"

def fetch_data(endpoint):
    url = f"{API_BASE}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def sync_usuarios(db):
    usuarios = fetch_data("usuarios/")
    for usuario in usuarios:
        email = usuario.get("email")
        if email:
            db.save_usuario(email, usuario) # Ya controla si existe

def sync_actividades(db):
    actividades = fetch_data("actividades/")
    for actividad in actividades:
        db.save_actividad(actividad)
        for comentario in actividad.get("comentarios", []):
            db.add_comentario(
                actividad_id=actividad["id"],
                usuario=comentario["usuario"],
                comentario=comentario.get("comentario", ""),
                puntuacion=comentario.get("puntuacion", 0),
                fecha=comentario.get("fecha")
            )

def sync_inscripciones(db):
    inscripciones = fetch_data("inscripcion/")
    for inscripcion in inscripciones:
        actividad_id = inscripcion.get("actividad")
        usuario_email = inscripcion.get("usuario")
        if actividad_id and usuario_email:
            db.add_inscripcion(actividad_id, usuario_email)




def main():
    db = Database()
    print("Sincronizando usuarios...")
    sync_usuarios(db)
    print("Sincronizando actividades...")
    sync_actividades(db)
    print("Sincronizando inscripciones...")
    sync_inscripciones(db)
    db.close()
    print("¡Sincronización completada!")

if __name__ == "__main__":
    main() 