from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp,QRegularExpression
from SettingWindow import load_setting





class CodeHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        self.triple_quote_ranges = []
        self.cached_text = ""
        self.dirty = True

        setting = load_setting()

        # Load colors from settings
        keyword_c = setting['colors_syntax']['keyword_color']
        builtin_c = setting['colors_syntax']['builtin_color']
        datatype_c = setting['colors_syntax']['datatype_color']
        exception_c = setting['colors_syntax']['exception_color']
        module_c = setting['colors_syntax']['module_color']
        number_c = setting['colors_syntax']['number_color']
        comment_c = setting['colors_syntax']['comment_color']
        structure_c = setting['colors_syntax']['structure_color']
        decorator_c = setting['colors_syntax']['decorator_color']
        string_c = setting['colors_syntax']['string_color']
        method_c = setting['colors_syntax'].get('method_color', '#00897B')

        # ============================================================
        # DEFINE FORMATS
        # ============================================================

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(keyword_c))
        keyword_format.setFontWeight(QFont.Bold)

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(builtin_c))

        method_format = QTextCharFormat()
        method_format.setForeground(QColor(method_c))

        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(datatype_c))
        datatype_format.setFontWeight(QFont.DemiBold)

        exception_format = QTextCharFormat()
        exception_format.setForeground(QColor(exception_c))
        exception_format.setFontWeight(QFont.Bold)

        module_format = QTextCharFormat()
        module_format.setForeground(QColor(module_c))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(string_c))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(number_c))
        number_format.setFontWeight(QFont.Bold)

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(comment_c))
        self.comment_format.setFontPointSize(14)

        structure_format = QTextCharFormat()
        structure_format.setForeground(QColor(structure_c))
        structure_format.setFontWeight(QFont.Bold)

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(decorator_c))

        # ============================================================
        # TOKEN DEFINITIONS (keywords, datatypes, exceptions, etc.)
        # ============================================================

        keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield", "match", "case"
        ]

        datatypes = [
            "int", "float", "complex", "bool", "str", "list", "tuple", "set",
            "frozenset", "dict", "bytes", "bytearray", "memoryview", "NoneType",
            "type", "object", "Ellipsis", "NotImplemented",
            "collections.Counter", "collections.OrderedDict", "collections.defaultdict",
            "collections.deque", "collections.namedtuple", "collections.ChainMap",
            "np.int8", "np.int16", "np.int32", "np.int64",
            "np.uint8", "np.uint16", "np.uint32", "np.uint64",
            "np.float16", "np.float32", "np.float64",
            "np.complex64", "np.complex128",
            "np.ndarray", "np.array", "np.matrix", "np.dtype",
            "pd.Series", "pd.DataFrame", "pd.Categorical",
            "pd.Timestamp", "pd.Timedelta", "pd.Period", "pd.Interval",
            "pd.Index", "pd.MultiIndex", "pd.DatetimeIndex",
            "scipy.sparse.csr_matrix", "scipy.sparse.csc_matrix",
            "decimal.Decimal", "fractions.Fraction",
            "datetime.date", "datetime.time", "datetime.datetime",
            "datetime.timedelta", "datetime.timezone",
            "uuid.UUID", "pathlib.Path", "pathlib.PosixPath", "pathlib.WindowsPath",
            "io.StringIO", "io.BytesIO", "io.TextIOWrapper",
            "typing.Any", "typing.Optional", "typing.Union",
            "typing.List", "typing.Dict", "typing.Tuple", "typing.Set",
        ]

        exceptions = [
            "BaseException", "Exception", "BaseExceptionGroup", "ExceptionGroup",
            "ArithmeticError", "FloatingPointError", "OverflowError", "ZeroDivisionError",
            "AssertionError", "AttributeError",
            "BufferError", "EOFError",
            "ImportError", "ModuleNotFoundError",
            "LookupError", "IndexError", "KeyError",
            "MemoryError", "NameError", "UnboundLocalError",
            "OSError", "FileNotFoundError", "FileExistsError",
            "PermissionError", "IsADirectoryError", "NotADirectoryError",
            "InterruptedError", "BlockingIOError", "ChildProcessError",
            "ConnectionError", "BrokenPipeError", "ConnectionAbortedError",
            "ConnectionRefusedError", "ConnectionResetError",
            "ProcessLookupError", "TimeoutError",
            "ReferenceError", "RuntimeError", "NotImplementedError", "RecursionError",
            "StopIteration", "StopAsyncIteration",
            "SyntaxError", "IndentationError", "TabError",
            "SystemError", "SystemExit", "KeyboardInterrupt", "GeneratorExit",
            "TypeError", "ValueError",
            "UnicodeError", "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeTranslateError",
            "Warning", "UserWarning", "DeprecationWarning",
            "PendingDeprecationWarning", "SyntaxWarning", "RuntimeWarning",
            "FutureWarning", "ImportWarning", "UnicodeWarning",
            "BytesWarning", "ResourceWarning",
            "EnvironmentError", "IOError", "WindowsError",
        ]

        modules = [
            "os", "sys", "io", "re", "json", "math", "time", "datetime",
            "random", "subprocess", "threading", "asyncio", "functools",
            "itertools", "collections", "argparse", "logging", "pickle",
            "pathlib", "importlib", "decimal", "fractions", "uuid",
            "hashlib", "base64", "tempfile", "shutil", "glob", "csv",
            "sqlite3", "socket", "ssl", "urllib", "http", "email",
            "xml", "html", "unittest", "typing", "dataclasses", "enum",
            "copy", "pprint", "traceback", "warnings", "contextlib",
            "inspect", "platform", "signal", "queue", "abc", "operator",
            "statistics", "secrets", "textwrap", "string", "struct",
            "weakref", "gc", "atexit", "codecs", "unicodedata",
            "numpy", "pandas", "scipy", "matplotlib", "seaborn",
            "sklearn", "statsmodels", "sympy", "networkx",
            "plotly", "bokeh", "dash", "pillow", "PIL", "cv2",
            "tensorflow", "torch", "keras", "jax", "numba",
            "requests", "flask", "django", "fastapi", "aiohttp",
            "beautifulsoup4", "bs4", "scrapy", "selenium",
            "PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter", "kivy", "wx",
            "jedi", "nbformat", "jupyter", "ipython", "IPython",
            "markdown2", "markdown", "yaml", "toml", "dotenv",
            "pytest", "nose", "mock", "hypothesis",
            "dask", "ray", "pyspark", "polars",
        ]

        builtins = [
            # Numeric & Math
            "abs", "divmod", "pow", "round", "sum", "min", "max",
            "bin", "oct", "hex",

            # Type Conversion
            "bool", "int", "float", "complex", "str", "bytes", "bytearray",
            "list", "tuple", "set", "frozenset", "dict",
            "chr", "ord", "repr", "ascii", "format",

            # I/O
            "input", "open", "print","close",

            # Iteration & Sequence
            "all", "any", "enumerate", "filter", "map", "reversed",
            "sorted", "zip", "iter", "next", "len", "range", "slice",

            # Object & Class
            "callable", "classmethod", "staticmethod", "property",
            "delattr", "getattr", "hasattr", "setattr",
            "isinstance", "issubclass", "super",
            "type", "vars", "dir", "id", "hash",

            # Execution & Evaluation
            "compile", "eval", "exec", "__import__", "globals", "locals",

            # Async (Python 3.10+)
            "aiter", "anext",

            # Helpers
            "help", "memoryview", "breakpoint",
        ]

        methods = [
            # String methods
            "capitalize", "casefold", "center", "encode",
            "endswith", "expandtabs", "format_map",
            "isalnum", "isalpha", "isascii", "isdecimal",
            "isdigit", "isidentifier", "islower", "isnumeric",
            "isprintable", "isspace", "istitle", "isupper",
            "join", "ljust", "lower", "lstrip", "maketrans",
            "partition", "removeprefix", "removesuffix", "replace",
            "rfind", "rindex", "rjust", "rpartition", "rsplit",
            "rstrip", "split", "splitlines", "startswith", "strip",
            "swapcase", "title", "translate", "upper", "zfill",

            # List methods
            "append", "extend", "insert", "reverse", "sort",

            # Dict methods
            "fromkeys", "items", "keys", "popitem",
            "setdefault", "values",

            # Set methods
            "difference", "difference_update", "discard",
            "intersection", "intersection_update", "isdisjoint",
            "issubset", "issuperset", "symmetric_difference",
            "symmetric_difference_update", "union",

            # File methods
            "fileno", "flush", "isatty", "readable","read",
            "readline", "readlines", "seek", "seekable", "tell",
            "truncate", "writable", "writelines", "write",

            # Shared methods
            "add", "clear", "copy", "count", "get", "index",
            "pop", "remove", "update",
        ]

        structure_keywords = ["def", "class", "self", "args", "kwargs", "cls"]

        # ============================================================
        # ADD RULES TO THE HIGHLIGHTER
        # ============================================================

        for kw in keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b"), keyword_format))

        for dt in datatypes:
            self.rules.append((QRegularExpression(r"\b" + dt + r"\b"), datatype_format))

        for ex in exceptions:
            self.rules.append((QRegularExpression(r"\b" + ex + r"\b"), exception_format))

        for mod in modules:
            self.rules.append((QRegularExpression(r"\b" + mod + r"\b"), module_format))

        for bi in builtins:
            self.rules.append((QRegularExpression(r"\b" + bi + r"\b"), builtin_format))

        for m in methods:
            self.rules.append((QRegularExpression(r"\b" + m + r"\b"), method_format))

        for word in structure_keywords:
            self.rules.append((QRegularExpression(r"\b" + word + r"\b"), structure_format))

        # ============================================================
        # SPECIAL RULES (Strings, Numbers, Decorators)
        # ============================================================

        # Numbers (integers and floats)
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), number_format))

        # Decorators (@decorator)
        self.rules.append((QRegularExpression(r"^\s*@\w+(\(.*\))?"), decorator_format))

    def line_index_to_offset(self, lines, line_num, char_index):
        res = sum(len(lines[i]) + 1 for i in range(line_num)) + char_index
        return res

    def find_triple_quote_blocks(self):
        full_text = self.document().toPlainText()
        lines = full_text.split('\n')

        # Using string concatenation to avoid syntax errors
        triple_double = '"' + '"' + '"'      
        triple_single = "'" + "'" + "'"      
        quote_types = [triple_double, triple_single]

        results = []
        in_block = False
        quote_char = None
        start_line = start_index = None

        for i, line in enumerate(lines):
            if not in_block:
                for qt in quote_types:
                    if qt in line:
                        idx = line.find(qt)
                        end_idx = line.find(qt, idx + 3)
                        if end_idx != -1:
                            # Single-line triple quote
                            start_offset = self.line_index_to_offset(lines, i, idx)
                            end_offset = self.line_index_to_offset(lines, i, end_idx + 3)
                            results.append((start_offset, end_offset))
                        else:
                            # Multi-line triple quote starts here
                            in_block = True
                            quote_char = qt
                            start_line, start_index = i, idx
                        break
            else:
                # We're inside a multi-line triple quote
                if quote_char in line:
                    idx = line.find(quote_char)
                    if idx != -1:
                        # Found the closing triple quote
                        start_offset = self.line_index_to_offset(lines, start_line, start_index)
                        end_offset = self.line_index_to_offset(lines, i, idx + 3)
                        results.append((start_offset, end_offset))
                        in_block = False
                        quote_char = None
                        start_line = start_index = None

        return results

    def _update_triple_quotes_if_needed(self):
        full_text = self.document().toPlainText()
        if self.dirty or self.cached_text != full_text:
            self.triple_quote_ranges = self.find_triple_quote_blocks()
            self.cached_text = full_text
            self.dirty = False

    def rehighlight(self):
        self.dirty = True
        super().rehighlight()

    def highlightBlock(self, text):
        # Reset block state for multi-line string handling
        self.setCurrentBlockState(0)

        # Get absolute positions of this block in the document
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)

        # Update triple-quote cache if needed
        self._update_triple_quotes_if_needed()

        # ============================================================
        # STEP 1: Initialize tracking variables
        # ============================================================

        # Track which characters are already formatted (to prevent overlap)
        formatted_mask = [False] * len(text)

        # Track if we're inside a single-line string
        in_string = False
        string_char = None

        # ============================================================
        # STEP 2: Process triple-quoted strings (HIGHEST PRIORITY)
        # ============================================================

        for start_offset, end_offset in self.triple_quote_ranges:
            # Check if this block intersects with a triple-quoted block
            if start_offset <= block_end and end_offset >= block_start:
                # Calculate local start and end positions within this block
                start = max(start_offset, block_start) - block_start
                end = min(end_offset, block_end) - block_start

                # Safety check
                if start < len(text) and end <= len(text):
                    # Format as string
                    self.setFormat(start, end - start, self.string_format)

                    # Mark these positions as "already formatted"
                    for i in range(start, end):
                        if i < len(text):
                            formatted_mask[i] = True

        # ============================================================
        # STEP 3: Process single-line strings (", ')
        # ============================================================
        # This uses a simple state machine to track string boundaries
        # It respects escape sequences (\) and ignores quotes inside strings

        i = 0
        while i < len(text):
            # Skip if already formatted (inside triple-quote)
            if formatted_mask[i]:
                i += 1
                continue

            char = text[i]

            # Check if this is a quote character
            if char in ('"', "'"):
                # Find the matching closing quote
                j = i + 1
                found_match = False

                while j < len(text):
                    # Check if this is the closing quote (not escaped)
                    if text[j] == char and text[j-1] != '\\':
                        # Found a match! But only if not already formatted
                        if not any(formatted_mask[i:j+1]):
                            # Format the entire string
                            self.setFormat(i, j - i + 1, self.string_format)
                            # Mark as formatted
                            for k in range(i, j + 1):
                                formatted_mask[k] = True
                        found_match = True
                        break
                    j += 1

                # Move to the position after the string
                if found_match:
                    i = j + 1
                else:
                    # Unterminated string - format to end of line
                    if not any(formatted_mask[i:]):
                        self.setFormat(i, len(text) - i, self.string_format)
                        for k in range(i, len(text)):
                            formatted_mask[k] = True
                    break
            else:
                i += 1

        # ============================================================
        # STEP 4: Find the comment start (#)
        # ============================================================
        # ONLY if the '#' is NOT inside a formatted region (string)

        comment_start = text.find('#')
        if comment_start < 0:
            comment_start = len(text)  # No comment in this block

        # CRITICAL FIX: If '#' is inside a string, ignore it
        if comment_start < len(text) and formatted_mask[comment_start]:
            comment_start = len(text)  # Treat as part of string, not comment

        # ============================================================
        # STEP 5: Process string and number rules
        # ============================================================
        # These are processed together to avoid double-checking

        for pattern, fmt in self.rules:
            # Skip if this is a string or number rule
            # We only want to apply these rules if the pattern is a string or number
            pattern_str = pattern.pattern()
            is_string_rule = pattern_str.startswith('"') or pattern_str.startswith("'")
            is_number_rule = pattern_str == r"\b\d+(\.\d+)?\b"

            if is_string_rule or is_number_rule:
                # Skip string rules - they're already handled above
                if is_string_rule:
                    continue

                # Process number rule
                match = pattern.match(text, 0)
                while match.hasMatch():
                    index = match.capturedStart()
                    length = match.capturedLength()

                    # Stop if we've reached the comment
                    if index >= comment_start:
                        break

                    # Don't extend past the comment
                    if index + length > comment_start:
                        length = comment_start - index

                    # Only apply if not already formatted (inside string)
                    if index < len(text) and index + length <= len(text):
                        if not any(formatted_mask[index:index + length]):
                            self.setFormat(index, length, fmt)

                    # Move to next match
                    match = pattern.match(text, index + length)

        # ============================================================
        # STEP 6: Process all other syntax rules
        # ============================================================
        # This includes keywords, builtins, datatypes, exceptions, modules

        for pattern, fmt in self.rules:
            pattern_str = pattern.pattern()

            # Skip string and number rules (already handled)
            if pattern_str.startswith('"') or pattern_str.startswith("'"):
                continue
            if pattern_str == r"\b\d+(\.\d+)?\b":
                continue

            # Process the pattern
            match = pattern.match(text, 0)
            while match.hasMatch():
                index = match.capturedStart()
                length = match.capturedLength()

                # Stop if we've reached the comment
                if index >= comment_start:
                    break

                # Don't extend past the comment
                if index + length > comment_start:
                    length = comment_start - index

                # Only apply if not already formatted (inside string)
                if index < len(text) and index + length <= len(text):
                    if not any(formatted_mask[index:index + length]):
                        self.setFormat(index, length, fmt)

                # Move to next match
                match = pattern.match(text, index + length)

        # ============================================================
        # STEP 7: Apply comment formatting (SIMPLE - no heading styles)
        # ============================================================
        # This runs ONLY if there is a real comment (not inside a string)
        # All comments are formatted the same way - no special ## or ### rules

        if comment_start < len(text):
            # Simple comment formatting - all comments look the same
            self.setFormat(comment_start, len(text) - comment_start, self.comment_format)