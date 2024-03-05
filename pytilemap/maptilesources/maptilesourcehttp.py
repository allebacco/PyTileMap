from __future__ import print_function, absolute_import

from qtpy.QtCore import Qt, Signal, Slot, QObject, QByteArray, QUrl, QThread
from qtpy.QtGui import QPixmap
from qtpy.QtNetwork import QNetworkRequest, QNetworkDiskCache, QNetworkAccessManager, \
    QNetworkReply

from .maptilesource import MapTileSource
from ..qtsupport import getQVariantValue, getCacheFolder

import os
from urllib.parse import urlparse

DEFAULT_CACHE_SIZE = 1024 * 1024 * 16000


class MapTileHTTPLoader(QObject):

    tileLoaded = Signal(int, int, int, QByteArray)

    def __init__(self, cacheSize=DEFAULT_CACHE_SIZE, userAgent='(PyQt) TileMap 1.0', parent=None):
        QObject.__init__(self, parent=parent)
        self._manager = None
        self._cache = None
        self._cacheSize = cacheSize

        try:
            # Convert user agent to bytes
            userAgent = userAgent.encode()
        except:
            # no encode method exists. This hsould be the Python 2 case
            pass

        self._userAgent = userAgent
        self._tileInDownload = dict()

    @Slot(int, int, int, str, str)
    def loadTile(self, x, y, zoom, url, cache_dir):
        if self._manager is None:
            self._manager = QNetworkAccessManager(parent=self)
            self._manager.finished.connect(self.handleNetworkData)
            self._cache = './tiles'

        key = (x, y, zoom)
        url = QUrl(url)
        #base = parsed_url.netloc
        if key not in self._tileInDownload:
            path = os.path.join(self._cache, str(cache_dir), str(zoom), str(x), str(y)+'.png')
            if os.path.exists(path):
                self.tileLoaded.emit(x, y, zoom,  open(path, 'rb').read())
            else:
                # Request the image to the map service
                request = QNetworkRequest(url=url)
                request.setRawHeader(b'User-Agent', self._userAgent)
                request.setAttribute(QNetworkRequest.User, [key, cache_dir])
                request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
                self._tileInDownload[key] = self._manager.get(request)


    @Slot(QNetworkReply)
    def handleNetworkData(self, reply):
        [tp, cache_dir] = getQVariantValue(reply.request().attribute(QNetworkRequest.User))
        if tp in self._tileInDownload:
            del self._tileInDownload[tp]

        zoom = tp[2]; x = tp[0]; y = tp[1]

        base = cache_dir

        if not reply.error():
            data = reply.readAll()
            if not os.path.isdir(os.path.join(self._cache, base, str(zoom), str(x))):
                os.makedirs(os.path.join(self._cache, base, str(zoom), str(x))) 
            fout = open(os.path.join(self._cache, base, str(zoom), str(x), str(y)+'.png'), 'wb')
            fout.write(data)
            fout.close()
            self.tileLoaded.emit(tp[0], tp[1], tp[2], data)
        reply.close()
        reply.deleteLater()

    @Slot()
    def abortRequest(self, x, y, zoom):
        p = (x, y, zoom)
        if p in self._tileInDownload:
            reply = self._tileInDownload[p]
            del self._tileInDownload[p]
            reply.close()
            reply.deleteLater()

    @Slot()
    def abortAllRequests(self):
        for x, y, zoom in list(self._tileInDownload.keys()):
            self.abortRequest(x, y, zoom)


class MapTileSourceHTTP(MapTileSource):

    def __init__(self, cacheSize=DEFAULT_CACHE_SIZE, userAgent='(PyQt) TileMap 1.0',
                 tileSize=256, minZoom=2, maxZoom=18, mapHttpLoader=None, parent=None):
        MapTileSource.__init__(self, tileSize=tileSize, minZoom=minZoom, maxZoom=maxZoom, parent=parent)

        if mapHttpLoader is not None:
            self._loader = mapHttpLoader
        else:
            self._loader = MapTileHTTPLoader(cacheSize=cacheSize, userAgent=userAgent)

        self._loader.tileLoaded.connect(self.handleTileDataLoaded)
        self._cache_dir = 'cache'

    @Slot()
    def close(self):
        self._loader.abortAllRequests()

    def url(self, x, y, zoom):
        raise NotImplementedError()

    def requestTile(self, x, y, zoom):
        url = self.url(x, y, zoom)
        self._loader.loadTile(x, y, zoom, url, self._cache_dir)

    @Slot(int, int, int, QByteArray)
    def handleTileDataLoaded(self, x, y, zoom, data):
        pix = QPixmap()
        pix.loadFromData(data)
        self.tileReceived.emit(x, y, zoom, pix)

    def abortAllRequests(self):
        self._loader.abortAllRequests()

    def imageFormat(self):
        return 'PNG'
