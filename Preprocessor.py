from PyQt5.QtWidgets import (QPushButton, QLabel,
                             QVBoxLayout, QWidget,
                             QHBoxLayout,)
from PyQt5.QtCore import Qt
from setConstruction import Dock_cunstraction


class PreprocessorTab(QWidget):  # Наследуем от QWidget, а не от QVBoxLayout
    def __init__(self, main_window):  # Принимаем главное окно как параметр
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setupPreprocessor()

    def setupPreprocessor(self):
        mainPreProc_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        middle_layout = QHBoxLayout()
        label = QLabel('Изображение')
        middle_layout.addWidget(label)



        FileButton = QPushButton('Файл')
        top_layout.addWidget(FileButton)
        top_layout.addStretch(1)

        # СОЗДАЕМ ВЫДВИЖНОЕ МЕНЮ
        self.create_dock_menu()

        # Кнопка для показа/скрытия меню (в тулбаре)
        self.toggle_dock_btn = QPushButton("Показать/скрыть настройки конструкции")
        self.toggle_dock_btn.clicked.connect(self.toggle_dock)

        top_layout.addWidget(self.toggle_dock_btn)



        mainPreProc_layout.addLayout(top_layout)
        mainPreProc_layout.addStretch(1)

        mainPreProc_layout.addLayout(middle_layout)
        mainPreProc_layout.addStretch(1)


        mainPreProc_layout.setAlignment(middle_layout, Qt.AlignCenter)

    def create_dock_menu(self):
        """Создаем выдвижное меню и добавляем его в главное окно"""
        self.dock_menu = Dock_cunstraction(self.main_window)  # Создаем для главного окна
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_menu)  # Добавляем в главное окно

    def toggle_dock(self):
        """Показываем/скрываем выдвижное меню"""
        self.dock_menu.setVisible(not self.dock_menu.isVisible())