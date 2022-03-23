from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtGui import QPainter, QPixmap


# Класс для отжимаемых кнопок
class NoteButton(QAbstractButton):
    """Кнопка наследованная от QAbstractButton.
    Главные отличия в том что она может посылать сигнал released и pressed"""

    def __init__(self, path, path2):
        super().__init__()
        self.note_on_pixmap = QPixmap(path)
        self.note_off_pixmap = QPixmap(path2)

    def paintEvent(self, event):
        """Настраиваем paintEvent так, что бы он мог показывать два состояния кнопки"""
        painter = QPainter(self)
        if self.isDown():
            pix = self.note_on_pixmap
        else:
            pix = self.note_off_pixmap
        painter.drawPixmap(event.rect(), pix)

    def sizeHint(self):
        return self.note_on_pixmap.size()


class SeqButton(QAbstractButton):
    """Кнопка с свойствами QCheckBox'а которая хранит в себе используемый паттерн
    TODO переделать paintEvent так что бы он мог показывать какой паттерн сейчас на этой кнопке"""

    def __init__(self, path, path2):
        super().__init__()
        self.seq_on = QPixmap(path)
        self.seq_off = QPixmap(path2)
        self.setCheckable(True)
        self.pattern = None

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.isChecked():
            pix = self.seq_on
        else:
            pix = self.seq_off

        painter.drawPixmap(event.rect(), pix)

    def index_pattern_set(self, pattern):
        """Привязываем индекс паттерна к кнопке"""
        self.pattern = pattern

    def return_pattern(self):
        """Возвращаем индекс паттерна привязанный к кнопке"""
        return self.pattern

    def sizeHint(self):
        return self.seq_on.size()
