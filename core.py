from PyQt5.QtCore import Qt, QRect, QSize, QObject, QPoint, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QColor

# I was trying to load json with parameters here
# But I can only use just one external lib, so...
CONFIG = {
    "rectSize": QSize(100, 50),
    "hitPointRadius": 10,
    "rounding": 5
}


class Rect(QObject):
    """
    Rect object keeps information about
    rect size, color and position
    """

    def __init__(self, id_: int, centerPoint: QPoint, *args, **kwargs):
        super(Rect, self).__init__(*args, **kwargs)
        self.id_ = id_
        size = QSize(CONFIG.get("rectSize"))

        # rect was create by mouse click, so we need to get
        # top-left point from center point
        pos = QPoint(centerPoint.x() - size.width()/2,
                     centerPoint.y() - size.height()/2)
        self._rect = QRect(pos, size)
        # create a random color for rect
        self.setColor()

    @staticmethod
    def createRandomColor():
        return QColor(Qt.red)

    def move(self, delta: QPoint):
        self._rect.moveTo(self._rect.topLeft() + delta)

    # region PROPERTIES:
    def setColor(self, value=None):
        if not value:
            # TODO: create random color by spinngin HSL wheel
            value = QColor(Qt.red)
        self._color = value

    def getColor(self):
        return self._color

    def getRect(self):
        return self._rect

    color = pyqtProperty(QColor, getColor, setColor)
    rect = pyqtProperty(QRect, getRect)
    # endregion


class Model(QObject):
    """ Model stores information about game field and objects on it """
    # SIGNALS
    # somethingChanged emits when model is changed and view should be re-painted
    somethingChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.rects = []
        self.links = []

    def createLink(self, startId: int, endId: int):
        """
        Create new links between two rects
        :param startId: id of the first rect
        :param endId: id of the second rect
        """
        # check if link is already existing
        if endId in self.links[startId]:
            # delete existing connection
            self.links[startId].discard(endId)
            self.links[endId].discard(startId)
        else:
            self.links[startId].add(endId)
            self.links[endId].add(startId)
            self.somethingChanged.emit()

    def createRect(self, pos: QPoint):
        """
        Create new rect and empty set in links list
        :param pos: position of the center of future rect
        """
        # create rect object
        # new rect's id is equal to length of current self.rects list
        # so I can easily found a connections inside
        # connection list without any computation cost
        newRect = Rect(id_=len(self.rects),
                       centerPoint=pos)
        # put new rect into list of rects
        self.rects.append(newRect)
        # and create new links set for possible links
        self.links.append(set())
        self.somethingChanged.emit()

    def isHitting(self, rect: QRect, id_: int = None):
        """ checks if rect in this point would hit another """
        # if any of existing rects collide with testing one
        # then exit function with True
        # otherwise return False (it means movement or creating is allowed)
        for existingRect in self.rects:
            if existingRect.rect.intersects(rect) and id_ != existingRect.id_:
                return True
        return False

