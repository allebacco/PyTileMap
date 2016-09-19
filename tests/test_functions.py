import pytest
import numpy as np

from PyQt4.QtGui import QColor

from pytilemap.functions import makeColorFromInts


@pytest.mark.parametrize('colorArgs,qcolor', [
    ((1, 2, 3, 4), QColor(1, 2, 3, 4)),
    ((1, 2, 3), QColor(1, 2, 3, 255)),
    ((1, 2, 3), QColor(1, 2, 3)),
])
def test_color_from_ints(colorArgs, qcolor):
    color = makeColorFromInts(colorArgs)

    assert color == qcolor
