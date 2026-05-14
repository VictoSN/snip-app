from PyQt6.QtWidgets import (
    QMainWindow, QSystemTrayIcon, QStyle, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLineEdit, QLabel, QApplication, QTextEdit, QScrollArea
)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIntValidator, QPixmap
from PyQt6.QtMultimedia import QSoundEffect

class SnipOverlay(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

        self.start = None
        self.end = None

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.show()