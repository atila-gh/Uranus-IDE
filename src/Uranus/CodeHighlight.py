from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp,QRegularExpression

class CodeHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Python code in the Uranus IDE.

    This class extends QSyntaxHighlighter to apply color formatting to Python source code
    within the CodeEditor widget. It supports a wide range of token categories including:

    - Python keywords (e.g., def, class, return)
    - Built-in functions and dunder methods
    - Data types from Python, NumPy, Pandas, SciPy, and other scientific libraries
    - Exception classes
    - Commonly used modules and aliases (e.g., np, pd, plt)
    - Strings (single, double, triple-quoted)
    - Numbers (integers and floats)
    - Comments
    - Function and class definitions

    Highlights:
    - Uses QRegExp and QRegularExpression for pattern matching.
    - Supports multi-line string highlighting with block state tracking.
    - Color schemes are carefully chosen for readability and semantic clarity.
    - Easily extensible: new token categories can be added via the `rules` list.

    Parameters:
    - document: QTextDocument instance to apply highlighting to.

    Usage:
    Instantiate with a QTextDocument (typically from CodeEditor), and it will automatically
    highlight each block of text as the user types or loads content.

    """

    def __init__(self, document):
        super().__init__(document)
        self.rules = []



        # ==========================
        # دسته‌بندی کلمات
        # ==========================

        structure_keywords = ["def", "class" ,"self"]

        keywords = [
                    "False", "None", "True", "and", "as", "assert", "async", "await",
                    "break",  "continue", "def", "del", "elif", "else", "except",
                    "finally", "for", "from", "global", "if", "import", "in", "is",
                    "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
                    "try", "while", "with", "yield", "match", "case"
                ]

        datatypes = [
                    # Python built-in types
                    "int", "float", "complex", "bool", "str", "list", "tuple", "set",
                    "frozenset", "dict", "bytes", "bytearray", "memoryview", "NoneType",

                    # Python collections
                    "collections.Counter", "collections.OrderedDict", "collections.defaultdict",
                    "collections.deque", "collections.ChainMap", "collections.UserDict",
                    "collections.UserList", "collections.UserString", "collections.abc.Iterable",
                    "collections.abc.Iterator", "collections.abc.Mapping", "collections.abc.Sequence",

                    # NumPy numeric & array types
                    "np.int8", "np.int16", "np.int32", "np.int64",
                    "np.uint8", "np.uint16", "np.uint32", "np.uint64",
                    "np.float16", "np.float32", "np.float64", "np.float128",
                    "np.complex64", "np.complex128", "np.complex256",
                    "np.bool_", "np.object_", "np.str_", "np.unicode_",
                    "np.ndarray", "np.matrix",

                    # Pandas structures
                    "pd.Series", "pd.DataFrame", "pd.Categorical", "pd.Timestamp",
                    "pd.Timedelta", "pd.Period", "pd.Interval", "pd.SparseArray",
                    "pd.IntervalIndex", "pd.CategoricalIndex", "pd.MultiIndex",
                    "pd.RangeIndex", "pd.DatetimeIndex", "pd.TimedeltaIndex", "pd.PeriodIndex",

                    # SciPy sparse matrices
                    "scipy.sparse.csr_matrix", "scipy.sparse.csc_matrix",
                    "scipy.sparse.lil_matrix", "scipy.sparse.dok_matrix",
                    "scipy.sparse.bsr_matrix", "scipy.sparse.coo_matrix",

                    # Python numeric & date types
                    "decimal.Decimal", "fractions.Fraction", "datetime.date", "datetime.time",
                    "datetime.datetime", "datetime.timedelta", "uuid.UUID", "range", "slice",

                    # IO and regex types
                    "io.StringIO", "io.BytesIO", "re.Pattern", "re.Match", "file", "pathlib.Path",

                    # Async / generator / coroutine types
                    "types.GeneratorType", "types.CoroutineType", "types.AsyncGeneratorType",
                    "types.MethodType", "types.FunctionType", "types.BuiltinFunctionType",

                    # Less-known / advanced types
                    "weakref.ReferenceType", "weakref.ProxyType", "weakref.CallableProxyType",
                    "array.array", "memoryview", "bytearray",
                    "queue.Queue", "queue.PriorityQueue", "queue.LifoQueue",
                    "multiprocessing.Queue", "threading.Thread", "asyncio.Future", "asyncio.Task",

                    # Other scientific / third-party structures
                    "xarray.DataArray", "xarray.Dataset", "dask.array.Array", "dask.dataframe.DataFrame",
                    "networkx.Graph", "networkx.DiGraph", "networkx.MultiGraph", "networkx.MultiDiGraph",
                    "sympy.Symbol", "sympy.Matrix", "sympy.ImmutableMatrix", "sympy.Expression",

                    # General Python object types
                    "function", "method", "module", "object"
                ]


        exceptions = [
                    "BaseException", "Exception", "ArithmeticError", "BufferError",
                    "LookupError", "AssertionError", "AttributeError", "EOFError",
                    "FloatingPointError", "GeneratorExit", "ImportError", "ModuleNotFoundError",
                    "IndexError", "KeyError", "KeyboardInterrupt", "MemoryError",
                    "NameError", "NotImplementedError", "OSError", "OverflowError",
                    "RecursionError", "ReferenceError", "RuntimeError", "StopIteration",
                    "SyntaxError", "IndentationError", "TabError", "SystemError",
                    "TypeError", "UnboundLocalError", "UnicodeError", "ValueError",
                    "ZeroDivisionError"
                    ]

        modules = ['cat', 'plotly', 'statistics', 'subprocess', 'sklearn', 'PyTorch', 'gensim', 'tf', 'XGBoost', 'Pillow', 'lgb', 'torch', 'PIL'
            , 'BeautifulSoup', 'scrapy', 'collections', 'Pandas', 'shutil', 'json', 'kivy', 'Seaborn', 'Bokeh', 'django', 'random', 'SciPy'
            , 'PyQt', 'pyqt', 'mp', 'time', 're', 'cv2', 'pathlib', 'tk', 'argparse', 'os', 'threading', 'NumPy', 'TensorFlow', 'itertools'
            , 'decimal', 'pytest', 'Django', 'unittest', 'PySide', 'Matplotlib', 'NLTK', 'asyncio', 'requests', 'Scrapy', 'sp', 'bokeh', 'Flask'
            , 'spacy', 'pd', 'fractions', 'LightGBM', 'Statsmodels', 'nltk', 'Tkinter', 'bs4', 'flask', 'spaCy', 'CatBoost', 'functools', 'plt', 'np'
            , 'Plotly', 'pyside', 'Requests', 'sys', 'imageio', 'sm', 'pickle', 'Kivy', 'Scikit-learn', 'datetime', 'OpenCV', 'logging', 'sns', 'multiprocessing'
            , 'xgb', 'math']

        builtins = [
                    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
                    "callable", "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
                    "divmod", "enumerate", "eval", "exec", "filter", "float", "format", "frozenset",
                    "getattr", "globals", "hasattr", "hash", "help", "hex", "id", "input",
                    "int", "isinstance", "issubclass", "iter", "len", "list", "locals", "map",
                    "max", "memoryview", "min", "next", "object", "oct", "open", "ord",
                    "pow", "print", "property", "range", "repr", "reversed", "round", "set",
                    "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple",
                    "type", "vars", "zip", "__import__",

                    # توابع مجیک (Dunder Methods)
                    "__abs__", "__add__", "__and__", "__annotations__", "__bool__", "__call__", "__class__",
                    "__contains__", "__del__", "__delattr__", "__delete__", "__delitem__", "__dir__",
                    "__divmod__", "__doc__", "__eq__", "__float__", "__floor__", "__floordiv__",
                    "__format__", "__ge__", "__get__", "__getattr__", "__getattribute__", "__getitem__",
                    "__gt__", "__hash__", "__iadd__", "__iand__", "__ifloordiv__", "__ilshift__",
                    "__imatmul__", "__imod__", "__imul__", "__index__", "__init__", "__init_subclass__",
                    "__int__", "__invert__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__iter__",
                    "__itruediv__", "__ixor__", "__le__", "__len__", "__lshift__", "__lt__", "__matmul__",
                    "__mod__", "__mul__", "__ne__", "__neg__", "__or__", "__pos__", "__pow__", "__radd__",
                    "__rand__", "__rdivmod__", "__repr__", "__reversed__", "__rfloordiv__", "__rlshift__",
                    "__rmatmul__", "__rmod__", "__rmul__", "__ror__", "__round__", "__rpow__", "__rrshift__",
                    "__rshift__", "__rsub__", "__rtruediv__", "__rxor__", "__set__", "__setattr__", "__setitem__",
                    "__str__", "__sub__", "__truediv__", "__xor__", "__enter__", "__exit__",
                    "__await__", "__aiter__", "__anext__", "__aenter__", "__aexit__"
                    ]





        library_functions = []


        # ==========================
        # رنگ‌بندی‌ها
        # ==========================


        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#008000"))   # آبی تیره
        #keyword_format.setFontWeight(QFont.Bold)

        # Builtins
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#990099"))   # بنفش
        #builtin_format.setFontWeight(QFont.Bold)

        # Data types
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor("#008000"))  # سبز پررنگ
        #datatype_format.setFontItalic(True)

        # Exceptions
        exception_format = QTextCharFormat()
        exception_format.setForeground(QColor("#AA0000")) # قرمز
        #exception_format.setFontWeight(QFont.Bold)

        # Modules
        module_format = QTextCharFormat()
        module_format.setForeground(QColor("#FF6600"))    # نارنجی
        #module_format.setFontWeight(QFont.Bold)



        # Library functions (NumPy, Pandas, etc.)
        # library_function_format = QTextCharFormat()
        # library_function_format.setForeground(QColor("#990000"))  # قهوه‌ای-قرمز
        #library_function_format.setFontWeight(QFont.Bold)


        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#BA2121"))    # قهوه‌ای روشن

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#000099"))    # آبی پررنگ

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#353333"))
        comment_format.setFontItalic(True)
        comment_format.setFont(QFont("Ubuntu Mono", 13))
        


        # Structure Format
        structure_format = QTextCharFormat()
        structure_format.setForeground(QColor("#267f99"))  # آبی-سبز
        structure_format.setFontWeight(QFont.Bold)
        
        # Decorator Formats
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#AA22FF"))  # بنفش روشن
        decorator_format.setFontItalic(True)


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


        # for li in library_functions:
        #     self.rules.append((QRegExp(r"\b" + li + r"\b"), library_function_format))

        for word in structure_keywords:
            self.rules.append((QRegExp(r"\b" + word + r"\b"), structure_format))

        # ===== رشته‌ها =====
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CC6600"))  # قهوه‌ای روشن

        # الگوهای رشته‌ها (شامل تک‌خطی و چندخطی)
        self.single_quote_pattern = QRegularExpression(r"'([^'\\]|\\.)*'")
        self.double_quote_pattern = QRegularExpression(r'"([^"\\]|\\.)*"')

       
        # اضافه به rules برای حالت‌های تک‌خطی
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
        self.rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))

        # کامنت‌ها
        self.rules.append((QRegExp(r"#.*"), comment_format))

        # اعداد
        self.rules.append((QRegExp(r"\b\d+(\.\d+)?\b"), number_format))
        
        # دکوراتور 
        self.rules.append((QRegExp(r"^@\w+(\(.*\))?"), decorator_format))



    def line_index_to_offset(self, lines, line_num, char_index):
        res = sum(len(lines[i]) + 1 for i in range(line_num)) + char_index  # +1 for \n
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
                            # triple opens and closes in same line
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

        return results  # فقط بلاک‌های کامل



    # this method is Override QtGui Standard Method dont Touch This 
    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # 🔹 رنگی‌سازی رشته‌های چندخطی
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)

        if not hasattr(self, "triple_quote_ranges"):
            self.triple_quote_ranges = self.find_triple_quote_blocks()

        for start_offset, end_offset in self.triple_quote_ranges:
            if end_offset < block_start or start_offset > block_end:
                continue
            start = max(start_offset, block_start) - block_start
            end = min(end_offset, block_end) - block_start
            self.setFormat(start, end - start, self.string_format)
            
        
