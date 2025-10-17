import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QWidget
from PyQt5.QtGui import QIcon
from Preprocessor import PreprocessorTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.statusLabel = QLabel("Проект сохранен")
        self.statusBar().addWidget(self.statusLabel)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"SAPR")
        self.setGeometry(350, 200, 1280, 720)
        self.setWindowIcon(QIcon("icons/MainIcon.png"))

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
        self.statusBar().showMessage("Новый проект создан", msecs=3000)

    def handle_open_project(self):
        """Обработка открытия существующего проекта"""
        self.statusBar().showMessage("Проект загружен", msecs=3000)

    def setup_processor(self):
        pass

    def setup_postprocessor(self):
        pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
