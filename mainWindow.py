from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout
from PyQt5.QtCore import QRect, QPoint, Qt,  pyqtProperty
from PyQt5.QtGui import QPainter, QPen, QBrush, QPalette
from PyQt5 import QtGui

from core import Model, CONFIG


class MainWindow(QMainWindow):
    """
    Main Windows handles a canvas
    which I would use as drawing surface.
    This window also handles all mouse events
    """

    def __init__(self, model: Model, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # link to the model object with all things to draw
        self.model = model

        # help message
        self.helpMessage = QLabel(text="Click–Click")
        self.setCentralWidget(self.helpMessage)
        self.helpMessage.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # qt's widgets didn't follow mouse without any button pressed
        # so I need to force it to track mouse movements
        self.setMouseTracking(True)

        self.roundings = CONFIG.get("rounding")
        self.hitpointRadius = CONFIG.get("hitPointRadius")
        self.startDraggingPoint = None
        self._hoveredRect = None
        # I won't use integrated ability of drag'n'drop
        # for the task my solution just enough and less code to write
        self._draggingRect = None
        self._cursor = None
        self._connectionBlueprint = False

    def paintEvent(self, event):
        """
        This is a main function where drawing magic is happen.
        """
        # create painter
        painter = QPainter(self)
        # just for nice smooth angles, it's looks nice and smooth even on straight lines
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen(self.palette().color(QPalette.Text), 1, Qt.DashLine)
        # create regular pen
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(0.4)
        painter.setPen(pen)

        for rect_id in range(len(self.model.rects)):
            rect = self.model.rects[rect_id]
            # draw all rects links
            connections = self.model.links[rect_id]
            if len(connections) > 0:
                # if rect#rect_id has a connections,
                # then I should store it's center point and draw a line to others rects
                # from a list of links, to their center points
                startPoint = rect.rect.center()
                for anotherRect in connections:
                    endPoint = self.model.rects[anotherRect].rect.center()
                    painter.drawLine(startPoint, endPoint)

        # draw all rects ontop of links (otherwise it's not that pretty)
        for rect_id in range(len(self.model.rects)):
            rect = self.model.rects[rect_id]
            # create filling brush with a color stored in a rect object
            color = rect.color
            # if mouse hovering above rect then draw it a little bit lighter
            if rect_id == self.hoveredRect:
                color = color.lighter(130)

            brush.setColor(color)
            painter.setBrush(brush)
            # draw the rect
            painter.drawRoundedRect(rect.rect, self.roundings, self.roundings)
            # draw the hit point for creating connections
            # color is similar to one used for lines (text color, white for dark theme, black on light one)
            brush.setColor(self.palette().color(QPalette.Text))
            painter.setBrush(brush)
            pen.setColor(brush.color().darker(120))
            painter.setPen(pen)
            painter.drawEllipse(rect.rect.center(), self.hitpointRadius, self.hitpointRadius)

        # draw temporary line if we moving mouse over field
        if self._cursor and self._connectionBlueprint:
            # create dash-style pen
            pen.setStyle(Qt.DashLine)
            pen.setWidth(1)
            pen.setDashPattern([3, 10])
            painter.setPen(pen)
            # draw temp line
            painter.drawLine(self.model.rects[self._draggingRect].rect.center(), self._cursor)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Key listener for one and only one function —
        close app when you get bored
        """
        if event.key() == Qt.Key_Escape:
            # QApplication.instance() return a running application instance
            QApplication.instance().exit()

    def foundRectWithPointInside(self, point: QPoint, hitpointForId: int = None):
        """
        Find ID of the rect wich has given point inside themself
        :param point: point which we test for
        :param hitpointForId: check if given rect_id contains given point inside hitpoint area
        :return: id of the rect or None if rect wasn't found
        """
        # if need check hit into hitpoint ot given rect
        if hitpointForId is not None:
            distanceDiffPoint = point - self.model.rects[hitpointForId].rect.center()
            # manhattanLenght() is just sqrt(pow(x(), 2) + pow(y(), 2))
            if distanceDiffPoint.manhattanLength() <= self.hitpointRadius:
                return True
            else:
                return False
        else:
            # look for every rect we have
            for rectangle in self.model.rects:
                if rectangle.rect.contains(point):
                    return rectangle.id_
        # if function wasn't returned so far then we found nothing
        return None

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        # hide help message
        self.helpMessage.hide()

        # calculate if new rect will fit
        # create test rect and check if it will not hit anyone
        rectSize = CONFIG.get("rectSize")
        newRect = QRect(event.pos().x()-rectSize.width()/2,
                        event.pos().y()-rectSize.height()/2,
                        rectSize.width(),
                        rectSize.height())
        if not self.model.isHitting(rect=newRect):
            # create new rect
            self.model.createRect(event.localPos())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # if mouse pressed over a rect
        # then we begin dragging!
        # if hit in
        self._draggingRect = self.foundRectWithPointInside(point=event.pos())
        if self._draggingRect is not None:
            self._connectionBlueprint = self.foundRectWithPointInside(point=event.pos(),
                                                                      hitpointForId=self._draggingRect)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        pass
        # look if we drop mouse over some rect
        destRect = self.foundRectWithPointInside(point=event.pos())
        # if we have start and end rects (and they are different) - we have connection
        if (destRect is not None and self._draggingRect is not None) and (destRect != self._draggingRect):
            self.model.createLink(self._draggingRect, destRect)

        # release cursor
        self._cursor = None
        self._draggingRect = None
        self._connectionBlueprint = False
        # update drawing
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # mark hovered rect if mouse is over any of them
        self.hoveredRect = self.foundRectWithPointInside(QPoint(event.pos()))
        if self.hoveredRect is not None:
            QApplication.setOverrideCursor(Qt.DragMoveCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)

        # if we dont create connection, then we draggin!
        if not self._connectionBlueprint and self._draggingRect is not None:
            if self._cursor is not None:
                # create future rectangle and check if it dont hit another ones
                delta = event.pos()-self._cursor
                rect = QRect(self.model.rects[self._draggingRect].rect)
                newPoint = rect.topLeft()+delta
                rect.moveTo(newPoint)
                if not self.model.isHitting(rect, self._draggingRect):
                    # if movement is safe - move the dragging rect
                    self.model.rects[self._draggingRect].move(delta)

        # update oldPos coordinates
        self._cursor = event.pos()

    # region PROPERTIES
    def getHoveredRect(self):
        return self._hoveredRect

    def setHoveredRect(self, id):
        self._hoveredRect = id
        self.update()
    hoveredRect = pyqtProperty(int, getHoveredRect, setHoveredRect)