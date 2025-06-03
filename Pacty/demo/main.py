from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

class MiLayout(BoxLayout):
    def cambiar_texto(self):
        self.ids.mi_label.text = "¡Texto cambiado!"

class MiApp(App):
    def build(self):
        Builder.load_file("template.kv")
        return MiLayout()

if __name__ == '__main__':
    MiApp().run()