import sys
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtCore import QRect, QTimer, QPoint, Qt, QSize

from core import Model
from mainWindow import MainWindow


if __name__ == "__main__":
    model = Model()

    # create test data
    model.createRect(QPoint(40, 40))
    model.createRect(QPoint(200, 60))
    model.createRect(QPoint(200, 200))
    model.createRect(QPoint(200, 400))

    model.createLink(0, 1)
    model.createLink(3, 2)

    # create application
    app = QApplication(sys.argv)
    # create main widget
    mainWindow = MainWindow(model=model,
                            flags=Qt.FramelessWindowHint)
    # style new widget
    mainWindow.setMinimumSize(800, 600)
    # connect signals to correspongins slots
    model.somethingChanged.connect(mainWindow.update)
    mainWindow.show()
    sys.exit(app.exec_())
