import numpy as np


class BarSystemCalculator:
    def __init__(self, data):
        self.data = data
        self.results = {}

    def calculate_all(self):
        """Выполнить все расчеты"""
        try:
            self.calculate_stiffness_matrix()
            self.calculate_nodal_displacements()
            self.calculate_bar_forces()
            self.calculate_bar_stresses()
            self.calculate_reactions()
            return True
        except Exception as e:
            print(f"Ошибка расчетов: {e}")
            return False

    def calculate_stiffness_matrix(self):
        """Расчет матрицы жесткости системы"""
        bars_data = self.data["Objects"][0]["list_of_values"]
        n_nodes = len(bars_data) + 1

        # Инициализация глобальной матрицы жестности
        K_global = np.zeros((n_nodes, n_nodes))

        for bar in bars_data:
            bar_num = bar["barNumber"] - 1
            L = bar["length"]
            A = bar["cross_section"]
            E = bar["modulus_of_elasticity"]

            # Жесткость стержня
            k = (E * A) / L

            # Локальная матрица жестности для стержня
            k_local = np.array([[k, -k], [-k, k]])

            # Добавление в глобальную матрицу
            i = bar_num
            j = bar_num + 1

            K_global[i, i] += k_local[0, 0]
            K_global[i, j] += k_local[0, 1]
            K_global[j, i] += k_local[1, 0]
            K_global[j, j] += k_local[1, 1]

        self.results['stiffness_matrix'] = K_global.tolist()
        return K_global

    def calculate_nodal_displacements(self):
        """Расчет перемещений узлов"""
        K = np.array(self.results['stiffness_matrix'])
        n_nodes = K.shape[0]

        # Вектор нагрузок
        F = np.zeros(n_nodes)

        # Сосредоточенные нагрузки
        node_loads = self.data["Objects"][1]["list_of_values"]
        for load in node_loads:
            node_idx = load["node_number"] - 1
            if node_idx < n_nodes:
                F[node_idx] += load["force_value"]

        # Учет распределенных нагрузок
        distributed_loads = self.data["Objects"][2]["list_of_values"]
        bars_data = self.data["Objects"][0]["list_of_values"]

        for dist_load in distributed_loads:
            bar_idx = dist_load["bar_number"] - 1
            if bar_idx < len(bars_data):
                bar = bars_data[bar_idx]
                L = bar["length"]
                q = dist_load["distributed_value"]

                # Эквивалентные узловые силы от распределенной нагрузки
                F_eq = q * L / 2
                F[bar_idx] += F_eq
                F[bar_idx + 1] += F_eq

        # Учет закреплений
        K_modified = K.copy()
        F_modified = F.copy()

        # Левая заделка
        if self.data["Left_support"] == 1:
            K_modified[0, :] = 0
            K_modified[:, 0] = 0
            K_modified[0, 0] = 1
            F_modified[0] = 0

        # Правая заделка
        if self.data["Right_support"] == 1:
            last_node = n_nodes - 1
            K_modified[last_node, :] = 0
            K_modified[:, last_node] = 0
            K_modified[last_node, last_node] = 1
            F_modified[last_node] = 0

        # Решение системы уравнений
        try:
            displacements = np.linalg.solve(K_modified, F_modified)
            self.results['nodal_displacements'] = displacements.tolist()
        except np.linalg.LinAlgError:
            # Если матрица вырождена, используем псевдообратную
            displacements = np.linalg.pinv(K_modified) @ F_modified
            self.results['nodal_displacements'] = displacements.tolist()

        return displacements

    def calculate_bar_forces(self):
        """Расчет продольных усилий в стержнях"""
        bars_data = self.data["Objects"][0]["list_of_values"]
        displacements = np.array(self.results['nodal_displacements'])

        bar_forces = []

        for bar in bars_data:
            bar_num = bar["barNumber"]
            L = bar["length"]
            A = bar["cross_section"]
            E = bar["modulus_of_elasticity"]

            i = bar_num - 1
            j = bar_num

            # Относительное перемещение
            delta_u = displacements[j] - displacements[i]

            # Находим распределенную нагрузку для этого стержня
            q = 0
            distributed_loads = self.data["Objects"][2]["list_of_values"]
            for dist_load in distributed_loads:
                if dist_load["bar_number"] == bar_num:
                    q = dist_load["distributed_value"]
                    break

            # Продольное усилие в начале стержня (x = 0)
            # Nx(0) = EA/L * Δu + qL/2
            Nx_start = (E * A / L) * delta_u + q * L / 2

            # Продольное усилие в конце стержня (x = L)
            # Nx(L) = EA/L * Δu - qL/2
            Nx_end = (E * A / L) * delta_u - q * L / 2

            # Для таблицы усилий по стержням берем среднее значение или значение в начале
            bar_forces.append(float(Nx_start))

        self.results['bar_forces'] = bar_forces
        return bar_forces

    def calculate_bar_stresses(self):
        """Расчет напряжений в стержнях"""
        bars_data = self.data["Objects"][0]["list_of_values"]
        bar_forces = self.results['bar_forces']

        bar_stresses = []

        for i, bar in enumerate(bars_data):
            A = bar["cross_section"]
            Nx = bar_forces[i]

            # Напряжение σ = Nx / A
            if A != 0:
                sigma = Nx / A
            else:
                sigma = 0

            bar_stresses.append(float(sigma))

        self.results['bar_stresses'] = bar_stresses
        return bar_stresses

    def calculate_reactions(self):
        """Расчет реакций в опорах"""
        K = np.array(self.results['stiffness_matrix'])
        displacements = np.array(self.results['nodal_displacements'])

        # Реакции R = K * U
        reactions_full = K @ displacements
        reactions = reactions_full.tolist()

        # Корректировка реакций в заделках
        n_nodes = len(displacements)

        if self.data["Left_support"] == 1:
            reactions[0] = -reactions_full[0]

        if self.data["Right_support"] == 1:
            reactions[n_nodes - 1] = -reactions_full[n_nodes - 1]

        self.results['reactions'] = reactions
        return reactions

    def calculate_distributed_parameters(self, bar_number, discretization_step=0.1):
        """Расчет распределенных параметров по длине стержня"""
        bars_data = self.data["Objects"][0]["list_of_values"]
        displacements = np.array(self.results['nodal_displacements'])

        if bar_number < 1 or bar_number > len(bars_data):
            return []

        bar = bars_data[bar_number - 1]
        L = bar["length"]
        A = bar["cross_section"]
        E = bar["modulus_of_elasticity"]

        i = bar_number - 1
        j = bar_number

        # Перемещения на концах стержня
        u_i = displacements[i]
        u_j = displacements[j]

        # Находим распределенную нагрузку для этого стержня
        q = 0
        distributed_loads = self.data["Objects"][2]["list_of_values"]
        for dist_load in distributed_loads:
            if dist_load["bar_number"] == bar_number:
                q = dist_load["distributed_value"]
                break

        # Расчет в дискретных точках
        points = np.arange(0, L + discretization_step, discretization_step)
        results = []

        for x in points:
            if x > L:
                x = L

            # ПРАВИЛЬНАЯ ФОРМУЛА ПЕРЕМЕЩЕНИЙ ИЗ МЕТОДИЧКИ
            # u_p(x) = U_{p,0} + (x/L_p)*(U_{p,L} - U_{p,0}) + (q_p * L_p²)/(2 * E_p * A_p) * (x/L_p) * (1 - x/L_p)
            xi = x / L  # безразмерная координата

            # Основная часть от узловых перемещений
            u_linear = u_i + (u_j - u_i) * xi

            # Дополнительная часть от распределенной нагрузки
            if E * A != 0:
                u_distributed = (q * L ** 2) / (2 * E * A) * xi * (1 - xi)
            else:
                u_distributed = 0

            u_x = u_linear + u_distributed

            # Продольная сила (у вас уже правильная)
            Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x)

            # Напряжение
            if A != 0:
                sigma = Nx / A
            else:
                sigma = 0

            results.append({
                'x': float(x),
                'displacement': float(u_x),
                'Nx': float(Nx),
                'stress': float(sigma)
            })

            if x >= L:
                break

        return results

    def get_all_results(self):
        """Получить все результаты расчетов"""
        return {
            'stiffness_matrix': self.results.get('stiffness_matrix', []),
            'nodal_displacements': self.results.get('nodal_displacements', []),
            'bar_forces': self.results.get('bar_forces', []),
            'bar_stresses': self.results.get('bar_stresses', []),
            'reactions': self.results.get('reactions', [])
        }

    def calculate_force_at_point(self, bar_number, x):
        """Расчет продольной силы в конкретной точке стержня"""
        bars_data = self.data["Objects"][0]["list_of_values"]
        displacements = np.array(self.results['nodal_displacements'])

        if bar_number < 1 or bar_number > len(bars_data):
            return 0

        bar = bars_data[bar_number - 1]
        L = bar["length"]
        A = bar["cross_section"]
        E = bar["modulus_of_elasticity"]

        i = bar_number - 1
        j = bar_number

        # Относительное перемещение
        delta_u = displacements[j] - displacements[i]

        # Находим распределенную нагрузку
        q = 0
        distributed_loads = self.data["Objects"][2]["list_of_values"]
        for dist_load in distributed_loads:
            if dist_load["bar_number"] == bar_number:
                q = dist_load["distributed_value"]
                break

        # Продольная сила в точке x
        Nx = (E * A / L) * delta_u + q * (L / 2 - x)

        return float(Nx)


