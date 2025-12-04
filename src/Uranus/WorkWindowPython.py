
import subprocess, sys, os ,tempfile ,hashlib
# Import Pyqt Feturse
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import  QIcon , QKeySequence , QTextCursor ,QTextDocument 
from PyQt5.QtCore import  QSize , Qt,QTimer , pyqtSignal  
from PyQt5.QtWidgets import (QToolBar, QToolButton,  QShortcut, QWidget , QFrame , QMainWindow
    , QVBoxLayout ,  QSizePolicy ,QDialog, QVBoxLayout, QLineEdit , QMdiSubWindow , QStatusBar , QSplitter , QInputDialog
    , QPushButton , QLabel, QHBoxLayout , QFileDialog, QMessageBox , QCheckBox,)

from Uranus.PyCodeEditor import PyCodeEditor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QColor


class TerminalRunner:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TerminalRunner, cls).__new__(cls)
        return cls._instance

    def run_code(self, code_text: str):
        """اجرای کد پایتون در ترمینال متناسب با سیستم‌عامل"""
        # ذخیرهٔ کد در فایل موقت
        temp_file = os.path.join(tempfile.gettempdir(), "uranus_temp.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code_text)

        python_exe = sys.executable

        # انتخاب دستور بر اساس سیستم‌عامل
        if sys.platform.startswith("win"):
            # ویندوز
            cmd = f'start cmd /k "{python_exe} -u {temp_file}"'
            subprocess.Popen(cmd, shell=True)

        elif sys.platform.startswith("linux"):
            # لینوکس (gnome-terminal)
            cmd = f'gnome-terminal -- bash -c "{python_exe} -u {temp_file}; exec bash"'
            subprocess.Popen(cmd, shell=True)

        elif sys.platform == "darwin":
            # macOS (AppleScript برای باز کردن ترمینال)
            apple_script = f'''
            tell application "Terminal"
                do script "{python_exe} -u {temp_file}"
                activate
            end tell
            '''
            subprocess.Popen(["osascript", "-e", apple_script])

        else:
            raise OSError(f"Unsupported platform: {sys.platform}")
        
        
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.bg = QColor("#f0f0f0")# 
        self.fg = QColor("#444444")
        self.sep = QColor("#d0d0d0")

    def sizeHint(self):
        # عرض ستون بر اساس تعداد رقم‌ها
        digits = len(str(max(1, self.editor.blockCount())))
        fm = self.editor.fontMetrics()
        return QSize(fm.horizontalAdvance("9" * digits) + 12, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#2d1ad8"))

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block)
                .translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(self.editor.font())

        # آفست بسیار کوچک پیکسلی برای هماهنگی بصری (اختیاری)
        pady = 1  # می‌تونی 0، 1 یا 2 تست کنی

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                block_height = int(self.editor.blockBoundingRect(block).height())

                # مستطیل کل بلاک و رسم متن در مرکز عمودی
                rect = QRect(0, top + pady, self.width() - 4, block_height)
                painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, number)

            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())


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
    
    def __init__(self, file_path=None , status_l=None , context=None,
                status_c=None , status_r=None , mdi_area=None):
        super().__init__()
        self.debug = False
        self.file_path = file_path        
        self.content = context or ''
        self.mdi_area = mdi_area        
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
        icon_path = os.path.join(os.path.dirname(__file__), "image", "python_icon.png")  
        self.setWindowIcon(QIcon(icon_path))  
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setMinimumSize(620, 600)
        
        # --- Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addSpacing(5)
    
        # --- Toolbar ---
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Horizontal)
        self.toolbar.setIconSize(QSize(24, 24))
        self.setup_top_toolbar_buttons()
        layout.addWidget(self.toolbar)
        
        # --- Editor + Line Numbers ---
        self.editor = PyCodeEditor()
        self.editor.cursorPositionInfo.connect(self.update_line_char_update)
        self.editor.clicked.connect(lambda: self.code_editor_clicked.emit(self))
        # LTR
        self.editor.setLayoutDirection(Qt.LeftToRight)

        # اجبار جهت پیش‌فرض سند به LTR
        opt = self.editor.document().defaultTextOption()
        opt.setTextDirection(Qt.LeftToRight)
        self.editor.document().setDefaultTextOption(opt)
        
        # # define F5 Shortcut on Editor to run 
        # shortcut = QShortcut(QKeySequence("F5"), self.editor)
        # shortcut.setContext(Qt.WidgetShortcut)
        # shortcut.activated.connect(self.run)

        # ساخت ستون شماره خط با LineNumberArea
        self.line_number_area = LineNumberArea(self.editor)
        self.editor.blockCountChanged.connect(self.update_line_number_area_width)
        self.editor.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.line_number_area)
        editor_layout.addWidget(self.editor)

        editor_container = QWidget()
        editor_container.setLayout(editor_layout)

        # --- Status Bar ---
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("Ready")
        
        # --- Splitter برای ادیتور و کنسول ---
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(editor_container)

        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)

        layout.addWidget(self.splitter)
        layout.addWidget(self.status_bar)

        # --- Focus Editor ---
        QTimer.singleShot(0, self.editor.setFocus)

        # --- Load Content ---
        if self.content:         
            self.editor.setPlainText(self.content)


    def setup_top_toolbar_buttons(self):
        
        # فاصله از سمت چپ
        left_spacer = QWidget()
        left_spacer.setFixedWidth(50)   # مقدار فاصله (مثلاً 10px)
        self.toolbar.addWidget(left_spacer)


       
        # Save py File
        btn_save = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "save.png")
        btn_save.setIcon(QIcon(icon_path))
        btn_save.setToolTip("""
                            <b>Save File</b><br>
                            <span style='color:gray;'>Shortcut: <kbd>Ctrl+S</kbd></span><br>
                            Save the current File.
                            """)

        btn_save.clicked.connect(self.save_file)
        self.toolbar.addWidget(btn_save)
        self.toolbar.addSeparator()  # فاصله یا خط نازک بین دکمه‌ها
       
     
         # Run Button
        self.run_btn = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "run_cell.png")
        self.run_btn.setIcon(QIcon(icon_path))
        self.run_btn.setToolTip("Run Module")
        self.run_btn.clicked.connect(self.run)
        self.toolbar.addWidget(self.run_btn)
        # define shortcut for run code F5
      
        # print 
        print_cell = QToolButton()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "print.png")
        print_cell.setIcon(QIcon(icon_path))
        print_cell.setToolTip("""
                                   <b>Print</b><br>                                   
                                   Print Module 
                                   """)
        print_cell.clicked.connect(self.print_cell)
        self.toolbar.addWidget(print_cell)
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
            "Python (*.py)"
        )

        if not new_path:
            return  # کاربر لغو کرده

        content = self.editor.toPlainText()
        if content : 
            try :
                with open(new_path , 'w' , encoding='utf-8') as f:
                    f.write(content)
                self.content = content # refresh last Content                 
                self.status_bar.showMessage("File saved successfully", 2000)
            except Exception  as e :
                self.status_l(f'Not Saved {e}')
        
           
    def closeEvent(self, event):
        
        if self.fake_close :
            self.fake_close = False
            return
        # --- منطق قبلی ذخیره‌سازی و هشدار ---
        if not self.is_notebook_modified():
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
            if parent:
                parent.close()
        elif choice == QMessageBox.Cancel:
            event.ignore()
            return

        event.accept()


        try:
            if self.kc:
                self.kc.stop_channels()
            if self.km:
                self.km.shutdown_kernel()
        except Exception as e:
            print(f"[WorkWindowPython] Kernel shutdown error: {e}")
    
    def is_notebook_modified(self):
        code_string = self.editor.toPlainText()
        current_hash = hashlib.md5(code_string.encode('utf-8')).hexdigest()
        original_hash = hashlib.md5(self.content.encode('utf-8')).hexdigest()
        if current_hash == original_hash :
            return False
        return True
        
    

    def toggle_detach_mode(self):
        self.fake_close = True
        if self.chk_detach.isChecked():
            # مسیر رفت: از MDI به QMainWindow
            mdi_subwindow = self.parent()
            if mdi_subwindow and isinstance(mdi_subwindow, QMdiSubWindow):
                self.setParent(None)
                mdi_subwindow.close()

            self.detached_window = QMainWindow()
            self.detached_window.setWindowTitle(self.windowTitle())
            self.detached_window.setCentralWidget(self)
            self.detached_window.closeEvent = self._handle_detached_close_event
            self.detached_window.resize(1000, 800)

            # آیکن
            icon_path = os.path.join(os.path.dirname(__file__), "image", "ipynb_icon.png")
            self.detached_window.setWindowIcon(QIcon(icon_path))

            # status bar
            status_bar = QStatusBar()
            status_bar.setStyleSheet("background-color: #f0f0f0; color: #444; font-size: 11px;")
            status_bar.showMessage("Detached mode active")
            self.detached_window.setStatusBar(status_bar)

            # 🔑 ساخت شورتکات F5 مخصوص detached
            self._detach_shortcut = QShortcut(QKeySequence("F5"), self.detached_window)
            self._detach_shortcut.activated.connect(self.run)
            
           

            self.detached_window.show()
            self.detached = True

        else:
            # مسیر برگشت: از QMainWindow به MDI
            if self.detached_window:
                # 🔑 حذف شورتکات detached
                if hasattr(self, "_detach_shortcut"):
                    self._detach_shortcut.disconnect()
                    self._detach_shortcut.setParent(None)
                    self._detach_shortcut = None

                self.detached_window.takeCentralWidget()
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

  
    def print_cell(self, parent=None):
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
        if  self.editor :
            cursor.insertText(self.editor.toPlainText())
            cursor.insertBlock()


        # --- پرینت کل ---
        doc.print_(printer)
    
    def update_line_number_area_width(self, _):
        self.line_number_area.setFixedWidth(self.line_number_area.sizeHint().width())

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                        self.line_number_area.width(), rect.height())
        
   

    def run(self):
        """خواندن متن ادیتور و ارسال به ترمینال"""
        editor_text = self.editor.toPlainText() if hasattr(self, "editor") else ""
        if not editor_text.strip():
            return  # اگر ادیتور خالی است، کاری نکن
 
        terminal = TerminalRunner()        
        terminal.run_code(editor_text)  # اجرای متن در همان ترمینال




