from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsLineItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QToolBar, QAction, QGraphicsRectItem,
                             QGraphicsItemGroup, QGraphicsItem, QGraphicsPixmapItem, QGridLayout)
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPixmap, QMouseEvent


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
    def __init__(self, x1, x2, y, length):
        super().__init__()
        self.line = QGraphicsLineItem(3, 0, x2 - 3, 0)

        self.length = length
        if str(self.length)[-2:] == ".0":
            self.length = int(str(self.length)[:-2])
        self.text_item = QGraphicsTextItem(str(self.length))

        self.left_arrow_top = QGraphicsLineItem(2, 0, 8, -4)
        self.left_arrow_bottom = QGraphicsLineItem(2, 0, 8, 4)
        self.right_arrow_top = QGraphicsLineItem(x2 - 2, 0, x2 - 8, -4)
        self.right_arrow_bottom = QGraphicsLineItem(x2 - 2, 0, x2 - 8, 4)

        self.addToGroup(self.line)
        self.addToGroup(self.left_arrow_top)
        self.addToGroup(self.left_arrow_bottom)
        self.addToGroup(self.right_arrow_top)
        self.addToGroup(self.right_arrow_bottom)

        if float(length) < 1:
            if len(str(self.length)) == 1:
                self.addToGroup(self.text_item)
                self.text_item.setPos(x2 / 2 - 8, -20)
            if len(str(self.length)) == 2:
                self.addToGroup(self.text_item)
                self.text_item.setPos(x2 / 2 - 10, -20)
            if len(str(self.length)) == 3:
                self.addToGroup(self.text_item)
                self.text_item.setPos(x2 / 2 - 13, -20)
            if len(str(self.length)) == 4:
                self.addToGroup(self.text_item)
                self.text_item.setPos(x2 / 2 - 16, -20)
            if len(str(self.length)) == 5:
                self.addToGroup(self.text_item)
                self.text_item.setPos(x2 / 2 - 19, -20)
        else:
            x_ = (len(str(self.length)) - 1) * 3 + 8
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - x_, -20)

        self.setPos(x1, y - 2)


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
    def __init__(self, x, y, is_left_support=True, height=60):
        super().__init__()

        self.x = x
        self.y = y
        self.height = height
        self.is_left_support = is_left_support
        self.support_width = self.height/10

        self.create_support()
        self.setPos(x, y)

    def create_support(self):
        """Создает графическое представление заделки"""

        # Основная вертикальная полоса (стенка)
        main_line = QGraphicsLineItem(0, -self.height / 2, 0, self.height / 2)
        main_line.setPen(QPen(Qt.black, 3))
        self.addToGroup(main_line)

        # Штрихи (треугольники или линии)
        self.create_hatching()


    def create_hatching(self):
        """Создает штриховку в зависимости от типа заделки"""
        hatch_spacing = self.height // 6
        num_hatches = int(self.height // hatch_spacing)
        y_ = self.height/9


        for i in range(num_hatches):
            y_pos = i * hatch_spacing
            if self.is_left_support:
                # Штрихи справа от основной линии
                hatch = QGraphicsLineItem(-self.support_width, -self.height/2 + y_pos + y_, 0, -self.height/2 + y_pos)
            else:
                # Штрихи слева от основной линии
                hatch = QGraphicsLineItem(0, -self.height/2 + y_pos + y_, self.support_width, -self.height/2 + y_pos)

            hatch.setPen(QPen(Qt.black, 2))
            self.addToGroup(hatch)




class GridItem(QGraphicsItem):
    def __init__(self, grid_size=20):
        super().__init__()
        self.grid_size = grid_size
        self.setFlag(QGraphicsItem.ItemDoesntPropagateOpacityToChildren)

    def boundingRect(self):
        return QRectF(-10000, -10000, 20000, 20000)

    def paint(self, painter, option, widget):

        pen = QPen(QColor("#f5f3f0"))
        pen.setWidth(0)
        painter.setPen(pen)

        left = -10000
        top = -10000
        right = 10000
        bottom = 10000

        x = left
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += self.grid_size

        y = top
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += self.grid_size


class NodeLoad(QGraphicsItemGroup):
    def __init__(self, x, y, force_value):
        super().__init__()
        if str(force_value)[-2:] == ".0":
            force_value = int(str(force_value)[:-2])

        x_main1 = 0
        x_main2 = 20
        x_top1 = 16
        x_top2 = 20
        y_top1 = -3
        y_top2 = 3
        x_text = 0

        if force_value < 0:
            x_main1 = -20
            x_main2 = 0
            x_top1 = -16
            x_top2 = -20
            y_top1 = -3
            y_top2 = 3
            x_text = -25
        value = force_value
        if len(str(value)) > 4:
            value = "{:.1e}".format(value)

        self.text_item = QGraphicsTextItem(f"{value}")
        font = self.text_item.font()
        font.setPointSize(6)  # Размер в пунктах
        self.text_item.setFont(font)


        main_lime = QGraphicsLineItem(x_main1, 0, x_main2, 0)
        arrow_top_line = QGraphicsLineItem(x_top1, y_top1, x_top2, 0)
        arrow_bot_line = QGraphicsLineItem(x_top1, y_top2, x_top2, 0)
        main_lime.setPen(QPen(QColor("#C05"), 2))
        arrow_top_line.setPen(QPen(QColor("#C05"), 2))
        arrow_bot_line.setPen(QPen(QColor("#C05"), 2))
        self.addToGroup(main_lime)
        self.addToGroup(arrow_top_line)
        self.addToGroup(arrow_bot_line)
        self.text_item.setDefaultTextColor(QColor("#C05"))
        self.addToGroup(self.text_item)
        x_ = 0
        if len(str(value)) > 3:
            x_ = (len(str(value)) - 1) * 2
        if force_value < 0:
            self.text_item.setPos(x_text - x_, -19)
        else:
            self.text_item.setPos(x_text, -19)



        self.setPos(x, y)


class DistributedLoad(QGraphicsItemGroup):
    def __init__(self, x1, x2, length, value):
        super().__init__()
        count_arrow = 4
        current_x = 0
        self.length = length
        if self.length > 15:
            self.length = 15
        if self.length < 1.2:
            self.length = 1.2
        spacing = 5
        self.value = value
        if str(self.value)[-2:] == ".0":
            self.value = int(str(self.value)[:-2])


        length_arrow = 15
        if self.length < 2:
            length_arrow = (self.length * 40) / 5.3
            spacing = (self.length * 40) / 16
            for i in range(count_arrow):

                main_arrow = QGraphicsLineItem(current_x, 0, current_x + length_arrow, 0)
                main_arrow.setPen(QPen(QColor("#245AC7"), 1))
                if self.value > 0:
                    top_arrow = QGraphicsLineItem(current_x + length_arrow - 4, -3, current_x + length_arrow, 0)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x + length_arrow - 4, 3, current_x + length_arrow, 0)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(bot_arrow)
                else:
                    top_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, -3)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, 3)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(bot_arrow)
                self.addToGroup(main_arrow)
                current_x += length_arrow + spacing
        else:
            while (current_x + length_arrow  < self.length * 40):
                main_arrow = QGraphicsLineItem(current_x, 0, current_x + length_arrow, 0)
                main_arrow.setPen(QPen(QColor("#245AC7"), 1))
                self.addToGroup(main_arrow)
                if self.value > 0:
                    top_arrow = QGraphicsLineItem(current_x + length_arrow - 4, -3, current_x + length_arrow, 0)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x + length_arrow - 4, 3, current_x + length_arrow, 0)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(bot_arrow)
                else:
                    top_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, -3)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, 3)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 1))
                    self.addToGroup(bot_arrow)
                current_x += length_arrow + spacing
        if len(str(self.value)) > 4:
            self.value = "{:.2e}".format(self.value)
        self.text_item = QGraphicsTextItem(f"{self.value}")
        font = self.text_item.font()
        font.setPointSize(6)  # Размер в пунктах
        self.text_item.setFont(font)
        self.setPos(x1, 0)
        x_ = 5
        if len(str(self.value)) != 1:
            x_ = (len(str(self.value)) - 1) * 3
        self.text_item.setDefaultTextColor(QColor("#245AC7"))
        self.addToGroup(self.text_item)

        self.text_item.setPos(length * 40 / 2 - x_, 2)





class ConstructionGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setup_view()
        self.x_ = None

    def setup_view(self):
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event):
        """Масштабирование колесом мыши"""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.resetTransform()
            self.centerOn(self.x_, 0)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake_event = QMouseEvent(
                event.type(), event.localPos(), event.screenPos(),
                Qt.LeftButton, Qt.LeftButton, event.modifiers()
            )
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)



class ConstructionGraphicsManager:
    def __init__(self):
        self.scene = QGraphicsScene()
        self.view = ConstructionGraphicsView(self.scene)
        self.setup_graphics()

    def setup_graphics(self):
        # Настройка сцены
        self.scene.setBackgroundBrush(QBrush(QColor(250, 250, 250)))

        # Рисуем сетку
        self.draw_grid()

    def draw_grid(self, spacing=10):
        grid = GridItem(10)
        self.scene.addItem(grid)
        # """Отрисовка сетки"""
        # pen = QPen(QColor(220, 220, 220), 1)
        #
        # # Вертикальные линии
        # for x in range(-1000, 1001, spacing):
        #     self.scene.addLine(x, -1000, x, 1000, pen)
        #
        # # Горизонтальные линии
        # for y in range(-1000, 1001, spacing):
        #     self.scene.addLine(-1000, y, 1000, y, pen)

    def draw_construction(self, data):
        """Отрисовка стержней и сил"""
        self.clear_construction()
        self.draw_loads(data)
        self.draw_bar(data)


    def draw_bar(self, data):
        """Отрисовка стержней"""
        #self.draw_grid()
        x_spacing = 40
        y_spacing = 40
        current_x = 0
        first_bar = True
        if not data:
            self.clear_construction()
            return
        max_cross_section = 0
        for list_of_values in data["Objects"][0]["list_of_values"]:
            if max_cross_section < list_of_values["cross_section"]:
                max_cross_section = list_of_values["cross_section"]
        if max_cross_section > 10:
            max_cross_section = 10


        for list_of_values in data["Objects"][0]["list_of_values"]:
            length_bar = list_of_values["length"]
            if length_bar > 15:
                length_bar = 15
            if length_bar < 1.2:
                length_bar = 1.2

            cross_section = list_of_values["cross_section"]
            if cross_section > 10:
                cross_section = 10
            if cross_section < 0.2:
                cross_section = 0.2
            bar_item = BarGraphicsItem(current_x * x_spacing, -cross_section/2 * y_spacing, length_bar * x_spacing, cross_section * y_spacing, list_of_values["barNumber"])
            self.scene.addItem(bar_item)

            bar_number = BarNumber(current_x * x_spacing + (length_bar * x_spacing)/2, cross_section/2 * y_spacing + 15, int(list_of_values["barNumber"]))
            self.scene.addItem(bar_number)

            LengthBarLine = LengthBarGraphicsItem(current_x * x_spacing, length_bar * x_spacing, (max_cross_section / 2 * y_spacing) + 60, list_of_values["length"])
            self.scene.addItem(LengthBarLine)
            if first_bar:
                left_line = QGraphicsLineItem(0, cross_section/2 * y_spacing ,0 , (max_cross_section/2 * y_spacing) + 60)
                right_line = QGraphicsLineItem(current_x * x_spacing + length_bar * x_spacing, cross_section / 2 * y_spacing, current_x * x_spacing + length_bar * x_spacing,
                                              (max_cross_section / 2 * y_spacing) + 60)
                self.scene.addItem(left_line)
                self.scene.addItem(right_line)

                left_node_item = NodeGraphicsItem(0, (max_cross_section/2 * y_spacing) + 30, 1)
                right_node_item = NodeGraphicsItem(current_x * x_spacing + length_bar * x_spacing, (max_cross_section / 2 * y_spacing) + 30, 2)
                self.scene.addItem(left_node_item)
                self.scene.addItem(right_node_item)
            else:
                line = QGraphicsLineItem(current_x * x_spacing + length_bar * x_spacing,
                                               cross_section / 2 * y_spacing,
                                               current_x * x_spacing + length_bar * x_spacing,
                                               (max_cross_section / 2 * y_spacing) + 60)
                self.scene.addItem(line)
                node_item = NodeGraphicsItem(current_x * x_spacing + length_bar * x_spacing,
                                             (max_cross_section / 2 * y_spacing) + 30, list_of_values["barNumber"]+1)
                self.scene.addItem(node_item)
            current_x += length_bar
            first_bar = False

        is_left_support = data["Left_support"]
        is_right_support = data["Right_support"]
        length_construction = 0
        for list_of_values in data["Objects"][0]["list_of_values"]:
            length_construction += list_of_values["length"]
        if is_left_support:
            left_support = SupportGraphicsItem(0, 0, True, max_cross_section * y_spacing + 20)
            self.scene.addItem(left_support)
        if is_right_support:
            length_construction = 0
            for list_of_values in data["Objects"][0]["list_of_values"]:
                if list_of_values["length"] > 15:
                    length_construction += 15
                elif list_of_values["length"] < 1.2:
                    length_construction += 1.2
                else:
                    length_construction += list_of_values["length"]
            right_support = SupportGraphicsItem(length_construction * x_spacing, 0, False, max_cross_section * y_spacing + 20)
            self.scene.addItem(right_support)

        self.center_on_constucrion((length_construction * x_spacing)/2)
        self.view.x_ = (length_construction * x_spacing)/2



        # # Подпись стержня
        # text_item = QGraphicsTextItem(f"Стержень {bar_index + 1}")
        # text_item.setPos((x1 + x2) / 2 - 20, y - 20)
        # text_item.setDefaultTextColor(Qt.darkBlue)
        # self.scene.addItem(text_item)

    def center_on_constucrion(self, x):
        self.view.centerOn(x, 0)

    def draw_loads(self, data):
        """Отрисовка нагрузок"""
        x_spacing = 40
        y_spacing = 40

        max_node = data["Objects"][0]["quantity"] + 1

        for distributed_load in data["Objects"][2]["list_of_values"]:
            current_x = 0
            for bar in data["Objects"][0]["list_of_values"]:
                length = bar["length"]
                if length > 15:
                    length = 15
                if length < 1.2:
                    length = 1.2
                if distributed_load["bar_number"] == bar["barNumber"]:
                    distrload = DistributedLoad(current_x, current_x + length * 40, length, distributed_load["distributed_value"])
                    self.scene.addItem(distrload)

                current_x += length * 40


        for node_load in data["Objects"][1]["list_of_values"]:
            node_number = node_load["node_number"]
            x_ = 0
            for bar in data["Objects"][0]["list_of_values"]:
                if bar["barNumber"] < node_number:
                    if bar["length"] > 15:
                        x_ += 15 * x_spacing
                    elif bar["length"] < 1.2:
                        x_ += 1.2 * x_spacing
                    else:
                        x_ += bar["length"] * x_spacing
            if not ((node_number == 1  and data["Left_support"] == 1) or (node_number == max_node and data["Right_support"] == 1)):
                load = NodeLoad(x_, 0, node_load["force_value"])
                self.scene.addItem(load)





    def clear_construction(self):
        """Очистка сцены"""
        self.scene.clear()
        #self.draw_grid()  # Перерисовываем сетку