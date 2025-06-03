from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class CustomDialog:
    def __init__(self, title, content, on_confirm):
        self.dialog = MDDialog(
            title=title,
            text=content,
            size_hint=(0.8, 1),
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dismiss()),
                MDFlatButton(text="Confirmar", on_release=lambda x: self.confirm(on_confirm))
            ]
        )

    def open(self):
        self.dialog.open()

    def dismiss(self):
        self.dialog.dismiss()

    def confirm(self, on_confirm):
        on_confirm()
        self.dismiss()