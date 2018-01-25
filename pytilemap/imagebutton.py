from __future__ import print_function, absolute_import

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QGraphicsObject, QGraphicsItemGroup, QGraphicsPixmapItem

class ImageButton(QGraphicsObject):
    '''
    Custom Image Holder Class that Allows for event handling -
        - QGraphicsPixmapItem is not a QObject, so cannot catch events.
    '''
    QtParentClass = QGraphicsObject

    clicked = Signal(int)

    def __init__(self, img, parent=None):
        '''
        Args:
            img: A QPixmap instance

        Keyword Args:
            parent: A pyqt window instance
        '''
        QGraphicsObject.__init__(self, parent=parent)
        self.image = QGraphicsPixmapItem(img, parent=self)
        self.parent = parent

    def paint(self, painter, option, widget):
        self.image.paint(painter,option,widget) 

    def boundingRect(self):
        return self.image.boundingRect()

    def mouseReleaseEvent(self, event):
        self.clicked.emit(1)
        
    def mousePressEvent(self, event):
        pass
# end ImageButton

