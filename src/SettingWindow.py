import json
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QColorDialog, QFontDialog, QSpinBox, QTabWidget, QFrame, QPushButton , QComboBox, QMessageBox  
)
from PyQt5.QtGui import  QFont
from PyQt5.QtCore import Qt

DEFAULT_SETTINGS = {
    "theme": "light",
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
        "string_color": "#FF1493",
        "method_color": "#00897B"
    },
    "colors_ui": {
        "statusbar_left_fg":       "#000000",
        "statusbar_center_fg":     "#000000",
        "statusbar_right_fg":      "#0000FF",
        "statusbar_border":        "#808080",

        "label_fg":                "#000000",
        "label_bg":                "#ffffff",
        "label_border":            "#aaaaaa",

        "cell_status_bg":          "#6E6E6E",
        "cell_status_fg":          "#000000",
        "cell_line_number_bg":     "#E3E3E3",
        "cell_line_number_fg":     "#000000",
        "cell_timing_bg":          "#E3E3E3",
        "cell_timing_fg":          "#000000",

        "cell_border_default":     "#BEBDBD",
        "cell_border_focused":     "#FF8800",

        "tree_bg":                 "#ffffff",
        "tree_fg":                 "#000000",
        "tree_path_bg":            "#f0f0f0",
        "tree_path_fg":            "#000000",

        "line_number_bg":          "#2d1ad8",
        "line_number_fg":          "#FFFFFF",

        "detached_status_bg":      "#f0f0f0",
        "detached_status_fg":      "#444444",

        "autocomplete_bg":         "#1e1e1e",
        "autocomplete_fg":         "#ffffff",
        "autocomplete_selected":   "#264f78",
        "autocomplete_border":     "#444444",
        "autocomplete_doc_bg":     "#252526",
        "autocomplete_doc_fg":     "#ffffff",

        "analyzer_bg":             "#000000",
        "analyzer_fg":             "#ffffff",
        "analyzer_button_bg":      "#333333",
        "analyzer_button_fg":      "#ffffff",

        "toggle_bg":               "#ffffff",
        "toggle_fg":               "#555555",
        "toggle_border":           "#aaaaaa",

        "selection_bg":            "#264f78",
        "selection_fg":            "#ffffff",

        "scrollbar_bg":            "#f0f0f0",
        "scrollbar_handle":        "#999999",
        "scrollbar_handle_border": "#666666",
    },
    "Code Font": "Space Mono",
    "Code Font Size": 13,
    "Meta Font": "Segoe UI",
    "Meta Font Size": 12,
    "OutPut Font": "Space Mono",
    "OutPut Font Size": 10,
    "Line Number Font": "Technology",
    "Line Number Font Size": 16,
    "Line Number Box Height": 30,
    "last_path": ""
}

THEMES = {
    "light": {
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
            "string_color": "#FF1493",
            "method_color": "#00897B"
        },
        "colors_ui": {
            "statusbar_left_fg":       "#000000",
            "statusbar_center_fg":     "#000000",
            "statusbar_right_fg":      "#0000FF",
            "statusbar_border":        "#808080",

            "label_fg":                "#000000",
            "label_bg":                "#ffffff",
            "label_border":            "#aaaaaa",

            "cell_status_bg":          "#6E6E6E",
            "cell_status_fg":          "#000000",
            "cell_line_number_bg":     "#E3E3E3",
            "cell_line_number_fg":     "#000000",
            "cell_timing_bg":          "#E3E3E3",
            "cell_timing_fg":          "#000000",

            "cell_border_default":     "#BEBDBD",
            "cell_border_focused":     "#FF8800",

            "tree_bg":                 "#ffffff",
            "tree_fg":                 "#000000",
            "tree_path_bg":            "#f0f0f0",
            "tree_path_fg":            "#000000",

            "line_number_bg":          "#2d1ad8",
            "line_number_fg":          "#FFFFFF",

            "detached_status_bg":      "#f0f0f0",
            "detached_status_fg":      "#444444",

            "autocomplete_bg":         "#1e1e1e",
            "autocomplete_fg":         "#ffffff",
            "autocomplete_selected":   "#264f78",
            "autocomplete_border":     "#444444",
            "autocomplete_doc_bg":     "#252526",
            "autocomplete_doc_fg":     "#ffffff",

            "analyzer_bg":             "#000000",
            "analyzer_fg":             "#ffffff",
            "analyzer_button_bg":      "#333333",
            "analyzer_button_fg":      "#ffffff",

            "toggle_bg":               "#ffffff",
            "toggle_fg":               "#555555",
            "toggle_border":           "#aaaaaa",

            "selection_bg":            "#264f78",
            "selection_fg":            "#ffffff",

            "scrollbar_bg":            "#f0f0f0",
            "scrollbar_handle":        "#999999",
            "scrollbar_handle_border": "#666666",
        }
    },
    "dark": {
        "colors": {
            "Back Ground Color Code": "#1e1e1e",
            "Back Ground Color MetaData": "#252526",
            "Back Ground Color OutPut": "#1e1e1e",
            "Back Ground Color WorkWindow": "#2d2d2d",
            "Default Title Color": "#555555",
            "ForGround Color Code": "#d4d4d4",
            "ForGround Color MetaData": "#d4d4d4",
            "ForGround Color Output": "#d4d4d4"
        },
        "colors_syntax": {
            "keyword_color":    "#C586C0",
            "builtin_color":    "#4EC9B0",
            "datatype_color":   "#569CD6",
            "exception_color":  "#F44747",
            "module_color":     "#C586C0",
            "number_color":     "#B5CEA8",
            "comment_color":    "#6A9955",
            "structure_color":  "#DCDCAA",
            "decorator_color":  "#DCDCAA",
            "string_color":     "#CE9178",
            "method_color":     "#9CDCFE"
        },
        "colors_ui": {
            "statusbar_left_fg":       "#d4d4d4",
            "statusbar_center_fg":     "#d4d4d4",
            "statusbar_right_fg":      "#569CD6",
            "statusbar_border":        "#444444",

            "label_fg":                "#d4d4d4",
            "label_bg":                "#2d2d2d",
            "label_border":            "#555555",

            "cell_status_bg":          "#4a4a4a",
            "cell_status_fg":          "#ffffff",
            "cell_line_number_bg":     "#3a3a3a",
            "cell_line_number_fg":     "#d4d4d4",
            "cell_timing_bg":          "#3a3a3a",
            "cell_timing_fg":          "#d4d4d4",

            "cell_border_default":     "#555555",
            "cell_border_focused":     "#FF8800",

            "tree_bg":                 "#252526",
            "tree_fg":                 "#d4d4d4",
            "tree_path_bg":            "#2d2d2d",
            "tree_path_fg":            "#d4d4d4",

            "line_number_bg":          "#1e1e1e",
            "line_number_fg":          "#858585",

            "detached_status_bg":      "#2d2d2d",
            "detached_status_fg":      "#d4d4d4",

            "autocomplete_bg":         "#252526",
            "autocomplete_fg":         "#d4d4d4",
            "autocomplete_selected":   "#094771",
            "autocomplete_border":     "#555555",
            "autocomplete_doc_bg":     "#1e1e1e",
            "autocomplete_doc_fg":     "#d4d4d4",

            "analyzer_bg":             "#1e1e1e",
            "analyzer_fg":             "#d4d4d4",
            "analyzer_button_bg":      "#3a3a3a",
            "analyzer_button_fg":      "#d4d4d4",

            "toggle_bg":               "#3a3a3a",
            "toggle_fg":               "#d4d4d4",
            "toggle_border":           "#555555",

            "selection_bg":            "#264f78",
            "selection_fg":            "#ffffff",

            "scrollbar_bg":            "#2d2d2d",
            "scrollbar_handle":        "#555555",
            "scrollbar_handle_border": "#3a3a3a",
        }
    }
}


def get_setting_path():
    current_file = os.path.abspath(__file__)  
    src_dir = os.path.dirname(os.path.dirname(current_file))  
    return os.path.join(src_dir, "setting.json")

def load_setting():
    path = get_setting_path()
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
        return json.loads(json.dumps(DEFAULT_SETTINGS))

    with open(path, "r", encoding="utf-8") as f:
        setting = json.load(f)

    # Fill missing keys
    for key, value in DEFAULT_SETTINGS.items():
        if key not in setting:
            setting[key] = value
        elif key == "colors":
            for color_key, color_value in DEFAULT_SETTINGS["colors"].items():
                if color_key not in setting["colors"]:
                    setting["colors"][color_key] = color_value
        elif key == "colors_syntax":
            for syntax_key, syntax_value in DEFAULT_SETTINGS["colors_syntax"].items():
                if syntax_key not in setting["colors_syntax"]:
                    setting["colors_syntax"][syntax_key] = syntax_value

    if "theme" not in setting:
        setting["theme"] = "light"

    return setting

class SettingsWindow(QWidget):

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

        self.tabs.addTab(self.tab_main, "Appearance")
        self.tabs.addTab(self.tab_extra, "Syntax Color")

        main_layout.addWidget(self.tabs)

        # ===== Bottom Buttons =====
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

        theme_row = QHBoxLayout()
        theme_row.setSpacing(6)
        theme_label = QLabel("Theme:")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentText(current_theme.capitalize())
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        # Temporary: disable theme selector until dark mode is fixed
        self.theme_combo.setEnabled(False)

        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

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
            if self.settings["colors"].get(key, False):
                self.settings["colors"][key] = color.name()
                self.color_previews[key].setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")

            elif self.settings["colors_syntax"].get(key, False):
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
                self.line_number_font_preview.setText(font.family())
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
        default_height = self.settings.get("Line Number Box Height", 30)        
        self.header_height_combo.setCurrentText(str(default_height))

        self.update_font_preview("code")
        self.update_font_preview("meta")
        self.update_font_preview("OutPut")
        self.update_font_preview("LineNumber")
        self.save_settings()

    def update_Line_Number_Box_Height(self):
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
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "setting.json")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
            return json.loads(json.dumps(DEFAULT_SETTINGS))

        with open(path, "r", encoding="utf-8") as f:
            setting = json.load(f)

        # Fill missing keys
        for key, value in DEFAULT_SETTINGS.items():
            if key not in setting:
                setting[key] = value
            elif key == "colors":
                for color_key, color_value in DEFAULT_SETTINGS["colors"].items():
                    if color_key not in setting["colors"]:
                        setting["colors"][color_key] = color_value
            elif key == "colors_syntax":
                for syntax_key, syntax_value in DEFAULT_SETTINGS["colors_syntax"].items():
                    if syntax_key not in setting["colors_syntax"]:
                        setting["colors_syntax"][syntax_key] = syntax_value

        if "theme" not in setting:
            setting["theme"] = "light"

        return setting

    def apply_theme(self):
        setting = load_setting()
        self.bg_main_window = setting["colors"]["Back Ground Color WorkWindow"]

        # Update cell style
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {self.border_color or self.bg_border_color_default};
                border-radius: 5px;
                background-color: {self.bg_main_window};
                padding: 6px;
            }}
        """)

        # Update task_frame style
        self.task_frame.setStyleSheet(f"""
            QFrame {{
                border: 0px solid {self.bg_border_color_default};
                border-radius: 0px;
                background-color: {self.bg_main_window};
                padding: 0px;
                margin: 0px;
            }}
        """)

        # Update toggle buttons
        button_style = """
            QLabel {
                background-color: white;
                border: 1px solid #aaa;
                border-radius: 0px;
                font-size: 12px;
                color: #555;
                padding: 0px;
            }
        """
        if hasattr(self, 'toggle_output_button'):
            self.toggle_output_button.setStyleSheet(button_style)
        if hasattr(self, 'toggle_output_button_data'):
            self.toggle_output_button_data.setStyleSheet(button_style)
        if hasattr(self, 'toggle_output_button_image'):
            self.toggle_output_button_image.setStyleSheet(button_style)

    def on_theme_changed(self, theme_name):
        theme_key = theme_name.lower()

        # Save selected theme
        self.settings["theme"] = theme_key

        # Get new theme colors for preview
        theme_colors = THEMES[theme_key]["colors"]
        theme_syntax = THEMES[theme_key]["colors_syntax"]

        # Update settings dictionary
        for key, value in theme_colors.items():
            self.settings["colors"][key] = value

        for key, value in theme_syntax.items():
            self.settings["colors_syntax"][key] = value

        # Update color previews
        for key, preview in self.color_previews.items():
            if key in theme_colors:
                preview.setStyleSheet(f"background-color: {theme_colors[key]}; border: 1px solid gray;")

        for key, preview in self.syntax_color_previews.items():
            if key in theme_syntax:
                preview.setStyleSheet(f"background-color: {theme_syntax[key]}; border: 1px solid gray;")

        # Save settings
        self.save_settings()

        # Show restart message
        QMessageBox.information(
            self,
            "Theme Changed",
            f"✅ Theme changed to '{theme_name.capitalize()}'\n\n"
            "🔄 Please restart the application for the changes to take effect.\n\n"
            "💡 All settings have been saved."
        )

# ==================== Entry Point برای تست مستقل ====================
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = SettingsWindow()
    window.setWindowTitle("Uranus IDE - Settings (Standalone)")
    window.show()
    
    sys.exit(app.exec_())
