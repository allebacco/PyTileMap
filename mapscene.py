from math import log as m_log
from math import tan as m_tan
from math import pi as m_PI
from math import cos as m_cos
from math import atan as m_atan
from math import exp as m_exp
from math import floor as m_floor

from PyQt4 import Qt, QtCore, QtGui

from mapitems import MapGraphicsEllipseItem


TDIM = 256
MIN_ZOOM = 2
MAX_ZOOM = 18


def qHash(point):
    '''Qt doesn't implement a qHash() for QPoint.'''
    return (point.x(), point.y())


class MapGraphicScene(QtGui.QGraphicsScene):

    _tileSource = None

    def __init__(self, tileSource, parent=None):
        QtCore.QObject.__init__(self)
        self._zoom = 15

        self._tileSource = tileSource
        self._tileSource.setParent(self)
        self._tileSource.tileReceived.connect(self.setTilePixmap)

        self._emptyTile = QtGui.QPixmap(TDIM, TDIM)
        self._emptyTile.fill(QtCore.Qt.lightGray)

        self._tilesRect = QtCore.QRect()
        self._tilePixmaps = {}

        self._tileInDownload = list()

        self.setSceneRect(0.0, 0.0, 400, 300)
        self.sceneRectChanged.connect(self.onSceneRectChanged)

    def onSceneRectChanged(self, rect):
        center = rect.center()
        ct = self.tileFromPos(center.x(), center.y())
        tx = ct.x()
        ty = ct.y()

        width = rect.width()
        height = rect.height()
        # top left corner of the center tile
        xp = int(width / 2.0 - (tx - m_floor(tx)) * TDIM)
        yp = int(height / 2.0 - (ty - m_floor(ty)) * TDIM)

        # first tile vertical and horizontal
        xa = (xp + TDIM - 1) / TDIM
        ya = (yp + TDIM - 1) / TDIM
        xs = tx - xa
        ys = ty - ya

        # last tile vertical and horizontal
        xe = tx + (width - xp - 1) / TDIM
        ye = ty + (height - yp - 1) / TDIM

        # build a rect
        self._tilesRect = QtCore.QRect(xs-1, ys-1, xe - xs + 2, ye - ys + 2)

        self.requestTiles()

        self.update()

    def drawBackground(self, painter, rect):
        tilesRect = self._tilesRect
        numXtiles = tilesRect.width()+1
        numYtiles = tilesRect.height()+1
        left = tilesRect.left()
        top = tilesRect.top()
        pixRect = QtCore.QRectF(0.0, 0.0, TDIM, TDIM)
        emptyTilePix = self._emptyTile
        tilePixmaps = self._tilePixmaps
        for x in xrange(numXtiles):
            for y in xrange(numYtiles):
                tp = (x + left, y + top)
                box = self.tileRect(tp[0], tp[1])
                if tp in self._tilePixmaps:
                    painter.drawPixmap(box, tilePixmaps[tp], pixRect)
                else:
                    painter.drawPixmap(box, emptyTilePix, pixRect)

    def zoomTo(self, zoomlevel):
        if zoomlevel > MAX_ZOOM or zoomlevel < MIN_ZOOM:
            return

        self._tilePixmaps = dict()
        self._tileSource.abortAllRequests()

        center = self.sceneRect().center()
        coord = self.lonLatFromPos(center.x(), center.y())
        self._zoom = zoomlevel
        for item in self.items():
            item.updatePosition(self)
        self.setCenter(coord.y(), coord.x())

    def zoomIn(self):
        self.zoomTo(self._zoom+1)

    def zoomOut(self):
        self.zoomTo(self._zoom-1)

    @Qt.pyqtSlot(int, int, int, QtGui.QPixmap)
    def setTilePixmap(self, x, y, zoom, pixmap):
        if self._zoom == zoom:
            self._tilePixmaps[(x, y)] = pixmap
            self.update()

    def requestTiles(self):
        tilesRect = self._tilesRect
        tilePixmaps = self._tilePixmaps

        # purge unused tiles
        bound = tilesRect.adjusted(-10, -10, 10, 10)
        for p in list(tilePixmaps.keys()):
            if not bound.contains(p[0], p[1]):
                del tilePixmaps[p]

        # Request load of new tiles
        numXtiles = tilesRect.width()
        numYtiles = tilesRect.height()
        left = tilesRect.left()
        top = tilesRect.top()
        tileSource = self._tileSource
        zoom = self._zoom
        update = False
        for x in xrange(numXtiles):
            for y in xrange(numYtiles):
                tp = (left + x, top + y)
                if tp not in tilePixmaps:
                    pix = tileSource.requestTile(tp[0], tp[1], zoom)
                    if pix is not None:
                        tilePixmaps[tp] = pix
                        update = True
        if update:
            self.update()

    def tileRect(self, tx, ty):
        return QtCore.QRectF(tx * TDIM, ty * TDIM, TDIM, TDIM)

    def setSize(self, width, height):
        rect = QtCore.QRectF(self.sceneRect())
        rect.setWidth(width)
        rect.setHeight(height)
        self.setSceneRect(rect)

    def setCenter(self, lat, lon):
        rect = QtCore.QRectF(self.sceneRect())
        pos = self.posFromLatLon(lat, lon)
        rect.moveCenter(pos)
        self.setSceneRect(rect)

    def translate(self, dx, dy):
        self.setSceneRect(self.sceneRect().translated(dx, dy))

    def posFromLatLon(self, lat, lon):
        zn = 1 << self._zoom
        zn = zn * TDIM
        tx = (lon+180.0)/360.0
        ty = (1.0 - m_log(m_tan(lat*m_PI/180.0) + 1.0/m_cos(lat*m_PI/180.0)) / m_PI) / 2.0
        return QtCore.QPointF(tx*zn, ty*zn)

    def lonLatFromPos(self, x, y):
        tx = x / float(TDIM)
        ty = y / float(TDIM)

        zn = 1 << self._zoom
        lon = tx / zn * 360.0 - 180.0
        n = m_PI - 2.0 * m_PI * ty / zn
        lat = 180.0 / m_PI * m_atan(0.5 * (m_exp(n) - m_exp(-n)))
        return QtCore.QPointF(lon, lat)

    def tileFromPos(self, x, y):
        tx = x / float(TDIM)
        ty = y / float(TDIM)
        return QtCore.QPointF(tx, ty)

    def addEllipse(self, longitude, latitude, radius):
        item = MapGraphicsEllipseItem(longitude, latitude, radius, self)
        return item
