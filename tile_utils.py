import math
from PyQt4 import QtCore

TDIM = 256

MIN_ZOOM = 2
MAX_ZOOM = 18


def qHash(point):
    '''Qt doesn't implement a qHash() for QPoint.'''
    return (point.x(), point.y())


def tileForCoordinate(lat, lng, zoom):
    zn = 1 << zoom    # 2**zoom
    tx = (lng+180.0)/360.0
    ty = (1.0 - math.log(math.tan(lat*math.pi/180.0) + 1.0/math.cos(lat*math.pi/180.0)) / math.pi) / 2.0
    return QtCore.QPointF(tx*zn, ty*zn)


def globalPosForCoordinate(lat, lng, zoom, tileSize=TDIM):
    zn = 1 << zoom    # 2**zoom
    zn = zn * tileSize
    tx = (lng+180.0)/360.0
    ty = (1.0 - math.log(math.tan(lat*math.pi/180.0) + 1.0/math.cos(lat*math.pi/180.0)) / math.pi) / 2.0
    return QtCore.QPointF(tx*zn, ty*zn)


def posForCoordinate(lat, lng, zoom, tileSize=TDIM):
    zn = 1 << zoom    # 2**zoom
    zn = zn * tileSize
    tx = (lng+180.0)/360.0
    ty = (1.0 - math.log(math.tan(lat*math.pi/180.0) + 1.0/math.cos(lat*math.pi/180.0)) / math.pi) / 2.0
    return QtCore.QPointF(tx*zn, ty*zn)


def lonLatFromPos(x, y, zoom, tileSize=TDIM):
    tx = x / float(tileSize)
    ty = y / float(tileSize)

    zn = 1 << zoom
    lon = tx / zn * 360.0 - 180.0
    n = math.pi - 2 * math.pi * ty / zn
    lat = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    return QtCore.QPointF(lon, lat)


def tileFromPos(x, y, zoom, tileSize=TDIM):
    tx = x / float(tileSize)
    ty = y / float(tileSize)
    return QtCore.QPointF(tx, ty)


def longitudeFromTile(tx, zoom):
    zn = 1 << zoom
    lon = tx / zn * 360.0 - 180.0
    return lon


def latitudeFromTile(ty, zoom):
    zn = 1 << zoom
    n = math.pi - 2 * math.pi * ty / zn
    lat = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    return lat
