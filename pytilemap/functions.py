import sys

import sip

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
