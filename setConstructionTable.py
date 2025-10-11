import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QLabel, QVBoxLayout, QTabWidget, \
    QWidget, QCheckBox, QTextEdit, QHBoxLayout, QToolBar, QDockWidget, QTableWidget, QTableWidgetItem, QMenu, QHeaderView, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon



class ConstructionTable(QTableWidget):
    def __init__(self, type, rowCount, columnCount, headers, data=None, parent=None):
        super().__init__(parent=parent)
        self.setRowCount(rowCount)
        self.setColumnCount(columnCount)
        self.fillingTable(data)
        self.setHorizontalHeaderLabels(headers)
        self.setupTable()
        self.type = type


    def setupTable(self):
        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растянуть по ширине

    def fillingTable(self, data):
        if data is None:
            return

    def add_row(self):
        """Добавить строку"""
        max_rows = 100  # Максимальное количество строк
        if self.rowCount() >= max_rows:
            QMessageBox.warning(self, "Предупреждение", f"Нельзя добавить более {max_rows} строк")
            return

        row_position = self.rowCount()
        self.insertRow(row_position)

    def remove_selected_row(self):
        """Удалить выбранную строку"""
        if self.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Таблица пустая")
            return
        if self.rowCount() == 1:
            self.removeRow(0)
            self.clearSelection()
            self.setCurrentCell(-1, -1)
            return

        current_row = self.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите строку для удаления")
            return

        # Подтверждение удаления
        # reply = QMessageBox.question(self, "Подтверждение",
        #                              f"Удалить строку {current_row}?",
        #                              QMessageBox.Yes | QMessageBox.No)

        # if reply == QMessageBox.Yes:
        #     self.removeRow(current_row)
        #     self.clearSelection()
        #     self.setCurrentCell(-1, -1)
        self.removeRow(current_row)
        self.clearSelection()
        self.setCurrentCell(-1, -1)

    def keyPressEvent(self, event):
        """Обработка клавиш с разными действиями"""
        if event.key() == Qt.Key_Delete:
            # Delete - удалить строки
            self.remove_selected_row()

        elif event.key() == Qt.Key_Backspace:
            # Backspace - очистить содержимое ячеек
            self.clear_selected_cells()

        else:
            super().keyPressEvent(event)

    def clear_selected_cells(self):
        """Очистить содержимое выделенных ячеек по Backspace"""
        for item in self.selectedItems():
            item.setText("")


    def getTableData(self):
        """Получить данные таблицы в виде словаря"""
        data = {}
        data["Object"] = self.type
        list_of_values = []

        rodsCount = self.rowCount()

        if self.type == "rod":
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1) and self.item(row, 2) and self.item(row, 3):
                    row_data = {}
                    row_data["rodNumber"] = row
                    row_data["length"] = self.item(row, 0).text()
                    row_data["cross_section"] = self.item(row, 1).text()
                    row_data["modulus_of_elasticity"] = self.item(row, 2).text()
                    row_data["pressure"] = self.item(row, 3).text()
                    list_of_values.append(row_data)
                else:
                    QMessageBox.information(self, "Информация", "Данные заполнены некорректно!")
                    return
            data["list_of_values"] = list_of_values

        if self.type == "node_loads":
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = {}
                    row_data["node_number"] = self.item(row, 0).text()
                    row_data["force_value"] = self.item(row, 1).text()
                    list_of_values.append(row_data)
                else:
                    QMessageBox.information(self, "Информация", "Данные заполнены некорректно!")
                    return
            data["list_of_values"] = list_of_values

        if self.type == "distributed_loads":
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = {}
                    row_data["rod_number"] = self.item(row, 0).text()
                    row_data["distributed_value"] = self.item(row, 1).text()
                    list_of_values.append(row_data)
                else:
                    QMessageBox.information(self, "Информация", "Данные заполнены некорректно!")
                    return
            data["list_of_values"] = list_of_values
        return data







        for rodNumber in range(rodsCount):
            pass




