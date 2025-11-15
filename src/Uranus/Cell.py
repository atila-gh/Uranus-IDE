import re ,  html2text , hashlib
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
             kernel=None, notify_done=None , origin = 'uranus' , outputs=None 
             , status_c = None , status_r = None , height = 0):
        
        
        super().__init__()
        self.debug = False
        if self.debug: print('[Cell->init]')


        self.outputs = outputs or []
        self.origin = origin
        self.editor_type = editor_type
        self.notify_done = notify_done
        self.content = content
        self.border_color = border_color
        self.editor = None
        self.kernel = kernel
        self.cells_content = []
        self.execution_lock = True  # activate the lock in start of Processing
        self.status_c = status_c
        self.status_r = status_r
        self.editor_height = height


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
        self.radio_doc = QRadioButton("Document")
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
            self.radio_doc.toggled.connect(lambda checked: self.initialize_editor("markdown" , original = True) if checked else None)

        elif self.editor_type == 'code':
            self.initialize_editor("code", content=self.content, border_color=self.border_color)

        elif self.editor_type == 'markdown':
            self.initialize_editor("markdown", content=self.content, border_color=self.border_color)


    def run(self):

        if self.editor_type != 'code':
            return

        code = self.editor.toPlainText()
        if hasattr(self,'output_editor'):
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
        if self.editor_type  == 'code':
            cursor = self.editor.textCursor()
            line = cursor.blockNumber() + 1       
            column = cursor.positionInBlock() + 1 
            self.update_line_char_update(line,column) 
            
         
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

    def initialize_editor(self, editor_type, content=None, border_color=None , original = False ):
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
            # Apply content and styling
            if content:
                self.editor.setPlainText(content)
            self.set_color(border_color)
            self.editor.adjust_height_code()
            self.editor.textChanged.connect(self.editor.adjust_height_code)
            self.editor.setFocus()
            
            if self.outputs:
                self.inject_outputs(self.outputs)



        elif editor_type == "markdown":
            # Create markdown editor
            self.d_editor = DocumentEditor()
            self.main_layout.addWidget(self.d_editor)
           
            if content:
                self.d_editor.editor.setHtml(content)
                self.d_editor.activate_readonly_mode(init= True)
            self.set_color(border_color) 
            
            
            if self.editor_height < 100 :
                #print('[EDITOR HEIGHT < 100]' , self.editor_height)
                self.d_editor.editor.document().adjustSize()
                QApplication.processEvents()          
                QTimer.singleShot(0, self.d_editor.adjust_height_document_editor) # adjust after cell rendering
                
            else :
                #print('[EDITOR HEIGHT > 100] ', self.editor_height) 
                QTimer.singleShot(0, lambda  : self.d_editor.set_fixed_height(self.editor_height)) # adjust after cell rendering
          
            
            self.d_editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.d_editor.editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.d_editor.editor.doubleClicked.connect(lambda: self.doc_editor_editor_clicked.emit(self))                
            self.d_editor.editor.textChanged.connect(self.d_editor.adjust_height_document_editor)
            self.d_editor.editor.setFocus(True)

    def append_output(self, out):
        if out.output_type == "display_data":
            editor_target = out.metadata.get("editor", "")
            
            # 🖼️ Image
            if editor_target == "output_image" and "image/png" in out.data:
                if not hasattr(self, 'output_image'):
                    self.create_output_image()
                self.output_image.show_image_from_base64(out.data["image/png"])
                self.toggle_output_button_image.setVisible(True)
                self.output_image.setVisible(True)
                self.outputs.append(out)  # ✅ ذخیره مجاز

            # 📊 Table 
            elif editor_target == "output_data" and "text/html" in out.data:
                if not hasattr(self, 'output_data'):
                    self.create_output_data()
                obj_id = out.metadata.get("object_ref")
                obj = self.kernel.object_store.get(obj_id)
                try:
                    import pandas as pd
                except ImportError:
                    return
                else:
                    if isinstance(obj, pd.DataFrame):
                        self.output_data.set_dataframe(obj)
                        self.toggle_output_button_data.setVisible(True)
                        self.scroll.setVisible(True)
                        return  

        elif out.output_type == "error":
            if not hasattr(self, 'output_editor'):
                self.create_output_editor()
            editor = self.output_editor.text_output
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            for line in out.traceback:
                clean_line = self.strip_ansi(line.rstrip())
                if "site-packages" in clean_line or "interactiveshell.py" in clean_line or "exec(code_obj" in clean_line:
                    continue
                cursor.insertText(clean_line)
                cursor.insertBlock()
            self.toggle_output_button.setVisible(True)
            self.output_editor.setVisible(True)
            self.output_editor.adjust_height()
            self.outputs.append(out)  

        elif out.output_type == "stream":
            if not hasattr(self, 'output_editor'):
                self.create_output_editor()
            editor = self.output_editor.text_output
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            clean = self.strip_ansi(out.text)
            for line in clean.splitlines():
                cursor.insertText(line)
                cursor.insertBlock()
            self.toggle_output_button.setVisible(True)
            self.output_editor.setVisible(True)
            self.output_editor.adjust_height()
            self.outputs.append(out)  
    
    def finalize(self):
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        if callable(self.notify_done):
            self.notify_done()

    def update_line_char_update(self, line, column):

            self.line_number.setText(f"Line: {line} | Chr: {column}")
            self.status_r(f"Line: {line} | Chr: {column}     ")

    def get_nb_code_cell(self):
        code = self.editor.toPlainText()
        cell = new_code_cell(source=code)

     
        filtered_outputs = []
        for out in self.outputs:
            if out.output_type == "stream":
                filtered_outputs.append(out)

            elif out.output_type == "error":
                filtered_outputs.append(out)

            elif out.output_type == "display_data":
                editor_target = out.metadata.get("editor", "")
                if editor_target == "output_image" and "image/png" in out.data:
                    filtered_outputs.append(out)

        
        cell.outputs = filtered_outputs
        cell.execution_count = 1

        # metadata
        cell['metadata']['bg'] = self.border_color
        cell['metadata']['uranus'] = {
            "origin": self.origin
        }
        
        
        # Generate md5 static hash code acording to context of cell
        hash_id = hashlib.sha1(code.encode("utf-8")).hexdigest()
        cell['id'] = hash_id

        return cell

   
        
    def create_output_editor (self):
        self.output_editor = OutputEditor()
        self.toggle_output_button.setVisible(False)
        self.main_layout.addWidget(self.toggle_output_button)
        self.main_layout.addWidget(self.output_editor)
        
        self.output_editor.setVisible(False)
           
    def create_output_image(self):
        self.output_image = ImageOutput()
        self.toggle_output_button_image.setVisible(False)
        self.main_layout.addWidget(self.toggle_output_button_image)
        self.main_layout.addWidget(self.output_image)
    
    def create_output_data(self):
        self.output_data = DataFrameWidget()
        #Scroll Widget
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.output_data)            
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.setVisible(False)
        self.scroll.setFixedHeight(500)  
        self.toggle_output_button_data.setVisible(False)
        self.main_layout.addWidget(self.toggle_output_button_data)
        self.main_layout.addWidget(self.scroll)
     
    def inject_outputs(self, outputs):
        for out in outputs:
            if out.output_type == "display_data":
                editor_target = out.metadata.get("editor", "")
                if editor_target == "output_image" and "image/png" in out.data:
                    if not hasattr(self, 'output_image'):
                        self.create_output_image()
                    self.output_image.show_image_from_base64(out.data["image/png"])
                    self.toggle_output_button_image.setVisible(True)
                    self.output_image.setVisible(True)

            elif out.output_type == "error":
                if not hasattr(self, 'output_editor'):
                    self.create_output_editor()
                editor = self.output_editor.text_output
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.End)
                for line in out.traceback:
                    clean_line = self.strip_ansi(line.rstrip())
                    if "site-packages" in clean_line or "interactiveshell.py" in clean_line or "exec(code_obj" in clean_line:
                        continue
                    cursor.insertText(clean_line)
                    cursor.insertBlock()
                self.toggle_output_button.setVisible(True)
                self.output_editor.setVisible(True)
                self.output_editor.adjust_height()

            elif out.output_type == "stream":
                if not hasattr(self, 'output_editor'):
                    self.create_output_editor()
                editor = self.output_editor.text_output
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.End)
                clean = self.strip_ansi(out.text)
                for line in clean.splitlines():
                    cursor.insertText(line)
                    cursor.insertBlock()
                self.toggle_output_button.setVisible(True)
                self.output_editor.setVisible(True)
                self.output_editor.adjust_height()

        self.outputs = outputs
        

    def get_nb_markdown_cell(self):
        """
        Converts the current cell's content to a Jupyter-compatible Markdown cell.
        Assigns a stable ID based on content hash to avoid unnecessary file changes.
        """

        html = self.d_editor.editor.toHtml()

        if self.origin != "uranus":
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.body_width = 0
            markdown = converter.handle(html)
            content = markdown
            origin = "jupyter"
            edited = True
        else:
            content = html
            origin = "uranus"
            edited = False

        # 🎯 تولید ID پایدار بر اساس محتوای سلول
        hash_id = hashlib.md5(content.encode("utf-8")).hexdigest()
        
        cell = new_markdown_cell(source=content)
        
        cell['id'] = hash_id  # ✅ تثبیت ID
        cell['metadata']['bg'] = self.border_color
        cell['metadata']['uranus'] = { "origin": origin, "edited": edited } if edited else {"origin": origin }
        if self.d_editor.flag_doc_height_adjust : # if is recalculted height in document editor 
            cell['metadata']['height'] = self.d_editor.editor_height  # height of editor in pixcel
            #print('[CELL-> FLAGED]' , self.d_editor.editor_height)
        else :
            cell['metadata']['height'] = self.editor_height  # height of editor in pixcel
            #print('[CELL-> NOT FLAGED]' , self.editor_height)
        return cell
    
    
    