import sys

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DH Solver")
        self.resize(640, 400)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        action_bar = QWidget()
        action_bar.setFixedHeight(48)
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(8, 8, 8, 8)
        action_layout.setSpacing(8)

        for name in ("Run Simulation", "Properties", "Verification", "Clear Results"):
            button = QPushButton(name)
            button.setFixedSize(120, 32)
            button.clicked.connect(lambda checked=False, name=name: self.show_message(name))
            action_layout.addWidget(button)

        action_layout.addStretch()
        main_layout.addWidget(action_bar)

        top_separator = QFrame()
        top_separator.setFrameShape(QFrame.HLine)
        top_separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(top_separator)

        workspace_layout = QHBoxLayout()

        toolbox = QWidget()
        toolbox.setFixedWidth(136)
        toolbox_layout = QVBoxLayout(toolbox)
        toolbox_layout.setContentsMargins(8, 8, 8, 8)
        toolbox_layout.setSpacing(8)

        for name in ("Nodes", "Pipes", "Source", "Consumer", "Delete"):
            button = QPushButton(name)
            button.setFixedSize(120, 32)
            button.clicked.connect(lambda checked=False, name=name: self.show_message(name))
            toolbox_layout.addWidget(button)

        toolbox_layout.addStretch()
        workspace_layout.addWidget(toolbox)

        toolbox_separator = QFrame()
        toolbox_separator.setFrameShape(QFrame.VLine)
        toolbox_separator.setFrameShadow(QFrame.Sunken)
        workspace_layout.addWidget(toolbox_separator)

        canvas = QWidget()
        workspace_layout.addWidget(canvas, 1)
        main_layout.addLayout(workspace_layout)

        self.setCentralWidget(central_widget)
        self.setup_menus()

    def setup_menus(self):
        file_menu = self.menuBar().addMenu("File")

        new_action = file_menu.addAction("New")
        new_action.triggered.connect(lambda: self.show_message("New"))

        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(lambda: self.show_message("Open"))

        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(lambda: self.show_message("Save"))

        save_as_action = file_menu.addAction("Save As")
        save_as_action.triggered.connect(lambda: self.show_message("Save As"))

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        edit_menu = self.menuBar().addMenu("Edit")

        undo_action = edit_menu.addAction("Undo")
        undo_action.triggered.connect(lambda: self.show_message("Undo"))

        redo_action = edit_menu.addAction("Redo")
        redo_action.triggered.connect(lambda: self.show_message("Redo"))

    def show_message(self, message):
        QMessageBox.information(self, message, message)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
