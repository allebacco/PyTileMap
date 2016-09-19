import pytest
import numpy as np

from PyQt4.QtGui import QColor

from pytilemap.functions import makeColorFromInts, makeColorFromFloats, makeColorFromStr, \
    makeColorFromList, makeColorFromNdArray, makeColor


COLOR_ARG_LIST_INT = [(1, 2, 3), (1, 2, 3, 4), [1, 2, 3]]
COLOR_ARG_LIST_INT_REF = [QColor(1, 2, 3), QColor(1, 2, 3, 4), QColor(1, 2, 3)]

COLOR_ARG_LIST_FLOAT = [(0.1, 0.2, 0.3), (0.1, 0.2, 0.3, 0.4), [0.1, 0.2, 0.3]]
COLOR_ARG_LIST_FLOAT_REF = [QColor(0.1 * 255, 0.2 * 255, 0.3 * 255),
                            QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 0.4 * 255),
                            QColor(0.1 * 255, 0.2 * 255, 0.3 * 255)]

COLOR_ARG_LIST_STR = ['#FFAA11', 'green']
COLOR_ARG_LIST_STR_REF = [QColor(255, 170, 17), QColor(0, 128, 0)]

COLOR_ARG_NDARRAY_INT3 = np.asarray([[1, 2, 3], [4, 5, 6]], dtype=np.int64)
COLOR_ARG_NDARRAY_INT3_REF = [QColor(1, 2, 3), QColor(4, 5, 6)]
COLOR_ARG_NDARRAY_INT4 = np.asarray([[1, 2, 3, 4], [4, 5, 6, 7]], dtype=np.int64)
COLOR_ARG_NDARRAY_INT4_REF = [QColor(1, 2, 3, 4), QColor(4, 5, 6, 7)]

COLOR_ARG_NDARRAY_FLOAT3 = np.asarray([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float64)
COLOR_ARG_NDARRAY_FLOAT3_REF = [QColor(0.1 * 255, 0.2 * 255, 0.3 * 255),
                                QColor(0.4 * 255, 0.5 * 255, 0.6 * 255)]
COLOR_ARG_NDARRAY_FLOAT4 = np.asarray([[0.1, 0.2, 0.3, 0.4], [0.4, 0.5, 0.6, 0.7]], dtype=np.float64)
COLOR_ARG_NDARRAY_FLOAT4_REF = [QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 0.4 * 255),
                                QColor(0.4 * 255, 0.5 * 255, 0.6 * 255, 0.7 * 255)]



@pytest.mark.parametrize('colorArgs,qcolor', [
    ((1, 2, 3, 4), QColor(1, 2, 3, 4)),
    ((1, 2, 3), QColor(1, 2, 3, 255)),
    ((1, 2, 3), QColor(1, 2, 3)),
])
def test_color_from_ints(colorArgs, qcolor):
    color = makeColorFromInts(colorArgs)
    assert color == qcolor


@pytest.mark.parametrize('colorArgs,qcolor', [
    ((0.1, 0.2, 0.3, 0.4), QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 0.4 * 255)),
    ((0.1, 0.2, 0.3), QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 255)),
    ((0.1, 0.2, 0.3), QColor(0.1 * 255, 0.2 * 255, 0.3 * 255)),
])
def test_color_from_floats(colorArgs, qcolor):
    color = makeColorFromFloats(colorArgs)
    assert color == qcolor


@pytest.mark.parametrize('colorArgs,qcolor', [
    ('#FFAA11', QColor(255, 170, 17)),
    ('green', QColor(0, 128, 0)),
])
def test_color_from_strings(colorArgs, qcolor):
    color = makeColorFromStr(colorArgs)
    assert color == qcolor


@pytest.mark.parametrize('colorArgs,qcolor', [
    (COLOR_ARG_LIST_INT, COLOR_ARG_LIST_INT_REF),
    (COLOR_ARG_LIST_FLOAT, COLOR_ARG_LIST_FLOAT_REF),
    (COLOR_ARG_NDARRAY_INT3, COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT3.astype(np.int32), COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT4, COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_INT4.astype(np.int32), COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT3, COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT3.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT4, COLOR_ARG_NDARRAY_FLOAT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT4.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT4_REF),
])
def test_color_from_list(colorArgs, qcolor):
    color = makeColorFromList(colorArgs)
    assert color == qcolor


@pytest.mark.parametrize('colorArgs,qcolor', [
    (COLOR_ARG_NDARRAY_INT3, COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT3.astype(np.int32), COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT4, COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_INT4.astype(np.int32), COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT3, COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT3.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT4, COLOR_ARG_NDARRAY_FLOAT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT4.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT4_REF),
])
def test_color_from_ndarray(colorArgs, qcolor):
    color = makeColorFromNdArray(colorArgs)
    assert color == qcolor


@pytest.mark.parametrize('colorArgs,qcolor', [
    ((1, 2, 3, 4), QColor(1, 2, 3, 4)),
    ((1, 2, 3), QColor(1, 2, 3, 255)),
    ((0.1, 0.2, 0.3, 0.4), QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 0.4 * 255)),
    ((0.1, 0.2, 0.3), QColor(0.1 * 255, 0.2 * 255, 0.3 * 255, 255)),
    ('#FFAA11', QColor(255, 170, 17)),
    ('green', QColor(0, 128, 0)),
    (COLOR_ARG_LIST_INT, COLOR_ARG_LIST_INT_REF),
    (COLOR_ARG_LIST_FLOAT, COLOR_ARG_LIST_FLOAT_REF),
    (COLOR_ARG_NDARRAY_INT3, COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT3.astype(np.int32), COLOR_ARG_NDARRAY_INT3_REF),
    (COLOR_ARG_NDARRAY_INT4, COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_INT4.astype(np.int32), COLOR_ARG_NDARRAY_INT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT3, COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT3.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT3_REF),
    (COLOR_ARG_NDARRAY_FLOAT4, COLOR_ARG_NDARRAY_FLOAT4_REF),
    (COLOR_ARG_NDARRAY_FLOAT4.astype(np.float32), COLOR_ARG_NDARRAY_FLOAT4_REF),
])
def test_color_default(colorArgs, qcolor):
    color = makeColor(colorArgs)
    assert color == qcolor
