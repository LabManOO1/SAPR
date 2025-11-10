import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from Preprocessor import PreprocessorTab
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"SAPR")
        self.setGeometry(350, 200, 1280, 720)
        self.setWindowIcon(QIcon("icons/MainIcon.png"))
        self.starus_bar_label = QLabel("")
        self.statusBar().addPermanentWidget(self.starus_bar_label)

        # СОЗДАЕМ ВИДЖЕТ ВКЛАДОК
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)  # Устанавливаем вкладки как центральный виджет

        # СОЗДАЕМ СОДЕРЖИМОЕ ДЛЯ КАЖДОЙ ВКЛАДКИ
        # Вкладка 1 - Препроцессор
        self.preprocessor_tab = PreprocessorTab(self, self.file_path)  # Передаем self (главное окно)
        self.tabs.addTab(self.preprocessor_tab, "Препроцессор")

        # Вкладка 2 - Процессор
        self.processor_tab = QWidget()
        self.setup_processor()
        self.tabs.addTab(self.processor_tab, "Процессор")

        # Вкладка 3 - Постпроцессор
        self.postprocessor_tab = QWidget()
        self.setup_postprocessor()
        self.tabs.addTab(self.postprocessor_tab, "Постпроцессор")

    def handle_new_project(self):
        """Обработка создания нового проекта"""
        self.statusBar().showMessage("Новый проект создан", 3000)

    def handle_open_project(self):
        """Обработка открытия существующего проекта"""
        self.statusBar().showMessage("Проект загружен", 3000)

    def set_project_saved_status(self, saved=True):
        """Установить статус сохраненности проекта"""
        if saved:
            self.statusBar().showMessage("Проект сохранен")
        else:
            self.statusBar().showMessage("Проект не сохранен")

    def set_window_title_with_file(self):
        """Установить заголовок окна с именем файла"""
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            self.setWindowTitle(f"SAPR - {file_name}")
        else:
            self.setWindowTitle("SAPR - Новый проект")

    def setup_processor(self):
        pass

    def setup_postprocessor(self):
        pass

    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        reply = QMessageBox.question(
            self,
            'Подтверждение выхода',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()  # Закрыть приложение
        else:
            event.ignore()  # Отменить закрытие

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
