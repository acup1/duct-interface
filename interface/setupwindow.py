import sys,os
from PyQt5.QtCore import Qt
from PyQt5 import QtCore,QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QLabel,QTableWidgetItem
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.Qt import pyqtSignal
from PyQt5.uic import loadUiType
import res

def openkeyboard():
    os.system("onboard &")


#cdform,base=

class setupwindow(*loadUiType("set.ui")):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)

        self.pas.setEchoMode(QtGui.QLineEdit.Password)

        self.keyboardbtn.clicked.connect(openkeyboard)
        self.keyboardbtn.setIcon(QIcon(":keyboard"))
        self.keyboardbtn.setIconSize(QtCore.QSize(50, 50))

        def swap():
            self.mainwin.activateWindow()
            self.s.send_command("setnr\x0a\x0d")
        self.tomain.clicked.connect(swap)
        self.tomain.setIcon(QIcon(":tograph"))
        self.tomain.setIconSize(QtCore.QSize(60, 60))

        self.table.setRowCount(100)
        self.table.setColumnCount(100)
        for y in range(100):
            for x in range(100):
                self.table.setItem(y, x, QTableWidgetItem("123"))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()





if __name__=="__main__":
    app = QApplication(sys.argv)
    window = setupwindow()
    window.show()
    app.exec()
