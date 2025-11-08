from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem,
    QHeaderView, QDialog, QTextEdit, QPushButton, QLabel
)
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt
import reprlib
import json

class ObjectInspectorWindow(QWidget):
    
    """
    A floating window for inspecting Python objects in a structured, type-aware table.

    This class displays a table of user-defined or runtime-discovered Python objects,
    showing their name, type, memory size, and a summarized value. It supports
    interactive exploration of structured types (e.g., list, dict, set) and file-like
    objects via double-click, opening a detailed view of the full value.

    Features:
    ---------
    - Displays object metadata in a QTableWidget:
        - Object name
        - Type (with color-coded background)
        - Size in bytes
        - Summarized value
    - Supports full value inspection via double-click on the "Value" column
    - Automatically detects structured types and file-like objects
    - Handles JSON serialization and fallback to reprlib for complex objects
    - Integrates with IPython shell or external namespace extractors
    - Designed to be extensible for future type-specific viewers (e.g., tree view, dataframe preview)

    Attributes:
    -----------
    table : QTableWidget
        The main table displaying object metadata.
    data : List[Dict[str, Any]]
        Internal storage of full object metadata, including real values.
    known_dtypes : Set[str]
        Optional filter for allowed types, used during namespace extraction.

    Methods:
    --------
    add_objects(objects: List[Dict[str, Any]]) -> None
        Populates the table with a list of object metadata dictionaries.
        Each dictionary must contain 'name', 'type', 'size', and 'value'.

    show_full_value(item: QTableWidgetItem) -> None
        Opens a dialog showing the full value of the selected object.
        Supports structured types and file-like objects.

    is_structured_type(value: Any) -> bool
        Returns True if the value is a list, dict, set, tuple, or frozenset.

    summarize_value(value: Any, max_len: int = 80) -> str
        Returns a short string summary of the value for display in the table.

    inspect_all_user_attributes(shell: InteractiveShell) -> List[Dict[str, Any]]
        Extracts user-defined objects from an IPython shell, filtering out
        built-ins and system objects. Returns metadata suitable for add_objects.

    Notes:
    ------
    - This class is designed to be launched as a floating window from within
      the Uranus IDE or any PyQt-based environment.
    - Future enhancements may include:
        - Tree-based viewers for nested structures
        - Specialized viewers for NumPy arrays, Pandas DataFrames, etc.
        - Export and copy-to-clipboard functionality
    """
    
    def __init__(self, parent=None ,  file_name = ''):
        super().__init__(parent)
        self.setWindowTitle(file_name)
        self.data = []
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Obj Name", "Type", "Size (Byte)", "Value"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFont(QFont("Segoe UI", 10))
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f8f8;
                gridline-color: #cccccc;
            }
            QHeaderView::section {
                background-color: #d0d0d0;
                font-weight: bold;
                padding: 4px;
            }
        """)

        self.table.itemDoubleClicked.connect(self.show_full_value)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.show()

    def summarize_value(self, value, max_len=80):
        t = type(value)
        mod = t.__module__
        name = t.__name__

        # ساختارهای داده‌ای ساده
        if isinstance(value, (list, tuple, set, frozenset)):
            return f"{name}({len(value)} items)"
        if isinstance(value, dict):
            return f"{name}({len(value)} keys)"

        # NumPy
        if mod == "numpy":
            try:
                shape = getattr(value, "shape", None)
                return f"{name} shape={shape}" if shape else name
            except Exception:
                return name

        # Pandas
        if mod == "pandas.core.frame":
            return f"DataFrame shape={value.shape}"
        if mod == "pandas.core.series":
            return f"Series len={len(value)}"
        if mod == "pandas.core.indexes":
            return f"{name} len={len(value)}"
        if mod == "pandas":
            return f"{name}"

        # collections
        if mod == "collections":
            try:
                return f"{name} len={len(value)}"
            except Exception:
                return name

        # datetime
        if mod == "datetime":
            return str(value)

        # io, re, types, threading, asyncio
        if mod in {"io", "re", "types", "threading", "asyncio"}:
            return name

        # سایر موارد
        try:
            text = str(value)
            return text if len(text) <= max_len else text[:max_len] + " ..."
        except Exception:
            return "<unrepresentable>"

    def is_structured_type(self, value):
        return isinstance(value, (list, dict, set, tuple, frozenset))

    def add_objects(self, data):
        self.data = data
        self.table.setRowCount(len(data))
        self.table.clearContents()
       

        color_map = {
        # Built-in types
        "int": "#b71c1c", "float": "#e65100", "str": "#212121", "bool": "#6a1b9a",
        "list": "#1e88e5", "tuple": "#00897b", "dict": "#2e7d32", "set": "#5d4037",
        "NoneType": "#9e9e9e", "complex": "#ef6c00", "bytes": "#616161", "bytearray": "#616161",
        "frozenset": "#4e342e", "range": "#827717", "slice": "#827717", "ellipsis": "#757575",
        "type": "#283593", "NotImplementedType": "#757575",

        # Functions & methods
        "function": "#8e24aa", "builtin_function_or_method": "#8e24aa",
        "method": "#6a1b9a", "classmethod": "#6a1b9a", "staticmethod": "#6a1b9a",

        # Modules & classes
        "module": "#00695c", "object": "#424242", "code": "#c62828", "frame": "#c62828",

        # IO & file types
        "TextIOWrapper": "#3e2723", "BufferedWriter": "#3e2723", "BufferedReader": "#3e2723",
        "StringIO": "#4e342e", "BytesIO": "#4e342e",

        # NumPy
        "ndarray": "#3949ab", "int32": "#5c6bc0", "float64": "#5c6bc0", "complex128": "#5c6bc0",
        "bool_": "#5c6bc0", "str_": "#5c6bc0", "object_": "#5c6bc0",

        # Pandas
        "DataFrame": "#1b5e20", "Series": "#2e7d32", "Index": "#33691e", "MultiIndex": "#558b2f",
        "Categorical": "#689f38", "Timestamp": "#827717", "Timedelta": "#827717",
        "Period": "#827717", "Interval": "#827717",

        # Collections
        "Counter": "#6d4c41", "OrderedDict": "#6d4c41", "defaultdict": "#6d4c41",
        "deque": "#6d4c41", "ChainMap": "#6d4c41", "UserDict": "#6d4c41",
        "UserList": "#6d4c41", "UserString": "#6d4c41",

        # Pathlib
        "Path": "#455a64", "PosixPath": "#455a64", "WindowsPath": "#455a64",

        # Threading & async
        "Thread": "#00838f", "Future": "#00838f", "Task": "#00838f", "coroutine": "#00838f",

        # Weakref
        "ref": "#9e9e9e", "proxy": "#9e9e9e",

        # Other
        "SimpleNamespace": "#5e35b1", "MappingProxyType": "#5e35b1", "memoryview": "#9e9d24",
        "array": "#6a1b9a", "Queue": "#6a1b9a", "PriorityQueue": "#6a1b9a", "LifoQueue": "#6a1b9a"
    }

        for i, obj in enumerate(data):
            name_item = QTableWidgetItem(obj["name"])
            size_item = QTableWidgetItem(str(obj["size"]))
            value = obj["value"]
            type_name = obj["type"]
            color = QColor(color_map.get(type_name, "#9e9e9e"))

            type_item = QTableWidgetItem(type_name)
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            type_item.setBackground(QBrush(color))
            type_item.setForeground(QBrush(QColor("white")))

            value_item = QTableWidgetItem(self.summarize_value(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            if self.is_structured_type(value):
                value_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                value_item.setBackground(QBrush(color))
                value_item.setForeground(QBrush(QColor("white")))

            for item in [name_item, type_item, size_item, value_item]:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)


            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, type_item)
            self.table.setItem(i, 2, size_item)
            self.table.setItem(i, 3, value_item)
            

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        header_height = self.table.horizontalHeader().height()
        row_heights = sum(self.table.rowHeight(i) for i in range(self.table.rowCount()))
        col_widths = sum(self.table.columnWidth(i) for i in range(self.table.columnCount()))
        v_scroll = self.table.verticalScrollBar().sizeHint().width()
        h_scroll = self.table.horizontalScrollBar().sizeHint().height()

        width = min(col_widths + v_scroll + 40, 900)
        height = min(header_height + row_heights + h_scroll + 60, 600)
        self.resize(width, height)

    def show_full_value(self, item):
        row = item.row()
        col = item.column()
        if col != 3:
            return

        value = self.data[row]["value"]
        type_name = type(value).__name__

        def is_file_like(val):
            import io
            return isinstance(val, (io.TextIOBase, io.StringIO, io.BytesIO))

        # مقدار کامل
        if is_file_like(value):
            try:
                value.seek(0)
                full_text = value.read()
            except Exception:
                full_text = "<unable to read file content>"
        elif self.is_structured_type(value):
            try:
                full_text = json.dumps(value, indent=4, ensure_ascii=False)
            except Exception:
                full_text = reprlib.repr(value)
        else:
            full_text = reprlib.repr(value)

        # ساخت پنجره
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Full Value: {self.data[row]['name']}")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Type: {type_name}"))

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(full_text if isinstance(full_text, str) else str(full_text))
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()
        
        
        
# import sys
# from PyQt5.QtWidgets import QApplication
# from ObjectInspectorWindow import ObjectInspectorWindow  
# if __name__ == "__main__":
#     app = QApplication(sys.argv)


    sample_data = [
        {"name": "x", "type": "int", "size": 28, "value": 42},
        {"name": "pi", "type": "float", "size": 24, "value": 3.1415},
        {"name": "name", "type": "str", "size": 53, "value": "Attila"},
        {"name": "active", "type": "bool", "size": 24, "value": True},
        {"name": "items", "type": "list", "size": 88, "value": [1, 2, 3]},
        {"name": "config", "type": "dict", "size": 120, "value": {"debug": True}},
        {"name": "callback", "type": "function", "size": 64, "value": "<function run_cell>"},
        {"name": "data_set", "type": "set", "size": 72, "value": {1, 2, 3}},
        {"name": "nothing", "type": "NoneType", "size": 16, "value": None}
    ]


#     inspector = ObjectInspectorWindow()
#     inspector.add_objects(sample_data)


#     inspector.show()

#     sys.exit(app.exec_())