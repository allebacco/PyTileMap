import numpy as np

from PyQt4.QtCore import QLineF
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPathItem, QPainterPath


class MapGraphicsEllipseItem(QGraphicsEllipseItem):

    def __init__(self, longitude, latitude, radius, scene, parent=None):
        QGraphicsEllipseItem.__init__(self, parent=parent, scene=scene)

        self._lon = longitude
        self._lat = latitude
        self._radius = radius

        self.updatePosition(scene)

    def updatePosition(self, scene):
        pos = scene.posFromLonLat(self._lon, self._lat)
        r = self._radius
        self.setRect(pos.x()-r, pos.y()-r, r, r)

    def setLonLat(self, longitude, latitude):
        self._lon = longitude
        self._lat = latitude
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)


class MapGraphicsLineItem(QGraphicsLineItem):

    def __init__(self, lon0, lat0, lon1, lat1, scene, parent=None):
        QGraphicsLineItem.__init__(self, parent=parent, scene=scene)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

        self.updatePosition(scene)

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)

        self.setLine(QLineF(pos0, pos1))

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())


class MapGraphicsPolylineItem(QGraphicsPathItem):

    def __init__(self, longitudes, latitudes, scene, parent=None):
        QGraphicsPathItem.__init__(self, parent=parent, scene=scene)

        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes)
        self._latitudes = np.array(latitudes)

    def updatePosition(self, scene):
        path = QPainterPath()

        count = len(self._longitudes)
        if count > 0:
            x, y = scene.posFromLonLat(self._longitudes, self._latitudes)
            path.moveTo(x[0], y[0])
            for i in xrange(count):
                path.lineTo(x[i], y[i])

        self.setPath(path)

    def setLonLat(self, longitudes, latitudes):
        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes)
        self._latitudes = np.array(latitudes)
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)
