import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QLineEdit
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.Qt import pyqtSignal
import pyqtgraph as pg
import time
import asyncio
import threading
import os


class CQDoubleSpinBox(QDoubleSpinBox):
    
    
    clicked = pyqtSignal()

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.clicked.emit()
    
class CQLineEdit(QLineEdit):
    
    clicked = pyqtSignal()

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.clicked.emit()