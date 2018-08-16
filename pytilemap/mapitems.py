from __future__ import print_function, absolute_import

import numpy as np

from qtpy.QtCore import Qt, QLineF, QPointF, QRectF, QSize
from qtpy.QtGui import QPainterPath, QPen, QBrush, QColor
from qtpy.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsItemGroup, \
    QGraphicsSimpleTextItem, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

from .functions import iterRange, makePen, izip
from .qtsupport import getQVariantValue

SolidLine = Qt.SolidLine


class MapItem(object):
    """Base class for each item in the MapGraphicScene

    The default implementation connects the MapGraphicScene.sigZoomChanged() signal
    to the MapItem.setZoom() slot. This slot call the MapItem.updatePosition() method
    for updating the position of the item in reaction to a change in the zoom level.
    """

    QtParentClass = None

    def __init__(self):
        if not isinstance(self, QGraphicsItem):
            raise RuntimeError('MapItem must be an instance of QGraphicsItem')

        self._label = "label"
        self._label_item = None
        self._label_html = False

    def itemChange(self, change, value):
        if change == self.ItemSceneChange:
            # Disconnect the old scene, if any
            oldScene = self.scene()
            if oldScene is not None:
                oldScene.sigZoomChanged.disconnect(self.setZoom)
            # Connect the new scene, if any
            newScene = getQVariantValue(value)
            if newScene is not None:
                newScene.sigZoomChanged.connect(self.setZoom)

            # Notify the item that the scene is changed
            self._sceneChanged(oldScene, newScene)

            # Setup the new position of the item
            if newScene is not None:
                self.updatePosition(newScene)

        return self.QtParentClass.itemChange(self, change, value)

    def _sceneChanged(self, oldScene, newScene):
        """Called when the current scene change.


        This function can be reimplemented for notifying that the scene has changed.
        The function is called when the scene has changed, just before the
        :meth:`~updatePosition` method.

        Default

        Args:
            oldScene (QGraphicsScene): The old scene, or ``None``.
            newScene (QGraphicsScene): The new scene, or ``None``.

        Note:
            :meth:`~scene` method is pointing to the ``oldScene``.
        """
        pass

    def setZoom(self, zoom):
        '''Set a new zoom level.

        Args:
            zoom (int): The new zoom level.
        '''
        scene = self.scene()
        self.updatePosition(scene)

    def updatePosition(self, scene):
        raise NotImplementedError()

    def setLabel(self, label, html=False):
        self._label = label
        self._label_html = html

    def getLabelLocation(self):
        ''' Get label location for this object

        Args:
            none

        Returns:
            (pos x, pos y) : position of label in pixels
        '''
        rect = self.getGeoRect()
        br = rect.bottomRight()
        pos = (br.x(), br.y())
        return pos

    def getGeoRect(self):
        ''' Get bounding rectangle for this obj

        Args:
            none

        Returns:
            QRectF: (px x, px y, w, h)
        '''
        return self.boundingRect()

    def showLabel(self):
        ''' Show label for this object, if html is indicated, display formatted'''
        if self._label_item:
            return
        self._label_item = MapGraphicsLabelItem(self, self._label)
        if self._label_html:
            self._label_item.setHtml(self._label)
        self.scene().addItem(self._label_item)
    
    def hideLabel(self):
        ''' Hide label for this object'''
        if not self._label_item:
            return
        self.scene().removeItem(self._label_item)
        self._label_item = None



class MapGraphicsCircleItem(QGraphicsEllipseItem, MapItem):
    """Circle item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsEllipseItem

    def __init__(self, longitude, latitude, radius, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the center of the circle.
            latitude(float): Latitude of the center of the circle.
            radius(float): Radius of the circle in pixels.
            scene(MapGraphicsScene): Scene to which the circle belongs.
            parent(QGraphicsItem): Parent item, default None.

        Note:
            The management of the parent item is work in progress.
        """
        QGraphicsEllipseItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon = longitude
        self._lat = latitude
        self._radius = radius

    def updatePosition(self, scene):
        """Update the position of the circle.

        Args:
            scene(MapGraphicsScene): Scene to which the circle belongs.
        """
        pos = scene.posFromLonLat(self._lon, self._lat)
        r = self._radius
        d = r * 2
        self.prepareGeometryChange()
        self.setRect(pos[0] - r, pos[1] - r, d, d)

    def setLonLat(self, longitude, latitude):
        """Set the center coordinates of the circle.

        Args:
            longitude(float): Longitude of the center of the circle.
            latitude(float): Latitude of the center of the circle.
        """
        self._lon = longitude
        self._lat = latitude
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)
        if self._label_item:
            self._label_item.updatePosition(scene)

    def setRadius(self, radius):
        self._radius = radius
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)

    def mousePressEvent(self, evt):
        print ("ellipse clicked!") 
        self.setLonLat(self._lon+0.0001, self._lat+0.0001)
    
    def hideLabel(self):
        if not self._label_item:
            return
        self.scene().removeItem(self._label_item)
        self._label_item = None


class MapGraphicsRectItem(QGraphicsRectItem, MapItem):
    """Circle item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsRectItem

    def __init__(self, lon0, lat0, lon1, lat1, parent=None):
        """Constructor.

        Args:
            lon0(float): Longitude of the top left point.
            lat0(float): Latitude of the top left point.
            lon1(float): Longitude of the bottom right point.
            lat1(float): Latitude of the bottom right point.
            parent(QGraphicsItem): Parent item, default None.

        Note:
            The management of the parent item is work in progress.
        """
        QGraphicsRectItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

    def updatePosition(self, scene):
        """Update the position of the circle.

        Args:
            scene(MapGraphicsScene): Scene to which the circle belongs.
        """
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)

        self.prepareGeometryChange()
        rect = QRectF(pos0, pos1).normalized()
        self.setRect(rect)
        self.setPos(QPointF(0.0, 0.0))

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())




class MapGraphicsLineItem(QGraphicsLineItem, MapItem):

    QtParentClass = QGraphicsLineItem

    def __init__(self, lon0, lat0, lon1, lat1, parent=None):
        QGraphicsLineItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        deltaPos = QPointF(pos1[0] - pos0[0], pos1[1] - pos0[1])

        self.prepareGeometryChange()
        self.setLine(QLineF(QPointF(0.0, 0.0), deltaPos))
        self.setPos(pos0[0], pos0[1])

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())



class MapGraphicsPolylineItem(QGraphicsPathItem, MapItem):

    QtParentClass = QGraphicsPathItem

    def __init__(self, longitudes, latitudes, parent=None):
        QGraphicsPathItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes, dtype=np.float64)
        self._latitudes = np.array(latitudes, dtype=np.float64)

    def updatePosition(self, scene):
        path = QPainterPath()

        self.prepareGeometryChange()

        count = len(self._longitudes)
        if count > 0:
            x, y = scene.posFromLonLat(self._longitudes, self._latitudes)
            path.moveTo(x[0], y[0])
            for i in iterRange(1, count):
                path.lineTo(x[i], y[i])

        self.setPath(path)

    def setLonLat(self, longitudes, latitudes):
        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes, dtype=np.float64)
        self._latitudes = np.array(latitudes, dtype=np.float64)
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)


    def mousePressEvent(self, evt):
        print ("poly line clicked!") #QGraphicsSceneMouseEvent *event)

class MapGraphicsGeoPixmapItem(QGraphicsPixmapItem, MapItem):

    QtParentClass = QGraphicsPixmapItem

    def __init__(self, lon0, lat0, lon1, lat1, pixmap, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
            pixmap(QPixmap): Pixmap.
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.
        """
        QGraphicsPixmapItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        
        self.orig_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setShapeMode(1)

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        self.prepareGeometryChange()
        xsize = abs(int(pos1[0] - pos0[0]))
        ysize = abs(int(pos0[1] - pos1[1]))
        newscale = QSize(xsize, ysize)
        scaled = self.orig_pixmap.scaled(newscale)
        self.setPixmap(scaled) 
        ul_x = min(pos0[0], pos1[0])
        ul_y = min(pos0[1], pos1[1])
        self.setPos(ul_x, ul_y)

    def getGeoRect(self):
        ''' get geo referenced rectangle for this object

        Returns:
            QRectF (upper left x, upper left y, width, height)
        '''
        pos0 = self.scene().posFromLonLat(self._lon0, self._lat0)
        pos1 = self.scene().posFromLonLat(self._lon1, self._lat1)
        xsize = abs(int(pos1[0] - pos0[0]))
        ysize = abs(int(pos0[1] - pos1[1]))
        ul_x = min(pos0[0], pos1[0])
        ul_y = min(pos0[1], pos1[1])
        rect = QRectF(ul_x, ul_y, xsize, ysize)
        return rect


    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())

# end MapGraphicsGeoPixmap




class MapGraphicsPixmapItem(QGraphicsPixmapItem, MapItem):
    """Item for showing a pixmap in a MapGraphicsScene.
    """

    QtParentClass = QGraphicsPixmapItem

    def __init__(self, longitude, latitude, pixmap, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
            pixmap(QPixmap): Pixmap.
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.
        """
        QGraphicsPixmapItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon = longitude
        self._lat = latitude
        self.setPixmap(pixmap)

    def getGeoRect(self):
        ''' get geo referenced rectangle for this object

        Returns:
            QRectF (upper left x, upper left y, width, height)
        '''
        rect = self.boundingRect() 
        pos = self.scene().posFromLonLat(self._lon, self._lat)
        w = rect.width()
        h = rect.height()
        rect2 = QRectF(pos[0], pos[1], w, h )
        return rect2


    def updatePosition(self, scene):
        """Update the origin position of the item.

        Origin coordinates are unchanged.

        Args:
            scene(MapGraphicsScene): Scene the item belongs to.
        """
        print ("here")
        pos = scene.posFromLonLat(self._lon, self._lat)
        self.prepareGeometryChange()
        self.setPos(pos[0], pos[1])
        if self._label_item:
            self._label_item.updatePosition(scene)
            print ("updated label item")

    def setLonLat(self, longitude, latitude):
        """Update the origin coordinates of the item.

        Origin position will be updated.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
        """
        self._lon = longitude
        self._lat = latitude
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)

    def mousePressEvent(self, evt):
        print ("image clicked!") #QGraphicsSceneMouseEvent *event)
        #------- pop up a text item here
        # First, a rectangle


class MapGraphicsTextItem(QGraphicsTextItem, MapItem):
    """Text item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsSimpleTextItem

    def __init__(self, longitude, latitude, text, parent=None, min_zoom_visibility=None):
        QGraphicsSimpleTextItem.__init__(self, text, parent=parent)
        MapItem.__init__(self)
        self._min_zoom = min_zoom_visibility
        self._lon, self._lat = longitude, latitude
        self._border = QGraphicsRectItem(parent=self)
        self._border.setPen(QPen(Qt.NoPen))
        self._border.setBrush(QBrush(QColor(190, 190, 190, 160)))

    def resetMinZoomVisibility(self):
        """Delete level of zoom under which the text disappears. """
        self._min_zoom = None

    def setMinZoomVisibility(self, zoom_level):
        """Update level of zoom under which the text disappears. """
        self._min_zoom = zoom_level

    def updatePosition(self, scene):
        """Update the origin position of the item."""

        pos = scene.posFromLonLat(self._lon, self._lat)
        self.setPos(pos[0], pos[1])
        if self._min_zoom is not None:
            self.setVisible(scene._zoom >= self._min_zoom)
        #rect = super(MapGraphicsTextItem, self).boundingRect()
        #self._border.setRect()

class MapGraphicsLabelItem(QGraphicsTextItem, MapItem):
    """ Label for an item - updates its position with the item
    """

    QtParentClass = QGraphicsSimpleTextItem

    def __init__(self, other_item, text, parent=None, min_zoom_visibility=None):
        QGraphicsSimpleTextItem.__init__(self, text, parent=parent)
        MapItem.__init__(self)
        self.other_item = other_item
        self._min_zoom = min_zoom_visibility
        self._border = QGraphicsRectItem(parent=self)
        self._border.setPen(QPen(Qt.NoPen))
        self._border.setBrush(QBrush(QColor(190, 190, 190, 160)))

    def resetMinZoomVisibility(self):
        """Delete level of zoom under which the text disappears. """
        self._min_zoom = None

    def setMinZoomVisibility(self, zoom_level):
        """Update level of zoom under which the text disappears. """
        self._min_zoom = zoom_level

    def updatePosition(self, scene):
        """Update the origin position of the item."""
        pos = self.other_item.getLabelLocation()
        self.setPos(pos[0], pos[1])
        if self._min_zoom is not None:
            self.setVisible(scene._zoom >= self._min_zoom)


class MapGraphicsLinesGroupItem(QGraphicsItem, MapItem):

    QtParentClass = QGraphicsItem

    def __init__(self, longitudes, latitudes, parent=None):
        QGraphicsItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        assert len(longitudes) == len(latitudes)
        assert len(longitudes) >= 2

        self._longitudes = np.array(longitudes, dtype=np.float64)
        self._latitudes = np.array(latitudes, dtype=np.float64)

        # Setup internal lines
        linesGroup = QGraphicsItemGroup(parent=self)
        self._linesGroup = linesGroup
        self._lines = [QGraphicsLineItem(parent=linesGroup) for i in iterRange(len(longitudes)-1)]

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self._linesGroup.boundingRect()

    def setLineStyle(self, colors, width=1., style=SolidLine):
        pen = makePen(colors, width=width, style=style)

        if isinstance(pen, list):
            if len(pen) != len(self._lines):
                raise ValueError('The number of colors must be equal to the number of lines')
            for line, p in izip(self._lines, pen):
                line.setPen(p)
        else:
            for line in self._lines:
                line.setPen(pen)

    def updatePosition(self, scene):
        self.prepareGeometryChange()

        x, y = scene.posFromLonLat(self._longitudes, self._latitudes)
        lines = self._lines
        for i in iterRange(0, len(lines)-1):
            lines[i].setLine(x[i], y[i], x[i+1], y[i+1])

    def setLonLat(self, longitudes, latitudes):
        assert len(longitudes) == len(latitudes)
        assert len(longitudes) >= 2

        self._longitudes = np.array(longitudes, dtype=np.float64)
        self._latitudes = np.array(latitudes, dtype=np.float64)

        old_lines = self._lines
        for line in old_lines:
            line.setParentItem(None)

        scene = self.scene()
        if scene is not None:
            for line in old_lines:
                scene.removeItem(line)

        linesGroup = self._linesGroup
        self._lines = [QGraphicsLineItem(parent=linesGroup) for i in iterRange(len(longitudes)-1)]

        if scene is not None:
            self.updatePosition(scene)

    def __getitem__(self, index):
        return self._lines[index]

