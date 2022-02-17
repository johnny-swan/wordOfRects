import sys
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtCore import QRect, QTimer, QPoint, Qt, QSize

from core import Model
from mainWindow import MainWindow
from darkPalette import darkPalette


if __name__ == "__main__":
    model = Model()

    # create application
    app = QApplication(sys.argv)
    # set nice dark palette
    app.setPalette(darkPalette)
    # create main widget
    mainWindow = MainWindow(model=model,
                            flags=Qt.FramelessWindowHint)
    # style new widget
    mainWindow.setMinimumSize(800, 600)
    # connect signals to correspongins slots
    model.somethingChanged.connect(mainWindow.update)
    mainWindow.show()
    sys.exit(app.exec_())
