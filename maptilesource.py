import os

from PyQt4.Qt import Qt, pyqtSignal, pyqtSlot
from PyQt4.QtCore import QObject, QByteArray, QUrl, QThread
from PyQt4.QtGui import QDesktopServices, QPixmap
from PyQt4.QtNetwork import QNetworkRequest, QNetworkDiskCache, QNetworkAccessManager, \
                            QNetworkReply,  QNetworkCacheMetaData


class MapTileSource(QObject):

    tileReceived = pyqtSignal(int, int, int, QPixmap)

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
            return QPixmap(filename)
        return None


class MapTileHTTPLoader(QObject):

    tileLoaded = pyqtSignal(int, int, int, QByteArray)

    _userAgent = None
    _cacheSize = None

    def __init__(self, cacheSize=1024*1024*100, userAgent='(PyQt) TileMap 1.2', parent=None):
        QObject.__init__(self, parent=parent)
        self._manager = None
        self._cache = None
        self._cacheSize = cacheSize
        self._userAgent = userAgent
        self._tileInDownload = dict()

    @pyqtSlot(int, int, int, str)
    def loadTile(self, x, y, zoom, url):
        if self._manager is None:
            self._manager = QNetworkAccessManager(parent=self)
            self._manager.finished.connect(self.handleNetworkData)
            self._cache = QNetworkDiskCache(parent=self)
            self._cache.setMaximumCacheSize(self._cacheSize)
            self._cache.setCacheDirectory(QDesktopServices.storageLocation(QDesktopServices.CacheLocation))

        key = (x, y, zoom)
        url = QUrl(url)
        if self._cache.metaData(url).isValid():
            iodevice = self._cache.data(url)
            data = iodevice.readAll()
            iodevice.close()
            iodevice.deleteLater()
            self.tileLoaded.emit(x, y, zoom, data)
        elif key in self._tileInDownload:
            # Image is already in download... return
            return
        else:
            request = QNetworkRequest(url=url)
            request.setRawHeader('User-Agent', self._userAgent)
            request.setAttribute(QNetworkRequest.User, key)
            self._tileInDownload[key] = self._manager.get(request)

        print 'In download:', len(self._tileInDownload)

    @pyqtSlot(QNetworkReply)
    def handleNetworkData(self, reply):
        tp = reply.request().attribute(QNetworkRequest.User).toPyObject()
        if tp in self._tileInDownload:
            del self._tileInDownload[tp]

        if not reply.error():
            data = reply.readAll()
            meta = QNetworkCacheMetaData()
            meta.setUrl(reply.request().url())
            meta.setSaveToDisk(True)
            iodevice = self._cache.prepare(meta)
            iodevice.write(data)
            self._cache.insert(iodevice)
            self.tileLoaded.emit(tp[0], tp[1], tp[2], data)
        reply.close()
        reply.deleteLater()
        print 'In download:', len(self._tileInDownload)

    @pyqtSlot()
    def abortRequest(self, x, y, zoom):
        p = (x, y, zoom)
        reply = self._tileInDownload[p]
        del self._tileInDownload[p]
        reply.close()
        reply.deleteLater()

    @pyqtSlot()
    def abortAllRequests(self):
        for x, y, zoom in self._tileInDownload.keys():
            self.abortRequest(x, y, zoom)
        print 'In download:', len(self._tileInDownload)


class MapTileSourceHTTP(MapTileSource):

    requestTileLoading = pyqtSignal(int, int, int, str)
    abortTileLoading = pyqtSignal()

    _userAgent = None
    _manager = None
    _tileInDownload = None
    _cache = None
    _thread = None

    def __init__(self, cacheSize=1024*1024*100, userAgent='(PyQt) TileMap 1.2',
                 tileSize=256, minZoom=2, maxZoom=18, parent=None):
        MapTileSource.__init__(self, tileSize=tileSize, minZoom=minZoom, maxZoom=maxZoom, parent=parent)

        self._thread = QThread(parent=self)
        self._loader = MapTileHTTPLoader(cacheSize=cacheSize, userAgent=userAgent)
        self._loader.moveToThread(self._thread)

        self.requestTileLoading.connect(self._loader.loadTile, Qt.QueuedConnection)
        self.abortTileLoading.connect(self._loader.abortAllRequests, Qt.QueuedConnection)
        self._loader.tileLoaded.connect(self.handleTileDataLoaded, Qt.QueuedConnection)

        self._thread.start()

    def url(self, x, y, zoom):
        raise NotImplementedError()

    def requestTile(self, x, y, zoom):
        url = self.url(x, y, zoom)
        self.requestTileLoading.emit(x, y, zoom, url)
        return None

    @pyqtSlot(int, int, int, QByteArray)
    def handleTileDataLoaded(self, x, y, zoom, data):
        pix = QPixmap()
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
