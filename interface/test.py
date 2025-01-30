import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Активация ввода")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_input = QLineEdit(self)
        self.layout.addWidget(self.text_input)

        self.activate_button = QPushButton("Активировать ввод", self)
        self.layout.addWidget(self.activate_button)

        self.activate_button.clicked.connect(self.activateInput)  # Подключение сигнала к слоту

    def activateInput(self):
        self.text_input.setEnabled(True)
        self.text_input.setFocus()  # Передача фокуса текстовому полю

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
