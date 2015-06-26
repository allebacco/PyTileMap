from PyQt4 import Qt, QtCore, QtGui

from tile_utils import TDIM, tileForCoordinate


class TileMapItem(QtCore.QObject):

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self._boundingRect = None

    def render(self, painter, rect):
        raise NotImplementedError()

    def updatePosition(self, topLeftTile, zoom):
        raise NotImplementedError()

    def move(self, dx, dy):
        raise NotImplementedError()

    def boundingRect(self):
        return self._boundingRect


class TileMapItemPoint(TileMapItem):

    def __init__(self, latitude, longitude, parent=None):
        QtCore.QObject.__init__(self, parent=parent)

        self.latitude = latitude
        self.longitude = longitude

        self.x = 0.0
        self.y = 0.0
        self.radius = 10
        self.brush = QtGui.QBrush(Qt.Qt.black)
        self.pen = QtGui.QPen(Qt.Qt.black)
        self._boundingRect = QtCore.QRect(0, 0, self.radius, self.radius)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self._boundingRect.moveCenter(QtCore.QPoint(self.x, self.y))

    def setCoordinate(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def updatePosition(self, topLeftTile, zoom):
        pos = tileForCoordinate(self.latitude, self.longitude, zoom)
        pos *= float(TDIM)
        pos -= topLeftTile
        self.x = pos.x()
        self.y = pos.y()
        self._boundingRect.moveCenter(QtCore.QPoint(self.x, self.y))

    def setRadius(self, r):
        self.radius = r
        self._boundingRect = QtCore.QRect(0, 0, self.radius, self.radius)
        self._boundingRect.moveCenter(QtCore.QPoint(self.x, self.y))

    def render(self, painter, rect):
        if rect.intersects(self._boundingRect):
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            painter.drawEllipse(QtCore.QPointF(self.x, self.y), self.radius, self.radius)


class TileMapItemLine(TileMapItem):

    def __init__(self, latitude1, longitude1, latitude2, longitude2, parent=None):
        QtCore.QObject.__init__(self, parent=parent)

        self.latitude1 = latitude1
        self.longitude1 = longitude1
        self.latitude2 = latitude2
        self.longitude2 = longitude2

        self.p1 = QtCore.QPointF(0.0, 0.0)
        self.p2 = QtCore.QPointF(0.0, 0.0)
        self.brush = QtGui.QBrush(Qt.Qt.black)
        self.pen = QtGui.QPen(Qt.Qt.black)
        self.pen.setWidth(5)

    def move(self, dx, dy):
        d = QtCore.QPointF(dx, dy)
        self.p1 += d
        self.p2 += d
        self._boundingRect.translate(dx, dy)

    def setCoordinate(self, latitude1, longitude1, latitude2, longitude2):
        self.latitude1 = latitude1
        self.longitude1 = longitude1
        self.latitude2 = latitude2
        self.longitude2 = longitude2

    def updatePosition(self, topLeftTile, zoom):
        pos = tileForCoordinate(self.latitude1, self.longitude1, zoom) * float(TDIM)
        pos -= topLeftTile
        self.p1 = pos
        pos = tileForCoordinate(self.latitude2, self.longitude2, zoom) * float(TDIM)
        pos -= topLeftTile
        self.p2 = pos
        self._boundingRect = QtCore.QRect(self.p1.toPoint(), self.p2.toPoint()).normalized()

    def render(self, painter, rect):
        if rect.intersects(self._boundingRect):
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            painter.drawLine(self.p1, self.p2)
