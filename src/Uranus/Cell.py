import re , importlib
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject , QTimer
from PyQt5.QtWidgets import QFrame, QHBoxLayout,QSizePolicy, QRadioButton, QButtonGroup, QVBoxLayout , QLabel, QScrollArea , QApplication

from Uranus.SettingWindow import load_setting
from Uranus.DocumentEditor import DocumentEditor
from Uranus.OutputEditor import OutputEditor
from Uranus.CodeEditor import CodeEditor
from nbformat.v4 import  new_code_cell, new_markdown_cell
from Uranus.DataOutputEditor import DataFrameWidget
from Uranus.ImageOutput import ImageOutput



class CodeRunner(QObject):
    finished = pyqtSignal(list)
    stream = pyqtSignal(object)
    """
        Executes a code string using the provided IPython kernel in a separate thread.

        Parameters:
        - kernel: IPythonKernel instance used to run the code.
        - code: Python code string to execute.

        Signals:
        - stream(object): Emitted for each intermediate output (stdout, stderr, etc.).
        - finished(list): Emitted when execution completes, passing the list of outputs.

        Usage:
        This class is designed to be run inside a QThread, allowing non-blocking execution
        of code cells in the Uranus IDE. It supports real-time output streaming and final result collection.
        """

    def __init__(self, kernel, code):
        super().__init__()
        self.kernel = kernel
        self.code = code

    def run(self):
        outputs = self.kernel.run_cell(self.code, self.stream.emit)
        self.finished.emit(outputs)

class Cell(QFrame):

    clicked = pyqtSignal() # focused Cell Signal
    code_editor_clicked = pyqtSignal(object)
    doc_editor_clicked  = pyqtSignal(object)
    doc_editor_editor_clicked = pyqtSignal(object)
 

    """
        Represents a single notebook cell in the Uranus IDE, supporting both code and markdown types.

        Features:
        - Dynamically switches between CodeEditor and DocumentEditor based on cell type.
        - Executes code using IPythonKernel and displays output in text, image, or table format.
        - Emits signals to notify focus and editor interactions.
        - Supports visual styling, border color, and output toggling.

        Parameters:
        - editor_type: "code" or "markdown" to determine initial editor type.
        - content: Initial content to load into the editor.
        - border_color: Optional color for the cell border.
        - kernel: IPythonKernel instance for code execution.
        - notify_done: Callback function to notify when execution finishes.
        - load_condition: Optional flag for conditional loading logic.

        Signals:
        - clicked(): Emitted when the cell is clicked.
        - code_editor_clicked(object): Emitted when the code editor is clicked.
        - doc_editor_clicked(object): Emitted when the document editor is clicked.
        - doc_editor_editor_clicked(object): Emitted when the inner RichTextEditor is double-clicked.

        Output Handling:
        - append_output(out): Routes output to appropriate viewer (text, image, table).
        - toggle_output_*(): Toggles visibility of output sections.
        - finalize(): Cleans up thread and notifies completion.

        Notebook Integration:
        - get_nb_code_cell(): Converts cell to nbformat code cell.
        - get_nb_markdown_cell(): Converts cell to nbformat markdown cell.
        """

    def __init__(self, editor_type=None, content=None, border_color=None,
             kernel=None, notify_done=None, load_condition=False):
        super().__init__()
        self.debug = False
        if self.debug: print('[Cell->init]')


        self.outputs = []
        self.editor_type = editor_type
        self.notify_done = notify_done
        self.load_condition = load_condition
        self.content = content
        self.border_color = border_color
        self.editor = None
        self.kernel = kernel
        self.cells_content = []
        self.execution_lock = True  # activate the lock in start of Processing
        



        # Load settings
        setting = load_setting()
        self.bg_main_window = setting["colors"]["Back Ground Color WorkWindow"]
        self.bg_border_color_default = setting["colors"]['Default Title Color']

        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {self.bg_border_color_default};
                border-radius: 5px;
                background-color: {self.bg_main_window};
                padding: 6px;
            }}
        """)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout: vertical only
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)

        # Data Output toggle button
        self.toggle_output_button_data = QLabel("⮞⮞  TABLE OUTPUT    ⮞⮞")
        self.toggle_output_button_data.setFixedHeight(16)
        self.toggle_output_button_data.setAlignment(Qt.AlignCenter)
        self.toggle_output_button_data.setCursor(Qt.PointingHandCursor)
        self.toggle_output_button_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_output_button_data.setContentsMargins(0, 0, 0, 0)
        self.toggle_output_button_data.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 1px solid #aaa;
                        border-radius: 0px;
                        font-size: 12px;
                        color: #555;
                        padding: 0px;
                    }
                """)
        self.toggle_output_button_data.mousePressEvent = lambda event: self.toggle_output_data()


        # Image Output toggle button
        self.toggle_output_button_image = QLabel("⮞⮞   IMAGE OUTPUT    ⮞⮞")
        self.toggle_output_button_image.setFixedHeight(16)
        self.toggle_output_button_image.setAlignment(Qt.AlignCenter)
        self.toggle_output_button_image.setCursor(Qt.PointingHandCursor)
        self.toggle_output_button_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_output_button_image.setContentsMargins(0, 0, 0, 0)
        self.toggle_output_button_image.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #aaa;
                border-radius: 0px;
                font-size: 12px;
                color: #555;
                padding: 0px;
            }
        """)
        self.toggle_output_button_image.mousePressEvent = lambda event: self.toggle_output_image()

        # Text Output toggle button
        self.toggle_output_button = QLabel("⮞⮞   TEXT OUTPUT    ⮞⮞")
        self.toggle_output_button.setFixedHeight(16)
        self.toggle_output_button.setAlignment(Qt.AlignCenter)
        self.toggle_output_button.setCursor(Qt.PointingHandCursor)
        self.toggle_output_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_output_button.setContentsMargins(0, 0, 0, 0)
        self.toggle_output_button.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 1px solid #aaa;
                        border-radius: 0px;
                        font-size: 12px;
                        color: #555;
                        padding: 0px;
                    }
                """)
        self.toggle_output_button.mousePressEvent = lambda event: self.toggle_output_editor()


        # Line number

        self.line_number = QLabel()
        self.line_number.setAlignment(Qt.AlignLeft)
        self.line_number.setFixedHeight(30)
        self.line_number.setObjectName("line")
        self.line_number.setStyleSheet("""
               #line {
                   background-color: #E3E3E3;
                   font-weight: bold;
                   border: 1px solid #222;
                   border-radius: 3px;
                   color: black;
               }
           """)

        self.main_layout.addWidget(self.line_number)
        self.main_layout.addSpacing(5)
        self.line_number.setVisible(False)


        # Type selector
        font = QFont("Technology", 16)
        self.radio_code = QRadioButton("Code")
        self.radio_doc = QRadioButton("MarkDown")
        self.radio_code.setFont(font)
        self.radio_doc.setFont(font)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_code)
        self.radio_group.addButton(self.radio_doc)

        if not self.editor_type:
            radio_layout = QHBoxLayout()
            radio_layout.addWidget(self.radio_code)
            radio_layout.addWidget(self.radio_doc)
            self.main_layout.addLayout(radio_layout)

            self.radio_code.toggled.connect(lambda checked: self.initialize_editor("code") if checked else None)
            self.radio_doc.toggled.connect(lambda checked: self.initialize_editor("markdown") if checked else None)

        elif self.editor_type == 'code':
            self.initialize_editor("code", content=self.content, border_color=self.border_color)

        elif self.editor_type == 'markdown':
            self.initialize_editor("markdown", content=self.content, border_color=self.border_color)


    def run(self):

        if self.editor_type != 'code':
            return

        code = self.editor.toPlainText()
        self.output_editor.clear()
        self.outputs = []

        self.runner = CodeRunner(self.kernel, code)
        self.runner.stream.connect(self.append_output)
        self.runner.finished.connect(self.finalize)

        self.thread = QThread(self)
        self.runner.moveToThread(self.thread)
        self.thread.started.connect(self.runner.run)
        self.runner.finished.connect(self.thread.quit)
        self.runner.finished.connect(self.thread.deleteLater)
        self.thread.start()
       
    def mousePressEvent(self, event):
            if self.debug :print('[Cell->mousePressEvent]')
            self.clicked.emit()
            super().mousePressEvent(event)

    def toggle_output_data(self):

        is_visible = self.scroll.isVisible()
        self.scroll.setVisible(not is_visible)
        self.toggle_output_button_data.setText("⮞⮞   TABEL OUTPUT    ⮞⮞" if is_visible else "⮟⮟   TABLE OUTPUT    ⮟⮟")

    def toggle_output_image(self):

        is_visible = self.output_image.isVisible()
        self.output_image.setVisible(not is_visible)
        self.toggle_output_button_image.setText("⮞⮞   IMAGE OUTPUT    ⮞⮞" if is_visible else "⮟⮟   IMAGE OUTPUT    ⮟⮟")

    def toggle_output_editor(self):

            is_visible = self.output_editor.isVisible()
            self.output_editor.setVisible(not is_visible)
            self.toggle_output_button.setText("⮞⮞   TEXT OUTPUT    ⮞⮞" if is_visible else "⮟⮟   TEXT OUTPUT    ⮟⮟")

    def set_color(self, color):
        if self.debug :print('[Cell->set_color]')
        self.border_color = color or self.bg_border_color_default
        self.setStyleSheet(f"background-color: {self.border_color}; font-weight: bold;  color: white;")
        self.setStyleSheet(f"""
                   QFrame {{
                       border: 5px solid {self.border_color};
                       border-radius: 5px;
                       padding: 6px;
                   }}
               """)
        if hasattr(self, 'output_data'):
            self.output_data.setStyleSheet("border: 1px solid black; padding: 0px;")
            if hasattr(self.output_data, 'table'): # if pandas is installed
                self.output_data.table.setStyleSheet("border: 1px solid gray; padding: 0px;")
                self.output_data.table.horizontalHeader().setStyleSheet("border: 0px solid gray; padding: 0px;")

    @staticmethod
    def strip_ansi(text):
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def initialize_editor(self, editor_type, content=None, border_color=None):
        """
        Initializes the editor based on the selected cell type.
        Removes the type selector and inserts the appropriate editor.
        Updates title and sidebar colors accordingly.
        """
        if self.debug:
            print('[Cell->initialize_editor]')

        # Hide type selector radio buttons if present
        if hasattr(self, 'radio_code') and hasattr(self, 'radio_doc'):
            self.radio_code.hide()
            self.radio_doc.hide()

        self.editor_type = editor_type

        if editor_type == "code":
            # Create code editor
            self.editor = CodeEditor()
            # Line number method Caller
            self.line_number.setVisible(True)
            self.editor.cursorPositionInfo.connect(self.update_line_char_update)
            self.editor.clicked.connect(lambda: self.code_editor_clicked.emit(self))
            # Add editor to layout
            self.main_layout.addWidget(self.editor)

            #Add output toggle and output table

            # Data Frame Table
            self.output_data = DataFrameWidget()
            # Scroll Widget
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setWidget(self.output_data)
            
            self.scroll.setStyleSheet("border: none; background: transparent;")
            self.scroll.setVisible(False)
            self.toggle_output_button_data.setVisible(False)

            self.main_layout.addWidget(self.toggle_output_button_data)
            self.main_layout.addWidget(self.scroll)


            # # Add output toggle and output image
            self.output_image = ImageOutput()
            self.toggle_output_button_image.setVisible(False)
            self.main_layout.addWidget(self.toggle_output_button_image)
            self.main_layout.addWidget(self.output_image)


            # Add output toggle and output editor
            self.output_editor = OutputEditor()
            self.toggle_output_button.setVisible(False)
            self.main_layout.addWidget(self.toggle_output_button)
            self.main_layout.addWidget(self.output_editor)

            # Apply content and styling
            if content:
                self.editor.setPlainText(content)
            self.set_color(border_color)

            self.editor.adjust_height_code()
            self.editor.textChanged.connect(self.editor.adjust_height_code)
            self.editor.setFocus()


        elif editor_type == "markdown":
            # Create markdown editor
            self.editor = DocumentEditor()
            self.main_layout.addWidget(self.editor)
            self.editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.editor.editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.editor.editor.doubleClicked.connect(lambda: self.doc_editor_editor_clicked.emit(self))
            if content:
                self.editor.editor.setHtml(content)
            self.set_color(border_color)                    
            
            self.editor.editor.textChanged.connect(self.editor.adjust_height_document_editor)
            QTimer.singleShot(5, self.editor.adjust_height_document_editor) # adjust after cell rendering
     


            self.editor.editor.setFocus(True)

    def border_focus(self,state):
        if self.debug :print('[Cell->border_focus]')
        self.border_color = self.border_color or self.bg_border_color_default
        if state :
           self.setStyleSheet(f"""
               QFrame {{
                   border: 5px solid {self.border_color};
                   border-radius: 5px;
                   background-color: {self.bg_main_window};
                   padding: 6px;
               }}""")


        else :
            self.setStyleSheet(f"""
                           QFrame {{
                               border: 2px solid {self.border_color};
                               border-radius: 5px;
                               background-color: {self.bg_main_window};
                               padding: 6px;
                           }}""")

        if hasattr(self, 'output_data'):
            self.output_data.setStyleSheet("border: 1px solid black; padding: 0px;")
            if hasattr(self.output_data,'table'):
                self.output_data.table.setStyleSheet("border: 1px solid gray; padding: 0px;")
                self.output_data.table.horizontalHeader().setStyleSheet("border: 0px solid gray; padding: 0px;")


    def append_output(self, out):
        editor = self.output_editor.text_output
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()


        self.output_editor.setVisible(False)
        self.output_image.setVisible(False)
        self.scroll.setVisible(False)

        if out.output_type == 'display_data':
            editor_target = out.metadata.get("editor", "")
            # 🖼️ Image
            if out.output_type == "display_data" and editor_target == "output_image":
                if "image/png" in out.data:

                    self.output_image.show_image_from_base64(out.data["image/png"])
                    self.toggle_output_button_image.setVisible(True)
                    self.output_image.setVisible(True)
                    self.outputs.append(out)
                    return

            # 📊 Table
            elif out.output_type == "display_data" and editor_target == "output_data":
                if "text/html" in out.data:
                    # دریافت مجدد ابجکت از طریق شناسه آن
                    obj_id = out.metadata.get("object_ref")
                    obj = self.kernel.object_store.get(obj_id)


                    # data Frame Table
                    try :
                        import pandas as pd
                    except ImportError :
                        return
                    else :
                        # DataFrame
                        if isinstance(obj, pd.DataFrame) and importlib.util.find_spec("pandas") is not None:
                            self.output_data.set_dataframe(obj) # Method for data frame show
                            self.toggle_output_button_data.setVisible(True)
                            self.scroll.setVisible(True)
                            self.outputs.append(out)
                            return

        else :
            # 🔥 Error
            if out.output_type == "error" :
                for line in out.traceback:
                    clean_line = self.strip_ansi(line.rstrip())

                    if "site-packages" in clean_line or "interactiveshell.py" in clean_line or "exec(code_obj" in clean_line :
                        continue
                    cursor.insertText(clean_line + "\n")

                self.toggle_output_button.setVisible(True)
                self.output_editor.setVisible(True)


            # 📤  String (stream)
            elif out.output_type == "stream":

                clean = self.strip_ansi(out.text).strip()
                if  clean.startswith("Out[") and "]: " in clean:
                   clean = clean.split(':')[1]
                cursor.insertText(clean)
                self.toggle_output_button.setVisible(True)
                self.output_editor.setVisible(True)
                self.outputs.append(out)
                return

        self.outputs.append(out)

    def finalize(self):
        if self.thread :
            self.thread.quit()
            self.thread.wait()
        self.notify_done()

    def update_line_char_update(self, line, column):

            self.line_number.setText(f"Line: {line} | Chr: {column}")

    def get_nb_code_cell(self):
        cell = new_code_cell(source=self.editor.toPlainText())
        cell.outputs = self.outputs
        cell.execution_count = 1
        cell['metadata']['bg'] = self.border_color # Save Title Color
        return cell

    def get_nb_markdown_cell(self):
        cell = new_markdown_cell(source=self.editor.editor.toHtml())
        cell['metadata']['bg'] = self.border_color
        return cell

