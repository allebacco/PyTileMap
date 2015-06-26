#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

'''
*****************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies)
** Contact: Qt Software Information (qt-info@nokia.com)
**
** Copyright (C) 2010 Mitja Kleider <mitja@kleider.name>
**
** This file may be used under the terms of the GNU General Public
** License version 3.0 as published by the Free Software Foundation
** Please review the following information to ensure GNU
** General Public Licensing requirements will be met:
** http://www.gnu.org/copyleft/gpl.html.
**
** This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
** WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
**
*****************************************************************************
'''

import sys
from PyQt4 import QtCore, QtGui

from osm import OsmTile
from here import HereTile

from items import TileMapItemPoint, TileMapItemLine


class TileMap(QtGui.QWidget):

    def __init__(self, parent=None, pressed=False, invert=False):
        QtGui.QWidget.__init__(self)

        self.pressed = pressed
        self.invert = invert

        self.pressPos = QtCore.QPoint()

        self.m_normalMap = HereTile(self)
        self.m_normalMap.updated.connect(self.updateMap)

        self.items = list()

    def addItem(self, item):
        self.items.append(item)

        tl = self.m_normalMap.rect.topLeft()
        zoom = self.m_normalMap.zoom
        item.updatePosition(tl, zoom)

        self.update()

    def addPoint(self, lat, lon, radius=None, color=None):
        point = TileMapItemPoint(lat, lon)
        if radius is not None:
            point.radius = radius
        if color is not None:
            point.brush.setColor(color)
        self.addItem(point)
        return point

    def addLine(self, lat1, lon1, lat2, lon2, width=None, color=None):
        line = TileMapItemLine(lat1, lon1, lat2, lon2)
        if width is not None:
            line.pen.setWidth(width)
        if color is not None:
            line.pen.setColor(color)
        self.addItem(line)
        return line

    def addLines(self, latLonList, width=None, color=None):
        lines = []
        for i in xrange(1, len(latLonList)):
            p1 = latLonList[i-1]
            p2 = latLonList[i]
            line = TileMapItemLine(p1[0], p1[1], p2[0], p2[1])
            if width is not None:
                line.pen.setWidth(width)
            if color is not None:
                line.pen.setColor(color)
            self.addItem(line)
            lines.append(line)
        return lines

    def clear(self):
        self.items = list()
        self.update()

    def setCenter(self, lat, lon):
        self.m_normalMap.setCenter(lat, lon)
        self.updateItemsPosition()

    def toggleNightMode(self):
        self.invert = not self.invert
        self.update()

    def updateMap(self, rect):
        self.update(rect)

    def resizeEvent(self, event):
        self.m_normalMap.width = self.width()
        self.m_normalMap.height = self.height()
        self.m_normalMap.invalidate()
        self.updateItemsPosition()

    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        self.m_normalMap.render(p, event.rect())
        p.setPen(QtCore.Qt.black)
        p.drawText(self.rect(), QtCore.Qt.AlignBottom | QtCore.Qt.TextWordWrap,
                   "Map data CCBYSA 2010 OpenStreetMap.org contributors")
        p.end()

        if self.invert:
            p = QtGui.QPainter(self)
            p.setCompositionMode(QtGui.QPainter.CompositionMode_Difference)
            p.fillRect(event.rect(), QtCore.Qt.white)
            p.end()

        p.begin(self)
        for item in self.items:
            item.render(p, event.rect())
        p.end()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.pressPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons():
            delta = event.pos() - self.pressPos
            self.pressPos = event.pos()
            self.pan(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.pan(20, 0)
        elif event.key() == QtCore.Qt.Key_Right:
            self.pan(-20, 0)
        elif event.key() == QtCore.Qt.Key_Up:
            self.pan(0, 20)
        elif event.key() == QtCore.Qt.Key_Down:
            self.pan(0, -20)
        elif event.key() == QtCore.Qt.Key_Plus:
            self.m_normalMap.zoomIn()
        elif event.key() == QtCore.Qt.Key_Minus:
            self.m_normalMap.zoomOut()

    def pan(self, dx, dy):
        self.m_normalMap.pan(QtCore.QPoint(dx, dy))
        for item in self.items:
            item.move(dx, dy)

    def zoomIn(self):
        self.m_normalMap.zoomIn()
        self.updateItemsPosition()

    def zoomOut(self):
        self.m_normalMap.zoomOut()
        self.updateItemsPosition()

    def updateItemsPosition(self):
        tl = self.m_normalMap.rect.topLeft()
        zoom = self.m_normalMap.zoom
        for item in self.items:
            item.updatePosition(tl, zoom)

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.zoomIn()
        else:
            self.zoomOut()
