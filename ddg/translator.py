
from PyQt5.QtCore import QTranslator, QLocale, QMetaType

class Translator:
    def __init__(self):
        self.translator = QTranslator()
        self.translator.load("./locale/de.ts", "main")

    def tr(self, *args, **kwargs):
        return self.translator.translate(*args, **kwargs)

translator = Translator()