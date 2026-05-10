from math import ceil 
import  json , re , os
from PyQt5.QtGui import  QFont,QFontMetrics,QTextCursor, QTextCursor,QKeySequence , QColor
from PyQt5.QtCore import Qt,pyqtSignal,QEvent 
from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QShortcut,
    QLabel,
    QPlainTextEdit,
    QApplication
    
)

from Uranus.CodeHighlight import CodeHighlighter
from Uranus.SettingWindow import load_setting  


class AutoCompleteSystem(QFrame):
    def __init__(self, editor):
        super().__init__(editor)

        self.setWindowFlags(Qt.ToolTip)
        self.editor = editor
        
        # وضعیت فعال بودن (بعد از Ctrl+Space فعال می‌شود)
        self.active = False

        self.load_database()

        self.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 1px solid #444;
                border-radius: 6px;
            }

            QListWidget {
                background: #1e1e1e;
                color: white;
                border: none;
                outline: none;
                padding: 4px;
                font-family: Consolas;
                font-size: 11pt;
            }

            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
            }

            QListWidget::item:selected {
                background: #264f78;
                color: white;
            }
        """)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.complete_selected)
        self.list_widget.currentItemChanged.connect(self.update_doc_popup)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.list_widget)

        # Documentation popup
        self.doc_popup = QFrame(editor)
        self.doc_popup.setWindowFlags(Qt.ToolTip)
        self.doc_popup.setStyleSheet("""
            QFrame {
                background: #252526;
                border: 1px solid #444;
                border-radius: 6px;
            }

            QLabel {
                color: white;
                padding: 10px;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)

        self.doc_label = QLabel()
        self.doc_label.setWordWrap(True)

        doc_layout = QVBoxLayout(self.doc_popup)
        doc_layout.setContentsMargins(6, 6, 6, 6)
        doc_layout.addWidget(self.doc_label)

        # اتصال به textChanged برای به‌روزرسانی زنده (فقط وقتی active است)
        self.editor.textChanged.connect(self.on_text_changed)

        # manual trigger با Ctrl+Space
        QShortcut(QKeySequence("Ctrl+Space"), editor, self.activate_and_show)

        self.hide()
        self.doc_popup.hide()

    def activate_and_show(self):
        """فعال کردن سیستم و نمایش لیست"""
        self.active = True
        self.show_completions()

    def deactivate(self):
        """غیرفعال کردن سیستم و بستن لیست"""
        self.active = False
        self.hide()
        self.doc_popup.hide()

    def on_text_changed(self):
        """هنگام تغییر متن - فقط اگر active باشد"""
        if self.active:
            self.show_completions()

    # =========================================================
    # DATABASE
    # =========================================================

    def load_database(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "autocomplete_db.json")
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

        self.all_commands_data = {}
        self.module_colors = {}

        # modules
        for module_name, module_data in self.db.get("modules", {}).items():
            color = module_data.get("color", "#87CEEB")
            self.module_colors[module_name] = color
            for name, data in module_data.get("items", {}).items():
                data["source_module"] = module_name
                self.all_commands_data[name] = data

        # builtins
        builtins_data = self.db.get("builtins", {})
        self.module_colors["builtins"] = builtins_data.get("color", "#FFFFFF")
        for name, data in builtins_data.get("items", {}).items():
            data["source_module"] = "builtins"
            self.all_commands_data[name] = data

        # keywords
        keyword_data = self.db.get("python_keywords", {})
        self.module_colors["python_keywords"] = keyword_data.get("color", "#FF6347")
        for name, data in keyword_data.get("items", {}).items():
            data["source_module"] = "python_keywords"
            self.all_commands_data[name] = data

        # magic_methods
        magic_data = self.db.get("magic_methods", {})
        self.module_colors["magic_methods"] = magic_data.get("color", "#C586C0")
        for name, data in magic_data.get("items", {}).items():
            data["source_module"] = "magic_methods"
            self.all_commands_data[name] = data

        # context_vars
        context_data = self.db.get("context_vars", {})
        self.module_colors["context_vars"] = context_data.get("color", "#9CDCFE")
        for name, data in context_data.get("items", {}).items():
            data["source_module"] = "context_vars"
            self.all_commands_data[name] = data

        self.command_names = list(self.all_commands_data.keys())

    # =========================================================
    # CONTEXT
    # =========================================================

    def get_current_context(self):
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        pos_in_block = self.editor.textCursor().positionInBlock()
        line_text = line_text[:pos_in_block]

        module_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z0-9_]*)$", line_text)
        if module_match:
            return module_match.group(1), module_match.group(2)

        word_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", line_text)
        if word_match:
            return None, word_match.group(1)

        return None, ""

    # =========================================================
    # SHOW
    # =========================================================

    def show_completions(self):
        if not self.active:
            return
            
        module_name, prefix = self.get_current_context()

        if not prefix or len(prefix) < 1:
            self.hide()
            self.doc_popup.hide()
            return

        suggestions = []

        if module_name and module_name in self.db.get("modules", {}):
            items = self.db["modules"][module_name]["items"]
            for name, data in items.items():
                if name.startswith(prefix):
                    suggestions.append((name, data))
        else:
            # builtins
            for name, data in self.db.get("builtins", {}).get("items", {}).items():
                if name.startswith(prefix):
                    suggestions.append((name, data))
            
            # python keywords
            for name, data in self.db.get("python_keywords", {}).get("items", {}).items():
                if name.startswith(prefix):
                    suggestions.append((name, data))
            
            # magic methods
            for name, data in self.db.get("magic_methods", {}).get("items", {}).items():
                if name.startswith(prefix):
                    suggestions.append((name, data))
            
            # context vars
            for name, data in self.db.get("context_vars", {}).get("items", {}).items():
                if name.startswith(prefix):
                    suggestions.append((name, data))
            
            # all modules
            for module_name, module_data in self.db.get("modules", {}).items():
                for name, data in module_data.get("items", {}).items():
                    if name.startswith(prefix) and (name, data) not in suggestions:
                        suggestions.append((name, data))

        if not suggestions:
            self.hide()
            self.doc_popup.hide()
            return

        def source_priority(data):
            src = data.get("source_module", "")
            if src == "builtins":
                return 0
            elif src == "python_keywords":
                return 1
            elif src == "magic_methods":
                return 2
            elif src == "context_vars":
                return 3
            else:
                return 4
        
        suggestions.sort(key=lambda x: (source_priority(x[1]), len(x[0]), x[0]))
        
        self.list_widget.clear()

        for name, data in suggestions[:30]:
            item = QListWidgetItem(name)
            source = data.get("source_module", "")
            
            if source == "magic_methods":
                color = "#C586C0"
            elif source == "context_vars":
                color = "#9CDCFE"
            else:
                color = self.module_colors.get(source, "#FFFFFF")
            
            item.setForeground(QColor(color))
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        cursor_rect = self.editor.cursorRect()
        global_pos = self.editor.mapToGlobal(cursor_rect.bottomRight())

        self.move(global_pos.x(), global_pos.y() + 4)
        self.resize(280, 180)
        self.show()
        self.update_doc_popup()

    # =========================================================
    # DOC POPUP
    # =========================================================

    def update_doc_popup(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            self.doc_popup.hide()
            return

        name = current_item.text()
        data = self.all_commands_data.get(name)

        if not data:
            self.doc_popup.hide()
            return

        signature = data.get("signature", "")
        doc = data.get("doc", "")
        source = data.get("source_module", "")

        html = f"""
        <div style="font-family: Consolas;">
        <span style="font-size: 13pt;"><b>{name}</b></span>
        <br><br>
        <span style="color:#4FC1FF;">{signature}</span>
        <br><br>
        <span style="color:#C586C0;">Source:</span>
        <span style="color:#CE9178;">{source}</span>
        <br><br>
        <span style="color:#D4D4D4;">{doc}</span>
        </div>
        """

        self.doc_label.setText(html)
        self.doc_popup.adjustSize()

        popup_pos = self.mapToGlobal(self.rect().topRight())
        self.doc_popup.move(popup_pos.x() + 10, popup_pos.y())
        self.doc_popup.show()

    # =========================================================
    # COMPLETE
    # =========================================================

    def complete_selected(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        completion = current_item.text()
        module_name, prefix = self.get_current_context()

        cursor = self.editor.textCursor()
        
        # حذف prefix فعلی
        for _ in range(len(prefix)):
            cursor.deletePreviousChar()
        
        # درج کلمه کامل
        cursor.insertText(completion)

        # غیرفعال کردن سیستم بعد از تکمیل
        self.deactivate()
        self.editor.setFocus()

    # =========================================================
    # KEY EVENTS
    # =========================================================

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
        if not self.active:
            event.ignore()
            return
            
        key = event.key()

        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
            self.complete_selected()
            return
        elif key == Qt.Key_Escape:
            self.deactivate()
            self.editor.setFocus()
            return
        elif key == Qt.Key_Up:
            self.select_previous()
            return
        elif key == Qt.Key_Down:
            self.select_next()
            return

        super().keyPressEvent(event)

    def hideEvent(self, event):
        self.doc_popup.hide()
        super().hideEvent(event)



class CodeEditor(QPlainTextEdit):
    cursorPositionInfo = pyqtSignal(int, int)   # سیگنال ارسال شماره خط و کاراکتر 
    clicked = pyqtSignal()

    """
        A custom plain text editor designed for code cells in the Uranus IDE.

        Features:
        - Monospaced font with syntax highlighting via CodeHighlighter.
        - Emits real-time cursor position updates (line and column) via `cursorPositionInfo`.
        - Supports block-level indentation/unindentation with Tab and Shift+Tab.
        - Auto-inserts paired characters (quotes, brackets, braces, parentheses).
        - Smart commenting/uncommenting with Ctrl+/ for single or multi-line selections.
        - Auto-indents after colon (:) for Python blocks.
        - Handles visual column calculation with tab-aware logic.
        - Dynamically adjusts height based on content (line count).

        Signals:
        - cursorPositionInfo(int line, int column): Emitted after each key press to update line/column info.
        - clicked(): Emitted when the editor is clicked, used to notify parent cell.

        Settings:
        - Tab size, font, colors, and syntax highlighting are loaded from external configuration via `load_setting()`.

        Usage:
        This editor is embedded inside Cell widgets and interacts with the kernel for code execution.
        It is optimized for Python editing but can be extended for other languages via the highlighter.
        """

    def __init__(self, parent=None):
        #print('[CodeEditor->__init__]')

        super().__init__(parent)
        setting = load_setting()
        self.copy = self.my_copy()
        self.autocomplete_status = False # define the auto complet On or Off
        
        # ------ Setting 
        self.tab_size = 4  # تعداد فاصله برای هر تب
        bg_code         = setting['colors']['Back Ground Color Code']       
        fg_code         = setting['colors']['ForGround Color Code']
        code_font       = setting['Code Font']
        code_font_size  = setting['Code Font Size']
      

        # ✅ ارتفاع اولیه (مثلاً 80 پیکسل)
        
        self.setFixedHeight(80)        
        self.setFont(QFont(code_font, code_font_size,QFont.Bold))  # تست با فونت معتبر        
        self.installEventFilter(self)
        self.setTabStopDistance(self.tab_size * self.fontMetrics().horizontalAdvance(' ')) # adjust Tab From 8 Char to 4
        
        self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {bg_code};
                    color: {fg_code};  
                    border: 1px solid #444;
                    padding: 4px;
                    selection-background-color: #264f78;
                    selection-color: #ffffff;
                }}
            """)


       
        # حذف اسکرول و اتصال تغییر ارتفاع
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # noinspection PyTypeChecker

       
        # ✅ فعال‌سازی های‌لایت سینتکس
        self.highlighter = CodeHighlighter(self.document())
        self.autocomplete = AutoCompleteSystem(self)



    @staticmethod
    def get_visual_column(cursor, tab_size=4):
        block_text = cursor.block().text()
        column = 0
        limit = min(cursor.positionInBlock(), len(block_text))
        for i in range(limit):
            if block_text[i] == '\t':
                column += tab_size - (column % tab_size)
            else:
                column += 1
        return column + 1

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.adjust_height_code()
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):

        
        def delayed_emit():
            QApplication.processEvents() 
            _cursor = self.textCursor()
            line = _cursor.blockNumber() + 1
            column = self.get_visual_column(_cursor, self.tab_size)
            self.cursorPositionInfo.emit(line, column)
            
            
             # اگر اتوکامپلیت فعال است، کلیدها را به آن بده
            if hasattr(self, 'autocomplete') and self.autocomplete.active:
                # اگر کلید Escape بود، اتوکامپلیت خودش مدیریت می‌کند
                if event.key() == Qt.Key_Escape:
                    self.autocomplete.keyPressEvent(event)
                    delayed_emit()
                    return
                # اگر Enter یا Tab بود
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
                    self.autocomplete.keyPressEvent(event)
                    delayed_emit()
                    return
                # اگر بالا یا پایین بود
                elif event.key() in (Qt.Key_Up, Qt.Key_Down):
                    self.autocomplete.keyPressEvent(event)
                    return
        
        cursor = self.textCursor()
        selected_text = cursor.selectedText()  
        
       

        # # ---------- Tab / Shift+Tab for selected block ----------
        
        if event.key() == Qt.Key_Tab and cursor.hasSelection():
           
            try:
                cursor.beginEditBlock()
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())

                block = self.document().findBlock(start)
                end_block = self.document().findBlock(end)

                while block.isValid() and block.position() <= end_block.position():
                    line_cursor = QTextCursor(block)
                    line_cursor.movePosition(QTextCursor.StartOfBlock)
                    line_cursor.insertText(" " * self.tab_size)
                    block = block.next()

                cursor.endEditBlock()
                delayed_emit()
                return

            except Exception as e:
                pass
                # print(f"[Tab Error] {e}")
        
        elif event.key() == Qt.Key_Backtab and cursor.hasSelection():
           
            try:
                cursor.beginEditBlock()
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())

                block = self.document().findBlock(start)
                end_block = self.document().findBlock(end)

                while block.isValid() and block.position() <= end_block.position():
                    line_cursor = QTextCursor(block)
                    block_text = block.text()
                    leading_spaces = len(block_text) - len(block_text.lstrip())
                    remove_count = min(self.tab_size, leading_spaces)
                    if remove_count > 0:
                        line_cursor.movePosition(QTextCursor.StartOfBlock)
                        line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, remove_count)
                        line_cursor.removeSelectedText()
                    block = block.next()

                cursor.endEditBlock()
                delayed_emit()
                return

            except Exception as e:
                pass
                # print(f"[Shift+Tab Error] {e}")
        
        elif event.key() == Qt.Key_Backtab :
            try:
                cursor.beginEditBlock()
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())

                block = self.document().findBlock(start)
                end_block = self.document().findBlock(end)

                while block.isValid() and block.position() <= end_block.position():
                    line_cursor = QTextCursor(block)
                    block_text = block.text()
                    leading_spaces = len(block_text) - len(block_text.lstrip())
                    remove_count = min(self.tab_size, leading_spaces)
                    if remove_count > 0:
                        line_cursor.movePosition(QTextCursor.StartOfBlock)
                        line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, remove_count)
                        line_cursor.removeSelectedText()
                    block = block.next()

                cursor.endEditBlock()
                delayed_emit()
                return

            except Exception as e:
                pass
                # print(f"[Shift+Tab Error] {e}")
        # ---------- Shift + Down → Select previous word ----------
        if event.key() == Qt.Key_Down and event.modifiers() == Qt.ControlModifier:
           
            cursor.movePosition(QTextCursor.PreviousWord, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            return
        
        # ---------- Shift + Left → Select Current Line ----------
        if event.key() == Qt.Key_Left and event.modifiers() == Qt.ControlModifier:
          
            cursor = self.textCursor()
            current_pos = cursor.positionInBlock()
            if current_pos > 0:
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, current_pos)
                self.setTextCursor(cursor)
            delayed_emit()
            return

        
        #---------- quote and double quote control ----------
        if event.text() in ["'", '"'] and not cursor.hasSelection():
            quote = event.text()
            cursor = self.textCursor()
            block_text = cursor.block().text()
            pos_in_block = cursor.positionInBlock()

            # بررسی تعداد کوتیشن‌های پشت سر کرسر
            count_behind = 0
            i = pos_in_block - 1
            while i >= 0 and block_text[i] == quote:
                count_behind += 1
                i -= 1

            if count_behind == 0:
                # حالت ۱: هیچ کوتیشن پشت کرسر نیست → درج دو تا و کرسر وسط
                cursor.insertText(f"{quote}{quote}")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                

            elif count_behind == 1:
                # حالت ۲: یک کوتیشن پشت کرسر → فقط کرسر جلو بره
                cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                

            elif count_behind == 2:
                # حالت ۳: دو کوتیشن پشت کرسر → یک کوتیشن اضافه کن، سه تا جلو، کرسر وسط
                cursor.insertText(quote)  # اضافه کردن سومین کوتیشن پشت سر
                cursor.insertText(f"{quote*3}")  # سه تا جلوی کرسر
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 3)
                self.setTextCursor(cursor)
            delayed_emit()
            return


        # ---------- Auto wrap selected text in quotes ----------
        if event.text() in ["'", '"'] and selected_text:
            quote = event.text()
            cursor.insertText(f"{quote}{selected_text}{quote}")
            delayed_emit()
            return

        # ------------- Comment Line Enter Control -----------
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            pos_in_block = cursor.positionInBlock()

            if block_text.strip().startswith("#"):
                if pos_in_block != 0:
                    cursor.movePosition(QTextCursor.EndOfBlock)
                    self.setTextCursor(cursor)
                
                
                #  After any Enter Key Pressed Indation Must get Fixed       
                self.fix_indentation(self.tab_size)
                #print('[FIX INDENTATION]')
                
                super().keyPressEvent(event)  # اینتر واقعی برای خطوط غیرکامنت
                delayed_emit()
                return
      
        # ---------- Wrap selected text in parentheses ----------
        if event.text() == "(":
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            if selected_text:
                cursor.insertText(f"({selected_text})")
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
            else:
                cursor.insertText("()")
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
                self.setTextCursor(cursor)

            delayed_emit()
            return


        # ---------- Wrap selected text in Brace ----------
        if event.text() == "{":
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            if selected_text:
                cursor.insertText(f"{{{selected_text}: }}")
                cursor.setPosition(cursor.position() - 1)
                self.setTextCursor(cursor)
            else:
                cursor.insertText("{}")
                cursor.setPosition(cursor.position() - 1)
                self.setTextCursor(cursor)

            delayed_emit()    
            return

        # ---------- Wrap selected text in brackets ----------
        if event.text() == "[":
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            if selected_text:
                cursor.insertText(f"[{selected_text} , ]")
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 2)
                self.setTextCursor(cursor)
            else:
                cursor.insertText("[]")
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
            delayed_emit()
            return


        # ---------- Auto Unindent for Backspace ----------
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            pos_in_block = cursor.positionInBlock()
            block_text = cursor.block().text()
            indent = len(block_text) - len(block_text.lstrip())

            if pos_in_block <= indent and indent > 0:
                remove_count = min(self.tab_size, pos_in_block)
                cursor.movePosition(cursor.Left, cursor.KeepAnchor, remove_count)
                cursor.removeSelectedText()
            else :
                # بک‌اسپیس معمولی
                 super().keyPressEvent(event)

            delayed_emit()
            return


        
        # -----------------make current line Comment --------------
        if event.key() == Qt.Key_Slash and event.modifiers() & Qt.ControlModifier:
            cursor = self.textCursor()

            cursor.beginEditBlock()

            # حالت چند خط انتخاب‌شده
            if cursor.hasSelection():
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())

                block = self.document().findBlock(start)
                end_block = self.document().findBlock(end)

                # بررسی اینکه آیا همه‌ی خطوط کامنت هستند
                all_commented = True
                check_block = block
                while check_block.isValid() and check_block.position() <= end_block.position():
                    if not check_block.text().strip().startswith("#"):
                        all_commented = False
                        break
                    check_block = check_block.next()

                                # اعمال تغییرات
                while block.isValid() and block.position() <= end_block.position():
                    line_cursor = QTextCursor(block)
                    line_text = block.text()
                    line_cursor.movePosition(QTextCursor.StartOfBlock)
                    if all_commented:
                        # حذف کامنت
                        index = line_text.find("#")
                        if index != -1:
                            after_hash = line_text[index+1:].lstrip()
                            end_index = len(line_text) - len(after_hash)

                            line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end_index)
                            line_cursor.removeSelectedText()
                    else:
                        # اضافه کردن کامنت
                        line_cursor.insertText("# ")
                    block = block.next()

            # حالت بدون انتخاب → فقط خط جاری
            else:
                block = cursor.block()
                block_text = block.text()
                line_cursor = QTextCursor(block)
                line_cursor.movePosition(QTextCursor.StartOfBlock)
                if block_text.strip().startswith("#"):
                    index = block_text.find("#")
                    if index != -1:
                        after_hash = block_text[index+1:].lstrip()
                        end_index = len(block_text) - len(after_hash)

                        line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,end_index)
                        line_cursor.removeSelectedText()
                else:
                    line_cursor.insertText("# ")

            cursor.endEditBlock()
            delayed_emit()
            return    



        
        # ---------- Auto Indent for Enter after : ----------
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            base_indent = len(block_text) - len(block_text.lstrip())

            if base_indent > 0 and base_indent % self.tab_size > 0:
               
                fix_indent = self.tab_size - (base_indent % self.tab_size)
                cursor.beginEditBlock()
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.insertText(" " * fix_indent)
                cursor.endEditBlock()

                # recalculate base indent
                block_text = cursor.block().text()
                base_indent = len(block_text) - len(block_text.lstrip())
               

            # بررسی موقعیت کرسر نسبت به انتهای خط
            cursor_at_end = cursor.positionInBlock() >= len(block_text.rstrip())
            ends_with_colon = block_text.rstrip().endswith(":")

            add_indent = self.tab_size if ends_with_colon and cursor_at_end else 0
            total_indent = base_indent + add_indent
            
            super().keyPressEvent(event)

            if total_indent > 0:
                if total_indent % self.tab_size > 0:
                    total_indent = ceil(total_indent / self.tab_size) * self.tab_size
        
                self.insertPlainText(" " * total_indent)

            delayed_emit()
            return


        # ---------- Default ----------       
           
        super().keyPressEvent(event)    
            
        delayed_emit()        
        self.highlighter.triple_quote_ranges = self.highlighter.find_triple_quote_blocks()
        self.highlighter.rehighlight()
        return

    def adjust_height_code(self):
        # print('[CodeEditor->adjust_height_code]')
        if not self:
            return

        font_metrics = QFontMetrics(self.font())
        line_height = font_metrics.lineSpacing()
        base_height = 1  
        block_count = self.blockCount()
        padding =  line_height * 1
        new_height = int(block_count * line_height + padding + base_height)
        self.setFixedHeight(new_height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # noinspection PyTypeChecker

    def mousePressEvent(self, event):
        
        super().mousePressEvent(event)
        if self.parent():
            self.parent().mousePressEvent(event)


    def my_copy(self):
        
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # حذف فضای خالی قبل و بعد
            trimmed_text = selected_text.strip()
            # ذخیره در حافظه (clipboard)
            QApplication.clipboard().setText(trimmed_text)
        else:
            super().copy()


    def fix_indentation(self, tab_size=4):
        '''
        This method is for solve 
        '''
        #print('[Indentation Fixed]')
        
        text = self.toPlainText()
        lines = text.split("\n")

        fixed = []

        for line in lines:
            # جدا کردن بخش اول خط (indentation)
            prefix = ""
            rest = line.lstrip(" \t")

            for ch in line:
                if ch in (" ", "\t"):
                    prefix += ch
                else:
                    break

            # اول همه tab ها را تبدیل کن
            prefix = prefix.replace("\t", " " * tab_size)

            # حالا تعداد اسپیس‌ها را استاندارد کن (اختیاری ولی بهتر)
            # مثلا همیشه مضرب 4 شود
            spc = len(prefix)
            level = spc // tab_size
            prefix = " " * (level * tab_size)

            fixed.append(prefix + rest)

        new_text = "\n".join(fixed)
        self.setPlainText(new_text)


    # Only for Debuging Indentation Method
    
    # def debug_indentation(self):
    #     text = self.toPlainText()

    #     print("\n===== INDENT DEBUG START =====")

    #     for i, line in enumerate(text.split("\n"), 1):

    #         prefix = ""
    #         for ch in line:
    #             if ch in (" ", "\t"):
    #                 prefix += ch
    #             else:
    #                 break

    #         visible = prefix.replace(" ", "·").replace("\t", "[TAB]")
    #         codes = [ord(c) for c in prefix]

    #         print(f"Line {i}")
    #         print("indent chars :", repr(prefix))
    #         print("visible      :", visible)
    #         print("ascii codes  :", codes)
    #         print("line content :", line)
    #         print("---------------------------")

    #     print("===== INDENT DEBUG END =====\n")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())