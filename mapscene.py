import math
from PyQt4 import Qt, QtCore, QtGui, QtNetwork

from mapitems import MapGraphicsEllipseItem


TDIM = 256
MIN_ZOOM = 2
MAX_ZOOM = 18


def qHash(point):
    '''Qt doesn't implement a qHash() for QPoint.'''
    return (point.x(), point.y())


class MapGraphicScene(QtGui.QGraphicsScene):

    def __init__(self, tileSource, parent=None):
        QtCore.QObject.__init__(self)
        self.zoom = 15

        self.m_emptyTile = QtGui.QPixmap(TDIM, TDIM)
        self.m_emptyTile.fill(QtCore.Qt.lightGray)

        self.m_manager = QtNetwork.QNetworkAccessManager()
        cache = QtNetwork.QNetworkDiskCache()
        cache.setCacheDirectory(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation))
        self.m_manager.setCache(cache)
        self.m_manager.finished.connect(self.handleNetworkData)

        self.m_url = QtCore.QUrl()
        self.m_offset = QtCore.QPoint()
        self.g_offset = QtCore.QPoint()
        self.m_tilesRect = QtCore.QRect()
        self.m_tilePixmaps = {}

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
        xp = int(width / 2.0 - (tx - math.floor(tx)) * TDIM)
        yp = int(height / 2.0 - (ty - math.floor(ty)) * TDIM)

        # first tile vertical and horizontal
        xa = (xp + TDIM - 1) / TDIM
        ya = (yp + TDIM - 1) / TDIM
        xs = tx - xa
        ys = ty - ya

        # offset for top-left tile
        self.m_offset = QtCore.QPoint(xp - xa * TDIM, yp - ya * TDIM)

        # last tile vertical and horizontal
        xe = tx + (width - xp - 1) / TDIM
        ye = ty + (height - yp - 1) / TDIM

        # build a rect
        self.m_tilesRect = QtCore.QRect(xs-1, ys-1, xe - xs + 2, ye - ys + 2)

        if len(self._tileInDownload) == 0:
            self.download()

        self.update()

    def drawBackground(self, painter, rect):
        tilesRect = self.m_tilesRect
        numXtiles = tilesRect.width()+1
        numYtiles = tilesRect.height()+1
        left = tilesRect.left()
        top = tilesRect.top()
        pixRect = QtCore.QRectF(0.0, 0.0, TDIM, TDIM)
        for x in xrange(numXtiles):
            for y in xrange(numYtiles):
                tp = QtCore.QPoint(x + left, y + top)
                box = self.tileRect(tp)
                if qHash(tp) in self.m_tilePixmaps:
                    painter.drawPixmap(box, self.m_tilePixmaps[qHash(tp)], pixRect)
                else:
                    painter.drawPixmap(box, self.m_emptyTile, pixRect)

    def zoomTo(self, zoomlevel):
        if zoomlevel > MAX_ZOOM or zoomlevel < MIN_ZOOM:
            return

        center = self.sceneRect().center()
        coord = self.lonLatFromPos(center.x(), center.y())
        self.zoom = zoomlevel
        print self.zoom
        for item in self.items():
            item.updatePosition(self)
        self.setCenter(coord.y(), coord.x())

    def zoomIn(self):
        self.zoomTo(self.zoom+1)

    def zoomOut(self):
        self.zoomTo(self.zoom-1)

    @Qt.pyqtSlot(QtNetwork.QNetworkReply)
    def handleNetworkData(self, reply):
        img = QtGui.QImage()
        tp = reply.request().attribute(QtNetwork.QNetworkRequest.User).toPyObject()
        hashTp = qHash(tp)
        if not reply.error():
            if img.load(reply, None):
                self.m_tilePixmaps[hashTp] = QtGui.QPixmap.fromImage(img)
        reply.deleteLater()
        if hashTp in self._tileInDownload:
            self._tileInDownload.remove(hashTp)
        self.update()

        # purge unused tiles
        bound = self.m_tilesRect.adjusted(-2, -2, 2, 2)
        for hashTp in list(self.m_tilePixmaps.keys()):
            if not bound.contains(hashTp[0], hashTp[1]):
                del self.m_tilePixmaps[hashTp]

    def url(self, lat, lon, zoom):
        url = "http://tile.openstreetmap.org/%d/%d/%d.png" % (zoom, lon, lat)
        return url

    def imageFormat(self):
        return 'PNG'

    def download(self):
        grab = list()
        for x in xrange(self.m_tilesRect.width()):
            for y in xrange(self.m_tilesRect.height()):
                tp = self.m_tilesRect.topLeft() + QtCore.QPoint(x, y)
                if qHash(tp) not in self.m_tilePixmaps:
                    grab.append(tp)

        if len(grab) == 0:
            self._tileInDownload = list()
            return

        for p in grab:
            url = QtCore.QUrl(self.url(p.y(), p.x(), self.zoom))
            self._tileInDownload.append(qHash(p))
            request = QtNetwork.QNetworkRequest(url=url)
            request.setRawHeader('User-Agent', '(PyQt) TileMap 1.1')
            request.setAttribute(QtNetwork.QNetworkRequest.User, p)
            self.m_manager.get(request)

    def tileRect(self, tp):
        x = tp.x() * TDIM
        y = tp.y() * TDIM
        return QtCore.QRectF(x, y, TDIM, TDIM)

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
        zn = 1 << self.zoom
        zn = zn * TDIM
        tx = (lon+180.0)/360.0
        ty = (1.0 - math.log(math.tan(lat*math.pi/180.0) + 1.0/math.cos(lat*math.pi/180.0)) / math.pi) / 2.0
        return QtCore.QPointF(tx*zn, ty*zn)

    def lonLatFromPos(self, x, y):
        tx = x / float(TDIM)
        ty = y / float(TDIM)

        zn = 1 << self.zoom
        lon = tx / zn * 360.0 - 180.0
        n = math.pi - 2 * math.pi * ty / zn
        lat = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
        return QtCore.QPointF(lon, lat)

    def tileFromPos(self, x, y):
        tx = x / float(TDIM)
        ty = y / float(TDIM)
        return QtCore.QPointF(tx, ty)

    def addEllipse(self, longitude, latitude, radius):
        item = MapGraphicsEllipseItem(longitude, latitude, radius, self)
        return item
