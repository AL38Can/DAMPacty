from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.toast import toast
from kivy.app import App
import random
from datetime import datetime, date, timedelta
from kivy.clock import Clock

class NuevaActividadScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fecha_text = "Selecciona fecha"
        self.plazas = 1  # Valor inicial de plazas

    def on_kv_post(self, base_widget):
        if not hasattr(self, 'plazas'):
            self.plazas = 1
        if not hasattr(self, 'categorias'):
            self.categorias = [
                "Aventura", "Naturaleza", "Bienestar", "Deportes", "Social", "Gastronomía"
            ]
            self.selected_categoria = self.categorias[0]
        self.categoria_menu = MDDropdownMenu(
            caller=self.ids.categoria_btn,
            items=[
                {"viewclass": "OneLineListItem", "text": cat, "on_release": lambda x=cat: self.set_categoria(x)}
                for cat in self.categorias
            ],
            width_mult=3,
        )
        self.ids.plazas_field.text = str(self.plazas)

    def open_categoria_menu(self, *args):
        self.categoria_menu.open()

    def set_categoria(self, categoria):
        self.selected_categoria = categoria
        self.ids.categoria_btn.text = categoria
        self.categoria_menu.dismiss()

    def open_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        """Guarda la fecha seleccionada en formato YYYY-MM-DD."""
        if isinstance(value, (datetime, date)):
            self.fecha_text = value.strftime("%Y-%m-%d")
            self.ids.fecha_field.text = self.fecha_text
        else:
            toast("Error al seleccionar la fecha")

    def incrementar_plazas(self, *args):
        self.plazas += 1
        self.ids.plazas_field.text = str(self.plazas)

    def decrementar_plazas(self, *args):
        if self.plazas > 1:
            self.plazas -= 1
            self.ids.plazas_field.text = str(self.plazas)

    def open_time_picker(self, *args):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_selected)
        time_dialog.open()

    def on_time_selected(self, instance, time_value):
        """Guarda la hora seleccionada en formato HH:MM."""
        if time_value:
            self.ids.hora_field.text = time_value.strftime("%H:%M")
        else:
            toast("Error al seleccionar la hora")

    def validar_fecha(self, fecha_str):
        """Valida que la fecha esté en formato correcto y sea futura."""
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            if fecha.date() < date.today():
                toast("La fecha debe ser futura")
                return False
            return True
        except ValueError:
            toast("Formato de fecha inválido")
            return False

    def validar_hora(self, hora_str):
        """Valida que la hora esté en formato correcto."""
        try:
            datetime.strptime(hora_str, "%H:%M")
            return True
        except ValueError:
            toast("Formato de hora inválido")
            return False

    def guardar_actividad(self, *args):
        # Validar campos obligatorios
        if not self.ids.nombre_field.text.strip():
            toast("El nombre es obligatorio")
            return
            
        if not self.ids.descripcion_field.text.strip():
            toast("La descripción es obligatoria")
            return
            
        if not self.validar_fecha(self.ids.fecha_field.text):
            return
            
        if not self.validar_hora(self.ids.hora_field.text):
            return
            
        if not self.ids.lugar_field.text.strip():
            toast("El lugar es obligatorio")
            return

        # instancia de la app
        app = App.get_running_app()
        
        # Crear activity data
        nueva = {
            "nombre": self.ids.nombre_field.text.strip(),
            "descripcion": self.ids.descripcion_field.text.strip(),
            "fecha": self.ids.fecha_field.text,
            "hora": self.ids.hora_field.text,
            "lugar": self.ids.lugar_field.text.strip(),
            "plazas": int(self.ids.plazas_field.text),
            "categoria": self.selected_categoria,
            "activo": self.ids.activo_switch.active
        }
        
        # Guardar BBDD
        app.db.save_actividad(nueva)
        
        # Lipiar
        self.ids.nombre_field.text = ""
        self.ids.descripcion_field.text = ""
        self.fecha_text = "Selecciona fecha"
        self.ids.fecha_field.text = self.fecha_text
        self.ids.hora_field.text = ""
        self.ids.lugar_field.text = ""
        self.plazas = 1
        self.ids.plazas_field.text = str(self.plazas)
        self.set_categoria(self.categorias[0])
        self.ids.activo_switch.active = True

        # Obtener la pantalla de empleado_home y refrescar datos
        if app.sm.has_screen("empleado_home"):
            empleado_home = app.sm.get_screen("empleado_home")
            if hasattr(empleado_home, "refresh_actividades"):
                # Primero refrescar los datos
                empleado_home.refresh_actividades()
                # Luego cambiar de pantalla
                Clock.schedule_once(lambda dt: setattr(app.sm, 'current', 'empleado_home'), 0.1)
        elif app.sm.has_screen("admin_home"):
            app.sm.current = "admin_home"

        toast("Actividad guardada con éxito")
    
    def rellenar_descripcion_ia(self):
        descripciones = [
            "Actividad divertida para todos.",
            "Aprende y comparte con amigos.",
            "Evento especial para la comunidad.",
            "¡No te lo pierdas!",
            "Una experiencia única.",
            "Taller práctico y entretenido.",
            "Ideal para todas las edades.",
            "Ven y descubre algo nuevo.",
            "Perfecto para relajarse y disfrutar.",
            "Comparte momentos inolvidables.",
        ]
        descripcion = random.choice(descripciones)
        self.ids.descripcion_field.text = descripcion

    def crear_actividad_ia(self):
        actividades_data = [
            {
                "nombre": "Aventura en la Naturaleza",
                "descripcion": "Explora los senderos ocultos de la zona con una caminata guiada. Descubre la flora y fauna local mientras disfrutas de vistas panorámicas. ¡Perfecto para amantes de la naturaleza!",
                "lugar": "Senderos Naturales",
                "categoria": "Naturaleza"
            },
            {
                "nombre": "Noche de Estrellas y Leyendas",
                "descripcion": "Reúnete alrededor de una hoguera bajo el cielo estrellado. Aprende a identificar constelaciones y escucha fascinantes historias y leyendas de la región. Incluye chocolate caliente o una bebida refrescante.",
                "lugar": "Mirador al Aire Libre",
                "categoria": "Cultura"
            },
            {
                "nombre": "Taller de Coctelería Creativa",
                "descripcion": "Aprende a preparar tus propios cócteles con un mixólogo experto. Descubre nuevas recetas, técnicas de preparación y disfruta de tus creaciones. ¡Ideal para socializar!",
                "lugar": "Sala de Eventos",
                "categoria": "Social"
            },
            {
                "nombre": "Mañana de Yoga y Bienestar",
                "descripcion": "Empieza el día con una sesión de yoga revitalizante al aire libre, con vistas al paisaje. Conecta con tu cuerpo y mente en un entorno de paz y tranquilidad.",
                "lugar": "Jardín al Aire Libre",
                "categoria": "Bienestar"
            },
            {
                "nombre": "Búsqueda del Tesoro Temática para Familias",
                "descripcion": "Una emocionante aventura para todas las edades. Resuelve acertijos y sigue pistas por todo el recinto para encontrar el tesoro escondido. ¡Diversión garantizada!",
                "lugar": "Parque Central",
                "categoria": "Aventura"
            },
            {
                "nombre": "Clase de Cocina Regional",
                "descripcion": "Sumérgete en la gastronomía local aprendiendo a preparar platos tradicionales con un chef experto. Degusta tus creaciones al final de la clase.",
                "lugar": "Aula de Cocina",
                "categoria": "Gastronomía"
            },
            {
                "nombre": "Torneo de Vóley Playa (o Piscina)",
                "descripcion": "Forma tu equipo y compite en un divertido y amigable torneo. ¡Perfecto para mantenerse activo y conocer gente!",
                "lugar": "Playa / Piscina",
                "categoria": "Deportes"
            },
            {
                "nombre": "Noche de Cine al Aire Libre",
                "descripcion": "Relájate bajo las estrellas con una selección de películas para toda la familia. Disfruta de palomitas de maíz y bebidas en un ambiente único.",
                "lugar": "Plaza Mayor",
                "categoria": "Social"
            },
            {
                "nombre": "Sesión de Fotografía de Paisajes",
                "descripcion": "Un taller práctico donde aprenderás a capturar la belleza del entorno con tu cámara o smartphone. Ideal para principiantes y entusiastas de la fotografía.",
                "lugar": "Mirador",
                "categoria": "Cultura"
            },
            {
                "nombre": "Día de Juegos Acuáticos",
                "descripcion": "Inflables gigantes, carreras de relevos en la piscina y actividades refrescantes para todas las edades. ¡La forma perfecta de combatir el calor!",
                "lugar": "Piscina Municipal",
                "categoria": "Deportes"
            },
            {
                "nombre": "Ruta en Bicicleta Guiada",
                "descripcion": "Descubre los encantos de los alrededores en una ruta en bicicleta adaptada a diferentes niveles. Se proporcionan bicicletas y cascos.",
                "lugar": "Paseo Marítimo",
                "categoria": "Aventura"
            },
            {
                "nombre": "Observación de Aves al Amanecer",
                "descripcion": "Para los más madrugadores, una experiencia tranquila para observar las aves locales en su hábitat natural mientras el sol se asoma.",
                "lugar": "Jardín Botánico",
                "categoria": "Naturaleza"
            },
            {
                "nombre": "Clase de Baile (Salsa, Bachata, etc.)",
                "descripcion": "Aprende los pasos básicos de un baile popular con un instructor divertido y enérgico. ¡Ideal para mover el esqueleto y pasar un buen rato!",
                "lugar": "Sala Multiusos",
                "categoria": "Social"
            },
            {
                "nombre": "Gimkana de Habilidades y Desafíos",
                "descripcion": "Supera una serie de pruebas divertidas y desafiantes, individualmente o en equipo. ¡Pon a prueba tu ingenio y destreza!",
                "lugar": "Patio Exterior",
                "categoria": "Aventura"
            },
            {
                "nombre": "Taller de Artesanía Local",
                "descripcion": "Aprende a crear un recuerdo único de tu estancia utilizando técnicas artesanales de la región. Todos los materiales incluidos.",
                "lugar": "Centro Cultural",
                "categoria": "Cultura"
            },
            {
                "nombre": "Taller de Creatividad",
                "descripcion": "Una actividad innovadora para estimular tu creatividad.",
                "lugar": "Aula 3",
                "categoria": "Cultura"
            },
            {
                "nombre": "Ruta de Senderismo",
                "descripcion": "Explora la naturaleza y haz nuevos amigos.",
                "lugar": "Parque Natural",
                "categoria": "Naturaleza"
            },
            {
                "nombre": "Torneo de Ajedrez",
                "descripcion": "Demuestra tu ingenio en un torneo amistoso.",
                "lugar": "Biblioteca",
                "categoria": "Social"
            },
            {
                "nombre": "Cata de Quesos",
                "descripcion": "Descubre sabores únicos en una experiencia gourmet.",
                "lugar": "Cafetería",
                "categoria": "Gastronomía"
            },
            {
                "nombre": "Noche de Juegos",
                "descripcion": "Diversión asegurada para todos los asistentes.",
                "lugar": "Sala de Conferencias",
                "categoria": "Social"
            },
            {
                "nombre": "Charla Motivacional",
                "descripcion": "Inspírate con historias de superación.",
                "lugar": "Auditorio",
                "categoria": "Cultura"
            },
            {
                "nombre": "Fiesta Temática",
                "descripcion": "Ven disfrazado y disfruta de una noche diferente.",
                "lugar": "Terraza",
                "categoria": "Social"
            },
            {
                "nombre": "Jornada de Voluntariado",
                "descripcion": "Ayuda a la comunidad y haz la diferencia.",
                "lugar": "Comunidad Local",
                "categoria": "Solidaridad"
            },
            {
                "nombre": "Concurso de Fotografía",
                "descripcion": "Captura los mejores momentos y participa por premios.",
                "lugar": "Jardín Botánico",
                "categoria": "Cultura"
            },
            {
                "nombre": "Picnic en el Parque",
                "descripcion": "Comparte una comida al aire libre con buena compañía.",
                "lugar": "Parque Central",
                "categoria": "Social"
            }
        ]



        actividad_ia = random.choice(actividades_data)
        self.ids.nombre_field.text = actividad_ia["nombre"]
        self.ids.descripcion_field.text = actividad_ia["descripcion"]
        
        # Generar fecha futura aleatoria
        today = date.today()
        random_days = random.randint(1, 60)
        future_date = today + timedelta(days=random_days)
        self.fecha_text = future_date.strftime("%Y-%m-%d")
        self.ids.fecha_field.text = self.fecha_text
        
        # Hora aleatoria
        hora = f"{random.randint(9,20):02d}:{random.choice(['00','15','30','45'])}"
        self.ids.hora_field.text = hora
        self.ids.lugar_field.text = actividad_ia["lugar"]
        self.plazas = random.randint(5, 50)
        self.ids.plazas_field.text = str(self.plazas)
        categoria =actividad_ia["categoria"]
        self.set_categoria(categoria)
        self.ids.activo_switch.active = random.choice([True, False])
