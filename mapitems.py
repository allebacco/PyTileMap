from PyQt4.QtGui import QGraphicsEllipseItem


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
