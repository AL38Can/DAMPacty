from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen

class ValorarScreen(MDScreen):
    def valorarActividad(self, actividad):
        """Construye la interfaz de la pantalla."""
        self.actividad = actividad
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Título
        layout.add_widget(MDLabel(
            text=f"Valorar {actividad['nombre']}",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=40
        ))

        layout.add_widget(Widget(size_hint_y=0.05))  # Espaciador

        # Estrellas para puntuación
        layout.add_widget(MDLabel(
            text="Puntúa esta actividad:",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            height=30
        ))

        self.puntuacion = 5  # Valor por defecto

        stars_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=5)
        self.stars = []
        for i in range(1, 6):
            star = MDIconButton(
                icon="star" if i <= self.puntuacion else "star-outline",
                theme_text_color="Custom",
                text_color=(1, 0.8, 0, 1),
                on_release=lambda btn, idx=i: self.set_puntuacion(idx)
            )
            self.stars.append(star)
            stars_layout.add_widget(star)
        layout.add_widget(stars_layout)

        layout.add_widget(Widget(size_hint_y=0.05))

        # Campo de comentario
        layout.add_widget(MDLabel(
            text="Escribe tu comentario:",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            height=30
        ))

        self.comment_field = MDTextField(
            multiline=True,
            size_hint_y=None,
            height=100
        )
        layout.add_widget(self.comment_field)

        # Botones
        buttons_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            spacing=10,
            padding=[0, 20, 0, 0]
        )

        cancel_button = MDFlatButton(
            text="Cancelar",
            on_release=self.cancelar
        )
        buttons_layout.add_widget(cancel_button)

        send_button = MDRaisedButton(
            text="Enviar",
            on_release=self.enviar_valoracion
        )
        buttons_layout.add_widget(send_button)

        layout.add_widget(buttons_layout)

        self.clear_widgets()
        self.add_widget(layout)

    def set_puntuacion(self, value):
        """Actualiza la puntuación y las estrellas."""
        self.puntuacion = value
        for i, star in enumerate(self.stars):
            star.icon = "star" if i < value else "star-outline"

    def enviar_valoracion(self):
        """Envía la valoración del usuario y la guarda en la base de datos."""
        puntuacion = self.puntuacion
        comentario = self.comment_field.text.strip()

        # Get current user
        app = self.manager.get_screen('app')
        usuario_actual = app.usuario_actual_detalle

        # Add comment to database
        app.db.add_comentario(
            self.actividad['id'],
            usuario_actual['email'],
            comentario,
            puntuacion
        )

        toast("Valoración enviada con éxito.")
        self.manager.current = "cliente_home"  # Volver a la pantalla principal

    def cancelar(self, instance=None):
        """Cancela la valoración y vuelve a la pantalla anterior."""
        self.manager.current = "cliente_home"  # Volver a la pantalla principal