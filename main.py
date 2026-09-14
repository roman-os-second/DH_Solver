import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DH Solver")
        self.resize(640, 400)

        label = QLabel("Hello from PySide6")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
