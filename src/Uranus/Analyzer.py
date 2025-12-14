import subprocess
import os
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QGridLayout,
    QCheckBox, QPushButton, QStatusBar
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class RuffHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Ruff output"""
    def __init__(self, parent):
        super().__init__(parent)
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("red"))

        self.warning_format = QTextCharFormat()
        self.warning_format.setForeground(QColor("orange"))

        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QColor("green"))

        self.line_number_format = QTextCharFormat()
        self.line_number_format.setForeground(QColor("#1E90FF"))

        self.line_regex = re.compile(r"^\s*\d+\s*\|")

    def highlightBlock(self, text):
        match = self.line_regex.match(text)
        if match:
            start, end = match.span()
            self.setFormat(start, end - start, self.line_number_format)

        if "F" in text or "E" in text:
            self.setFormat(0, len(text), self.error_format)
        elif "W" in text:
            self.setFormat(0, len(text), self.warning_format)
        elif "All checks passed" in text or "Clean" in text:
            self.setFormat(0, len(text), self.success_format)


class Analyzer(QWidget):
    """Analyzer window with Ruff integration and category checkboxes"""
    def __init__(self, file_path="", parent=None):
        super().__init__(parent)
        self.path = file_path

       

        self.layout = QVBoxLayout(self)

        # Output editor
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.layout.addWidget(self.editor)

        self.highlighter = RuffHighlighter(self.editor.document())

        # Status bar
        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)

        # Grid layout for checkboxes
        self.checkbox_layout = QGridLayout()
        self.checkboxes = {}

        categories = [
            "E","W","F","F403","F405","B","UP","SIM","I","D","ANN","N","Q",
            "ARG","C4","PL","TID","ERA","PGH","TRY","ASYNC","RET","SLF","DTZ","EXE"
        ]

        descriptions = {
            "E": "Style errors from pycodestyle (indentation, spacing, line length, etc.).",
            "W": "Style warnings from pycodestyle (extra spaces, minor formatting issues).",
            "F": "Logical errors from Pyflakes (undefined names, unused imports, etc.).",
            "F403": "Using 'import *' (star imports). Ruff cannot reliably detect which names are imported.",
            "F405": "Name may be undefined or only defined via star imports.",
            "B": "Common bugs and risky patterns detected by flake8-bugbear.",
            "UP": "Outdated Python syntax flagged by pyupgrade.",
            "SIM": "Simplification opportunities from flake8-simplify.",
            "I": "Import sorting issues detected by isort.",
            "D": "Docstring style issues detected by pydocstyle.",
            "ANN": "Missing or incorrect type annotations (flake8-annotations).",
            "N": "Naming convention issues (pep8-naming).",
            "Q": "Quote style issues (flake8-quotes).",
            "ARG": "Unused function arguments (flake8-unused-arguments).",
            "C4": "Comprehension optimizations (flake8-comprehensions).",
            "PL": "Lint rules inspired by pylint.",
            "TID": "Tidying imports (flake8-tidy-imports).",
            "ERA": "Dead code removal (eradicate).",
            "PGH": "Regex-based hooks (pygrep-hooks).",
            "TRY": "Exception handling best practices (tryceratops).",
            "ASYNC": "Async/await misuse (flake8-async).",
            "RET": "Return statement consistency (flake8-return).",
            "SLF": "Improper use of self/cls (flake8-self).",
            "DTZ": "Datetime/timezone issues (flake8-datetimez).",
            "EXE": "File executability issues (flake8-executable)."
        }

        # ✅ قرار دادن همه چک‌باکس‌ها در دو ردیف
        half = len(categories) // 2
        for idx, cat in enumerate(categories):
            row = 0 if idx < half else 1
            col = idx if idx < half else idx - half
            cb = QCheckBox(cat)
            cb.description = descriptions[cat]
            cb.installEventFilter(self)
            cb.setChecked(True)
            self.checkboxes[cat] = cb
            self.checkbox_layout.addWidget(cb, row, col)

        self.layout.addLayout(self.checkbox_layout)

        # Run button
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis)
        self.layout.addWidget(self.run_button)

        # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
                font-family: Consolas, Courier, monospace;
                font-size: 12pt;
            }
            QPlainTextEdit {
                background-color: black;
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QStatusBar {
                color: white;
            }
        """)

        self.run_analysis()

    def eventFilter(self, obj, event):
        if isinstance(obj, QCheckBox):
            if event.type() == event.Enter:
                self.status_bar.showMessage(obj.description)
            elif event.type() == event.Leave:
                self.status_bar.clearMessage()
        return super().eventFilter(obj, event)

    def build_ignore_string(self):
        ignored = [cat for cat, cb in self.checkboxes.items() if not cb.isChecked()]
        return ",".join(ignored) if ignored else ""

    def run_analysis(self):
        if not os.path.exists(self.path):
            self.editor.clear()
            self.editor.appendPlainText(f"❌ File not found: {self.path}")
            return

        ignore_string = self.build_ignore_string()
        cmd = ["ruff", "check", self.path]
        if ignore_string:
            cmd.extend(["--ignore", ignore_string])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.editor.clear()
            if result.stdout:
                self.editor.appendPlainText(result.stdout)
            if result.stderr:
                self.editor.appendPlainText("Errors:\n" + result.stderr)
        except Exception as e:
            self.editor.appendPlainText(f"Analyzer error: {e}")