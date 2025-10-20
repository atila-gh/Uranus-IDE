

from PyQt5.QtGui import QFont,QFontMetrics, QTextCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout,QApplication,QWidget, QSizePolicy,QTextEdit
from Uranus.SettingWindow import load_setting


class OutputEditor(QWidget):
    """
        A styled output viewer widget for displaying execution results in Uranus IDE.

        Features:
        - Displays read-only rich text output using QTextEdit.
        - Automatically adjusts its height based on content size.
        - Supports dynamic visibility toggling and scrollbar behavior.
        - Styled via external settings (background, foreground, font, size).

        Components:
        - QTextEdit (self.text_output): Main output area for text, HTML, or embedded images.
        - QVBoxLayout: Layout container with zero margins and spacing.

        Methods:
        - adjust_height(): Calculates and sets widget height based on document content.
        - clear(): Clears the output and hides the widget.

        Usage:
        Used inside Cell widgets to display textual output from code execution.
        Can be toggled via output buttons and resized automatically for clean presentation.
        """

    def __init__(self):
        super().__init__()
        self.setVisible(False)


        setting = load_setting()
        bg         = setting['colors']['Back Ground Color OutPut']
        fg         = setting['colors']['ForGround Color Output']
        font       = setting['OutPut Font']
        font_size  = setting['OutPut Font Size']

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        self.text_output = QTextEdit()
        self.text_output.setFont(QFont(font, font_size, QFont.Bold))
        self.text_output.setReadOnly(True)

        self.text_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid #ccc;
                padding: 6px;
            }}

            QScrollBar:vertical {{
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background-color: #999;
                border-radius: 4px;
                min-height: 20px;
                border: 1px solid #666;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: transparent;
                border: none;
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        self.text_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.text_output.setMaximumHeight(1000)

        self.layout.addWidget(self.text_output)

    def adjust_height1(self):
        layout = self.text_output.document().documentLayout()
        doc_height = layout.documentSize().height()
        line_height = QFontMetrics(self.text_output.font()).lineSpacing()

        content_height = int(doc_height) + 2 * line_height
        final_height = min(content_height, 1000)
        final_height = max(final_height, 100)

        self.text_output.setMinimumHeight(final_height)
        self.text_output.setMaximumHeight(final_height)

        # فعال‌سازی اسکرول داخلی اگر ارتفاع زیاد بود
        self.text_output.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if content_height > 1000 else Qt.ScrollBarAlwaysOff
        )

        self.text_output.updateGeometry()

    def adjust_height(self):
        text = self.text_output.toPlainText()
        lines = text.splitlines()
        line_count = max(len(lines), 1)  # min 1 line

        line_height = QFontMetrics(self.text_output.font()).lineSpacing()
        content_height = line_count * line_height + 20

        final_height = min(content_height, 600)
        final_height = max(final_height, 100)

        self.text_output.setMinimumHeight(final_height)
        self.text_output.setMaximumHeight(final_height)
        self.text_output.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if content_height > 600 else Qt.ScrollBarAlwaysOff
        )
        self.text_output.updateGeometry()


    def clear(self):
        self.text_output.clear()
        self.setVisible(False)

