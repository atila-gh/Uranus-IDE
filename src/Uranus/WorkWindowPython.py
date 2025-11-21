 
import os ,base64  ,io ,builtins ,uuid , importlib , hashlib , sys,inspect , nbformat
from nbformat.v4 import  new_output
from contextlib import redirect_stdout, redirect_stderr
from traitlets.config import Config
from IPython.core.interactiveshell import InteractiveShell

# Import Pyqt Feturse
from PyQt5.QtGui import  QIcon , QKeySequence , QTextCursor
from PyQt5.QtCore import  QSize ,QMetaObject, Qt, pyqtSlot, QObject  , QTimer , pyqtSignal
from PyQt5.QtWidgets import (QToolBar, QToolButton,  QShortcut, QWidget , QFrame , QMainWindow
    , QVBoxLayout , QSpacerItem, QSizePolicy , QScrollArea,QDialog, QVBoxLayout, QLineEdit , QMdiSubWindow , QStatusBar
    , QPushButton , QLabel, QHBoxLayout , QFileDialog, QMessageBox , QCheckBox)

# Import Uranus Class
try :
    from Uranus.ObjectInspectorWindow import ObjectInspectorWindow
    from Uranus.PyCodeEditor import PyCodeEditor
except ModuleNotFoundError : 
    from ObjectInspectorWindow import ObjectInspectorWindow
    from PyCodeEditor import PyCodeEditor
    
    

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


    
class WorkWindowPython(QFrame):
    
    code_editor_clicked = pyqtSignal(object)
    
    def __init__(self, file_path=None , status_l = None , context= None
                 , status_c = None , status_r = None  , mdi_area = None):
        self.debug = False
        if self.debug: print('[WorkWindowPython]->[__init__]')

        super().__init__() 
        self.file_path = file_path        
        self.content = context
        self.mdi_area = mdi_area # Midwindow Mainwindow Original Window Container        
        self.status_l = status_l
        self.status_c = status_c
        self.status_r = status_r       
        self.outputs = []
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
        icon_path = os.path.join(os.path.dirname(__file__), "image", "python_icon.png")  
        self.setWindowIcon(QIcon(icon_path))  
        
        
        self.setFrameShape(QFrame.StyledPanel)   # خط دور فریم
        self.setFrameShadow(QFrame.Raised)       # حالت برجسته
        self.setLineWidth(2)                     # ضخامت خط دور فریم
 
        # Set minimum window size
        self.setMinimumSize(620, 600)
        
        # --- Main Layout
        layout = QVBoxLayout(self) # Biuld a main Vertical Layout and attached on window 
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addSpacing(5)  # فاصله افقی از سمت چپ
       

        # --- Top Horizontal Toolbar ---
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Horizontal)
        self.toolbar.setIconSize(QSize(24, 24))
        self.setup_top_toolbar_buttons()
        layout.addWidget(self.toolbar)
        
        
        # --- Add Editor to Layout 
        self.editor = PyCodeEditor()
        self.editor.cursorPositionInfo.connect(self.update_line_char_update)
        self.editor.clicked.connect(lambda: self.code_editor_clicked.emit(self))
        layout.addWidget(self.editor , stretch=1)        
        
        
        # --- sdd Status Bar to Layout
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("Ready")
        layout.addWidget(self.status_bar)   
        
        # --- Editir Make Focusd     
        QTimer.singleShot(0, self.editor.setFocus)


        # --- write Code to Editor  ---
        if self.content :         
            self.editor.setPlainText(self.content)


    def setup_top_toolbar_buttons(self):
       
        # Save py File
        btn_save = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "save.png")
        btn_save.setIcon(QIcon(icon_path))
        btn_save.setToolTip("""
                            <b>Save File</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>Ctrl+S</kbd></span><br>
                            Save the current File in Specific Location.
                            """)

        btn_save.clicked.connect(self.save_file)
        self.toolbar.addWidget(btn_save)
        self.toolbar.addSeparator()  # فاصله یا خط نازک بین دکمه‌ها
       
     
         # Run Button
        self.run_btn = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "run_cell.png")
        self.run_btn.setIcon(QIcon(icon_path))
        self.run_btn.setToolTip("Run Cell")
        self.run_btn.clicked.connect(self.run)
        self.toolbar.addWidget(self.run_btn)
        # define shortcut for run code F5
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.setContext(Qt.ApplicationShortcut)
        shortcut.activated.connect(self.run)
        self.run_btn.setToolTip("""
                                <b>Run Cell</b><br>
                                <span style='color:gray;'>Shortcut: <kbd>F5</kbd></span><br>
                                Executes the current cell and displays the output.
                                """)

 
 
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
        self.toolbar.addWidget(memory)
        self.toolbar.addSeparator()
        
        # print 
        print_cell = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "print.png")
        print_cell.setIcon(QIcon(icon_path))
        print_cell.setToolTip("""
                                   <b>Print</b><br>
                                   
                                   Print Focused Cell 
                                   """)
        print_cell.clicked.connect(self.print_cell)
        self.toolbar.addWidget(print_cell)
        self.toolbar.addSeparator()
        
        # Drawing  Graph
        graph = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "graph.png")
        graph.setIcon(QIcon(icon_path))
        graph.setToolTip("""
                                   <b>Graph</b><br>                                   
                                   Drawing Graph For Run cell Focused Cell 
                                   """)
        graph.clicked.connect(self.graph)
        self.toolbar.addWidget(graph)
        self.toolbar.addSeparator()
        
       
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
        self.toolbar.addWidget(spacer)         # این فاصله‌دهنده همه‌چیز رو به چپ می‌چسبونه
        self.toolbar.addWidget(self.chk_detach)  # این می‌ره سمت راست


    def run(self):
        
       
        # 🔒 غیرفعال کردن دکمه‌ها
        
        self.status_l(self.file_path)
        
        #self.run_btn.setEnabled(False)
        

    def find_replace(self):       
     
            dialog = FindReplaceDialog(self.editor, self)
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
        
           
            if  not self.is_notebook_modified():
                return 
            
            
            msg = QMessageBox(self)            
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Save File")
            msg.setText(f"Do you want to save changes to:\n\n{self.name_only}")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Save)

            choice = msg.exec_()

            if choice == QMessageBox.Save:
              
                    self.save_file()
               

            elif choice == QMessageBox.Discard:
                parent = self.parent()
                
                parent.close()



            elif choice == QMessageBox.Cancel:
               
                event.ignore()
                return

        # اگر از حلقه با موفقیت خارج شد یعنی هیچ Cancel وجود ندارد
            event.accept()

    
    def is_notebook_modified(self):
        code_string = self.editor.toPlainText()
        current_hash = hashlib.md5(code_string.encode('utf-8')).hexdigest()
        original_hash = hashlib.md5(self.content.encode('utf-8')).hexdigest()
        if current_hash == original_hash :
            return False
        return True
        
    
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

    def save_file(self):
       
        content = self.editor.toPlainText()
        if content : 
            try :
                with open(self.file_path , 'w' , encoding='utf-8') as f:
                    f.write(content)
                self.content = content # refresh last Content                 
                self.status_bar.showMessage("File saved successfully", 2000)
                
               
                

            except Exception  as e :
                self.status_l(f'Not Saved {e}')
                
                
    def update_line_char_update(self, line, column):           
            
            self.status_bar.showMessage(f"Line: {line} | Chr: {column}     ")    

    def mousePressEvent(self, event):      

        if self.debug :print('[Cell->mousePressEvent]')
       
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1       
        column = cursor.positionInBlock() + 1 
        self.update_line_char_update(line,column)         


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ساخت پنجرهٔ اصلی
    main_window = QMainWindow()
    main_window.setWindowTitle("Uranus IDE - WorkWindow Test")
    main_window.resize(900, 700)

    # اضافه کردن WorkWindow به عنوان ویجت مرکزی
    work_window = WorkWindowPython()
    main_window.setCentralWidget(work_window)

    main_window.show()
    sys.exit(app.exec_())