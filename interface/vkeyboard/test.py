import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget

class ExampleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('QTableWidget Example')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Создание QTableWidget
        self.table_widget = QTableWidget(self)
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(2)

        # Заголовки столбцов
        self.table_widget.setHorizontalHeaderLabels(['Name', 'Actions'])

        data = [
            ('Alice', 'Button 1'),
            ('Bob', 'Button 2'),
            ('Charlie', 'Button 3'),
            ('David', 'Button 4')
        ]

        for row, (name, action_text) in enumerate(data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(name))
            
            button = QPushButton(action_text)
            button.clicked.connect(self.on_button_clicked)
            self.table_widget.setCellWidget(row, 1, button)

        layout.addWidget(self.table_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_button_clicked(self):
        sender = self.sender()
        if isinstance(sender, QPushButton):
            button_text = sender.text()
            print(f'Button "{button_text}" clicked.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec_())
