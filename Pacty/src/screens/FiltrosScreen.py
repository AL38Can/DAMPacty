from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.app import App
from datetime import datetime
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from datetime import date
from kivy.clock import Clock
from src.utils.database import Database
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.toast import toast



class FiltrosScreen(MDScreen):
    def __init__(self, **kwargs):
        # Guardar la pantalla cliente_home antes de la inicialización del padre
        self.cliente_home_screen = kwargs.pop('cliente_home_screen', None)
        super().__init__(**kwargs)
        self.dialog = None
        self.db = Database()
        self.menu_categorias = None
        self.selected_categories = set()  # Para mantener un registro de categorías seleccionadas
        
    def cerrar(self):
        """Cierra la pantalla de filtros y vuelve a la anterior."""
        self.manager.current = "cliente_home"

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados y vuelve a la pantalla anterior."""
        try:
            # Obtener los valores de los filtros
            filtros = {
                "nombre": self.ids.nombre_filter.text,
                "categoria": list(self.selected_categories),  # Convertir set a lista
                "fecha_desde": self.ids.fecha_desde_filter.text,
                "fecha_hasta": self.ids.fecha_hasta_filter.text
            }
            
            # Actualizar los filtros en la pantalla principal
            cliente_home = self.manager.get_screen("cliente_home")
            cliente_home.filtro_nombre = filtros["nombre"]
            cliente_home.filtro_categoria = filtros["categoria"]
            cliente_home.filtro_fecha_desde = filtros["fecha_desde"]
            cliente_home.filtro_fecha_hasta = filtros["fecha_hasta"]
            
            # Aplicar los filtros y volver a la pantalla principal
            cliente_home.cargar_actividades()
            self.manager.current = "cliente_home"
        except Exception as e:
            toast(f"Error al aplicar filtros: {str(e)}")

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        try:
            self.ids.nombre_filter.text = ""
            self.ids.categoria_filter.text = "Seleccionar Categoría"
            self.ids.fecha_desde_filter.text = date.today().strftime("%Y-%m-%d")
            self.ids.fecha_hasta_filter.text = ""
            self.selected_categories.clear()
            
            # Limpiar los chips de categorías
            if hasattr(self.ids, 'categorias_chip_box'):
                self.ids.categorias_chip_box.clear_widgets()
        except Exception as e:
            toast(f"Error al limpiar filtros: {str(e)}")

    def abrir_date_picker(self, tipo):
        """Abre el selector de fecha."""
        toast(f"Seleccionar fecha {tipo}")

    def on_kv_post(self, base_widget):
        """Se llama cuando el archivo KV ya está cargado y los ids están disponibles"""
        try:
            # Inicializar el menú de categorías
            if "categoria_filter" in self.ids:
                self._init_menu_categorias()

            # Poner fecha de hoy por defecto en "desde"
            if "fecha_desde_filter" in self.ids:
                Clock.schedule_once(self._set_fecha_desde_default, 0)
        except Exception as e:
            toast(f"Error al inicializar filtros: {str(e)}")

    def _set_fecha_desde_default(self, *args):
        """Establece la fecha actual como valor por defecto para el filtro 'desde'"""
        try:
            self.ids.fecha_desde_filter.text = date.today().strftime("%Y-%m-%d")
        except Exception as e:
            toast(f"Error al establecer fecha por defecto: {str(e)}")

    def _init_menu_categorias(self):
        """Inicializa el menú de categorías"""
        try:
            if not hasattr(self, 'ids') or "categoria_filter" not in self.ids:
                return
                
            categorias = self.db.get_categorias()
            menu_items = [
                {
                    "text": cat,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=cat: self.seleccionar_categoria_filtro(x),
                }
                for cat in categorias.keys()
            ]
            self.menu_categorias = MDDropdownMenu(
                caller=self.ids.categoria_filter,
                items=menu_items,
                width_mult=4,
            )
            self.menu_categorias.open()
        except Exception as e:
            toast(f"Error al inicializar menú de categorías: {str(e)}")

    def seleccionar_categoria_filtro(self, categoria):
        """Maneja la selección/deselección de categorías"""
        try:
            chip_box = self.ids.categorias_chip_box
            
            if categoria in self.selected_categories:
                # Si la categoría ya está seleccionada, la removemos
                self.selected_categories.remove(categoria)
                # Remover el chip correspondiente
                for chip in chip_box.children[:]:
                    if isinstance(chip, MDChip) and chip.children[0].text == categoria:
                        chip_box.remove_widget(chip)
            else:
                # Si la categoría no está seleccionada, la agregamos
                self.selected_categories.add(categoria)
                # Crear y agregar el chip
                chip = MDChip(
                    on_release=lambda x, cat=categoria: self.seleccionar_categoria_filtro(cat)
                )
                chip.add_widget(
                    MDChipText(
                        text=categoria,
                        theme_text_color="Secondary",
                    )
                )
                chip_box.add_widget(chip)
                
            self.menu_categorias.dismiss()
        except Exception as e:
            toast(f"Error al seleccionar categoría: {str(e)}")

    def actualizar_fondo_chips(self):
        chip_box = self.ids.categorias_chip_box
        chip_box.canvas.before.clear()
        if len(chip_box.children) > 0:
            with chip_box.canvas.before:
                Color(0.8, 0.8, 0.8, 1)
                Rectangle(pos=chip_box.pos, size=chip_box.size)

    def agregar_chip(self, *args, **kwargs):
        """Actualiza los chips al agregar uno"""
        self.actualizar_fondo_chips()

    def quitar_chip(self, *args, **kwargs):
        """Actualiza los chips al quitar uno"""
        self.actualizar_fondo_chips()
