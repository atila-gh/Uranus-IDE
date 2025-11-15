

import os , base64
from PyQt5.QtGui import QIcon, QTextCharFormat, QFont, QFontMetrics, QTextImageFormat, QTextCursor, QColor , QMouseEvent , QPixmap  
from PyQt5.QtCore import  QSize , QEvent ,pyqtSignal, QBuffer, Qt 
from PyQt5.QtWidgets import (QDialog, QToolBar, QDialogButtonBox, QLabel, QWidget, QVBoxLayout, QTextEdit,QAction , QScrollArea, QPlainTextEdit
, QFileDialog, QMessageBox, QSlider, QComboBox, QHBoxLayout, QPushButton)
from Uranus.SettingWindow import load_setting

class RichTextEditor(QTextEdit):
    clicked = pyqtSignal()  # سیگنال کلیک برای اتصال به سلول
    doubleClicked = pyqtSignal()
    """
       A rich text editor widget with extended clipboard and mouse event handling.

       Features:
       - Emits `clicked` and `doubleClicked` signals for integration with parent containers.
       - Automatically converts pasted images into base64-encoded HTML <img> tags.
       - Supports rich text formatting and custom event filtering.

       Signals:
       - clicked: Emitted when the editor is clicked.
       - doubleClicked: Emitted on double-click, typically used to activate edit mode.

       Usage:
       This widget is designed to be embedded inside higher-level editors like DocumentEditor,
       and supports both text and image input with enhanced interactivity.
       """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setCursor(Qt.IBeamCursor)
        self.setAcceptRichText(True)
        self.installEventFilter(self)
        
        
    def wheelEvent(self, event):
        # فقط خود ادیتور اسکرول شود، به والد پاس داده نشود
        super().wheelEvent(event)
        event.accept()



    def mousePressEvent(self, event: QMouseEvent):
        # print('\n\n Editor.editor\n\n')
        self.clicked.emit()  # فعال‌سازی سیگنال کلیک
        super().mousePressEvent(event)

    def insertFromMimeData(self, source):
        if source.hasImage():
            image = source.imageData()
            buffer = QBuffer()
            buffer.open(QBuffer.WriteOnly)
            image.save(buffer, "PNG")
            img_base64 = base64.b64encode(buffer.data()).decode("utf-8")
            html = f'<img src="data:image/png;base64,{img_base64}"><br>'
            self.insertHtml(html)
        else:
            super().insertFromMimeData(source)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


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
        metadata_font = setting['Meta Font']
        metadata_font_size = setting['Meta Font Size']
        self.tab_size = 4
        self.readonly_mode = False
        self.editor_height = 0
        self.flag_doc_height_adjust = False
      

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(20, 20))

        # Editor
        self.editor = RichTextEditor()
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
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #444; padding: 3px; }"
)
        self.scroll_area.setWidget(self.editor)
        

        # Internal layout
        self.editor_frame = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_frame)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)
        self.editor_layout.addWidget(self.toolbar)
        self.editor_layout.addWidget(self.scroll_area)
       

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.editor_frame)

        # Font and tab setup
        self.set_font_and_size(metadata_font, metadata_font_size)

        # Toolbar setup
        self.setup_toolbar()


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

    def setup_toolbar(self):
        """
        Adds formatting actions to the toolbar.
        Restores editor focus after each action is triggered.
        """
        # print('[DocumentEditor->setup_toolbar]')

        def wrap(slot):
            """
            This function provides a simple pattern for wrapping another function and performing additional actions.
            Any function we want can be passed as an argument, and it will be executed first.
            Then, we attach our desired process to it — which in this case is focusing the editor itself.
            """


            def wrapped():
                slot()
                self.editor.setFocus()
            return wrapped



        def toggle_bold():
            cursor = self.editor.textCursor() # Return Cursor Position
            if cursor.hasSelection():
                end_pos = cursor.selectionEnd()
                temp_cursor = QTextCursor(self.editor.document())
                temp_cursor.setPosition(end_pos - 1)
                is_bold = temp_cursor.charFormat().fontWeight() == QFont.Bold
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Normal if is_bold else QFont.Bold)
                cursor.mergeCharFormat(fmt)
            else:
                fmt = self.editor.currentCharFormat()
                fmt.setFontWeight(QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold)
                self.editor.setCurrentCharFormat(fmt)

           
            
            
        # Bold - Deactivate
        icon_path = os.path.join(os.path.dirname(__file__), "image", "bold.png")
        bold_action = QAction(QIcon(icon_path), "Bold", self)
        bold_action.triggered.connect(wrap(toggle_bold))
        bold_action.setCheckable(True)
        self.toolbar.addAction(bold_action)
        self.toolbar.addSeparator()
        

        def toggle_italic():
            cursor = self.editor.textCursor()

            if cursor.hasSelection():
                end_pos = cursor.selectionEnd()
                temp_cursor = QTextCursor(self.editor.document())
                temp_cursor.setPosition(end_pos - 1)
                is_italic = temp_cursor.charFormat().fontItalic()

                fmt = QTextCharFormat()
                fmt.setFontItalic(not is_italic)
                cursor.mergeCharFormat(fmt)


            else:
                fmt = self.editor.currentCharFormat()
                fmt.setFontItalic(not fmt.fontItalic())
                self.editor.setCurrentCharFormat(fmt)

            
        # Italic - Deactivate
        icon_path = os.path.join(os.path.dirname(__file__), "image", "italic.png")
        italic_action = QAction(QIcon(icon_path), "Italic", self)
        italic_action.toggled.connect(wrap(toggle_italic))
        italic_action.setCheckable(True)
            
        self.toolbar.addAction(italic_action)

        self.toolbar.addSeparator()

        


        def toggle_underline():
            cursor = self.editor.textCursor()

            if cursor.hasSelection():
                end_pos = cursor.selectionEnd()
                temp_cursor = QTextCursor(self.editor.document())
                temp_cursor.setPosition(end_pos - 1)
                is_underlined = temp_cursor.charFormat().fontUnderline()

                fmt = QTextCharFormat()
                fmt.setFontUnderline(not is_underlined)
                cursor.mergeCharFormat(fmt)


            else:
                fmt = self.editor.currentCharFormat()
                fmt.setFontUnderline(not fmt.fontUnderline())
                self.editor.setCurrentCharFormat(fmt)

            

        # Underline - Deactivate
        icon_path = os.path.join(os.path.dirname(__file__), "image", "underline.png")
        underline_action = QAction(QIcon(icon_path), "Underline", self)
      
        underline_action.toggled.connect(wrap(toggle_underline))
        underline_action.setCheckable(True)
        self.toolbar.addAction(underline_action)
        self.toolbar.addSeparator()

        

        # Center Align
        icon_path = os.path.join(os.path.dirname(__file__), "image", "center.png")
        align_center = QAction(QIcon(icon_path), "Center", self)
        align_center.triggered.connect(wrap(lambda: self.editor.setAlignment(Qt.AlignCenter)))
        self.toolbar.addAction(align_center)
        
        self.toolbar.addSeparator()

        # Justify Text
        icon_path = os.path.join(os.path.dirname(__file__), "image", "justify.png")
        align_justify = QAction(QIcon(icon_path), "Justify", self)
        align_justify.triggered.connect(wrap(lambda: self.editor.setAlignment(Qt.AlignJustify)))
        self.toolbar.addAction(align_justify)

        self.toolbar.addSeparator()

        # Insert image
        icon_path = os.path.join(os.path.dirname(__file__), "image", "insert_image.png")
        image_action = QAction(QIcon(icon_path), "Insert Image", self)
        image_action.triggered.connect(wrap(self.insert_image))
        self.toolbar.addAction(image_action)
        
        self.toolbar.addSeparator()

        # Resize image
        icon_path = os.path.join(os.path.dirname(__file__), "image", "resize.png")
        resize_action = QAction(QIcon(icon_path), "Resize Image", self)
        resize_action.triggered.connect(wrap(self.resize_selected_image))
        self.toolbar.addAction(resize_action)
        
        self.toolbar.addSeparator()


        # Heading selector: applies font size and weight

        def apply_heading(index):
            cursor = self.editor.textCursor()
            char_fmt = QTextCharFormat()

            # define font size and font weight
            sizes = [14, 26, 22, 18, 16]
            weights = [QFont.Normal, QFont.Bold, QFont.Bold, QFont.Bold, QFont.Bold]

            char_fmt.setFontPointSize(sizes[index])
            char_fmt.setFontWeight(weights[index])

            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()

                cursor.mergeCharFormat(char_fmt)
                self.editor.setTextCursor(cursor)

                
                new_cursor = self.editor.textCursor()
                new_cursor.setPosition(start)
                new_cursor.setPosition(end, QTextCursor.KeepAnchor)
                self.editor.setTextCursor(new_cursor)
            else:
                self.editor.setCurrentCharFormat(char_fmt)

        self.heading_combo = QComboBox()
        self.heading_combo.addItems(["Normal", "Heading 1","Heading 2", "Heading 3", "Heading 4"])
        self.heading_combo.setToolTip("Heading style")
        # adjust the lenght of Comobox
        font_metrics = self.heading_combo.fontMetrics()
        max_width = max(font_metrics.width(self.heading_combo.itemText(i)) for i in range(self.heading_combo.count()))
        self.heading_combo.setMinimumWidth(max_width + 100)  # 20px padding

        self.heading_combo.currentIndexChanged.connect(apply_heading)  # ✅ بدون wrap
        self.toolbar.addWidget(self.heading_combo)


        self.toolbar.addSeparator()
        
        
        # Color choose button and its functions
        def show_color_dialog():
            dialog = QDialog(self)
            dialog.setWindowTitle("Choose Text Color")
            layout = QHBoxLayout(dialog)

            colors = ["#000000", "#FF0000", "#00AA00", "#0000FF", "#FF8800", "#8800FF", "#008888", "#888888"]
            selected_color = {"value": None}

            for color in colors:
                btn = QPushButton()
                btn.setFixedSize(32, 32)
                btn.setStyleSheet(f"background-color: {color}; border: 1px solid #444;")
                btn.clicked.connect(lambda _, c=color: (selected_color.update({"value": c}), dialog.accept()))
                layout.addWidget(btn)

            dialog.exec()
            return selected_color["value"]

        def apply_text_color():
            color = show_color_dialog()
            if not color:
                return

            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))

            
            original_format = self.editor.currentCharFormat()

            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()

                cursor.mergeCharFormat(fmt)
                self.editor.setTextCursor(cursor)

               
                new_cursor = self.editor.textCursor()
                new_cursor.setPosition(start)
                new_cursor.setPosition(end, QTextCursor.KeepAnchor)
                self.editor.setTextCursor(new_cursor)
            else:
                self.editor.setCurrentCharFormat(fmt)

        icon_path = os.path.join(os.path.dirname(__file__), "image", "text_color.png")
        color_action = QAction(QIcon(icon_path), "Text Color", self)
        self.toolbar.addAction(color_action)
        color_action.triggered.connect(apply_text_color)
        
        

        self.toolbar.addSeparator()
        
        
        def toggle_alignment():
            cursor = self.editor.textCursor()
            block_format = cursor.blockFormat()
            if block_format.alignment() == Qt.AlignLeft:
                block_format.setAlignment(Qt.AlignRight)
            else:
                block_format.setAlignment(Qt.AlignLeft)
            cursor.setBlockFormat(block_format)
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
        
        # Text alignment
        icon_path = os.path.join(os.path.dirname(__file__), "image", "text_direction.png")
        align = QAction(QIcon(icon_path), "Change Align", self)
        align.triggered.connect(wrap(toggle_alignment))
        self.toolbar.addAction(align)
        

        self.toolbar.addSeparator()
        
          
    
         # Text RTL / LTR
        icon_path = os.path.join(os.path.dirname(__file__), "image", "rtl.png")
        rtl_action = QAction(QIcon(icon_path), "RTL Action", self)
        rtl_action.setToolTip("Force Right-to-Left direction for selected text")
        rtl_action.triggered.connect(lambda: self.apply_direction_to_selection(Qt.RightToLeft))
        self.toolbar.addAction(rtl_action)
        
        
          # Text RTL / LTR
        icon_path = os.path.join(os.path.dirname(__file__), "image", "ltr.png")
        ltr_action = QAction(QIcon(icon_path), "LTR Action", self)
        ltr_action.setToolTip("Force Left-to-Right direction for selected text")
        ltr_action.triggered.connect(lambda: self.apply_direction_to_selection(Qt.LeftToRight))
        self.toolbar.addAction(ltr_action)

    
    def insert_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            from PyQt5.QtGui import QImage
            from PyQt5.QtCore import QBuffer

            image = QImage(path)
            if image.isNull():
                QMessageBox.warning(self, "Insert Failed", "Could not load image.")
                return

            buffer = QBuffer()
            buffer.open(QBuffer.WriteOnly)
            image.save(buffer, "PNG")
            img_base64 = base64.b64encode(buffer.data()).decode("utf-8")
            html = f'<img src="data:image/png;base64,{img_base64}"><br>'

            self.editor.insertHtml(html)

    def selected_image_format(self):
        """
        Returns the QTextImageFormat of the image under the current cursor, if any.
        """
        # print('[DocumentEditor->selected_image_format]')
        cursor = self.editor.textCursor()
        char_format = cursor.charFormat()
        if char_format.isImageFormat():
            return char_format.toImageFormat()
        return None

    def set_text_cursor(self, cursor):

        #solve The Right click problem on editor

         #print('[DocumentEditor->set_text_cursor]')
         self.editor.setTextCursor(cursor)

    def resize_selected_image(self):
        """
        Opens a dialog to resize the currently selected image.
        Applies percentage-based scaling while preserving aspect ratio.
        """
        # print('[DocumentEditor->resize_selected_image]')
        image_format = self.selected_image_format()
        if not image_format or not image_format.name():
            QMessageBox.warning(self, "Resize Failed", "No image selected or image path missing.")
            return

        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(image_format.name())
        original_width = pixmap.width()
        original_height = pixmap.height()

        if original_width == 0 or original_height == 0:
            QMessageBox.warning(self, "Resize Failed", "Could not load image dimensions.")
            return

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Resize Image")
        layout = QVBoxLayout(dialog)

        # Label to show current percentage
        percent_label = QLabel("Size: 100%")
        percent_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(percent_label)

        # Slider instead of SpinBox
        size_slider = QSlider(Qt.Horizontal)
        size_slider.setRange(10, 200)
        size_slider.setValue(100)
        layout.addWidget(size_slider)

        size_slider.valueChanged.connect(lambda val: percent_label.setText(f"Size: {val}%"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def apply_resize():
            scale = size_slider.value() / 100.0
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            cursor = self.editor.textCursor()

            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                temp_cursor = QTextCursor(cursor)
                temp_cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                if temp_cursor.charFormat().isImageFormat():
                    temp_cursor.deleteChar()
                    cursor = temp_cursor

            new_format = QTextImageFormat()
            new_format.setName(image_format.name())
            new_format.setWidth(new_width)
            new_format.setHeight(new_height)
            cursor.insertImage(new_format)
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
            dialog.accept()

        buttons.accepted.connect(apply_resize)
        buttons.rejected.connect(dialog.reject)
        dialog.exec()
   

    def resize_selected_image(self):
            """
            Resize the selected image (Base64 or file-based) with proper Base64 decoding,
            QPixmap reconstruction, scaling, and reinsertion.
            """
            image_format = self.selected_image_format()
            if not image_format or not image_format.name():
                return

            name = image_format.name()

            # ---------------------------------------------------------
            # 1) Load QPixmap correctly (Base64 OR a file path)
            # ---------------------------------------------------------
            
            pixmap = QPixmap()

            if name.startswith("data:image"):
                try:
                    base64_data = name.split(",")[1]
                    raw_bytes = base64.b64decode(base64_data)
                    pixmap.loadFromData(raw_bytes)
                except Exception:
                    QMessageBox.warning(self, "Resize Failed", "Could not decode Base64 image.")
                    return
            else:
                # شاید کاربر عکس از فایل وارد کرده باشد
                if not pixmap.load(name):
                    QMessageBox.warning(self, "Resize Failed", "Could not load image from file.")
                    return

            original_width = pixmap.width()
            original_height = pixmap.height()

            if original_width == 0 or original_height == 0:
                QMessageBox.warning(self, "Resize Failed", "Could not load image dimensions.")
                return

            # ---------------------------------------------------------
            # 2) Create resize dialog
            # ---------------------------------------------------------
            dialog = QDialog(self)
            dialog.setWindowTitle("Resize Image")
            layout = QVBoxLayout(dialog)

            percent_label = QLabel("Size: 100%")
            percent_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(percent_label)

            size_slider = QSlider(Qt.Horizontal)
            size_slider.setRange(10, 200)
            size_slider.setValue(100)
            layout.addWidget(size_slider)

            size_slider.valueChanged.connect(lambda v: percent_label.setText(f"Size: {v}%"))

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(buttons)

            # ---------------------------------------------------------
            # 3) Apply resize when OK is pressed
            # ---------------------------------------------------------
            def apply_resize():
                scale = size_slider.value() / 100.0
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                # Scale pixmap
                new_pixmap = pixmap.scaled(
                    new_width, new_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                # ---------------------------------------------------------
                # 4) Convert back to Base64 (always store as Base64)
                # ---------------------------------------------------------
                buffer = QBuffer()
                buffer.open(QBuffer.WriteOnly)
                new_pixmap.save(buffer, "PNG")

                new_base64 = base64.b64encode(buffer.data()).decode("utf-8")
                new_src = f"data:image/png;base64,{new_base64}"

                # ---------------------------------------------------------
                # 5) Insert image back into the document
                # ---------------------------------------------------------
                cursor = self.editor.textCursor()

                # اگر کاربر تصویر را انتخاب کرده بود → پاک کن
                if cursor.hasSelection():
                    cursor.removeSelectedText()
                else:
                    # اگر روی تصویر هست → تصویر قبلی را حذف کن
                    temp_cursor = QTextCursor(cursor)
                    temp_cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                    if temp_cursor.charFormat().isImageFormat():
                        temp_cursor.deleteChar()
                        cursor = temp_cursor

                # فرمت جدید + سایز جدید
                new_format = QTextImageFormat()
                new_format.setName(new_src)
                new_format.setWidth(new_width)
                new_format.setHeight(new_height)

                cursor.insertImage(new_format)
                self.editor.setTextCursor(cursor)
                self.editor.setFocus()

                dialog.accept()

            buttons.accepted.connect(apply_resize)
            buttons.rejected.connect(dialog.reject)

            dialog.exec()
        
   
   
    
    def mousePressEvent(self, event):
       
        super().mousePressEvent(event)
        if self.parent():
            self.parent().mousePressEvent(event)

    def activate_readonly_mode(self , init = False):
        self.readonly_mode = True
        self.toolbar.hide()
        self.editor.setReadOnly(True)       
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if not init :
            self.adjust_height_document_editor()
        
    

    def activate_edit_mode(self):
        self.readonly_mode = False
        self.toolbar.show()
        self.editor.setReadOnly(False)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        #self.editor.setStyleSheet(self.editor.styleSheet().replace("border: none;", "border: 1px solid #444;"))
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

    def apply_direction_to_selection(self, direction: Qt.LayoutDirection):
        cursor = self.editor.textCursor()

        # اگر چیزی انتخاب نشده بود، فقط روی بلاک جاری اعمال کن
        if not cursor.hasSelection():
            block = cursor.block()
            temp_cursor = QTextCursor(block)
            block_format = temp_cursor.blockFormat()
            block_format.setLayoutDirection(direction)
            temp_cursor.mergeBlockFormat(block_format)
            return

        # اگر انتخاب وجود دارد، روی همهٔ بلاک‌ها اعمال کن
        start = min(cursor.selectionStart(), cursor.selectionEnd())
        end = max(cursor.selectionStart(), cursor.selectionEnd())

        doc = self.editor.document()
        block = doc.findBlock(start)
        end_block = doc.findBlock(end)

        while block.isValid() and block.position() <= end_block.position():
            temp_cursor = QTextCursor(block)
            block_format = temp_cursor.blockFormat()
            block_format.setLayoutDirection(direction)
            temp_cursor.mergeBlockFormat(block_format)
            block = block.next()
    
    def update_heading_combo(self):
        cursor = self.editor.textCursor()
        

        if cursor.hasSelection():
            self.heading_combo.blockSignals(True)
            self.heading_combo.setCurrentIndex(-1)
            self.heading_combo.blockSignals(False)
            return
          
        
        
        fmt = cursor.charFormat()
        size = fmt.fontPointSize()
        
        if size == 26:
            self.heading_combo.setCurrentIndex(1)  # Heading 1
        elif size == 18:
            self.heading_combo.setCurrentIndex(2)  # Heading 2
        elif size == 18:
            self.heading_combo.setCurrentIndex(3)  # Heading 3
        elif size == 16:
            self.heading_combo.setCurrentIndex(4)  # Heading 4
        else:
            self.heading_combo.setCurrentIndex(0)  # Normal
 
 
    def adjust_height_document_editor(self):
        print('[adjust_height_document_editor]')
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
        # print(f"Applied new_h: {new_height}, editor.h now: {self.editor.height()}")
        # doc = self.editor.document()
        # layout = doc.documentLayout()

        # print(f"widgetResizable: {self.scroll_area.widgetResizable()}")
        # print(f"documentSize.h: {layout.documentSize().height()}")   # ارتفاع واقعی محتوای رندرشده
        # print(f"documentMargin: {doc.documentMargin()}")

        # cm = self.editor.contentsMargins()
        # print(f"contentsMargins: {cm.left()}, {cm.top()}, {cm.right()}, {cm.bottom()}")
        # print(f"frameWidth: {self.editor.frameWidth()}")

        # print(f"sizeHint.h: {self.editor.sizeHint().height()}")
        # print(f"viewport.h: {self.scroll_area.viewport().size().height()}")
        # print(f"editor.h before: {self.editor.height()}")
     
    def set_fixed_height(self , height = 0):
        """Set editor to exact pixel height (from metadata)"""
        print('[SET FIXED HEIGHT METHOD] ' ,height)
        """
        Force editor to exact pixel height.
        """
        self.setFixedHeight(height)   # دقیقاً همون ارتفاع
        self.resize(self.width(), height)  # اگر داخل layout باشه، این هم کمک می‌کنه
        self.updateGeometry()


        
        
    

