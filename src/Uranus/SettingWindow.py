import json
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QColorDialog, QFontDialog, QSpinBox, QTabWidget, QFrame, QPushButton
)
from PyQt5.QtGui import  QFont
from PyQt5.QtCore import Qt

DEFAULT_SETTINGS = {
    "colors": {
        "Back Ground Color Code": "#ffffff",
        "Back Ground Color MetaData": '#ffffff',
        "Back Ground Color OutPut": "#ffffff",
        "Back Ground Color WorkWindow": "#d9d9d9",
        "Default Title Color": "#BEBDBD",
        "ForGround Color Code": "#181515",
        "ForGround Color MetaData": "#0d0e0f",
        "ForGround Color Output" : "#0d0e0f"

    },
    "Code Font": "Space Mono",
    "Code Font Size": 13,
    "Meta Font": "Segoe UI",
    "Meta Font Size": 12 ,
    "OutPut Font": "Space Mono",
    "OutPut Font Size": 10 ,
    'last_path' : ''
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

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        self.tabs = QTabWidget()
        self.tab_main = QWidget()
        self.tab_extra = QWidget()

        self.init_main_tab()
        self.tab_extra.setLayout(QVBoxLayout())

        self.tabs.addTab(self.tab_main, "Appearance")
        self.tabs.addTab(self.tab_extra, "Advanced")

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
        self.output_font_preview.setFont(QFont(self.settings["Meta Font"], self.settings["OutPut Font Size"]))
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

        self.tab_main.setLayout(layout)

    def select_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["colors"][key] = color.name()
            self.color_previews[key].setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")
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

        self.save_settings()

    def reset_to_defaults(self):
        self.settings = json.loads(json.dumps(DEFAULT_SETTINGS))
        for key in self.settings["colors"]:
            self.color_previews[key].setStyleSheet(f"background-color: {self.settings['colors'][key]}; border: 1px solid gray;")
        self.code_font_preview.setText(self.settings["Code Font"])
        self.code_font_size_spin.setValue(self.settings["Code Font Size"])
        self.meta_font_preview.setText(self.settings["Meta Font"])
        self.meta_font_size_spin.setValue(self.settings["Meta Font Size"])
        self.output_font_preview.setText(self.settings["OutPut Font"])
        self.output_font_size_spin.setValue(self.settings["OutPut Font Size"])
        self.update_font_preview("code")
        self.update_font_preview("meta")
        self.update_font_preview("OutPut")
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
