import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class Window1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно 1")
        self.setGeometry(100, 100, 300, 200)

        button = QPushButton("Открыть второе окно", self)
        button.setGeometry(50, 50, 200, 30)
        button.clicked.connect(self.open_second_window)

        self.window2 = None  # Создаем атрибут для хранения экземпляра второго окна

    def open_second_window(self):
        self.window2 = Window2()  # Сохраняем экземпляр второго окна в атрибуте класса
        self.window2.show()

class Window2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно 2")
        self.setGeometry(500, 100, 300, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window1 = Window1()
    window1.show()
    sys.exit(app.exec_())
