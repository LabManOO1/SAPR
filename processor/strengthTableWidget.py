from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class StrengthTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            "Стержень",
            "Макс. напряжение |σ|",
            "Допустимое напряжение [σ]",
            "Состояние"
        ])
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def set_strength_data(self, bars_data, max_stresses, allowable_stresses, conditions):
        self.setRowCount(len(bars_data))

        for i, bar in enumerate(bars_data):
            # Номер стержня
            item_bar = QTableWidgetItem(f"{bar['barNumber']}")
            item_bar.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 0, item_bar)

            # Максимальное напряжение
            item_stress = QTableWidgetItem(f"{smart_round(max_stresses[i])}")
            item_stress.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 1, item_stress)

            # Допустимое напряжение
            item_allowable = QTableWidgetItem(f"{smart_round(allowable_stresses[i])}")
            item_allowable.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 2, item_allowable)

            # Состояние
            status = "Прочность обеспечена" if conditions[i] else "ПРЕВЫШЕНИЕ!"
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 3, item_status)

            # Изменяем цвет строки если прочность не обеспечена
            if not conditions[i]:
                for col in range(4):
                    self.item(i, col).setBackground(QColor(255, 200, 200))  # Красный фон
                    self.item(i, col).setForeground(QColor(139, 0, 0))  # Темно-красный текст

def smart_round(number, precision=6):
    """
    Округляет число до указанной точности и убирает лишние нули
    """
    rounded = round(number, precision)

    # Преобразуем в строку для обработки
    str_rounded = str(rounded)

    # Если есть дробная часть
    if '.' in str_rounded:
        # Убираем нули в конце и точку, если после нее ничего не осталось
        str_rounded = str_rounded.rstrip('0').rstrip('.')

    return str_rounded