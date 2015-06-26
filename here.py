from tile import BaseTile


class HereTile(BaseTile):

    def __init__(self, parent=None, width=400, height=300, zoom=15, latitude=59.9138204, longitude=10.7386413):
        BaseTile.__init__(self, parent=parent, width=width, height=height,
                          zoom=zoom, latitude=latitude, longitude=longitude)

    def url(self, lat, lon, zoom):
        url = "http://1.base.maps.cit.api.here.com/maptile/2.1/maptile/"
        url += "newest/normal.day/%d/%d/%d/256/png8" % (zoom, lon, lat)
        url += '?app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg'
        return url

    def imageFormat(self):
        return 'PNG'
