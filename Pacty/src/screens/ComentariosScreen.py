from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.button import MDRaisedButton
from kivymd.app import App

class ComentariosScreen(MDScreen):
    def cargar_comentarios(self, actividad):
        """Carga los comentarios y votaciones de la actividad."""
        self.ids.comentarios_list.clear_widgets()
        comentarios = actividad.get("comentarios", [])
        titulo = actividad.get("nombre", "Actividad sin título")
        self.ids.titulo_actividad.text = titulo

        # Cambia el color de fondo del header
        if hasattr(self.ids, "header_box"):
            self.ids.header_box.md_bg_color = (20/255, 203/255, 186/255, 1) 


        for comentario in comentarios:
            # Crear un contenedor de comentarios con borde
            comentario_card = MDCard(
                orientation="vertical",
                padding=dp(10),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(220),  # Ajusta el tamaño de cada comentario
                radius=[dp(10)],  # Bordes redondeados
                elevation=5,  # Sombra para darle un poco de profundidad
                md_bg_color=(1, 1, 1, 1),  # Fondo blanco para la tarjeta
            )

            # Contenedor del usuario con el icono
            comentario_box = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))

            # Icono de perfil
            icono_perfil = IconLeftWidget(icon="account-circle")
            comentario_box.add_widget(icono_perfil)

            # Etiqueta de usuario
            usuario_label = MDLabel(
                text=comentario.get("usuario", "Anónimo"),
                theme_text_color="Primary",
                bold=True,
                font_style="H6"
            )
            comentario_box.add_widget(usuario_label)

            # Etiqueta de fecha
            fecha = comentario.get("fecha", "")
            if fecha:
                fecha_label = MDLabel(
                    text=fecha,
                    theme_text_color="Hint",
                    font_style="Caption",
                    halign="right",
                    size_hint_x=None,
                    width=dp(120)
                )
                comentario_box.add_widget(fecha_label)

            comentario_card.add_widget(comentario_box)

            # Comentario
            comentario_label = MDLabel(
                text=comentario.get("comentario", ""),
                theme_text_color="Secondary",
                size_hint_y=None,
                text_size=(self.width - dp(32), None),
                halign="left",
                valign="top",
                font_style="Body1"
            )
            comentario_label.bind(texture_size=comentario_label.setter('size'))
            comentario_card.add_widget(comentario_label)

            # Puntuación
            puntuacion_label = MDLabel(
                text=f"Puntuación: {comentario.get('puntuacion', 'N/A')}/5",
                theme_text_color="Hint",
                italic=True,
                font_style="Body2"
            )
            comentario_card.add_widget(puntuacion_label)

            # Añadir comentario a la lista
            self.ids.comentarios_list.add_widget(comentario_card)
        
        # Botón de salir
        salir_btn = MDRaisedButton(
            text="Salir",
            md_bg_color=(20/255, 203/255, 186/255, 1),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: App.get_running_app().volver_atras()
        )
        self.ids.comentarios_list.add_widget(salir_btn)
