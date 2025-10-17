from PyQt5.QtWidgets import (QFileDialog, QMessageBox)
import os


class FileManager(QFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.file_path = None

    def create_new_project(self):
        """Обработчик создания нового проекта"""
        # Получаем путь для сохранения файла
        self.file_path, _ = self.getSaveFileName(
            self,
            "Создать новый проект SAPR",
            f"{os.getcwd()}/projects",
            "SAPR Projects (*.json);"
        )

        if self.file_path:  # Если пользователь выбрал путь (не нажал Cancel)
            # Добавляем расширение, если его нет
            if not self.file_path.endswith('.json'):
                self.file_path += '.json'

            return self.file_path
        else:
            return None

    def open_existing_project(self):
        """Обработчик открытия существующего проекта"""
        self.file_path, _ = self.getOpenFileName(
            self,
            "Открыть проект SAPR",
            f"{os.getcwd()}/projects",
            "JSON Files (*.json)"
        )

        if self.file_path:  # Если пользователь выбрал файл
            # Простая проверка существования файла
            if os.path.exists(self.file_path):
                return self.file_path
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не существует")
        else:
            return None