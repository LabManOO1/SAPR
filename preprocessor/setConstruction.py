from PyQt5.QtWidgets import (QVBoxLayout, QWidget,
                             QDockWidget, QPushButton, QHBoxLayout, QLabel,
                             QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from preprocessor.setConstructionTable import ConstructionTable


class Dock_cunstraction(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)  # Используем современный синтаксис
        self.mainWindow = parent

        self.setupUI()
        self.setWindowTitle('Конструкция')

        self.visibilityChanged.connect(self.on_visibility_changed)
        self.topLevelChanged.connect(self.on_top_level_changed)

    def setupUI(self):
        self.setMinimumWidth(650)

        # Создаем содержимое для меню
        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)

        # Добавляем таблицу (Стержни)
        self.barsTable = ConstructionTable("bar", 4, ['Длина, L', 'Поперечное сечение, A', 'Модуль упругости, Е',
                                                      'Напряжение, σ'], parent=self.mainWindow)

        barsTableTitle = QLabel('Стержни')
        barsTableTitle.setAlignment(Qt.AlignCenter)
        dock_layout.addWidget(barsTableTitle)

        barsLayout = QHBoxLayout()
        barsLayout.addStretch(1)
        addBar = QPushButton('Добавить')
        remBar = QPushButton('Удалить')
        addBar.clicked.connect(self.barsTable.add_row)
        remBar.clicked.connect(self.remove_bar_with_loads)  # Изменено на новый метод
        addBar.setFixedSize(170, 30)
        remBar.setFixedSize(170, 30)
        barsLayout.addWidget(addBar)
        barsLayout.addWidget(remBar)

        dock_layout.addWidget(self.barsTable)
        dock_layout.addLayout(barsLayout)
        # Добавляем таблицы (нагрузки)
        LoadLayout = QHBoxLayout()

        # Добавляем таблицу (Сосредоточенные нагрузки)

        self.concentratedLoadsTable = ConstructionTable("node_loads", 2, ['Номер узла', 'Значение, F'],
                                                        parent=self.mainWindow)

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

        self.distributedLoadTable = ConstructionTable("distributed_loads", 2, ['Номер стержня', 'Значение, q'],
                                                      parent=self.mainWindow)

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
        self.left_seal_ChBox = QCheckBox()
        text_left_seal_ChBox = QLabel('Левая заделка')
        text_right_seal_ChBox = QLabel('Правая заделка')
        self.right_seal_ChBox = QCheckBox()

        sealingLayout.addWidget(self.left_seal_ChBox)
        sealingLayout.addWidget(text_left_seal_ChBox)
        sealingLayout.addSpacing(20)
        sealingLayout.addWidget(self.right_seal_ChBox)
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

    def on_visibility_changed(self, visible):
        """Обновляем графику при изменении видимости док-меню"""
        self.update_construction_graphics()

    def on_top_level_changed(self, floating):
        """Обновляем графику при откреплении/прикреплении док-меню"""
        self.update_construction_graphics()

    def update_construction_graphics(self):
        """Обновляет графику конструкции"""
        if hasattr(self.mainWindow, 'preprocessor_tab'):
            preprocessor_tab = self.mainWindow.preprocessor_tab
            if hasattr(preprocessor_tab, 'graphics_manager') and preprocessor_tab.graphics_manager:
                # Даем время на применение новых размеров
                QTimer.singleShot(150, preprocessor_tab.graphics_manager.update_construction)

    def remove_bar_with_loads(self):
        """Удалить стержень и все связанные с ним нагрузки"""
        if self.barsTable.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Таблица пустая")
            return

        current_row = self.barsTable.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите строку для удаления")
            return

        # Получаем номер удаляемого стержня
        bar_number = current_row + 1

        # Удаляем стержень и связанные нагрузки через PreprocessorTab
        preprocessor_tab = self.mainWindow.preprocessor_tab
        preprocessor_tab.remove_bar_with_related_loads(bar_number)

        # Удаляем сам стержень из таблицы
        self.barsTable.removeRow(current_row)
        self.barsTable.clearSelection()
        self.barsTable.setCurrentCell(-1, -1)
        self.barsTable.emit_data_changed_signal()