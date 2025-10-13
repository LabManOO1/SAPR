from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt
from fileManager import FileManager


class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.file_path = None

    def setup_ui(self):
        # Настройки окна
        self.setWindowTitle("SAPR - Начало работы")
        self.setFixedSize(400, 300)
        self.setModal(True)  # ★ Ключевой параметр - модальное окно

        # Убираем стандартные кнопки окна
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        # Главный layout

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel("Добро пожаловать в SAPR")
        title_label.setAlignment(Qt.AlignCenter)

        # Описание
        desc_label = QLabel("Выберите действие для начала работы:")
        desc_label.setAlignment(Qt.AlignCenter)
        #desc_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        #separator.setStyleSheet("background-color: #bdc3c7;")

        # Layout для кнопок
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)

        # Кнопка "Создать файл"
        self.create_btn = QPushButton("Создать новый проект")
        self.create_btn.setMinimumHeight(50)
        self.create_btn.clicked.connect(self.create_new_project)

        # Кнопка "Открыть файл"
        self.open_btn = QPushButton("Открыть существующий проект")
        self.open_btn.setMinimumHeight(50)
        self.open_btn.clicked.connect(self.open_existing_project)

        # Кнопка "Выход"
        self.exit_btn = QPushButton("Выход")
        self.exit_btn.setMinimumHeight(40)
        self.exit_btn.clicked.connect(self.reject)

        # Собираем layout
        buttons_layout.addWidget(self.create_btn)
        buttons_layout.addWidget(self.open_btn)
        # buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.exit_btn)

        # Добавляем все в главный layout
        self.layout.addWidget(title_label)
        self.layout.addWidget(desc_label)
        self.layout.addStretch(1)
        self.layout.addWidget(separator)
        self.layout.addLayout(buttons_layout)

    def create_new_project(self):
        file_manager = FileManager(self)
        file_manager.create_new_project()
        self.file_path = file_manager.file_path
        self.done(1)

    def open_existing_project(self):
        file_manager = FileManager(self)
        file_manager.open_existing_project()
        self.file_path = file_manager.file_path
        self.done(2)
