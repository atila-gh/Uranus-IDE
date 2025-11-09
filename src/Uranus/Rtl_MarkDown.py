import sys
from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt
import markdown2

class ToggleMarkdownEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Markdown فارسی بنویسید، Shift+Enter برای رندر، Escape برای برگشت به ویرایش")
        self.setAcceptRichText(True)
        self.setStyleSheet("font-family: Tahoma; font-size: 14px;")
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.raw_markdown = ""
        self.is_rendered = False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ShiftModifier:
            self.render_markdown()
        elif event.key() == Qt.Key_Escape and self.is_rendered:
            self.restore_markdown()
        else:
            super().keyPressEvent(event)

    def render_markdown(self):
        self.raw_markdown = self.toPlainText()
        html = markdown2.markdown(self.raw_markdown)
        styled_html = f"""
        <div dir="rtl" style="font-family: Tahoma; font-size: 14px; line-height: 1.6;">
            {html}
        </div>
        """
        self.setReadOnly(True)
        self.setHtml(styled_html)
        self.is_rendered = True

    def restore_markdown(self):
        self.setReadOnly(False)
        self.setPlainText(self.raw_markdown)
        self.moveCursor(QTextCursor.End)
        self.is_rendered = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ToggleMarkdownEditor()
    editor.setWindowTitle("Markdown فارسی با کنترل Shift+Enter")
    editor.resize(800, 600)
    editor.show()
    sys.exit(app.exec_())