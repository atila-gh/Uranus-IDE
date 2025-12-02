

import os , base64
from PyQt5.QtGui import QIcon, QTextCharFormat, QFont, QFontMetrics, QTextImageFormat, QTextCursor, QColor , QMouseEvent , QPixmap  
from PyQt5.QtCore import  QSize , QEvent ,pyqtSignal, QBuffer, Qt 
from PyQt5.QtWidgets import (QDialog, QToolBar, QDialogButtonBox, QLabel, QWidget, QVBoxLayout, QTextEdit,QAction , QScrollArea, QPlainTextEdit
, QFileDialog, QMessageBox, QSlider, QComboBox, QHBoxLayout, QPushButton)
from Uranus.SettingWindow import load_setting

import sys, base64, hashlib
import markdown2
from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QMimeData, QBuffer
from PyQt5.QtGui import QImage

class MarkdownCell(QTextEdit):
    def __init__(self):
        super().__init__()
        self.is_rendered = False
        self.images = {}   # دیکشنری: key = short hash, value = Base64
        self.raw_text = "" # متن اصلی مارکدان

    def insertFromMimeData(self, source: QMimeData):
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage):
                # تبدیل تصویر به دادهٔ باینری
                buffer = QBuffer()
                buffer.open(QBuffer.WriteOnly)
                image.save(buffer, "PNG")
                data = bytes(buffer.data())
                buffer.close()

                # تولید هش کامل و گرفتن 6 کاراکتر انتهایی
                full_hash = hashlib.sha1(data).hexdigest()
                short_hash = full_hash[-6:]

                # تبدیل به Base64
                b64 = base64.b64encode(data).decode("utf-8")

                # ذخیره در دیکشنری
                self.images[short_hash] = b64

                # درج لینک کوتاه در متن ادیت
                markdown_img = f"\n![pasted image](data:image/png;base64,{short_hash})\n"
                self.insertPlainText(markdown_img)
        else:
            super().insertFromMimeData(source)

    


class DocumentEditor(QWidget):

    doc_returnPressed = pyqtSignal()  # KeyPress Event  signal
    clicked = pyqtSignal()  # Click Signal
    """
        A styled rich text editor with formatting toolbar, designed for Markdown-like document cells.

        Components:
        - RichTextEditor: The core QTextEdit-based editor with extended image and event support.
        - QToolBar: Provides formatting actions (bold, italic, underline, alignment, heading styles, color).
        - Signals: Emits `clicked` and `doc_returnPressed` for integration with cell containers.

        Features:
        - Toggle between editable and read-only modes.
        - Supports image insertion and resizing via dialogs.
        - Auto-adjusts height based on content.
        - Handles block-level indentation with Tab/Shift+Tab, including RTL-safe logic.
        - Customizable font, tab size, and color scheme via external settings.

        Event Handling:
        - Shift+Enter: Switches to read-only mode.
        - Double-click: Activates edit mode.
        - Tab/Shift+Tab: Indents/unindents selected blocks with RTL-aware logic.

        Intended Use:
        This widget is used as the document cell editor in Uranus IDE, supporting styled text,
        embedded images, and interactive formatting for notebook-style workflows.
        """

    def __init__(self, parent=None ):
        super().__init__(parent)

        # Load settings
        setting = load_setting()
        bg_meta = setting['colors']['Back Ground Color MetaData']
        fg_meta = setting['colors']['ForGround Color MetaData']
        self.code_font_size = setting['Code Font Size']
        metadata_font = setting['Meta Font']
        metadata_font_size = setting['Meta Font Size']
        self.tab_size = 4
        self.readonly_mode = False
        self.editor_height = 0
        self.flag_doc_height_adjust = False
      

        # Editor
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
        self.editor.doubleClicked.connect(self.activate_edit_mode)
        self.editor.clicked.connect(self.clicked.emit)
        self.editor.cursorPositionChanged.connect(self.update_heading_combo)

        # ScrollArea for editor
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #444; padding: 3px; }")
        self.scroll_area.setWidget(self.editor)
        

        # Internal layout
        self.editor_frame = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_frame)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)
        
        self.editor_layout.addWidget(self.scroll_area)
       

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.editor_frame)

        # Font and tab setup
        self.set_font_and_size(metadata_font, metadata_font_size)

      


    def set_font_and_size(self,font,size):

        
        self.default_font = QFont(font, size)
        self.default_format = QTextCharFormat()
        self.default_format.setFont(self.default_font)
        self.default_format.setFontPointSize(size)

        # initial setting for document
        self.editor.document().setDefaultFont(self.default_font)
        self.editor.setCurrentCharFormat(self.default_format)
        # define tabsize after define font
        font_metrics = QFontMetrics(self.editor.font())
        tab_width = font_metrics.horizontalAdvance(' ') * self.tab_size 
        self.editor.setTabStopDistance(tab_width)

    def keyPressEvent(self, event):
        # Only for Enter
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.doc_returnPressed.emit()
        # default react for other keys
        super().keyPressEvent(event)

 
    def mousePressEvent(self, event):
       
        super().mousePressEvent(event)
        if self.parent():
            self.parent().mousePressEvent(event)

    
    
    
    def toggle_mode(self):
        if not self.editor.is_rendered:
            # ذخیره متن ادیت قبل از رندر
            self.raw_text = self.editor.toPlainText()

            # جایگزینی short_hash با Base64 واقعی
            text = self.editor.raw_text
            for key, b64 in self.editor.images.items():
                text = text.replace(f"data:image/png;base64,{key}", f"data:image/png;base64,{b64}")

            # رندر به HTML
            html = markdown2.markdown(text, extras=["fenced-code-blocks","tables","strike","task_list"])
            self.editor.setHtml(html)
            self.editor.setReadOnly(True)
            self.editor.is_rendered = True
        else:
            # بازگشت به متن ادیت اصلی
            self.editor.setPlainText(self.raw_text)
            self.editor.setReadOnly(False)
            self.editor.is_rendered = False
        
        self.editor.setFocus()
        self.adjust_height_document_editor()



    def eventFilter(self, obj, event):
        if obj == self.editor:
            if event.type() == QEvent.KeyPress:
                cursor = self.editor.textCursor()

                # ---------- Shift+Enter ----------
                if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ShiftModifier:
                    self.activate_readonly_mode()
                    return True

                # ---------- Tab ----------
                elif event.key() == Qt.Key_Tab and cursor.hasSelection():
                    try:
                        cursor.beginEditBlock()
                        start = min(cursor.anchor(), cursor.position())
                        end = max(cursor.anchor(), cursor.position())

                        block = self.editor.document().findBlock(start)
                        end_block = self.editor.document().findBlock(end)

                        while block.isValid() and block.position() <= end_block.position():
                            line_cursor = QTextCursor(block)
                            line_cursor.movePosition(QTextCursor.StartOfBlock)
                            line_cursor.insertText(" " * 4)
                            block = block.next()

                        cursor.endEditBlock()
                        self.editor.setTextCursor(cursor)
                        return True

                    except Exception as e:
                        
                        return True

                # ---------- Shift+Tab ----------
                elif event.key() == Qt.Key_Backtab and cursor.hasSelection():
                    try:
                        cursor.beginEditBlock()
                        start = min(cursor.anchor(), cursor.position())
                        end = max(cursor.anchor(), cursor.position())

                        block = self.editor.document().findBlock(start)
                        end_block = self.editor.document().findBlock(end)

                        while block.isValid() and block.position() <= end_block.position():
                            block_text = block.text()
                            leading_spaces = len(block_text) - len(block_text.lstrip())
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

                    except Exception as e:
                        
                        return True

            elif event.type() == QEvent.MouseButtonDblClick:
                if self.readonly_mode:
                    self.activate_edit_mode()
                    return True

        return super().eventFilter(obj, event)

   
 
 
    def adjust_height_document_editor(self):
        #print('[adjust_height_document_editor]')
        doc = self.editor.document()
        layout = doc.documentLayout()

        # ارتفاع واقعی محتوای رندر شده
        content_height = layout.documentSize().height()
               
        cm = self.editor.contentsMargins()
        toolbar_height = 30 if self.toolbar.isVisible() else 0
        

        
        new_height = int(content_height 
                 + toolbar_height 
                 + doc.documentMargin()   # می‌تونی اینو کم یا حذف کنی
                 + self.editor.frameWidth() * 2  # یا فقط یک بار بذاری
                 + cm.top() 
                 + cm.bottom()
                 + 2)   # به جای 10، فقط 2 پیکسل اضافه


        self.editor_height = new_height #  New Height to save to file metadata
        
        if self.readonly_mode:
            self.setMinimumHeight(new_height)
            self.setMaximumHeight(new_height)
        else:
            min_height = 100
            max_height = 800
            final_height = max(min_height, min(new_height, max_height))
            self.setMinimumHeight(final_height)
            self.setMaximumHeight(final_height)

        self.updateGeometry()
        self.flag_doc_height_adjust = True
       
     
    def set_fixed_height(self , height = 0):
        """Set editor to exact pixel height (from metadata)"""
        #print('[SET FIXED HEIGHT METHOD] ' ,height)
      
        self.setFixedHeight(height)   # دقیقاً همون ارتفاع
        self.resize(self.width(), height)  # اگر داخل layout باشه، این هم کمک می‌کنه
        self.updateGeometry()


        
        
    

