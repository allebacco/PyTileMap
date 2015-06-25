import sys
from PyQt4 import QtCore, QtGui

from items import TileMapItemPoint
from tilemap import TileMap


class MapZoom(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.map = TileMap(self)
        self.setCentralWidget(self.map)
        self.map.setFocus()

        osloAction = QtGui.QAction("&Oslo", self)
        berlinAction = QtGui.QAction("&Berlin", self)
        jakartaAction = QtGui.QAction("&Jakarta", self)
        nightModeAction = QtGui.QAction("&Night Mode", self)
        nightModeAction.setCheckable(True)
        nightModeAction.setChecked(False)
        osmAction = QtGui.QAction("&About OpenStreetMap", self)
        osloAction.triggered.connect(self.chooseOslo)
        berlinAction.triggered.connect(self.chooseBerlin)
        jakartaAction.triggered.connect(self.chooseJakarta)
        nightModeAction.triggered.connect(self.map.toggleNightMode)
        osmAction.triggered.connect(self.aboutOsm)

        menu = self.menuBar().addMenu("&Options")
        menu.addAction(osloAction)
        menu.addAction(berlinAction)
        menu.addAction(jakartaAction)
        menu.addSeparator()
        menu.addAction(nightModeAction)
        menu.addAction(osmAction)

        item = TileMapItemPoint(59.9138204, 10.7387413)
        self.map.addItem(item)

    def chooseOslo(self):
        self.map.setCenter(59.9138204, 10.7387413)

    def chooseBerlin(self):
        self.map.setCenter(52.52958999943302, 13.383053541183472)

    def chooseJakarta(self):
        self.map.setCenter(-6.211544, 106.845172)

    def aboutOsm(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.openstreetmap.org"))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("TileMap")

    w = MapZoom()
    w.setWindowTitle("OpenStreetMap")

    if False:
        w.showMaximized()
    else:
        w.resize(800, 600)
        w.show()

    sys.exit(app.exec_())
