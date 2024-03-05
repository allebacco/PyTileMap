from __future__ import print_function, absolute_import

import os
from qtpy.QtCore import Qt, Slot, QRectF, QPointF, QObject, Signal
from qtpy.QtGui import QPen, QBrush, QColor, QPixmap
from qtpy.QtWidgets import QGraphicsObject, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsSimpleTextItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPixmapItem

from .imagebutton import ImageButton
from .mapitems import MapItem
from .functions import makePen, makeBrush
from .qtsupport import getQVariantValue

from .maplegenditem import *


class MapNavItem(QGraphicsObject, MapItem):

    QtParentClass = QGraphicsObject

    _posForAnchors = {
        Qt.TopLeftCorner: QPointF(20.0, 75.0),
        Qt.TopRightCorner: QPointF(40.0, -15.0),
        Qt.BottomLeftCorner: QPointF(20.0, -15.0),
        Qt.BottomRightCorner: QPointF(30.0, 75.0),
    }


    def __init__(self, anchor, parent=None):
        QGraphicsObject.__init__(self, parent=parent)
        MapItem.__init__(self)
        self.setZValue(200.0)

        anchorPos = self._posForAnchors[anchor]
        self._anchorPos = QPointF(anchorPos)
        self._anchor = anchor

        self._border = QGraphicsRectItem(parent=self)
        self._border.setPen(QPen(Qt.NoPen))
        self._border.setBrush(QBrush(QColor(190, 190, 190, 160)))

        self._entries = list()

        imgfile = os.path.dirname(__file__) + os.sep + 'zoom_in_symbol.png'
        img = QPixmap(24,24)
        img.load(imgfile)
        img = img.scaled(24,24) 
        img = ImageButton(img, parent=self)
        self.zoom_in_button = img
        self.addEntry(self.zoom_in_button)

        imgfile = os.path.dirname(__file__) + os.sep + 'zoom_out_symbol.png'
        img2 = QPixmap(24,24)
        img2.load(imgfile)
        img2 = img2.scaled(24,24) 
        img2 = ImageButton(img2, parent=self)
        self.zoom_out_button = img2
        self.addEntry(self.zoom_out_button)

    def _sceneChanged(self, oldScene, newScene):
        if oldScene is not None:
            oldScene.sceneRectChanged.disconnect(self.setSceneRect)
        if newScene is not None:
            newScene.sceneRectChanged.connect(self.setSceneRect)
            # Setup the new position of the item
            self.setSceneRect(newScene.sceneRect())

    def updatePosition(self, scene):
        pass

    def addRect(self, text, color, border=None, size=20.0):
        shape = QGraphicsRectItem(size / 2.0, size / 2.0, size, size)
        brush = makeBrush(color)
        shape.setBrush(brush)
        shape.setPen(makePen(border))

        self.addEntry(MapLegendEntryItem(shape, text))

    def addEntry(self, entry):
        self._entries.append(entry)
        self._updateLayout()

    def boundingRect(self):
        return self._border.boundingRect()

    def paint(*args, **kwargs):
        pass

    @Slot(QRectF)
    def setSceneRect(self, rect):
        anchorPos = self._anchorPos
        anchor = self._anchor
        newPos = None
        if anchor == Qt.BottomRightCorner:
            newPos = rect.bottomRight() - anchorPos
        elif anchor == Qt.TopRightCorner:
            newPos = rect.topRight() - anchorPos
        elif anchor == Qt.TopLeftCorner:
            newPos = rect.topLeft() + anchorPos
        elif anchor == Qt.BottomLeftCorner:
            newPos = rect.bottomLeft() + anchorPos
        else:
            raise NotImplementedError('Other corner have not actually been implemented')

        self.setPos(newPos)


    def _updateLayout(self):
        self.prepareGeometryChange()

        bottom = 0.0
        left = 0.0
        right = 0.0
        for entry in self._entries:
            entry.setPos(left, bottom)
            bottom += entry.boundingRect().bottom()
            right = max(right, entry.boundingRect().right() + 1.0)

        self._border.setRect(0.0, 0.0, right, bottom + 1.0)

    def pen(self):
        """Pen for the background of the legend

        Returns:
            QPen: Pen for the background of the legend
        """
        return self._border.pen()

    def brush(self):
        """Brush for the background of the legend

        Returns:
            QBrush: Brush for the background of the legend
        """
        return self._border.brush()

    def setPen(self, *args, **kwargs):
        """Set the pen for the background of the legend

        The arguments are the same of the :func:`makePen` function
        """
        return self._border.setPen(makePen(*args, **kwargs))

    def setBrush(self, *args, **kwargs):
        """Set the brush for the background of the legend

        The arguments are the same of the :func:`makeBrush` function
        """
        return self._border.setBrush(makeBrush(*args, **kwargs))

