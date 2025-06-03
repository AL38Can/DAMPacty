from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.app import App
import datetime
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton

class NuevoUsuarioScreen(MDScreen):
    def __init__(self, on_save, **kwargs):
        super().__init__(**kwargs)
        self.on_save = on_save
        self.perfiles = ['empleado', 'cliente', 'admin']
        self.edit_email = None
        self._build_ui()

    def _build_ui(self):
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', padding=30, spacing=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        self.nombre_field = MDTextField(hint_text="Nombre completo", required=True)
        self.email_field = MDTextField(hint_text="Email", required=True)
        self.password_field = MDTextField(hint_text="Contraseña", password=True, required=True)
        self.telefono_field = MDTextField(hint_text="Teléfono")
        self.direccion_field = MDTextField(hint_text="Dirección")
        self.condiciones_field = MDTextField(hint_text="Condiciones médicas")
        self.gustos_field = MDTextField(hint_text="Gustos (ej: Noche/Día, Aventurero/Tranquilo)")

        # --- SOLO ADMIN VE "admin" EN EL DESPLEGABLE ---
        app = App.get_running_app()
        perfil_actual = getattr(app, "rol_actual", None) or getattr(app, "perfil_actual", None)
        if perfil_actual == "admin":
            perfiles_menu = self.perfiles
        else:
            perfiles_menu = [p for p in self.perfiles if p != "admin"]

        # Perfil con botón de selección
        perfil_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=56)
        self.perfil_field = MDTextField(hint_text="Perfil", readonly=True, required=True)
        perfil_btn = MDIconButton(icon="menu-down", on_release=lambda x: self.menu.open())
        perfil_layout.add_widget(self.perfil_field)
        perfil_layout.add_widget(perfil_btn)

        # Menú de selección
        menu_items = [
            {"viewclass": "OneLineListItem", "text": p.capitalize(), "on_release": lambda x=p: self._set_perfil(x)}
            for p in perfiles_menu
        ]
        self.menu = MDDropdownMenu(
            caller=self.perfil_field,
            items=menu_items,
            width_mult=3,
            position="top", 
        )
        self.perfil_field.bind(on_focus=lambda instance, value: self.menu.open() if value else None)

        # Add fields to layout
        layout.add_widget(self.nombre_field)
        layout.add_widget(self.email_field)
        layout.add_widget(self.password_field)
        layout.add_widget(self.telefono_field)
        layout.add_widget(self.direccion_field)
        layout.add_widget(self.condiciones_field)
        layout.add_widget(self.gustos_field)
        layout.add_widget(perfil_layout)  # Usa el nuevo layout para perfil

        # Buttons
        buttons_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        cancel_button = MDRaisedButton(
            text="Cancelar",
            on_release=self._cancelar
        )
        buttons_layout.add_widget(cancel_button)

        save_button = MDRaisedButton(
            text="Guardar",
            on_release=self._guardar
        )
        buttons_layout.add_widget(save_button)

        layout.add_widget(buttons_layout)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def _set_perfil(self, perfil):
        self.perfil_field.text = perfil.capitalize()
        self.menu.dismiss()

    def _guardar(self, *args):
        # Validate required fields
        if not self.nombre_field.text or not self.email_field.text or not self.password_field.text or not self.perfil_field.text:
            toast("Por favor, completa todos los campos obligatorios")
            return

        # Get database instance
        app = App.get_running_app()
        
        # Create user data
        usuario_data = {
            "password": self.password_field.text,
            "perfil": self.perfil_field.text.lower(),
            "nombre": self.nombre_field.text,
            "telefono": self.telefono_field.text,
            "direccion": self.direccion_field.text,
            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d"),
            "condiciones_medicas": self.condiciones_field.text,
            "gustos": self.gustos_field.text
        }

        # Save to database
        app.db.save_usuario(self.email_field.text, usuario_data)

        # Call on_save callback
        if self.on_save:
            self.on_save(self.email_field.text)

        # Clear fields
        self._limpiar_campos()

        toast("Usuario guardado con éxito")
        # Cambia a la pestaña de usuarios
        app.sm.current = "empleado_home"
        app.sm.get_screen('empleado_home').nav.switch_tab('usuarios')

    def _cancelar(self, *args):
        # Cambia a la pestaña de usuarios
        app = App.get_running_app()
        app.sm.current = "empleado_home"
        app.sm.get_screen('empleado_home').nav.switch_tab('usuarios')

    def _limpiar_campos(self):
        # Clear fields
        self.nombre_field.text = ""
        self.email_field.text = ""
        self.password_field.text = ""
        self.telefono_field.text = ""
        self.direccion_field.text = ""
        self.condiciones_field.text = ""
        self.gustos_field.text = ""
        self.perfil_field.text = ""
        self.email_field.disabled = False

    def set_usuario(self, email, datos):
        """Set the fields with user data for editing."""
        self.edit_email = email
        self.nombre_field.text = datos.get('nombre', '')
        self.email_field.text = email
        self.email_field.disabled = True  # no editable
        self.password_field.text = datos.get('password', '')
        self.telefono_field.text = datos.get('telefono', '')
        self.direccion_field.text = datos.get('direccion', '')
        self.condiciones_field.text = datos.get('condiciones_medicas', '')
        self.gustos_field.text = datos.get('gustos', '')
        self.perfil_field.text = datos.get('perfil', '').capitalize()


    # Renombra este método:
    def _refrescar_lista_usuarios(self, email_editado=None): 
        self._build_lists(email_resaltado=email_editado)
        app = App.get_running_app()
        app.sm.current = "empleado_home"
        if hasattr(app.sm.get_screen('empleado_home'), 'ids'):
            app.sm.get_screen('empleado_home').nav.switch_tab('usuarios')