from __future__ import print_function, absolute_import

from .maptilesourcehttp import MapTileSourceHTTP


class MapTileSourceOSM(MapTileSourceHTTP):

    def __init__(self, parent=None):
        MapTileSourceHTTP.__init__(self, parent=parent)

    def url(self, x, y, zoom):
        url = "http://tile.openstreetmap.org/%d/%d/%d.png" % (zoom, x, y)
        #url = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Aerosol/default/2014-04-09/GoogleMapsCompatible_Level6/%d/%d/%d.png" % (zoom,x,y) #{level}/{row}/{col}.png
        print (url)
        return url
