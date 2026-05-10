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

class AutoCompleteSystem(QFrame):

    def __init__(self, editor):

        super().__init__(editor, Qt.Popup)

        self.editor = editor

        # -----------------------------
        # load json database
        # -----------------------------
 

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "autocomplete_db.json")
        
        with open(db_path, "r", encoding="utf-8-sig") as f:
            self.db = json.load(f)


        self.aliases = self.db.get("aliases",{})
        self.modules = self.db.get("modules",{})
        self.builtins = self.db.get("builtins",{})

        # -----------------------------
        # build global command index
        # -----------------------------

        self.commands = {}
        self.command_names = []

        # builtins
        for name,data in self.builtins.items():

            self.commands[name] = data
            self.command_names.append(name)

        # modules
        for module,items in self.modules.items():

            for name,data in items.items():

                key = name

                if key not in self.commands:

                    self.commands[key] = data
                    self.command_names.append(key)

        # -----------------------------
        # popup list
        # -----------------------------

        self.list_widget = QListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.list_widget)

        self.setStyleSheet("""
        QFrame {
            background:#2b2b2b;
            border:1px solid #555;
            border-radius:5px;
        }

        QListWidget {
            background:#2b2b2b;
            color:white;
            border:none;
            padding:4px;
            font-size:12px;
        }

        QListWidget::item {
            padding:5px;
        }

        QListWidget::item:selected {
            background:#3d6dcc;
        }
        """)

        # -----------------------------
        # doc popup
        # -----------------------------

        self.doc_popup = QFrame(editor, Qt.Popup)

        doc_layout = QVBoxLayout(self.doc_popup)
        doc_layout.setContentsMargins(8,6,8,6)

        self.doc_label = QLabel()
        self.doc_label.setWordWrap(True)

        doc_layout.addWidget(self.doc_label)

        self.doc_popup.setStyleSheet("""
        QFrame {
            background:#2b2b2b;
            border:1px solid #555;
            border-radius:5px;
            color:white;
            font-size:12px;
        }
        """)

        # -----------------------------
        # signals
        # -----------------------------

        self.list_widget.itemClicked.connect(self.complete_selected)
        self.list_widget.currentItemChanged.connect(self.update_doc_popup)

        # -----------------------------
        # shortcut
        # -----------------------------

        self.shortcut = QShortcut(QKeySequence("Ctrl+Space"), self.editor)
        self.shortcut.activated.connect(self.show_completions)


    # ------------------------------------------------
    # prefix detection
    # ------------------------------------------------

    def get_current_prefix(self):

        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)

        return cursor.selectedText()


    # ------------------------------------------------
    # show suggestions
    # ------------------------------------------------

    def show_completions(self):

        prefix = self.get_current_prefix()

        if len(prefix) < 2:
            self.hide()
            self.doc_popup.hide()
            return

        suggestions = [
            cmd for cmd in self.command_names
            if cmd.startswith(prefix)
        ]

        if not suggestions:
            self.hide()
            self.doc_popup.hide()
            return

        self.list_widget.clear()

        for cmd in suggestions:
            QListWidgetItem(cmd, self.list_widget)

        self.list_widget.setCurrentRow(0)

        self.adjustSize()

        cursor_rect = self.editor.cursorRect()

        pos = self.editor.mapToGlobal(cursor_rect.bottomRight())

        self.move(pos + QPoint(0,6))

        self.show()

        self.list_widget.setFocus()

        self.update_doc_popup()


    # ------------------------------------------------
    # update documentation popup
    # ------------------------------------------------

    def update_doc_popup(self):

        item = self.list_widget.currentItem()

        if not item:
            self.doc_popup.hide()
            return

        name = item.text()

        data = self.commands.get(name,{})

        sig = data.get("signature","")
        doc = data.get("doc","")

        text = name

        if sig:
            text += sig

        if doc:
            text += "\n\n" + doc

        self.doc_label.setText(text)

        self.doc_popup.adjustSize()

        pos = self.mapToGlobal(QPoint(self.width()+6,0))

        self.doc_popup.move(pos)

        self.doc_popup.show()


    # ------------------------------------------------
    # insert completion
    # ------------------------------------------------

    def complete_selected(self, item):

        completion = item.text()

        cursor = self.editor.textCursor()

        cursor.select(QTextCursor.WordUnderCursor)

        cursor.insertText(completion)

        self.editor.setTextCursor(cursor)

        self.hide()
        self.doc_popup.hide()

        self.editor.setFocus()


    # ------------------------------------------------
    # keyboard navigation
    # ------------------------------------------------

    def keyPressEvent(self, event):

        key = event.key()

        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):

            item = self.list_widget.currentItem()

            if item:
                self.complete_selected(item)

            return

        elif key == Qt.Key_Escape:

            self.hide()
            self.doc_popup.hide()

            self.editor.setFocus()

            return

        super().keyPressEvent(event)


