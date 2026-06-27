from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp
from Uranus.SettingWindow import load_setting


class CodeHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Python code in the Uranus IDE.
    """

    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        self._triple_quote_ranges = []
        self._cached_text = ""
        self._dirty = True
        
        setting = load_setting()
        
        # ------ Setting 
        code_font_size  = setting['Code Font Size']
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
 
        # ==========================
        # دسته‌بندی کلمات
        # ==========================

        structure_keywords = ["def", "class", "self", "args", "kwargs"]

        keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield", "match", "case", "nonlocal",
        ]

        datatypes = [
            "int", "float", "complex", "bool", "str", "list", "tuple", "set", "frozenset", "dict",
            "bytes", "bytearray", "memoryview", "NoneType", "type", "Ellipsis", "NotImplemented",
            "collections.Counter", "collections.OrderedDict", "collections.defaultdict", "collections.deque",
            "collections.ChainMap", "collections.UserDict", "collections.UserList", "collections.UserString",
            "collections.abc.Iterable", "collections.abc.Iterator", "collections.abc.Mapping", "collections.abc.Sequence",
            "collections.abc.Callable", "collections.abc.Hashable", "collections.abc.Sized", "collections.abc.Container",
            "collections.abc.Reversible", "collections.abc.Generator",
            "np.int8", "np.int16", "np.int32", "np.int64", "np.uint8", "np.uint16", "np.uint32", "np.uint64",
            "np.float16", "np.float32", "np.float64", "np.float128", "np.complex64", "np.complex128", "np.complex256",
            "np.bool_", "np.bool8", "np.object_", "np.object0", "np.str_", "np.unicode_", "np.generic", "np.number",
            "np.void", "np.ndarray", "np.matrix",
            "pd.Series", "pd.DataFrame", "pd.Categorical", "pd.Timestamp", "pd.Timedelta", "pd.Period", "pd.Interval",
            "pd.SparseArray", "pd.IntervalIndex", "pd.CategoricalIndex", "pd.MultiIndex", "pd.RangeIndex",
            "pd.DatetimeIndex", "pd.TimedeltaIndex", "pd.PeriodIndex", "pd.Index", "pd.Int64Index", "pd.UInt64Index",
            "pd.NaT", "pd.NamedAgg",
            "scipy.sparse.csr_matrix", "scipy.sparse.csc_matrix", "scipy.sparse.lil_matrix", "scipy.sparse.dok_matrix",
            "scipy.sparse.bsr_matrix", "scipy.sparse.coo_matrix",
            "decimal.Decimal", "fractions.Fraction", "datetime.date", "datetime.time", "datetime.datetime",
            "datetime.timedelta", "uuid.UUID", "slice",
            "io.StringIO", "io.BytesIO", "io.TextIOWrapper", "re.Pattern", "re.Match", "pathlib.Path",
            "pathlib.PosixPath", "pathlib.WindowsPath", "file",
            "types.GeneratorType", "types.CoroutineType", "types.AsyncGeneratorType", "types.MethodType",
            "types.FunctionType", "types.BuiltinFunctionType", "types.SimpleNamespace", "types.MappingProxyType",
            "types.TracebackType", "types.CodeType",
            "weakref.ReferenceType", "weakref.ProxyType", "weakref.CallableProxyType", "array.array",
            "queue.Queue", "queue.PriorityQueue", "queue.LifoQueue", "multiprocessing.Queue", "threading.Thread",
            "asyncio.Future", "asyncio.Task",
            "xarray.DataArray", "xarray.Dataset", "dask.array.Array", "dask.dataframe.DataFrame",
            "networkx.Graph", "networkx.DiGraph", "networkx.MultiGraph", "networkx.MultiDiGraph",
            "sympy.Symbol", "sympy.Matrix", "sympy.ImmutableMatrix", "sympy.Expression",
            "function", "method", "module", "object"
        ]

        exceptions = [
            "ArithmeticError", "AssertionError", "AttributeError", "BaseException", "BufferError",
            "EOFError", "Exception", "FloatingPointError", "GeneratorExit", "ImportError",
            "IndexError", "KeyError", "KeyboardInterrupt", "LookupError", "MemoryError",
            "ModuleNotFoundError", "NameError", "NotImplementedError", "OSError", "OverflowError",
            "RecursionError", "ReferenceError", "RuntimeError", "StopIteration", "SyntaxError",
            "IndentationError", "TabError", "SystemError", "TypeError", "UnboundLocalError",
            "UnicodeError", "ValueError", "ZeroDivisionError", "FileNotFoundError", "PermissionError", "TimeoutError",
            "ConnectionError", "BrokenPipeError", "IsADirectoryError", "NotADirectoryError", "InterruptedError",
            "BlockingIOError", "ChildProcessError", "ProcessLookupError", "ConnectionAbortedError", "ConnectionRefusedError",
            "ConnectionResetError", "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeTranslateError"
        ]

        modules = [
            "argparse", "asyncio", "BeautifulSoup", "Bokeh", "bs4", "CatBoost", "collections",
            "cv2", "datetime", "decimal", "Django", "Flask", "fractions", "functools", "gensim",
            "imageio", "importlib", "itertools", "json", "kivy", "LightGBM", "logging", "lgb",
            "math", "matplotlib", "mp", "multiprocessing", "networkx", "nltk", "np", "NumPy",
            "OpenCV", "os", "pandas", "pathlib", "pd", "pickle", "PIL", "Plotly", "plotly",
            "pyside", "PyQt", "PySide", "pytest", "random", "re", "requests", "scikit-learn",
            "SciPy", "scrapy", "Seaborn", "shutil", "sklearn", "sm", "sns", "sp", "spaCy",
            "spacy", "statistics", "subprocess", "sys", "tensorflow", "tf", "threading",
            "time", "tk", "Tkinter", "torch", "unittest", "uuid", "xarray", "xgb", "XGBoost"
        ]

        builtins = [
            "abs", "all", "any", "ascii", "aiter", "anext", "bin", "breakpoint",
            "callable", "chr", "classmethod", "compile", "delattr", "dir", "divmod", "enumerate",
            "eval", "exec", "filter", "format", "getattr", "globals", "hasattr", "hash", "help",
            "hex", "id", "input", "isinstance", "issubclass", "iter", "len", "locals", "map", "max",
            "min", "next", "oct", "open", "ord", "pow", "print", "property", "repr", "reversed",
            "round", "setattr", "sorted", "staticmethod", "sum", "super", "type", "vars", "zip",
            "__import__", "range",
            "read", "readline", "readlines", "write", "writelines", "get",
            "__abs__", "__add__", "__and__", "__annotations__", "__await__", "__bool__", "__call__", "__class__",
            "__contains__", "__del__", "__delattr__", "__delete__", "__delitem__", "__dir__", "__divmod__", "__doc__",
            "__enter__", "__eq__", "__exit__", "__float__", "__floor__", "__floordiv__", "__format__", "__ge__",
            "__get__", "__getattr__", "__getattribute__", "__getitem__", "__gt__", "__hash__", "__iadd__", "__iand__",
            "__ifloordiv__", "__ilshift__", "__imatmul__", "__imod__", "__imul__", "__index__", "__init__",
            "__init_subclass__", "__int__", "__invert__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__iter__",
            "__itruediv__", "__ixor__", "__le__", "__len__", "__lshift__", "__lt__", "__matmul__", "__mod__", "__mul__",
            "__ne__", "__neg__", "__or__", "__pos__", "__pow__", "__radd__", "__rand__", "__rdivmod__", "__repr__",
            "__reversed__", "__rfloordiv__", "__rlshift__", "__rmatmul__", "__rmod__", "__rmul__", "__ror__",
            "__round__", "__rpow__", "__rrshift__", "__rshift__", "__rsub__", "__rtruediv__", "__rxor__", "__set__",
            "__setattr__", "__setitem__", "__str__", "__sub__", "__truediv__", "__xor__", "__aiter__", "__anext__",
            "__aenter__", "__aexit__", '__dict__'
        ]

        # ==========================
        # رنگ‌بندی‌ها
        # ==========================

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(keyword_c))
        keyword_format.setFontWeight(QFont.Bold)

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(builtin_c))

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

        self.comment_h2_format = QTextCharFormat(self.comment_format)
        self.comment_h2_format.setFontPointSize(code_font_size+2)

        self.comment_h3_format = QTextCharFormat(self.comment_format)
        self.comment_h3_format.setFontPointSize(code_font_size+4)
        self.comment_h3_format.setFontWeight(QFont.Bold)

        structure_format = QTextCharFormat()
        structure_format.setForeground(QColor(structure_c))
        structure_format.setFontWeight(QFont.Bold)

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(decorator_c))

        # ==========================
        # اضافه کردن قوانین
        # ==========================
        for kw in keywords:
            self.rules.append((QRegExp(r"\b" + kw + r"\b"), keyword_format))

        for dt in datatypes:
            self.rules.append((QRegExp(r"\b" + dt + r"\b"), datatype_format))

        for ex in exceptions:
            self.rules.append((QRegExp(r"\b" + ex + r"\b"), exception_format))

        for mod in modules:
            self.rules.append((QRegExp(r"\b" + mod + r"\b"), module_format))

        for bi in builtins:
            self.rules.append((QRegExp(r"\b" + bi + r"\b"), builtin_format))

        for word in structure_keywords:
            self.rules.append((QRegExp(r"\b" + word + r"\b"), structure_format))

        # ===== رشته‌ها =====
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
        self.rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))

        # اعداد
        self.rules.append((QRegExp(r"\b\d+(\.\d+)?\b"), number_format))
        
        # دکوراتور 
        self.rules.append((QRegExp(r"^\s*@\w+(\(.*\))?"), decorator_format))

    def line_index_to_offset(self, lines, line_num, char_index):
        res = sum(len(lines[i]) + 1 for i in range(line_num)) + char_index
        return res

    def find_triple_quote_blocks(self):
        full_text = self.document().toPlainText()
        lines = full_text.split('\n')
        quote_types = ["'''", '"""']
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
                            start_offset = self.line_index_to_offset(lines, i, idx)
                            end_offset = self.line_index_to_offset(lines, i, end_idx + 3)
                            results.append((start_offset, end_offset))
                        else:
                            in_block = True
                            quote_char = qt
                            start_line, start_index = i, idx
                        break
            else:
                if quote_char in line:
                    idx = line.find(quote_char)
                    if idx != -1:
                        start_offset = self.line_index_to_offset(lines, start_line, start_index)
                        end_offset = self.line_index_to_offset(lines, i, idx + 3)
                        results.append((start_offset, end_offset))
                        in_block = False
                        quote_char = None
                        start_line = start_index = None

        return results

    def _update_triple_quotes_if_needed(self):
        full_text = self.document().toPlainText()
        if self._dirty or self._cached_text != full_text:
            self._triple_quote_ranges = self.find_triple_quote_blocks()
            self._cached_text = full_text
            self._dirty = False

    def rehighlight(self):
        self._dirty = True
        super().rehighlight()

    def highlightBlock(self, text):
        self.setCurrentBlockState(0)
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)

        self._update_triple_quotes_if_needed()

        formatted_mask = [False] * len(text)

        # Triple quotes
        for start_offset, end_offset in self._triple_quote_ranges:
            if start_offset <= block_end and end_offset >= block_start:
                start = max(start_offset, block_start) - block_start
                end = min(end_offset, block_end) - block_start
                if start < len(text) and end <= len(text):
                    self.setFormat(start, end - start, self.string_format)
                    for i in range(start, end):
                        if i < len(text):
                            formatted_mask[i] = True

        # پیدا کردن موقعیت کامنت
        comment_start = text.find('#')
        if comment_start < 0:
            comment_start = len(text)

        if comment_start < len(text) and formatted_mask[comment_start]:
            comment_start = len(text)

        # Single-line strings (با QRegExp)
        for pattern, fmt in self.rules:
            if isinstance(pattern, QRegExp):
                pattern_str = pattern.pattern()
                if pattern_str.startswith('"') or pattern_str.startswith("'") or pattern_str == r"\b\d+(\.\d+)?\b":
                    index = pattern.indexIn(text, 0)
                    while index != -1:
                        length = pattern.matchedLength()
                        if index >= comment_start:
                            break
                        if index + length > comment_start:
                            length = comment_start - index
                        if index < len(text) and index + length <= len(text):
                            if not any(formatted_mask[index:index + length]):
                                self.setFormat(index, length, fmt)
                        index = pattern.indexIn(text, index + length)

        # ===== حلقه اصلی برای قوانین =====
        for pattern, fmt in self.rules:
            if isinstance(pattern, QRegExp):
                index = pattern.indexIn(text, 0)
                while index != -1:
                    length = pattern.matchedLength()
                    if index >= comment_start:
                        break
                    if index + length > comment_start:
                        length = comment_start - index
                    if index < len(text) and index + length <= len(text):
                        if not any(formatted_mask[index:index + length]):
                            self.setFormat(index, length, fmt)
                    index = pattern.indexIn(text, index + length)

        if comment_start < len(text):
            comment_text = text[comment_start:]
            if comment_text.startswith("###"):
                self.setFormat(comment_start, len(text) - comment_start, self.comment_h3_format)
            elif comment_text.startswith("##"):
                self.setFormat(comment_start, len(text) - comment_start, self.comment_h2_format)
            else:
                self.setFormat(comment_start, len(text) - comment_start, self.comment_format)
                
                
                
                