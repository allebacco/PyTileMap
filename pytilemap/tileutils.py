from __future__ import division

from numpy import log, tan, cos, arctan, exp
from numpy import pi as PI


Deg2Rad = PI / 180.0
PI2 = PI * 2.0


def posFromLonLat(lon, lat, zoom, tileSize):
    """Position in scene coordinate of the WGS84 coordinates.

    Convert from WGS84 reference system to scene reference system.

    Args:
        lon(float or numpy.ndarray): Longitude value or values.
        lat(float or numpy.ndarray): Latitude value or values.
        zoom(int): The zoom level.
        tileSize(int): The size of the tile.

    Returns:
        tuple: (x, y) with the positions of the input coordinates.
    """
    tx = (lon + 180.0) / 360.0
    ty = (1.0 - log(tan(lat * Deg2Rad) + 1.0 / cos(lat * Deg2Rad)) / PI) / 2.0
    zn = (1 << zoom) * float(tileSize)
    tx *= zn
    ty *= zn
    return tx, ty


def lonLatFromPos(x, y, zoom, tileSize):
    """Position in WGS84 coordinate of the scene coordinates.

    Convert from scene reference system to WGS84 reference system.

    Args:
        x(float, int or numpy.ndarray): X value or values.
        y(float, int or numpy.ndarray): Y value or values.
        zoom(int): The zoom level.
        tileSize(int): The size of the tile.

    Returns:
        tuple: (lon, lat) with the coordinates of the input positions.
    """
    tx = x / tileSize
    ty = y / tileSize
    zn = 1 << zoom
    lon = tx / zn * 360.0 - 180.0
    n = PI - PI2 * ty / zn
    lat = arctan(0.5 * (exp(n) - exp(-n))) / Deg2Rad
    return lon, lat
