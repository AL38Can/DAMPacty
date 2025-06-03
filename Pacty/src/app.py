from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from src.screens.LoginScreen import LoginScreen
from src.screens.ClienteHomeScreen import ClienteHomeScreen
from src.screens.EmpleadoHomeScreen import EmpleadoHomeScreen
from src.screens.AdminHomeScreen import AdminHomeScreen
from src.screens.ComentariosScreen import ComentariosScreen
from src.screens.ValorarScreen import ValorarScreen
from src.screens.FiltrosScreen import FiltrosScreen
from src.screens.NuevoUsuarioScreen import NuevoUsuarioScreen
from src.screens.NuevaActividadScreen import NuevaActividadScreen
from src.screens.EditarActividadScreen import EditarActividadScreen
from kivy.core.window import Window
import locale 
from src.utils.database import Database
from src.utils.auth import verify_token

# Configurar la localización para el formato de fecha en español
locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize database
        self.db = Database()
        # Initialize user variables
        self.usuario_actual = None
        self.rol_actual = None
        self.usuario_actual_detalle = None
        self.current_user_email = None
        self.token = None  # Almacenar el token JWT
    
    def on_usuario_guardado(self):
        # Aquí puedes actualizar la UI, recargar datos, etc.
        pass

    def verify_session(self):
        """
        Verifica si hay una sesión válida
        """
        if self.token:
            payload = verify_token(self.token)
            if payload:
                self.usuario_actual = payload['email']
                self.rol_actual = payload['perfil']
                return True
        return False
    
    def build(self):
        #Abrimos en dev con las dimensiones de un movil por defecto
        Window.size = (400, 640)
        Window.top = 30
        
        # definimos el tema de la app
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "400"
        self.theme_cls.theme_style = "Light"

        

        # Load KV files
        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/cliente.kv")
        Builder.load_file("kv/empleado.kv")
        Builder.load_file("kv/admin.kv")
        Builder.load_file("kv/comentarios.kv")
        Builder.load_file("kv/filtros.kv")
        Builder.load_file("kv/nuevaactividad.kv")

        # Create screen manager
        self.sm = ScreenManager()
        
        # Create screens with app reference
        self.login_screen = LoginScreen(name="login")
        self.cliente_home_screen = ClienteHomeScreen(name="cliente_home")
        self.empleado_home_screen = EmpleadoHomeScreen(name="empleado_home")
        self.admin_home_screen = AdminHomeScreen(name="admin_home")
        self.comentarios_screen = ComentariosScreen(name="comentarios_home")
        self.valorar_screen = ValorarScreen(name="valorar")
        self.usuarios_gestion_screen = NuevoUsuarioScreen(
            on_save=self.on_usuario_guardado, 
            name="usuarios_gestion"
        )
        self.nueva_actividad_screen = NuevaActividadScreen(name="nueva_actividad")
        self.filtros_screen = FiltrosScreen(cliente_home_screen=self.cliente_home_screen, name="filter_screen")
        self.editar_actividad_screen = EditarActividadScreen(name="editar_actividad")

        # Add screens to manager first
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.cliente_home_screen)
        self.sm.add_widget(self.admin_home_screen)
        self.sm.add_widget(self.empleado_home_screen)
        self.sm.add_widget(self.comentarios_screen)
        self.sm.add_widget(self.valorar_screen)
        self.sm.add_widget(self.usuarios_gestion_screen)
        self.sm.add_widget(self.nueva_actividad_screen)
        self.sm.add_widget(self.filtros_screen)
        self.sm.add_widget(self.editar_actividad_screen)

        # Add app reference to screens
        for screen in [self.login_screen, self.cliente_home_screen, self.empleado_home_screen,
                      self.admin_home_screen, self.comentarios_screen, self.valorar_screen,
                      self.filtros_screen, self.usuarios_gestion_screen, self.nueva_actividad_screen,
                      self.editar_actividad_screen]:
            screen.app = self

        # Verificar sesión al iniciar
        if self.verify_session():
            # Variable home según el rol
            if self.rol_actual == "admin":
                self.home = self.admin_home_screen
            elif self.rol_actual == "cliente":
                self.home = self.cliente_home_screen
            elif self.rol_actual == "empleado":
                self.home = self.empleado_home_screen
            else:
                self.home = self.login_screen
            self.sm.current = self.home.name
        else:
            self.home = self.login_screen
            self.sm.current = "login"

        return self.sm

    def volver_atras(self):
        """Navega a la pantalla correspondiente según el rol del usuario."""
        self.sm.current = self.home.name

    def on_stop(self):
        """Close database connection when app stops."""
        self.db.close()

    def salir(self, instance=None):
        """Cierra la sesión y limpia el token"""
        self.token = None
        self.usuario_actual = None
        self.rol_actual = None
        self.usuario_actual_detalle = None
        self.sm.current = "login"
    
    def cancelar_edicion_usuario(self):
        self.root.current = 'empleado_home'  # O la pantalla a la que quieras volver


if __name__ == '__main__':
    App().run()