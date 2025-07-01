import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
                               QMessageBox)

from backend.efibootmgr import get_boot_entries


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bootviz - EFI Boot Manager")

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Tabela z 4 kolumnami: ID, Active, Default, Description
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Active", "Default", "Description"])
        self.table.setColumnWidth(3, 565)
        layout.addWidget(self.table)

        # Move Up / Move Down pod tabelą
        buttons_layout = QHBoxLayout()
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_up)
        buttons_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_down)
        buttons_layout.addWidget(self.move_down_button)

        layout.addLayout(buttons_layout)

        # --- Górne przyciski Refresh i Save ---
        top_buttons_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh boot entries")
        refresh_button.clicked.connect(self.load_boot_entries)
        top_buttons_layout.addWidget(refresh_button)

        save_button = QPushButton("Save boot order")
        save_button.clicked.connect(self.apply_new_boot_order)
        top_buttons_layout.addWidget(save_button)

        layout.addLayout(top_buttons_layout)
        # ----------------------------------------

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.load_boot_entries()

    def move_up(self):
        current_row = self.table.currentRow()
        if current_row <= 0:
            return
        self.swap_rows(current_row, current_row - 1)
        self.table.selectRow(current_row - 1)

    def move_down(self):
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= self.table.rowCount() - 1:
            return
        self.swap_rows(current_row, current_row + 1)
        self.table.selectRow(current_row + 1)

    def swap_rows(self, row1, row2):
        for col in range(self.table.columnCount()):
            item1 = self.table.item(row1, col)
            item2 = self.table.item(row2, col)
            text1 = item1.text() if item1 else ""
            text2 = item2.text() if item2 else ""
            self.table.setItem(row1, col, QTableWidgetItem(text2))
            self.table.setItem(row2, col, QTableWidgetItem(text1))

    def apply_new_boot_order(self):
        order = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # kolumna ID
            if item:
                boot_id = item.text()
                order.append(boot_id.upper())

        from backend.efibootmgr import set_boot_order

        try:
            set_boot_order(order)
            QMessageBox.information(self, "Success", "Boot order updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update boot order:\n{e}")

    def load_boot_entries(self):
        try:
            data = get_boot_entries()
            entries = data['entries']
            current_boot = data['current_boot']

            self.table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                self.table.setItem(row, 0, QTableWidgetItem(entry["id"]))
                self.table.setItem(row, 1, QTableWidgetItem("Yes" if entry["active"] else "No"))
                self.table.setItem(row, 2, QTableWidgetItem("Yes" if entry["id"].lower() == current_boot.lower() else "No"))
                self.table.setItem(row, 3, QTableWidgetItem(entry["description"]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boot entries:\n{e}")


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 400)
    window.show()
    sys.exit(app.exec())
