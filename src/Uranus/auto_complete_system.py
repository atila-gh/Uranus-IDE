import  jedi
from PyQt5.QtGui import  QTextCursor, QTextCursor,QKeySequence , QColor 
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QShortcut,
    QLabel,
    
)


class AutoCompleteSystem(QFrame):

    def __init__(self, editor):
        super().__init__(editor)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.WindowStaysOnTopHint)

        self.editor = editor
        self.active = False
        self.completions_cache = []

        self.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QListWidget {
                background: #1e1e1e;
                color: white;
                border: none;
                outline: none;
                padding: 2px;
                font-family: Consolas;
                font-size: 9pt;
            }
            QListWidget::item {
                padding: 3px 6px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background: #264f78;
                color: white;
            }
        """)

        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self.complete_selected)
        self.list_widget.currentItemChanged.connect(self.update_doc_popup)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.list_widget)

        # Documentation popup
        self.doc_popup = QFrame(editor)
        self.doc_popup.setWindowFlags(Qt.WindowType.ToolTip)
        self.doc_popup.setStyleSheet("""
            QFrame {
                background: #252526;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QLabel {
                color: white;
                padding: 6px;
                font-family: Consolas;
                font-size: 8pt;
            }
        """)

        self.doc_label = QLabel()
        self.doc_label.setWordWrap(True)
        self.doc_label.setMaximumWidth(250)

        doc_layout = QVBoxLayout(self.doc_popup)
        doc_layout.setContentsMargins(4, 4, 4, 4)
        doc_layout.addWidget(self.doc_label)

            # تایمر برای تاخیر در پاسخ به تغییرات متن
        self.text_change_timer = QTimer()
        self.text_change_timer.setSingleShot(True)
        self.text_change_timer.timeout.connect(self.on_text_changed_delayed)
        self.editor.textChanged.connect(self.text_change_timer.start)

        # Ctrl+Space برای فعال‌سازی دستی
        QShortcut(QKeySequence("Ctrl+Space"), editor, self.activate_and_show)

        self.hide()
        self.doc_popup.hide()

    def activate_and_show(self):
        self.active = True
        self.setVisible(True)
        self.show()
        self.show_completions()

    def deactivate(self):
        self.active = False
        self.hide()
        if hasattr(self, 'doc_popup'):
            self.doc_popup.hide()
        self.setVisible(False)

    def on_text_changed_delayed(self):
        if self.active:
            self.show_completions()

    def get_current_word(self):
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()

    def get_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber()
        return line, column

    def get_full_code(self):
        return self.editor.toPlainText()

    def show_completions(self):
        if not self.active:
            return

        code = self.get_full_code()
        line, column = self.get_cursor_position()

        try:
            script = jedi.Script(code=code, path='temp_editor.py')
            completions = script.complete(line=line, column=column)

            if not completions:
                self.hide()
                self.doc_popup.hide()
                return

            self.completions_cache = completions
            self.list_widget.clear()

            for completion in completions[:20]:
                item = QListWidgetItem(completion.name)
                color = self.get_color_for_type(completion.type)
                item.setForeground(QColor(color))
                item.setData(Qt.ItemDataRole.UserRole, completion)
                self.list_widget.addItem(item)

            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)

            cursor_rect = self.editor.cursorRect()
            global_pos = self.editor.mapToGlobal(cursor_rect.bottomRight())

            self.move(global_pos.x(), global_pos.y() + 4)
            self.resize(220, 120)
            self.show()
            self.raise_()
            self.update_doc_popup()

        except Exception as e:
            print(f"[Jedi Error] {e}")
            self.hide()
            self.doc_popup.hide()

    def get_color_for_type(self, completion_type):
        colors = {
            'module': '#BA68C8',
            'class': '#FFD54F',
            'function': '#FFD54F',
            'method': '#FFD54F',
            'property': '#81C784',
            'statement': '#64B5F6',
            'keyword': '#FF6347',
            'param': '#9CDCFE',
            'path': '#CE9178',
            'builtin': '#FFD54F',
        }
        return colors.get(completion_type, '#D4D4D4')

    def update_doc_popup(self):
            current_item = self.list_widget.currentItem()
            if not current_item:
                self.doc_popup.hide()
                return

            completion = current_item.data(Qt.ItemDataRole.UserRole)
            if not completion:
                self.doc_popup.hide()
                return

            name = completion.name
            signature = completion.complete or name
            docstring = completion.docstring() or "No documentation available"
            completion_type = completion.type or "unknown"

            if len(docstring) > 200:
                docstring = docstring[:200] + "..."

            html = f"""
            <div style="font-family: Consolas; font-size: 8pt;">
            <span style="font-size: 10pt;"><b>{name}</b></span>
            <br>
            <span style="color:#4FC1FF; font-size: 8pt;">{signature}</span>
            <br>
            <span style="color:#C586C0; font-size: 8pt;">Type:</span>
            <span style="color:#CE9178; font-size: 8pt;">{completion_type}</span>
            <br>
            <span style="color:#D4D4D4; font-size: 8pt;">{docstring}</span>
            </div>
            """

            self.doc_label.setText(html)
            self.doc_popup.adjustSize()

            if self.doc_popup.width() > 250:
                self.doc_popup.resize(250, self.doc_popup.height())

            popup_pos = self.mapToGlobal(self.rect().topRight())
            self.doc_popup.move(popup_pos.x() + 5, popup_pos.y())
            self.doc_popup.show()

    def complete_selected(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        completion = current_item.data(Qt.ItemDataRole.UserRole)
        if not completion:
            return

        cursor = self.editor.textCursor()
        current_pos = cursor.position()

        # ===== دریافت کلمه زیر مکان‌نما با روش دستی =====
        line_text = cursor.block().text()
        pos_in_block = cursor.positionInBlock()

        # پیدا کردن شروع کلمه (از موقعیت فعلی به عقب)
        start = pos_in_block
        for i in range(pos_in_block - 1, -1, -1):
            if line_text[i].isalnum() or line_text[i] == '_':
                start = i
            else:
                break

        # پیدا کردن پایان کلمه (از موقعیت فعلی به جلو)
        end = pos_in_block
        for i in range(pos_in_block, len(line_text)):
            if line_text[i].isalnum() or line_text[i] == '_':
                end = i + 1
            else:
                break

        full_word = line_text[start:end]
        start_pos = cursor.position() - (pos_in_block - start)
        end_pos = cursor.position() + (end - pos_in_block)

        print(f"[DEBUG] full_word: '{full_word}'")
        print(f"[DEBUG] start_pos: {start_pos}, end_pos: {end_pos}")

        # ===== بررسی یک کاراکتر سمت چپ =====
        left_char = ''
        if start_pos > 0:
            left_char = line_text[start - 1] if start - 1 >= 0 else ''
        print(f"[DEBUG] left_char: '{left_char}'")

        # ===== بررسی یک کاراکتر سمت راست =====
        right_char = ''
        if end_pos < len(line_text):
            right_char = line_text[end] if end < len(line_text) else ''
        print(f"[DEBUG] right_char: '{right_char}'")

        # ===== اگر کلمه انتخاب‌شده دقیقاً '()' یا '[]' یا '{}' بود =====
        if full_word in ['()', '[]', '{}']:
            print("[DEBUG] Special case: empty parentheses")
            left_paren = full_word[0]
            right_paren = full_word[1]
            final_text = left_paren + completion.name + right_paren
            print(f"[DEBUG] final_text: '{final_text}'")

            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(final_text)

            cursor.movePosition(QTextCursor.MoveOperation.Right, 
                                QTextCursor.MoveMode.MoveAnchor, len(final_text))

            self.active = False
            self.hide()
            if hasattr(self, 'doc_popup'):
                self.doc_popup.hide()

            self.editor.setFocus()
            self.editor.setTextCursor(cursor)
            return

        # ===== حالت عادی =====
        final_text = completion.name
        print(f"[DEBUG] initial final_text: '{final_text}'")

        # ===== اگر full_word خالی نیست =====
        if full_word:
            # کلمه انتخاب شده رو حذف کن
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()

            # کلمه جدید رو جایگزین کن
            cursor.insertText(final_text)
        else:
            # ===== full_word خالی است =====
            # یعنی کاربر فقط پرانتز تایپ کرده و هیچ کلمه‌ای وجود نداره
            # فقط کلمه جدید رو اضافه کن
            cursor.insertText(final_text)

        # ===== مکان‌نما رو به بعد از کلمه درج شده ببر =====
        cursor.movePosition(QTextCursor.MoveOperation.Right, 
                            QTextCursor.MoveMode.MoveAnchor, len(final_text))

        self.active = False
        self.hide()
        if hasattr(self, 'doc_popup'):
            self.doc_popup.hide()

        self.editor.setFocus()
        self.editor.setTextCursor(cursor)
        print("[DEBUG] complete_selected finished")

    def select_previous(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.list_widget.setCurrentRow(row - 1)
        else:
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def select_next(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(row + 1)
        else:
            self.list_widget.setCurrentRow(0)

    def keyPressEvent(self, event):
        if not self.isVisible():
            event.ignore()
            return

        key = event.key()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
            self.complete_selected()
        elif key == Qt.Key.Key_Escape:
            self.deactivate()
            self.editor.setFocus()
        elif key == Qt.Key.Key_Up:
            self.select_previous()
        elif key == Qt.Key.Key_Down:
            self.select_next()
        else:
            super().keyPressEvent(event)

    def hideEvent(self, event):
        if hasattr(self, 'doc_popup'):
            self.doc_popup.hide()
        super().hideEvent(event)
