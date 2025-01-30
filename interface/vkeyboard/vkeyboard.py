import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
#from pynput.keyboard import Controller
from PyQt5.QtWidgets import QApplication

class Keyboard(QWidget):
    def __init__(self,main,keys,edit_obj):
        self.main=main
        self.keys=keys
        self.edit_obj=edit_obj
        super().__init__()
        dx,dy=QApplication.primaryScreen().availableGeometry().width(),QApplication.primaryScreen().availableGeometry().height()
        wx,wy=self.frameSize().width(), self.frameSize().height()
        dy=600
        dx=1024
        print(dx,dy,wx,wy)
        self.move(dx//2-wx//2,dy//2-wy//2)
        self.move(100,600)
        self.setWindowTitle("Экранная клавиатура")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setFocusPolicy(Qt.StrongFocus)
        #self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        layout = QVBoxLayout()

        buttons_layout = QVBoxLayout()
        buttons1en = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['сменить раскладку',' ', 'Backspace']
        ]
        buttons1ru = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З'],
            ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д'],
            ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь'],
            ['сменить раскладку',' ', 'Backspace']
        ]
        buttons2=[
            ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            [',','0','Backspace'],
        ]

        buttons=[
            buttons1en,buttons1ru,buttons2
        ]

        for row in buttons[keys]:
            row_layout = QHBoxLayout()
            for button in row:
                button_widget = QPushButton(button)
                button_widget.clicked.connect(self.button_clicked)
                row_layout.addWidget(button_widget)
            buttons_layout.addLayout(row_layout)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        #self.keyboard_controller = Controller()

    def button_clicked(self):
        #self.activateWindow()
        button = self.sender()
        text = button.text()
        
        if text == 'Backspace':
            self.edit_obj.valueFromText(self.edit_obj.toPlainText()[:-1])
        elif text == 'сменить раскладку':
            self.main.k=Keyboard(self.main,1-self.keys,self.edit_obj)
            self.main.k.show()
        else:
            self.edit_obj.valueFromText(self.edit_obj.toPlainText()+text)
        
        



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Keyboard(1,2,3)
    window.show()
    app.exec()
