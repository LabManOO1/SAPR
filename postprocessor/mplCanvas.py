import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    """Виджет для отображения matplotlib графиков с инструментами навигации"""

    def __init__(self, parent=None, width=14, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_all_components(self, data, calculation_results, bar_number, show_u, show_n, show_sigma):
        """Построение графиков всех компонентов для выбранного стержня"""
        try:
            self.fig.clear()

            if not data or not calculation_results:
                return

            bars_data = data["Objects"][0]["list_of_values"]
            displacements = calculation_results.get('nodal_displacements', [])

            if displacements is None or len(displacements) == 0:
                return

            # Находим выбранный стержень
            selected_bar = None
            for bar in bars_data:
                if bar['barNumber'] == bar_number:
                    selected_bar = bar
                    break

            if not selected_bar:
                return

            # Создаем основной график
            ax = self.fig.add_subplot(111)

            # Вычисляем все три компонента
            x_coords, u_values = self.calculate_function_values(
                selected_bar, displacements, bar_number, "displacement", calculation_results
            )
            _, n_values = self.calculate_function_values(
                selected_bar, displacements, bar_number, "force", calculation_results
            )
            _, sigma_values = self.calculate_function_values(
                selected_bar, displacements, bar_number, "stress", calculation_results
            )

            if x_coords.size == 0:
                return

            lines = []
            labels = []

            # График перемещений
            if show_u:
                line_u = ax.plot(x_coords, u_values, 'b-', linewidth=2, label='u(x)')[0]
                lines.append(line_u)
                labels.append('u(x)')

            # График продольных сил
            if show_n:
                line_n = ax.plot(x_coords, n_values, 'r-', linewidth=2, label='N(x)')[0]
                lines.append(line_n)
                labels.append('N(x)')

            # График напряжений
            if show_sigma:
                line_sigma = ax.plot(x_coords, sigma_values, 'g-', linewidth=2, label='σ(x)')[0]
                lines.append(line_sigma)
                labels.append('σ(x)')

            # Настройки графика
            ax.set_xlabel('Локальная координата x, м')
            ax.set_ylabel('Значения')

            title = f'Компоненты НДС для стержня {bar_number}'
            if not (show_u and show_n and show_sigma):
                shown = []
                if show_u: shown.append("перемещения")
                if show_n: shown.append("силы")
                if show_sigma: shown.append("напряжения")
                title += f' ({", ".join(shown)})'
            ax.set_title(title)

            ax.grid(True, alpha=0.3)

            # Легенда только если есть линии
            if lines:
                ax.legend(lines, labels, loc='upper right', fontsize=9, framealpha=0.7)

            # Добавляем вертикальные линии для границ стержня
            ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)
            ax.axvline(x=selected_bar['length'], color='black', linestyle='--', alpha=0.5)

            # Автоматически настраиваем масштаб
            self.adjust_scale(ax, show_u, show_n, show_sigma, u_values, n_values, sigma_values)

            self.fig.tight_layout()
            self.draw()

        except Exception:
            # Тихая обработка ошибок
            pass

    def adjust_scale(self, ax, show_u, show_n, show_sigma, u_values, n_values, sigma_values):
        """Настраивает масштаб для отображения всех выбранных графиков"""
        try:
            # Собираем все выбранные значения
            all_values = []
            if show_u:
                all_values.extend(u_values)
            if show_n:
                all_values.extend(n_values)
            if show_sigma:
                all_values.extend(sigma_values)

            if not all_values:
                return

            y_min = np.min(all_values)
            y_max = np.max(all_values)
            y_range = y_max - y_min

            if y_range == 0:
                y_range = 1

            margin = y_range * 0.1
            ax.set_ylim(y_min - margin, y_max + margin)

        except Exception:
            pass

    def calculate_function_values(self, bar, displacements, bar_number, func_type, calculation_results):
        """Вычисляет значения функции для одного стержня"""
        try:
            L = bar['length']
            A = bar['cross_section']
            E = bar['modulus_of_elasticity']

            if bar_number < 1 or bar_number >= len(displacements):
                return np.array([]), np.array([])

            u_i = displacements[bar_number - 1]
            u_j = displacements[bar_number]

            # Находим распределенную нагрузку
            q = 0
            if calculation_results and 'distributed_loads' in calculation_results:
                for load in calculation_results['distributed_loads']:
                    if load['bar_number'] == bar_number:
                        q = load['distributed_value']
                        break

            num_points = 100
            x_coords = np.linspace(0, L, num_points)
            values = np.zeros(num_points)

            for idx, x in enumerate(x_coords):
                try:
                    if func_type == "displacement":
                        u_linear = u_i + (u_j - u_i) * (x / L)
                        if E * A != 0 and q != 0:
                            u_distributed = (q * x * (L - x)) / (2 * E * A)
                        else:
                            u_distributed = 0
                        values[idx] = u_linear + u_distributed

                    elif func_type == "force":
                        Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x)
                        values[idx] = Nx

                    elif func_type == "stress":
                        Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x)
                        sigma = Nx / A if A != 0 else 0
                        values[idx] = sigma

                except (ZeroDivisionError, OverflowError):
                    values[idx] = 0.0

            return x_coords, values

        except Exception:
            return np.array([]), np.array([])