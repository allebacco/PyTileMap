import math
from PyQt4 import Qt, QtCore, QtGui, QtNetwork

from tile_utils import TDIM, MIN_ZOOM, MAX_ZOOM, qHash, tileForCoordinate, longitudeFromTile, latitudeFromTile


class BaseTile(QtCore.QObject):
    updated = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self, parent=None, width=400, height=300, zoom=15, latitude=59.9138204, longitude=10.7386413):
        QtCore.QObject.__init__(self)
        self.width = width
        self.height = height
        self.zoom = zoom
        self.latitude = latitude
        self.longitude = longitude

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

        self.rect = QtCore.QRectF(0.0, 0.0, width, height)
        self.setCenter(latitude, longitude)

    def invalidate(self, emitSignal=True):
        if self.width <= 0 or self.height <= 0:
            return

        self.rect = QtCore.QRectF(0.0, 0.0, self.width, self.height)

        ct = tileForCoordinate(self.latitude, self.longitude, self.zoom)
        cx = ct.x() * TDIM
        cy = ct.y() * TDIM

        self.rect.moveCenter(QtCore.QPointF(cx, cy))

        tx = ct.x()
        ty = ct.y()

        # top left corner of the center tile
        xp = int(self.width / 2 - (tx - math.floor(tx)) * TDIM)
        yp = int(self.height / 2 - (ty - math.floor(ty)) * TDIM)

        # first tile vertical and horizontal
        xa = (xp + TDIM - 1) / TDIM
        ya = (yp + TDIM - 1) / TDIM
        xs = tx - xa
        ys = ty - ya

        # offset for top-left tile
        self.m_offset = QtCore.QPoint(xp - xa * TDIM, yp - ya * TDIM)

        # last tile vertical and horizontal
        xe = tx + (self.width - xp - 1) / TDIM
        ye = ty + (self.height - yp - 1) / TDIM

        # build a rect
        self.m_tilesRect = QtCore.QRect(xs, ys, xe - xs + 1, ye - ys + 1)

        x = xs * TDIM - self.m_offset.x()
        y = ys * TDIM - self.m_offset.y()
        self.g_offset = QtCore.QPointF(x, y)

        if len(self._tileInDownload) == 0:
            self.download()

        if emitSignal:
            self.updated.emit(QtCore.QRect(0, 0, self.width, self.height))

    def render(self, painter, rect):
        for x in xrange(self.m_tilesRect.width()+1):
            for y in xrange(self.m_tilesRect.height()+1):
                tp = QtCore.QPoint(x + self.m_tilesRect.left(), y + self.m_tilesRect.top())
                box = self.tileRect(tp)
                if rect.intersects(box):
                    if qHash(tp) in self.m_tilePixmaps:
                        painter.drawPixmap(box, self.m_tilePixmaps[qHash(tp)])
                    else:
                        painter.drawPixmap(box, self.m_emptyTile)

    def pan(self, delta):
        dx = QtCore.QPointF(delta) / TDIM
        center = tileForCoordinate(self.latitude, self.longitude, self.zoom) - dx
        self.latitude = latitudeFromTile(center.y(), self.zoom)
        self.longitude = longitudeFromTile(center.x(), self.zoom)
        self.invalidate()

    def zoomTo(self, zoomlevel):
        self.zoom = zoomlevel
        self.invalidate(True)

    def zoomIn(self):
        if self.zoom < MAX_ZOOM:
            self.zoomTo(self.zoom+1)

    def zoomOut(self):
        if self.zoom > MIN_ZOOM:
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
        self.updated.emit(self.tileRect(tp))

        # purge unused tiles
        bound = self.m_tilesRect.adjusted(-2, -2, 2, 2)
        for hashTp in list(self.m_tilePixmaps.keys()):
            if not bound.contains(hashTp[0], hashTp[1]):
                del self.m_tilePixmaps[hashTp]

    def url(self, lat, lon, zoom):
        raise NotImplementedError()

    def imageFormat(self):
        raise NotImplementedError()

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
        t = tp - self.m_tilesRect.topLeft()
        x = t.x() * TDIM + self.m_offset.x()
        y = t.y() * TDIM + self.m_offset.y()
        rect = QtCore.QRect(x, y, TDIM, TDIM)
        return rect

    def globalOffset(self):
        return self.g_offset

    def topLeftTile(self):
        return self.m_tilesRect.topLeft()

    def setCenter(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
        self.invalidate()
