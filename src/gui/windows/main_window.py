import customtkinter as ctk
from typing import Optional
from src.db.models import init_db, Project
from src.db.crud import ProjectManager, PaymentManager, ModificationManager


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FreeLance Compass")
        self.geometry("1200x800")

        # Инициализация менеджеров
        self.session = init_db()
        self.project_manager = ProjectManager(self.session)
        self.payment_manager = PaymentManager(self.session)
        self.modification_manager = ModificationManager(self.session)

        self._setup_ui()
        self._load_projects()

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Верхняя панель с кнопками и поиском
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        # Кнопка создания проекта
        self.add_button = ctk.CTkButton(
            self.top_frame, text="Новый проект", command=self._show_project_form
        )
        self.add_button.pack(side="left", padx=5)

        # Поиск
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_search)
        self.search_entry = ctk.CTkEntry(
            self.top_frame,
            placeholder_text="Поиск проектов...",
            textvariable=self.search_var,
            width=200,
        )
        self.search_entry.pack(side="right", padx=5)

        # Фильтры статуса
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        statuses = ["Все", "Активные", "Завершенные", "Просроченные"]
        self.status_var = ctk.StringVar(value="Все")

        for status in statuses:
            ctk.CTkRadioButton(
                self.status_frame,
                text=status,
                variable=self.status_var,
                value=status,
                command=self._load_projects,
            ).pack(side="left", padx=10)

        # Список проектов
        self.projects_frame = ctk.CTkScrollableFrame(self)
        self.projects_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_projects(self):
        """Загрузка списка проектов"""
        # Очистка списка
        for widget in self.projects_frame.winfo_children():
            widget.destroy()

        # Получение проектов
        status_filter = self.status_var.get()
        if status_filter == "Все":
            projects = self.project_manager.get_all_projects()
        else:
            status_map = {
                "Активные": "active",
                "Завершенные": "completed",
                "Просроченные": "overdue",
            }
            projects = self.project_manager.get_all_projects(status_map[status_filter])

        # Отображение проектов
        for project in projects:
            self._create_project_card(project)

    def _create_project_card(self, project: Project):
        """Создание карточки проекта"""
        frame = ctk.CTkFrame(self.projects_frame)
        frame.pack(fill="x", padx=5, pady=5)

        # Основная информация
        header_frame = ctk.CTkFrame(frame)
        header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(header_frame, text=project.name, font=("Arial", 16, "bold")).pack(
            side="left"
        )

        status_label = ctk.CTkLabel(
            header_frame,
            text=project.status.capitalize(),
            font=("Arial", 12),
            text_color=self._get_status_color(project.status),
        )
        status_label.pack(side="right")

        # Информация о проекте
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=5)

        # Даты
        dates_label = ctk.CTkLabel(
            info_frame,
            text=f"Начало: {project.start_date.strftime('%d.%m.%Y')} | "
            f"Дедлайн: {project.deadline.strftime('%d.%m.%Y')}",
        )
        dates_label.pack(side="left", padx=5)

        # Финансы
        balance = project.calculate_balance()
        finance_label = ctk.CTkLabel(
            info_frame,
            text=f"Стоимость: {project.total_cost:,.2f} | "
            f"Оплачено: {balance['total_paid']:,.2f} | "
            f"Баланс: {balance['balance']:,.2f}",
            text_color=self._get_balance_color(balance["balance"]),
        )
        finance_label.pack(side="right", padx=5)

        # Кнопки управления
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Открыть",
            command=lambda: self._open_project_details(project.id),
            width=100,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Платеж",
            command=lambda: self._show_payment_form(project.id),
            width=100,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Доработка",
            command=lambda: self._show_modification_form(project.id),
            width=100,
        ).pack(side="left", padx=5)

    def _get_status_color(self, status: str) -> str:
        """Получение цвета для статуса"""
        colors = {"active": "green", "completed": "gray", "overdue": "red"}
        return colors.get(status, "white")

    def _get_balance_color(self, balance: float) -> str:
        """Получение цвета для баланса"""
        if balance > 0:
            return "green"
        elif balance < 0:
            return "red"
        return "white"

    def _on_search(self, *args):
        """Обработка поиска"""
        search_text = self.search_var.get().lower()
        for child in self.projects_frame.winfo_children():
            child.pack_forget()

        for project in self.project_manager.get_all_projects():
            if (
                search_text in project.name.lower()
                or search_text in project.description.lower()
            ):
                self._create_project_card(project)

    def _show_project_form(self, project_id: Optional[int] = None):
        """Показать форму создания/редактирования проекта"""
        from src.gui.forms.project_form import ProjectForm

        ProjectForm(self, project_id, self._load_projects)

    def _show_payment_form(self, project_id: int):
        """Показать форму добавления платежа"""
        from src.gui.forms.payment_form import PaymentForm

        PaymentForm(self, project_id, self._load_projects)

    def _show_modification_form(self, project_id: int):
        """Показать форму добавления доработки"""
        from src.gui.forms.modification_form import ModificationForm

        ModificationForm(self, project_id, self._load_projects)

    def _open_project_details(self, project_id: int):
        """Открыть детальную информацию о проекте"""
        from src.gui.forms.project_details import ProjectDetails

        ProjectDetails(self, project_id, self._load_projects)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
