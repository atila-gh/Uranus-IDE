import base64
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from Uranus.SettingWindow import load_setting

class ImageOutput(QWidget):
    """
    A dedicated widget for displaying image outputs in Uranus IDE.

    Features:
    - Loads and displays base64-encoded PNG images.
    - Automatically adjusts its height based on image size.
    - Styled via external settings (background, border, alignment).
    - Can be toggled and cleared dynamically.

    Components:
    - QLabel (self.image_label): Displays the image as QPixmap.
    - QVBoxLayout: Layout container with zero margins and spacing.
    """

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
        """
        Loads and displays a base64-encoded PNG image.
        Automatically adjusts widget height.
        """
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_data))
        self.image_label.setPixmap(pixmap)

        height = pixmap.height()
        height = max(height, 150)  # حداقل ارتفاع منطقی


        self.image_label.setMinimumHeight(height)
        self.image_label.setMaximumHeight(height)
        self.image_label.updateGeometry()
        self.setVisible(True)

    def clear(self):
        """
        Clears the image and hides the widget.
        """
        self.image_label.clear()
        self.setVisible(False)