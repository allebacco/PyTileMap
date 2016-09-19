import sys
import sip
import numpy as np

from PyQt4.QtGui import QColor, QBrush, QPen

__all__ = [
    'getQVariantValue',
    'iterRange',
]

try:
    QVARIANT_API = sip.getapi('QVariant')
except ValueError:
    QVARIANT_API = 1

PYTHON_VERSION = sys.version_info[0]


if QVARIANT_API == 1:
    def getQVariantValue(variant):
        return variant.toPyObject()
else:
    def getQVariantValue(variant):
        return variant

if PYTHON_VERSION == 2:
    iterRange = xrange
else:
    iterRange = range


def makeColorFromInts(ints):
    r = ints[0]
    g = ints[1]
    b = ints[2]
    a = ints[3] if len(ints) == 4 else 255
    return QColor(r, g, b, a)


def makeColorFromStr(name):
    color = QColor()
    color.setNamedColor(name)
    return color


def makeColorFromFloats(floats):
    r = int(floats[0] * 255.0)
    g = int(floats[1] * 255.0)
    b = int(floats[2] * 255.0)
    a = int(floats[3] * 255.0) if len(floats) == 4 else 255
    return QColor(r, g, b, a)


def makeColorFromNdArray(array):
    dtype = array.dtype
    if dtype in [np.float32, np.float64]:
        array = np.asarray(array * 255.0, dtype=np.int32)

    colors = list()
    for row in array:
        color = makeColorFromInts(row)
        colors.append(color)
    return colors


def makeColorFromList(colorList):
    colors = list()
    if len(colorList) == 0:
        return colors

    element = colorList[0][0]
    if isinstance(element, float):
        makeFunction = makeColorFromFloats
    elif isinstance(element, int):
        makeFunction = makeColorFromInts
    else:
        makeFunction = makeColorFromStr

    for row in colorList:
        color = makeFunction(row)
        colors.append(color)
    return colors


def makeColor(args):
    makeFunction = QColor
    if isinstance(args, str):
        makeFunction = makeColorFromStr
    elif isinstance(args, tuple):
        if isinstance(args[0], int):
            makeFunction = makeColorFromInts
        else:
            makeFunction = makeColorFromFloats
    elif isinstance(args, np.ndarray):
        makeFunction = makeColorFromNdArray
    elif isinstance(args, list):
        makeFunction = makeColorFromList

    return makeFunction(args)

