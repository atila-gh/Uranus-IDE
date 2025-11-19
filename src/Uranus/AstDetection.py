from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRectF
from graphviz import Digraph
import ast


CLASS_PALETTE = [
    "#FF8C00", "#1E90FF", "#32CD32", "#8A2BE2", "#DC143C",
    "#20B2AA", "#FF1493", "#A0522D", "#2F4F4F", "#FFD700"
]
FUNC_PALETTE = [
    "#2ECC71", "#3498DB", "#9B59B6", "#E67E22", "#E74C3C",
    "#16A085", "#F1C40F", "#7F8C8D"
]

class CodeAnalyzer:
    """
    A static-code analysis utility that inspects Python source code using the AST module
    and extracts structural information about variables, functions, classes, methods,
    and their interactions.

    This analyzer identifies:
      • Root-level variables
      • Functions and their local variables
      • Classes, including:
            - Parent classes
            - Class-level variables
            - Instance variables
            - Methods and their local variables
            - Cross-class references and method/instance usages

    The collected data is normalized into a rich dictionary structure and is intended
    for consumption by visualization or documentation tools.

    Parameters
    ----------
    code : str
        Raw Python source code to be analyzed.

    Attributes
    ----------
    code : str
        The original source code.
    tree : ast.AST
        Parsed AST tree of the input code.
    root_vars : list
        List of variable names defined at module root level.
    functions : dict
        Mapping of function_name → list of 'function.local_variable'.
    classes : dict
        Mapping of class_name → metadata extracted from class body.
    res : dict
        Final aggregated analysis result containing: root_vars, functions, classes.
    """
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)
        self.root_vars = []
        self.functions = {}
        self.classes = {}
        self.res = self.analyze()
        
       

    def analyze(self):
        defined_classes = set()

        for node in self.tree.body:
            # --- Root variables ---
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.root_vars.append(target.id)

            # --- Functions ---
            elif isinstance(node, ast.FunctionDef):
                func_name = node.name
                self.functions[func_name] = []
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name):
                                self.functions[func_name].append(f"{func_name}.{target.id}")

            # --- Classes ---
            elif isinstance(node, ast.ClassDef):
                cls_name = node.name
                defined_classes.add(cls_name)
                bases = [ast.unparse(b) for b in node.bases]
                self.classes[cls_name] = {
                    "parents": bases,
                    "class_vars": [],
                    "instance_vars": [],
                    "methods": {},
                    "connections": []
                }
                for item in node.body:
                    # class-level vars
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                self.classes[cls_name]["class_vars"].append(f"{cls_name}.{target.id}")

                    # methods
                    elif isinstance(item, ast.FunctionDef):
                        method_name = f"{cls_name}.{item.name}"
                        self.classes[cls_name]["methods"][method_name] = {
                            "locals": []
                        }
                        for stmt in ast.walk(item):
                            # instance vars
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                        self.classes[cls_name]["instance_vars"].append(f"{method_name}.self.{target.attr}")
                                    elif isinstance(target, ast.Name):
                                        self.classes[cls_name]["methods"][method_name]["locals"].append(f"{method_name}.{target.id}")

                            # --- تشخیص ارتباطات ---
                            if isinstance(stmt, ast.Call):
                                # فراخوانی متد یا ساخت اینستنس
                                if isinstance(stmt.func, ast.Attribute) and isinstance(stmt.func.value, ast.Name):
                                    other_cls = stmt.func.value.id
                                    self.classes[cls_name]["connections"].append(f"{other_cls}.Method:{stmt.func.attr}")
                                elif isinstance(stmt.func, ast.Name):
                                    other_cls = stmt.func.id
                                    if other_cls in defined_classes:
                                        self.classes[cls_name]["connections"].append(f"{other_cls}.Instance:{other_cls}")
                            elif isinstance(stmt, ast.Attribute):
                                if isinstance(stmt.value, ast.Name):
                                    other_cls = stmt.value.id
                                    if other_cls in defined_classes and other_cls != cls_name:
                                        self.classes[cls_name]["connections"].append(f"{other_cls}.CVar:{stmt.attr}")

        # --- اضافه کردن کلاس‌های والد ناشناخته ---
        for cls_name, cls_info in list(self.classes.items()):
            for parent in cls_info["parents"]:
                if parent not in defined_classes:
                    imported_name = f"{parent}.import"
                    if imported_name not in self.classes:
                        self.classes[imported_name] = {
                            "parents": [],
                            "class_vars": [],
                            "instance_vars": [],
                            "methods": {},
                            "connections": []
                        }
                        

        return {
            "root_vars": self.root_vars,
            "functions": self.functions,
            "classes": self.classes
        }



class RelationChartView(QGraphicsView):
    """
    A PyQt-based graphical viewer that visualizes relationships between classes,
    functions, variables, and method interactions extracted from Python source code.

    Internally, Graphviz is used to generate an SVG diagram representing:
        • Classes and inherited parents
        • Class variables and instance variables
        • Methods and their local variables
        • Function-level variables
        • Cross-class connections (method calls, attribute access, instantiations)
        • Imported or external parent classes

    The generated SVG graph is rendered inside a QGraphicsScene and supports
    interactive navigation such as:
        • Mouse-wheel zooming
        • Drag-to-pan
        • Auto-centering

    Parameters
    ----------
    code : str, optional
        Python code whose structure will be analyzed and visualized.
    parent : QWidget, optional
        Parent widget for the QGraphicsView.

    Attributes
    ----------
    code : str
        Provided source code to be visualized.
    scene : QGraphicsScene
        The scene containing the SVG graph.
    astdetect : CodeAnalyzer
        Analyzer instance used to extract code structure.
    context : dict
        Parsed analysis result containing functions, classes, variables.
    """
    def __init__(self, code=None, parent=None):
        super().__init__(parent)
        if not code:
            return

        self.code = code
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        
        self.astdetect = CodeAnalyzer(self.code)
        self.context = self.astdetect.res

        self.load_graph()

    def normalize_classes(self, classes_dict):
        """
        Merge imported-parent placeholder classes into their real class names
        and unify class metadata.

        This method resolves duplicates created for imported parents,
        removes suffixes such as '.import', merges attributes, methods, variables,
        and ensures uniqueness of lists.

        Parameters
        ----------
        classes_dict : dict
            Raw class metadata extracted by CodeAnalyzer.

        Returns
        -------
        dict
            Normalized class metadata indexed by clean class names.
        """
        normalized = {}
        for cls_name, info in classes_dict.items():
            base_name = cls_name.replace(".import", "")
            if base_name not in normalized:
                normalized[base_name] = {
                    "parents": list(info.get("parents", [])),
                    "class_vars": list(info.get("class_vars", [])),
                    "instance_vars": list(info.get("instance_vars", [])),
                    "methods": dict(info.get("methods", {})),
                    "connections": list(info.get("connections", [])),
                    "imported": cls_name.endswith(".import") or info.get("imported", False)
                }
            else:
                normalized[base_name]["parents"] += info.get("parents", [])
                normalized[base_name]["class_vars"] += info.get("class_vars", [])
                normalized[base_name]["instance_vars"] += info.get("instance_vars", [])
                normalized[base_name]["connections"] += info.get("connections", [])
                normalized[base_name]["methods"].update(info.get("methods", {}))
                normalized[base_name]["imported"] = (
                    normalized[base_name]["imported"]
                    or cls_name.endswith(".import")
                    or info.get("imported", False)
                )
        for k, v in normalized.items():
            v["parents"] = list(dict.fromkeys(v["parents"]))
            v["class_vars"] = list(dict.fromkeys(v["class_vars"]))
            v["instance_vars"] = list(dict.fromkeys(v["instance_vars"]))
            v["connections"] = list(dict.fromkeys(v["connections"]))
        return normalized

    def assign_colors(self, keys, palette):
        """
        Assign deterministic colors to keys based on a given palette.

        Parameters
        ----------
        keys : iterable
            Names of classes or functions.
        palette : list
            List of color hex strings.

        Returns
        -------
        dict
            Mapping of key → color.
        """
        color_map = {}
        for i, k in enumerate(sorted(keys)):
            color_map[k] = palette[i % len(palette)]
        return color_map

    def load_graph(self):
        """
        Build the Graphviz graph for all detected code entities, render it
        into SVG, and display it in the QGraphicsScene.

        This includes:
            • Root variables
            • Functions and their locals
            • Classes, variables, instance vars, and methods
            • Inheritance edges
            • Cross-class call/attribute relationships

        The final SVG is centered and scaled inside the view.
        """
        dot = Digraph(format="svg")
        classes = self.normalize_classes(self.context.get("classes", {}))
        class_color = self.assign_colors(classes.keys(), CLASS_PALETTE)
        functions = self.context.get("functions", {})
        func_color = self.assign_colors(functions.keys(), FUNC_PALETTE)

        # Root vars
        for rv in self.context.get("root_vars", []):
            dot.node(rv, rv, shape="hexagon", style="filled", color="lightblue")

        # Functions
        for func, locals in functions.items():
            fc = func_color[func]
            dot.node(func, func, shape="ellipse", style="filled", color=fc)
            for lv in locals:
                var_name = lv.split(".")[-1]
                node_id = f"{func}_local_{var_name}"
                dot.node(node_id, var_name, shape="ellipse", style="filled", color=fc)
                dot.edge(func, node_id)

        # Classes
        for cls, info in classes.items():
            base_color = "grey" if info.get("imported", False) else class_color[cls]
            dot.node(cls, cls, shape="box", style="filled", color=base_color)

            for parent in info["parents"]:
                dot.edge(cls, parent.replace(".import", ""))

            for cv in info["class_vars"]:
                var_name = cv.split(".")[-1]
                node_id = f"{cls}_cvar_{var_name}"
                dot.node(node_id, var_name, shape="diamond", style="filled", color=base_color)
                dot.edge(cls, node_id)

            for iv in info["instance_vars"]:
                var_name = iv.split(".")[-1]
                node_id = f"{cls}_ivar_{var_name}"
                dot.node(node_id, var_name, shape="parallelogram", style="filled", color=base_color)
                dot.edge(cls, node_id)

            for m, m_info in info["methods"].items():
                method_name = m.split(".")[-1]
                m_id = f"{cls}_method_{method_name}"
                dot.node(m_id, method_name, shape="ellipse", style="filled", color=base_color)
                dot.edge(cls, m_id)
                for lv in m_info.get("locals", []):
                    var_name = lv.split(".")[-1]
                    lv_id = f"{m_id}_local_{var_name}"
                    dot.node(lv_id, var_name, shape="hexagon", style="filled", color=base_color)
                    dot.edge(m_id, lv_id)

            for conn in info["connections"]:
                target_cls = conn.split('.')[0].replace(".import", "")
                dot.edge(cls, target_cls)

        # Legend سبک matplotlib
        # with dot.subgraph(name="cluster_legend") as legend:
        #     legend.attr(label="Legend", fontsize="true", style="dashed", rankdir="TB")

        #     items = [
        #         ("legend_class", "Class", "box", "orange"),
        #         ("legend_cvar", "ClassVar", "diamond", "orange"),
        #         ("legend_ivar", "InstanceVar", "parallelogram", "orange"),
        #         ("legend_method", "Method", "ellipse", "orange"),
        #         ("legend_local", "LocalVar", "hexagon", "orange"),
        #         ("legend_func", "Function", "ellipse", "green"),
        #         ("legend_root", "RootVar", "hexagon", "lightblue"),
        #         ("legend_imported", "Imported", "box", "grey")
        #     ]

        #     prev = None
        #     for node_id, label, shape, color in items:
        #         legend.node(node_id, label, shape=shape, style="filled", color=color,
        #                     width="0.1", height="0.1" )
        #         if prev:
        #             legend.edge(prev, node_id, style="invis")  # یال نامرئی برای چینش عمودی
        #         prev = node_id

        # دریافت خروجی SVG و نمایش
        svg_bytes = dot.pipe(format='svg')
        renderer = QSvgRenderer(svg_bytes)
        svg_item = QGraphicsSvgItem()
        svg_item.setSharedRenderer(renderer)

        bounds = svg_item.boundingRect()
        svg_item.setPos(-bounds.width() / 2, -bounds.height() / 2)

        self.scene.clear()
        self.scene.addItem(svg_item)
        margin = 1000
        self.scene.setSceneRect(QRectF(-margin, -margin, 2 * margin, 2 * margin))
        self.centerOn(0, 0)

    def wheelEvent(self, event):
        """
        Handle mouse-wheel zooming for the diagram.

        Parameters
        ----------
        event : QWheelEvent
            Wheel event containing zoom direction.
        """
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)



        
        
# from PyQt5.QtWidgets import QApplication, QMainWindow


# sample_code = '''
# class A:
#     def foo(self):
#         B.data
#         C()
#         B.method()

# class B(A,C):
#     data = []
#     def bar(self):
#         a = A()
#         A.x
#         A.foo()
# '''

# app = QApplication([])
# window = QMainWindow()
# chart = RelationChartView(code=sample_code)
# window.setCentralWidget(chart)
# window.resize(1000, 800)
# window.show()
# app.exec_()

