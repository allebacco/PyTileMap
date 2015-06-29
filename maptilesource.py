import os
from cStringIO import StringIO

from PyQt4 import Qt, QtGui, QtCore
from PyQt4.QtCore import QObject
from PyQt4.QtNetwork import QNetworkRequest, QNetworkDiskCache, QNetworkAccessManager, QNetworkReply

from cache import Pycachu


class MapTileSource(QObject):

    tileReceived = Qt.pyqtSignal(int, int, int, QtGui.QPixmap)

    _tileSize = None
    _minZoom = None
    _maxZoom = None

    def __init__(self, tileSize=256, minZoom=2, maxZoom=18, parent=None):
        QObject.__init__(self, parent=parent)
        self._tileSize = tileSize
        self._minZoom = minZoom
        self._maxZoom = maxZoom

    def tileSize(self):
        return self._tileSize

    def maxZoom(self):
        return self._maxZoom

    def minZoom(self):
        return self._minZoom

    def requestTile(self, x, y, zoom):
        raise NotImplementedError()

    def abortAllRequests(self):
        pass


class MapTileSourceDirectory(MapTileSource):

    _directory = None
    _fnameSuffix = None

    def __init__(self, directory, filenameSuffix='.png', tileSize=256, minZoom=2, maxZoom=18, parent=None):
        MapTileSource.__init__(self, tileSize=tileSize, minZoom=minZoom, maxZoom=maxZoom, parent=parent)
        self._directory = directory
        self._fnameSuffix = filenameSuffix

    def tileSize(self):
        return self._tileSize

    def maxZoom(self):
        return self._maxZoom

    def minZoom(self):
        return self._minZoom

    def requestTile(self, x, y, zoom):
        filename = os.path.join(self._directory, str(zoom), str(x), str(y)+self._fnameSuffix)
        if os.path.exists(filename):
            return QtGui.QPixmap(filename)
        return None


class MapTileHTTPLoader(QtCore.QObject):

    tileLoaded = Qt.pyqtSignal(int, int, int, QtCore.QByteArray)

    def __init__(self, cacheSize=1024*1024*100, userAgent='(PyQt) TileMap 1.2',
                 tileSize=256, parent=None):
        QtCore.QThread.__init__(self, parent=parent)
        self._manager = None
        self._tileInDownload = dict()

    @Qt.pyqtSlot(int, int, int, str)
    def loadTile(self, x, y, zoom, url):
        if self._manager is None:
            self._manager = QNetworkAccessManager()
            self._manager.finished.connect(self.handleNetworkData)
            cache = QNetworkDiskCache()
            cache.setCacheDirectory(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation))
            self.m_manager.setCache(cache)

        print 'request', url

        url = QtCore.QUrl(url)
        request = QNetworkRequest(url=url)
        request.setRawHeader('User-Agent', '(PyQt) TileMap 1.2')
        p = (x, y, zoom)
        request.setAttribute(QNetworkRequest.User, p)
        self._tileInDownload[p] = self._manager.get(request)

    @Qt.pyqtSlot(QNetworkReply)
    def handleNetworkData(self, reply):
        tp = reply.request().attribute(QNetworkRequest.User).toPyObject()
        if tp in self._tileInDownload:
            del self._tileInDownload[tp]

        if not reply.error():
            data = reply.readAll()
            self.tileLoaded.emit(tp[0], tp[1], tp[2], data)
        reply.deleteLater()

    @Qt.pyqtSlot()
    def abortRequest(self, x, y, zoom):
        p = (x, y, zoom)
        reply = self._tileInDownload[p]
        del self._tileInDownload[p]
        reply.abort()
        reply.deleteLater()

    @Qt.pyqtSlot()
    def abortAllRequests(self):
        for x, y, zoom in self._tileInDownload.keys():
            self.abortRequest(x, y, zoom)


class MapTileSourceHTTP(MapTileSource):

    requestTileLoading = Qt.pyqtSignal(int, int, int, str)
    abortTileLoading = Qt.pyqtSignal()

    _userAgent = None
    _manager = None
    _tileInDownload = None
    _cache = None
    _thread = None

    def __init__(self, cacheSize=1024*1024*100, userAgent='(PyQt) TileMap 1.2',
                 tileSize=256, minZoom=2, maxZoom=18, parent=None):
        MapTileSource.__init__(self, tileSize=tileSize, minZoom=minZoom, maxZoom=maxZoom, parent=parent)

        self._thread = QtCore.QThread(parent=self)
        self._loader = MapTileHTTPLoader(tileSize=tileSize)
        self._loader.moveToThread(self._thread)
        self.requestTileLoading.connect(self._loader.loadTile, Qt.Qt.QueuedConnection)
        self.abortTileLoading.connect(self._loader.abortAllRequests, Qt.Qt.QueuedConnection)
        self._loader.tileLoaded.connect(self.handleTileDataLoaded, Qt.Qt.QueuedConnection)

        self._thread.start()

    def url(self, x, y, zoom):
        raise NotImplementedError()

    def requestTile(self, x, y, zoom):
        url = self.url(x, y, zoom)
        self.requestTileLoading.emit(x, y, zoom, url)
        return None

    @Qt.pyqtSlot(int, int, int, QtCore.QByteArray)
    def handleTileDataLoaded(self, x, y, zoom, data):
        pix = QtGui.QPixmap()
        pix.loadFromData(data)
        self.tileReceived.emit(x, y, zoom, pix)

    def abortAllRequests(self):
        self.abortTileLoading.emit()

    def imageFormat(self):
        return 'PNG'


class MapTileSourceOSM(MapTileSourceHTTP):

    def __init__(self, parent=None):
        MapTileSourceHTTP.__init__(self, parent=parent)

    def url(self, x, y, zoom):
        url = "http://tile.openstreetmap.org/%d/%d/%d.png" % (zoom, x, y)
        return url


class MapTileSourceHereDemo(MapTileSourceHTTP):

    _server = None

    def __init__(self, tileSize=256, parent=None):
        MapTileSourceHTTP.__init__(self, tileSize=tileSize, parent=parent)
        assert tileSize == 256 or tileSize == 512
        self._server = 0

    def url(self, x, y, zoom):
        self._server += 1
        if self._server > 4:
            self._server = 0
        url = "http://%d.base.maps.cit.api.here.com/maptile/2.1/maptile/" % self._server
        url += "newest/normal.day/%d/%d/%d/%d/png8" % (zoom, x, y, self._tileSize)
        url += '?app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg'
        return url
