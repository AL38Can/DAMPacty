import jwt
import datetime
from functools import wraps
from kivy.app import App
from kivymd.toast import toast

# Clave secreta para firmar los tokens JWT
SECRET_KEY = "claveAndreaSecretaSecreta"  # En producción, usar una clave segura y almacenarla de forma segura

def generate_token(user_data):
    """
    Genera un token JWT para el usuario
    """
    payload = {
        'email': user_data['email'],
        'perfil': user_data['perfil'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expira en 1 día
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_token(token):
    """
    Verifica un token JWT y devuelve los datos del usuario si es válido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(func):
    """
    Decorador para proteger rutas que requieren autenticación
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        app = App.get_running_app()
        if not app.token:
            toast("Por favor, inicie sesión para continuar")
            app.sm.current = "login"
            return None
        return func(*args, **kwargs)
    return wrapper