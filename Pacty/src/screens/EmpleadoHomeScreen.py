from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconRightWidget, IconLeftWidget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
import json
import os
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from .NuevaActividadScreen import NuevaActividadScreen
from kivy.app import App
from datetime import datetime, date
from kivy.uix.widget import Widget
from src.utils.format_date import formatear_fecha
from src.utils.database import Database
from .ClienteHomeScreen import ActividadCard
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.toast import toast
import functools
from kivymd.uix.pickers import MDDatePicker

class UsuariosGestionScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuarios_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.json')
        self.layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=(234/255, 221/255, 208/255, 1)
        )
        self.scroll = ScrollView()
        self.user_lists = {}
        self.perfiles = [ 'cliente','empleado', 'admin',]

        # Más separación arriba del título
        self.layout.add_widget(
            MDBoxLayout(
                size_hint_y=None,
                height=30  # Más separación arriba del título
            )
        )
        # Añadir título
        self.layout.add_widget(
            MDLabel(
                text="[b]Gestión de Usuarios[/b]",
                markup=True,
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=60,
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.2, 1),
                padding=(0, 10, 0, 0)
            )
        )
        

        # Añadir panel de filtros
        self._build_filters_panel()

        self._build_lists()
        self._build_add_button()
        self.add_widget(self.layout)

    def _build_filters_panel(self):
        
        # Contenedor vertical para título y filtros
        filters_outer = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=80,
            padding=[0, 10, 0, 0],
            spacing=10,
        )

        filters_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,  # Altura más estándar para botones y campos
            padding=[20, 0, 20, 0],
            spacing=16,
            pos_hint={"center_x": 0.5},
            md_bg_color=(234/255, 221/255, 208/255, 1),
        )

        self.filter_perfil = "todos"

        self.filter_name = MDTextField(
            hint_text="Filtrar por nombre",
            size_hint_x=0.5,
            size_hint_y=None,
            mode="rectangle",
            height=40,
            icon_left="magnify",
        )
        self.filter_name.bind(text=lambda instance, value: self._build_lists())

        perfiles_items = [
            {"viewclass": "OneLineListItem", "text": "Todos", "on_release": lambda x="todos": self._set_perfil_filter(x)},
            {"viewclass": "OneLineListItem", "text": "Empleado", "on_release": lambda x="empleado": self._set_perfil_filter(x)},
            {"viewclass": "OneLineListItem", "text": "Cliente", "on_release": lambda x="cliente": self._set_perfil_filter(x)},
            {"viewclass": "OneLineListItem", "text": "Admin", "on_release": lambda x="admin": self._set_perfil_filter(x)},
        ]


        self.perfil_menu = MDDropdownMenu(
            caller=None,
            items=perfiles_items,
            width_mult=3,
        )
        self.perfil_selector = MDRaisedButton(
            text="Todos",
            size_hint_x=0.5,
            height=40,
            size_hint_y=None,
            md_bg_color=(0.8, 0.8, 0.8, 1),
            on_release=lambda x: self.perfil_menu.open()
        )
        self.perfil_menu.caller = self.perfil_selector

        filters_layout.add_widget(self.filter_name)
        filters_layout.add_widget(self.perfil_selector)
        filters_outer.add_widget(filters_layout)
        self.layout.add_widget(filters_outer)

    def _set_perfil_filter(self, perfil):
        self.filter_perfil = perfil
        self.perfil_selector.text = perfil.capitalize() if perfil != "todos" else "Todos"
        self.perfil_menu.dismiss()
        self._build_lists()

    def _build_lists(self, email_resaltado=None):
        self.scroll.clear_widgets()
        container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[0, 10, 0, 0],
            spacing=0
        )
        container.bind(minimum_height=container.setter('height'))
        usuarios = self._load_usuarios()
        filtro_nombre = getattr(self, "filter_name", None)
        filtro_perfil = getattr(self, "filter_perfil", "todos")

        usuario_actual = getattr(self, "usuario_actual", None)
        perfil_actual = getattr(self, "perfil_actual", None)

        # print(f"Usuario actual: {usuario_actual}, Perfil actual: {perfil_actual}")

        for idx, perfil in enumerate(self.perfiles):
            if filtro_perfil != "todos" and perfil != filtro_perfil:
                continue
            if idx > 0:
                container.add_widget(
                    MDBoxLayout(
                        size_hint_y=None,
                        height=40
                    )
                )
            label = MDLabel(
                text=f"[b]{perfil.capitalize()}s[/b]",
                markup=True,
                halign="left",
                size_hint_y=None,
                height=24,
                padding=(20, 0),
                theme_text_color="Custom",
                text_color=(0.659, 0.620, 0.576, 1)
            )
            user_list = MDList()
            app = App.get_running_app()
            isadmin = getattr(app, "rol_actual", None) == "admin"
            for email, datos in usuarios.items():
                if datos.get('perfil') == perfil and email:
                    nombre = datos.get('nombre', '')
                    gustos = datos.get('gustos') or ''
                    if filtro_nombre and filtro_nombre.text:
                        if filtro_nombre.text.lower() not in nombre.lower():
                            continue
                    puede_editar = True
                    if datos.get('perfil') == "admin":
                        # Solo un admin puede editar admins
                        puede_editar =   isadmin
                    left_icon = IconLeftWidget(icon="account", theme_text_color="Custom", text_color=(0.659, 0.620, 0.576, 1))
                    # --- RESALTAR USUARIO EDITADO ---
                    if email_resaltado and email == email_resaltado:
                        # Icono usuario a la izquierda
                        left_icon = IconLeftWidget(
                            icon="account",
                            theme_text_color="Custom",
                            text_color=(0.659, 0.620, 0.576, 1)
                        )
                        item = OneLineAvatarIconListItem(
                            text=f"{nombre}",
                            theme_text_color="Custom",
                            text_color=(0.14, 0.80, 0.73, 1),
                        )
                        item.add_widget(left_icon)

                        if puede_editar:
                            edit_icon = IconRightWidget(
                                icon="pencil",
                                theme_text_color="Custom",
                                text_color=(20/255, 203/255, 186/255, 1)
                            )
                            item.add_widget(edit_icon)
                            item.on_release = functools.partial(self._editar_usuario, email)
                    else:
                        item = OneLineAvatarIconListItem(
                            text=f"{nombre}",
                            theme_text_color="Custom",
                            text_color=(0.659, 0.620, 0.576, 1)
                        )
                        item.add_widget(left_icon)
                        if puede_editar:
                            edit_icon = IconRightWidget(
                                icon="pencil",
                                theme_text_color="Custom",
                                text_color=(20/255, 203/255, 186/255, 1)
                            )
                            item.add_widget(edit_icon)
                            item.on_release = functools.partial(self._editar_usuario, email)
                    # --- FIN RESALTADO ---

                    user_list.add_widget(item)
            container.add_widget(label)
            container.add_widget(
                MDBoxLayout(size_hint_y=None, height=2)
            )
            container.add_widget(user_list)
            self.user_lists[perfil] = user_list
        self.scroll.add_widget(container)
        if len(self.layout.children) > 0:
            self.layout.remove_widget(self.scroll)
        self.layout.add_widget(self.scroll)

    def _build_add_button(self):
        btn_layout = MDBoxLayout(
            size_hint_y=None,
            height=80,
            padding=[0, 40, 0, 25],
            orientation="horizontal"
        )
        btn_layout.add_widget(MDBoxLayout(size_hint_x=0.25))
        btn = MDRaisedButton(
            text="Añadir Usuario",
            size_hint_x=0.5,
            pos_hint={"center_x": 0.5},
            md_bg_color=(20/255, 203/255, 186/255, 1)
        )
        btn.bind(on_release=self._ir_a_nuevo_usuario)
        btn_layout.add_widget(btn)
        btn_layout.add_widget(MDBoxLayout(size_hint_x=0.30))
        self.layout.add_widget(btn_layout)

    def _ir_a_nuevo_usuario(self, *args):
        from .NuevoUsuarioScreen import NuevoUsuarioScreen

        def on_save():
            self._build_lists()
            # Volver a la pestaña de usuarios
            app = App.get_running_app()
            app.sm.current = "empleado_home"
            if hasattr(app.sm.get_screen('empleado_home'), 'ids'):
                app.sm.get_screen('empleado_home').nav.switch_tab('usuarios')

        app = App.get_running_app()
        sm = app.sm

        # Verificar si ya existe la pantalla
        if not sm.has_screen("nuevo_usuario"):
            nuevo_screen = NuevoUsuarioScreen(on_save=on_save, name="nuevo_usuario")
            sm.add_widget(nuevo_screen)
        else:
            nuevo_screen = sm.get_screen("nuevo_usuario")
            # Limpiar campos por si acaso
            nuevo_screen._cancelar()

        sm.current = "nuevo_usuario"

    def _editar_usuario(self, email):
        from .NuevoUsuarioScreen import NuevoUsuarioScreen
        usuarios = self._load_usuarios()
        datos = usuarios.get(email, {})

        def on_save(email_editado=None):
            self._build_lists(email_resaltado=email_editado)
            app = App.get_running_app()
            app.sm.current = "empleado_home"
            if hasattr(app.sm.get_screen('empleado_home'), 'ids'):
                app.sm.get_screen('empleado_home').nav.switch_tab('usuarios')

        app = App.get_running_app()
        sm = app.sm

        # Verificar si ya existe la pantalla
        if not sm.has_screen("nuevo_usuario"):
            editar_screen = NuevoUsuarioScreen(on_save=on_save, name="nuevo_usuario")
            sm.add_widget(editar_screen)
        else:
            editar_screen = sm.get_screen("nuevo_usuario")

        editar_screen.set_usuario(email, datos)
        sm.current = "nuevo_usuario"

    def _load_usuarios(self):
        """Carga los usuarios"""
        app = App.get_running_app()
        return app.db.get_all_usuarios()

    def _save_usuarios(self, usuarios):
        with open(self.usuarios_path, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)

class EmpleadoActividadesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.actividades = self.db.get_all_actividades()
        config = self.db.get_configuracion()
        self.iconos_categorias = config["iconos_categorias"]
        self.color_categorias = config["color_categorias"]
        
        # Filtros
        self.filtro_nombre = ""
        self.filtro_categoria = []
        self.filtro_fecha_desde = date.today().strftime("%Y-%m-%d")
        self.filtro_fecha_hasta = ""
        self.filtro_estado = None  # None = todas, True = activas, False = inactivas
        
        # Layout principal
        self.layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=(234/255, 221/255, 208/255, 1)
        )
        
        # Título
        self.layout.add_widget(
            MDLabel(
                text="[b]Gestión de Actividades[/b]",
                markup=True,
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=60,
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.2, 1),
                padding=(0, 10, 0, 0)
            )
        )
        
        # Panel de filtros
        self._build_filters_panel()
        
        # Lista de actividades
        self.scroll = ScrollView()
        self.actividad_list = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=8,
            padding=[24, 16, 24, 16]
        )
        self.actividad_list.bind(minimum_height=self.actividad_list.setter('height'))
        self.scroll.add_widget(self.actividad_list)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
        
        # Cargar actividades iniciales
        self.cargar_actividades()

    def _build_filters_panel(self):
        filters_outer = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=80,
            padding=[0, 10, 0, 0],
            spacing=10,
        )

        filters_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48, 
            padding=[20, 0, 20, 0],
            spacing=16,
            pos_hint={"center_x": 0.5},
            md_bg_color=(234/255, 221/255, 208/255, 1),
        )

        # Crear menú desplegable para estado
        estado_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Todas",
                "on_release": lambda x="todas": self._set_estado_filter(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Activas",
                "on_release": lambda x="activas": self._set_estado_filter(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Inactivas",
                "on_release": lambda x="inactivas": self._set_estado_filter(x)
            }
        ]
        
        self.estado_menu = MDDropdownMenu(
            caller=None,
            items=estado_items,
            width_mult=3,
        )
        
        # Crear el botón de estado
        self.estado_button = MDRaisedButton(
            text="Todas",
            size_hint_x=None,
            width="120dp",
            pos_hint={"center_x": 0.2},
            on_release=lambda x: self.estado_menu.open()
        )
        self.estado_menu.caller = self.estado_button
        
        # Crear icono de filtros
        self.filtros_icon = MDIconButton(
            icon="filter-variant",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self.abrir_panel_filtros()
        )

        # Añade el icono después del botón de estado
        filters_layout.add_widget(MDBoxLayout(size_hint_x=0.3))  # Espacio izquierdo
        filters_layout.add_widget(self.estado_button)
        filters_layout.add_widget(self.filtros_icon)
        filters_layout.add_widget(MDBoxLayout(size_hint_x=0.3))  # Espacio derecho

        filters_outer.add_widget(filters_layout)
        self.layout.add_widget(filters_outer)
    
    def abrir_panel_filtros(self):
        """Abre un diálogo para filtrar actividades."""
        if hasattr(self, 'dialog_filtros') and self.dialog_filtros:
            self.dialog_filtros.dismiss()

        nombre_field = MDTextField(
            hint_text="Nombre o descripción",
            text=self.filtro_nombre,
            size_hint_y=None,
            height=48,
        )
        fecha_desde_field = MDTextField(
            hint_text="Desde (YYYY-MM-DD)",
            text=self.filtro_fecha_desde or "",
            size_hint_y=None,
            height=48,
        )
        fecha_hasta_field = MDTextField(
            hint_text="Hasta (YYYY-MM-DD)",
            text=self.filtro_fecha_hasta or "",
            size_hint_y=None,
            height=48,
        )

        def on_aplicar_filtros(*args):
            self.filtro_nombre = nombre_field.text
            self.filtro_fecha_desde = fecha_desde_field.text
            self.filtro_fecha_hasta = fecha_hasta_field.text
            self.dialog_filtros.dismiss()
            self.cargar_actividades()

        # Layout del contenido con padding superior para evitar solapamiento
        content = MDBoxLayout(
            orientation="vertical",
            spacing=12,
            padding=[12, 24, 12, 12],  # padding top aumentado
            size_hint_y=None,
        )
        content.add_widget(nombre_field)
        content.add_widget(fecha_desde_field)
        content.add_widget(fecha_hasta_field)
        content.height = 300

        self.dialog_filtros = MDDialog(
            title="Filtrar actividades",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog_filtros.dismiss()),
                MDFlatButton(text="Aplicar", on_release=on_aplicar_filtros)
            ]
        )
        self.dialog_filtros.open()

    def _set_estado_filter(self, estado):
        if estado == "todas":
            self.filtro_estado = None
            self.estado_button.text = "Todas"
        elif estado == "activas":
            self.filtro_estado = True
            self.estado_button.text = "Activas"
        else:  # inactivas
            self.filtro_estado = False
            self.estado_button.text = "Inactivas"
        
        self.estado_menu.dismiss()
        self.cargar_actividades()

    def parse_date(self, date_str):
        """Parsea una fecha en formato YYYY-MM-DD o DD/MM/YYYY."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                return None

    def cargar_actividades(self, id_resaltado=None):
        """Carga las actividades disponibles y las muestra en tarjetas, agrupadas por fecha."""
        self.actividad_list.clear_widgets()
        
        actividades_filtradas = []
        
        for act in self.actividades:
            # Filtro por estado
            if self.filtro_estado is not None and act.get("activo", True) != self.filtro_estado:
                continue

            # Filtro por categoría
            if self.filtro_categoria and act["categoria"] not in self.filtro_categoria:
                continue

            # Filtro por nombre o descripción
            if self.filtro_nombre:
                nombre = act.get("nombre", "")
                descripcion = act.get("descripcion", "")
                if self.filtro_nombre.lower() not in nombre.lower() and self.filtro_nombre.lower() not in descripcion.lower():
                    continue

            # Filtro por fecha
            act_date = self.parse_date(act["fecha"])
            if not act_date:
                continue

            if self.filtro_fecha_desde:
                desde_date = self.parse_date(self.filtro_fecha_desde)
                if not desde_date or act_date < desde_date:
                    continue

            if self.filtro_fecha_hasta:
                hasta_date = self.parse_date(self.filtro_fecha_hasta)
                if not hasta_date or act_date > hasta_date:
                    continue

            actividades_filtradas.append(act)

        actividades_ordenadas = sorted(actividades_filtradas, key=lambda x: x["fecha"])
        fecha_actual = None
        primer_bloque = True
        
        for act in actividades_ordenadas:
            # Si la fecha cambia, añade un título de sección con fondo
            if act["fecha"] != fecha_actual:
                fecha_actual = act["fecha"]
                fecha_titulo = formatear_fecha(fecha_actual)
                # Añadir separación extra entre bloques de fecha (excepto el primero)
                if not primer_bloque:
                    self.actividad_list.add_widget(Widget(size_hint_y=None, height=32))
                else:
                    primer_bloque = False
                titulo_fecha = MDBoxLayout(
                    md_bg_color=(0.72, 0.94, 0.92, 1),
                    radius=[12, 12, 12, 12],
                    size_hint_y=None,
                    height=38,
                    padding=(8, 0),
                )
                titulo_fecha.add_widget(MDLabel(
                    text=f"[b]{fecha_titulo}[/b]",
                    markup=True,
                    theme_text_color="Custom",
                    text_color=(0.13, 0.33, 0.27, 1),
                    halign="center",
                    valign="middle",
                    font_style="Subtitle1"
                ))
                self.actividad_list.add_widget(titulo_fecha)
            
            # Añadir separación entre el título y la tarjeta
            self.actividad_list.add_widget(Widget(size_hint_y=None, height=4))
            
            # Crear y añadir la tarjeta de actividad
            card = ActividadCard(
                act,
                self.iconos_categorias,
                self.color_categorias,
                self.parse_date,
                on_comentarios_callback=self.mostrar_comentarios,
                on_detalles_callback=self.mostrar_detalles
            )
            # Resalta la tarjeta si es la editada
            if id_resaltado is not None and act.get("id") == id_resaltado:
                card.md_bg_color = (0.14, 0.80, 0.73, 0.25)
            self.actividad_list.add_widget(card)
            self.actividad_list.add_widget(Widget(size_hint_y=None, height=4))

    def mostrar_comentarios(self, actividad):
        """Muestra los comentarios de una actividad en un cuadro de diálogo."""
        comentarios = actividad.get("comentarios", [])
        if not comentarios:
            toast("Esta actividad no tiene comentarios.")
            return

        contenido = "\n\n".join(
            [f"[b]{c['usuario']}:[/b] {c['comentario']} (Puntuación: {c.get('puntuacion', 'N/A')}/5)" for c in comentarios]
        )

        self.dialog = MDDialog(
            title=f"Comentarios de {actividad['nombre']}",
            text=contenido.strip(),
            size_hint=(0.85, None),
            buttons=[
                MDFlatButton(
                    text="Cerrar",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def mostrar_detalles(self, actividad):
        """Muestra los detalles de una actividad en un cuadro de diálogo."""
        fecha_formateada = formatear_fecha(actividad['fecha'])
        plazas_disponibles = actividad["plazas"] - len(actividad["inscritos"])
        
        # Obtener comentarios y puntuaciones
        comentarios = actividad.get("comentarios", [])
        num_comentarios = len(comentarios)
        puntuaciones = [c['puntuacion'] for c in comentarios if 'puntuacion' in c]
        num_votaciones = len(puntuaciones)
        media_puntuacion = sum(puntuaciones) / num_votaciones if num_votaciones > 0 else 0

        # Crear contenido personalizado
        contenido = MDBoxLayout(orientation="vertical", spacing="12dp", padding="12dp", size_hint_y=None)
        contenido.bind(minimum_height=contenido.setter("height"))

        def add_label(texto):
            label = MDLabel(
                text=texto,
                markup=True,
                size_hint_y=None,
                height=self.theme_cls.font_styles["Body1"][1] * 2.2
            )
            contenido.add_widget(label)

        add_label(f"[b]Descripción:[/b] {actividad['descripcion']}")
        add_label(f"[b]Lugar:[/b] {actividad['lugar']}")
        add_label(f"[b]Fecha:[/b] {fecha_formateada} a las {actividad['hora']}")
        add_label(f"[b]Plazas disponibles:[/b] {plazas_disponibles}")
        add_label(f"[b]Valoraciones:[/b] {media_puntuacion:.1f}/5 [{num_votaciones} voto(s)]")
        
        # Comentarios con ícono al lado
        fila_comentarios = MDBoxLayout(orientation="horizontal", spacing="8dp", size_hint_y=None, height="48dp")
        comentario_label = MDLabel(
            text=f"[b]Comentarios:[/b] {num_comentarios}",
            markup=True,
            halign="left"
        )
        fila_comentarios.add_widget(comentario_label)

        if num_comentarios > 0:
            fila_comentarios.add_widget(MDIconButton(
                icon="comment-text-outline",
                on_release=lambda x: (
                    self.dialog.dismiss(),
                    self.ir_a_comentarios(actividad)
                ),
                theme_text_color="Custom",
                text_color=(0.0, 0.6, 0.5, .5)
            ))

        contenido.add_widget(fila_comentarios)

        # Botones del diálogo
        botones = [
            MDFlatButton(
                text="Cerrar", 
                on_release=lambda x: self.dialog.dismiss(),
                md_bg_color=(0.596, 0.596, 0.596, 0.5),
                text_color=(1, 1, 1, 1)
            ),
            MDFlatButton(
                text="Editar", 
                on_release=lambda x: self.editar_actividad(actividad),
                md_bg_color=(0.0, 0.6, 0.5, .5),
                text_color=(1, 1, 1, 1)
            )
        ]

        # Crear y mostrar el diálogo
        self.dialog = MDDialog(
            title=actividad['nombre'],
            type="custom",
            content_cls=contenido,
            buttons=botones,
            size_hint=(0.85, None)
        )
        self.dialog.open()

    def editar_actividad(self, actividad):
        """Navega a la pantalla de edición de actividad."""
        self.dialog.dismiss()
        app = App.get_running_app()
        sm = app.sm  # Accede al ScreenManager principal
        editar_screen = sm.get_screen("editar_actividad")
        editar_screen.set_actividad(actividad)
        sm.current = "editar_actividad"

    def ir_a_comentarios(self, actividad):
        """Navega a la pantalla de comentarios."""
        app = App.get_running_app()
        sm = app.sm
        sm.current = 'comentarios_home'
        sm.get_screen('comentarios_home').cargar_comentarios(actividad)



class EmpleadoHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal vertical
        main_layout = MDBoxLayout(orientation="vertical")
        
        # Barra superior con icono de salida alineado a la derecha
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="30dp",
            padding=[0, 0, 8, 0],  # padding derecho
            md_bg_color=(234/255, 221/255, 208/255, 1)
        )
        top_bar.add_widget(Widget())  # Espacio a la izquierda
        icono_salida = MDIconButton(
            icon="assets/icons/icon-exit.png",
            user_font_size="24dp",
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self.salir()
        )
        top_bar.add_widget(icono_salida)
        main_layout.add_widget(top_bar)
        
        nav = MDBottomNavigation()
        self.nav = nav

        # Crear NuevaActividadScreen con el nombre del screen manager
        nueva_actividad = NuevaActividadScreen(name="nueva_actividad")
        nueva_actividad.bind(on_save=self.refresh_actividades)
        
        crear_tab = MDBottomNavigationItem(name='crear', text='Nueva Actividad', icon='plus-box')
        crear_tab.add_widget(nueva_actividad)
        
        actividades_tab = MDBottomNavigationItem(name='actividades', text='Actividades', icon='clipboard-text')
        actividades_screen = EmpleadoActividadesScreen(name="empleado_actividades")
        actividades_tab.add_widget(actividades_screen)

        # Añade el evento para refrescar al cambiar de tab
        def on_tab_switch(instance_tabs, instance_tab, instance_tab_label, tab_text):
            if tab_text == "Actividades":
                self.refresh_actividades()
        nav.bind(on_tab_switch=on_tab_switch)

        usuarios_tab = MDBottomNavigationItem(name='usuarios', text='Usuarios', icon='account-group')
        usuarios_tab.add_widget(UsuariosGestionScreen(name="usuarios_gestion"))
        
        nav.add_widget(actividades_tab)
        nav.add_widget(crear_tab)
        nav.add_widget(usuarios_tab)
        
        main_layout.add_widget(nav)
        self.add_widget(main_layout)

    def refresh_actividades(self, id_resaltado=None):
        """Refresca los datos de las actividades en todas las pantallas relevantes."""
        # Encontrar la pestaña de actividades
        for tab in self.nav.children:
            if getattr(tab, "name", "") == "actividades":
                actividades_screen = tab.children[0]
                if actividades_screen:
                    # Recargar actividades
                    actividades_screen.actividades = actividades_screen.db.get_all_actividades()
                    # Cargar actividades con el ID resaltado si se proporciona
                    actividades_screen.cargar_actividades(id_resaltado=id_resaltado)
                    # Asegurarse de que estamos en la pestaña de actividades
                    self.nav.switch_tab('actividades')
                break

    def on_pre_enter(self):
        """Se llama antes de entrar a la pantalla."""
        # Recargar datos de todas las pestañas
        if hasattr(self, 'nav'):
            for tab in self.nav.children:
                # Refrescar pantalla de actividades
                if getattr(tab, "name", "") == "actividades":
                    actividades_screen = tab.children[0]
                    if actividades_screen:
                        actividades_screen.actividades = actividades_screen.db.get_all_actividades()
                        actividades_screen.cargar_actividades()
                
                # Refrescar pantalla de usuarios
                elif getattr(tab, "name", "") == "usuarios":
                    usuarios_screen = tab.children[0]
                    if usuarios_screen:
                        usuarios_screen._build_lists()
                
                # Refrescar pantalla de nueva actividad
                elif getattr(tab, "name", "") == "crear":
                    nueva_actividad_screen = tab.children[0]
                    if nueva_actividad_screen:
                        # Limpiar campos si es necesario
                        if hasattr(nueva_actividad_screen, '_cancelar'):
                            nueva_actividad_screen._cancelar()

    def salir(self):
        """Cierra la sesión y vuelve a la pantalla de login."""
        app = App.get_running_app()
        # Limpiar datos de usuario
        app.rol_actual = None
        app.usuario_actual = None
        app.usuario_actual_detalle = None
        # Volver a la pantalla de login
        self.manager.current = "login"

def get_all_usuarios(self):
    """Devuelve todos los usuarios como un diccionario {email: datos}."""
    cursor = self.conn.cursor()
    cursor.execute("SELECT email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos FROM usuarios")
    usuarios = {}
    for row in cursor.fetchall():
        email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos = row
        usuarios[email] = {
            "password": password,
            "perfil": perfil,
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "fecha_registro": fecha_registro,
            "condiciones_medicas": condiciones_medicas,
            "gustos": gustos
        }
    return usuarios

def cargar_actividades(self):
    self.actividades = self.db.get_all_actividades()
    app = App.get_running_app()
    return app.db.get_all_actividades()