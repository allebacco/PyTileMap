from PyQt4.Qt import Qt
from PyQt4.QtGui import QGraphicsView

from mapscene import MapGraphicScene
from maptilesource import MapTileSourceOSM, MapTileSourceHereDemo


class MapGraphicsView(QGraphicsView):

    _lastMousePos = None

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent=parent)
        scene = MapGraphicScene(MapTileSourceOSM())
        self.setScene(scene)

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        size = event.size()
        self.scene().setSize(size.width(), size.height())

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            event.accept()
            self._lastMousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            event.accept()
            delta = self._lastMousePos - event.pos()
            self._lastMousePos = event.pos()
            self.scene().translate(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        self._lastMousePos = None

    def wheelEvent(self, event):
        event.accept()
        if event.delta() > 0:
            self.scene().zoomIn()
        elif event.delta() < 0:
            self.scene().zoomOut()
