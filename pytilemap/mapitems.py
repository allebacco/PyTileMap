from __future__ import print_function, absolute_import

import numpy as np

from qtpy.QtCore import Qt, QLineF, QPointF, QRectF, QSize
from qtpy.QtGui import QPainterPath, QPen, QBrush, QColor, QTransform, QPolygonF
from qtpy.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsItemGroup, \
    QGraphicsSimpleTextItem, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QMenu, QAction

#from qtpy.QtWidgets import QGraphicsSvgItem
from qtpy.QtSvg import QGraphicsSvgItem, QSvgRenderer

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
        self.setFlags(QGraphicsItem.ItemIsMovable)

        self._lon    = longitude
        self._lat    = latitude
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

    def hideLabel(self):
        if not self._label_item:
            return
        self.scene().removeItem(self._label_item)
        self._label_item = None

class MapGraphicsRectShapeItem(QGraphicsRectItem, MapItem):
    """Circle item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsRectItem

    def __init__(self, lon, lat, width, height, parent=None):
        """Constructor.

        Args:
            lon0(float): Longitude of the center point
            lat0(float): Latitude of the center point
            width(int): width in pixels
            height(int): height in pixels
            parent(QGraphicsItem): Parent item, default None.

        """
        QGraphicsRectItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon    = lon
        self._lat    = lat
        self._width  = width
        self._height = height

    def updatePosition(self, scene):
        """Update the position of the circle.

        Args:
            scene(MapGraphicsScene): Scene to which the circle belongs.
        """
        pos = scene.posFromLonLat(self._lon, self._lat)

        self.prepareGeometryChange()
        # This object is centered on the lat lon point, so shift it by half width/height
        rect = QRectF(pos[0]-self._height//2, pos[1]-self._width//2, self._width, self._height)
        self.setRect(rect)
        self.setPos(QPointF(0.0, 0.0))

    def setLonLat(self, lon, lat):
        self._lon = lon
        self._lat = lat
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())


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
        width = abs(int(pos1[0] - pos0[0]))
        height= abs(int(pos0[1] - pos1[1]))

        self.prepareGeometryChange()
        rect = QRectF(pos0[0], pos0[1], width, height)
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

class MapGraphicsGeoSvgItem(QGraphicsSvgItem, MapItem):

    QtParentClass = QGraphicsSvgItem

    def __init__(self, lon0, lat0, lon1, lat1, svg_filename, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the upper left corner
            latitude(float): Latitude of the upper left corner
            longitude(float): Longitude of the lower right corner
            latitude(float): Latitude of the lower right corner
            svg_filename: Svg file name
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.

        This will display an svg file with the corners geo-registered
        """
        QGraphicsSvgItem.__init__(self, svg_filename, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        self._xsize = 0
        self._ysize = 0
        
        self.x_mult = 1
        self.y_mult = 1
        self._renderer = QSvgRenderer(svg_filename);
        self._border = QGraphicsRectItem(parent=self)
        self._border.setPen(Qt.black)

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        self.prepareGeometryChange()
        xsize = abs(int(pos1[0] - pos0[0]))
        ysize = abs(int(pos0[1] - pos1[1]))

        rect   = scene.sceneRect()
        x      = rect.x()
        y      = rect.y()
        width  = rect.width()
        height = rect.height()
        self.ul_x = min(pos0[0], pos1[0])
        self.ul_y = min(pos0[1], pos1[1])
        self.lr_x = max(pos0[0], pos1[0])
        self.lr_y = max(pos0[1], pos1[1])
        #self.scale(width, height)

        #print ("screen rect: {0}:{1}, {2}:{3}".format(int(x), int(x+width), int(y), int(y+height)),   
        #       "img rect: {0}:{1}, {2}:{3}".format(int(self.ul_x), int(self.lr_x), int(self.ul_y), int(self.lr_y)))

        #if xsize != self._xsize or ysize != self._ysize:
        self._xsize = xsize
        self._ysize = ysize
        self.ul_x = min(pos0[0], pos1[0])
        self.ul_y = min(pos0[1], pos1[1])
        self.setPos(self.ul_x, self.ul_y)

    # Scaled approach - does weird smoothing
    def paint(self, painter, option, widget=None):
        #print (self.x_mult, self.y_mult, self.orig_pixmap.width(), self.orig_pixmap.height())
        self._renderer.render(painter, QRectF(0,0, self._xsize, self._ysize))
    
    def boundingRect(self):
        return QRectF(0, 0, self._xsize, self._ysize)

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

# end MapGraphicsGeoSvg

class MapGraphicsGeoPixmapItemCorners(QGraphicsPixmapItem, MapItem):
    '''
    A pixmap that has all 4 corners specified so it warps to the map
    '''

    QtParentClass = QGraphicsPixmapItem

    def __init__(self, lon0, lat0, lon1, lat1,
                 lon2, lat2, lon3, lat3, pixmap, parent=None):
        """Constructor.

        Args:
            lon0(float): Longitude (decimal degrees) of the upper left corner of the image
            lat0(float): Latitude of the upper left corner of the image
            lon1(float): longitude of the next point clockwise
            lat0(float): latitude of the next point clockwise
            lon2(float): longitude of the next point clockwise
            lat2(float): longitude of the next point clockwise
            lon3(float): latitude of the next point clockwise
            lat3(float): latitude of the next point clockwise
            pixmap(QPixmap): Pixmap.
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.

        Show a pixamp with geo-registered corners
        """
        QGraphicsPixmapItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        self._lon2 = lon2
        self._lat2 = lat2
        self._lon3 = lon3
        self._lat3 = lat3
        self._xsize = 0
        self._ysize = 0
        self.setPixmap(pixmap)
        self.setShapeMode(1)
        self.x_mult = 1
        self.y_mult = 1

    def updatePosition(self, scene):

        # 1. Get pix coords for each lat/lon point
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        pos2 = scene.posFromLonLat(self._lon2, self._lat2)
        pos3 = scene.posFromLonLat(self._lon3, self._lat3)
        self.prepareGeometryChange()

        # Set the image to 0, 0, then use a transform to 
        #   to translate, rotate and warp it to the map

        # tranfsorm and scale
        self.setPos(0, 0)
        t = QTransform()
        poly1 = QPolygonF()

        w = self.pixmap().width()
        h = self.pixmap().height()

        poly1.append(QPointF( 0, 0 ))
        poly1.append(QPointF( w, 0 ))
        poly1.append(QPointF( w, h ))
        poly1.append(QPointF( 0, h ))

        poly2 = QPolygonF()
        poly2.append(QPointF(pos0[0], pos0[1]))
        poly2.append(QPointF(pos1[0], pos1[1]))
        poly2.append(QPointF(pos2[0], pos2[1]))
        poly2.append(QPointF(pos3[0], pos3[1]))
        success = QTransform.quadToQuad(poly1, poly2, t)
        if not success:
            logging.error('Unable to register image')
            
        self.setTransform(t)


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




class MapGraphicsGeoPixmapItem(QGraphicsPixmapItem, MapItem):

    QtParentClass = QGraphicsPixmapItem

    def __init__(self, lon0, lat0, lon1, lat1, pixmap, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the upper left corner
            latitude(float): Latitude of the upper left corner
            longitude(float): Longitude of the lower right corner
            latitude(float): Latitude of the lower right corner
            pixmap(QPixmap): Pixmap.
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.

        Show a pixamp with geo-registered corners
        """
        QGraphicsPixmapItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        self._xsize = 0
        self._ysize = 0
        
        self.orig_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setShapeMode(1)
        self.x_mult = 1
        self.y_mult = 1

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        self.prepareGeometryChange()
        xsize = abs(int(pos1[0] - pos0[0]))
        ysize = abs(int(pos0[1] - pos1[1]))

        rect   = scene.sceneRect()
        x      = rect.x()
        y      = rect.y()
        width  = rect.width()
        height = rect.height()
        self.ul_x = min(pos0[0], pos1[0])
        self.ul_y = min(pos0[1], pos1[1])
        self.lr_x = max(pos0[0], pos1[0])
        self.lr_y = max(pos0[1], pos1[1])


        #if xsize != self._xsize or ysize != self._ysize:
        self._xsize = xsize
        self._ysize = ysize
        self.x_mult = xsize / self.orig_pixmap.width()
        self.y_mult = ysize / self.orig_pixmap.width()
        if 1:
            newscale = QSize(xsize, ysize)
            scaled = self.orig_pixmap.scaled(newscale)
            self.setPixmap(scaled) 
        self.ul_x = min(pos0[0], pos1[0])
        self.ul_y = min(pos0[1], pos1[1])
        self.setPos(self.ul_x, self.ul_y)


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
            longitude(float): Longitude of the center of the pixmap
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
        pos = scene.posFromLonLat(self._lon, self._lat)
        self.prepareGeometryChange()
        rect = self.boundingRect()
        w = rect.width()
        h = rect.height()
        self.setPos(pos[0] - h//2, pos[1] -w//2)
        if self._label_item:
            self._label_item.updatePosition(scene)

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
        for i in iterRange(0, len(lines)):
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

