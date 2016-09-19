from __future__ import print_function, absolute_import

from PyQt4.Qt import Qt, pyqtSlot
from PyQt4.QtCore import QRectF, QPointF
from PyQt4.QtGui import QGraphicsObject, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsSimpleTextItem, QGraphicsEllipseItem, QPen, QBrush, QColor

from .mapitems import MapItem
from .functions import getQVariantValue


class MapLegendEntryItem(QGraphicsItemGroup):

    def __init__(self, shape, text, parent=None):
        QGraphicsItemGroup.__init__(self, parent=parent)

        text = QGraphicsSimpleTextItem(text, parent=shape)
        br = shape.boundingRect()
        x = br.right() + 10
        y = br.top() + 3
        text.setPos(x, y)
        self.addToGroup(shape)

        self._text = text

    def top(self):
        return self.boundingRect().top()

    def bottom(self):
        return self.boundingRect().bottom()

    def right(self):
        return self.boundingRect().right()

    def left(self):
        return self.boundingRect().left()

    def text(self):
        return self._text


class MapLegendItem(QGraphicsObject, MapItem):

    QtParentClass = QGraphicsObject

    def __init__(self, pos=None, parent=None):
        QGraphicsObject.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._anchorPos = QPointF(pos) if pos is not None else QPointF(10.0, 10.0)

        self._border = QGraphicsRectItem(parent=self)
        self._border.setPen(QPen(Qt.NoPen))
        self._border.setBrush(QBrush(QColor(190, 190, 190, 160)))
        self._border.setZValue(-100.0)

        self._entries = list()
        self._entriesGroup = QGraphicsItemGroup(parent=self)

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
        pass

    def addPoint(self, text, pen=None, color=None, size=20.0):
        if pen is None and color is None:
            raise ValueError("`pen` and `color` can't be both None")

        shape = QGraphicsEllipseItem(size / 2.0, size / 2.0, size, size)
        if color is not None:
            shape.setBrush(QBrush(color))
        if pen is not None:
            shape.setPen(QPen(pen))

        entry = MapLegendEntryItem(shape, text)
        self.addEntry(entry)

    def addRect(self, text, pen=None, color=None, size=20.0):
        if pen is None and color is None:
            raise ValueError("`pen` and `color` can't be both None")

        shape = QGraphicsRectItem(size / 2.0, size / 2.0, size, size)
        if color is not None:
            shape.setBrush(QBrush(color))
        if pen is not None:
            shape.setPen(QPen(pen))

        entry = MapLegendEntryItem(shape, text)
        self.addEntry(entry)

    def addEntry(self, entry):
        self._entries.append(entry)
        self._entriesGroup.addToGroup(entry)
        self._updateLayout()

    def boundingRect(self):
        return self._border.boundingRect()

    def paint(*args, **kwargs):
        pass

    @pyqtSlot(QRectF)
    def setSceneRect(self, rect):
        self.setPos(rect.topLeft() + self._anchorPos)

    def _updateLayout(self):
        self.prepareGeometryChange()

        bottom = 0.0
        left = 0.0
        right = 0.0
        for entry in self._entries:
            entry.setPos(left, bottom)
            bottom += entry.bottom() + 5.0
            right = max(right, entry.right() + 5.0)

        self._border.setRect(0.0, 0.0, right, bottom + 5.0)

