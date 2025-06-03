from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton  
from kivymd.toast import toast
from datetime import datetime, date
import re
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDIcon
from kivy.utils import get_color_from_hex
from kivy.uix.widget import Widget
from kivymd.uix.chip import ( MDChipText, MDChip )
from src.utils.format_date import formatear_fecha
from kivy.app import App
from src.utils.database import Database
import sqlite3
from kivymd.uix.menu import MDDropdownMenu

class ActividadCard(MDCard):
    def __init__(self, actividad, iconos_categorias, color_categorias, parse_date_func, on_comentarios_callback=None, on_detalles_callback=None, padding_izquierda=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [16, 12, 16, 12]
        self.size_hint = (1, None)
        self.height = self.minimum_height
        self.bind(minimum_height=self.setter("height"))
        self.radius = [15, 15, 15, 15]
        self.elevation = 0  # sombra
        self.md_bg_color = (1, 1, 1, 1)
        self.ripple_behavior = True

        # Hacer que toda la tarjeta sea clicable para mostrar detalles
        if on_detalles_callback:
            self.on_release = lambda: on_detalles_callback(actividad)

        # Indicador de estado (punto)
        estado_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=20,
            padding=[0, 0, 0, 0]
        )
        estado_layout.add_widget(Widget(size_hint_x=1))  # Espaciador
        estado_punto = MDIcon(
            icon="circle",
            theme_text_color="Custom",
            text_color=(0, 0.8, 0, 1) if actividad.get("activo", True) else (0.8, 0, 0, 1),
            size_hint=(None, None),
            size=(16, 16),
            pos_hint={"center_y": 0.5}
        )
        estado_layout.add_widget(estado_punto)
        self.add_widget(estado_layout)

        # Cabecera: icono de categoría + nombre
        cabecera = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
            spacing=8,
            padding=[16, 0, 0, 10] if padding_izquierda else [0, 0, 0, 10]
        )
        icono_categoria = iconos_categorias.get(actividad.get("categoria", ""), "tag")
        color_categoria = color_categorias.get(actividad.get("categoria", ""), "#BDBDBD")
        cabecera.add_widget(MDIcon(
            icon=icono_categoria,
            theme_text_color="Custom",
            text_color=color_categoria,
            font_size=28,
            pos_hint={"center_y": 0.5}
        ))
        cabecera.add_widget(MDLabel(
            text=f"[b]{actividad['nombre']}[/b]",
            markup=True,
            font_style="H6",
            theme_text_color="Primary",
            size_hint_x=0.8,
            padding=[12, 0] if padding_izquierda else [0, 0] 
        ))
        self.add_widget(cabecera)

        # Info: chip de categoría, fecha, lugar
        info = MDBoxLayout(
            orientation="vertical",
            spacing=6,
            padding=[4, 8, 4, 8],
            size_hint_y=None,
            height=self.minimum_height
        )
        info.bind(minimum_height=info.setter("height"))

        # Chip de categoría
        chip = MDChip(
            MDChipText(
                text=actividad.get("categoria", "Otra"),
                theme_text_color="Secondary",
            ),
            md_bg_color=get_color_from_hex(color_categoria),
            height=30,
            radius=[14, 14, 14, 14],
        )
        info.add_widget(chip)

        # Fecha y hora (nuevo formato)
        fecha_obj = parse_date_func(actividad["fecha"])
        if fecha_obj:
            fecha_formateada = fecha_obj.strftime("%d de %B de %Y")
        else:
            fecha_formateada = actividad["fecha"]
        fecha_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        fecha_layout.add_widget(
            MDIcon(
                icon="calendar-month",
                theme_text_color="Secondary",
                pos_hint={"center_y": 0.5},
                size_hint_x=None,
                width=24
            )
        )
        fecha_layout.add_widget(
            MDLabel(
                text=f"{fecha_formateada} • {actividad['hora']}",
                theme_text_color="Secondary"
            )
        )
        info.add_widget(fecha_layout)

        # Lugar (nuevo formato)
        lugar_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        lugar_layout.add_widget(
            MDIcon(
                icon="map-marker",
                theme_text_color="Secondary",
                pos_hint={"center_y": 0.5},
                size_hint_x=None,
                width=24
            )
        )
        lugar_layout.add_widget(
            MDLabel(
                text=actividad["lugar"],
                theme_text_color="Secondary"
            )
        )
        info.add_widget(lugar_layout)

        # Plazas disponibles
        plazas_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=30)
        plazas_disponibles = actividad["plazas"] - len(actividad.get("inscritos", []))
        plazas_layout.add_widget(
            MDIcon(
                icon="account-group",
                theme_text_color="Secondary",
                pos_hint={"center_y": 0.5},
                size_hint_x=None,
                width=24
            )
        )
        plazas_layout.add_widget(
            MDLabel(
                text=f"Plazas disponibles: {plazas_disponibles}/{actividad['plazas']}",
                theme_text_color="Secondary"
            )
        )
        info.add_widget(plazas_layout)

        self.add_widget(info)

        # Separador
        self.add_widget(
            MDBoxLayout(
                size_hint_y=None,
                height=1,
                md_bg_color=[0.9, 0.9, 0.9, 1],
                padding=[8, 8, 8, 8]
            )
        )

        # Footer: puntuación + botón comentarios + botón detalles
        footer = MDBoxLayout(orientation="horizontal", spacing=16, size_hint_y=None, height=50, padding=[8, 8, 8, 0])
        comentarios = actividad.get("comentarios", [])
        puntuaciones = [c['puntuacion'] for c in comentarios if 'puntuacion' in c]
        media = round(sum(puntuaciones) / len(puntuaciones), 1) if puntuaciones else None

        puntuacion_layout = MDBoxLayout(orientation="horizontal", size_hint_x=0.6, pos_hint={"center_y": 0.5})
        if media:
            for i in range(int(media)):
                puntuacion_layout.add_widget(MDIcon(icon="star", theme_text_color="Custom", text_color="#FF9800", size_hint=(None, None), size=(20, 20)))
            if media % 1 >= 0.5:
                puntuacion_layout.add_widget(MDIcon(icon="star-half-full", theme_text_color="Custom", text_color="#FF9800", size_hint=(None, None), size=(20, 20)))
            puntuacion_layout.add_widget(MDLabel(text=f" {media}", theme_text_color="Secondary", font_style="Caption", size_hint_x=None, width=30))
        else:
            puntuacion_layout.add_widget(MDLabel(text="Sin valoraciones", theme_text_color="Secondary", font_style="Caption"))
        footer.add_widget(puntuacion_layout)

        # Botón comentarios (icono de comentario + número)
        comentarios_layout = MDBoxLayout(orientation="horizontal", spacing=0, size_hint_x=None, width=44)
        btn_comentarios = MDIconButton(
            icon="comment-text-outline",
            on_release=lambda x: on_comentarios_callback(actividad) if on_comentarios_callback else None,
            theme_text_color="Custom",
            text_color=(0.25, 0.25, 0.25, 1),
            pos_hint={"center_y": 0.5},
            size_hint_x=None
        )
        comentarios_layout.add_widget(btn_comentarios)
        comentarios_layout.add_widget(MDLabel(
            text=str(len(comentarios)),
            theme_text_color="Secondary",
            font_style="Caption",
            pos_hint={"center_y": 0.5, "center_x": 0}
        ))

        footer.add_widget(comentarios_layout)

        # Botón detalles (icono de información)
        if on_detalles_callback:
            btn_detalles = MDIconButton(
                icon="information-outline",
                on_release=lambda x: on_detalles_callback(actividad),
                theme_text_color="Custom",
                text_color=(20/255, 203/255, 186/255, 1),
                pos_hint={"center_y": 0.5, "center_x": 1},
            )
            footer.add_widget(btn_detalles)

        self.add_widget(footer)

class ClienteHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        self.usuario_actual = None
        self.dialog = None
        self.db = Database()
        

        super().__init__(**kwargs)
        
        # Cargar datos del usuario actual
        app = App.get_running_app()
        if app.usuario_actual:
            self.usuario_actual = self.db.get_usuario(app.usuario_actual)
        
        # Cargar datos de la base de datos
        self.actividades = self.db.get_all_actividades()
        config = self.db.get_configuracion()
        self.iconos_categorias = config["iconos_categorias"]
        self.color_categorias = config["color_categorias"]
        
        # Obtener inscripciones de la base de datos
        self.inscripciones = {}
        for actividad in self.actividades:
            self.inscripciones[str(actividad["id"])] = actividad["inscritos"]

        self.items_salir() # Crear el botón de salir y el comportamiento de arrastre

        #Accedemos a los MDTetxtFields
        self.nombre_field = self.ids.nombre_field
        self.email_field = self.ids.email_field
        self.telefono_field = self.ids.telefono_field
        self.direccion_field = self.ids.direccion_field
        self.condiciones_field = self.ids.condiciones_field
        self.fecha_registro_field = self.ids.fecha_registro_field
        self.gustos_field = self.ids.gustos_field

        # Filtros
        self.filtro_nombre = ""
        self.filtro_categoria = []
        self.filtro_fecha_desde = ""
        self.filtro_fecha_hasta = ""

    def parse_date(self, date_str):
        """Parsea una fecha en formato YYYY-MM-DD o DD/MM/YYYY."""
        try:
            # 1º YYYY-MM-DD
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # 2º: DD/MM/YYYY
                return datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                return None

    def on_pre_enter(self):
        """Called before the screen is entered."""
        # Cargar datos del usuario actual
        app = App.get_running_app()
        if not app.usuario_actual:
            # Si no hay usuario actual, mostrar un mensaje y volver a la pantalla de login
            self.manager.current = 'login'
            return
            
        # Actualizar datos del usuario desde la base de datos
        usuario_detalle = self.db.get_usuario(app.usuario_actual)
        if usuario_detalle:
            app.usuario_actual_detalle = usuario_detalle
            self.usuario_actual = usuario_detalle
            
            # Actualizar los campos del formulario
            self.nombre_field.text = usuario_detalle.get("nombre", "")
            self.email_field.text = usuario_detalle.get("email", "")
            self.telefono_field.text = usuario_detalle.get("telefono", "")
            self.direccion_field.text = usuario_detalle.get("direccion", "")
            self.condiciones_field.text = usuario_detalle.get("condiciones_medicas", "")
            self.fecha_registro_field.text = usuario_detalle.get("fecha_registro", "")
            self.gustos_field.text = usuario_detalle.get('gustos', '')
            
        # Recargar actividades de la base de datos
        self.actividades = self.db.get_all_actividades()
        # Actualizar inscripciones
        self.inscripciones = {}
        for actividad in self.actividades:
            self.inscripciones[str(actividad["id"])] = actividad["inscritos"]
            
        # Establecer el filtro de fecha por defecto a la fecha actual
        self.filtro_fecha_desde = date.today().strftime("%Y-%m-%d")
        
        # Cargar las actividades en la UI
        self.cargar_actividades()
        self.cargar_inscripciones()

    def guardar_inscripciones(self, datos):
        """Guarda las inscripciones en la base de datos."""
        for actividad_id, emails in datos.items():
            actividad_id = int(actividad_id)
            # Obtener inscripciones actuales de la base de datos
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT usuario_email FROM inscripciones WHERE actividad_id = ?", (actividad_id,))
            inscripciones_actuales = [row['usuario_email'] for row in cursor.fetchall()]
            
            # Eliminar inscripciones que ya no están en la lista
            for email in inscripciones_actuales:
                if email not in emails:
                    self.db.remove_inscripcion(actividad_id, email)
            
            # Añadir nuevas inscripciones
            for email in emails:
                if email not in inscripciones_actuales:
                    try:
                        self.db.add_inscripcion(actividad_id, email)
                    except sqlite3.IntegrityError:
                        # Si ya existe la inscripción, la ignoramos
                        pass

    def _init_menu_estado(self):
        """Inicializa el menú desplegable para filtrar por estado."""
        menu_items = [
            {
                "text": "Todos",
                "on_release": lambda: self._seleccionar_estado(None)
            },
            {
                "text": "Activas",
                "on_release": lambda: self._seleccionar_estado(True)
            },
            {
                "text": "Inactivas",
                "on_release": lambda: self._seleccionar_estado(False)
            }
        ]
        
        self.menu_estado = MDDropdownMenu(
            caller=self.ids.estado_filter,
            items=menu_items,
            width_mult=4,
            position="bottom"
        )
        self.menu_estado.open()

    def _seleccionar_estado(self, estado):
        """Selecciona el estado para filtrar las actividades."""
        self.filtro_estado = estado
        self.ids.estado_filter.text = "Todos" if estado is None else "Activas" if estado else "Inactivas"
        if hasattr(self, 'menu_estado'):
            self.menu_estado.dismiss()

    def cargar_actividades(self):
        """Carga las actividades disponibles y las muestra en tarjetas, agrupadas por fecha."""
        self.ids.actividad_list.clear_widgets()
        
        actividades_filtradas = []
        email = self.usuario_actual["email"]
        
        for act in self.actividades:
            # Solo mostrar actividades activas
            if not act.get("activo", True):
                continue
                
            # No mostrar actividades en las que el usuario ya está inscrito
            if email in act.get("inscritos", []):
                continue
                
            # Filtro por nombre
            if self.filtro_nombre and self.filtro_nombre.lower() not in act["nombre"].lower() and self.filtro_nombre.lower() not in act["descripcion"].lower():
                continue
                
            # Filtro por categoría
            if self.filtro_categoria and act["categoria"] not in self.filtro_categoria:
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
                    self.ids.actividad_list.add_widget(Widget(size_hint_y=None, height=32))  # Más separación
                else:
                    primer_bloque = False
                titulo_fecha = MDBoxLayout(
                    md_bg_color=(0.72, 0.94, 0.92, 1),  # Verde suave
                    radius=[12, 12, 12, 12],
                    size_hint_y=None,
                    height=38,
                    padding=(16, 0),
                )
                titulo_fecha.add_widget(MDLabel(
                    text=f"[b]{fecha_titulo}[/b]",
                    markup=True,
                    theme_text_color="Custom",
                    text_color=(0.13, 0.33, 0.27, 1),  # Verde oscuro
                    halign="center",
                    valign="middle",
                    font_style="Subtitle1"
                ))
                self.ids.actividad_list.add_widget(titulo_fecha)
            # Añadir separación entre el título y la tarjeta
            self.ids.actividad_list.add_widget(Widget(size_hint_y=None, height=8))
            card = ActividadCard(
                act,
                self.iconos_categorias,
                self.color_categorias,
                self.parse_date,
                on_comentarios_callback=self.mostrar_comentarios,
                on_detalles_callback=self.mostrar_detalles
            )
            self.ids.actividad_list.add_widget(card)
            self.ids.actividad_list.add_widget(Widget(size_hint_y=None, height=16))  # Espacio entre cards

    def cargar_inscripciones(self):
        """Carga las actividades inscritas y las muestra en tarjetas."""
        self.ids.inscripcion_list.clear_widgets()
        email = self.usuario_actual["email"]
        for act in self.actividades:
            # Buscar si el usuario está inscrito
            inscritos = self.inscripciones.get(str(act["id"]), [])
            if email in inscritos:
                card = ActividadCard(
                    act,
                    self.iconos_categorias,
                    self.color_categorias,
                    self.parse_date,
                    on_comentarios_callback=self.mostrar_comentarios,
                    on_detalles_callback=lambda a=act: self.mostrar_detalles(a, cancelar=True, valorar=True),
                    padding_izquierda=True
                )
                self.ids.inscripcion_list.add_widget(card)
                self.ids.inscripcion_list.add_widget(Widget(size_hint_y=None, height=16))  # Espacio entre cards

    def mostrar_detalles(self, actividad, cancelar=False, valorar=False):
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
                height=self.theme_cls.font_styles["Body1"][1] * 2.2  # altura por línea
            )
            contenido.add_widget(label)

        add_label(f"[b]Descripción:[/b] {actividad['descripcion']}")
        add_label(f"[b]Lugar:[/b] {actividad['lugar']}")
        add_label(f"[b]Fecha:[/b] {fecha_formateada} a las {actividad['hora']}")
        add_label(f"[b]Plazas disponibles:[/b] {plazas_disponibles}")
        add_label(f"[b]Valoraciones:[/b] {media_puntuacion:.1f}/5 [{num_votaciones} voto(s)]")
        
        # Comentarios con ícono al lado (solo si hay comentarios)
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
            )
        ]

        app = App.get_running_app()
        rol = getattr(app, "rol_actual", "cliente")

        if rol in ("empleado", "admin"):
            # Botón editar para empleados/admins
            botones.append(
                MDFlatButton(
                    text="Editar",
                    on_release=lambda x: (
                        self.dialog.dismiss(),
                        self.ir_a_editar_actividad(actividad)
                    ),
                    md_bg_color=(0.0, 0.6, 0.5, .5),
                    text_color=(1, 1, 1, 1)
                )
            )
        elif cancelar:
            botones.append(
                MDFlatButton(
                    text="Cancelar inscripción", 
                    on_release=lambda x: self.cancelar_inscripcion(actividad),
                    md_bg_color=(0.9, 0.1, 0.1, .5),
                    text_color=(1, 1, 1, 1)
                )
            )
        else:
            # Solo mostrar el botón de inscribirse si el usuario no está inscrito
            if self.usuario_actual["email"] not in actividad["inscritos"]:
                botones.append(
                    MDFlatButton(
                        text="Inscribirme", 
                        on_release=lambda x: self.inscribirse(actividad),
                        md_bg_color=(0.0, 0.6, 0.5, .5),
                        text_color=(1, 1, 1, 1)
                    )
                )

        if valorar and self.usuario_actual["email"] in actividad["inscritos"]:
            botones.append(
                MDFlatButton(
                    text="Valorar",
                    on_release=lambda x: (
                        self.dialog.dismiss(),
                        self.abrirValorar(actividad)
                    ),
                    md_bg_color=(0.0, 0.6, 0.5, .5),
                    text_color=(1, 1, 1, 1)
                )
            )

        # Crear y mostrar el diálogo
        self.dialog = MDDialog(
            title=actividad['nombre'],
            type="custom",
            content_cls=contenido,
            buttons=botones,
            size_hint=(0.85, None)
        )
        self.dialog.open()

    def inscribirse(self, actividad):
        email = self.usuario_actual["email"]
        actividad_id = str(actividad["id"])
        inscritos = self.inscripciones.get(actividad_id, [])
        if email in inscritos:
            toast("Ya estás inscrito en esta actividad.")
        elif len(inscritos) < actividad["plazas"]:
            # Solo añade el email y guarda esa inscripción
            self.db.add_inscripcion(actividad["id"], email)
            inscritos.append(email)
            self.inscripciones[actividad_id] = inscritos
            toast("Inscripción exitosa.")
            # Solo recarga las listas necesarias
            self.cargar_actividades()
            self.cargar_inscripciones()
        else:
            toast("No hay plazas disponibles.")
        self.dialog.dismiss()

    def cancelar_inscripcion(self, actividad):
        """Cancela la inscripción del usuario en una actividad y actualiza la base de datos."""
        email = self.usuario_actual["email"]
        actividad_id = str(actividad["id"])
        inscritos = self.inscripciones.get(actividad_id, [])
        if email in inscritos:
            inscritos.remove(email)
            self.inscripciones[actividad_id] = inscritos
            self.guardar_inscripciones(self.inscripciones)
            toast("Inscripción cancelada.")
            # Actualizar la actividad en la lista de actividades
            for act in self.actividades:
                if str(act["id"]) == actividad_id:
                    act["inscritos"] = inscritos
                    break
        else:
            toast("No estabas inscrito.")
        self.dialog.dismiss()
        # Recargar tanto las actividades disponibles como las inscripciones
        self.cargar_actividades()
        self.cargar_inscripciones()

    def salir(self):
        """Cierra la sesión y vuelve a la pantalla de login."""
        app = App.get_running_app()
        # Limpiar datos de usuario
        app.usuario_actual = None
        app.rol_actual = None
        app.usuario_actual_detalle = None
        # Cambiar a la pantalla de login
        self.manager.current = 'login'

    def validar_campos_perfil(self):
        """Valida los campos del perfil del usuario."""
        valid = True

        input_nombre_field = self.nombre_field
        input_email_field = self.email_field
        input_telefono_field = self.telefono_field

        # Validar nombre
        nombre = input_nombre_field.text.strip()
        if not nombre:
            input_nombre_field.helper_text = "El nombre es obligatorio"
            input_nombre_field.error = True
            toast("El nombre es obligatorio")
            valid = False
        else:
            input_nombre_field.helper_text = "Nombre completo"
            input_nombre_field.error = False

        # Validar email
        email = input_email_field.text.strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            input_email_field.helper_text = "Correo electrónico inválido"
            input_email_field.error = True
            toast("Correo electrónico inválido")
            valid = False
        else:
            input_email_field.helper_text = "Correo electrónico"
            input_email_field.error = False

        # Validar teléfono
        telefono = input_telefono_field.text.strip()
        patron_telefono = r"^\+?(\d{1,3}[\s-]?)?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,4}$"
        if not re.match(patron_telefono, telefono):
            input_telefono_field.helper_text = "Número de teléfono inválido"
            input_telefono_field.error = True
            toast("Número de teléfono inválido")
            valid = False
        else:
            input_telefono_field.helper_text = "Teléfono de contacto"
            input_telefono_field.error = False

        if valid:
            # Preparar datos para actualizar
            datos_actualizados = {
                "email": email,  # Incluir el email en los datos actualizados
                "nombre": nombre,
                "telefono": telefono,
                "direccion": self.direccion_field.text.strip(),
                "condiciones_medicas": self.condiciones_field.text.strip()
            }
            
            # Intentar guardar los cambios
            if self.db.save_usuario(self.usuario_actual["email"], datos_actualizados):
                toast("Perfil actualizado correctamente")
                # Actualizar los datos en memoria
                self.usuario_actual.update(datos_actualizados)
                # Si el email cambió, actualizar el email en la app
                if email != self.usuario_actual["email"]:
                    app = App.get_running_app()
                    app.usuario_actual = email
            else:
                toast("Error al actualizar el perfil")

    def abrirValorar(self, actividad):
        """Navega a la pantalla de valoración."""
        valorar_screen = self.manager.get_screen("valorar")
        valorar_screen.actividad = actividad
        valorar_screen.valorarActividad(actividad)
        self.manager.current = "valorar"

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

    def ir_a_comentarios(self, actividad):
        """Navega a la pantalla de comentarios y votaciones."""
        self.manager.current = 'comentarios_home'  # Cambiar a la pantalla de comentarios
        self.manager.get_screen('comentarios_home').cargar_comentarios(actividad)

    def abrir_panel_filtros(self):
        """Abre el panel de filtros como una nueva pantalla."""
        self.manager.current = "filter_screen"
    
    def aplicar_filtros(self):
        self.cargar_actividades()

    def obtener_actividades_db(self):
        """Obtiene todas las actividades de la base de datos."""
        return self.db.get_all_actividades()

    def items_salir(self):
        """Crea el botón de salir y configura el comportamiento de arrastre."""
        # El botón de salir se configura en el archivo .kv
        pass

    def ir_a_editar_actividad(self, actividad):
        """Navega a la pantalla de edición de actividad."""
        editar_screen = self.manager.get_screen("editarActividad")
        editar_screen.cargar_actividad(actividad)
        self.manager.current = "editarActividad"