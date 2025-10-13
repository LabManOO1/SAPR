from PyQt5.QtWidgets import (QPushButton, QLabel,
                             QVBoxLayout, QWidget,
                             QHBoxLayout, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt
from setConstruction import Dock_cunstraction
from fileManager import FileManager
import os
import json


class PreprocessorTab(QWidget):  # Наследуем от QWidget, а не от QVBoxLayout
    def __init__(self, main_window, current_path_file):  # Принимаем главное окно как параметр
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.current_path_file = current_path_file
        self.setupPreprocessor()


    def setupPreprocessor(self):
        mainPreProc_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        middle_layout = QHBoxLayout()
        label = QLabel('Изображение')
        middle_layout.addWidget(label)



        self.FileButton = QPushButton('Файл')
        self.create_file_menu()
        top_layout.addWidget(self.FileButton)
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

    def create_file_menu(self):
        """Создает всплывающее меню для кнопки Файл"""
        # Создаем меню и привязываем его к кнопке
        file_menu = QMenu(self)

        # Действие "Новый проект"
        new_action = QAction("Новый проект", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)

        # Действие "Открыть проект"
        open_action = QAction("Открыть проект...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)

        # Действие "Сохранить"
        save_action = QAction("Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)


        # Разделитель
        file_menu.addSeparator()


        # Разделитель
        file_menu.addSeparator()

        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close_application)

        # Добавляем все действия в меню
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        file_menu.addAction(exit_action)

        # Привязываем меню к кнопке
        self.FileButton.setMenu(file_menu)
    def new_project(self):
        file_manager = FileManager(self)
        file_manager.create_new_project()
        self.current_path_file = file_manager.file_path
        self.main_window.file_path = self.current_path_file
        self.main_window.statusBar().showMessage("Новый проект создан", msecs=3000)

    def open_project(self):
        file_manager = FileManager(self)
        file_manager.open_existing_project()
        self.current_path_file = file_manager.file_path
        self.main_window.file_path = self.current_path_file
        self.main_window.statusBar().showMessage("Проект загружен", msecs=3000)

    def save_project(self):
        """Сохранить проект"""
        # Проверяем, есть ли путь к файлу
        if not self.main_window.file_path:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или откройте проект")
            return

        data = {}
        Objects = []

        # Получаем данные из таблиц
        bars_data = self.dock_menu.barsTable.getTableData()
        concentrated_data = self.dock_menu.concentratedLoadsTable.getTableData()
        distributed_data = self.dock_menu.distributedLoadTable.getTableData()

        # Проверяем, что все данные заполнены
        if bars_data and concentrated_data and distributed_data:
            Objects.append(bars_data)
            Objects.append(concentrated_data)
            Objects.append(distributed_data)
            data["Objects"] = Objects

            print("Данные для сохранения:", data)
            print("Путь файла:", self.main_window.file_path)

            try:
                # Проверка и создание директории
                directory = os.path.dirname(self.main_window.file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)

                # Проверка прав доступа
                if directory and not os.access(directory, os.W_OK):
                    QMessageBox.critical(self, "Ошибка", f"Нет прав на запись в директорию: {directory}")
                    return

                with open(self.main_window.file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)


                print("Файл успешно сохранен!")

                self.main_window.statusLabel.setText("Проект сохранен")
                QMessageBox.information(self, "Успех", f"Файл сохранен:\n{self.main_window.file_path}")

            except PermissionError:
                QMessageBox.critical(self, "Ошибка",
                                    f"Нет прав доступа к файлу.\n"
                                    f"Возможно файл открыт в другой программе.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                    f"Ошибка сохранения:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не все данные заполнены корректно!")

    def close_application(self):
        reply = QMessageBox.question(self, "Выход",
                                     "Вы уверены, что хотите выйти?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_window.close()
