import re
import sys

from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
                               QMessageBox, QInputDialog)

from backend.efibootmgr import get_boot_entries, set_boot_order

COLOR_ACTIVE = QColor(70, 125, 70)  # green
COLOR_DEFAULT = QColor(100, 0, 0)  # red
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 400
DESCRIPTION_COLUMN_WIDTH = 565

HEX_ID_PATTERN = re.compile(r"^[0-9A-Fa-f]{4}$")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bootviz - EFI Boot Manager")

        self.changes_made = False

        central_widget = QWidget()
        layout = QVBoxLayout()

        # --- Top buttons: Refresh, Add, Remove, Save ---
        top_buttons_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh boot entries")
        refresh_button.clicked.connect(self.load_boot_entries)
        top_buttons_layout.addWidget(refresh_button)

        add_button = QPushButton("Add Entry")
        add_button.clicked.connect(self.add_entry)
        top_buttons_layout.addWidget(add_button)

        remove_button = QPushButton("Remove Entry")
        remove_button.clicked.connect(self.remove_entry)
        top_buttons_layout.addWidget(remove_button)

        self.save_button = QPushButton("Save boot order")
        self.save_button.clicked.connect(self.apply_new_boot_order)
        self.save_button.setEnabled(False)  # disabled initially
        top_buttons_layout.addWidget(self.save_button)

        layout.addLayout(top_buttons_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Active", "Default", "Description"])
        self.table.setColumnWidth(3, DESCRIPTION_COLUMN_WIDTH)  # fixed Description column width
        layout.addWidget(self.table)

        # Move Up / Move Down buttons below the table
        buttons_layout = QHBoxLayout()
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_up)
        buttons_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_down)
        buttons_layout.addWidget(self.move_down_button)

        layout.addLayout(buttons_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.load_boot_entries()

    def load_boot_entries(self):
        try:
            entries = get_boot_entries()
            self.table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                id_item = QTableWidgetItem(entry["id"])
                active_item = QTableWidgetItem("Yes" if entry["active"] else "No")
                default_item = QTableWidgetItem("Yes" if entry.get("default", False) else "No")
                desc_item = QTableWidgetItem(entry["description"])

                # Colors: green for active entries, dark red for default
                if entry["active"]:
                    for item in (id_item, active_item, default_item, desc_item):
                        item.setBackground(QBrush(COLOR_ACTIVE))
                if entry.get("default", False):
                    for item in (id_item, active_item, default_item, desc_item):
                        item.setBackground(QBrush(COLOR_DEFAULT))
                    # Bold font for the default entry
                    font = QFont()
                    font.setBold(True)
                    for item in (id_item, active_item, default_item, desc_item):
                        item.setFont(font)

                self.table.setItem(row, 0, id_item)
                self.table.setItem(row, 1, active_item)
                self.table.setItem(row, 2, default_item)
                self.table.setItem(row, 3, desc_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boot entries:\n{e}")

    def apply_new_boot_order(self):
        order = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # ID column
            if item:
                boot_id = item.text().strip().upper()
                # Validate ID (4-digit hex)
                if not HEX_ID_PATTERN.match(boot_id):
                    QMessageBox.critical(self, "Error", f"Invalid boot ID format in row {row + 1}: '{boot_id}' (must be 4 hex digits)")
                    return
                order.append(boot_id)

        try:
            set_boot_order(order)
            QMessageBox.information(self, "Success", "Boot order updated successfully!")
            self.changes_made = False
            self.save_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update boot order:\n{e}")

    def move_up(self):
        current_row = self.table.currentRow()
        if current_row <= 0:
            return
        self.swap_rows(current_row, current_row - 1)
        self.table.selectRow(current_row - 1)
        self.changes_made = True
        self.save_button.setEnabled(True)

    def move_down(self):
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= self.table.rowCount() - 1:
            return
        self.swap_rows(current_row, current_row + 1)
        self.table.selectRow(current_row + 1)
        self.changes_made = True
        self.save_button.setEnabled(True)

    def swap_rows(self, row1, row2):
        for col in range(self.table.columnCount()):
            item1 = self.table.item(row1, col)
            item2 = self.table.item(row2, col)
            text1 = item1.text() if item1 else ""
            text2 = item2.text() if item2 else ""
            self.table.setItem(row1, col, QTableWidgetItem(text2))
            self.table.setItem(row2, col, QTableWidgetItem(text1))

    def add_entry(self):
        # Dialog to add entry: ID and description
        id_text, ok = QInputDialog.getText(self, "Add Boot Entry", "Enter 4-digit hex ID (e.g. 000A):")
        if not ok or not id_text:
            return
        id_text = id_text.strip().upper()
        if not HEX_ID_PATTERN.match(id_text):
            QMessageBox.critical(self, "Error", "Invalid ID format. Must be exactly 4 hex digits.")
            return
        desc_text, ok = QInputDialog.getText(self, "Add Boot Entry", "Enter description:")
        if not ok:
            return
        # Add to table (active and default set to False)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(id_text))
        self.table.setItem(row, 1, QTableWidgetItem("No"))
        self.table.setItem(row, 2, QTableWidgetItem("No"))
        self.table.setItem(row, 3, QTableWidgetItem(desc_text))
        self.changes_made = True
        self.save_button.setEnabled(True)

    def remove_entry(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "No row selected to remove.")
            return
        reply = QMessageBox.question(self, "Confirm Remove", "Are you sure you want to remove the selected boot entry?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)
            self.changes_made = True
            self.save_button.setEnabled(True)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec())
