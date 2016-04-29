from PyQt4 import Qt, QtGui

from pytilemap.mapview import MapGraphicsView
from pytilemap.maptilesources.maptilesourcehere import MapTileSourceHere
from pytilemap.maptilesources.maptilesourceosm import MapTileSourceOSM


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


class MapZoom(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        view = MapGraphicsView(tileSource=MapTileSourceHere())

        self.setCentralWidget(view)

        view.scene().setCenter(10.065990, 44.861041)
        view.setOptimizationFlag(QtGui.QGraphicsView.DontSavePainterState, True)
        view.setRenderHint(QtGui.QPainter.Antialiasing, True)
        view.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        pointItem = view.scene().addCircle(10.068640, 44.860767, 3.0)
        pointItem.setBrush(Qt.Qt.black)
        pointItem.setToolTip('10.068640, 44.860767')
        pointItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

        lats = list()
        lons = list()
        for p in POINTS:
            pointItem = view.scene().addCircle(p[1], p[0], 5.0)
            pointItem.setBrush(Qt.Qt.green)
            pointItem.setPen(QtGui.QPen(Qt.Qt.NoPen))
            pointItem.setToolTip('%f, %f' % (p[1], p[0]))
            pointItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
            lons.append(p[1])
            lats.append(p[0])

        lineItem = view.scene().addLine(10.191037, 44.832810, 10.201736, 44.837632)
        lineItem.setPen(QtGui.QPen(QtGui.QBrush(Qt.Qt.blue), 3.0))

        polylineItem = view.scene().addPolyline(lons, lats)
        polylineItem.setPen(QtGui.QPen(QtGui.QBrush(Qt.Qt.red), 3.0))

        pix = QtGui.QPixmap(24, 24)
        pix.fill(Qt.Qt.red)
        pixmapItem = view.scene().addPixmap(10.090598, 44.857893, pix)
        pixmapItem.setOffset(-12, -12)
        pointItemPixmapOrigin = view.scene().addCircle(10.090598, 44.857893, 3.0)
        pointItemPixmapOrigin.setBrush(Qt.Qt.black)

        pointItemWithChild = view.scene().addCircle(10.083103, 44.858014, 3.0)
        pointItemWithChild.setBrush(Qt.Qt.blue)
        pointItemWithChild.setPen(QtGui.QPen(Qt.Qt.NoPen))

        textItem = QtGui.QGraphicsSimpleTextItem('Annotation\nfor blue point', parent=pointItemWithChild)
        textItem.setBrush(QtGui.QBrush(QtGui.QColor(Qt.Qt.blue)))
        textItem.setPos(-5, 3)

        legendItem = view.scene().addLegend()
        legendItem.addPoint('Point 1', color=QtGui.QColor('#FF0000'))
        legendItem.addRect('Rect 2', color=QtGui.QColor('#00FF00'))
        legendItem.addPoint('Circle 3', color=QtGui.QColor('#0000FF'))
        legendItem.addRect('Sphere 4', color=QtGui.QColor('#00FFFF'))
        legendItem.addPoint('Polygon 5', color=QtGui.QColor('#FF00FF'))


if __name__ == '__main__':
    app = QtGui.QApplication([])
    app.setApplicationName("TileMap")

    w = MapZoom()
    w.setWindowTitle("OpenStreetMap")

    w.resize(800, 600)
    w.show()

    app.exec_()
