 
import os ,base64  ,io ,builtins ,uuid
from PyQt5.QtGui import  QIcon , QKeySequence
from PyQt5.QtCore import  QSize ,QMetaObject, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import (QToolBar, QToolButton, QColorDialog, QShortcut, QWidget,
    QInputDialog , QSpacerItem, QSizePolicy , QScrollArea)

import nbformat
from nbformat.v4 import new_notebook, new_output
from contextlib import redirect_stdout, redirect_stderr
from IPython.core.interactiveshell import InteractiveShell
import pandas as pd
from Uranus.Cell import Cell

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout

class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)

        self.matches = []
        self.current_index = -1

        self.editor = editor
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()


        self.status_label = QLabel("No matches")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_input)
        layout.addWidget(QLabel("Replace with:"))
        layout.addWidget(self.replace_input)

        btn_layout = QHBoxLayout()
        btn_find = QPushButton("Find Next")
        btn_replace = QPushButton("Replace")
        btn_replace_all = QPushButton("Replace All")

        btn_find.clicked.connect(self.find_next)
        btn_replace.clicked.connect(self.replace_one)
        btn_replace_all.clicked.connect(self.replace_all)



        btn_layout.addWidget(btn_find)
        btn_layout.addWidget(btn_replace)
        btn_layout.addWidget(btn_replace_all)
        layout.addLayout(btn_layout)

    def find_next(self):
        text = self.find_input.text()
        if not text:
            return

        # پیدا کردن همه موارد
        self.matches = []
        cursor = self.editor.textCursor()
        doc = self.editor.document()
        pos = 0
        while True:
            found = doc.find(text, pos)
            if found.isNull():
                break
            self.matches.append(found)
            pos = found.position() + 1

        if not self.matches:
            self.status_label.setText("No matches found")
            self.current_index = -1
            return

        # حرکت به مورد بعدی
        self.current_index = (self.current_index + 1) % len(self.matches)
        self.editor.setTextCursor(self.matches[self.current_index])
        self.status_label.setText(f"Match {self.current_index + 1} of {len(self.matches)}")

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()  # بعد از جایگزینی، برو به مورد بعدی

    def replace_all(self):
        self.status_label.setText(f"Replaced {len(self.matches)} matches")
        self.matches = []
        self.current_index = -1
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        text = self.editor.toPlainText()
        new_text = text.replace(find_text, replace_text)
        self.editor.setPlainText(new_text)
        cursor.endEditBlock()



class InputWaiter(QObject): # for Covering Input

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
        text, ok = QInputDialog.getText(self._dialog_parent, "Input", self._prompt)
        self._value = text if ok else ""

class StreamCatcher(io.StringIO): # 2025-10-11 - edited
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
    def __init__(self):
        self.shell = InteractiveShell.instance()
        self.input_waiter = InputWaiter()
        self.object_store = {}

    def run_cell(self, code: str, callback):

        builtins.input = self.input_waiter.wait_for_input

        # 🔧 تزریق backend امن و جایگزینی plt.show() با ذخیره‌سازی فایل
        if "matplotlib" in code or "plt." in code:
            injected = "import matplotlib; matplotlib.use('Agg')\n"
            code = injected + code.replace("plt.show()", "plt.savefig('plot.png')")

        outputs = []
        stdout_catcher = StreamCatcher("stdout", callback)
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_catcher), redirect_stderr(stderr_buffer):
            result = self.shell.run_cell(code)

        obj = result.result
        stderr_text = stderr_buffer.getvalue().strip()

        # 🖼️ ارسال تصویر اگر فایل ساخته شده باشد
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
                os.remove("plot.png")

        # 🔥 خطا
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

        # ⛔ اگر خروجی None بود یا خطا داشت، ادامه نده
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

        # 📊 جدول
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

        # 🖼️ تصویر — فقط اگر آبجکت خودش قابل ذخیره‌سازی باشه
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


    @staticmethod
    def __uranus_inspect_variables():
        data = []
        for name, value in globals().items():
            if name.startswith("__") or callable(value):
                continue
            data.append({
                "Variable": name,
                "Type": type(value).__name__,
                "Preview": str(value)[:50]
            })
        return pd.DataFrame(data)


class WorkWindow(QWidget):

    focused_cell = None
    """
    Main application window for the Uranus notebook.
    Manages cell creation, deletion, styling, and toolbar actions.
    CodeWindow
            
            |- self.cell_widgets -> List for appending all instance of Cell Class With add_cell() Method [IMPORTANT]
            |- self.active_cell  -> Current Class Instance of Cell() -> Updated Value in set_active_cell()
            |- file_path         -> file path that send from ManinWindow Class
    """

    def __init__(self, content=None, file_path=None):
        self.debug = False
        if self.debug: print('[WorkWindow]->[__init__]')

        super().__init__()

        self.ipython_kernel = IPythonKernel()
        self.ipython_kernel.input_waiter = InputWaiter(self) # for cover input with dialog
        self.file_path = file_path
        self.cell_widgets = []
        self.content = content
        self.execution_in_progress = False
        self.outputs = []

        self.deleted_cells_stack = []

        # Set window title from file name
        if self.file_path:
            filename = os.path.basename(self.file_path)
            name_only = os.path.splitext(filename)[0]
            self.setWindowTitle(name_only)

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


        #ShortCut For Find and Replace
        shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_find.setContext(Qt.ApplicationShortcut)
        shortcut_find.activated.connect(self.open_find_replace)


        # --- Load initial content ---
        self.load_file(self.content)

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
                            <span style='color:gray;'>Shortcut: <kbd>F2</kbd></span><br>
                            Save the current File in Specific Location.
                            """)


        btn_save.clicked.connect(self.ipynb_format_save_file)
        self.top_toolbar.addWidget(btn_save)
        self.top_toolbar.addSeparator()  # فاصله یا خط نازک بین دکمه‌ها
        # Define ShortCut F2
        shortcut_save = QShortcut(QKeySequence("F2"), self)
        shortcut_save.setContext(Qt.ApplicationShortcut)
        shortcut_save.activated.connect(self.ipynb_format_save_file)


        # Move Cell Up
        btn_move_up = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "move_up.png")  # آیکون دلخواه
        btn_move_up.setIcon(QIcon(icon_path))
        btn_move_up.setToolTip("""
                            <b>Move Cell Up</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F3</kbd></span><br>
                            Move Focused Cell Up.
                            """)
        btn_move_up.clicked.connect(self.move_cell_up)
        self.top_toolbar.addWidget(btn_move_up)
        # Define ShortCut F3
        shortcut_move_up = QShortcut(QKeySequence("F3"), self)
        shortcut_move_up.setContext(Qt.ApplicationShortcut)
        shortcut_move_up.activated.connect(self.move_cell_up)


        # Move Sell Botton
        btn_move_down = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "move_down.png")  
        btn_move_down.setIcon(QIcon(icon_path))
        btn_move_down.setToolTip("""
                            <b>Move Cell Down</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F4</kbd></span><br>
                            Move Focused Cell Down.
                            """)
        btn_move_down.clicked.connect(self.move_cell_down)
        self.top_toolbar.addWidget(btn_move_down)

        # Define ShortCut F4
        shortcut_move_down = QShortcut(QKeySequence("F4"), self)
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

        btn_run_all = QToolButton()

        icon_path = os.path.join(os.path.dirname(__file__), "image", "run_all.png")
        btn_run_all.setIcon(QIcon(icon_path))
        btn_run_all.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn_run_all.setToolTip("Run all code cells")
        btn_run_all.clicked.connect(self.run_all_cells)
        self.top_toolbar.addWidget(btn_run_all)


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

        # # Memory Variable List
        # memory = QToolButton()
        # icon_path = os.path.join(os.path.dirname(__file__), "image", "memory.png")
        # memory.setIcon(QIcon(icon_path))
        # memory.setToolTip("""
        #                            <b>Object and Variable</b><br>
        #                            <span style='color:gray;'>Shortcut: <kbd>F9</kbd></span><br>
        #                            Object And Variable List
        #                            """)
        # memory.clicked.connect(lambda : self.ipython_kernel.run_cell("__uranus_inspect_variables()" , self.handle_result))
        # self.top_toolbar.addWidget(memory)

    def setup_toolbar_buttons(self):
        if self.debug :print('[WorkWindow->setup_toolbar_buttons]')


        # Add cell above
        btn_up = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "up.png")
        btn_up.setIcon(QIcon(icon_path))
        btn_up.setToolTip("""
                            <b>Add Cell Above</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F7</kbd></span>
                            """)
        btn_up.clicked.connect(self.add_cell_above)
        self.toolbar.addWidget(btn_up)

        # Define ShortCut F7
        shortcut_add_cell_above = QShortcut(QKeySequence("F7"), self)
        shortcut_add_cell_above.setContext(Qt.ApplicationShortcut)
        shortcut_add_cell_above.activated.connect(self.add_cell_above)

        # Add cell below
        btn_down = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "down.png")
        btn_down.setIcon(QIcon(icon_path))
        btn_down.setToolTip("""
                            <b>Add Cell Below</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>F8</kbd></span>
                            """)
        btn_down.clicked.connect(self.add_cell_below)
        self.toolbar.addWidget(btn_down)

        # Define ShortCut F8
        shortcut_add_cell_below = QShortcut(QKeySequence("F8"), self)
        shortcut_add_cell_below.setContext(Qt.ApplicationShortcut)
        shortcut_add_cell_below.activated.connect(self.add_cell_below)


        # Delete active cell
        btn_delete = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "delete_Page.png")
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

    def add_cell(self,editor_type = None,content=None , border_color=None):
        """
        Adds a new cell at the end of the notebook.
        """
        if self.debug :print('[WorkWindow->add_cell]')
        # create an object of cell class with type of editor if exist
        cell = Cell(editor_type, content , border_color , kernel = self.ipython_kernel , notify_done=self.execution_done )
        # Mouse Event Handler
        cell.clicked.connect(lambda c=cell : self.set_focus(c))
        cell.doc_editor_clicked.connect(lambda c=cell : self.set_focus(c))
        cell.doc_editor_editor_clicked.connect(lambda c=cell : self.set_focus(c))


        self.cell_widgets.append(cell)   # cell append to list of cells
        self.cell_layout.addWidget(cell) # for showing cell add cell to layout
        self.set_focus(cell)

        return cell

    def set_focus(self, cell):
        if self.debug:print('[WorkWindow->set_focus]')

        if self.focused_cell and cell is not self.focused_cell and len(self.cell_widgets) > 1 :
             self.focused_cell.border_focus(False)

        self.focused_cell = cell
        self.run_btn.setEnabled(isinstance(cell, Cell) and not self.execution_in_progress)
        cell.border_focus(True)

    # Run a Single Cell
    def run_focused_cell(self) :
        if self.debug :print('[WorkWindow]->[run_focused_cell]')

       
        if isinstance(self.focused_cell, Cell) and not self.execution_in_progress:
            self.execution_in_progress = True
            self.run_btn.setEnabled(False)
            self.focused_cell.run() # focused_cell is an instance of Cell Class that is focused

    def execution_done(self):
        self.execution_in_progress = False
        self.set_focus(self.focused_cell)

    # Connected to a Button 1
    def add_cell_above(self):
        """
        Inserts a new cell above the currently active cell.
        """
        if self.debug :print('[WorkWindow->add_cell_above]')
        if not self.cell_widgets :
            self.add_cell()

        elif self.focused_cell:
            index = self.cell_widgets.index(self.focused_cell) # شماره اندیس نمونه جاری کلاس را در لیست نمونه های کلاس باز میگرداند
            cell = Cell( kernel = self.ipython_kernel , notify_done=self.execution_done )
            # Mouse Event Handler
            cell.clicked.connect(lambda  c=cell : self.set_focus(c)) # فعال کردن ارسال سیگنال روی هرجای سلول ساخته شده
            cell.doc_editor_clicked.connect(lambda c=cell : self.set_focus(c))
            cell.doc_editor_editor_clicked.connect(lambda c=cell : self.set_focus(c))

            self.cell_widgets.insert(index,cell)
            self.cell_layout.insertWidget(index, cell)

            self.set_focus(cell) # set New Cell focused

    # Connected to a Button 2
    def add_cell_below(self):
        """
        Inserts a new cell below the currently active cell.
        """
        if self.debug :print('[WorkWindow->add_cell_below]')
        if not self.cell_widgets:
            self.add_cell()

        elif self.focused_cell :
            index = self.cell_widgets.index(self.focused_cell)
            cell = Cell( kernel = self.ipython_kernel , notify_done=self.execution_done)
            # Mouse Event Handler
            cell.clicked.connect(lambda  c=cell : self.set_focus(c)) # فعال کردن ارسال سیگنال روی هرجای سلول ساخته شده
            cell.doc_editor_clicked.connect(lambda c=cell : self.set_focus(c))
            cell.doc_editor_editor_clicked.connect(lambda c=cell : self.set_focus(c))


            self.cell_widgets.insert(index + 1,cell)
            self.cell_layout.insertWidget(index + 1, cell)

            self.set_focus(cell) # set New Cell Focused

    # Connected to a Button 3
    def delete_active_cell(self):
        """
        Deletes the currently active cell from the notebook and stores it for multistep undo.
        """
        content = None
        if self.debug: print('[WorkWindow->delete_active_cell]')
        

        if self.focused_cell and self.cell_widgets:
            index = self.cell_widgets.index(self.focused_cell)

            # استخراج محتوا بسته به نوع سلول
            if self.focused_cell.editor_type == 'code':
                content = self.focused_cell.editor.toPlainText()
            elif self.focused_cell.editor_type == 'markdown':
                content = self.focused_cell.editor.editor.toHtml()

            # ذخیره اطلاعات در پشته
            if self.focused_cell.editor_type in ('code', 'markdown'):
                self.deleted_cells_stack.append({
                    "index": index,
                    "cell_type": self.focused_cell.editor_type,
                    "source": content,
                    "color": self.focused_cell.border_color
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
    def ipynb_format_save_file(self,path = None):
        if not path : path = self.file_path
        nb = new_notebook()
        for i in self.cell_widgets :
            if i.editor_type == 'code' :
                nb.cells.append(i.get_nb_code_cell())

            elif i.editor_type == 'markdown':
                nb.cells .append (i.get_nb_markdown_cell())
        try :
            with open(path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

        except TypeError :
            with open('last_save_file.ipynb', "w", encoding="utf-8") as f:
                nbformat.write(nb, f)


    def load_file (self,file_content):
            if self.debug :print('[WorkWindow->load_file]')
            if not file_content :               
                self.add_cell()
            else :

                self.cell_widgets = []
                for  c in file_content.cells:                    

                    bg = c['metadata'].get('bg' , '#000000') # get cell title color

                    if c.cell_type == 'code' :
                        cell = self.add_cell( editor_type='code' , content=c.source ,border_color = bg)
                        for out in c.get('outputs',[]) :
                            cell.append_output(out)


                    elif c.cell_type == 'markdown' :
                         self.add_cell(editor_type='markdown' , content=c.source ,border_color = bg )
                         

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
        Restores the most recently deleted cell from the undo stack.
        """
        if self.debug: print('[WorkWindow->undo_delete_cell]')
        if not self.deleted_cells_stack:
            return

        data = self.deleted_cells_stack.pop()

        cell = Cell(
            editor_type=data["cell_type"],
            content=data["source"],
            border_color=data["color"],
            kernel=self.ipython_kernel,
            notify_done=self.execution_done
        )
        cell.clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_clicked.connect(lambda c=cell: self.set_focus(c))
        cell.doc_editor_editor_clicked.connect(lambda c=cell: self.set_focus(c))

        index = min(data["index"], len(self.cell_widgets))
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
        """
        Executes all code cells in order.
        """
        if self.debug: print('[WorkWindow->run_all_cells]')
        if self.execution_in_progress:
            return  # جلوگیری از اجرای همزمان

        self.execution_in_progress = True
        self.outputs.clear()

        for cell in self.cell_widgets:
            if cell.editor_type == "code":
                cell.run()

        self.execution_in_progress = False

   

    def open_find_replace(self):
        if self.focused_cell and hasattr(self.focused_cell, "editor"):
            editor = self.focused_cell.editor
            if hasattr(editor, "editor"):  # برای DocumentEditor
                editor = editor.editor
            dialog = FindReplaceDialog(editor, self)
            dialog.exec_()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = WorkWindow()
    window.show()
    sys.exit(app.exec_())