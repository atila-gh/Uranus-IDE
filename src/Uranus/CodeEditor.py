from math import ceil 
import  os , json
from PyQt5.QtGui import  QFont,QFontMetrics,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal,QEvent 
from PyQt5.QtWidgets import QPlainTextEdit,QApplication                     
from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QShortcut,
    QLabel
)

from PyQt5.QtGui import (
    QTextCursor,
    QKeySequence
)

from PyQt5.QtCore import Qt, QPoint

from Uranus.CodeHighlight import CodeHighlighter
from Uranus.SettingWindow import load_setting  
#from Uranus.AutoComplete import AutoCompleteSystem

# class AutoCompleteSystem(QFrame):

#     def __init__(self, editor):

#         super().__init__(editor, Qt.Popup)

#         self.editor = editor

#         # -----------------------------
#         # load json database
#         # -----------------------------
 

#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         db_path = os.path.join(base_dir, "autocomplete_db.json")
        
#         with open(db_path, "r", encoding="utf-8-sig") as f:
#             self.db = json.load(f)


#         self.aliases = self.db.get("aliases",{})
#         self.modules = self.db.get("modules",{})
#         self.builtins = self.db.get("builtins",{})

#         # -----------------------------
#         # build global command index
#         # -----------------------------

#         self.commands = {}
#         self.command_names = []

#         # builtins
#         for name,data in self.builtins.items():

#             self.commands[name] = data
#             self.command_names.append(name)

#         # modules
#         for module,items in self.modules.items():

#             for name,data in items.items():

#                 key = name

#                 if key not in self.commands:

#                     self.commands[key] = data
#                     self.command_names.append(key)

#         # -----------------------------
#         # popup list
#         # -----------------------------

#         self.list_widget = QListWidget()

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0,0,0,0)
#         layout.addWidget(self.list_widget)

#         self.setStyleSheet("""
#         QFrame {
#             background:#2b2b2b;
#             border:1px solid #555;
#             border-radius:5px;
#         }

#         QListWidget {
#             background:#2b2b2b;
#             color:white;
#             border:none;
#             padding:4px;
#             font-size:12px;
#         }

#         QListWidget::item {
#             padding:5px;
#         }

#         QListWidget::item:selected {
#             background:#3d6dcc;
#         }
#         """)

#         # -----------------------------
#         # doc popup
#         # -----------------------------

#         self.doc_popup = QFrame(editor, Qt.Popup)

#         doc_layout = QVBoxLayout(self.doc_popup)
#         doc_layout.setContentsMargins(8,6,8,6)

#         self.doc_label = QLabel()
#         self.doc_label.setWordWrap(True)

#         doc_layout.addWidget(self.doc_label)

#         self.doc_popup.setStyleSheet("""
#         QFrame {
#             background:#2b2b2b;
#             border:1px solid #555;
#             border-radius:5px;
#             color:white;
#             font-size:12px;
#         }
#         """)

#         # -----------------------------
#         # signals
#         # -----------------------------

#         self.list_widget.itemClicked.connect(self.complete_selected)
#         self.list_widget.currentItemChanged.connect(self.update_doc_popup)

#         # -----------------------------
#         # shortcut
#         # -----------------------------

#         self.shortcut = QShortcut(QKeySequence("Ctrl+Space"), self.editor)
#         self.shortcut.activated.connect(self.show_completions)


#     # ------------------------------------------------
#     # prefix detection
#     # ------------------------------------------------

#     def get_current_prefix(self):

#         cursor = self.editor.textCursor()
#         cursor.select(QTextCursor.WordUnderCursor)

#         return cursor.selectedText()


#     # ------------------------------------------------
#     # show suggestions
#     # ------------------------------------------------

#     def show_completions(self):

#         prefix = self.get_current_prefix()

#         if len(prefix) < 2:
#             self.hide()
#             self.doc_popup.hide()
#             return

#         suggestions = [
#             cmd for cmd in self.command_names
#             if cmd.startswith(prefix)
#         ]

#         if not suggestions:
#             self.hide()
#             self.doc_popup.hide()
#             return

#         self.list_widget.clear()

#         for cmd in suggestions:
#             QListWidgetItem(cmd, self.list_widget)

#         self.list_widget.setCurrentRow(0)

#         self.adjustSize()

#         cursor_rect = self.editor.cursorRect()

#         pos = self.editor.mapToGlobal(cursor_rect.bottomRight())

#         self.move(pos + QPoint(0,6))

#         self.show()

#         self.list_widget.setFocus()

#         self.update_doc_popup()


#     # ------------------------------------------------
#     # update documentation popup
#     # ------------------------------------------------

#     def update_doc_popup(self):

#         item = self.list_widget.currentItem()

#         if not item:
#             self.doc_popup.hide()
#             return

#         name = item.text()

#         data = self.commands.get(name,{})

#         sig = data.get("signature","")
#         doc = data.get("doc","")

#         text = name

#         if sig:
#             text += sig

#         if doc:
#             text += "\n\n" + doc

#         self.doc_label.setText(text)

#         self.doc_popup.adjustSize()

#         pos = self.mapToGlobal(QPoint(self.width()+6,0))

#         self.doc_popup.move(pos)

#         self.doc_popup.show()


#     # ------------------------------------------------
#     # insert completion
#     # ------------------------------------------------

#     def complete_selected(self, item):

#         completion = item.text()

#         cursor = self.editor.textCursor()

#         cursor.select(QTextCursor.WordUnderCursor)

#         cursor.insertText(completion)

#         self.editor.setTextCursor(cursor)

#         self.hide()
#         self.doc_popup.hide()

#         self.editor.setFocus()


#     # ------------------------------------------------
#     # keyboard navigation
#     # ------------------------------------------------

#     def keyPressEvent(self, event):

#         key = event.key()

#         if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):

#             item = self.list_widget.currentItem()

#             if item:
#                 self.complete_selected(item)

#             return

#         elif key == Qt.Key_Escape:

#             self.hide()
#             self.doc_popup.hide()

#             self.editor.setFocus()

#             return

#         super().keyPressEvent(event)



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
        # import os
        # print(os.listdir(os.path.dirname(__file__)))
        import importlib

        m = importlib.import_module("Uranus.AutoComplete")
        print(m)

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