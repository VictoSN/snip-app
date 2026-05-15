from PyQt6.QtWidgets import (
    QWidget
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor

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
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.show()

    def mousePressEvent(self, event):
        self.start = event.position()

    def mouseMoveEvent(self, event):
        self.end = event.position()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.position()

        x1 = int(self.start.x())
        y1 = int(self.start.y())
        x2 = int(self.end.x())
        y2 = int(self.end.y())

        x = min(x1, x2)
        y = min (y1, y2)
        w = abs(x1 - x2)
        h = abs(y1 - 2)

        self.callback(x, y, w, h)
        self.close()

    def paintEvent(self, event):
        if not self.start or not self.end:
            return
        
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.red)
        rect = QRect(self.start.toPoint(), self.end.toPoint())
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        painter.drawRect(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()