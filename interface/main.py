import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.Qt import pyqtSignal
import pyqtgraph as pg
import time
import asyncio
import threading
import os
import res
from vkeyboard.vkeyboard import Keyboard
from serialworker import serial_worker
from time import time
from render import render as updater
from QThreadRender import render as qupdater
from setupwindow import setupwindow
from PyQt5.QtCore import QTimer
from exlambda import exlambda

s=serial_worker("/dev/ttyS3",115200)


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

uiclass, baseclass = pg.Qt.loadUiType("mainwindow.ui")

def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


class MainWindow(uiclass, baseclass):
    selected=0
    can_draw=False
    can_draw_d1=True
    can_draw_d2=True
    can_draw_d3=True
    testing_mode=False
    testing_counter=0
    show_maxes=True
    finale_data={
        'd1':{
            "x":[],
            "y":[],
        },
        'd2':{
            "x":[],
            "y":[],
        },
        'd3':{
            "x":[],
            "y":[],
        },        
    } 

    k={
        # k   1 2 3 4
        "d1":[0,0,0,0],
        "d2":[0,0,0,0],
        "d3":[0,0,0,0],
    }
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)
        
        

        self.disabeble_elements=[
            self.startbtn,
            self.o1,
            self.o2,
            self.o3,
            self.o4,
            self.heater,
            self.settings,
            self.shutdownbtn,
            self.left,
            self.leftleft,
            self.right,
            self.rightright,
            self.vozvrat,
            self.keyboardbtn,
            ]

        #self.legend = self.graph.addLegend(offset=(590, 370))
        self.legend = self.graph.addLegend(offset=(0, 0))
        self.legend.mouseDragEvent = lambda *args, **kwargs: None
        self.legend.hoverEvent = lambda *args, **kwargs: None

        self.graph.showGrid(x=True, y=True, alpha=0.5)
        self.graph.setLimits(xMin=0, yMin=0)
        self.graph.setRange(xRange=[0, 15], yRange=[0, 50])
        self.graph.setTitle("Измерения")
        self.graph.setLabel('left', 'Нагрузка, Н')
        self.graph.setLabel('bottom', 'Перемещение, мм')
        self.graph.enableAutoRange(axis='y')
        self.graph.setAutoVisible(y=True)
        self.graph.enableAutoRange(axis='x')
        self.graph.setAutoVisible(x=True)

        self.d1data=[[],[]]
        self.d2data=[[],[]]
        self.d3data=[[],[]]
        self.d1=self.graph.plot(self.d1data[0], self.d1data[1], pen=pg.mkPen(color='r'), symbol="d",
                        symbolBrush=pg.mkBrush('r'), symbolSize=0, name="датчик 1")
        self.d2=self.graph.plot(self.d2data[0], self.d2data[1], pen=pg.mkPen(color='g'), symbol="d",
                        symbolBrush=pg.mkBrush('g'), symbolSize=0, name="датчик 2")
        self.d3=self.graph.plot(self.d3data[0], self.d3data[1], pen=pg.mkPen(color='b'), symbol="d",
                        symbolBrush=pg.mkBrush('b'), symbolSize=0, name="датчик 3")
        
        self.lcd1.setDigitCount(6)
        self.lcd2.setDigitCount(6)
        self.lcd3.setDigitCount(6)
        self.lcd4.setDigitCount(6)
        self.lcd5.setDigitCount(5)
        #updater(self,s)
        self.upd=qupdater()
        #self.upd.finished.connect(lambda: qupdater(self,s).start())
        self.upd.iteration_finished.connect(self.render_iteration)
        self.upd.start()
        
        #threading.Thread(target=self.start_proc_events).start()
        ######

        self.doubleSpinBox.hide()
        self.label_2.hide()
        self.statusbar.showMessage("test",5000)

        self.startbtn.setIcon(QIcon(":play"))
        self.startbtn.setIconSize(QtCore.QSize(50, 50))
        self.startbtn.clicked.connect(self.startbtn_func)

        self.stopbtn.setIcon(QIcon(":stop"))
        self.stopbtn.setIconSize(QtCore.QSize(50, 50))
        self.stopbtn.clicked.connect(self.stopbtn_func)


        self.shutdownbtn.setIcon(QIcon(":shutdown"))
        self.shutdownbtn.setIconSize(QtCore.QSize(56, 56))
        self.shutdownbtn.clicked.connect(self.shutdownbtn_func)

        self.settings.setIcon(QIcon(":settings"))
        self.settings.setIconSize(QtCore.QSize(56, 56))
        self.settings.clicked.connect(self.open_settings)

        self.left.setIcon(QIcon(":left"))
        self.left.setIconSize(QtCore.QSize(66, 66))
        #self.left.clicked.connect(self.left_func)
        self.left.pressed.connect(lambda: s.send_command("left\x0a\x0d\x00"))
        self.left.released.connect(lambda: s.send_command("stop\x0a\x0d\x00"))

        self.leftleft.setIcon(QIcon(":leftleft"))
        self.leftleft.setIconSize(QtCore.QSize(66, 66))
        #self.leftleft.clicked.connect(self.leftleft_func)
        self.leftleft.pressed.connect(lambda: s.send_command("rleft\x0a\x0d"))
        self.leftleft.released.connect(lambda: s.send_command("stop\x0a\x0d\x00"))

        self.right.setIcon(QIcon(":right"))
        self.right.setIconSize(QtCore.QSize(66, 66))
        #self.right.clicked.connect(self.left_func)
        self.right.pressed.connect(lambda: s.send_command("right\x0a\x0d"))
        self.right.released.connect(lambda: s.send_command("stop\x0a\x0d\x00"))

        self.rightright.setIcon(QIcon(":rightright"))
        self.rightright.setIconSize(QtCore.QSize(66, 66))
        #self.rightright.clicked.connect(self.rightright_func)
        self.rightright.pressed.connect(lambda: s.send_command("rrigh\x0a\x0d"))
        self.rightright.released.connect(lambda: s.send_command("stop\x0a\x0d\x00"))

        self.vozvrat.setIcon(QIcon(":vozvrat"))
        self.vozvrat.setIconSize(QtCore.QSize(66, 66))
        self.vozvrat.clicked.connect(lambda: s.send_command("reset\x0a\x0d"))
        
        self.o1.setIcon(QIcon(":0"))
        self.o1.setIconSize(QtCore.QSize(40, 40))
        self.o1.clicked.connect(lambda:self.lcd1.display(0))

        self.o2.setIcon(QIcon(":0"))
        self.o2.setIconSize(QtCore.QSize(40, 40))
        self.o2.clicked.connect(lambda:self.lcd2.display(0))

        self.o3.setIcon(QIcon(":0"))
        self.o3.setIconSize(QtCore.QSize(40, 40))
        self.o3.clicked.connect(lambda:self.lcd3.display(0))
        
        self.clear_accept.hide()
        self.clear_accept.clicked.connect(self.clear_accept_func)
        self.o4.setIcon(QIcon(":0"))
        self.o4.setIconSize(QtCore.QSize(40, 40))
        self.o4.clicked.connect(self.o4_func)


        self.turn_off_testing_led()
        #self.testing.setIconSize(QtCore.QSize(70, 70))
        #self.testing.clicked.connect(self.rightright_func)

        self.POac.hide()
        self.POac.clicked.connect(self.po_accepted)

        self.heater.setIcon(QIcon(":off"))
        self.heater.setIconSize(QtCore.QSize(40, 40))
        self.heater_active=False
        self.heater.clicked.connect(self.heater_toggler)
        self.heater.hide()

        self.maxes.clicked.connect(self.toggle_values_mode)

        #SETTINGS
        self.setting_canvas.hide()
        
        self.doubleSpinBox.setStyleSheet("QDoubleSpinBox::up-button { width: 50px; height: 50px; }" "QDoubleSpinBox::down-button { width: 50px; height: 50px; }")

        self.keyboardbtn.clicked.connect(self.openkeyboard)
        self.keyboardbtn.setIcon(QIcon(":keyboard"))
        self.keyboardbtn.setIconSize(QtCore.QSize(50, 50))
        self.doubleSpinBox.clicked.connect(self.openkeyboard)

        def swap():
            self.setupwin.activateWindow()
            s.rezhim_parametrv=True
            s.send_command("setpp\x0a\x0d")
        self.setparam.clicked.connect(swap)
        self.setparam.setIcon(QIcon(":settingsio"))
        self.setparam.setIconSize(QtCore.QSize(50, 50))

        self.changeX.clicked.connect(exlambda('''
    if self.selected<3:
        self.selected+=1
    else:
        self.selected=0
''',"self",[self]))
        

    def render_iteration(self,n):
        #while True:pass
        #self.processEvents()
        try:
            if self.s.KL:
                self.statusbar.showMessage("Зафиксировано нажатие левого концевика",2000)
            if self.s.KR:
                self.statusbar.showMessage("Зафиксировано нажатие правого концевика",2000)
            if self.s.ES:
                self.statusbar.showMessage("Аварийная остновка",2000)

            if self.testing_mode==False and int(s.mode)==5:
                #while s.mode==b'\x05':
                s.send_command("stop\x0a\x0d\x00")
            #print(int(time())%2)
            #if int(time())%5==0:
            self.lcd5.display(str(int(s.time)))
            self.lcd6.display(f"{float(s.temp):.1f}")
            #main.lcd4.display(0)
            if self.selected==0:
                self.label_11.setText("Перемещение, мм")
                self.lcd4.display(f"{float(s.x):.2f}")
            elif self.selected==1:
                self.label_11.setText("Образец 1, мм")
                self.lcd4.display(f"{float(max(self.finale_data['d1']['x']+[0])):.2f}")
            elif self.selected==2:
                self.label_11.setText("Образец 2, мм")
                self.lcd4.display(f"{float(max(self.finale_data['d2']['x']+[0])):.2f}")
            elif self.selected==3:
                self.label_11.setText("Образец 3, мм")
                self.lcd4.display(f"{float(max(self.finale_data['d3']['x']+[0])):.2f}")
            #print(s.x,main.lcd4.value())
            k=5
            if n%5==0 and self.testing_mode:
                if self.can_draw_d1:
                    self.d1data[0]=s.bx[::k] 
                    self.d1data[1]=s.bd1[::k]
                    self.finale_data['d1']["x"]=list(s.bx)
                    self.finale_data['d1']["y"]=s.bd1

                if self.can_draw_d2:
                    self.d2data[0]=s.bx[::k] 
                    self.d2data[1]=s.bd2[::k]
                    self.finale_data['d2']["x"]=list(s.bx)
                    self.finale_data['d2']["y"]=s.bd2

                if self.can_draw_d3:
                    self.d3data[0]=s.bx[::k] 
                    self.d3data[1]=s.bd3[::k]
                    self.finale_data['d3']["x"]=list(s.bx)
                    self.finale_data['d3']["y"]=s.bd3

                self.graph.disableAutoRange()
                self.plot()
                self.graph.enableAutoRange()
                #print(int(k1),int(k2),int(k3))
            
            if self.show_maxes:
                self.lcd1.display(f"{float(max(s.bd1+[0])):.2f}")
                self.lcd2.display(f"{float(max(s.bd2+[0])):.2f}")
                self.lcd3.display(f"{float(max(s.bd3+[0])):.2f}")
            else:
                self.lcd1.display(f"{float(s.bd1[-1]):.2f}")
                self.lcd2.display(f"{float(s.bd2[-1]):.2f}")
                self.lcd3.display(f"{float(s.bd3[-1]):.2f}")

            

            if n%5==0:
                if self.testing_mode:self.turn_on_testing_led()
                else:self.turn_off_testing_led()


            
            if len(s.bd1)>0:
                y1=s.bd1[-1]
                if y1>0.01*300 and self.k["d1"][0]!=1:self.k["d1"][0]=1
                if y1>0.1*300 and self.k["d1"][2]!=1:self.k["d1"][2]=1
                if y1<0.01*300 and self.k["d1"][2]==1:self.k["d1"][3]=1
            
            if len(s.bd2)>0:
                y2=s.bd2[-1]
                if y2>0.01*300 and self.k["d2"][0]!=1:self.k["d2"][0]=1
                if y2>0.1*300 and self.k["d2"][2]!=1:self.k["d2"][2]=1
                if y2<0.01*300 and self.k["d2"][2]==1:self.k["d2"][3]=1

            if len(s.bd3)>0:
                y3=s.bd3[-1]
                if y3>0.01*300 and self.k["d3"][0]!=1:self.k["d3"][0]=1
                if y3>0.1*300 and self.k["d3"][2]!=1:self.k["d3"][2]=1
                if y3<0.01*300 and self.k["d3"][2]==1:self.k["d3"][3]=1

            
            if len(s.bx)>0 and int(s.time)>=30:
                dx=s.bx[-1]-s.bx[-2]
                if dx!=0:
                    dy1=y1-s.bd1[-2]
                    dy2=y2-s.bd2[-2]
                    dy3=y3-s.bd3[-2]
                    k1=dy1/dx
                    k2=dy2/dx
                    k3=dy3/dx
                    if k1<=-10 and self.k["d1"][1]!=1 and self.k["d1"][0]==1:self.k["d1"][1]=1
                    if k2<=-10 and self.k["d2"][1]!=1 and self.k["d2"][0]==1:self.k["d2"][1]=1
                    if k3<=-10 and self.k["d3"][1]!=1 and self.k["d3"][0]==1:self.k["d3"][1]=1

            if sum(self.k["d1"][0:2])==2 or sum(self.k["d1"][2:4])==2:
                self.can_draw_d1=False
                
                #print("stop 1",sum(self.k["d1"][0:2])==2,sum(self.k["d1"][2:4])==2)
            if sum(self.k["d2"][0:2])==2 or sum(self.k["d2"][2:4])==2:
                self.can_draw_d2=False

                #print("stop 2",sum(self.k["d2"][0:2])==2,sum(self.k["d2"][2:4])==2)
            if sum(self.k["d3"][0:2])==2 or sum(self.k["d3"][2:4])==2:
                self.can_draw_d3=False

                #print("stop 3",sum(self.k["d3"][0:2])==2,sum(self.k["d3"][2:4])==2)
            #print(*self.k["d1"])

            if (not(self.can_draw_d1)) and (not(self.can_draw_d2)) and (not(self.can_draw_d3)):
                s.send_command("stop\x0a\x0d\x00")
                self.stopbtn_func()



            #print(self.testing_mode)
            #if n%20==0:

            if False:
                self.msleep(100)
                main.processEvents()
                print(1)
            #main.can_draw=False 
            #main.processEvents()
            QApplication.processEvents()
            #self.msleep(500)
            #sleep(0.1)
            self.iteration_finished.emit()
        except Exception as err: 
            print(err)

    def focusInEvent(self, event):
        print('Got focus')

    def start_proc_events(self):
        #return 0
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.proc_events())

    async def proc_events(self):
        while True:
            self.processEvents()
            await asyncio.sleep(1)
    
    def toggle_values_mode(self):
        if self.maxes.isChecked():
            self.show_maxes=True
        else:
            self.show_maxes=False

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
    
    
    def disable_interface(self):
        for i in self.disabeble_elements:i.setEnabled(False)
        self.close_settings()
        
    def enable_interface(self):
        for i in self.disabeble_elements:i.setEnabled(True)
    

    def clear_accept_func(self):
        self.clear_accept.hide()
        self.o4.setIcon(QIcon(":0"))
        s.send_command("setx0\x0a\x0d")
        self.lcd4.display(0)

    def o4_func(self):
        if self.clear_accept.isHidden():
            self.clear_accept.show()
            self.o4.setIcon(QIcon(":0_b"))
        else:
            self.clear_accept.hide()
            self.o4.setIcon(QIcon(":0"))

    def heater_toggler(self):
        if self.heater_active:
            self.heater.setIcon(QIcon(":off"))
            self.heater_active=False
            s.send_command("hatof\x0a\x0d")
        else:
            self.heater.setIcon(QIcon(":on"))
            self.heater_active=True
            s.send_command("hater\x0a\x0d")


    def open_settings(self):
        if self.setting_canvas.isHidden():
            self.setting_canvas.show()
            self.settings.setIcon(QIcon(":settings_o"))
        else:
            self.setting_canvas.hide()
            self.settings.setIcon(QIcon(":settings"))
    
    def close_settings(self):
        self.setting_canvas.hide()
        self.settings.setIcon(QIcon(":settings"))

    def stopbtn_func(self):
        self.can_draw_d1=False
        self.can_draw_d2=False
        self.can_draw_d3=False
        '''
        if any([self.can_draw_d1,self.can_draw_d2,self.can_draw_d3]):
            self.can_draw_d1=False
            self.finale_data['d1']["x"]=s.bx
            self.finale_data['d1']["y"]=s.bd1
            self.can_draw_d2=False
            self.finale_data['d2']["x"]=s.bx
            self.finale_data['d2']["y"]=s.bd2
            self.can_draw_d3=False
            self.finale_data['d3']["x"]=s.bx
            self.finale_data['d3']["y"]=s.bd3
        '''
        
        self.d1data[0]=self.finale_data['d1']['x']
        self.d1data[1]=self.finale_data['d1']['y']
        self.d2data[0]=self.finale_data['d2']['x']
        self.d2data[1]=self.finale_data['d2']['y']
        self.d3data[0]=self.finale_data['d3']['x']
        self.d3data[1]=self.finale_data['d3']['y']
        self.graph.disableAutoRange()
        self.plot()
        self.graph.enableAutoRange()
        finale_data={
            'd1':{
                "x":[],
                "y":[],
            },
            'd2':{
                "x":[],
                "y":[],
            },
            'd3':{
                "x":[],
                "y":[],
            },        
        } 
        #os.system("poweroff")
        #self.pushButton.hide()
        #self.pushButton.show()
        #self.d1.setData([], [])
        #self.close()
        self.k={
            # k   1 2 3 4
            "d1":[0,0,0,0],
            "d2":[0,0,0,0],
            "d3":[0,0,0,0],
        }
        self.testing_mode=False
        self.can_draw_d1=True
        self.can_draw_d2=True
        self.can_draw_d3=True
        self.enable_interface()
        s.clear_buffer()
        #self.clear_graph()
        s.send_command("stop\x0a\x0d\x00")
        #exit()

    def clear_graph(self):
        self.d1data=[[],[]]
        self.d2data=[[],[]]
        self.d3data=[[],[]]
        s.clear_buffer()
        self.plot()

    def startbtn_func(self):
        self.clear_graph()
        self.disable_interface()
        self.can_draw=True
        self.testing_mode=True
        s.send_command('start\x0a\x0d')
        #threading.Thread(target=self.test_start).start()

    def shutdownbtn_func(self):
        if self.POac.isHidden():
            self.POac.show()
            self.shutdownbtn.setIcon(QIcon(":shutdown_b"))
        else:
            self.POac.hide()
            self.shutdownbtn.setIcon(QIcon(":shutdown"))
        
    
    def po_accepted(self):
        os.system("systemctl reboot")
        #os.system("systemctl poweroff")

    def turn_off_testing_led(self):
        self.testing.setPixmap(QIcon(":off_g").pixmap(QtCore.QSize(40, 40)))

    def turn_on_testing_led(self):
        self.testing.setPixmap(QIcon(":on_g").pixmap(QtCore.QSize(40, 40)))

    def test_start(self):
        return 0
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.test())

    async def test(self):
        self.turn_on_testing_led()
        self.testing_counter=0
        k=10
        j=10
        while self.testing_mode:
            
            if self.testing_counter%j==0:
                self.plot()
                self.can_draw=True
            
            self.testing_counter+=1
            await asyncio.sleep(0.1)

        try:
            for x in frange(0,20,0.1):
                self.d1add(x, -0.5*x**2+5*x+20)
                self.lcd4.display(x)
                self.lcd1.display(-1*x**2-10*x)
                time.sleep(0.01)
        except:
            pass
        self.turn_off_testing_led()
        self.can_draw=False
        self.enable_interface()


    def plot(self):
        if self.can_draw_d1:
            self.d1.setData(self.d1data[0], self.d1data[1])
        if self.can_draw_d2:
            self.d2.setData(self.d2data[0], self.d2data[1])
        if self.can_draw_d3:
            self.d3.setData(self.d3data[0], self.d3data[1])
        #QApplication.processEvents()
        
        #self.graph.enableAutoRange(axis='y')
        #self.graph.setAutoVisible(y=True)
        #self.graph.enableAutoRange(axis='x')
        #self.graph.setAutoVisible(x=True)
        
        '''
        try:minx=min(self.d1data[0]+self.d2data[0]+self.d3data[0]+self.d4data[0])
        except:minx=0

        try:maxx=max(self.d1data[0]+self.d2data[0]+self.d3data[0]+self.d4data[0])
        except:maxx=100

        try:miny=min(self.d1data[1]+self.d2data[1]+self.d3data[1]+self.d4data[1])
        except:miny=0

        try:maxy=max(self.d1data[1]+self.d2data[1]+self.d3data[1]+self.d4data[1])
        except:maxy=100

        self.graph.setRange(xRange=[minx, maxx], yRange=[miny, maxy])
        #self.graph.viewAll()
        '''

    def d1add(self,x,y):
        #self.graph.clear()
        self.d1data[0].append(x)
        self.d1data[1].append(y)
        self.can_draw=True

    def d2add(self,x,y):
        #self.graph.clear()
        self.d2data[0].append(x)
        self.d2data[1].append(y)
        self.can_draw=True

    def d3add(self,x,y):
        #self.graph.clear()
        self.d3data[0].append(x)
        self.d3data[1].append(y)
        self.can_draw=True


if __name__=="__main__":
    app = QApplication(sys.argv)
    setupwin = setupwindow(s)
    mainwin = MainWindow()
    mainwin.setupwin=setupwin
    setupwin.mainwin=mainwin
    mainwin.show()
    setupwin.show()
    app.exec()
