from PyQt4 import Qt, QtGui, QtCore


class MapTileSource(object):

    def url(self, longitude, latitude, zoom):
        raise NotImplementedError()

    def imageFormat(self):
        return 'PNG'

    def tileSize(self):
        return 256

    def maxZoom(self):
        return 2

    def minZoom(self):
        return 18


class MapTileSourceOSM(MapTileSource):

    def url(self, longitude, latitude, zoom):
        url = "http://tile.openstreetmap.org/%d/%d/%d.png" % (zoom, longitude, latitude)
        return url


class MapTileSourceHereDemo(MapTileSource):

    _server = 0

    def url(self, lat, lon, zoom):
        self._server += 1
        if self._server > 4:
            self._server = 0
        url = "http://%d.base.maps.cit.api.here.com/maptile/2.1/maptile/" % self._server
        url += "newest/normal.day/%d/%d/%d/256/png8" % (zoom, lon, lat)
        url += '?app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg'
        return url

    def imageFormat(self):
        return 'PNG'

    def tileSize(self):
        return 256

    def maxZoom(self):
        return 2

    def minZoom(self):
        return 18
