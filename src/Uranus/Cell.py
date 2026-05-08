import re ,  hashlib ,os ,markdown2 ,time ,sys
from nbformat.v4 import  new_code_cell, new_markdown_cell

# PyQT Methods Import
from PyQt5.QtGui import QFont, QTextCursor , QTextDocument, QTextImageFormat , QTextOption 
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject , QTimer
from PyQt5.QtWidgets import QFrame, QHBoxLayout,QSizePolicy, QRadioButton, QButtonGroup, QVBoxLayout , QLabel, QScrollArea , QApplication
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Uranus Calss Import
from Uranus.SettingWindow import load_setting
from Uranus.DocumentEditor import DocumentEditor
from Uranus.OutputEditor import OutputEditor
from Uranus.CodeEditor import CodeEditor
from Uranus.DataOutputEditor import DataFrameWidget
from Uranus.ImageOutput import ImageOutput
from Uranus.MarkdownEditor import MarkdownEditor


import sys

class CodeRunner(QObject):
    finished = pyqtSignal(list)
    stream = pyqtSignal(object)

    def __init__(self, kernel, code):
        super().__init__()
        self.kernel = kernel
        self.code = code
        # تعریف متغیر پرچم در اینجا بسیار مهم است
        self._stop_request = False 

    def stop(self):
        """این متد توسط دکمه استاپ فراخوانی می‌شود"""
        self._stop_request = True

    def run(self):
        # دسترسی به shell برای مدیریت نمایش خطا
        shell = self.kernel.shell
        
        # ذخیره تنظیمات قبلی
        old_showtb = shell.showtraceback
        
        # تابع هوشمند برای فیلتر کردن فقط KeyboardInterrupt
        def dummy_showtb(*args, **kwargs):
            # args[1] معمولاً نوع خطا (etype) است
            if len(args) > 1 and args[1] is KeyboardInterrupt:
                return # فقط این خطا را نمایش نده
            # سایر خطاها را با تابع اصلی نمایش بده
            old_showtb(*args, **kwargs)

        # تابع trace برای بررسی پرچم توقف
        def trace_func(frame, event, arg):
            if self._stop_request:
                self._stop_request = False
                raise KeyboardInterrupt("Execution stopped by user")
            return trace_func
        
        # فعال کردن trace
        old_trace = sys.settrace(trace_func)
        
        try:
            # جایگزینی تابع نمایش خطا
            shell.showtraceback = dummy_showtb
            
            # اجرای کد
            outputs = self.kernel.run_cell(self.code, self.stream.emit)            
       
        except:
                pass
            
        finally:
            # بسیار مهم: برگرداندن تنظیمات به حالت قبل
            sys.settrace(old_trace)
            shell.showtraceback = old_showtb
            
        self.finished.emit(outputs)


class Cell(QFrame):

    clicked = pyqtSignal() # focused Cell Signal
    code_editor_clicked = pyqtSignal(object)
    doc_editor_clicked  = pyqtSignal(object)
    doc_editor_editor_clicked = pyqtSignal(object)
    markdown_editor_clicked  = pyqtSignal(object)
    markdown_editor_editor_clicked = pyqtSignal(object)
 

    """
        Represents a single notebook cell in the Uranus IDE, supporting both code and doc_editor types.

        Features:
        - Dynamically switches between CodeEditor and DocumentEditor based on cell type.
        - Executes code using IPythonKernel and displays output in text, image, or table format.
        - Emits signals to notify focus and editor interactions.
        - Supports visual styling, border color, and output toggling.

        Parameters:
        - editor_type: "code" or "doc_editor" to determine initial editor type.
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
        - get_nb_doc_editor_cell(): Converts cell to nbformat doc_editor cell.
        """

    def __init__(self,nb_cell ,editor_type=None, src_content=None, border_color=None,
             kernel=None, notify_done=None, origin='uranus', outputs=None,
             status_c=None, status_r=None, height=0 ):

        
        
        super().__init__()
        
        os.environ["QT_LOGGING_RULES"] = "*.debug=false"        
        self.debug = False
        if self.debug: print('[Cell->init]')


        self.outputs = outputs or []
        self.origin = origin
        self.editor_type = editor_type
        self.notify_done = notify_done
        self.src_content = src_content
        self.border_color = border_color
        self.editor = None
        self.kernel = kernel
        self.cells_content = []
        self.execution_lock = True  # activate the lock in start of Processing
        self.status_c = status_c
        self.status_r = status_r
        self.editor_height = height
        self.nb_cell = nb_cell   
        self._start_time = None
        self._stop_time = None
        self._duration = None
        self._delta_time = None
        self.led_permission = True # Permission to chane led color 
        self.output_editor_enable = True
          
      
        # Load settings
        setting = load_setting()
        self.bg_main_window = setting["colors"]["Back Ground Color WorkWindow"]
        self.bg_border_color_default = setting["colors"]['Default Title Color']
        line_number_font = setting['Line Number Font']
        line_number_font_size = setting['Line Number Font Size']
        header_height = setting["Line Number Box Height"] # پیش‌فرض ۴۰ اگر کلید وجود نداشت

        
        

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


        # Frame internal
        self.task_frame = QFrame()

        
        self.task_frame.setStyleSheet(f"""
                    QFrame {{
                        border: 0px solid {self.bg_border_color_default};
                        border-radius: 0px;
                        background-color: {self.bg_main_window};
                        padding: 0px;   /* بدون فاصله داخلی */
                        margin: 0px;    /* بدون فاصله خارجی */
                    }}
                """)


        
        # Horizental Layout
        self.task_layout = QHBoxLayout(self.task_frame)
        self.task_layout.setContentsMargins(0, 0, 0, 0)  # حذف margin
        self.task_layout.setSpacing(5)                   # حذف فاصله بین ویجت‌ها
        
        
        self.run_status = QLabel()
        self.run_status.setAlignment(Qt.AlignLeft)
        self.run_status.setFixedWidth(16)
        self.run_status.setFixedHeight(16)
        self.run_status.setObjectName("Status")
        self.run_status.setStyleSheet("""
               #Status {
                   background-color: #6E6E6E;
                   font-weight: bold;
                   border: 1px solid black;
                   border-radius: 8px;
                   color: black;
               }
           """)
        
        # Line number
        font = QFont(line_number_font, line_number_font_size)
        self.line_number = QLabel()
        self.line_number.setFont(font)
        self.line_number.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)        
        self.line_number.setFixedHeight(header_height)
        self.line_number.setFixedWidth(350)
        self.line_number.setObjectName("Line_Number")
        self.line_number.setStyleSheet("""
               #Line_Number {
                   background-color: #E3E3E3;
                   font-weight: bold;
                   
                   border: 1px solid #222;
                   border-radius: 3px;
                   color: black;
               }
           """)

       
        
        self.timing = QLabel()
        self.timing.setFont(font)
        self.timing.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Vertical Center
        self.timing.setFixedHeight(header_height)
        self.timing.setObjectName("Timing")
        self.timing.setStyleSheet("""
               #Timing {
                   background-color: #E3E3E3;
                   font-weight: bold;
                   
                   border: 1px solid #222;
                   border-radius: 3px;
                   color: black;
               }
           """)
        
        
        
        # add to H layout 
        self.task_layout.addWidget(self.run_status)
        self.task_layout.addWidget(self.line_number)        
        self.task_layout.addWidget(self.timing)
       

        self.main_layout.addSpacing(5)
      
        # Type selector
        
        self.radio_code = QRadioButton("Code")
        self.radio_doc = QRadioButton("Document")
        self.radio_mark = QRadioButton("MarkDown")
        self.radio_code.setFont(font)
        self.radio_doc.setFont(font)
        self.radio_mark.setFont(font)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_code)
        self.radio_group.addButton(self.radio_doc)
        self.radio_group.addButton(self.radio_mark)

        if not self.editor_type:
            radio_layout = QHBoxLayout()
            radio_layout.addWidget(self.radio_code)
            radio_layout.addWidget(self.radio_doc)
            radio_layout.addWidget(self.radio_mark)
            
            self.main_layout.addLayout(radio_layout)

            self.radio_code.toggled.connect(lambda checked: self.initialize_editor("code") if checked else None)
            self.radio_doc.toggled.connect(lambda checked: self.initialize_editor("doc_editor") if checked else None)
            self.radio_mark.toggled.connect(lambda checked: self.initialize_editor("markdown") if checked else None)

        else :
            self.initialize_editor(editor_type = self.editor_type)


    def run(self):

        self.output_editor_enable = True
        if self.editor_type != 'code':
            return

        self.led_permission = True # Permision to change led Color
        # the indentaion error mast fixed
        self.editor.fix_indentation()
        code = self.editor.toPlainText()
        if hasattr(self,'output_editor'):
                self.output_editor.clear()   
                self.set_led_color('orange')     
        self.outputs = []

        self.runner = CodeRunner(self.kernel, code)
        self._start_time = time.perf_counter()

        
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
        self.setStyleSheet(f"""
                   QFrame {{
                       border: 5px solid {self.border_color};
                       border-radius: 5px;
                       padding: 6px;
                       background-color: {self.bg_main_window}
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

    def initialize_editor(self , editor_type ) :
        """
        Initializes the editor based on the selected cell type.
        Removes the type selector and inserts the appropriate editor.
        Updates title and sidebar colors accordingly.
        """
        if self.debug:
            print('[Cell->initialize_editor]')

        self.editor_type = editor_type

        # Hide type selector radio buttons if present
        if hasattr(self, 'radio_code') and hasattr(self, 'radio_doc') and hasattr(self, 'radio_mark'):
            self.radio_code.hide()
            self.radio_doc.hide()
            self.radio_mark.hide()

        # Code Cell
        if self.editor_type == "code":
            # Create code editor
            self.editor = CodeEditor()
            # LTR
            self.editor.setLayoutDirection(Qt.LeftToRight)

            # اجبار جهت پیش‌فرض سند به LTR
            opt = self.editor.document().defaultTextOption()
            opt.setTextDirection(Qt.LeftToRight)
            opt.setWrapMode(QTextOption.NoWrap)   # جلوگیری از wrap شدن خطوط
            # --- اسکرول‌ها ---
            self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # اسکرول افقی فعال
            self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   # اسکرول عمودی غیرفعال

            self.editor.document().setDefaultTextOption(opt) 
            
                      
            self.main_layout.addWidget(self.task_frame)
            
            self.editor.cursorPositionInfo.connect(self.update_line_char_update)
            self.editor.clicked.connect(lambda: self.code_editor_clicked.emit(self))
            # Add editor to layout
            self.main_layout.addWidget(self.editor)
            # Apply content and styling
            if self.src_content:
                self.editor.setPlainText(self.src_content)
            self.set_color(self.border_color)
            self.editor.adjust_height_code()
            self.editor.textChanged.connect(self.editor.adjust_height_code)
            self.editor.setFocus()
            
            if self.outputs:
                self.inject_outputs(self.outputs)

        # Document Cell
        elif self.editor_type == "doc_editor":
            self.d_editor = DocumentEditor()
            self.main_layout.addWidget(self.d_editor)

            if self.src_content:
                if getattr(self, "origin", None) == "uranus":
                    # 1) تبدیل doc_editor به HTML
                    html = markdown2.markdown(self.src_content)

                    # 2) جایگزینی attachment:image.png با data URL از nb_cell.attachments
                    attachments = getattr(self.nb_cell, "attachments", {}) or {}
                    # attachments شکل: {"image.png": {"image/png": "base64string", ...}, ...}
                    for name, mime_map in attachments.items():
                        # اولویت با image/png
                        b64 = None
                        if "image/png" in mime_map:
                            b64 = mime_map["image/png"]
                            html = html.replace(
                                f"attachment:{name}",
                                f"data:image/png;base64,{b64}"
                            )
                        elif "image/jpeg" in mime_map:
                            b64 = mime_map["image/jpeg"]
                            html = html.replace(
                                f"attachment:{name}",
                                f"data:image/jpeg;base64,{b64}"
                            )
                        # سایر MIMEها هم قابل اضافه شدن‌اند

                    self.d_editor.editor.setHtml(html)
                else:
                    # محتوای تولیدشده توسط اورانوس معمولاً HTML است
                    self.d_editor.editor.setHtml(self.src_content)
                self.d_editor.activate_readonly_mode(init=True)

            self.set_color(self.border_color)
   
            
            if self.editor_height < 100 :
                
                self.d_editor.editor.document().adjustSize()
                QApplication.processEvents()          
                QTimer.singleShot(0, self.d_editor.adjust_height_document_editor) # adjust after cell rendering
                
            else :
                
                QTimer.singleShot(0, lambda  : self.d_editor.set_fixed_height(self.editor_height)) # adjust after cell rendering
          
            
            self.d_editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.d_editor.editor.clicked.connect(lambda: self.doc_editor_clicked.emit(self))
            self.d_editor.editor.doubleClicked.connect(lambda: self.doc_editor_editor_clicked.emit(self))                
            self.d_editor.editor.textChanged.connect(self.d_editor.adjust_height_document_editor)
            self.d_editor.editor.setFocus(True)
            
            
        # Markdown Cell
        elif self.editor_type == "markdown":
            # self.src_content = self.nb_cell.get("source", "")

            # 🔑 نرمالایز کردن attachments
            attachments = self.nb_cell.get("attachments", {})
            images = {}
            for filename, data in attachments.items():
                if isinstance(data, dict):
                    images[filename] = data.get("image/png", "")
                else:
                    images[filename] = data

            self.image = images

            # ساخت ادیتور با متن و تصاویر درست
            self.m_editor = MarkdownEditor(image=self.image)
            self.main_layout.addWidget(self.m_editor)

            if self.src_content:
                self.m_editor.editor.setPlainText(self.src_content)
                self.m_editor.toggle()
            
            
            self.m_editor.clicked.connect(lambda: self.markdown_editor_clicked.emit(self))
            self.m_editor.editor.clicked.connect(lambda: self.markdown_editor_clicked.emit(self))
            self.m_editor.editor.doubleClicked.connect(lambda: self.markdown_editor_editor_clicked.emit(self))  
            
                        
            
            

           

            self.set_color(self.border_color)
   
            
            if self.editor_height < 100 :
                
                self.m_editor.editor.document().adjustSize()
                QApplication.processEvents()          
                QTimer.singleShot(0, self.m_editor.adjust_height_document_editor) # adjust after cell rendering
                
            else :
                
                QTimer.singleShot(0, lambda  : self.m_editor.set_fixed_height(self.editor_height)) # adjust after cell rendering
          
            
               
            self.m_editor.editor.textChanged.connect(self.m_editor.adjust_height_document_editor)
            self.m_editor.editor.setFocus(True)
            
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
                if "site-packages" in clean_line or "interactiveshell.py" in clean_line or "exec(code_obj" in clean_line :
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
            if "KeyboardInterrupt" in clean:
                self.output_editor_enable = False
            
            if not self.output_editor_enable :
               clean = ''                 
              
            for line in clean.splitlines():
                cursor.insertText(line)
                cursor.insertBlock()
                
                # 🔑 تشخیص خطا بر اساس قالب متن
                if ("Traceback" in line) and ("Error" in line) and ("Exception" in line):
                    self.set_led_color("red")
                else:
                    self.set_led_color("green")


            self.toggle_output_button.setVisible(True)
            self.output_editor.setVisible(True)
            self.output_editor.adjust_height()
            self.outputs.append(out)  
    
    def finalize(self):
        self._stop_time = time.perf_counter()
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.compute_execution_time()
        
        
        

        # 🔑 بررسی کل متن خروجی در ادیتور
        if hasattr(self, 'output_editor'):
            full_text = self.output_editor.text_output.toPlainText()
            has_traceback = "Traceback (most recent call last)" in full_text
            has_error_term = ("Error" in full_text) or ("Exception" in full_text)

            if has_traceback and has_error_term:
                self.set_led_color("red")
            else:
                self.set_led_color("green")
        else:
            # اگر ادیتور خروجی ساخته نشده بود، فرض بر موفقیت
            self.set_led_color("green")

        if callable(self.notify_done):
            self.notify_done()

    def update_line_char_update(self, line, column):
            self.line_number.setText(f"Line: {line:^5} | Char: {column:^5}")
            self.status_r(f"Line: {line:^5} | Char: {column:^5}     ")

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
        hash_id = hashlib.sha1(code.encode("utf-8")).hexdigest()[:8]
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
      
    def get_nb_doc_editor_cell(self):
        """
        Converts the current cell's content to a Jupyter-compatible doc_editor cell.
        Assigns a stable ID based on content hash to avoid unnecessary file changes.
        """

        content = self.d_editor.editor.toHtml()    
       
        origin = "uranus"       

        # 🎯 تولید ID پایدار بر اساس محتوای سلول
        hash_id = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]     
        cell = new_markdown_cell(source=content)        
        cell['id'] = hash_id  # ✅ تثبیت ID
        cell['metadata']['bg'] = self.border_color
        cell['metadata']['uranus'] = {"origin": origin} 
        if self.d_editor.flag_doc_height_adjust : # if is recalculted height in document editor 
            cell['metadata']['height'] = self.d_editor.editor_height  # height of editor in pixcel
            
        else :
            cell['metadata']['height'] = self.editor_height  # height of editor in pixcel
           
        return cell
    
    def print_full_cell(self, parent=None):
        """
        Print the full content of this cell (code/doc editor + outputs),
        but only if each editor/output is visible.
        """
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, parent or self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return

        doc = QTextDocument()
        cursor = QTextCursor(doc)

        # --- بخش کد یا داکیومنت ---
        if self.editor_type == "code" and self.editor is not None and self.editor.isVisible():
            cursor.insertText(self.editor.toPlainText())
            cursor.insertBlock()

        elif self.editor_type == "doc_editor" and hasattr(self, "d_editor") and self.d_editor.isVisible():
            cursor.insertHtml(self.d_editor.editor.toHtml())
            cursor.insertBlock()
            
        elif self.editor_type == "markdown" and hasattr(self, "m_editor") and self.m_editor.isVisible():
            cursor.insertHtml(self.m_editor.editor.toHtml())
            cursor.insertBlock()
            
        

        # --- خروجی متنی ---
        if hasattr(self, "output_editor") and self.output_editor.isVisible():
            text_out = self.output_editor.text_output.toPlainText()
            if text_out.strip():
                cursor.insertText(text_out)
                cursor.insertBlock()

        # --- خروجی تصویری ---
        if hasattr(self, "output_image") and self.output_image.isVisible():
            # فرض: base64 در خروجی ذخیره شده
            try:
                base64_data = self.outputs[-1].data["image/png"]  # آخرین خروجی تصویری
                img_format = QTextImageFormat()
                img_format.setName(f"data:image/png;base64,{base64_data}")
                img_format.setWidth(400)  # یا مقدار دلخواه
                img_format.setHeight(300)
                cursor.insertImage(img_format)
                cursor.insertBlock()
            except Exception as e:
                print("[Print Image Error]", e)

       

        # --- پرینت کل ---
        doc.print_(printer)
    
    def get_nb_markdown_cell(self):
        """
        Converts the current cell's content to a Jupyter-compatible markdown cell.
        Assigns a stable ID based on content hash to avoid unnecessary file changes.
        """

        content = self.m_editor.editor.raw_text or self.m_editor.editor.toPlainText()
        

        cell = new_markdown_cell(source=str(content))

        # build attachments correctly
        attachments = {}
        for filename, b64 in self.m_editor.editor.images.items():
            # اگر b64 خودش دیکشنری بود، فقط مقدار رشته را بردار
            if isinstance(b64, dict):
                # معمولاً {"image/png": "..."} است
                data = b64.get("image/png", "")
            else:
                data = b64
            attachments[filename] = {"image/png": data}

        if attachments:
            cell["attachments"] = attachments

        # stable metadata
        hash_id = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]
        cell["id"] = hash_id
        cell["metadata"]["bg"] = self.border_color
        cell["metadata"]["uranus"] = {"origin": "jupyter"}

        return cell
    
    def set_led_color(self, color):
        if self.led_permission :
            if self.debug: print('[Cell->set_led_color]')
            self.run_status.setStyleSheet(f"""
                QLabel#Status {{
                    background-color: {color};
                    border: 1px solid black;
                    border-radius: 8px;
                }}
            """)
        
        
    def compute_execution_time(self):
        self._duration = self._stop_time - self._start_time
        self._delta_time = self._duration 
        self.timing.setText(f'Elapsed : {self._duration:.3f} ')
            
            
        
