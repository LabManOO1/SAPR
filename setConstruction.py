from PyQt5.QtWidgets import (QVBoxLayout, QWidget,
                             QDockWidget, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt


class Dock_cunstraction(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)  # Используем современный синтаксис
        self.setupUI()
        self.setWindowTitle('Конструкция')

    def setupUI(self):
        self.setMinimumWidth(500)

        # Создаем содержимое для меню
        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)

        # Добавляем таблицу (временно)
        table = QTableWidget()
        table.setRowCount(3)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Параметр", "Значение"])

        # Добавляем тестовые данные
        table.setItem(0, 0, QTableWidgetItem("Длина"))
        table.setItem(0, 1, QTableWidgetItem("1000"))
        table.setItem(1, 0, QTableWidgetItem("Ширина"))
        table.setItem(1, 1, QTableWidgetItem("500"))
        table.setItem(2, 0, QTableWidgetItem("Высота"))
        table.setItem(2, 1, QTableWidgetItem("200"))

        dock_layout.addWidget(table)
        self.setWidget(dock_content)

        # Настраиваем свойства dock
        self.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetFloatable
        )
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Скрываем меню по умолчанию
        self.setVisible(False)