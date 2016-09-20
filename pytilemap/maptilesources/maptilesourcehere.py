from __future__ import print_function, absolute_import

from .maptilesourcehttp import MapTileSourceHTTP


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


class MapTileSourceHere(MapTileSourceHTTP):

    def __init__(self, tileSize=256, app_id='DemoAppId01082013GAL', app_code='AJKnXv84fjrb0KIHawS0Tg',
                 scheme='normal.day', cit=True, tileType='maptile',
                 userAgent='(PyQt) TileMap 1.2 - HERE', mapHttpLoader=None,
                 minZoom=2, maxZoom=20, parent=None):
        MapTileSourceHTTP.__init__(self, tileSize=tileSize, parent=parent)
        assert tileSize == 256 or tileSize == 512
        self._server = 0

        self._app_id = app_id
        self._app_code = app_code

        self._tileType = tileType
        self._scheme = scheme
        self._cit = '.cit' if cit else ''

    def url(self, x, y, zoom):
        self._server += 1
        if self._server > 4:
            self._server = 0

        url = "http://%d.base.maps%s.api.here.com/maptile/2.1/%s/" % (self._server, self._cit, self._tileType)
        url += "newest/%s/%d/%d/%d/%d/png8" % (self._scheme, zoom, x, y, self._tileSize)
        url += '?app_id=%s&app_code=%s' % (self._app_id, self._app_code)
        return url
