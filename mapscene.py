from math import log as m_log
from math import tan as m_tan
from math import pi as m_PI
from math import cos as m_cos
from math import atan as m_atan
from math import exp as m_exp
from math import floor as m_floor

from PyQt4.Qt import Qt, pyqtSlot
from PyQt4.QtCore import QRect, QRectF, QPointF
from PyQt4.QtGui import QGraphicsScene, QPixmap

from mapitems import MapGraphicsEllipseItem


def qHash(point):
    '''Qt doesn't implement a qHash() for QPoint.'''
    return (point.x(), point.y())


class MapGraphicScene(QGraphicsScene):

    _tileSource = None

    def __init__(self, tileSource, parent=None):
        QGraphicsScene.__init__(self)
        self._zoom = 15

        self._tileSource = tileSource
        self._tileSource.setParent(self)
        self._tileSource.tileReceived.connect(self.setTilePixmap)
        tdim = self._tileSource.tileSize()

        self._emptyTile = QPixmap(tdim, tdim)
        self._emptyTile.fill(Qt.lightGray)

        self._tilesRect = QRect()
        self._tilePixmaps = {}

        self._tileInDownload = list()

        self.setSceneRect(0.0, 0.0, 400, 300)
        self.sceneRectChanged.connect(self.onSceneRectChanged)

    def onSceneRectChanged(self, rect):
        tdim = self._tileSource.tileSize()
        center = rect.center()
        ct = self.tileFromPos(center.x(), center.y())
        tx = ct.x()
        ty = ct.y()

        width = rect.width()
        height = rect.height()
        # top left corner of the center tile
        xp = int(width / 2.0 - (tx - m_floor(tx)) * tdim)
        yp = int(height / 2.0 - (ty - m_floor(ty)) * tdim)

        # first tile vertical and horizontal
        xa = (xp + tdim - 1) / tdim
        ya = (yp + tdim - 1) / tdim
        xs = tx - xa
        ys = ty - ya

        # last tile vertical and horizontal
        xe = tx + (width - xp - 1) / tdim + 1
        ye = ty + (height - yp - 1) / tdim + 1

        # build a rect
        self._tilesRect = QRect(xs, ys, xe - xs + 1, ye - ys + 1)

        self.requestTiles()

        self.update()

    def drawBackground(self, painter, rect):
        tilesRect = self._tilesRect
        numXtiles = tilesRect.width()+1
        numYtiles = tilesRect.height()+1
        left = tilesRect.left()
        top = tilesRect.top()
        tdim = self._tileSource.tileSize()
        pixRect = QRectF(0.0, 0.0, tdim, tdim)
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
        tileSource = self._tileSource
        if zoomlevel > tileSource.maxZoom() or zoomlevel < tileSource.minZoom():
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

    @pyqtSlot(int, int, int, QPixmap)
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
        tdim = self._tileSource.tileSize()
        return QRectF(tx * tdim, ty * tdim, tdim, tdim)

    def setSize(self, width, height):
        rect = QRectF(self.sceneRect())
        rect.setWidth(width)
        rect.setHeight(height)
        self.setSceneRect(rect)

    def setCenter(self, lat, lon):
        rect = QRectF(self.sceneRect())
        pos = self.posFromLatLon(lat, lon)
        rect.moveCenter(pos)
        self.setSceneRect(rect)

    def translate(self, dx, dy):
        self.setSceneRect(self.sceneRect().translated(dx, dy))

    def posFromLatLon(self, lat, lon):
        zn = 1 << self._zoom
        zn = zn * self._tileSource.tileSize()
        tx = (lon+180.0)/360.0
        ty = (1.0 - m_log(m_tan(lat*m_PI/180.0) + 1.0/m_cos(lat*m_PI/180.0)) / m_PI) / 2.0
        return QPointF(tx*zn, ty*zn)

    def lonLatFromPos(self, x, y):
        tdim = float(self._tileSource.tileSize())
        tx = x / tdim
        ty = y / tdim
        zn = 1 << self._zoom
        lon = tx / zn * 360.0 - 180.0
        n = m_PI - 2.0 * m_PI * ty / zn
        lat = 180.0 / m_PI * m_atan(0.5 * (m_exp(n) - m_exp(-n)))
        return QPointF(lon, lat)

    def tileFromPos(self, x, y):
        tdim = float(self._tileSource.tileSize())
        return QPointF(x / tdim, y / tdim)

    def addEllipse(self, longitude, latitude, radius):
        item = MapGraphicsEllipseItem(longitude, latitude, radius, self)
        return item
