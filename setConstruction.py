from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QVBoxLayout, QWidget,
                             QDockWidget, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QSizePolicy, QLabel,
                             QCheckBox, QApplication, QMessageBox)
from PyQt5.QtCore import Qt
from setConstructionTable import ConstructionTable
import json
import os


class Dock_cunstraction(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)  # Используем современный синтаксис
        self.mainWindow = parent
        self.setupUI()
        self.setWindowTitle('Конструкция')


    def setupUI(self):
        self.setMinimumWidth(650)

        # Создаем содержимое для меню
        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)

        # Добавляем таблицу (Стержни)
        self.barsTable = ConstructionTable("bar", 1, 4, ['Длина, L', 'Поперечное сечение, A', 'Модуль упругости, Е', 'Напряжение, σ'], parent=self.mainWindow)
        self.barsTable.itemChanged.connect(self.on_table_item_changed)

        barsTableTitle = QLabel('Стержни')
        barsTableTitle.setAlignment(Qt.AlignCenter)
        dock_layout.addWidget(barsTableTitle)

        barsLayout = QHBoxLayout()
        barsLayout.addStretch(1)
        addBar = QPushButton('Добавить')
        remBar = QPushButton('Удалить')
        addBar.clicked.connect(self.barsTable.add_row)
        remBar.clicked.connect(self.barsTable.remove_selected_row)
        addBar.setFixedSize(170, 30)
        remBar.setFixedSize(170, 30)
        barsLayout.addWidget(addBar)
        barsLayout.addWidget(remBar)

        dock_layout.addWidget(self.barsTable)
        dock_layout.addLayout(barsLayout)
        # Добавляем таблицы (нагрузки)
        LoadLayout = QHBoxLayout()


        # Добавляем таблицу (Сосредоточенные нагрузки)

        self.concentratedLoadsTable = ConstructionTable("node_loads", 3, 2, ['Номер узла', 'Значение, F'], parent=self.mainWindow)
        self.concentratedLoadsTable.itemChanged.connect(self.on_table_item_changed)

        concLoadsTableTitle = QLabel('Сосредоточенные нагрузки')
        concLoadsTableTitle.setAlignment(Qt.AlignCenter)
        conLoadLayout = QVBoxLayout()
        conLoadLayout.addWidget(concLoadsTableTitle)

        dock_layout.addWidget(self.concentratedLoadsTable)
        addConLoad = QPushButton('Добавить')
        remConLoad = QPushButton('Удалить')
        remConLoad.setFixedHeight(30)
        addConLoad.setFixedHeight(30)
        addConLoad.clicked.connect(self.concentratedLoadsTable.add_row)
        remConLoad.clicked.connect(self.concentratedLoadsTable.remove_selected_row)

        buttonsConLayout = QHBoxLayout()
        buttonsConLayout.addWidget(addConLoad)
        buttonsConLayout.addWidget(remConLoad)
        conLoadLayout.addWidget(self.concentratedLoadsTable)
        conLoadLayout.addLayout(buttonsConLayout)

        # Добавляем таблицу (Распределенные нагрузки)

        self.distributedLoadTable = ConstructionTable("distributed_loads", 1, 2, ['Номер стержня', 'Значение, q'], parent=self.mainWindow)
        self.distributedLoadTable.itemChanged.connect(self.on_table_item_changed)

        distrLoadsTableTitle = QLabel('Распределенные нагрузки')
        distrLoadsTableTitle.setAlignment(Qt.AlignCenter)
        distrLoadLayout = QVBoxLayout()
        distrLoadLayout.addWidget(distrLoadsTableTitle)


        buttonsDistrLayout = QHBoxLayout()
        addDistrLoad = QPushButton('Добавить')
        remDistrLoad = QPushButton('Удалить')
        addDistrLoad.setFixedHeight(30)
        remDistrLoad.setFixedHeight(30)
        addDistrLoad.clicked.connect(self.distributedLoadTable.add_row)
        remDistrLoad.clicked.connect(self.distributedLoadTable.remove_selected_row)


        buttonsDistrLayout.addWidget(addDistrLoad)
        buttonsDistrLayout.addWidget(remDistrLoad)

        distrLoadLayout.addWidget(self.distributedLoadTable)
        distrLoadLayout.addLayout(buttonsDistrLayout)

        LoadLayout.addLayout(conLoadLayout)
        LoadLayout.addLayout(distrLoadLayout)

        dock_layout.addLayout(LoadLayout)

        # Управление заделками
        sealingLayout = QHBoxLayout()
        left_seal_ChBox = QCheckBox()
        text_left_seal_ChBox = QLabel('Левая заделка')
        text_right_seal_ChBox = QLabel('Правая заделка')
        right_seal_ChBox = QCheckBox()

        sealingLayout.addWidget(left_seal_ChBox)
        sealingLayout.addWidget(text_left_seal_ChBox)
        sealingLayout.addSpacing(20)
        sealingLayout.addWidget(right_seal_ChBox)
        sealingLayout.addWidget(text_right_seal_ChBox)
        sealingLayout.addStretch(1)

        dock_layout.addLayout(sealingLayout)

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

    def on_table_item_changed(self):
        self.mainWindow.statusLabel.setText("Проект не сохранен")

