import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

class TransparentButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("border: 2px solid black; background-color: rgba(0, 0, 0, 0); color: black;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))  # Заполняем фон прозрачным цветом
        super().paintEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle("Прозрачная кнопка с рамками")
        
        button = TransparentButton("Прозрачная кнопка", self)
        button.setGeometry(50, 50, 200, 50)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
