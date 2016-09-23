import math
from PyQt4.Qt import Qt, pyqtSlot
from PyQt4.QtCore import QRectF, QPointF
from PyQt4.QtGui import QGraphicsObject, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsSimpleTextItem, QGraphicsEllipseItem, QPen, QBrush, QColor

from .mapitems import MapItem
from .functions import getQVariantValue, makePen, makeBrush, clip



class MapScaleItem(QGraphicsObject, MapItem):

    QtParentClass = QGraphicsObject

    _defaultScaleVisualization = {
        21: 5,
        20: 10,
        19: 20,
        18: 20,
        17: 50,
        16: 100,
        15: 200,
        14: 500,
        13: 1 * 1000,
        12: 2 * 1000,
        11: 5 * 1000,
        10: 10 * 1000,
        9: 20 * 1000,
        8: 50 * 1000,
        7: 100 * 1000,
        6: 200 * 1000,
        5: 200 * 1000,
        4: 500 * 1000,
        3: 1000 * 1000,
    }
    """dict: Default meters that will be shown within the scale for each zoom value.
    """

    def __init__(self, pos=None, parent=None, earthRadius=6372.7982):
        QGraphicsObject.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._scaleView = MapScaleItem._defaultScaleVisualization.copy()
        self._minZoomScale = min(self._scaleView.keys())
        self._maxZoomScale = max(self._scaleView.keys())

        self._anchorPos = QPointF(pos) if pos is not None else QPointF(30.0, 10.0)

        self._scaleBar = QGraphicsRectItem(QRectF(0.0, 0.0, 100., 5.0), parent=self)
        self._scaleBar.setPen(makePen('black'))
        self._scaleBar.setBrush(makeBrush((190, 190, 190, 160)))

        self._textItem = QGraphicsSimpleTextItem('', parent=self._scaleBar)
        self._textItem.setPos(10., -30.)
        self._earthCircumference = 1000.0 * earthRadius * 2.0 * math.pi
        self._zoom = 0

    def itemChange(self, change, value):
        if change == self.ItemSceneChange:
            # Disconnect the old scene, if any
            oldScene = self.scene()
            if oldScene is not None:
                oldScene.sceneRectChanged.disconnect(self.setSceneRect)
            # Connect the new scene, if any
            if value is not None:
                newScene = getQVariantValue(value)
                newScene.sceneRectChanged.connect(self.setSceneRect)
                # Setup the new position of the item
                self.setSceneRect(QRectF())
        return MapItem.itemChange(self, change, value)

    def updatePosition(self, scene):
        self.setSceneRect(scene.sceneRect())

    def boundingRect(self):
        return self._scaleBar.boundingRect()

    def paint(*args, **kwargs):
        pass

    @pyqtSlot(QRectF)
    def setSceneRect(self, rect):
        self._updateScaleBar()
        bar = self._scaleBar.rect()
        self.setPos(rect.bottomRight() - self._anchorPos - bar.topRight())

    def _updateScaleBar(self):
        scene = self.scene()
        if scene is None:
            self._scaleBar.setVisible(False)
            return

        self._scaleBar.setVisible(True)

        centerCoord = scene.center()
        centerYRad = centerCoord.y() * math.pi / 180.0
        meterPerPixels = self._earthCircumference * math.cos(centerYRad)
        zoom = self._zoom
        meterPerPixels = abs(meterPerPixels / math.pow(2.0, zoom + 8))

        zoomSelector = clip(zoom, self._minZoomScale, self._maxZoomScale)
        meters = self._scaleView[zoomSelector]
        width = meters / meterPerPixels
        rect = self._scaleBar.rect()
        rect.setWidth(width)
        self._scaleBar.setRect(rect)
        if meters >= 1000:
            text = '%d km' % (meters / 1000.0)
        else:
            text = '%d km' % meters
        self._textItem.setText(text)

    def setZoom(self, zoom):
        '''Set a new zoom level.
        Args:
            zoom (int): The new zoom level.
        '''
        self._zoom = zoom
        MapItem.setZoom(self, zoom)
