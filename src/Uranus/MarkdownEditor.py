import os, base64, hashlib, sys
import markdown2
from PyQt5.QtGui import (
    QFont, QFontMetrics, QTextCharFormat, QTextCursor, QImage, QMouseEvent
)
from PyQt5.QtCore import QEvent, pyqtSignal, QBuffer, Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from Uranus.SettingWindow import load_setting


class MarkdownCell(QTextEdit):
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_rendered = False
        self.images = {}
        self.raw_text = ""

    def insertFromMimeData(self, source):
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage):
                buffer = QBuffer()
                buffer.open(QBuffer.WriteOnly)
                image.save(buffer, "PNG")
                data = bytes(buffer.data())
                buffer.close()

                full_hash = hashlib.sha1(data).hexdigest()
                short_hash = full_hash[-6:]
                b64 = base64.b64encode(data).decode("utf-8")

                self.images[short_hash] = b64
                markdown_img = f"\n![pasted image](data:image/png;base64,{short_hash})\n"
                self.insertPlainText(markdown_img)
        else:
            super().insertFromMimeData(source)

    def toggle_mode(self):
        if not self.is_rendered:
            self.raw_text = self.toPlainText()
            text = self.raw_text
            for key, b64 in self.images.items():
                text = text.replace(f"data:image/png;base64,{key}", f"data:image/png;base64,{b64}")

            html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "strike", "task_list"])
            self.setHtml(html)
            self.setReadOnly(True)
            self.is_rendered = True
        else:
            self.setPlainText(self.raw_text)
            self.setReadOnly(False)
            self.is_rendered = False

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if self.hasFocus() and not self.isReadOnly():
            super().wheelEvent(event)
            event.accept()
        else:
            event.ignore()


class MarkdownEditor(QWidget):
    doc_returnPressed = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        setting = load_setting()
        bg_meta = setting['colors']['Back Ground Color MetaData']
        fg_meta = setting['colors']['ForGround Color MetaData']
        metadata_font = setting['Meta Font']
        metadata_font_size = setting['Meta Font Size']
        self.tab_size = 4
        
        self.editor_height = 0

        self.editor = MarkdownCell()
        self.editor.setAcceptRichText(True)
        self.editor.setFont(QFont(metadata_font, metadata_font_size))
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_meta};
                color: {fg_meta};
                font-family: {metadata_font};
                font-size: {metadata_font_size}pt;
                border: none;
                padding: 6px;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }}
        """)
        self.editor.installEventFilter(self)
        self.editor.doubleClicked.connect(self.toggle)
        self.editor.clicked.connect(self.clicked.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.editor)

        self.set_font_and_size(metadata_font, metadata_font_size)

    def set_font_and_size(self, font, size):
        default_font = QFont(font, size)
        default_format = QTextCharFormat()
        default_format.setFont(default_font)
        default_format.setFontPointSize(size)

        self.editor.document().setDefaultFont(default_font)
        self.editor.setCurrentCharFormat(default_format)

        font_metrics = QFontMetrics(self.editor.font())
        tab_width = font_metrics.horizontalAdvance(' ') * self.tab_size
        self.editor.setTabStopDistance(tab_width)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.doc_returnPressed.emit()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.parent():
            self.parent().mousePressEvent(event)

    def toggle(self):
        if not self.editor.is_rendered:
            self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.editor.toggle_mode()
        self.editor.setFocus()
        QTimer.singleShot(0, self.adjust_height_document_editor)



    def eventFilter(self, obj, event):
        if obj == self.editor:
            if event.type() == QEvent.KeyPress:
                cursor = self.editor.textCursor()

                if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ShiftModifier:
                    self.toggle()
                    return True

                elif event.key() == Qt.Key_Tab and cursor.hasSelection():
                    cursor.beginEditBlock()
                    start, end = sorted([cursor.anchor(), cursor.position()])
                    block = self.editor.document().findBlock(start)
                    end_block = self.editor.document().findBlock(end)

                    while block.isValid() and block.position() <= end_block.position():
                        line_cursor = QTextCursor(block)
                        line_cursor.movePosition(QTextCursor.StartOfBlock)
                        line_cursor.insertText(" " * self.tab_size)
                        block = block.next()

                    cursor.endEditBlock()
                    self.editor.setTextCursor(cursor)
                    return True

                elif event.key() == Qt.Key_Backtab and cursor.hasSelection():
                    cursor.beginEditBlock()
                    start, end = sorted([cursor.anchor(), cursor.position()])
                    block = self.editor.document().findBlock(start)
                    end_block = self.editor.document().findBlock(end)

                    while block.isValid() and block.position() <= end_block.position():
                        text = block.text()
                        leading_spaces = len(text) - len(text.lstrip())
                        remove_count = min(self.tab_size, leading_spaces)

                        if remove_count > 0:
                            line_cursor = QTextCursor(self.editor.document())
                            line_cursor.setPosition(block.position())
                            line_cursor.setPosition(block.position() + remove_count, QTextCursor.KeepAnchor)
                            line_cursor.removeSelectedText()

                        block = block.next()

                    cursor.endEditBlock()
                    self.editor.setTextCursor(cursor)
                    return True

            elif event.type() == QEvent.MouseButtonDblClick:
                if self.editor.is_rendered:
                    self.toggle()
                    return True

        return super().eventFilter(obj, event)

    def adjust_height_document_editor(self):
        doc = self.editor.document()
        layout = doc.documentLayout()
        content_height = layout.documentSize().height()
        cm = self.editor.contentsMargins()

        new_height = int(content_height + doc.documentMargin() + self.editor.frameWidth()*2 + cm.top() + cm.bottom() + 2)
        self.editor_height = new_height

        if self.editor.is_rendered:
    # حالت رندر → دقیقاً برابر محتوا
            self.setMinimumHeight(new_height)
            self.setMaximumHeight(new_height)
        else:
            # حالت ادیت → محدودیت بین 100 تا 800
            min_height = 100
            max_height = 800
            final_height = max(min_height, min(new_height, max_height))
            self.setMinimumHeight(final_height)
            self.setMaximumHeight(final_height)