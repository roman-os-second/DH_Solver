import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models import NetworkModel


class NodeMarker(QGraphicsEllipseItem):
    def __init__(self, x, y):
        super().__init__(-5, -5, 10, 10)
        self.setPos(x, y)

        self.normal_pen = QPen(QColor("#1f4d7a"))
        self.normal_brush = QBrush(QColor("#4a90c2"))
        self.selected_pen = QPen(QColor("#f28c28"))
        self.selected_brush = QBrush(QColor("#ffd84d"))

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.update_appearance(False)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update_appearance(value)

        return super().itemChange(change, value)

    def update_appearance(self, selected):
        if selected:
            self.setPen(self.selected_pen)
            self.setBrush(self.selected_brush)
        else:
            self.setPen(self.normal_pen)
            self.setBrush(self.normal_brush)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawEllipse(self.rect())


class CanvasView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        self.zoom_level = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 5.0
        self.zoom_factor = 1.15
        self.node_placement_mode = False
        self.selection_mode = False
        self.node_placement_callback = None
        self.pan_start_position = None
        self.last_pan_position = None
        self.is_panning = False

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def set_node_placement_mode(self, active):
        self.node_placement_mode = active
        self.update_cursor()

    def set_selection_mode(self, active):
        self.selection_mode = active
        if not active:
            self.scene().clearSelection()
        self.update_cursor()

    def update_cursor(self):
        if self.is_panning:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif self.node_placement_mode:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.unsetCursor()

    def select_item_at(self, position):
        clicked_item = self.itemAt(position)

        item = clicked_item

        while item is not None:
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
                self.scene().clearSelection()
                item.setSelected(True)
                break

            item = item.parentItem()
        else:
            self.scene().clearSelection()

        #PySide6 workaround: accessing the clicked item's scene prevents grid lines from disappearing after a Select-mode click
        #revisit if the canvas/selection implementation is refactored
        _ = (clicked_item is not None and clicked_item.scene() is self.scene())

    def wheelEvent(self, event):
        wheel_delta = event.angleDelta().y()
        if wheel_delta == 0:
            super().wheelEvent(event)
            return

        zoom_factor = self.zoom_factor if wheel_delta > 0 else 1 / self.zoom_factor
        new_zoom = self.zoom_level * zoom_factor

        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.scale(zoom_factor, zoom_factor)
            self.zoom_level = new_zoom

        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pan_start_position = event.position().toPoint()
            self.last_pan_position = self.pan_start_position
            self.is_panning = False
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_pan_position is not None:
            current_position = event.position().toPoint()

            if not self.is_panning:
                distance = (current_position - self.pan_start_position).manhattanLength()
                if distance < QApplication.startDragDistance():
                    event.accept()
                    return

                self.is_panning = True
                self.update_cursor()

            delta = current_position - self.last_pan_position

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.last_pan_position = current_position
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.last_pan_position is not None:
            should_place_node = self.node_placement_mode and not self.is_panning
            should_select_item = self.selection_mode and not self.is_panning
            click_position = event.position().toPoint()

            self.pan_start_position = None
            self.last_pan_position = None
            self.is_panning = False
            self.update_cursor()

            if should_place_node and self.node_placement_callback is not None:
                self.node_placement_callback(self.mapToScene(click_position))
            elif should_select_item:
                self.select_item_at(click_position)

            event.accept()
            return

        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = NetworkModel()

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
            if name == "Properties":
                button.clicked.connect(self.show_properties)
            else:
                button.clicked.connect(
                    lambda checked=False, name=name: self.show_message(name)
                )
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

        self.active_tool = None
        self.toolbox_buttons = {}

        for name in ("Select", "Nodes", "Pipes", "Source", "Consumer", "Delete"):
            button = QPushButton(name)
            button.setFixedSize(120, 32)
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked, name=name: self.set_active_tool(name, checked)
            )
            self.toolbox_buttons[name] = button
            toolbox_layout.addWidget(button)

        toolbox_layout.addStretch()
        workspace_layout.addWidget(toolbox)

        toolbox_separator = QFrame()
        toolbox_separator.setFrameShape(QFrame.VLine)
        toolbox_separator.setFrameShadow(QFrame.Sunken)
        workspace_layout.addWidget(toolbox_separator)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 2000, 2000)

        self.grid_size = 25
        grid_pen = QPen(QColor("#d0d0d0"))
        for position in range(0, 2001, self.grid_size):
            vertical_line = self.scene.addLine(position, 0, position, 2000, grid_pen)
            horizontal_line = self.scene.addLine(0, position, 2000, position, grid_pen)

            for grid_line in (vertical_line, horizontal_line):
                grid_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                grid_line.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
                grid_line.setZValue(-1)

        self.canvas = CanvasView(self.scene)
        self.canvas.node_placement_callback = self.place_node
        workspace_layout.addWidget(self.canvas, 1)
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

    def show_properties(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Model Data")

        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()

        def create_read_only_table(headers, row_count=0):
            table = QTableWidget(row_count, len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            return table

        nodes_table = create_read_only_table(
            ("ID", "X", "Y", "Z"), len(self.model.nodes)
        )

        for row, node in enumerate(self.model.nodes.values()):
            nodes_table.setItem(row, 0, QTableWidgetItem(node.ID))
            nodes_table.setItem(row, 1, QTableWidgetItem(str(node.X)))
            nodes_table.setItem(row, 2, QTableWidgetItem(str(node.Y)))
            nodes_table.setItem(row, 3, QTableWidgetItem(str(node.Z)))

        pipes_table = create_read_only_table(
            (
                "ID",
                "Start Node",
                "End Node",
                "Diameter",
                "Roughness",
                "Length",
                "Heat Loss Coefficient",
            )
        )
        sources_table = create_read_only_table(
            ("ID", "Node", "P_s", "P_r", "T_s", "T_r")
        )
        consumers_table = create_read_only_table(
            ("ID", "Node", "Thermal Power Demand")
        )

        for table, name in (
            (nodes_table, "Nodes"),
            (pipes_table, "Pipes"),
            (sources_table, "Sources"),
            (consumers_table, "Consumers"),
        ):
            table.resizeColumnsToContents()
            tabs.addTab(table, name)

        layout.addWidget(tabs)
        dialog.resize(640, 300)
        dialog.exec()

    def set_active_tool(self, tool_name, active):
        if active:
            for name, button in self.toolbox_buttons.items():
                if name != tool_name:
                    button.setChecked(False)
            self.active_tool = tool_name
        else:
            self.active_tool = None

        self.canvas.set_node_placement_mode(self.active_tool == "Nodes")
        self.canvas.set_selection_mode(self.active_tool == "Select")

    def place_node(self, scene_position):
        x = float(round(scene_position.x() / self.grid_size) * self.grid_size)
        y = float(round(scene_position.y() / self.grid_size) * self.grid_size)
        node = self.model.createNode(x, y, 0.0)

        marker = NodeMarker(x, y)
        self.scene.addItem(marker)

        label = self.scene.addText(node.ID)
        label.setParentItem(marker)
        label.setPos(8, -12)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
