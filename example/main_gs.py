import sys

from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from qtpy.QtWidgets import QMainWindow, QGraphicsView, QGraphicsItem, \
    QGraphicsSimpleTextItem, QApplication

from pytilemap import MapGraphicsView, MapTileSourceHere, MapTileSourceOSM



POINTS = [(44.837632, 10.201736),
          (44.837621, 10.201474),
          (44.837594, 10.201205),
          (44.837558, 10.200954),
          (44.837528, 10.200715),
          (44.837501, 10.200464),
          (44.837473, 10.200212),
          (44.837437, 10.199949),
          (44.837390, 10.199687),
          (44.837340, 10.199453),
          (44.837297, 10.199205),
          (44.837244, 10.198961),
          (44.837186, 10.198719),
          (44.837130, 10.198492),
          (44.837076, 10.198255),
          (44.837012, 10.198013),
          (44.836951, 10.197785),
          (44.836875, 10.197554),
          (44.836797, 10.197321),
          (44.836720, 10.197089),
          (44.836641, 10.196857),
          (44.836554, 10.196610),
          (44.836468, 10.196377),
          (44.836382, 10.196144),
          (44.836257, 10.195911),
          (44.836167, 10.195688),
          (44.836072, 10.195474),
          (44.835972, 10.195254),
          (44.835867, 10.195032),
          (44.835764, 10.194817),
          (44.835679, 10.194624),
          (44.835570, 10.194426),
          (44.835457, 10.194223),
          (44.835341, 10.194014),
          (44.835196, 10.193864),
          (44.835078, 10.193683),
          (44.834959, 10.193495),
          (44.834845, 10.193302),
          (44.834724, 10.193118),
          (44.834596, 10.192943),
          (44.834460, 10.192766),
          (44.834327, 10.192593),
          (44.834200, 10.192429),
          (44.834065, 10.192293),
          (44.833928, 10.192140),
          (44.833793, 10.191997),
          (44.833653, 10.191842),
          (44.833520, 10.191694),
          (44.833388, 10.191560),
          (44.833248, 10.191425),
          (44.833100, 10.191291),
          (44.832954, 10.191164),
          (44.832810, 10.191037)]

POINTS_2 = [(44.868333, 10.053170), (44.867962, 10.053621), (44.867141, 10.054216),
            (44.866913, 10.054104), (44.867016, 10.053782), (44.866993, 10.052650)]
POINTS_2_SIZES = [1, 2, 3, 4, 5]
POINTS_2_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 0, 0)]


class MapZoom(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        view = MapGraphicsView(tileSource=MapTileSourceHere())

        self.setCentralWidget(view)

        view.scene().setCenter(10.065990, 44.861041, zoom=13)
        view.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        view.setRenderHint(QPainter.Antialiasing, True)
        view.setRenderHint(QPainter.SmoothPixmapTransform, True)

        pointItem = view.scene().addCircle(10.068640, 44.860767, 3.0)
        pointItem.setBrush(Qt.black)
        pointItem.setToolTip('10.068640, 44.860767')
        pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)

        lats = list()
        lons = list()
        for p in POINTS:
            pointItem = view.scene().addCircle(p[1], p[0], 5.0)
            pointItem.setBrush(Qt.green)
            pointItem.setPen(QPen(Qt.NoPen))
            pointItem.setToolTip('%f, %f' % (p[1], p[0]))
            pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
            lons.append(p[1])
            lats.append(p[0])

        lineItem = view.scene().addLine(10.191037, 44.832810, 10.201736, 44.837632)
        lineItem.setPen(QPen(QBrush(Qt.blue), 3.0))

        polylineItem = view.scene().addPolyline(lons, lats)
        polylineItem.setPen(QPen(QBrush(Qt.red), 3.0))

        pix = QPixmap(24, 24)
        pix.fill(Qt.red)
        pixmapItem = view.scene().addPixmap(10.090598, 44.857893, pix)
        pixmapItem.setOffset(-12, -12)
        pointItemPixmapOrigin = view.scene().addCircle(10.090598, 44.857893, 3.0)
        pointItemPixmapOrigin.setBrush(Qt.black)

        # Pixmap with both corners geo-referenced
        geo_pixmap = QPixmap(36,36)
        geo_pixmap.fill(Qt.blue)
        geo_pixmap_item= view.scene().addGeoPixmap(10.090598, 44.8709, 10.092, 44.873, geo_pixmap)
        geo_pixmap_item.setLabel("GeoPixmapItem")
        geo_pixmap_item.showLabel()

        # Blue Point with an HTML label
        blue_point = view.scene().addCircle(10.083103, 44.868014, 3.0)
        blue_point.setBrush(Qt.blue)
        blue_point.setPen(QPen(Qt.NoPen))
        blue_point.setLabel("<div style='background-color: #ffff00;'>" + "Label for Blue Point" + "</div>", html=True)
        blue_point.showLabel()

        # Location Pin
        pin_item = view.scene().addPin(10.06, 44.84)
        pin_item.setLabel("<div style='background-color: #00ff00;'><I>Pin Item</I></div>",html=True)
        pin_item.showLabel()

        lon0r = 10.06
        lat0r = 44.83
        lon1r = 10.110000000000001
        lat1r = 44.743397459621555
        lon2r = 9.936794919243113
        lat2r = 44.64339745962155
        lon3r = 9.886794919243112
        lat3r = 44.73

        pin0 = view.scene().addPin(lon0r, lat0r)
        pin1 = view.scene().addPin(lon1r, lat1r)
        pin2 = view.scene().addPin(lon2r, lat2r)
        pin3 = view.scene().addPin(lon3r, lat3r)

        clr = QColor(0,255,0,100)
        pix = QPixmap(100,100)
        pix.fill(clr)


        view.scene().addGeoPixmapCorners(lon0r, lat0r,
                                        lon1r, lat1r,
                                        lon2r, lat2r,
                                        lon3r, lat3r,
                                        pix)



        lats_2 = list()
        lons_2 = list()
        for p in POINTS_2:
            lons_2.append(p[1])
            lats_2.append(p[0])
        linesGroupItem = view.scene().addLinesGroup(lons_2, lats_2)
        linesGroupItem.setLineStyle(POINTS_2_COLORS, width=POINTS_2_SIZES)

        legendItem = view.scene().addLegend()
        legendItem.addPoint('Point 1', '#FF0000', border=None)
        legendItem.addRect('Rect 2', '#00FF00', border=None)
        legendItem.addPoint('Circle 3', '#0000FF', border=None)
        legendItem.addRect('Sphere 4', '#00FFFF', border=None)
        legendItem.addPoint('Polygon 5', '#FF00FF', border=None)

        navItem = view.scene().addNavItem(anchor=Qt.TopRightCorner)

        scaleItem = view.scene().addScale(anchor=Qt.BottomRightCorner)

        


def main():
    w = MapZoom()
    w.setWindowTitle("OpenStreetMap")

    w.resize(800, 600)
    w.show()

    return app.exec_()

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("TileMap")

    sys.exit(main())
