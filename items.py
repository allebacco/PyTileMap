from PyQt4 import Qt, QtCore, QtGui

from tile_utils import TDIM, tileForCoordinate


class TileMapItem(QtCore.QObject):

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent=parent)

    def render(self, painter, rect):
        raise NotImplementedError()

    def updatePosition(self, topLeftTile, zoom):
        raise NotImplementedError()

    def move(self, dx, dy):
        raise NotImplementedError()


class TileMapItemPoint(TileMapItem):

    def __init__(self, latitude, longitude, radius=10, parent=None):
        QtCore.QObject.__init__(self, parent=parent)

        self.latitude = latitude
        self.longitude = longitude

        self.x = 0.0
        self.y = 0.0
        self.radius = radius
        self.brush = QtGui.QBrush(Qt.Qt.black)
        self.pen = QtGui.QPen(Qt.Qt.black)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def setCoordinate(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def updatePosition(self, topLeftTile, zoom):
        pos = tileForCoordinate(self.latitude, self.longitude, zoom)
        pos *= float(TDIM)
        pos -= topLeftTile
        self.x = pos.x()
        self.y = pos.y()

    def render(self, painter, rect):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawEllipse(QtCore.QPointF(self.x, self.y), self.radius, self.radius)
