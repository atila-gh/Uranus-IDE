 
import os ,base64  ,io ,builtins ,uuid , importlib , hashlib , sys,inspect , nbformat , sys
from nbformat.v4 import  new_output
from contextlib import redirect_stdout, redirect_stderr
from traitlets.config import Config
from IPython.core.interactiveshell import InteractiveShell

# Import Pyqt Feturse
from PyQt5.QtGui import  QIcon , QKeySequence , QTextCursor
from PyQt5.QtCore import  QSize ,QMetaObject, Qt, pyqtSlot, QObject ,QEventLoop 
from PyQt5.QtWidgets import (QToolBar, QToolButton, QColorDialog, QShortcut, QWidget , QFrame , QMainWindow
    , QVBoxLayout , QSpacerItem, QSizePolicy , QScrollArea,QDialog, QVBoxLayout, QLineEdit , QMdiSubWindow , QStatusBar
    , QPushButton , QLabel, QHBoxLayout , QFileDialog, QMessageBox , QCheckBox)

# Import Uranus Class
from Uranus.Cell import Cell
from Uranus.ObjectInspectorWindow import ObjectInspectorWindow
#from Uranus.AstDetection import RelationChartView


class FindReplaceDialog(QDialog):
    """
    Find/replace with preindexed matches. No overlapping search. Navigation and replacement
    operate on stored ranges to avoid rebuilding and infinite loops (e.g., prin -> print).
    """

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.matches = []         # list of (start, length)
        self.current_index = -1   # index into matches
        self.find_text = ""
        self.replace_text = ""

        layout = QVBoxLayout(self)
        self.status_label = QLabel("No matches")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        layout.addWidget(self.find_input)

        layout.addWidget(QLabel("Replace with:"))
        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_input)

        btn_layout = QHBoxLayout()
        btn_find_all = QPushButton("Find All")
        btn_find_next = QPushButton("Next")
        btn_find_prev = QPushButton("Prev")
        btn_replace = QPushButton("Replace")
        btn_replace_all = QPushButton("Replace All")

        btn_layout.addWidget(btn_find_all)
        btn_layout.addWidget(btn_find_prev)
        btn_layout.addWidget(btn_find_next)
        btn_layout.addWidget(btn_replace)
        btn_layout.addWidget(btn_replace_all)
        layout.addLayout(btn_layout)

        # connections
        btn_find_all.clicked.connect(self.find_all)
        btn_find_next.clicked.connect(self.goto_next)
        btn_find_prev.clicked.connect(self.goto_prev)
        btn_replace.clicked.connect(self.replace_one)
        btn_replace_all.clicked.connect(self.replace_all)

        # optional: rebuild when find text changes
        self.find_input.textChanged.connect(self.on_find_text_changed)

    def on_find_text_changed(self, _):
        # reset index so user must press Find All again
        self.matches.clear()
        self.current_index = -1
        self.status_label.setText("No matches")

    def find_all(self):
        self.find_text = self.find_input.text()
        if not self.find_text:
            self.matches.clear()
            self.current_index = -1
            self.status_label.setText("Empty find text")
            return

        self.matches = []
        doc = self.editor.document()
        cursor = QTextCursor(doc)
        cursor.setPosition(0)

        # non-overlapping search: advance from selectionEnd()
        while True:
            found = doc.find(self.find_text, cursor)
            if found.isNull():
                break
            start = found.selectionStart()
            length = found.selectionEnd() - start
            self.matches.append((start, length))
            cursor.setPosition(found.selectionEnd())

        if not self.matches:
            self.current_index = -1
            self.status_label.setText("No matches found")
            return

        self.current_index = 0
        self._select_match(self.current_index)
        self._update_status()

    def goto_next(self):
        if not self.matches:
            self.status_label.setText("No matches")
            return
        self.current_index = (self.current_index + 1) % len(self.matches)
        self._select_match(self.current_index)
        self._update_status()

    def goto_prev(self):
        if not self.matches:
            self.status_label.setText("No matches")
            return
        self.current_index = (self.current_index - 1) % len(self.matches)
        self._select_match(self.current_index)
        self._update_status()

    def replace_one(self):
        if not self.matches or self.current_index < 0:
            return
        self.replace_text = self.replace_input.text()
        start, length = self.matches[self.current_index]

        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.KeepAnchor)
        cursor.insertText(self.replace_text)

        # compute delta and update subsequent match positions
        delta = len(self.replace_text) - length
        self.matches[self.current_index] = (start, len(self.replace_text))

        for i in range(self.current_index + 1, len(self.matches)):
            s, l = self.matches[i]
            self.matches[i] = (s + delta, l)

        # move to next match (if any)
        if len(self.matches) > 1:
            self.current_index = (self.current_index + 1) % len(self.matches)
            self._select_match(self.current_index)
        self._update_status()

    def replace_all(self):
        if not self.matches:
            self.status_label.setText("No matches")
            return
        self.replace_text = self.replace_input.text()

        # replace from end to start to avoid shifting positions
        doc = self.editor.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()
        try:
            for start, length in reversed(self.matches):
                c = QTextCursor(doc)
                c.setPosition(start)
                c.setPosition(start + length, QTextCursor.KeepAnchor)
                c.insertText(self.replace_text)
        finally:
            cursor.endEditBlock()

        count = len(self.matches)
        self.matches.clear()
        self.current_index = -1
        self.status_label.setText(f"Replaced {count} matches")

    def _select_match(self, idx: int):
        start, length = self.matches[idx]
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()

    def _update_status(self):
        if self.matches and self.current_index >= 0:
            self.status_label.setText(f"Match {self.current_index + 1} of {len(self.matches)}")
        else:
            self.status_label.setText("No matches")
 

class InputWaiter(QObject): # for Covering Input
    """
       A blocking input handler that replaces Python's built-in input() with a GUI dialog.

       Purpose:
       - Enables synchronous input collection from users during code execution.
       - Used by IPythonKernel to intercept input() calls and show QInputDialog.

       Attributes:
       - _prompt (str): The input prompt text.
       - _value (str): The value entered by the user.
       - _dialog_parent (QWidget): Parent widget for the input dialog.

       Usage:
       Called via wait_for_input(prompt), which blocks until user input is received.
       """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prompt = ""
        self._value = ""
        self._dialog_parent = parent  # معمولاً self از MainWindow

    def wait_for_input(self, prompt = None):
        self._prompt = prompt
        QMetaObject.invokeMethod(self, "_show_dialog", Qt.BlockingQueuedConnection)
        return self._value

    @pyqtSlot()
    def _show_dialog(self):
        from PyQt5.QtWidgets import QInputDialog

        dlg = QInputDialog(self._dialog_parent)
        dlg.setWindowTitle("Input")
        dlg.setLabelText(self._prompt)

        # حذف علامت ؟ از بالای پنجره
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        if dlg.exec_() == QInputDialog.Accepted:
            self._value = dlg.textValue()
        else:
            self._value = ""


class StreamCatcher(io.StringIO): # 2025-10-11 - edited
    """
       A stream interceptor that captures stdout/stderr line-by-line and emits structured output.

       Purpose:
       - Used during code execution to redirect and format console output.
       - Converts each line into a Jupyter-compatible nbformat output object.

       Parameters:
       - name (str): Stream name ("stdout" or "stderr").
       - callback (function): Function to receive each parsed output line.

       Behavior:
       - Buffers incoming text until newline.
       - Emits each complete line via callback as nbformat stream output.
       """

    def __init__(self, name, callback):
        super().__init__()
        self._name = name
        self.callback = callback
        self._buffer = ""

    def write(self, text):
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                out = new_output("stream", name=self._name, text=line)
                self.callback(out)


class IPythonKernel:
    """
       A lightweight wrapper around IPython's InteractiveShell for executing notebook cells.

       Responsibilities:
       - Executes code cells and captures stdout, stderr, and display outputs.
       - Handles input() via InputWaiter.
       - Converts matplotlib and image outputs to base64 PNG for inline display.
       - Maps Python objects to appropriate output editors (e.g., table, image, text).

       Attributes:
       - shell (InteractiveShell): IPython shell instance.
       - input_waiter (InputWaiter): Handles blocking input dialogs.
       - object_store (dict): Stores references to large objects for later inspection.

       Methods:
       - run_cell(code, callback): Executes code and emits outputs via callback.
       - __uranus_inspect_variables(): Returns a DataFrame of global variables (optional).
       """

    def __init__(self):
        # self.shell = InteractiveShell.instance()
        # self.input_waiter = InputWaiter()
        # self.object_store = {}
        
        
        cfg = Config()
        cfg.InteractiveShellEmbed = Config()
        cfg.InteractiveShellEmbed.user_ns = {}


        self.shell = InteractiveShell(config=cfg)
        self.input_waiter = InputWaiter()
        self.object_store = {}


       

    def run_cell(self, code: str, callback):

        builtins.input = self.input_waiter.wait_for_input

        # 🔧 تزریق backend امن و جایگزینی plt.show() با ذخیره‌سازی فایل
        if ("matplotlib" in code or "plt." in code) and importlib.util.find_spec("matplotlib") is not None:
            injected = "import matplotlib; matplotlib.use('Agg')\n"
            code = injected + code.replace("plt.show()", "plt.savefig('plot.png')")

        outputs = []
        stdout_catcher = StreamCatcher("stdout", callback)
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_catcher), redirect_stderr(stderr_buffer):
            result = self.shell.run_cell(code)
       
        
       


        obj = result.result
        stderr_text = stderr_buffer.getvalue().strip()
        
        

        # 🖼️ image
        if os.path.exists("plot.png"):
            try:
                with open("plot.png", "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                out = new_output("display_data", data={"image/png": encoded},
                                 metadata={"object_type": "Figure", "editor": "output_image"})
                outputs.append(out)
                callback(out)
            except Exception:
                pass
            finally:
                try :
                     os.remove("plot.png")
                except Exception:
                    pass

        # 🔥 error
        if stderr_text:
            tb_lines = stderr_text.splitlines()
            out = new_output(
                "error",
                ename="Exception",
                evalue=tb_lines[-1] if tb_lines else "",
                traceback=tb_lines,
            )
            outputs.append(out)
            callback(out)

        # ⛔ if None or error stop
        if obj is None or (isinstance(obj, str) and stderr_text):
            return outputs

        # ✅ نگاشت نوع به ادیتور — فقط مواردی که ژوپیتر هم نمایش می‌دهد
        obj_type = type(obj).__name__
        obj_module = obj.__class__.__module__
        full_type = f"{obj_module}.{obj_type}" if obj_module != "builtins" else obj_type

        EDITOR_MAP = {
            "pandas.core.frame.DataFrame": "output_data",
            "matplotlib.figure.Figure": "output_image",
            "PIL.Image.Image": "output_image",
            "plotly.graph_objs._figure.Figure": "output_image",
            "str": "output_editor",
            "Exception": "output_editor"
        }

        editor = EDITOR_MAP.get(full_type)

        # 📊 table
        if editor == "output_data":
            obj_id = f"obj_{uuid.uuid4().hex}"
            self.object_store[obj_id] = obj
            html = obj.to_html(index=False)
            out = new_output(
                "display_data",
                data={"text/html": html},
                metadata={"object_type": obj_type, "editor": editor, "object_ref": obj_id}
            )
            outputs.append(out)
            callback(out)

        # 🖼️ image
        elif editor == "output_image":
            buf = io.BytesIO()
            try:
                if hasattr(obj, "savefig"):
                    obj.savefig(buf, format="png")
                    if hasattr(obj, "close"):
                        obj.close()
                elif hasattr(obj, "save"):
                    obj.save(buf, format="PNG")
                else:
                    return outputs
                buf.seek(0)
                encoded = base64.b64encode(buf.read()).decode("utf-8")
                buf.close()
                out = new_output(
                    "display_data",
                    data={"image/png": encoded},
                    metadata={"object_type": obj_type, "editor": editor}
                )
                outputs.append(out)
                callback(out)
            except Exception:
                return outputs
            
            
        
        return outputs
    
    
    def inspect_all_user_attributes(self, shell):
        user_ns = shell.user_ns
        results = []

        def extract_known_dtypes(user_ns):
            types_set = set()
            for name, obj in user_ns.items():
                if name.startswith("_"):
                    continue
                try:
                    t = type(obj)
                    mod = t.__module__
                    name = t.__name__
                    full = f"{mod}.{name}" if mod not in ("builtins", None) else name
                    types_set.add(full)
                except Exception:
                    continue
            return sorted(types_set)

        def safe_size(obj):
            try:
                return sys.getsizeof(obj)
            except Exception:
                return 0

        def full_type_name(obj):
            try:
                t = type(obj)
                mod = t.__module__
                name = t.__name__
                return f"{mod}.{name}" if mod not in ("builtins", None) else name
            except ReferenceError:
                return "ReferenceError"

        def is_supported(obj):
            try:
                return full_type_name(obj) in allowed_types
            except ReferenceError:
                return False

        allowed_types = set(extract_known_dtypes(user_ns))

        for name, obj in user_ns.items():
            if name.startswith("_"):
                continue
            if name in {"In", "Out", "get_ipython", "exit", "quit", "__builtins__", "open"}:
                continue
            if not is_supported(obj):
                continue

            results.append({
                "name": name,
                "type": type(obj).__name__,
                "size": safe_size(obj),
                "value": obj  # ✅ مقدار واقعی حفظ شود
            })

            try:
                # User-defined class
                if inspect.isclass(obj) and getattr(obj, "__module__", None) == "__main__":
                    for attr_name, attr_value in vars(obj).items():
                        if attr_name.startswith("_"):
                            continue
                        if not is_supported(attr_value):
                            continue
                        results.append({
                            "name": f"{name}.{attr_name}",
                            "type": type(attr_value).__name__,
                            "size": safe_size(attr_value),
                            "value": attr_value
                        })

                # Instance of user-defined class
                elif hasattr(obj, "__class__") and getattr(obj.__class__, "__module__", None) == "__main__":
                    for attr_name, attr_value in vars(obj).items():
                        if attr_name.startswith("_"):
                            continue
                        if not is_supported(attr_value):
                            continue
                        results.append({
                            "name": f"{name}.{attr_name}",
                            "type": type(attr_value).__name__,
                            "size": safe_size(attr_value),
                            "value": attr_value
                        })
            except ReferenceError:
                pass

        return results
            
    
    
class WorkWindow(QFrame):
    """
       The main notebook interface for Uranus IDE.

       Responsibilities:
       - Hosts and manages multiple Cell instances (code/markdown).
       - Provides toolbars for cell manipulation, execution, and styling.
       - Integrates with IPythonKernel for backend execution.
       - Supports undo stack for deleted cells and find/replace dialog.

       Attributes:
       - cell_widgets (list): List of all Cell instances in the notebook.
       - focused_cell (Cell): Currently focused cell.
       - file_path (str): Path to the associated .ipynb file.
       - content (NotebookNode): Parsed nbformat content (optional).
       - ipython_kernel (IPythonKernel): Execution backend.
       - deleted_cells_stack (list): Stack for undoing deleted cells.
       - outputs (list): List of outputs emitted during execution.

       Methods:
       - add_cell(): Adds a new cell to the notebook.
       - run_focused_cell(): Executes the currently focused cell.
       - ipynb_format_save_file(): Saves notebook content to disk.
       - load_file(): Loads notebook content from nbformat.
       - undo_delete_cell(): Restores the last deleted cell.
       - move_cell_up/down(): Reorders cells.
       - choose_border_color(): Opens color dialog for cell styling.
       - find_replace(): Opens find/replace dialog.
       """

    focused_cell = None

    def __init__(self, nb_content=None, file_path=None , status_l = None 
                 , status_c = None , status_r = None  , mdi_area = None):
        self.debug = False
        if self.debug: print('[WorkWindow]->[__init__]')

        super().__init__()

        self.ipython_kernel = IPythonKernel()
        self.ipython_kernel.input_waiter = InputWaiter(self) # for cover input with dialog        
        self.file_path = file_path        
        self.nb_content = nb_content
        self.mdi_area = mdi_area # Midwindow Mainwindow Original Window Container        
        self.status_l = status_l
        self.status_c = status_c
        self.status_r = status_r
        
        self.cell_widgets = []
        self.outputs = []
        self.original_sources = []
        self.deleted_cells_stack = []
        
        self.execution_in_progress = False        
        
        self.detached = False
        self.detached_window = None
        self.fake_close = False
       
       
        # path of temp.chk file 
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_path = os.path.join(base_dir, 'temp.chk')
        
        # Set window title from file name
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.name_only = os.path.splitext(filename)[0]
            self.setWindowTitle(self.name_only)


        # --------------------------- GRAPHIC -----------------------------
        
        # Define New QFrame
        
        
       
        self.setFrameShape(QFrame.StyledPanel)   # خط دور فریم
        self.setFrameShadow(QFrame.Raised)       # حالت برجسته
        self.setLineWidth(2)                      # ضخامت خط دور فریم


    
        
        
        # Set minimum window size
        self.setMinimumSize(620, 600)

        # --- Top Horizontal Toolbar ---
        self.top_toolbar = QToolBar()
        self.top_toolbar.setOrientation(Qt.Horizontal)
        self.top_toolbar.setIconSize(QSize(24, 24))
        self.setup_top_toolbar_buttons()

        # --- Layout for top toolbar with left spacing ---
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(0)
        top_bar_layout.addSpacing(64)  # فاصله افقی از سمت چپ
        top_bar_layout.addWidget(self.top_toolbar)

        # --- Vertical Toolbar ---
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setIconSize(QSize(24, 24))
        self.setup_toolbar_buttons()

        # --- Scrollable Area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.cell_container = QWidget()
        self.cell_layout = QVBoxLayout(self.cell_container)
        self.cell_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.cell_container)

        # --- Horizontal Layout: toolbar + scroll area ---
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(0)
        horizontal_layout.addWidget(self.toolbar)
        horizontal_layout.addWidget(self.scroll_area)

        # --- Final Layout: top toolbar + horizontal layout ---
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.setSpacing(0)
        final_layout.addLayout(top_bar_layout)
        final_layout.addLayout(horizontal_layout)


        # --- Load initial content ---
        self.load_file(self.nb_content)

        # fpr scrolling window more than half of page
        extra_scroll_space = QSpacerItem(20, 400, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.cell_layout.addItem(extra_scroll_space)

    def setup_top_toolbar_buttons(self):
        if self.debug: print('[WorkWindow->setup_top_toolbar_buttons]')

        # Save ipynb File
        btn_save = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "save.png")
        btn_save.setIcon(QIcon(icon_path))
        btn_save.setToolTip("""
                            <b>Save File</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>Ctrl+S</kbd></span><br>
                            Save the current File in Specific Location.
                            """)


        btn_save.clicked.connect(self.ipynb_format_save_file)
        self.top_toolbar.addWidget(btn_save)
        self.top_toolbar.addSeparator()  # فاصله یا خط نازک بین دکمه‌ها
       

        # Move Cell Up
        btn_move_up = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "move_up.png")  # آیکون دلخواه
        btn_move_up.setIcon(QIcon(icon_path))
        btn_move_up.setToolTip("""
                            <b>Move Cell Up</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F7</kbd></span><br>
                            Move Focused Cell Up.
                            """)
        btn_move_up.clicked.connect(self.move_cell_up)
        self.top_toolbar.addWidget(btn_move_up)
        # Define ShortCut F7
        shortcut_move_up = QShortcut(QKeySequence("F7"), self)
        shortcut_move_up.setContext(Qt.ApplicationShortcut)
        shortcut_move_up.activated.connect(self.move_cell_up)

        self.top_toolbar.addSeparator()

        # Move Sell Bottom
        btn_move_down = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "move_down.png")  
        btn_move_down.setIcon(QIcon(icon_path))
        btn_move_down.setToolTip("""
                            <b>Move Cell Down</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F8</kbd></span><br>
                            Move Focused Cell Down.
                            """)
        btn_move_down.clicked.connect(self.move_cell_down)
        self.top_toolbar.addWidget(btn_move_down)
        

        # Define ShortCut F4
        shortcut_move_down = QShortcut(QKeySequence("F8"), self)
        shortcut_move_down.setContext(Qt.ApplicationShortcut)
        shortcut_move_down.activated.connect(self.move_cell_down)

        self.top_toolbar.addSeparator()  

        # Choose title color
        btn_color = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "color.png")
        btn_color.setIcon(QIcon(icon_path))
        btn_color.setToolTip("""
                            <b>Choose Color</b><br>
                            Can Change Border Color .
                            """)
        btn_color.clicked.connect(self.choose_border_color)
        self.top_toolbar.addWidget(btn_color)
        self.top_toolbar.addSeparator()  


        # Button Run All
        self.btn_run_all = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "run_all.png")
        self.btn_run_all.setIcon(QIcon(icon_path))        
        self.btn_run_all.setToolTip("""
                            <b>Choose Run All Code</b><br>
                            Executes the All Code cell and displays the outputs
                            """)
        self.btn_run_all.clicked.connect(self.run_all_cells)
        self.top_toolbar.addWidget(self.btn_run_all)
        self.top_toolbar.addSeparator()


        # Undo Cell Button
        btn_undo = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "undo_cell.png")
        btn_undo.setIcon(QIcon(icon_path))
        btn_undo.setToolTip("""
                            <b>Undo Delete</b><br>
                            Restore the last deleted cell.
                            """)
        btn_undo.clicked.connect(self.undo_delete_cell)
        self.top_toolbar.addWidget(btn_undo)
        self.top_toolbar.addSeparator()
        
       
        # Memory Variable List
        memory = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "memory.png")
        memory.setIcon(QIcon(icon_path))
        memory.setToolTip("""
                                   <b>Objects List</b><br>
                                   <span style='color:gray;'>Shortcut: <kbd>F9</kbd></span><br>
                                   Object And Variable List
                                   """)
        memory.clicked.connect(self.variable_table)
        self.top_toolbar.addWidget(memory)
        self.top_toolbar.addSeparator()
        
        # print cell
        print_cell = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "print.png")
        print_cell.setIcon(QIcon(icon_path))
        print_cell.setToolTip("""
                                   <b>Print</b><br>
                                   
                                   Print Focused Cell 
                                   """)
        print_cell.clicked.connect(self.print_cell)
        self.top_toolbar.addWidget(print_cell)
        self.top_toolbar.addSeparator()
        
        # Drawing  Graph
        graph = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "graph.png")
        graph.setIcon(QIcon(icon_path))
        graph.setToolTip("""
                                   <b>Graph</b><br>                                   
                                   Drawing Graph For Run cell Focused Cell 
                                   """)
        graph.clicked.connect(self.graph)
        self.top_toolbar.addWidget(graph)
        self.top_toolbar.addSeparator()
        
        
        # IPYTON TO PY  
        ippy = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "iptopy.png")
        ippy.setIcon(QIcon(icon_path))
        ippy.setToolTip("""
                                   <b>IPYTON TO PYTHON</b><br>                                   
                                   CONVERT IPYNB TO PY 
                                   """)
        ippy.clicked.connect(self.iptopy)
        self.top_toolbar.addWidget(ippy)
      
        
        # Detach Check Button 
        icon_path = os.path.join(os.path.dirname(__file__), "image", "detach.png")
        self.chk_detach = QCheckBox()
        self.chk_detach.setToolTip("Toggle floating mode")
        self.chk_detach.setIcon(QIcon(icon_path))  # یا مسیر مستقیم فایل
        self.chk_detach.setToolTip("""
                            <b>Detach Window</b><br>                            
                            "Detach editor into a floating window." 
                            """)
        self.chk_detach.clicked.connect(self.toggle_detach_mode)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.top_toolbar.addWidget(spacer)         # این فاصله‌دهنده همه‌چیز رو به چپ می‌چسبونه
        self.top_toolbar.addWidget(self.chk_detach)  # این می‌ره سمت راست

    def setup_toolbar_buttons(self):
        if self.debug :print('[WorkWindow->setup_toolbar_buttons]')


        # Add cell above
        btn_up = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "up.png")
        btn_up.setIcon(QIcon(icon_path))
        btn_up.setToolTip("""
                            <b>Add Cell Above</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F2</kbd></span>
                            """)
        btn_up.clicked.connect(self.add_cell_above)
        self.toolbar.addWidget(btn_up)

        # Define ShortCut F2
        shortcut_add_cell_above = QShortcut(QKeySequence("F2"), self)
        shortcut_add_cell_above.setContext(Qt.ApplicationShortcut)
        shortcut_add_cell_above.activated.connect(self.add_cell_above)

        # Add cell below
        btn_down = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "down.png")
        btn_down.setIcon(QIcon(icon_path))
        btn_down.setToolTip("""
                            <b>Add Cell Below</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F3</kbd></span>
                            """)
        btn_down.clicked.connect(self.add_cell_below)
        self.toolbar.addWidget(btn_down)

        # Define ShortCut F3
        shortcut_add_cell_below = QShortcut(QKeySequence("F3"), self)
        shortcut_add_cell_below.setContext(Qt.ApplicationShortcut)
        shortcut_add_cell_below.activated.connect(self.add_cell_below)


        # Delete active cell
        btn_delete = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "delete_page.png")
        btn_delete.setIcon(QIcon(icon_path))
        btn_delete.setToolTip("Delete active cell")
        btn_delete.clicked.connect(self.delete_active_cell)
        self.toolbar.addWidget(btn_delete)


        # Run Button
        self.run_btn = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "run_cell.png")
        self.run_btn.setIcon(QIcon(icon_path))
        self.run_btn.setToolTip("Run Cell")
        self.run_btn.clicked.connect(self.run_focused_cell)
        self.toolbar.addWidget(self.run_btn)
        # define shortcut for run code F5
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.setContext(Qt.ApplicationShortcut)
        shortcut.activated.connect(self.run_focused_cell)
        self.run_btn.setToolTip("""
                                <b>Run Cell</b><br>
                                <span style='color:gray;'>Shortcut: <kbd>F5</kbd></span><br>
                                Executes the current cell and displays the output.
                                """)

    def add_cell(self, editor_type=None, nb_cell=None,
             src_content=None, border_color=None,
             origin="uranus", outputs=None, height=0):
        
        cell = Cell(
            editor_type=editor_type,
            src_content=src_content,
            border_color=border_color,
            kernel=self.ipython_kernel,
            notify_done=self.execution_done,
            origin=origin,
            outputs=outputs,
            status_c=self.status_c,
            status_r=self.status_r,
            height=height,
            nb_cell=nb_cell
        )



        # Mouse Event Handler
        cell.clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_editor_clicked.connect(lambda c=cell: self.set_focus(c))

        self.cell_widgets.append(cell)  # cell append to list of cells
        self.cell_layout.addWidget(cell)  # for showing cell add cell to layout
        self.set_focus(cell)  # set cell focused

        return cell
          
    def set_focus(self, cell):
        if self.debug:print('[WorkWindow->set_focus]')

        # UnFocus Last Cell
        if self.focused_cell and cell is not self.focused_cell and len(self.cell_widgets) > 1 :
            self.focused_cell.border_color = self.focused_cell.border_color or self.focused_cell.bg_border_color_default
            self.focused_cell.setStyleSheet(f"""
                           QFrame {{
                               border: 2px solid {self.focused_cell.border_color};
                               border-radius: 5px;
                               background-color: {self.focused_cell.bg_main_window};
                               padding: 6px;
                           }}""")     
            
            
            if hasattr(self.focused_cell, 'output_data'):
                self.focused_cell.output_data.setStyleSheet("border: 1px solid black; padding: 0px;")
                if hasattr(self.focused_cell.output_data,'table'):
                    self.focused_cell.output_data.table.setStyleSheet("border: 1px solid gray; padding: 0px;")
                    self.focused_cell.output_data.table.horizontalHeader().setStyleSheet("border: 0px solid gray; padding: 0px;")
                
        
        # Focus Current Cell  
        self.focused_cell = cell       
        
        cell.border_color = cell.border_color or cell.bg_border_color_default
        cell.setStyleSheet(f"""
               QFrame {{
                   border: 5px solid {cell.border_color};
                   border-radius: 5px;
                   background-color: {cell.bg_main_window};
                   padding: 6px;
               }}""")
        
        if hasattr(cell, 'output_data'):
            cell.output_data.setStyleSheet("border: 1px solid black; padding: 0px;")
            if hasattr(cell.output_data,'table'):
                cell.output_data.table.setStyleSheet("border: 1px solid gray; padding: 0px;")
                cell.output_data.table.horizontalHeader().setStyleSheet("border: 0px solid gray; padding: 0px;")

    def run_focused_cell(self):
        if not self.focused_cell:
            return

       
        # 🔒 غیرفعال کردن دکمه‌ها
        self.status_c("")
        self.status_l(self.file_path)
        
        self.run_btn.setEnabled(False)
        self.btn_run_all.setEnabled(False)

        # اتصال پایان اجرا به فعال‌سازی دکمه‌ها
        def on_done():
            print("[run_focused_cell] execution finished")
            self.run_btn.setEnabled(True)
            self.btn_run_all.setEnabled(True)
            self.variable_table(True)

        self.focused_cell.notify_done = on_done
        self.focused_cell.run()

    def execution_done(self):
        self.execution_in_progress = False
        self.set_focus(self.focused_cell)

    # Connected to a Button 1
    def add_cell_above(self):
        """
        Inserts a new cell above the currently active cell.
        """
        if self.debug:
            print('[WorkWindow->add_cell_above]')

        if not self.cell_widgets:
            return

        elif self.focused_cell:
            index = self.cell_widgets.index(self.focused_cell)
            cell = Cell(
                kernel=self.ipython_kernel,
                notify_done=self.execution_done,
                origin="uranus"  ,
                status_c = self.status_c ,
                status_r = self.status_r
                
                
            )

            cell.clicked.connect(lambda c=cell: self.set_focus(c))
            cell.doc_editor_clicked.connect(lambda c=cell: self.set_focus(c))
            cell.doc_editor_editor_clicked.connect(lambda c=cell: self.set_focus(c))

            self.cell_widgets.insert(index, cell)
            self.cell_layout.insertWidget(index, cell)
            self.set_focus(cell)

    # Connected to a Button 2
    def add_cell_below(self):
        """
        Inserts a new cell below the currently active cell.
        """
        if self.debug:
            print('[WorkWindow->add_cell_below]')

        if not self.cell_widgets:
           return

        elif self.focused_cell:
            index = self.cell_widgets.index(self.focused_cell)
            cell = Cell(
                kernel=self.ipython_kernel,
                notify_done=self.execution_done,
                origin="uranus" ,
                status_c = self.status_c ,
                status_r = self.status_r
            )

            cell.clicked.connect(lambda c=cell: self.set_focus(c))
            cell.doc_editor_clicked.connect(lambda c=cell: self.set_focus(c))
            cell.doc_editor_editor_clicked.connect(lambda c=cell: self.set_focus(c))

            self.cell_widgets.insert(index + 1, cell)
            self.cell_layout.insertWidget(index + 1, cell)
            self.set_focus(cell)

    # Connected to a Button 3
    def delete_active_cell(self):
        """
        Deletes the currently active cell from the notebook and stores it for multistep undo.
        """
        content = None
        if self.debug:
            print('[WorkWindow->delete_active_cell]')

        if  len(self.cell_widgets) <=1 :
            self.status_l('You can`t delete the last cell — at least one cell is required. Create a new one first, then you can delete this one.')
            return
        
        if self.focused_cell and self.cell_widgets :
            index = self.cell_widgets.index(self.focused_cell)

            # استخراج محتوا بسته به نوع سلول
            if self.focused_cell.editor_type == 'code':
                content = self.focused_cell.editor.toPlainText()
            elif self.focused_cell.editor_type == 'markdown':
                content = self.focused_cell.d_editor.editor.toHtml()

            # ذخیره اطلاعات در پشته
            if self.focused_cell.editor_type in ('code', 'markdown'):
                self.deleted_cells_stack.append({
                    "index": index,
                    "cell_type": self.focused_cell.editor_type,
                    "source": content,
                    "color": self.focused_cell.border_color,
                    "origin": self.focused_cell.origin , # ← فقط این خط اضافه شده
                    "nb_cell" : self.focused_cell.nb_cell
                    
                })

            # حذف سلول از رابط کاربری و لیست
            self.cell_layout.removeWidget(self.focused_cell)
            self.focused_cell.deleteLater()
            self.cell_widgets.remove(self.focused_cell)

            # فعال‌سازی سلول قبلی
            if self.cell_widgets:
                new_index = max(0, index - 1)
                self.set_focus(self.cell_widgets[new_index])

    # Connected to a Button 4
    def choose_border_color(self):
        """
        Opens a color dialog to change the title color of the active cell.
        """
        if self.debug :print('[WorkWindow->choose_border_color]')
        if self.focused_cell:
            color = QColorDialog.getColor()   # دیالوک انتخاب رنگ را باز میکند
            if color.isValid():          # چک میکند که رنگ انتخابی معتبر میباشد
                self.focused_cell.set_color(color.name()) # رنگ سلول جاری را تغییر میدهد

    # called by ipynb_format_save_file
    # this method convert image file to string with base64 for puts instead of image path im html file
    def image_to_base64(self,image_path):
        """
        Converts an image file to a base64 encoded string.
        """
        if self.debug :print('[WorkWindow->image_to_base64]')
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
        except FileNotFoundError:
            print(f"Error: The image file at {image_path} was not found.")
        except Exception as e:
            print(f"Error while converting image {image_path}: {e}")
        return None

    # Connected to Save File Button
    # gather all cell_widgets contents and build an ipynb file (SAVE FILE)
    def ipynb_format_save_file(self , temp = False):
        """
        Converts all cells into nbformat-compatible structure and saves to disk.
        """
        if self.debug:
            print('[WorkWindow->ipynb_format_save_file]')
            
            
        cells = []
        for cell in self.cell_widgets:
            if cell.editor_type == "code":
                cells.append(cell.get_nb_code_cell())
                self.original_sources.append(cell.editor.toPlainText().strip())
            elif cell.editor_type == "markdown":
                cells.append(cell.get_nb_markdown_cell())
                self.original_sources.append(cell.d_editor.editor.toHtml().strip())
        nb = nbformat.v4.new_notebook()        
        nb["cells"] = cells
        
        file_path = self.temp_path if temp else self.file_path

        if file_path:
            
            with open(file_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
            
         
            if not temp :
                print(f'[FILE {file_path} SAVED]')
                self.status_l('Saved To : '+self.file_path)
            
  
    def load_file(self, content):
        if self.debug:
            print('[WorkWindow->load_file]')

        if not content or not isinstance(content.cells, list):
            self.add_cell(origin='uranus')
            return

        #self.content = content
        self.cell_widgets.clear()

        # WorkWindow.load_file
        for cell_data in content.cells:
            editor_type = "code" if cell_data.cell_type == "code" else "markdown"
            source = cell_data.source
            metadata = cell_data.get("metadata", {})
            border_color = metadata.get("bg")

            if "uranus" not in metadata:
                metadata["uranus"] = {}
            if "origin" not in metadata["uranus"]:
                metadata["uranus"]["origin"] = "jupyter"

            origin = metadata["uranus"]["origin"]
            height = metadata.get('height', 0)

            outputs = None
            if editor_type == "code" and hasattr(cell_data, "outputs"):
                outputs = [
                    out for out in cell_data.outputs
                    if out.output_type in ("stream", "error") or (
                        out.output_type == "display_data" and out.metadata.get("editor") == "output_image"
                    )
                ]

            self.add_cell(
                editor_type=editor_type,
                src_content=source,
                border_color=border_color,
                origin=origin,
                outputs=outputs,
                height=height,
                nb_cell=cell_data  # ← پاس دادن سلول
            )

        # تمرکز روی آخرین سلول
        if self.cell_widgets:
            self.set_focus(self.cell_widgets[-1])

        # فضای اضافه برای اسکرول
        self.cell_layout.addItem(QSpacerItem(20, 400, QSizePolicy.Minimum, QSizePolicy.Fixed))


    def move_cell_up(self):
        if self.debug: print('[WorkWindow->move_cell_up]')
        if self.focused_cell and self.cell_widgets:
            index = self.cell_widgets.index(self.focused_cell)
            if index > 0:
                # جابجایی در لیست
                self.cell_widgets[index], self.cell_widgets[index - 1] = self.cell_widgets[index - 1], \
                    self.cell_widgets[index]
                # جابجایی در layout
                self.cell_layout.removeWidget(self.focused_cell)
                self.cell_layout.insertWidget(index - 1, self.focused_cell)
                self.set_focus(self.focused_cell)

    def undo_delete_cell(self):
        """
        Restores the last deleted cell.
        """
        if self.debug:
            print('[WorkWindow->undo_delete_cell]')

        if not self.deleted_cells_stack:
            return

        cell_info = self.deleted_cells_stack.pop()
        index = cell_info["index"]
        cell_type = cell_info["cell_type"]
        source = cell_info["source"]
        color = cell_info["color"]
        origin = cell_info['origin']
        nb_cell = cell_info['nb_cell']

        cell = Cell(
            editor_type=cell_type,
            src_content=source,
            border_color=color,
            kernel=self.ipython_kernel,
            notify_done=self.execution_done,
            origin = origin  ,
            status_c = self.status_c ,
            status_r = self.status_r,
            nb_cell = nb_cell
            
        )

        cell.clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_editor_clicked.connect(lambda c=cell: self.set_focus(c))

        self.cell_widgets.insert(index, cell)
        self.cell_layout.insertWidget(index, cell)
        self.set_focus(cell)

    def move_cell_down(self):
        """
        Moves the currently focused cell one position down in the notebook.
        """
        if self.debug: print('[WorkWindow->move_cell_down]')
        if self.focused_cell and self.cell_widgets:
            index = self.cell_widgets.index(self.focused_cell)
            if index < len(self.cell_widgets) - 1:
                # جابجایی در لیست داده‌ای
                self.cell_widgets[index], self.cell_widgets[index + 1] = self.cell_widgets[index + 1], \
                self.cell_widgets[index]
                # حذف و درج مجدد در لایه گرافیکی
                self.cell_layout.removeWidget(self.focused_cell)
                self.cell_layout.insertWidget(index + 1, self.focused_cell)
                self.set_focus(self.focused_cell)

    def run_all_cells(self):
        print('[WorkWindow->run_all_cells]')

        # 🔒 غیرفعال کردن دکمه‌ها
        self.run_btn.setEnabled(False)
        self.btn_run_all.setEnabled(False)

        for cell in self.cell_widgets:
            if cell.editor_type == "code":
                self.set_focus(cell)
                self.run_cell_blocking(cell)

        # ✅ فعال کردن دکمه‌ها بعد از پایان کامل
        self.run_btn.setEnabled(True)
        self.btn_run_all.setEnabled(True)

    def find_replace(self):       
        
        
        if self.focused_cell :
            if hasattr(self.focused_cell, "editor"): # for Code Editor
                editor = self.focused_cell.editor
                dialog = FindReplaceDialog(editor, self)
                dialog.exec_()

                
            elif hasattr(self.focused_cell, "d_editor"):  # for  DocumentEditor
                editor = self.focused_cell.d_editor.editor
                dialog = FindReplaceDialog(editor, self)
                dialog.exec_()

    def save_as_file(self):
        """
        Prompts the user to choose a new file path and saves the notebook content there.
        Updates self.file_path and status bar message.
        """
        

        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            self.file_path or "",
            "Jupyter Notebook (*.ipynb)"
        )

        if not new_path:
            return  # کاربر لغو کرده

        cells = []
        for cell in self.cell_widgets:
            if cell.editor_type == "code":
                cells.append(cell.get_nb_code_cell())
            elif cell.editor_type == "markdown":
                cells.append(cell.get_nb_markdown_cell())

        nb = nbformat.v4.new_notebook()
        nb["cells"] = cells

        try:
            with open(new_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save file:\n{e}")
        else:
            self.file_path = new_path
            self.status_l("Saved As: " + new_path)

    def run_cell_blocking(self, cell):
        loop = QEventLoop()

        def on_done():
            print("[run_cell_blocking] cell finished")
            loop.quit()

        cell.notify_done = on_done
        cell.run()
        loop.exec_()
    
    def variable_table(self, refresh=False):
        new_data = self.ipython_kernel.inspect_all_user_attributes(self.ipython_kernel.shell)
       
        if not new_data :
            self.status_c("    No Data For Showing In Table -> Run a Cell To Process " )
            return

        if hasattr(self, 'obj_table_window') and self.obj_table_window.isVisible() and refresh:
            
            
            self.obj_table_window.add_objects(new_data)
        elif not refresh:
            
            self.obj_table_window = ObjectInspectorWindow(file_name=self.name_only)
            self.obj_table_window.add_objects(new_data)
              
    def closeEvent(self, event):
        
            if self.fake_close :
                self.fake_close = False
                return
            
            if  self.is_notebook_modified():
                return 
            
            
            msg = QMessageBox(self)            
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Save File")
            msg.setText(f"Do you want to save changes to:\n\n{self.name_only}")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Save)

            choice = msg.exec_()

            if choice == QMessageBox.Save:
              
                    self.ipynb_format_save_file()
               

            elif choice == QMessageBox.Discard:
                parent = self.parent()
                
                parent.close()



            elif choice == QMessageBox.Cancel:
               
                event.ignore()
                return

        # اگر از حلقه با موفقیت خارج شد یعنی هیچ Cancel وجود ندارد
            event.accept()

    
    def is_notebook_modified(self):
        self.ipynb_format_save_file(True)
        hash1 = self.compute_md5(self.temp_path)
        hash2 = self.compute_md5(self.file_path)
        
        if hash1 == hash2 :            
            return True
        return False
     
    def compute_md5(self, path):
        try:
            with open(path, "rb") as f:
                data = f.read()
            hash_code = hashlib.md5(data).hexdigest()            
            return hash_code[:6] # return only 6 char of hashcode 
        except Exception as e:
            print(f"[compute_md5] Error: {e}")
            return None         
        
        
    def print_cell(self):
        if self.focused_cell : 
            self.focused_cell.print_full_cell()
            
    
    def toggle_detach_mode(self):
        self.fake_close = True
        if self.chk_detach.isChecked():
            
            # مسیر رفت: از MDI به QMainWindow
            mdi_subwindow = self.parent()
            if mdi_subwindow and isinstance(mdi_subwindow, QMdiSubWindow):
                self.setParent(None)  # قطع ارتباط با QMdiSubWindow                
                mdi_subwindow.close()

            self.detached_window = QMainWindow()
            self.detached_window.setWindowTitle(self.windowTitle())
            self.detached_window.setCentralWidget(self)
            self.detached_window.closeEvent = self._handle_detached_close_event
            self.detached_window.resize(1000, 800)
            icon_path = os.path.join(os.path.dirname(__file__), "image", "ipynb_icon.png")  
            icon = QIcon(icon_path)  # مسیر آیکن یا QRC
            self.detached_window.setWindowIcon(icon)


            # افزودن status bar
            status_bar = QStatusBar()
            status_bar.setStyleSheet("background-color: #f0f0f0; color: #444; font-size: 11px;")
            status_bar.showMessage("Detached mode active")
            self.detached_window.setStatusBar(status_bar)


            self.detached_window.show()
            self.detached = True

        else:
            # مسیر برگشت: از QMainWindow به MDI
            if self.detached_window:
                self.detached_window.takeCentralWidget()  # جلوگیری از حذف self
                self.detached_window.close()
                self.detached_window = None
                self.detached = False

                if self.mdi_area and hasattr(self.mdi_area, "addSubWindow"):
                    sub_window = self.mdi_area.addSubWindow(self)
                    sub_window.show()
            

    def _handle_detached_close_event(self, event):
        """
        Custom closeEvent for detached QMainWindow.
        This ensures WorkWindow's closeEvent logic is triggered.
        """
        self.closeEvent(event)  # اجرای منطق ذخیره‌سازی و هشدار
        if event.isAccepted():
            self.detached_window = None
            self.detached = False
            
            
    def graph (self) :
        pass
        
        # if hasattr(self.focused_cell , 'editor'):
        #     text = self.focused_cell.editor.toPlainText()
        #     self.graph_window = QMainWindow(self)
        #     self.graph_window.setWindowTitle("Graph Window")
        #     # ویجت گراف
        #     chart = RelationChartView(code=text)
        #     # قرار دادن در پنجرهٔ جدید
        #     self.graph_window.setCentralWidget(chart)
        #     self.graph_window.resize(800, 600)
        #     self.graph_window.show()

    def iptopy(self):
        if not self.file_path :
            return
            
        i = 0
        base_dir = os.path.dirname(self.file_path)
        new_path = os.path.join(base_dir, f'{self.name_only}.py')
        print(new_path)
        

        with open (new_path , 'w' , encoding='utf-8') as f:
            
            for cell in self.cell_widgets :
                i  = i + 1
                if cell.editor_type == 'code' and  hasattr(cell , 'editor') and cell.editor :                    
                                
                    f.write('\n#--------------------------------------')
                    f.write(f'\n# CODE CELL {i}')                                          
                    f.write('\n#--------------------------------------')                 
                    f.write('\n'+cell.editor.toPlainText() + '\n')
                    
                elif cell.editor_type == 'markdown' and hasattr(cell , 'd_editor') and cell.d_editor.editor : 
                    
                    f.write('\n#--------------------------------------')
                    f.write(f'\n# DOCUMENT CELL {i}')                                          
                    f.write('\n#--------------------------------------')     
                    
                    
                    f.write('\n""" \n')
                    f.write(cell.d_editor.editor.toPlainText()+ '\n')
                    f.write('"""\n')
                
                        
                    
                    