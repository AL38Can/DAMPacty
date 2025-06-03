from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from src.screens.EmpleadoHomeScreen import UsuariosGestionScreen, EmpleadoActividadesScreen
from src.screens.NuevaActividadScreen import NuevaActividadScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import DictProperty
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.app import App

class EmpresaPanel(MDBoxLayout):
    fields = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        Clock.schedule_once(lambda dt: self.load_data())

    def load_data(self):
        """Datos empresa"""
        try:
            app = App.get_running_app()
            empresa = app.db.get_empresa()
            if empresa:
                self.fields = {k: type("Field", (), {"text": v})() for k, v in empresa.items()}
        except Exception as e:
            print(f"Error loading company data: {e}")

    def save_data(self, *args):
        """Guardar datos de la empresa"""
        try:
            app = App.get_running_app()  
            data = {key: self.ids[key].text for key in self.fields}
            app.db.save_empresa(data)
            toast("Datos de la empresa guardados con éxito")
        except Exception as e:
            print(f"Error saving company data: {e}")

    def on_fields(self, instance, value):
        # Update text fields when fields changes
        for key in self.fields:
            if key in self.ids:
                self.ids[key].text = self.fields[key].text

class AdminHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        nav = MDBottomNavigation()

        # Pestaña Nueva Actividad (igual que empleado)
        crear_tab = MDBottomNavigationItem(name='crear', text='Nueva Actividad', icon='plus-box')
        crear_tab.add_widget(NuevaActividadScreen(name="admin_nueva_actividad"))

        # Pestaña Actividades (igual que empleado)
        actividades_tab = MDBottomNavigationItem(name='actividades', text='Actividades', icon='clipboard-text')
        actividades_tab.add_widget(EmpleadoActividadesScreen(name="admin_actividades"))

        # Pestaña Usuarios (igual que empleado, pero con gestión real)
        usuarios_tab = MDBottomNavigationItem(name='usuarios', text='Usuarios', icon='account-group')
        usuarios_tab.add_widget(UsuariosGestionScreen(name="admin_usuarios_gestion"))

        # Pestaña Empresa (solo admin)
        empresa_tab = MDBottomNavigationItem(name='empresa', text='Empresa', icon='domain')
        empresa_tab.add_widget(EmpresaPanel())

        nav.add_widget(actividades_tab)
        nav.add_widget(crear_tab)
        nav.add_widget(usuarios_tab)
        nav.add_widget(empresa_tab)

        self.add_widget(nav)
        self.load_data()

    def load_data(self):
        """cargar datos de la empresa y usuarios"""
        try:
            app = App.get_running_app() 
        except Exception as e:
            print(f"Error loading admin data: {e}")