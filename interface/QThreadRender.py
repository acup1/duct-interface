from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
from time import sleep

class render(QThread):
    iteration_finished = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        n=0
        while True:
            n+=1
            self.iteration_finished.emit(n)
            self.msleep(100)