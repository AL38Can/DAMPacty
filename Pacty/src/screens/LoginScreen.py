from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivy.app import App
from src.utils.auth import generate_token

# --- PANTALLA DE LOGIN ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_login(self, instance):
        email = self.ids.email.text
        password = self.ids.password.text
        
        # Get app instance
        app = App.get_running_app()
        
        # Autenticar usuario
        if app.db.authenticate_user(email, password):
            # Obtener datos del usuario
            user = app.db.get_usuario(email)
            
            # Generar token JWT
            token = generate_token(user)
            app.token = token
            
            # Update current user in app
            app.usuario_actual = email
            app.rol_actual = user["perfil"]
            app.usuario_actual_detalle = user
            
            # Navigate to appropriate home screen
            self.manager.current = f"{user['perfil']}_home"
        else:
            # Verificar si el usuario está bloqueado
            user = app.db.get_usuario(email)
            if user and user.get('bloqueado'):
                self.ids.message.text = "Cuenta bloqueada por demasiados intentos fallidos"
                toast("Cuenta bloqueada por demasiados intentos fallidos")
            else:
                self.ids.message.text = "Credenciales incorrectas"
                toast("Credenciales incorrectas")