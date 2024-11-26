import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from typing import Optional, Callable


class ProjectForm(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        project_id: Optional[int] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__(parent)

        self.title("Проект")
        self.geometry("600x700")

        self.project_manager = parent.project_manager
        self.project_id = project_id
        self.callback = callback

        self.project = None
        if project_id:
            self.project = self.project_manager.get_project(project_id)

        self._setup_ui()
        if self.project:
            self._load_project_data()

    def _setup_ui(self):
        """Настройка интерфейса формы"""
        # Основная информация
        ctk.CTkLabel(self, text="Название проекта:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.name_var = ctk.StringVar(value=self.project.name if self.project else "")
        self.name_entry = ctk.CTkEntry(self, width=400, textvariable=self.name_var)
        self.name_entry.pack(anchor="w", padx=10, pady=(0, 10))

        # Даты
        dates_frame = ctk.CTkFrame(self)
        dates_frame.pack(fill="x", padx=10, pady=5)

        # Дата начала
        start_frame = ctk.CTkFrame(dates_frame)
        start_frame.pack(side="left", padx=5)
        ctk.CTkLabel(start_frame, text="Дата начала:").pack()
        self.start_date = DateEntry(
            start_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
        )
        self.start_date.pack()

        # Дедлайн
        deadline_frame = ctk.CTkFrame(dates_frame)
        deadline_frame.pack(side="left", padx=5)
        ctk.CTkLabel(deadline_frame, text="Дедлайн:").pack()
        self.deadline = DateEntry(
            deadline_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
        )
        self.deadline.pack()

        # Стоимость
        ctk.CTkLabel(self, text="Стоимость проекта:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.cost_var = ctk.StringVar(
            value=str(self.project.total_cost) if self.project else "0"
        )
        self.cost_entry = ctk.CTkEntry(self, width=200, textvariable=self.cost_var)
        self.cost_entry.pack(anchor="w", padx=10, pady=(0, 10))

        # Технологический стек
        ctk.CTkLabel(self, text="Технологический стек:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.tech_text = ctk.CTkTextbox(self, width=400, height=100)
        self.tech_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Описание
        ctk.CTkLabel(self, text="Описание проекта:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.description_text = ctk.CTkTextbox(self, width=400, height=150)
        self.description_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Контакты клиента
        ctk.CTkLabel(self, text="Контакты клиента:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.contacts_text = ctk.CTkTextbox(self, width=400, height=100)
        self.contacts_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Статус
        ctk.CTkLabel(self, text="Статус:").pack(anchor="w", padx=10, pady=(10, 0))
        self.status_var = ctk.StringVar(
            value=self.project.status if self.project else "active"
        )
        statuses = ["active", "completed", "overdue"]

        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        for status in statuses:
            ctk.CTkRadioButton(
                status_frame,
                text=status.capitalize(),
                variable=self.status_var,
                value=status,
            ).pack(side="left", padx=10)

        # Кнопки
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkButton(
            buttons_frame, text="Сохранить", command=self._save_project, width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame, text="Отмена", command=self.destroy, width=120
        ).pack(side="left", padx=5)

    def _load_project_data(self):
        """Загрузка данных проекта в форму"""
        if self.project.tech_stack:
            self.tech_text.insert("1.0", self.project.tech_stack)
        if self.project.description:
            self.description_text.insert("1.0", self.project.description)
        if self.project.client_contacts:
            self.contacts_text.insert("1.0", self.project.client_contacts)

        # Установка дат
        self.start_date.set_date(self.project.start_date)
        self.deadline.set_date(self.project.deadline)

    def _save_project(self):
        """Сохранение проекта"""
        try:
            project_data = {
                "name": self.name_var.get(),
                "start_date": datetime.strptime(self.start_date.get(), "%d.%m.%Y"),
                "deadline": datetime.strptime(self.deadline.get(), "%d.%m.%Y"),
                "total_cost": float(self.cost_var.get()),
                "tech_stack": self.tech_text.get("1.0", "end-1c"),
                "description": self.description_text.get("1.0", "end-1c"),
                "client_contacts": self.contacts_text.get("1.0", "end-1c"),
                "status": self.status_var.get(),
            }

            if self.project:
                self.project_manager.update_project(self.project_id, **project_data)
            else:
                self.project_manager.create_project(**project_data)

            if self.callback:
                self.callback()

            self.destroy()

        except ValueError as e:
            # Показать сообщение об ошибке
            error_window = ctk.CTkToplevel(self)
            error_window.title("Ошибка")
            error_window.geometry("300x100")

            ctk.CTkLabel(
                error_window, text=f"Ошибка при сохранении проекта:\n{str(e)}"
            ).pack(padx=20, pady=20)

            ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(
                pady=10
            )
