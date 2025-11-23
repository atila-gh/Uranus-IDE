

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QFrame
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import os

class AboutWindow(QWidget):
    """
        A simple informational window displaying details about the Uranus IDE.

        Features:
        - Shows application logo, name, version, and description.
        - Includes developer contact information and external links.
        - Uses a clean vertical layout with styled labels and separators.

        Components:
        - QPixmap logo loaded from local image directory.
        - QLabel elements for name, version, description, and developer info.
        - QFrame separator for visual clarity.

        Usage:
        Typically invoked from the Help or About section of the Uranus IDE.
        Provides branding and contact context for users and contributors.
        """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Uranus IDE")
        self.setFixedSize(700, 400)
        self.init_ui()

    def init_ui(self):
        logo_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "Uranus.png")
        pixmap = QPixmap(icon_path)
        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)

        name_label = QLabel("Uranus IDE")
        name_label.setFont(QFont("Arial", 20, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel("Version 2.0.0")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        description = QLabel(
            "Uranus IDE is a lightweight, extensible development environment inspired by Jupyter.\n"
            "It supports interactive coding, modular plugin architecture, and a clean UI.\n"
            "Designed for clarity, speed, and educational use."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignTop)
        description.setAlignment(Qt.AlignCenter)

        description.setFont(QFont("Arial", 11))

        developer_info = QLabel(
            "Developed by Atila Ghashghaie - آتیلا قشقایی\n"
            "Contact: atila.gh@gmail.com\n"
            'GitHub : https://github.com/atila-gh/Uranus-IDE\n'
            "Website: https://poyeshmashin.ir/\n\n"
            "PyPi   : https://pypi.org/project/Uranus-IDE\n"
        )
        developer_info.setFont(QFont("Arial", 10))

        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        layout.addWidget(name_label)
        layout.addWidget(version_label)
        layout.addWidget(separator)
        layout.addWidget(description)
        layout.addStretch()
        layout.addWidget(developer_info)

        self.setLayout(layout)

