from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsLineItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QToolBar, QAction, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsItem, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPixmap


class BarGraphicsItem(QGraphicsRectItem):
    def __init__(self, x1, y1, x2, y2, bar_number):
        super().__init__(x1, y1, x2, y2)
        self.bar_number = bar_number
        self.setup_appearance()

    def setup_appearance(self):
        self.setPen(QPen(Qt.black, 3))  # Steel blue


class NodeGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x, y, node_number, is_support=False):
        super().__init__()
        self.node_number = node_number
        self.is_support = is_support

        # Создаем элементы и добавляем в группу
        self.rect_item = QGraphicsRectItem(-8, -8, 16, 16)
        self.text_item = QGraphicsTextItem(f"{node_number}")

        self.addToGroup(self.rect_item)
        self.addToGroup(self.text_item)

        # Позиционируем текст
        self.text_item.setPos(-7, -11)

        self.setPos(x, y)  # Устанавливаем позицию всей группы
        self.setup_appearance()

    def setup_appearance(self):
        self.rect_item.setPen(QPen(QColor("#245AC7"), 1))
        self.rect_item.setBrush(QBrush(QColor(255, 255, 255)))

        self.text_item.setDefaultTextColor(QColor("#245AC7"))

class LengthBarGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x1, x2,  y, length):
        super().__init__()
        self.line = QGraphicsLineItem(3, 0, x2 - 3, 0)
        self.text_item = QGraphicsTextItem(length)

        self.left_arrow_top = QGraphicsLineItem(2, 0, 8, -4)
        self.left_arrow_bottom = QGraphicsLineItem(2, 0, 8, 4)
        self.right_arrow_top = QGraphicsLineItem(x2-2, 0, x2 - 8, -4)
        self.right_arrow_bottom = QGraphicsLineItem(x2-2, 0, x2 - 8, 4)

        self.addToGroup(self.line)
        self.addToGroup(self.text_item)
        self.addToGroup(self.left_arrow_top)
        self.addToGroup(self.left_arrow_bottom)
        self.addToGroup(self.right_arrow_top)
        self.addToGroup(self.right_arrow_bottom)


        self.text_item.setPos(x2/2-8, -20)

        self.setPos(x1, y-2)

        #self.setup_appearance()


class BarNumber(QGraphicsItemGroup):
    def __init__(self, x, y, bar_number):
        super().__init__()
        self.circle = QGraphicsEllipseItem(-8, -8, 16, 16)
        self.text_item = QGraphicsTextItem(f"{bar_number}")
        self.addToGroup(self.circle)
        self.addToGroup(self.text_item)
        self.text_item.setPos(-7, -11)
        self.setPos(x, y)
        self.setup_appearance()

    def setup_appearance(self):
        self.circle.setPen(QPen(QColor("#C05"), 1))

        self.text_item.setDefaultTextColor(QColor("#C05"))


class SupportGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x, y, is_left_support=True, height=60, support_width=15):
        super().__init__()

        self.x = x
        self.y = y
        self.height = height
        self.is_left_support = is_left_support
        self.support_width = support_width

        self.create_support()
        self.setPos(x, y)

    def create_support(self):
        """Создает графическое представление заделки"""

        # Основная вертикальная полоса (стенка)
        main_line = QGraphicsLineItem(0, -self.height/2, 0, self.height/2)
        main_line.setPen(QPen(Qt.black, 3))
        self.addToGroup(main_line)

        # Штрихи (треугольники или линии)
        self.create_hatching()


    def create_hatching(self):
        """Создает штриховку в зависимости от типа заделки"""
        num_hatches = 6  # Количество штрихов
        hatch_spacing = self.height / (num_hatches)

        for i in range(num_hatches):
            y_pos = i * hatch_spacing
            if self.is_left_support:
                # Штрихи справа от основной линии
                hatch = QGraphicsLineItem(-self.support_width, -self.height/2 + y_pos + 15, 0, -self.height/2 + y_pos)
            else:
                # Штрихи слева от основной линии
                hatch = QGraphicsLineItem(0, -self.height/2 + y_pos + 15, self.support_width, -self.height/2 + y_pos)

            hatch.setPen(QPen(Qt.black, 2))
            self.addToGroup(hatch)


class ConstructionGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setup_view()

    def setup_view(self):
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        """Масштабирование колесом мыши"""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)


class ConstructionGraphicsManager:
    def __init__(self):
        self.scene = QGraphicsScene()
        self.view = ConstructionGraphicsView(self.scene)
        self.setup_graphics()

    def setup_graphics(self):
        # Настройка сцены
        self.scene.setSceneRect(-500, -500, 1000, 1000)
        self.scene.setBackgroundBrush(QBrush(QColor(250, 250, 250)))

        # Рисуем сетку
        #self.draw_grid()

    def draw_grid(self, spacing=10):
        """Отрисовка сетки"""
        pen = QPen(QColor(220, 220, 220), 1)

        # Вертикальные линии
        for x in range(-1000, 1001, spacing):
            self.scene.addLine(x, -1000, x, 1000, pen)

        # Горизонтальные линии
        for y in range(-1000, 1001, spacing):
            self.scene.addLine(-1000, y, 1000, y, pen)

    def draw_construction(self, data):
        """Отрисовка стержней и сил"""
        self.clear_construction()

        self.draw_bar(data)

    def draw_bar(self, data):
        """Отрисовка стержней"""
        x_spacing = 40
        y_spacing = 40
        current_x = 0
        first_bar = True
        max_cross_section = 0
        for list_of_values in data["Objects"][0]["list_of_values"]:
            if max_cross_section < int(list_of_values["cross_section"]):
                max_cross_section = int(list_of_values["cross_section"])


        for list_of_values in data["Objects"][0]["list_of_values"]:
            bar_item = BarGraphicsItem(current_x * x_spacing, -int(list_of_values["cross_section"])/2 * y_spacing, int(list_of_values["length"]) * x_spacing, int(list_of_values["cross_section"]) * y_spacing, list_of_values["barNumber"])
            self.scene.addItem(bar_item)

            bar_number = BarNumber(current_x * x_spacing + (int(list_of_values["length"]) * x_spacing)/2, int(list_of_values["cross_section"])/2 * y_spacing + 15, int(list_of_values["barNumber"]))
            self.scene.addItem(bar_number)

            LengthBarLine = LengthBarGraphicsItem(current_x * x_spacing, int(list_of_values["length"]) * x_spacing, (max_cross_section / 2 * y_spacing) + 60, list_of_values["length"])
            self.scene.addItem(LengthBarLine)
            if first_bar:
                left_line = QGraphicsLineItem(0, int(list_of_values["cross_section"])/2 * y_spacing ,0 , (max_cross_section/2 * y_spacing) + 60)
                right_line = QGraphicsLineItem(current_x * x_spacing + int(list_of_values["length"]) * x_spacing, int(list_of_values["cross_section"]) / 2 * y_spacing, current_x * x_spacing + int(list_of_values["length"]) * x_spacing,
                                              (max_cross_section / 2 * y_spacing) + 60)
                self.scene.addItem(left_line)
                self.scene.addItem(right_line)

                left_node_item = NodeGraphicsItem(0, (max_cross_section/2 * y_spacing) + 30, 1)
                right_node_item = NodeGraphicsItem(current_x * x_spacing + int(list_of_values["length"]) * x_spacing, (max_cross_section / 2 * y_spacing) + 30, 2)
                self.scene.addItem(left_node_item)
                self.scene.addItem(right_node_item)
            else:
                line = QGraphicsLineItem(current_x * x_spacing + int(list_of_values["length"]) * x_spacing,
                                               int(list_of_values["cross_section"]) / 2 * y_spacing,
                                               current_x * x_spacing + int(list_of_values["length"]) * x_spacing,
                                               (max_cross_section / 2 * y_spacing) + 60)
                self.scene.addItem(line)
                node_item = NodeGraphicsItem(current_x * x_spacing + int(list_of_values["length"]) * x_spacing,
                                             (max_cross_section / 2 * y_spacing) + 30, int(list_of_values["barNumber"])+1)
                self.scene.addItem(node_item)
            current_x += int(list_of_values["length"])
            first_bar = False

        is_left_support = data["Left_support"]
        is_right_support = data["Right_support"]
        length_construction = 0
        for list_of_values in data["Objects"][0]["list_of_values"]:
            length_construction += int(list_of_values["length"])
        if is_left_support:
            left_support = SupportGraphicsItem(0, 0, True, max_cross_section * y_spacing + 20)
            self.scene.addItem(left_support)
        if is_right_support:
            length_construction = 0
            for list_of_values in data["Objects"][0]["list_of_values"]:
                length_construction += int(list_of_values["length"])
            right_support = SupportGraphicsItem(length_construction * x_spacing, 0, False, max_cross_section * y_spacing + 20)
            self.scene.addItem(right_support)



        # # Подпись стержня
        # text_item = QGraphicsTextItem(f"Стержень {bar_index + 1}")
        # text_item.setPos((x1 + x2) / 2 - 20, y - 20)
        # text_item.setDefaultTextColor(Qt.darkBlue)
        # self.scene.addItem(text_item)

    def draw_nodes_and_supports(self, bars_count, supports_data):
        """Отрисовка узлов и заделок"""
        x_spacing = 100

        for i in range(bars_count + 1):
            x = i * x_spacing
            y = 0

            # Определяем тип узла (обычный или заделка)
            is_left_support = (i == 0 and supports_data.get('left_support', False))
            is_right_support = (i == bars_count and supports_data.get('right_support', False))
            is_support = is_left_support or is_right_support

            node_item = NodeGraphicsItem(x, y, i + 1, is_support)
            self.scene.addItem(node_item)

            # Подпись узла
            support_text = " (заделка)" if is_support else ""
            text_item = QGraphicsTextItem(f"Узел {i + 1}{support_text}")
            text_item.setPos(x - 15, y + 15)
            text_item.setDefaultTextColor(Qt.darkGreen)
            self.scene.addItem(text_item)

    def clear_construction(self):
        """Очистка сцены"""
        self.scene.clear()
        #self.draw_grid()  # Перерисовываем сетку