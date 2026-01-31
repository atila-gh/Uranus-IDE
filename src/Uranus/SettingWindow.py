import json
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QColorDialog, QFontDialog, QSpinBox, QTabWidget, QFrame, QPushButton , QComboBox
)
from PyQt5.QtGui import  QFont
from PyQt5.QtCore import Qt

'''
BLACK MODE

{
    "colors": {
        "Back Ground Color Code": "#000000",
        "Back Ground Color MetaData": "#000000",
        "Back Ground Color OutPut": "#000000",
        "Back Ground Color WorkWindow": "#444444",
        "Default Title Color": "#444444",
        "ForGround Color Code": "#ffffff",
        "ForGround Color MetaData": "#ffffff",
        "ForGround Color Output": "#ffffff"
    },
    "colors_syntax": {
        "keyword_color": "#aaaaff",
        "builtin_color": "#aa00ff",
        "datatype_color": "#FF8C00",
        "exception_color": "#CC0000",
        "module_color": "#008dce",
        "number_color": "#1E90FF",
        "comment_color": "#d3d3d3",
        "structure_color": "#008f00",
        "decorator_color": "#B22222",
        "string_color": "#ab0056"
    },
    "Code Font": "Space Mono",
    "Code Font Size": 13,
    "Meta Font": "Segoe UI",
    "Meta Font Size": 12,
    "OutPut Font": "Space Mono",
    "OutPut Font Size": 10,
    "Line Number Font": "Technology",
    "Line Number Font Size": 16,
    "last_path": "C:/Users/Tonal/Desktop"
}

'''


DEFAULT_SETTINGS = {
    "colors": {
        "Back Ground Color Code": "#ffffff",
        "Back Ground Color MetaData": "#ffffff",
        "Back Ground Color OutPut": "#ffffff",
        "Back Ground Color WorkWindow": "#d9d9d9",
        
        "Default Title Color": "#BEBDBD",
        "ForGround Color Code": "#181515",
        "ForGround Color MetaData": "#0d0e0f",
        "ForGround Color Output": "#0d0e0f"
        
    },

    "colors_syntax": {
    "keyword_color": "#0000CC",
    "builtin_color": "#6A0DAD",
    "datatype_color": "#FF8C00",
    "exception_color": "#CC0000",
    "module_color": "#008080",
    "number_color": "#1E90FF",
    "comment_color": "#696969",
    "structure_color": "#006400",
    "decorator_color": "#B22222",
    "string_color": "#FF1493"
},

    "Code Font": "Space Mono",
    "Code Font Size": 13,
    "Meta Font": "Segoe UI",
    "Meta Font Size": 12,
    "OutPut Font": "Space Mono",
    "OutPut Font Size": 10,
    "Line Number Font": "Technology",
    "Line Number Font Size": 16,
    "Line Number Box Height" : 30 ,    
    "last_path": ""
}

def get_setting_path():
    """Returns absolute path to setting.json inside Uranus/src/"""
    current_file = os.path.abspath(__file__)  # src/Uranus/SettingWindow.py
    src_dir = os.path.dirname(os.path.dirname(current_file))  # ← src/
    return os.path.join(src_dir, "setting.json")

def load_setting():
    path = get_setting_path()
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
        return json.loads(json.dumps(DEFAULT_SETTINGS))  # Deep copy

    with open(path, "r", encoding="utf-8") as f:
        setting = json.load(f)

    # تکمیل کلیدهای ناقص
    for key, value in DEFAULT_SETTINGS.items():
        if key not in setting:
            setting[key] = value
        elif key == "colors":
            for color_key, color_value in DEFAULT_SETTINGS["colors"].items():
                if color_key not in setting["colors"]:
                    setting["colors"][color_key] = color_value

    return setting

class SettingsWindow(QWidget):
    """
        A configuration panel for customizing appearance and font settings in Uranus IDE.

        This class provides a tabbed interface for modifying UI colors, font families, and font sizes
    used across code editors, markdown cells, and output viewers. Changes are persisted to a JSON
    settings file and applied globally across the application.

        Features:
        - Color pickers for background and foreground elements (code, metadata, output, workspace).
        - Font selectors for code, metadata, and output sections.
        - Spin boxes for adjusting font sizes.
        - Reset-to-default functionality for restoring original settings.
        - Tabbed layout for future extensibility (e.g., advanced settings).

        Components:
        - QTabWidget: Contains "Appearance" and "Advanced" tabs.
        - QVBoxLayout: Main layout with color previews and font controls.
        - QPushButton: Reset and Close actions.

        Methods:
        - select_color(key): Opens QColorDialog and updates preview + settings.
        - select_font(target): Opens QFontDialog and updates font preview + settings.
        - update_font_preview(target): Refreshes font preview label and saves size.
        - reset_to_defaults(): Restores all settings to DEFAULT_SETTINGS.
        - save_settings(): Writes current settings to setting.json.
        - load_settings(): Loads settings from file or creates default if missing.

        Usage:
        Typically invoked from the main menu or toolbar to personalize the IDE's look and feel.
        All changes are immediately saved and reflected in editor components.
        """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 500)
        self.settings = self.load_settings()

        for key, value in DEFAULT_SETTINGS.items():
            if key not in self.settings:
                self.settings[key] = value

        for key, value in DEFAULT_SETTINGS["colors"].items():
            if key not in self.settings["colors"]:
                self.settings["colors"][key] = value
                
        for key, value in DEFAULT_SETTINGS["colors_syntax"].items():
            if key not in self.settings["colors_syntax"]:
                self.settings["colors_syntax"][key] = value

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        self.tabs = QTabWidget()
        self.tab_main = QWidget()
        self.tab_extra = QWidget()

        self.init_main_tab()
        self.init_syntax_tab()
        #self.tab_extra.setLayout(QVBoxLayout())

        self.tabs.addTab(self.tab_main, "Appearance")
        self.tabs.addTab(self.tab_extra, "Syntax Color")

        main_layout.addWidget(self.tabs)

        button_row = QHBoxLayout()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_row.addWidget(reset_btn, alignment=Qt.AlignLeft)
        button_row.addStretch()
        button_row.addWidget(close_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)

    def init_main_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.color_previews = {}
        for key in self.settings["colors"]:
            row = QHBoxLayout()
            row.setSpacing(6)
            label = QLabel(f"{key}:")
            preview = QFrame()
            preview.setFixedSize(60, 22)
            preview.setStyleSheet(f"background-color: {self.settings['colors'][key]}; border: 1px solid gray;")
            preview.setCursor(Qt.PointingHandCursor)
            preview.mousePressEvent = lambda event, k=key: self.select_color(k)
            row.addWidget(label)
            row.addWidget(preview)
            layout.addLayout(row)
            self.color_previews[key] = preview
            
            

        code_row = QHBoxLayout()
        code_row.setSpacing(6)
        code_label = QLabel("Code Font:")
        self.code_font_preview = QLabel(self.settings["Code Font"])
        self.code_font_preview.setFont(QFont(self.settings["Code Font"], self.settings["Code Font Size"]))
        self.code_font_preview.setCursor(Qt.PointingHandCursor)
        self.code_font_preview.mousePressEvent = lambda event: self.select_font("code")
        code_row.addWidget(code_label)
        code_row.addWidget(self.code_font_preview)
        layout.addLayout(code_row)

        code_size_row = QHBoxLayout()
        code_size_row.setSpacing(6)
        code_size_label = QLabel("Code Size:")
        self.code_font_size_spin = QSpinBox()
        self.code_font_size_spin.setRange(8, 48)
        self.code_font_size_spin.setValue(self.settings["Code Font Size"])
        self.code_font_size_spin.valueChanged.connect(lambda: self.update_font_preview("code"))
        code_size_row.addWidget(code_size_label)
        code_size_row.addWidget(self.code_font_size_spin)
        layout.addLayout(code_size_row)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        meta_label = QLabel("Metadata Font:")
        self.meta_font_preview = QLabel(self.settings["Meta Font"])
        self.meta_font_preview.setFont(QFont(self.settings["Meta Font"], self.settings["Meta Font Size"]))
        self.meta_font_preview.setCursor(Qt.PointingHandCursor)
        self.meta_font_preview.mousePressEvent = lambda event: self.select_font("meta")
        meta_row.addWidget(meta_label)
        meta_row.addWidget(self.meta_font_preview)
        layout.addLayout(meta_row)

        meta_size_row = QHBoxLayout()
        meta_size_row.setSpacing(6)
        meta_size_label = QLabel("Metadata Size:")
        self.meta_font_size_spin = QSpinBox()
        self.meta_font_size_spin.setRange(8, 48)
        self.meta_font_size_spin.setValue(self.settings["Meta Font Size"])
        self.meta_font_size_spin.valueChanged.connect(lambda: self.update_font_preview("meta"))
        meta_size_row.addWidget(meta_size_label)
        meta_size_row.addWidget(self.meta_font_size_spin)
        layout.addLayout(meta_size_row)


        output_row = QHBoxLayout()
        output_row.setSpacing(6)
        output_label = QLabel("OutPut Font:")
        self.output_font_preview = QLabel(self.settings["OutPut Font"])
        self.output_font_preview.setFont(QFont(self.settings["OutPut Font"], self.settings["OutPut Font Size"]))
        self.output_font_preview.setCursor(Qt.PointingHandCursor)
        self.output_font_preview.mousePressEvent = lambda event: self.select_font("OutPut")
        output_row.addWidget(output_label)
        output_row.addWidget(self.output_font_preview)
        layout.addLayout(output_row)

        output_size_row = QHBoxLayout()
        output_size_row.setSpacing(6)
        output_size_label = QLabel("OutPut Size:")
        self.output_font_size_spin = QSpinBox()
        self.output_font_size_spin.setRange(8, 48)
        self.output_font_size_spin.setValue(self.settings["OutPut Font Size"])
        self.output_font_size_spin.valueChanged.connect(lambda: self.update_font_preview("OutPut"))
        output_size_row.addWidget(output_size_label)
        output_size_row.addWidget(self.output_font_size_spin)
        layout.addLayout(output_size_row)
        
        
        line_number_row = QHBoxLayout()
        line_number_row.setSpacing(6)
        line_number_row_label = QLabel("Line Number Font:")
        self.line_number_font_preview = QLabel(self.settings["Line Number Font"])
        self.line_number_font_preview.setFont(QFont(self.settings["Line Number Font"], self.settings["Line Number Font Size"]))
        self.line_number_font_preview.setCursor(Qt.PointingHandCursor)
        self.line_number_font_preview.mousePressEvent = lambda event: self.select_font("LineNumber")
        line_number_row.addWidget(line_number_row_label)
        line_number_row.addWidget(self.line_number_font_preview)
        layout.addLayout(line_number_row)

        line_number_size_row = QHBoxLayout()
        line_number_size_row.setSpacing(6)
        line_number_size_label = QLabel("Line Number Font Size:")
        self.line_number_size_spin = QSpinBox()
        self.line_number_size_spin.setRange(8, 48)
        self.line_number_size_spin.setValue(self.settings["Line Number Font Size"])
        self.line_number_size_spin.valueChanged.connect(lambda: self.update_font_preview("LineNumber"))
        line_number_size_row.addWidget(line_number_size_label)
        line_number_size_row.addWidget(self.line_number_size_spin)
        layout.addLayout(line_number_size_row)
        
        # Line Number Box Height
        header_height_row = QHBoxLayout()
        header_height_label = QLabel("Line Number Box Height :")
        self.header_height_combo = QComboBox()
        heights = [str(i) for i in range(30, 56, 5)]
        self.header_height_combo.addItems(heights)
        current_height = str(self.settings.get("Line Number Box Height", "30"))
        self.header_height_combo.setCurrentText(current_height)
        self.header_height_combo.currentTextChanged.connect(self.update_Line_Number_Box_Height)
        header_height_row.addWidget(header_height_label)
        header_height_row.addWidget(self.header_height_combo)
        layout.addLayout(header_height_row)
        



        self.tab_main.setLayout(layout)
   
    def init_syntax_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.syntax_color_previews = {}
        for key in self.settings["colors_syntax"]:
            row = QHBoxLayout()
            row.setSpacing(6)
            label = QLabel(f"{key}:")
            preview = QFrame()
            preview.setFixedSize(60, 22)
            preview.setStyleSheet(
                f"background-color: {self.settings['colors_syntax'][key]}; border: 1px solid gray;"
            )
            preview.setCursor(Qt.PointingHandCursor)
            preview.mousePressEvent = lambda event, k=key: self.select_color(k)
            row.addWidget(label)
            row.addWidget(preview)
            layout.addLayout(row)
            self.syntax_color_previews[key] = preview

        self.tab_extra.setLayout(layout)
  
    def select_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            if  self.settings["colors"].get(key,False):
                self.settings["colors"][key] = color.name()
                self.color_previews[key].setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")
                
            elif  self.settings["colors_syntax"].get(key,False):
                 self.settings["colors_syntax"][key] = color.name()
                 self.syntax_color_previews[key].setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")
            
            self.save_settings()
  
    def select_font(self, target):
        font, ok = QFontDialog.getFont()
        if ok:
            if target == "code":
                self.settings["Code Font"] = font.family()
                self.code_font_preview.setText(font.family())
                self.update_font_preview("code")
            elif target == "meta":
                self.settings["Meta Font"] = font.family()
                self.meta_font_preview.setText(font.family())
                self.update_font_preview("meta")
            elif target == "OutPut":
                self.settings["OutPut Font"] = font.family()
                self.output_font_preview.setText(font.family())
                self.update_font_preview("OutPut")
            elif target == "LineNumber":
                self.settings["Line Number Font"] = font.family()
                self.output_font_preview.setText(font.family())
                self.update_font_preview("LineNumber")
                
                
            self.save_settings()

    def update_font_preview(self, target):
        if target == "code":
            size = self.code_font_size_spin.value()
            self.settings["Code Font Size"] = size
            font = QFont(self.settings["Code Font"], size)
            self.code_font_preview.setFont(font)

        elif target == "meta":
            size = self.meta_font_size_spin.value()
            self.settings["Meta Font Size"] = size
            font = QFont(self.settings["Meta Font"], size)
            self.meta_font_preview.setFont(font)

        elif target == "OutPut":
            size = self.output_font_size_spin.value()
            self.settings["OutPut Font Size"] = size
            font = QFont(self.settings["OutPut Font"], size)
            self.output_font_preview.setFont(font)

        elif target == "LineNumber":
            size = self.line_number_size_spin.value()
            self.settings["Line Number Font Size"] = size
            font = QFont(self.settings["Line Number Font"], size)
            self.line_number_font_preview.setFont(font)

        self.save_settings()

    def reset_to_defaults(self):
        self.settings = json.loads(json.dumps(DEFAULT_SETTINGS))
        for key in self.settings["colors"]:
            self.color_previews[key].setStyleSheet(f"background-color: {self.settings['colors'][key]}; border: 1px solid gray;")
        
        for key in self.settings["colors_syntax"]:
            self.syntax_color_previews[key].setStyleSheet(f"background-color: {self.settings['colors_syntax'][key]}; border: 1px solid gray;")
        
        
        self.code_font_preview.setText(self.settings["Code Font"])
        self.code_font_size_spin.setValue(self.settings["Code Font Size"])
        self.meta_font_preview.setText(self.settings["Meta Font"])
        self.meta_font_size_spin.setValue(self.settings["Meta Font Size"])
        self.output_font_preview.setText(self.settings["OutPut Font"])
        self.output_font_size_spin.setValue(self.settings["OutPut Font Size"])
        self.line_number_font_preview.setText(self.settings["Line Number Font"])
        self.line_number_size_spin.setValue(self.settings["Line Number Font Size"])
        # ارتفاع باکس شماره خط 
        default_height = self.settings.get("Line Number Box Height", 30)        
        self.header_height_combo.setCurrentText(str(default_height))
        
        self.update_font_preview("code")
        self.update_font_preview("meta")
        self.update_font_preview("OutPut")
        self.update_font_preview("LineNumber")
        self.save_settings()

    def update_Line_Number_Box_Height(self):
        """
        این متد مقادیر جدید از ویجت‌های تنظیمات را می‌خواند و در دیکشنری settings ذخیره می‌کند.
        """
       
        header_height = self.header_height_combo.currentText()       
        self.settings["Line Number Box Height"] = int(header_height) 
        self.save_settings()
               
        


    def save_settings(self):
        path = get_setting_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save settings: {e}")

            
    @staticmethod
    def load_settings():
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "setting.json")  # ← مسیر src/
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
            return json.loads(json.dumps(DEFAULT_SETTINGS))

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
# import sys
# from PyQt5.QtWidgets import QApplication
# from SettingWindow import SettingsWindow

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = SettingsWindow()
#     window.show()
#     sys.exit(app.exec_())