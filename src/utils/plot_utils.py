import customtkinter as ctk
import pandas as pd


class SimpleChart(ctk.CTkFrame):
    def __init__(self, master, title="", height=200, **kwargs):
        super().__init__(master, height=height, **kwargs)

        self.title = title
        self.canvas_height = height - 40  # Оставляем место для заголовка
        self.canvas_width = 600

        # Заголовок
        self.title_label = ctk.CTkLabel(self, text=title, font=("Arial", 14, "bold"))
        self.title_label.pack(pady=5)

        # Canvas для рисования
        self.canvas = ctk.CTkCanvas(
            self, width=self.canvas_width, height=self.canvas_height, bg="white"
        )
        self.canvas.pack(pady=5)

    def clear(self):
        """Очистка холста"""
        self.canvas.delete("all")


def create_payments_chart(parent, project) -> SimpleChart:
    """Создание графика платежей"""
    chart = SimpleChart(parent, title="График платежей")

    # Получаем данные о платежах
    payments_data = []
    for payment in project.payments:
        if payment.status == "completed":
            payments_data.append(
                {"date": payment.payment_date, "amount": payment.amount}
            )

    if not payments_data:
        chart.canvas.create_text(
            chart.canvas_width // 2,
            chart.canvas_height // 2,
            text="Нет данных о платежах",
            fill="gray",
        )
        return chart

    # Создаем DataFrame и сортируем по дате
    df = pd.DataFrame(payments_data)
    df = df.sort_values("date")
    df["cumulative"] = df["amount"].cumsum()

    # Находим границы для масштабирования
    max_amount = df["cumulative"].max()
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = (max_date - min_date).days

    # Масштабирование и отрисовка
    padding = 20
    y_scale = (chart.canvas_height - 2 * padding) / max_amount
    x_scale = (chart.canvas_width - 2 * padding) / date_range

    # Рисуем оси
    chart.canvas.create_line(
        padding,
        chart.canvas_height - padding,
        chart.canvas_width - padding,
        chart.canvas_height - padding,
        fill="black",
    )
    chart.canvas.create_line(
        padding, padding, padding, chart.canvas_height - padding, fill="black"
    )

    # Рисуем график
    prev_x = prev_y = None
    for _, row in df.iterrows():
        x = padding + (row["date"] - min_date).days * x_scale
        y = chart.canvas_height - (padding + row["cumulative"] * y_scale)

        # Точка
        chart.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

        # Линия к предыдущей точке
        if prev_x is not None:
            chart.canvas.create_line(prev_x, prev_y, x, y, fill="blue")

        prev_x, prev_y = x, y

        # Подпись значения
        chart.canvas.create_text(
            x, y - 10, text=f"{row['cumulative']:,.0f}", font=("Arial", 8)
        )

    return chart


def create_modifications_chart(parent, project) -> SimpleChart:
    """Создание графика доработок"""
    chart = SimpleChart(parent, title="График доработок")

    # Получаем данные о доработках
    mods_data = []
    for mod in project.modifications:
        if mod.is_paid:
            mods_data.append(
                {
                    "date": mod.start_date,
                    "cost": mod.cost,
                    "description": mod.description[:20] + "..."
                    if len(mod.description) > 20
                    else mod.description,
                }
            )

    if not mods_data:
        chart.canvas.create_text(
            chart.canvas_width // 2,
            chart.canvas_height // 2,
            text="Нет данных о доработках",
            fill="gray",
        )
        return chart

    # Создаем DataFrame и сортируем по дате
    df = pd.DataFrame(mods_data)
    df = df.sort_values("date")
    df["cumulative"] = df["cost"].cumsum()

    # Находим границы для масштабирования
    max_amount = df["cumulative"].max()
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = (max_date - min_date).days or 1  # Избегаем деления на ноль

    # Масштабирование и отрисовка
    padding = 20
    y_scale = (chart.canvas_height - 2 * padding) / max_amount if max_amount > 0 else 1
    x_scale = (chart.canvas_width - 2 * padding) / date_range

    # Рисуем оси
    chart.canvas.create_line(
        padding,
        chart.canvas_height - padding,
        chart.canvas_width - padding,
        chart.canvas_height - padding,
        fill="black",
    )
    chart.canvas.create_line(
        padding, padding, padding, chart.canvas_height - padding, fill="black"
    )

    # Рисуем столбцы доработок и линию общей стоимости
    bar_width = min(30, x_scale * date_range / len(df) - 5)
    prev_x = prev_y = None

    for _, row in df.iterrows():
        x = padding + (row["date"] - min_date).days * x_scale
        y_cost = chart.canvas_height - (padding + row["cost"] * y_scale)
        y_cum = chart.canvas_height - (padding + row["cumulative"] * y_scale)

        # Столбец доработки
        chart.canvas.create_rectangle(
            x - bar_width / 2,
            chart.canvas_height - padding,
            x + bar_width / 2,
            y_cost,
            fill="lightblue",
            outline="blue",
        )

        # Точка на линии общей стоимости
        chart.canvas.create_oval(x - 3, y_cum - 3, x + 3, y_cum + 3, fill="red")

        # Линия общей стоимости
        if prev_x is not None:
            chart.canvas.create_line(prev_x, prev_y, x, y_cum, fill="red")

        prev_x, prev_y = x, y_cum

        # Подписи
        chart.canvas.create_text(
            x, y_cost - 10, text=f"{row['cost']:,.0f}", font=("Arial", 8)
        )

        # Описание доработки (повернуто)
        chart.canvas.create_text(
            x,
            chart.canvas_height - padding + 10,
            text=row["description"],
            angle=45,
            anchor="w",
            font=("Arial", 8),
        )

    return chart
