from PyQt4.Qt import Qt, pyqtSignal, pyqtSlot
from PyQt4.QtCore import QObject, QByteArray, QUrl, QThread
from PyQt4.QtGui import QDesktopServices, QPixmap
from PyQt4.QtNetwork import QNetworkRequest, QNetworkDiskCache, QNetworkAccessManager, \
                            QNetworkReply,  QNetworkCacheMetaData

from maptilesource import MapTileSource


class MapTileHTTPCache(QNetworkDiskCache):

    def __init__(self, directory=None, maxSize=104857600, parent=None):
        QNetworkDiskCache.__init__(self, parent=parent)

        if directory is None:
            directory = str(QDesktopServices.storageLocation(QDesktopServices.CacheLocation))

        self.setMaximumCacheSize(maxSize)
        self.setCacheDirectory(directory)

    def __contains__(self, url):
        return self.metaData(url).isValid()

    def __getitem__(self, url):
        iodevice = self.data(url)
        if iodevice is None:
            return None
        data = iodevice.readAll()
        iodevice.close()
        iodevice.deleteLater()
        return data

    def __setitem__(self, url, data):
        meta = QNetworkCacheMetaData()
        meta.setUrl(url)
        meta.setSaveToDisk(True)
        iodevice = self.prepare(meta)
        iodevice.write(data)
        self.insert(iodevice)

    def __delitem__(self, url):
        self.remove(url)


class MapTileHTTPLoader(QObject):

    tileLoaded = pyqtSignal(int, int, int, QByteArray)

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
