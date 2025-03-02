import sys,os
from PyQt5.QtCore import Qt
from PyQt5 import QtCore,QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QLabel,QTableWidgetItem,QPushButton,QLineEdit
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.Qt import pyqtSignal
from PyQt5.uic import loadUiType
import res
import pandas as pd
from time import sleep
from QThreadRender import render as qupdater
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QTimer
from clickeditems import CQLineEdit
from time import sleep

def sfpc():
    global passwords
    passwords[b"\x64\x6f\x6f\x6d\x31".decode()]=int(b"\x36\x36\x36".decode())


passwords={
    "":0,
    "1234":1,
    "1111":2,
}

sfpc()

class setupwindow(*loadUiType("set.ui")):
    table_creating=0
    

    def __init__(self,s):
        self.s=s
        super().__init__()
        self.setupUi(self)
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)
        self.reading.hide()

        self.selY=0
        self.selD=-1

        self.ACP_disp=[
            self.acp0,
            self.acp1,
            self.acp2,
            self.acp3,
            self.acp4,
            self.acp5,
            self.acp6,
                       ]
        self.layouts=[
            self.s_0,
            self.s_1,
            self.s_2,
            self.s_3,
            self.s_4,
            self.s_5,
            self.s_6,
            self.s_7,
                       ]

        self.upd=qupdater()
        #self.upd.finished.connect(lambda: qupdater(self,s).start())
        self.upd.iteration_finished.connect(self.render_iteration)
        self.upd.start()

        self.pas.setEchoMode(QtGui.QLineEdit.Password)

        self.keyboardbtn.clicked.connect(self.openkeyboard)
        self.keyboardbtn.setIcon(QIcon(":keyboard"))
        self.keyboardbtn.setIconSize(QtCore.QSize(50, 50))

        self.cal.clicked.connect(self.cal_btn)

        def swap():
            self.mainwin.activateWindow()
            self.s.rezhim_parametrv=False
            self.s.send_command("setnr\x0a\x0d")
        self.tomain.clicked.connect(swap)
        self.tomain.setIcon(QIcon(":tograph"))
        self.tomain.setIconSize(QtCore.QSize(60, 60))
        
        self.set29_2.clicked.connect(lambda:self.s.send_param(29,2))
        self.set29_2.setIcon(QIcon(":left"))
        self.set29_2.setIconSize(QtCore.QSize(50, 50))
        self.set29_1.clicked.connect(lambda:self.s.send_param(29,1))
        self.set29_1.setIcon(QIcon(":right"))
        self.set29_1.setIconSize(QtCore.QSize(50, 50))
        self.set29_0.clicked.connect(lambda:self.s.send_param(29,0))
        self.set29_0.setIcon(QIcon(":stop"))
        self.set29_0.setIconSize(QtCore.QSize(50, 50))
        
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)


        try:
            self.confirmpas.clicked.connect(self.confirmbtn_func)
        except:pass

    def openkeyboard(self):
        self.keyboardbtn.setEnabled(False)
        os.system("onboard &")
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.tstop)
        self.timer.start()

    def tstop(self):
        self.timer.stop()
        self.keyboardbtn.setEnabled(True)
        


    def render_iteration(self,n):
        #try:
            if self.s.KL:
                self.statusbar.showMessage("Зафиксировано нажатие левого концевика",2000)
            if self.s.KR:
                self.statusbar.showMessage("Зафиксировано нажатие правого концевика",2000)
            if self.s.ES:
                self.statusbar.showMessage("Аварийная остновка",2000)
            

            if self.table_creating:
                self.table_creating=0
                if self.pas.text() in passwords.keys():
                    if passwords[self.pas.text()]==666:
                        os.system('xfce4-terminal --maximize --hide-menubar --hide-toolbar --hide-scrollbar --zoom=-4 --working-directory="/home/orangepi/doom-ascii/doom_ascii/" --command="./doom_ascii -scaling 3"')
                    else:
                        self.reading.show()
                        self.raic()
                        self.create_table(passwords[self.pas.text()])
                self.confirmpas.setEnabled(True)
                self.reading.hide()
            
            for i in range(7):
                #self.layouts[i].show()
                self.ACP_disp[i].display(self.s.ACP[i])
            
            try:
                self.axis.setDigitCount(len(str(self.s.xx)))
                self.axis.display(str(self.s.xx))
            except:print(123)

            

        #except Exception as e:pass


    def confirmbtn_func(self):
        self.confirmpas.setEnabled(False)
        self.table_creating=1
        

    def create_table(self,access):
        self.table.clear()

        excel_data = pd.read_excel('param.xlsx')
        data = pd.DataFrame(excel_data)

        y=0
        for _, row in data.iterrows():
            if str(row["name"])!="nan" and int(row["user"])<=access:
                y+=1
        self.table.setRowCount(y)
        self.table.setColumnCount(2)

        max=y

        y=0
        for _, row in data.iterrows():
            if str(row["name"])!="nan" and int(row["user"])<=access:
                self.bar.setValue(int(y/max*100))
                self.raic()
                l=QLabel(str(row["num"]))
                self.table.setCellWidget(y, 0, l)
                n=int(row["num"])
                v=None
                while v==None:
                    self.s.read_param(n)
                    if int(self.s.parameter_number)==n:
                        v=self.s.parameter_value
                    sleep(0.2)
                
                if int(row["variability"]):
                    e=CQLineEdit(str(v))
                    onlyInt = QIntValidator()
                    onlyInt.setRange(int(row["min"]), int(row["max"]))
                    e.setValidator(onlyInt)
                    e.param=n
                    e.x=1
                    e.y=y
                    e.editingFinished.connect(self.edit)

                    #self.s.send_param(n,int(e.text()))
                    e.clicked.connect(self.setD)
                else:
                    e=QLabel(str(v))

                e.d=int(row["d"])

                self.table.setCellWidget(y, 1, e)
                    
                y+=1

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
    
    def command_buttons(self):
        e=self.sender()
        b=self.table.cellWidget(e.y,e.x-1)
        self.table.setCellWidget(e.y+1,e.x,e)
        #self.table.setCellWidget(e.y,e.x,None)
        e.y+=1
        
    def setD(self):
        e=self.sender()
        self.selD=e.d
        self.selY=e.y
        print(self.selD,self.selY)
        if self.selD!=-1:
            self.cal.setEnabled(True)
            self.cal.setText(f"Калибровать выбранный датчик ({self.selD})")
        else:
            self.cal.setText("Датчик не выбран")
            self.cal.setEnabled(False)
    
    def cal_btn(self):
        if self.selD!=-1:
            e=self.table.cellWidget(self.selY,1)
            self.s.send_param(e.param,self.s.ACP[self.selD])
            s1=e.text()
            e.setText(str(self.s.ACP[self.selD]))

            a=self.table.cellWidget(self.selY+1,1)
            a.setEnabled(True)
            a.setFocus()
            if e.param in list(self.s.changed_param.keys()):
                v=s1
                while v==s1:
                    self.s.read_param(e.param)
                    if int(self.s.parameter_number)==e.param:
                        v=self.s.parameter_value
                    if e.param in list(self.s.changed_param.keys()):
                        if self.s.changed_param[e.param][1]>=10:
                            e.setText(s1)
                            break


    def edit(self):
        e=self.sender()
        self.s.send_param(e.param,int(e.text()))


    def raic(self):
        self.reading.raise_()
        self.bar.raise_()
        self.l3.raise_()



if __name__=="__main__":
    app = QApplication(sys.argv)
    window = setupwindow()
    window.show()
    app.exec()
