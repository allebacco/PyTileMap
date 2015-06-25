from tile import BaseTile


class OsmTile(BaseTile):

    def __init__(self, parent=None, width=400, height=300, zoom=15, latitude=59.9138204, longitude=10.7386413):
        BaseTile.__init__(self, parent=parent, width=width, height=height,
                          zoom=zoom, latitude=latitude, longitude=longitude)

    def url(self, lat, lon, zoom):
        url = "http://tile.openstreetmap.org/%d/%d/%d.png" % (zoom, lon, lat)
        return url

    def imageFormat(self):
        return 'PNG'
