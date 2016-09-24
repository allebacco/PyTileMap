import numpy as np
from PyQt4.Qt import Qt, pyqtSlot
from PyQt4.QtCore import QRectF, QPointF
from PyQt4.QtGui import QGraphicsObject, QFontMetrics, QFont

from .mapitems import MapItem
from .functions import getQVariantValue, makePen, makeBrush, clip


class MapScaleItem(QGraphicsObject, MapItem):
    """Scale bar for the visualization of the scale of teh map.

    The scale bar is located on the bottom right of the map and can' be moved.
    The scale bar accepts hover events and change its color.
    """

    QtParentClass = QGraphicsObject

    EarthCircumference = 1000.0 * 6372.7982 * 2.0 * np.pi
    DegToRad = np.pi / 180.0

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

    def __init__(self, textPen='black', barBrush=(190, 190, 190, 160), barPen=(190, 190, 190, 240),
                 barBrushHover=(110, 110, 110, 255), barPenHover=(90, 90, 90, 255), parent=None):
        """Construct a scale bar with text on the right bottom of the map

        Keyword Args:
            textPen: QPen to use for drawing the text. Default 'black'.
            barBrush: QBrush to use for drawing the scale bar. Default (190, 190, 190, 160)
            barPen: QPen to use for drawing the scale bar border. Default (190, 190, 190, 240) 
            barBrushHover:  QBrush to use for drawing the scale bar when the mouse is over it.
                Default (110, 110, 110, 255).
            barPenHover: QPen to use for drawing the scale bar borderwhen the mouse is over it.
                Default (90, 90, 90, 255).

        Note:
            Almost all the argumnets accepted by the functions.makeBrush() and functions.makePen()
            are accepted.
        """
        QGraphicsObject.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._textPen = makePen(textPen)
        self._barBrush = makeBrush(barBrush)
        self._barPen = makePen(barPen)
        self._barBrushHover = makeBrush(barBrushHover)
        self._barPenHover = makePen(barPenHover)

        self._scaleView = MapScaleItem._defaultScaleVisualization.copy()
        self._minZoomScale = min(self._scaleView.keys())
        self._maxZoomScale = max(self._scaleView.keys())

        self.setAcceptHoverEvents(True)
        self._hover = False

        self._anchorPos = QPointF(30.0, 15.0)

        self._barWidth = 0  # The width of the scale bar
        self._text = ''  # The text to display near the scale bar
        self._zoom = 0  # The current zoom level
        self._meters = 0  # The number of meters used to evaluate the size of the scale bar and its text
        self._meterPerPixelsEquator = 0  # The number of meters each pixel represents at the equator
        self._textRect = QRectF()  # The bounding rect of text

    def itemChange(self, change, value):
        if change == self.ItemSceneChange:
            # Disconnect the old scene, if any
            oldScene = self.scene()
            if oldScene is not None:
                oldScene.sceneRectChanged.disconnect(self._setSceneRect)
            # Connect the new scene, if any
            if value is not None:
                newScene = getQVariantValue(value)
                newScene.sceneRectChanged.connect(self._setSceneRect)
                self.setZoom(newScene.zoom())
                # Setup the new position of the item
                self._setSceneRect(newScene.sceneRect())
        return MapItem.itemChange(self, change, value)

    def updatePosition(self, scene):
        # Nothing to do here
        pass

    def boundingRect(self):
        return QRectF(0, 0, self._barWidth, 10).united(self._textRect)

    def paint(self, painter, option, widget):
        if self._hover:
            painter.setPen(self._barPenHover)
            painter.setBrush(self._barBrushHover)
        else:
            painter.setPen(self._barPen)
            painter.setBrush(self._barBrush)
        painter.drawRoundedRect(0, 0, self._barWidth, 10, 3, 3)

        painter.setPen(self._textPen)
        painter.drawText(self._textRect, Qt.TextSingleLine, self._text)

    @pyqtSlot(QRectF)
    def _setSceneRect(self, rect):
        self._updateScaleBar()
        self.setPos(rect.bottomRight() - self._anchorPos - QPointF(self._barWidth, 0.0))

    def _updateScaleBar(self):
        scene = self.scene()
        if scene is None:
            self.setVisible(False)
            return
        self.setVisible(True)

        centerYRad = scene.center().y() * self.DegToRad
        meterPerPixels = self._meterPerPixelsEquator * np.cos(centerYRad)
        self._barWidth = int(self._meters / meterPerPixels)

    def setZoom(self, zoom):
        '''Set a new zoom level.
        Args:
            zoom (int): The new zoom level.
        '''
        self._zoom = zoom
        zoomSelector = clip(zoom, self._minZoomScale, self._maxZoomScale)
        meters = self._scaleView[zoomSelector]
        if meters >= 1000:
            self._text = '%d km' % (meters / 1000.0)
        else:
            self._text = '%d m' % meters
        self._meters = meters
        self._meterPerPixelsEquator = self.EarthCircumference / np.power(2.0, zoom + 8)

        # Evaluate the bounding box of the current text
        textRect = QFontMetrics(QFont()).boundingRect(self._text)
        textRect.moveLeft(-textRect.width() - 10)
        textRect.moveTop(-textRect.height() + 10)
        self._textRect = QRectF(textRect)

    def setScaleForZoom(self, zoomLevel, metersInScaleBar):
        """Set the scale in meters/kilometers to be shown for a zoom level

        Args:
            zoomLevel(int): Level of the zoom
            metersInScaleBar(int): Meters to be shown in the scale bar
        """
        if zoomLevel > self._maxZoomScale + 1:
            raise ValueError('zoomLevel must be at least %d' % (self._maxZoomScale + 1))
        if zoomLevel < self._minZoomScale - 1:
            raise ValueError('zoomLevel must be at minimum %d' % (self._minZoomScale + 1))

        self._scaleView[zoomLevel] = metersInScaleBar
        self._minZoomScale = min(self._scaleView.keys())
        self._maxZoomScale = max(self._scaleView.keys())

        # Re-evaluate the scale bar for the current zoom
        self.setZoom(self._zoom)

        self.update()

    def restoreDefaultScaleLevels(self):
        """Restore the default meter scale for the zoom levels
        """
        self._scaleView = MapScaleItem._defaultScaleVisualization.copy()
        self._minZoomScale = min(self._scaleView.keys())
        self._maxZoomScale = max(self._scaleView.keys())

        # Re-evaluate the scale bar for the current zoom
        self.setZoom(self._zoom)

        self.update()

    def setColors(self, **kwargs):
        """Set a new color for the scale bar and the text

        Keyword Args:
            textPen: QPen to use for drawing the text. Default do not change.
            barBrush: QBrush to use for drawing the scale bar. Default do not change.
            barPen: QPen to use for drawing the scale bar border.Default do not change.
            barBrushHover:  QBrush to use for drawing the scale bar when the mouse is over it.
                Default do not change.
            barPenHover: QPen to use for drawing the scale bar borderwhen the mouse is over it.
                Default do not change.
        """
        if 'textPen' in kwargs:
            self._textPen = makePen(kwargs['textPen'])
        if 'barBrush' in kwargs:
            self._barBrush = makeBrush(kwargs['barBrush'])
        if 'barPen' in kwargs:
            self._barPen = makePen(kwargs['barPen'])
        if 'barBrushHover' in kwargs:
            self._barBrushHover = makeBrush(kwargs['barBrushHover'])
        if 'barPenHover' in kwargs:
            self._barPenHover = makePen(kwargs['barPenHover'])
        self.update()

    def hoverEnterEvent(self, event):
        event.accept()
        self._hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        event.accept()
        self._hover = False
        self.update()
