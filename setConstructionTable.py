from PyQt5.QtWidgets import QMessageBox, QTableWidget, QHeaderView, QItemDelegate, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class NumericDelegate(QItemDelegate):
    def __init__(self, parent=None, is_integer=False, is_plus=False):
        super().__init__(parent)
        self.main_window = parent
        self.is_integer = is_integer
        self.is_plus = is_plus

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)

        if self.is_integer:
            # Только целые числа
            validator = QIntValidator()
            if self.is_plus:
                validator.setBottom(0)  # Только положительные числа
        else:
            # Дробные числа
            validator = QDoubleValidator()
            if self.is_plus:
                validator.setBottom(0)  # Только положительные числа
            validator.setNotation(QDoubleValidator.StandardNotation)

        editor.setValidator(validator)
        return editor

class ConstructionTable(QTableWidget):
    def __init__(self, type, rowCount, columnCount, headers, data=None, parent=None):
        super().__init__(parent=parent)
        self.setRowCount(rowCount)
        self.setColumnCount(columnCount)
        self.fillingTable(data)
        self.setHorizontalHeaderLabels(headers)
        self.type = type
        self.setupTable()

    def setupTable(self):
        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растянуть по ширине
        self.setDelegate()

    def setDelegate(self):
        if self.type == "bar":
            self.setItemDelegate(NumericDelegate(self, is_integer=False, is_plus=True))
        if self.type == "node_loads":
            self.setItemDelegateForColumn(0, NumericDelegate(self, is_integer=True, is_plus=True))
            self.setItemDelegateForColumn(1, NumericDelegate(self, is_integer=False, is_plus=False))
        if self.type == "distributed_loads":
            self.setItemDelegateForColumn(0, NumericDelegate(self, is_integer=True, is_plus=True))
            self.setItemDelegateForColumn(1, NumericDelegate(self, is_integer=False, is_plus=False))

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
            for item in self.selectedItems():
                self.setItem(item.row(), item.column(), None)  # Устанавливаем None

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
        f = True
        barsCount = self.rowCount()


        if self.type == "bar":
            data["quantity"] = barsCount
            for row in range(self.rowCount()):
                if all([self.item(row, 0), self.item(row, 1), self.item(row, 2), self.item(row, 3)]):
                    row_data = dict()
                    row_data["barNumber"] = row
                    row_data["length"] = self.item(row, 0).text()
                    row_data["cross_section"] = self.item(row, 1).text()
                    row_data["modulus_of_elasticity"] = self.item(row, 2).text()
                    row_data["pressure"] = self.item(row, 3).text()
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values

        if self.type == "node_loads":
            data["quantity"] = barsCount
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = dict()
                    row_data["node_number"] = self.item(row, 0).text()
                    row_data["force_value"] = self.item(row, 1).text()
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values

        if self.type == "distributed_loads":
            data["quantity"] = barsCount
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = dict()
                    row_data["bar_number"] = self.item(row, 0).text()
                    row_data["distributed_value"] = self.item(row, 1).text()
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values
        if f:
            return data
        else:
            return





