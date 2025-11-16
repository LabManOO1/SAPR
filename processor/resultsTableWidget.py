from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt



class ResultsTable(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Только чтение
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def set_data(self, data):
        self.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)