from PyQt6.QtWidgets import (
    QMainWindow, QSystemTrayIcon, QStyle, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLineEdit, QLabel, QApplication, QTextEdit, QScrollArea,
    QComboBox
)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIntValidator, QPixmap
from PyQt6.QtMultimedia import QSoundEffect

from snipping import Snipping
from storage import Storage
from overlay import SnipOverlay
from pathlib import Path
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.snipping = Snipping() # Handles the capture logic
        self.storage = Storage() # Handle the database operation

        self.snips = []
        self.snip = None # Currently selected snip data
        self.snips = self.storage.get_snips()
        self.selected_idx = None
        self.input_option = "Mouse Select" # Save the user option

        self.setup_notification()
        self.setup_sound_effects()
        self.setup_ui()
        self.setup_connections()
        self.render_snips()
        self.set_layout_visible(self.viewer_layout, False)
        self.set_layout_visible(self.coords_layout, False)

    def setup_notification(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.show()

    def setup_sound_effects(self):
        BASE_DIR = Path(__file__).resolve().parent
        snap_file = BASE_DIR / "sound_effects/snap.wav"

        # Much faster than QMediaPlayer
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(str(snap_file)))

    def setup_ui(self):
        self.resize(650, 500)
        self.setWindowTitle("Snipping OCR")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Viewer Layout
        ## Displays the selected screenshot details and buttons
        self.viewer_layout = QVBoxLayout()
        # self.viewer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.viewer_layout)

        self.snip_name = QLineEdit()
        self.viewer_layout.addWidget(self.snip_name)

        self.snip_image = QLabel()
        self.snip_image_scroll = QScrollArea()
        self.snip_image_scroll.setWidgetResizable(True)
        self.snip_image_scroll.setWidget(self.snip_image)
        self.viewer_layout.addWidget(self.snip_image_scroll)

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
        ## Displays all the saved screenshots
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        # self.scroll.setMinimumHeight(350)
        # self.scroll.setMaximumHeight(600)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.list_container)
        main_layout.addWidget(self.scroll)
        main_layout.setStretch(1, 1)  # index 1 = scroll, give it all the stretch

        # Control Layout
        ## Screenshot controls
        self.control_layout = QVBoxLayout()
        main_layout.addLayout(self.control_layout)

        # Dropdown
        self.control_option_layout = QHBoxLayout()
        self.control_layout.addLayout(self.control_option_layout)

        self.snip_dropdown = QComboBox()
        self.snip_dropdown.addItems(["Mouse Select", "Coordinates", "Full Window"])
        self.control_option_layout.addWidget(self.snip_dropdown)

        # Coords Layout
        self.coords_layout = QHBoxLayout()
        self.control_option_layout.addLayout(self.coords_layout)
        coords_validator = QIntValidator()

        self.x_coords = QLineEdit()
        self.x_coords.setPlaceholderText("X Coordinate")
        self.x_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.x_coords)

        self.y_coords = QLineEdit()
        self.y_coords.setPlaceholderText("Y Coordinate")
        self.y_coords.setValidator(coords_validator)
        self.coords_layout.addWidget(self.y_coords)

        self.width_dimension = QLineEdit()
        self.width_dimension.setPlaceholderText("Width")
        self.width_dimension.setValidator(coords_validator)
        self.coords_layout.addWidget(self.width_dimension)

        self.height_dimension = QLineEdit()
        self.height_dimension.setPlaceholderText("Height")
        self.height_dimension.setValidator(coords_validator)
        self.coords_layout.addWidget(self.height_dimension)

        self.snip_button = QPushButton("+")
        self.snip_button.setStyleSheet("QPushButton {font-size: 28px; font-weight: bold;}")
        self.control_layout.addWidget(self.snip_button)
    
    def setup_connections(self):
        self.snip_button.clicked.connect(self.snip_screen)
        self.snip_name.editingFinished.connect(self.update_snip_name)
        self.back_button.clicked.connect(self.back_snip)
        self.delete_button.clicked.connect(self.delete_snip)
        self.copy_button.clicked.connect(self.copy_snip)
        self.snip_dropdown.currentTextChanged.connect(self.set_user_option)
    
    # View Logic
    def clear_render(self, layout):
        # Recursively delete old rendered widgets/layouts
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

            # Store idx in lambda default argument to avoid late-binding closure issue
            btn.clicked.connect(lambda _, idx=i: self.select_snip(idx))

            snip_layout.addWidget(title)
            snip_layout.addWidget(date)
            snip_layout.addWidget(btn)
            self.list_layout.addLayout(snip_layout)
        self.list_layout.addStretch()

    def set_snip_image(self):
        pixmap = QPixmap(self.snip[8])
        # Scale the image while preserving the aspect ratio
        scaled = pixmap.scaledToWidth(
            self.snip_image_scroll.width() - 20,
            Qt.TransformationMode.SmoothTransformation
        )
        self.snip_image.setPixmap(scaled)
        self.snip_image.setAlignment(Qt.AlignmentFlag.AlignTop)

    def select_snip(self, idx):
        self.selected_idx = idx
        self.snip = self.snips[idx]

        self.snip_name.setText(self.snip[1])
        self.snip_text.setText(self.snip[2])

        # Toggle between list mode and viewer mode
        self.set_view_mode(True)
        QTimer.singleShot(50, self.set_snip_image)  

    def update_snip_name(self):
        if self.storage.close:
            return
        self.storage.update_snip(self.snip[0], self.snip_name.text())

    def delete_snip(self):
        self.storage.delete_snip(self.snip[0])
        self.back_snip()

    def back_snip(self):
        # Toggle between list mode and viewer mode
        self.set_view_mode(False)
        self.set_user_option()
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
        self.showMinimized() # Hide the program to get the text
        if self.input_option == "Mouse Select":
            QTimer.singleShot(100, lambda: self.create_overlay())
        elif self.input_option == "Coordinates":
            # Capture current coordinate inputs, Empty values trigger fullscreen capture
            QTimer.singleShot(100, lambda: self.take_screenshot(
                    self.x_coords.text(), 
                    self.y_coords.text(), 
                    self.width_dimension.text(), 
                    self.height_dimension.text()
                )
            )
        elif self.input_option == "Full Window":
            QTimer.singleShot(100, lambda: self.take_screenshot())

    def create_overlay(self):
        self.overlay = SnipOverlay(self.take_screenshot)

    def take_screenshot(self, x='', y='', w='', h=''):
        self.sound.play()
        self.show_notifications("Screenshot Taken!")
        self.snipping.screenshot(x, y, w, h)
        self.update_snips()
        self.showNormal()

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

    def set_view_mode(self, viewing: bool):
        # True = Viewer | False = List
        self.scroll.setVisible(not viewing)
        self.set_layout_visible(self.viewer_layout, viewing)
        self.set_layout_visible(self.control_layout, not viewing)

    # Hide or Show the user option for screenshots
    def set_user_option(self):
        self.input_option = self.snip_dropdown.currentText() # User Input for the screenshot
        if self.input_option == "Mouse Select" or self.input_option == "Full Window":
            self.set_layout_visible(self.coords_layout, False)
        elif self.input_option == "Coordinates":
            self.set_layout_visible(self.coords_layout, True)

    # Close Database
    def closeEvent(self, event):
        print("Closing DB")
        self.storage.closed = True
        self.storage.close()
        event.accept()

    # Resizes the image whenever the app's size change
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.snip is not None:
            self.set_snip_image()