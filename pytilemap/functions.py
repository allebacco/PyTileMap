import sys

try:
    from PyQt4.QtCore import QVariant
    HAS_QVARIANT = True
except ImportError:
    HAS_QVARIANT = False

PYTHON_VERSION = sys.version_info[0]


__all__ = [
    'getQVariantValue',
    'iterRange',
]


if HAS_QVARIANT:
    def getQVariantValue(variant):
        return variant.toPyObject()
else:
    def getQVariantValue(variant):
        return variant

if PYTHON_VERSION == 2:
    iterRange = xrange
else:
    iterRange = range
