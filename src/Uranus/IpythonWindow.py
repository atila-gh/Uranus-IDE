from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel
from PyQt5.QtGui import QFont
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager

class IPythonConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPython Console - White on Black")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # راه‌اندازی kernel
        km = QtKernelManager()
        km.start_kernel()
        kc = km.client()
        kc.start_channels()

        # ویجت ترمینال IPython
        self.console = RichJupyterWidget()
        self.console.kernel_manager = km
        self.console.kernel_client = kc

        # فقط سفید روی مشکی (بدون syntax_style)
        self.console.setStyleSheet("""
            QPlainTextEdit {
                background-color: gray;
                color: white;
            }
        """)

        # ComboBox برای سایز فونت
        font_label = QLabel("Font Size:")
        self.font_selector = QComboBox()
        self.font_selector.addItems(["10", "12", "14", "16", "18", "20", "22", "24", "28", "32"])
        self.font_selector.setCurrentText("14")
        self.font_selector.currentTextChanged.connect(self.change_font_size)

        layout.addWidget(font_label)
        layout.addWidget(self.font_selector)
        layout.addWidget(self.console)

        # تنظیم اولیه
        self.change_font_size("14")

    def change_font_size(self, size_str):
        size = int(size_str)
        self.console.font = QFont("Consolas", size)

if __name__ == "__main__":
    app = QApplication([])
    win = IPythonConsole()
    win.show()
    app.exec_()
