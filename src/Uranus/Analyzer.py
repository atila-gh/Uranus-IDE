# Analyzer

from PyQt5.QtGui import  QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal 
from PyQt5.QtWidgets import QPlainTextEdit,QApplication  
import ruff                      


from Uranus.CodeHighlight import CodeHighlighter
from Uranus.SettingWindow import load_setting  


class Analyzer  (QPlainTextEdit):
   


    def __init__(self, parent=None):
        # print('[CodeEditor->__init__]')
        self.copy = self.my_copy()

        super().__init__(parent)
        setting = load_setting()
        
        # ------ Setting 
        self.tab_size = 4  # تعداد فاصله برای هر تب
        bg_code         = setting['colors']['Back Ground Color Code']       
        fg_code         = setting['colors']['ForGround Color Code']
        code_font       = setting['Code Font']
        code_font_size  = setting['Code Font Size']
      

        # ✅ ارتفاع اولیه (مثلاً 80 پیکسل)
        
        
        self.setFont(QFont(code_font, code_font_size,QFont.Bold))  # تست با فونت معتبر               
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


    
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = Analyzer ()
    window.show()
    sys.exit(app.exec_())