import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
import ctypes

if __name__ == "__main__":
    # Set a custom app model id to use the icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("snip-app")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())