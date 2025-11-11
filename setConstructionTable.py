from PyQt5.QtWidgets import QMessageBox, QTableWidget, QHeaderView, QItemDelegate, QLineEdit, QTableWidgetItem
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator


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

        return editor

    def setModelData(self, editor, model, index):
        """Сохраняем данные из редактора в модель - УПРОЩЕННАЯ ВЕРСИЯ"""
        text = editor.text().strip()

        # Разрешаем пустые значения
        if text == "":
            model.setData(index, "", Qt.EditRole)
            return

        text = text.replace(',', '.')
        if text[0] == '.':
            text = '0' + text
        if text[-1] == '.':
            text = 1

        # Для целых чисел
        if self.is_integer:
            try:
                value = int(float(text))  # Сначала в float, потом в int для случаев "1.0"
                if self.is_plus and value < 0:
                    model.setData(index, "", Qt.EditRole)
                else:
                    model.setData(index, str(value), Qt.EditRole)
            except (ValueError, TypeError):
                model.setData(index, "", Qt.EditRole)
        # Для вещественных чисел
        else:
            try:
                value = float(text)
                if self.is_plus and value < 0:
                    model.setData(index, "", Qt.EditRole)
                else:
                    # Сохраняем как есть, без лишних преобразований
                    model.setData(index, text, Qt.EditRole)
            except (ValueError, TypeError):
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

        current_row = self.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите строку для удаления")
            return

        self.removeRow(current_row)
        self.clearSelection()
        self.setCurrentCell(-1, -1)
        self.emit_data_changed_signal()

    def remove_related_loads(self, bar_number, concentrated_loads_table, distributed_loads_table):
        """Удалить нагрузки, связанные с удаляемым стержнем"""
        # Удаляем распределенные нагрузки для этого стержня
        self.remove_distributed_loads(bar_number, distributed_loads_table)

        # Удаляем сосредоточенные нагрузки для узлов этого стержня
        self.remove_node_loads(bar_number, concentrated_loads_table)

    def remove_distributed_loads(self, bar_number, distributed_loads_table):
        """Удалить распределенные нагрузки для указанного стержня"""
        rows_to_remove = []

        for row in range(distributed_loads_table.rowCount()):
            item = distributed_loads_table.item(row, 0)
            if item and item.text().strip():
                try:
                    load_bar_number = int(item.text().strip())
                    if load_bar_number == bar_number:
                        rows_to_remove.append(row)
                except ValueError:
                    continue

        # Удаляем строки в обратном порядке, чтобы индексы не сбивались
        for row in sorted(rows_to_remove, reverse=True):
            distributed_loads_table.removeRow(row)

    def remove_node_loads(self, bar_number, concentrated_loads_table):
        """Удалить сосредоточенные нагрузки для узлов указанного стержня"""
        node1 = bar_number
        node2 = bar_number + 1

        rows_to_remove = []

        for row in range(concentrated_loads_table.rowCount()):
            item = concentrated_loads_table.item(row, 0)
            if item and item.text().strip():
                try:
                    load_node_number = int(item.text().strip())
                    if load_node_number == node1 or load_node_number == node2:
                        rows_to_remove.append(row)
                except ValueError:
                    continue

        # Удаляем строки в обратном порядке, чтобы индексы не сбивались
        for row in sorted(rows_to_remove, reverse=True):
            concentrated_loads_table.removeRow(row)

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
                quantity = data["Objects"][0]["quantity"]
                if isinstance(quantity, str):
                    quantity = int(quantity)
                self.setRowCount(quantity)

                for list_of_values in data["Objects"][0]["list_of_values"]:
                    bar_number = list_of_values["barNumber"]
                    if isinstance(bar_number, str):
                        bar_number = int(bar_number)
                    bar_index = bar_number - 1

                    if 0 <= bar_index < self.rowCount():
                        # Безопасное создание элементов с проверкой значений
                        length = list_of_values.get("length", "")
                        cross_section = list_of_values.get("cross_section", "")
                        modulus = list_of_values.get("modulus_of_elasticity", "")
                        pressure = list_of_values.get("pressure", "")

                        self.setItem(bar_index, 0, QTableWidgetItem(str(length) if length else ""))
                        self.setItem(bar_index, 1, QTableWidgetItem(str(cross_section) if cross_section else ""))
                        self.setItem(bar_index, 2, QTableWidgetItem(str(modulus) if modulus else ""))
                        self.setItem(bar_index, 3, QTableWidgetItem(str(pressure) if pressure else ""))

            if self.type == "node_loads":
                quantity = data["Objects"][1]["quantity"]
                if isinstance(quantity, str):
                    quantity = int(quantity)
                self.setRowCount(quantity)

                current_row = 0
                for list_of_values in data["Objects"][1]["list_of_values"]:
                    if 0 <= current_row < self.rowCount():
                        node_number = list_of_values.get("node_number", "")
                        force_value = list_of_values.get("force_value", "")

                        self.setItem(current_row, 0, QTableWidgetItem(str(node_number) if node_number else ""))
                        self.setItem(current_row, 1, QTableWidgetItem(str(force_value) if force_value else ""))
                        current_row += 1

            if self.type == "distributed_loads":
                quantity = data["Objects"][2]["quantity"]
                if isinstance(quantity, str):
                    quantity = int(quantity)
                self.setRowCount(quantity)

                current_row = 0
                for list_of_values in data["Objects"][2]["list_of_values"]:
                    if 0 <= current_row < self.rowCount():
                        bar_number = list_of_values.get("bar_number", "")
                        distributed_value = list_of_values.get("distributed_value", "")

                        self.setItem(current_row, 0, QTableWidgetItem(str(bar_number) if bar_number else ""))
                        self.setItem(current_row, 1,
                                     QTableWidgetItem(str(distributed_value) if distributed_value else ""))
                        current_row += 1

        except (KeyError, ValueError, IndexError, AttributeError) as e:
            print(f"Ошибка загрузки таблицы: {e}")
            return False
        finally:
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
                row_data = dict()
                row_data["barNumber"] = row + 1

                # Безопасное получение значений с проверкой на None
                try:
                    # Получаем элементы безопасно
                    item_0 = self.item(row, 0)
                    item_1 = self.item(row, 1)
                    item_2 = self.item(row, 2)
                    item_3 = self.item(row, 3)

                    # Получаем текст или пустую строку если элемент None
                    length_text = item_0.text().strip() if item_0 else ""
                    cross_section_text = item_1.text().strip() if item_1 else ""
                    modulus_text = item_2.text().strip() if item_2 else ""
                    pressure_text = item_3.text().strip() if item_3 else ""

                    # Проверяем, что все ячейки заполнены
                    if not all([length_text, cross_section_text, modulus_text, pressure_text]):
                        f = False
                        continue

                    # Преобразуем в числа
                    row_data["length"] = float(length_text) if length_text else 0
                    row_data["cross_section"] = float(cross_section_text) if cross_section_text else 0
                    row_data["modulus_of_elasticity"] = float(modulus_text) if modulus_text else 0
                    row_data["pressure"] = float(pressure_text) if pressure_text else 0

                    list_of_values.append(row_data)
                except (ValueError, AttributeError) as e:
                    print(f"Ошибка в строке {row}: {e}")
                    f = False

            data["list_of_values"] = list_of_values

        if self.type == "node_loads":
            data["quantity"] = rowsCount
            for row in range(self.rowCount()):
                row_data = dict()

                try:
                    item_0 = self.item(row, 0)
                    item_1 = self.item(row, 1)

                    node_text = item_0.text().strip() if item_0 else ""
                    force_text = item_1.text().strip() if item_1 else ""

                    if not all([node_text, force_text]):
                        f = False
                        continue

                    row_data["node_number"] = int(node_text) if node_text else 0
                    row_data["force_value"] = float(force_text) if force_text else 0

                    list_of_values.append(row_data)
                except (ValueError, AttributeError) as e:
                    print(f"Ошибка в строке {row}: {e}")
                    f = False

            data["list_of_values"] = list_of_values

        if self.type == "distributed_loads":
            data["quantity"] = rowsCount
            for row in range(self.rowCount()):
                row_data = dict()

                try:
                    item_0 = self.item(row, 0)
                    item_1 = self.item(row, 1)

                    bar_text = item_0.text().strip() if item_0 else ""
                    distributed_text = item_1.text().strip() if item_1 else ""

                    if not all([bar_text, distributed_text]):
                        f = False
                        continue

                    row_data["bar_number"] = int(bar_text) if bar_text else 0
                    row_data["distributed_value"] = float(distributed_text) if distributed_text else 0

                    list_of_values.append(row_data)
                except (ValueError, AttributeError) as e:
                    print(f"Ошибка в строке {row}: {e}")
                    f = False

            data["list_of_values"] = list_of_values

        if f:
            return data
        else:
            return False