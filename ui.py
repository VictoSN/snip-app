from PyQt6.QtWidgets import (
    QMainWindow, QSystemTrayIcon, QStyle, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLineEdit, QLabel, QApplication, QTextEdit
)
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIntValidator, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from snipping import Snipping
from storage import Storage
from pathlib import Path
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.snipping = Snipping()
        self.storage = Storage()

        self.snips = []
        self.snips = self.storage.get_snips()
        self.selected_idx = None
        self.snip = None

        self.setup_notification()
        self.setup_sound_effects()
        self.setup_ui()
        self.setup_connections()
        self.render_snips()
        self.set_layout_visible(self.viewer_layout, False)

    def setup_notification(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.show()

    def setup_sound_effects(self):
        BASE_DIR = Path(__file__).resolve().parent
        snap_file = BASE_DIR / "sound_effects/snap.wav"

        self.sound = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.sound.setAudioOutput(self.audio_output)
        self.sound.setSource(QUrl.fromLocalFile(str(snap_file)))

    def setup_ui(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Snipping OCR")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Viewer Layout
        self.viewer_layout = QVBoxLayout()
        self.viewer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.viewer_layout)

        self.snip_name = QLineEdit()
        self.viewer_layout.addWidget(self.snip_name)

        self.snip_image = QLabel()
        self.viewer_layout.addWidget(self.snip_image)

        self.snip_text = QTextEdit()
        self.snip_text.setReadOnly(True)
        self.viewer_layout.addWidget(self.snip_text)

        button_layout = QHBoxLayout()
        self.viewer_layout.addLayout(button_layout)

        self.back_button = QPushButton("Back")
        button_layout.addWidget(self.back_button)

        self.delete_button = QPushButton("Delete")
        button_layout.addWidget(self.delete_button)

        self.copy_button = QPushButton("Copy")
        button_layout.addWidget(self.copy_button)

        # List Layout
        self.list_layout = QVBoxLayout()
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.list_layout)

        # Control Layout
        self.control_layout = QVBoxLayout()
        main_layout.addLayout(self.control_layout)

        # Coords Layout
        self.coords_layout = QHBoxLayout()
        self.control_layout.addLayout(self.coords_layout)
        coords_validator = QIntValidator()

        self.x_coords = QLineEdit()
        self.x_coords.setPlaceholderText("X")
        self.x_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.x_coords)

        self.y_coords = QLineEdit()
        self.y_coords.setPlaceholderText("Y")
        self.y_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.y_coords)

        self.width_coords = QLineEdit()
        self.width_coords.setPlaceholderText("W")
        self.width_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.width_coords)

        self.height_coords = QLineEdit()
        self.height_coords.setPlaceholderText("H")
        self.height_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.height_coords)

        self.snip_button = QPushButton("+")
        self.control_layout.addWidget(self.snip_button)
    
    def setup_connections(self):
        self.snip_button.clicked.connect(self.snip_screen)
        self.back_button.clicked.connect(self.back_snip)
        self.delete_button.clicked.connect(self.delete_snip)
        self.copy_button.clicked.connect(self.copy_snip)
    
    # View Logic
    def clear_render(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_render(item.layout())

    def update_snips(self):
        self.snips = self.storage.get_snips()
        self.render_snips()

    def render_snips(self):
        self.clear_render(self.list_layout)
        
        for i, snip in enumerate(self.snips):
            snip_layout = QHBoxLayout()
            snip_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            raw_date = snip[7]
            formatted_date = datetime.strptime(
                raw_date,
                "%Y%m%d_%H%M%S.%f"
            ).strftime("%Y-%m-%d : %H:%M:%S.%f")[:-3]

            title = QLabel(snip[1])
            date = QLabel(formatted_date)
            btn = QPushButton("View")
            btn.clicked.connect(lambda _, idx=i: self.select_snip(idx))

            snip_layout.addWidget(title)
            snip_layout.addWidget(date)
            snip_layout.addWidget(btn)
            self.list_layout.addLayout(snip_layout)

    def set_snip_image(self):
        pixmap = QPixmap(self.snip[8])
        scaled = pixmap.scaled(
            500,
            500,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.snip_image.setPixmap(scaled)

    def select_snip(self, idx):
        self.selected_idx = idx
        self.snip = self.snips[idx]
        print(self.snip)

        self.snip_name.setText(self.snip[1])
        self.set_snip_image()
        self.snip_text.setText(self.snip[2])

        self.set_layout_visible(self.viewer_layout, True)
        self.set_layout_visible(self.list_layout, False)
        self.set_layout_visible(self.control_layout, False)

    def delete_snip(self):
        self.storage.delete_snip(self.snip[0])
        self.back_snip()

    def back_snip(self):
        self.set_layout_visible(self.viewer_layout, False)
        self.set_layout_visible(self.list_layout, True)
        self.set_layout_visible(self.control_layout, True)
        self.update_snips()

    def copy_snip(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.snip[2])

    # Snip Logic
    def show_notifications(self, title, message=''):
        self.tray.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )

    def snip_screen(self):
        x = self.x_coords.text()
        y = self.y_coords.text()
        w = self.width_coords.text()
        h = self.height_coords.text()

        self.show_notifications("Screenshot Taken...")
        self.sound.play()
        self.snipping.screenshot(x, y, w, h)
        self.update_snips()

    # UI Visibility
    def set_layout_visible(self, layout, visible):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            if item.widget():
                if visible:
                    item.widget().show()
                else:
                    item.widget().hide()
            elif item.layout():
                self.set_layout_visible(item.layout(), visible)

    # Close Database
    def closeEvent(self, event):
        self.storage.close()
        event.accept()