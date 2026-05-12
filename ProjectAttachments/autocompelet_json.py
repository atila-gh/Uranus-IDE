import inspect
import importlib
import json
import keyword
import builtins
import pkgutil
import time      # برای محاسبه زمان


OUTPUT = "autocomplete_db.json"

# List of modules to scan
modules = [
    "numpy",
    "pandas", 
    "matplotlib.pyplot",
    "seaborn",
    "scipy",
    "sympy",
    "tkinter",
    "math",
    "random",
    "time",
    "datetime",
    "itertools",
    "functools",
    "collections",
    "os",
    "sys",
    "re",
    "json",
    "pathlib",
]

MODULE_COLORS = [
    "#87CEEB",  # blue
    "#FFA07A",  # salmon
    "#98FB98",  # green
    "#FFD700",  # gold
    "#DDA0DD",  # purple
    "#4EC9B0",  # teal
    "#F08080",  # coral
]

database = {
    "modules": {},
    "builtins": {
        "color": "#FFFFFF",
        "items": {}
    },
    "python_keywords": {
        "color": "#FF6347",
        "items": {}
    },
    "magic_methods": {
        "color": "#C586C0",
        "items": {}
    },
    "context_vars": {
        "color": "#9CDCFE",
        "items": {}
    }
}



import time
import pkgutil
import importlib

def add_library_recursive(library_name, color):
    """
    Recursively scan a package and all its submodules,
    then add them to database["modules"] using scan_module().
    Better suited for large libraries like PyQt5 / PyQt6.
    """

    print(f"\n✨ Starting recursive scan for library: {library_name}")
    start_time = time.time()

    scanned_modules = set()
    total_items_added = 0
    total_modules_scanned = 0

    try:
        root_package = importlib.import_module(library_name)
    except Exception as e:
        print(f"❌ Cannot import root library '{library_name}': {e}")
        return

    modules_to_scan = {library_name}

    # پیدا کردن تمام زیرماژول‌ها
    if hasattr(root_package, "__path__"):
        try:
            for module_info in pkgutil.walk_packages(root_package.__path__, prefix=root_package.__name__ + "."):
                modules_to_scan.add(module_info.name)
        except Exception as e:
            print(f"⚠ Error while walking submodules of {library_name}: {e}")

    print(f"📦 Total discovered modules: {len(modules_to_scan)}")

    for module_name in sorted(modules_to_scan):
        if module_name in scanned_modules:
            continue

        print(f"  🔍 Scanning: {module_name}")
        scanned_modules.add(module_name)

        try:
            items_added = scan_module(module_name, color)
            if items_added is None:
                items_added = 0
            elif not isinstance(items_added, int):
                print(f"  ⚠ scan_module returned invalid value for {module_name}: {items_added}")
                items_added = 0

            total_items_added += items_added
            total_modules_scanned += 1

        except Exception as e:
            print(f"  ⚠ Error scanning module {module_name}: {e}")

    duration = time.time() - start_time

    print(f"\n✨ Finished recursive scan for '{library_name}'")
    print(f"  Total discovered modules: {len(modules_to_scan)}")
    print(f"  Total scanned modules: {total_modules_scanned}")
    print(f"  Total items added: {total_items_added}")
    print(f"  Duration: {duration:.2f} seconds")






def clean_signature_text(text):
    """Clean and normalize function signature text"""
    if not text:
        return ""

    bad_patterns = {
        "()",
        "(self)",
        "(cls)",
        "(/, *args, **kwargs)",
        "(*args, **kwargs)",
        "(*args)",
        "(*args, **kwds)",
    }

    t = str(text).strip()

    if t in bad_patterns:
        return ""

    t = t.replace("(self, ", "(").replace("(cls, ", "(")
    t = t.replace("(self)", "()").replace("(cls)", "()")

    if t in bad_patterns:
        return ""

    return t

def get_doc(obj):
    """Get the docstring of an object"""
    try:
        doc = inspect.getdoc(obj)
        if not doc:
            return ""
        return doc.split("\n")[0].strip()
    except:
        return ""

def extract_signature(obj):
    """Extract signature using inspect module"""
    try:
        sig = inspect.signature(obj)
        return clean_signature_text(sig)
    except:
        return ""

def get_signature(obj):
    """Get cleaned signature for any object"""
    sig = extract_signature(obj)
    if sig:
        return sig

    if inspect.isclass(obj):
        try:
            sig = extract_signature(obj.__init__)
            if sig:
                return sig
        except:
            pass

        try:
            sig = extract_signature(obj.__new__)
            if sig:
                return sig
        except:
            pass

    doc = get_doc(obj)
    if doc and "(" in doc and ")" in doc:
        a = doc.find("(")
        b = doc.find(")") + 1
        candidate = clean_signature_text(doc[a:b])
        if candidate:
            return candidate

    return ""

def should_keep_item(name, sig, doc):
    """Determine if an item should be kept in the database"""
    # Skip private items (except magic methods)
    if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
        return False

    if not sig and not doc:
        return False

    return True

def scan_module(module_name, color):
    """Scan a module and extract its items"""
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        print(f"  ⚠️ Cannot import {module_name}: {e}")
        return

    items = {}
    
    for name in dir(module):
        try:
            obj = getattr(module, name)
            sig = get_signature(obj)
            doc = get_doc(obj)

            if should_keep_item(name, sig, doc):
                items[name] = {
                    "signature": sig,
                    "doc": doc,
                    "source_module": module_name
                }
        except:
            pass

    if items:
        database["modules"][module_name] = {
            "color": color,
            "items": items
        }
        print(f"  ✅ {module_name}: {len(items)} items")

# ============================================================
# 1. Add self and context variables
# ============================================================
print("\n📝 Adding context variables (self, cls, etc)...")

context_items = {
    "self": {
        "signature": "self",
        "doc": "Reference to the current instance of the class. Used in instance methods to access instance attributes and methods.",
        "source_module": "context_vars"
    },
    "cls": {
        "signature": "cls",
        "doc": "Reference to the current class. Used in class methods to access class attributes and methods.",
        "source_module": "context_vars"
    },
    "args": {
        "signature": "*args",
        "doc": "Variable-length argument list. Allows passing a variable number of positional arguments to a function.",
        "source_module": "context_vars"
    },
    "kwargs": {
        "signature": "**kwargs",
        "doc": "Variable-length keyword argument dictionary. Allows passing a variable number of keyword arguments to a function.",
        "source_module": "context_vars"
    },
    "super": {
        "signature": "super()",
        "doc": "Return a proxy object that delegates method calls to a parent or sibling class of type.",
        "source_module": "context_vars"
    },
    "property": {
        "signature": "property(fget=None, fset=None, fdel=None, doc=None)",
        "doc": "Return a property attribute. Used to define getter, setter, and deleter methods.",
        "source_module": "context_vars"
    },
    "classmethod": {
        "signature": "classmethod(function)",
        "doc": "Convert a function into a class method. The first parameter is the class itself (cls).",
        "source_module": "context_vars"
    },
    "staticmethod": {
        "signature": "staticmethod(function)",
        "doc": "Convert a function into a static method. No self or cls parameter is passed.",
        "source_module": "context_vars"
    },
    "__name__": {
        "signature": "__name__",
        "doc": "The name of the class, function, method, descriptor, or generator instance.",
        "source_module": "context_vars"
    },
    "__class__": {
        "signature": "__class__",
        "doc": "The class to which a class instance belongs.",
        "source_module": "context_vars"
    },
    "__dict__": {
        "signature": "__dict__",
        "doc": "A dictionary or other mapping object used to store an object's (writable) attributes.",
        "source_module": "context_vars"
    },
    "__doc__": {
        "signature": "__doc__",
        "doc": "The docstring of the class, function, or module.",
        "source_module": "context_vars"
    }
}

for name, data in context_items.items():
    database["context_vars"]["items"][name] = data

print(f"  ✅ Added {len(context_items)} context variables")

# ============================================================
# 2. Add magic methods
# ============================================================
print("\n✨ Adding magic methods...")

magic_methods = {
    "__init__": {
        "signature": "__init__(self, *args, **kwargs)",
        "doc": "Constructor method. Called when an instance of the class is created.",
        "source_module": "magic_methods"
    },
    "__new__": {
        "signature": "__new__(cls, *args, **kwargs)",
        "doc": "Static method that creates a new instance of the class.",
        "source_module": "magic_methods"
    },
    "__del__": {
        "signature": "__del__(self)",
        "doc": "Destructor method. Called when the instance is about to be destroyed.",
        "source_module": "magic_methods"
    },
    "__str__": {
        "signature": "__str__(self)",
        "doc": "Returns a string representation of the object. Used by str() and print().",
        "source_module": "magic_methods"
    },
    "__repr__": {
        "signature": "__repr__(self)",
        "doc": "Returns a developer-friendly string representation. Used by repr().",
        "source_module": "magic_methods"
    },
    "__len__": {
        "signature": "__len__(self)",
        "doc": "Returns the length of the container. Used by len().",
        "source_module": "magic_methods"
    },
    "__getitem__": {
        "signature": "__getitem__(self, key)",
        "doc": "Retrieves an item by key. Used for subscription (obj[key]).",
        "source_module": "magic_methods"
    },
    "__setitem__": {
        "signature": "__setitem__(self, key, value)",
        "doc": "Sets an item by key. Used for assignment (obj[key] = value).",
        "source_module": "magic_methods"
    },
    "__delitem__": {
        "signature": "__delitem__(self, key)",
        "doc": "Deletes an item by key. Used by del obj[key].",
        "source_module": "magic_methods"
    },
    "__iter__": {
        "signature": "__iter__(self)",
        "doc": "Returns an iterator object. Used by iter().",
        "source_module": "magic_methods"
    },
    "__next__": {
        "signature": "__next__(self)",
        "doc": "Returns the next item in iteration. Used by next().",
        "source_module": "magic_methods"
    },
    "__contains__": {
        "signature": "__contains__(self, item)",
        "doc": "Checks if container contains an item. Used by 'in' operator.",
        "source_module": "magic_methods"
    },
    "__call__": {
        "signature": "__call__(self, *args, **kwargs)",
        "doc": "Allows an instance to be called like a function.",
        "source_module": "magic_methods"
    },
    "__enter__": {
        "signature": "__enter__(self)",
        "doc": "Context manager method. Called when entering a 'with' block.",
        "source_module": "magic_methods"
    },
    "__exit__": {
        "signature": "__exit__(self, exc_type, exc_val, exc_tb)",
        "doc": "Context manager method. Called when exiting a 'with' block.",
        "source_module": "magic_methods"
    },
    "__eq__": {
        "signature": "__eq__(self, other)",
        "doc": "Equal operator. Used by ==.",
        "source_module": "magic_methods"
    },
    "__ne__": {
        "signature": "__ne__(self, other)",
        "doc": "Not equal operator. Used by !=.",
        "source_module": "magic_methods"
    },
    "__lt__": {
        "signature": "__lt__(self, other)",
        "doc": "Less than operator. Used by <.",
        "source_module": "magic_methods"
    },
    "__le__": {
        "signature": "__le__(self, other)",
        "doc": "Less than or equal operator. Used by <=.",
        "source_module": "magic_methods"
    },
    "__gt__": {
        "signature": "__gt__(self, other)",
        "doc": "Greater than operator. Used by >.",
        "source_module": "magic_methods"
    },
    "__ge__": {
        "signature": "__ge__(self, other)",
        "doc": "Greater than or equal operator. Used by >=.",
        "source_module": "magic_methods"
    },
    "__add__": {
        "signature": "__add__(self, other)",
        "doc": "Addition operator. Used by +.",
        "source_module": "magic_methods"
    },
    "__sub__": {
        "signature": "__sub__(self, other)",
        "doc": "Subtraction operator. Used by -.",
        "source_module": "magic_methods"
    },
    "__mul__": {
        "signature": "__mul__(self, other)",
        "doc": "Multiplication operator. Used by *.",
        "source_module": "magic_methods"
    },
    "__truediv__": {
        "signature": "__truediv__(self, other)",
        "doc": "Division operator. Used by /.",
        "source_module": "magic_methods"
    },
    "__floordiv__": {
        "signature": "__floordiv__(self, other)",
        "doc": "Floor division operator. Used by //.",
        "source_module": "magic_methods"
    },
    "__mod__": {
        "signature": "__mod__(self, other)",
        "doc": "Modulo operator. Used by %.",
        "source_module": "magic_methods"
    },
    "__pow__": {
        "signature": "__pow__(self, other)",
        "doc": "Power operator. Used by **.",
        "source_module": "magic_methods"
    },
    "__and__": {
        "signature": "__and__(self, other)",
        "doc": "Bitwise AND operator. Used by &.",
        "source_module": "magic_methods"
    },
    "__or__": {
        "signature": "__or__(self, other)",
        "doc": "Bitwise OR operator. Used by |.",
        "source_module": "magic_methods"
    },
    "__xor__": {
        "signature": "__xor__(self, other)",
        "doc": "Bitwise XOR operator. Used by ^.",
        "source_module": "magic_methods"
    },
    "__lshift__": {
        "signature": "__lshift__(self, other)",
        "doc": "Left shift operator. Used by <<.",
        "source_module": "magic_methods"
    },
    "__rshift__": {
        "signature": "__rshift__(self, other)",
        "doc": "Right shift operator. Used by >>.",
        "source_module": "magic_methods"
    },
    "__neg__": {
        "signature": "__neg__(self)",
        "doc": "Unary negation operator. Used by -obj.",
        "source_module": "magic_methods"
    },
    "__pos__": {
        "signature": "__pos__(self)",
        "doc": "Unary positive operator. Used by +obj.",
        "source_module": "magic_methods"
    },
    "__abs__": {
        "signature": "__abs__(self)",
        "doc": "Absolute value operator. Used by abs().",
        "source_module": "magic_methods"
    },
    "__invert__": {
        "signature": "__invert__(self)",
        "doc": "Bitwise NOT operator. Used by ~obj.",
        "source_module": "magic_methods"
    },
    "__format__": {
        "signature": "__format__(self, format_spec)",
        "doc": "Formats the object. Used by format().",
        "source_module": "magic_methods"
    },
    "__hash__": {
        "signature": "__hash__(self)",
        "doc": "Returns a hash value. Used by hash().",
        "source_module": "magic_methods"
    },
    "__bool__": {
        "signature": "__bool__(self)",
        "doc": "Truth value testing. Used by bool().",
        "source_module": "magic_methods"
    },
    "__dir__": {
        "signature": "__dir__(self)",
        "doc": "Returns list of attributes. Used by dir().",
        "source_module": "magic_methods"
    },
    "__getattr__": {
        "signature": "__getattr__(self, name)",
        "doc": "Called when attribute lookup fails.",
        "source_module": "magic_methods"
    },
    "__setattr__": {
        "signature": "__setattr__(self, name, value)",
        "doc": "Called when setting an attribute.",
        "source_module": "magic_methods"
    },
    "__delattr__": {
        "signature": "__delattr__(self, name)",
        "doc": "Called when deleting an attribute.",
        "source_module": "magic_methods"
    },
    "__getattribute__": {
        "signature": "__getattribute__(self, name)",
        "doc": "Called unconditionally to implement attribute access.",
        "source_module": "magic_methods"
    }
}

for name, data in magic_methods.items():
    database["magic_methods"]["items"][name] = data

print(f"  ✅ Added {len(magic_methods)} magic methods")

# ============================================================
# 3. Python keywords
# ============================================================
print("\n📝 Collecting Python keywords...")
for k in keyword.kwlist:
    database["python_keywords"]["items"][k] = {
        "signature": "",
        "doc": f"Python keyword: {k}",
        "source_module": "python_keywords"
    }
print(f"  ✅ Added {len(keyword.kwlist)} keywords")

# ============================================================
# 4. Builtins
# ============================================================
print("\n📦 Collecting Python builtins...")
builtins_count = 0
for name in dir(builtins):
    try:
        obj = getattr(builtins, name)
        
        if name.startswith("__") and name not in ["__name__", "__doc__"]:
            continue
            
        sig = get_signature(obj)
        doc = get_doc(obj)

        if should_keep_item(name, sig, doc):
            database["builtins"]["items"][name] = {
                "signature": sig,
                "doc": doc,
                "source_module": "builtins"
            }
            builtins_count += 1
    except:
        pass

print(f"  ✅ Added {builtins_count} builtins")

# ============================================================
# 5. Modules
# ============================================================
print("\n🔍 Scanning modules...")
for i, mod in enumerate(modules):
    color = MODULE_COLORS[i % len(MODULE_COLORS)]
    print(f"\n  📚 Scanning {mod}...")
    scan_module(mod, color)

# ============================================================
# Save
# ============================================================
print(f"\n💾 Saving to {OUTPUT}...")
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(database, f, indent=2, ensure_ascii=False)

# ============================================================
# Statistics
# ============================================================
print("\n" + "="*50)
print("📊 STATISTICS")
print("="*50)
print(f"  ✅ Context variables: {len(database['context_vars']['items'])}")
print(f"  ✅ Magic methods: {len(database['magic_methods']['items'])}")
print(f"  ✅ Python keywords: {len(database['python_keywords']['items'])}")
print(f"  ✅ Builtins: {len(database['builtins']['items'])}")
print(f"  ✅ Modules: {len(database['modules'])}")
total_items = (len(database['context_vars']['items']) + 
               len(database['magic_methods']['items']) + 
               len(database['python_keywords']['items']) + 
               len(database['builtins']['items']) + 
               sum(len(m['items']) for m in database['modules'].values()))
print(f"  📝 TOTAL ITEMS: {total_items}")
print(f"\n✅ Successfully saved to {OUTPUT}")

add_library_recursive("PyQt5", "#a020f0")



