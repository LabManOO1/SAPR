from PyQt5.QtWidgets import QMessageBox, QTableWidget, QHeaderView, QItemDelegate, QLineEdit, QTableWidgetItem
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QValidator, QRegExpValidator


class NumericDelegate(QItemDelegate):
    def __init__(self, parent=None, is_integer=False, is_plus=False):
        super().__init__(parent)
        self.is_integer = is_integer
        self.is_plus = is_plus

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)

        if self.is_integer:
            validator = QIntValidator()
            if self.is_plus:
                validator.setBottom(0)
            editor.setValidator(validator)
        else:
            if self.is_plus:
                # Для положительных чисел: цифры, точка, запятая
                regex = QRegExp(r"^\d*[,.]?\d*$")
            else:
                # Для любых чисел: цифры, точка, запятая, знак минуса
                regex = QRegExp(r"^-?\d*[,.]?\d*$")

            validator = QRegExpValidator(regex)
            editor.setValidator(validator)

            editor.textChanged.connect(lambda text: self.on_text_changed(editor, text))

        return editor

    def on_text_changed(self, editor, text):
        """Автоматически заменяем запятую на точку"""
        if ',' in text:
            new_text = text.replace(',', '.')
            editor.setText(new_text)
            editor.setCursorPosition(len(new_text))
        if text[-1] == '.':
            text += "0"

    def setModelData(self, editor, model, index):
        """Сохраняем данные из редактора в модель"""
        text = editor.text().strip()


        # Разрешаем пустые значения
        if text == "":
            model.setData(index, "", Qt.EditRole)
            return

        # Заменяем запятую на точку для корректного преобразования
        text = text.replace(',', '.')
        if text[-1] == '.':
            text += "0"
        if text == "0" or text == "0.0":
            text = "1"
        if text == ".0":
            text = "1"
        if text[0] == ".":
            text = text.replace(".", "")

        # Проверяем валидность
        if self.is_integer:
            try:
                value = int(text)
                if self.is_plus and value < 0:
                    model.setData(index, "", Qt.EditRole)
                else:
                    model.setData(index, str(value), Qt.EditRole)
            except ValueError:
                model.setData(index, "", Qt.EditRole)
        else:
            try:
                value = float(text)
                if self.is_plus and value < 0:
                    model.setData(index, "", Qt.EditRole)
                else:
                    model.setData(index, text, Qt.EditRole)  # Сохраняем с точкой
            except ValueError:
                model.setData(index, "", Qt.EditRole)

class ConstructionTable(QTableWidget):
    def __init__(self, type, columnCount, headers, rowCount=0, data=None, parent=None):
        super().__init__(parent=parent)
        self.setRowCount(rowCount)
        self.setColumnCount(columnCount)
        self.setItem
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

        if self.currentRow() < 0:
            row_position = self.rowCount()
            self.insertRow(row_position)
        else:
            self.insertRow(self.currentRow() + 1)
            self.clearSelection()

        self.clearSelection()
        self.setCurrentCell(-1, -1)

    def remove_selected_row(self):
        """Удалить выбранную строку"""
        if self.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Таблица пустая")
            return
        if self.rowCount() == 1:
            self.removeRow(0)
            self.clearSelection()
            self.setCurrentCell(-1, -1)
            self.emit_data_changed_signal()
            return

        current_row = self.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите строку для удаления")
            return

        self.removeRow(current_row)
        self.clearSelection()
        self.setCurrentCell(-1, -1)
        self.emit_data_changed_signal()

    def emit_data_changed_signal(self):
        """Генерирует сигнал об изменении данных"""
        # Создаем фиктивный QTableWidgetItem и эмитируем сигнал
        if self.rowCount() > 0:
            # Используем первую ячейку для генерации сигнала
            fake_item = QTableWidgetItem()
            self.itemChanged.emit(fake_item)
        else:
            # Если таблица пустая, все равно генерируем сигнал
            fake_item = QTableWidgetItem()
            self.itemChanged.emit(fake_item)

    def keyPressEvent(self, event):
        """Обработка клавиш с разными действиями"""
        if event.key() == Qt.Key_Delete:
            # Delete - удалить строки
            self.remove_selected_row()

        elif event.key() == Qt.Key_Insert:
            self.add_row()

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

    def setTableData(self, data):
        try:
            self.blockSignals(True)
            if self.type == "bar":
                self.setRowCount(int(data["Objects"][0]["quantity"]))
                for list_of_values in data["Objects"][0]["list_of_values"]:
                    bar_index = int(list_of_values["barNumber"]) - 1
                    if 0 <= bar_index < self.rowCount():
                        self.setItem(bar_index, 0, QTableWidgetItem(str(list_of_values["length"])))
                        self.setItem(bar_index, 1, QTableWidgetItem(str(list_of_values["cross_section"])))
                        self.setItem(bar_index, 2, QTableWidgetItem(str(list_of_values["modulus_of_elasticity"])))
                        self.setItem(bar_index, 3, QTableWidgetItem(str(list_of_values["pressure"])))
            if self.type == "node_loads":
                current_row = 0
                self.setRowCount(int(data["Objects"][1]["quantity"]))
                for list_of_values in data["Objects"][1]["list_of_values"]:
                    if 0 <= current_row < self.rowCount():
                        self.setItem(current_row, 0, QTableWidgetItem(str(list_of_values["node_number"])))
                        self.setItem(current_row, 1, QTableWidgetItem(str(list_of_values["force_value"])))
                        current_row += 1
            if self.type == "distributed_loads":
                current_row = 0
                self.setRowCount(int(data["Objects"][2]["quantity"]))
                for list_of_values in data["Objects"][2]["list_of_values"]:
                    if 0 <= current_row < self.rowCount():
                        self.setItem(current_row, 0, QTableWidgetItem(str(list_of_values["bar_number"])))
                        self.setItem(current_row, 1, QTableWidgetItem(str(list_of_values["distributed_value"])))
                        current_row += 1
        except (KeyError, ValueError, IndexError) as e:
            print(f"Ошибка загрузки таблицы: {e}")
            return False
        finally:
            # Всегда разблокируем сигналы, даже при ошибке
            self.blockSignals(False)
        return True

    def getTableData(self):
        """Получить данные таблицы в виде словаря"""
        data = {}
        data["Object"] = self.type
        list_of_values = []
        f = True
        rowsCount = self.rowCount()
        if (self.type == "bar") and (self.rowCount() == 0):
            f = False

        if self.type == "bar":
            data["quantity"] = rowsCount
            for row in range(self.rowCount()):
                if all([self.item(row, 0), self.item(row, 1), self.item(row, 2), self.item(row, 3)]):
                    row_data = dict()
                    row_data["barNumber"] = row + 1
                    row_data["length"] = float(self.item(row, 0).text())
                    row_data["cross_section"] = float(self.item(row, 1).text())
                    row_data["modulus_of_elasticity"] = float(self.item(row, 2).text())
                    row_data["pressure"] = float(self.item(row, 3).text())
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values

        if self.type == "node_loads":
            data["quantity"] = rowsCount
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = dict()
                    row_data["node_number"] = float(self.item(row, 0).text())
                    row_data["force_value"] = float(self.item(row, 1).text())
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values

        if self.type == "distributed_loads":
            data["quantity"] = rowsCount
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 1):
                    row_data = dict()
                    row_data["bar_number"] = float(self.item(row, 0).text())
                    row_data["distributed_value"] = float(self.item(row, 1).text())
                    list_of_values.append(row_data)
                else:
                    f = False
            data["list_of_values"] = list_of_values
        if f:
            return data
        else:
            return False
