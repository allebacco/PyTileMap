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


def globalPosForCoordinate(lat, lng, zoom):
    zn = 1 << zoom    # 2**zoom
    zn = zn * float(TDIM)
    tx = (lng+180.0)/360.0
    ty = (1.0 - math.log(math.tan(lat*math.pi/180.0) + 1.0/math.cos(lat*math.pi/180.0)) / math.pi) / 2.0
    return QtCore.QPointF(tx*zn, ty*zn)


def longitudeFromTile(tx, zoom):
    zn = 1 << zoom
    lat = tx / zn * 360.0 - 180.0
    return lat


def latitudeFromTile(ty, zoom):
    zn = 1 << zoom
    n = math.pi - 2 * math.pi * ty / zn
    lng = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    return lng
