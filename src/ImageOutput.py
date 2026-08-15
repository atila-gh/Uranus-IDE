import base64
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from SettingWindow import load_setting



class ImageOutput(QWidget):

    def __init__(self):
        super().__init__()
        self.setVisible(False)

        setting = load_setting()
        bg = setting['colors']['Back Ground Color OutPut']

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                border: 1px solid #ccc;
                padding: 6px;
            }}
        """)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.layout.addWidget(self.image_label)

    def show_image_from_base64(self, base64_data):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_data))
        self.image_label.setPixmap(pixmap)

        height = pixmap.height()
        height = max(height, 150)  


        self.image_label.setMinimumHeight(height)
        self.image_label.setMaximumHeight(height)
        self.image_label.updateGeometry()
        self.setVisible(True)

    def clear(self):
        self.image_label.clear()
        self.setVisible(False)