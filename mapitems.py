from PyQt4.QtCore import QLineF
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsLineItem


class MapGraphicsEllipseItem(QGraphicsEllipseItem):

    _lon = None
    _lat = None
    _radius = None

    def __init__(self, longitude, latitude, radius, scene, parent=None):
        QGraphicsEllipseItem.__init__(self, parent=parent, scene=scene)

        self._lon = longitude
        self._lat = latitude
        self._radius = radius

        self.updatePosition(scene)

    def updatePosition(self, scene):
        pos = scene.posFromLatLon(self._lat, self._lon)
        r = self._radius
        self.setRect(pos.x()-r, pos.y()-r, r, r)

    def setLonLat(self, longitude, latitude):
        self._lon = longitude
        self._lat = latitude
        self.updatePosition(self.scene())


class MapGraphicsLineItem(QGraphicsLineItem):

    _lon0 = None
    _lat0 = None
    _lon1 = None
    _lat1 = None

    def __init__(self, lon0, lat0, lon1, lat1, scene, parent=None):
        QGraphicsLineItem.__init__(self, parent=parent, scene=scene)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

        self.updatePosition(scene)

    def updatePosition(self, scene):
        pos0 = scene.posFromLatLon(self._lat0, self._lon0)
        pos1 = scene.posFromLatLon(self._lat1, self._lon1)

        self.setLine(QLineF(pos0, pos1))

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())
