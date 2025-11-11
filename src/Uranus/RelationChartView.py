from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QRectF
from graphviz import Digraph
import sys

class RelationChartView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.load_graph()

    def load_graph(self):
        # ساخت گراف با Graphviz
        dot = Digraph()
        dot.node('A', 'Main Box', shape='box', style='filled', fillcolor='#88c')
        dot.node('B', 'Target 1', shape='box', style='filled', fillcolor='#c88')
        dot.node('C', 'Target 2', shape='box', style='filled', fillcolor='#8c8')
        dot.node('D', 'Target 3', shape='box', style='filled', fillcolor='#cc8')
        dot.edge('A', 'B')
        dot.edge('A', 'C')
        dot.edge('A', 'D')

        # دریافت خروجی SVG به‌صورت bytes
        svg_bytes = dot.pipe(format='svg')
        renderer = QSvgRenderer(svg_bytes)
        svg_item = QGraphicsSvgItem()
        svg_item.setSharedRenderer(renderer)

        # قرار دادن SVG در مرکز صحنه
        bounds = svg_item.boundingRect()
        svg_item.setPos(-bounds.width() / 2, -bounds.height() / 2)

        self.scene.clear()
        self.scene.addItem(svg_item)

        # تنظیم sceneRect بزرگ‌تر از SVG برای pan کامل
        margin = 1000
        self.scene.setSceneRect(QRectF(-margin, -margin, 2 * margin, 2 * margin))

        # مرکز کردن view روی SVG
        self.centerOn(0, 0)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = RelationChartView()
    view.setWindowTitle("Graphviz Viewer with Pan & Zoom")
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())