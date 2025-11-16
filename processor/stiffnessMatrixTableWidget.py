from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt



class StiffnessMatrixTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setMinimumHeight(400)

    def set_matrix_data(self, matrix):
        if not matrix:
            return

        n = len(matrix)
        self.setRowCount(n)
        self.setColumnCount(n)

        # Устанавливаем заголовки
        headers = [f"Узел {i + 1}" for i in range(n)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        # Заполняем данными
        for i in range(n):
            for j in range(n):
                value = matrix[i][j]
                if abs(value) < 1e-10:  # Показываем нули как 0
                    display_value = "0"
                else:
                    display_value = f"{value:.6e}"

                item = QTableWidgetItem(display_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)