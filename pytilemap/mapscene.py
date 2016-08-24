from numpy import log, tan, cos, arctan, exp, floor
from numpy import pi as PI

from PyQt4.Qt import Qt, pyqtSlot, pyqtSignal
from PyQt4.QtCore import QRect, QRectF, QPointF, QSizeF
from PyQt4.QtGui import QGraphicsScene, QPixmap

from .mapitems import MapGraphicsCircleItem, MapGraphicsLineItem, \
    MapGraphicsPolylineItem, MapGraphicsPixmapItem, MapGraphicsTextItem, \
    MapGraphicsRectItem
from .maplegenditem import MapLegendItem


PI_div_180 = PI / 180.0
PI_div_180_inv = 180.0 / PI
PI2 = PI * 2.0


class MapGraphicsScene(QGraphicsScene):
    """Graphics scene for showing a slippy map.
    """

    sigZoomChanged = pyqtSignal(int)

    def __init__(self, tileSource, parent=None):
        """Constructor.

        Args:
            tileSource(MapTileSource): Source for loading the tiles.
            parent(QObject): Parent object, default `None`
        """
        QGraphicsScene.__init__(self)

        self._zoom = 15

        self._tileSource = tileSource
        self._tileSource.setParent(self)
        self._tileSource.tileReceived.connect(self.setTilePixmap)
        tdim = self._tileSource.tileSize()

        self._emptyTile = QPixmap(tdim, tdim)
        self._emptyTile.fill(Qt.lightGray)

        self._tilesRect = QRect()
        self._tilePixmaps = {}

        self._tileInDownload = list()

        self.setSceneRect(0.0, 0.0, 400, 300)
        self.sceneRectChanged.connect(self.onSceneRectChanged)

    @pyqtSlot()
    def close(self):
        self._tileSource.close()

    @pyqtSlot(QRectF)
    def onSceneRectChanged(self, rect):
        """Callback for the changing of the visible rect.

        Evaluate the visible tiles and request to load the new tiles.

        Args:
            rect(QRectF): Current visible area.
        """
        tdim = self._tileSource.tileSize()
        center = rect.center()
        ct = self.tileFromPos(center.x(), center.y())
        tx = ct.x()
        ty = ct.y()

        width = rect.width()
        height = rect.height()
        # top left corner of the center tile
        xp = int(width / 2.0 - (tx - floor(tx)) * tdim)
        yp = int(height / 2.0 - (ty - floor(ty)) * tdim)

        # first tile vertical and horizontal
        xs = tx - (xp + tdim - 1) / tdim
        ys = ty - (yp + tdim - 1) / tdim

        # last tile vertical and horizontal
        xe = (width - xp - 1) / tdim - xs + 1 + tx
        ye = (height - yp - 1) / tdim - ys + 1 + ty

        # define the rect of visible tiles
        self._tilesRect = QRect(xs, ys, xe, ye)

        # Request the loading of new tiles (if needed)
        self.requestTiles()

        self.invalidate()
        self.update()

    def drawBackground(self, painter, rect):
        """Draw the background tiles.

        If a tile is not available, draw a gray rectangle.

        Args:
            painter(QPainter): Painter for drawing.
            rect(QRectF): Current visible area.
        """
        tilesRect = self._tilesRect
        left = tilesRect.left()
        top = tilesRect.top()
        numXtiles = tilesRect.width()
        numYtiles = tilesRect.height()
        tdim = self._tileSource.tileSize()
        pixRect = QRectF(0.0, 0.0, tdim, tdim)
        emptyTilePix = self._emptyTile
        tilePixmaps = self._tilePixmaps

        for x in range(numXtiles):
            for y in range(numYtiles):
                tp = (x + left, y + top)
                box = self.tileRect(tp[0], tp[1])
                # Use default gray image if tile image is missing
                pix = tilePixmaps.get(tp, emptyTilePix)
                painter.drawPixmap(box, pix, pixRect)

    def zoomTo(self, pos, zoomlevel):
        """Zoom to a specific zoom level.

        If the level is out of range, the zoom action is ignored.

        clear the current tile cache, evaluate the new center and
        update the position of all the items.

        Args:
            zoomlevel(int): New zoom level.
        """

        tileSource = self._tileSource
        if zoomlevel > tileSource.maxZoom() or zoomlevel < tileSource.minZoom():
            return

        # Get the coordinates of the center using the position in pixels of the mouse
        pos_corr = self.views()[0].mapToScene(pos)
        coord = self.lonLatFromPos(pos_corr.x(), pos_corr.y())

        # Set the new zoom level
        self._zoom = zoomlevel

        # Clear cache and abort active requests
        self._tilePixmaps.clear()
        self._tileSource.abortAllRequests()

        # Re-center map so that the point on which it was zoomed is in the same position
        self.setCenter(coord.x(), coord.y())
        pos_corr = self.views()[0].mapToScene(pos)
        center = self.sceneRect().center()
        self.translate(center.x() - pos_corr.x(), center.y() - pos_corr.y())

        self.sigZoomChanged.emit(zoomlevel)

    def zoomIn(self, pos=None):
        """Increments the zoom level

        Args:
            pos (QPointF): Center position, Latitude and Longitude. Default None for the
                           current center position.
        """
        if pos is None:
            pos = self.sceneRect().center()
        self.zoomTo(pos, self._zoom + 1)

    def zoomOut(self, pos=None):
        """Decrements the zoom level

        Args:
            pos (QPointF): Center position, Latitude and Longitude. Default None for the
                           current center position.
        """
        if pos is None:
            pos = self.sceneRect().center()
        self.zoomTo(pos, self._zoom - 1)

    @pyqtSlot(int, int, int, QPixmap)
    def setTilePixmap(self, x, y, zoom, pixmap):
        """Set the image of the tile.

        Args:
            x(int): X coordinate of the tile.
            y(int): Y coordinate of the tile.
            zoom(int): Zoom coordinate of the tile.
            pixmap(QPixmap): Image for the tile.
        """
        if self._zoom == zoom:
            self._tilePixmaps[(x, y)] = pixmap
        self.update()

    def requestTiles(self):
        """Request the loading of tiles.

        Remove from the cache the oldest tiles.
        Check the loaded tiles and request the requests only
        the missing tiles.
        """
        tilesRect = self._tilesRect
        tilePixmaps = self._tilePixmaps

        # Purge unused tiles
        bound = tilesRect.adjusted(-10, -10, 10, 10)
        for p in list(tilePixmaps.keys()):
            if not bound.contains(p[0], p[1]):
                del tilePixmaps[p]

        numXtiles = tilesRect.width()
        numYtiles = tilesRect.height()
        left = tilesRect.left()
        top = tilesRect.top()
        tileSource = self._tileSource
        zoom = self._zoom

        # Request load of new tiles
        for x in range(numXtiles):
            for y in range(numYtiles):
                tp = (left + x, top + y)
                # Request tile only if missing
                if tp not in tilePixmaps:
                    pix = tileSource.requestTile(tp[0], tp[1], zoom)
                    if pix is not None:
                        tilePixmaps[tp] = pix

        self.update()

    def tileRect(self, tx, ty):
        """Area fro a specific tile.

        Args:
            tx(int): X coordinate of the tile.
            ty(int): Y coordinate of the tile.

        Returns:
            QRectF, the area of the tile.
        """
        tdim = self._tileSource.tileSize()
        return QRectF(tx * tdim, ty * tdim, tdim, tdim)

    def setSize(self, width, height):
        """Set the size of the visible area in pixels.

        Update the scene rect.

        Args:
            width(int): Width of the visible area.
            height(int): Height of the visible area.
        """
        rect = QRectF(self.sceneRect().topLeft(), QSizeF(width, height))
        self.setSceneRect(rect)

    def setCenter(self, lon, lat):
        """Move the center of the visible area to new coordinates.

        Update the scene rect.

        Args:
            lon(float): New longitude of the center.
            lat(float): New latitude of the center.
        """
        rect = QRectF(self.sceneRect())
        pos = self.posFromLonLat(lon, lat)
        rect.moveCenter(pos)
        self.setSceneRect(rect)

    def translate(self, dx, dy):
        """Translate the visible area by dx, dy pixels.

        Update the scene rect.

        Args:
            dx(int): Increments for the center x coord in pixels.
            dy(int): Increments for the center y coord in pixels.
        """
        self.setSceneRect(self.sceneRect().translated(dx, dy))

    def posFromLonLat(self, lon, lat):
        """Position in scene coordinate of the WGS84 coordinates.

        Convert from WGS84 reference system to scene reference system.

        Args:
            lon(float or numpy.ndarray): Longitude value or values.
            lat(float or numpy.ndarray): Latitude value or values.

        Returns:
            If input data is float, QPointF with the position of the input coordinate.
            If input data is array, tuple of numpy.ndarray (x, y) with the positions of the input coordinates.
        """
        zn = 1 << self._zoom
        zn = float(zn * self._tileSource.tileSize())
        tx = (lon + 180.0) / 360.0
        ty = (1.0 - log(tan(lat * PI_div_180) + 1.0 / cos(lat * PI_div_180)) / PI) / 2.0
        tx *= zn
        ty *= zn
        if type(tx) in [float, int]:
            return QPointF(tx, ty)
        return (tx, ty)

    def lonLatFromPos(self, x, y):
        """Position in WGS84 coordinate of the scene coordinates.

        Convert from scene reference system to WGS84 reference system.

        Args:
            x(float, int or numpy.ndarray): X value or values.
            y(float, int or numpy.ndarray): Y value or values.

        Returns:
            If input data is float, QPointF with the coordinate of the input position.
            If input data is array, tuple of numpy.ndarray (x, y) with the coordinates of the input positions.
        """
        tdim = float(self._tileSource.tileSize())
        tx = x / tdim
        ty = y / tdim
        zn = 1 << self._zoom
        lon = tx / zn * 360.0 - 180.0
        n = PI - PI2 * ty / zn
        lat = PI_div_180_inv * arctan(0.5 * (exp(n) - exp(-n)))
        if type(tx) in [float, int]:
            return QPointF(lon, lat)
        return (lon, lat)

    def tileFromPos(self, x, y):
        """Tile in the selected position.

        Args:
            x(float, int): X value for position.
            y(float, int): Y value for position.

        Returns:
            QPointF with the coordinates of the tile.
        """
        tdim = float(self._tileSource.tileSize())
        return QPointF(x / tdim, y / tdim)

    def addCircle(self, longitude, latitude, radius):
        """Add a new circle to the graphics scene.

        Args:
            longitude(float): Longitude of the center of the circle.
            latitude(float): Latitude of the center of the circle.
            radius(float): Longitude of the center of the circle.

        Returns:
            MapGraphicsCircleItem added to the scene.
        """
        item = MapGraphicsCircleItem(longitude, latitude, radius)
        self.addItem(item)
        return item

    def addLine(self, lon0, lat0, lon1, lat1):
        """Add a newline) to the graphics scene.

        Args:
            lon0(float): Longitude of the start point.
            lat0(float): Latitude of the start point.
            lon1(float): Longitude of the end point.
            lat1(float): Latitude of the end point.

        Returns:
            MapGraphicsLineItem added to the scene.
        """
        item = MapGraphicsLineItem(lon0, lat0, lon1, lat1)
        self.addItem(item)
        return item

    def addRect(self, lon0, lat0, lon1, lat1):
        """Add a newline) to the graphics scene.

        Args:
            lon0(float): Longitude of the top left point.
            lat0(float): Latitude of the top left point.
            lon1(float): Longitude of the bottom right point.
            lat1(float): Latitude of the bottom right point.

        Returns:
            MapGraphicsLineItem added to the scene.
        """
        item = MapGraphicsRectItem(lon0, lat0, lon1, lat1)
        self.addItem(item)
        return item

    def addPolyline(self, longitudes, latitudes):
        """Add a new circle (point) to the graphics scene.

        Args:
            longitudes(iterable): Longitudes of all the points of the polyline.
            latitudes(iterable): Latitudes of all the points of the polyline.

        Returns:
            MapGraphicsPolylineItem added to the scene.
        """
        item = MapGraphicsPolylineItem(longitudes, latitudes)
        self.addItem(item)
        return item

    def addPixmap(self, longitude, latitude, pixmap):
        """Add a new circle (point) to the graphics scene.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
            pixmap(QPixmap): Pixmap.

        Returns:
            MapGraphicsPixmapItem added to the scene.

        Note:
            Use `MapGraphicsPixmapItem.setOffset(off)` to translate by `off` pixels
            the pixmap respect the origin coordinates.
        """
        item = MapGraphicsPixmapItem(longitude, latitude, pixmap)
        self.addItem(item)
        return item

    def addText(self, longitude, latitude, text):
        """Add a test item to the graphics scene.

        Args:
            longitude(float): Longitude of the origin of the text
            latitude(float): Latitude of the origin of the text

        Returns:
            MapGraphicsTextItem added to the scene.
        """
        item = MapGraphicsTextItem(longitude, latitude, text)
        self.addItem(item)
        return item

    def addLegend(self, pos=QPointF(10.0, 10.0)):
        legend = MapLegendItem(pos=pos)
        self.addItem(legend)
        return legend
