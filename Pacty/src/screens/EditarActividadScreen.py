from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.app import App
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivymd.toast import toast

class EditarActividadScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.actividad = None
        self.layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))  # Para que el scroll funcione

        self.nombre = MDTextField(hint_text="Nombre")
        self.descripcion = MDTextField(hint_text="Descripción")
        self.fecha = MDTextField(hint_text="Fecha (YYYY-MM-DD)")
        self.hora = MDTextField(hint_text="Hora (HH:MM)")
        self.lugar = MDTextField(hint_text="Lugar")
        self.plazas = MDTextField(hint_text="Plazas", input_filter="int")
        self.categoria = MDTextField(hint_text="Categoría")
        # Checkbox para activo/inactivo
        self.checkbox_activo = MDCheckbox(active=True)
        activo_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=12)
        activo_layout.add_widget(self.checkbox_activo)
        activo_layout.add_widget(MDLabel(text="Activo", valign="middle"))
        # Añadir widgets
        self.layout.add_widget(self.nombre)
        self.layout.add_widget(self.descripcion)
        self.layout.add_widget(self.fecha)
        self.layout.add_widget(self.hora)
        self.layout.add_widget(self.lugar)
        self.layout.add_widget(self.plazas)
        self.layout.add_widget(self.categoria)
        self.layout.add_widget(activo_layout)

        # Nuevo layout horizontal para los botones
        botones_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,
            spacing=12
        )
        botones_layout.add_widget(
            MDRaisedButton(text="Guardar", on_release=self.guardar)
        )
        botones_layout.add_widget(
            MDFlatButton(text="Cancelar", on_release=self.cancelar)
        )
        self.layout.add_widget(botones_layout)

        scroll = ScrollView()
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

    def set_actividad(self, actividad):
        self.actividad = actividad
        self.nombre.text = actividad.get("nombre", "")
        self.descripcion.text = actividad.get("descripcion", "")
        self.fecha.text = actividad.get("fecha", "")
        self.hora.text = actividad.get("hora", "")
        self.lugar.text = actividad.get("lugar", "")
        self.plazas.text = str(actividad.get("plazas", ""))
        self.categoria.text = actividad.get("categoria", "")
        self.checkbox_activo.active = actividad.get("activo", True)

    def guardar(self, *args):
        app = App.get_running_app()
        db = app.db
        datos = {
            "id": self.actividad["id"],
            "nombre": self.nombre.text,
            "descripcion": self.descripcion.text,
            "fecha": self.fecha.text,
            "hora": self.hora.text,
            "lugar": self.lugar.text,
            "plazas": int(self.plazas.text),
            "categoria": self.categoria.text,
            "activo": self.checkbox_activo.active
        }
        db.save_actividad(datos)

        # Obtener la pantalla de empleado_home y refrescar datos
        if app.sm.has_screen("empleado_home"):
            empleado_home = app.sm.get_screen("empleado_home")
            if hasattr(empleado_home, "refresh_actividades"):
                # Primero refrescar los datos
                empleado_home.refresh_actividades(datos["id"])
                # Luego cambiar de pantalla
                Clock.schedule_once(lambda dt: setattr(app.sm, 'current', 'empleado_home'), 0.1)
        elif app.sm.has_screen("admin_home"):
            app.sm.current = "admin_home"

    def cancelar(self, *args):
        app = App.get_running_app()
        if app.sm.has_screen("empleado_home"):
            app.sm.current = "empleado_home"
        elif app.sm.has_screen("admin_home"):
            app.sm.current = "admin_home"
