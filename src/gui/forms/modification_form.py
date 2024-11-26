import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from typing import Optional, Callable


class ModificationForm(ctk.CTkToplevel):
    def __init__(self, parent, project_id: int, callback: Optional[Callable] = None):
        super().__init__(parent)

        self.title("Доработка проекта")
        self.geometry("500x700")

        self.project_manager = parent.project_manager
        self.modification_manager = parent.modification_manager
        self.project_id = project_id
        self.callback = callback

        self.project = self.project_manager.get_project(project_id)
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса формы"""
        # Информация о проекте
        project_frame = ctk.CTkFrame(self)
        project_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            project_frame,
            text=f"Проект: {self.project.name}",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=10, pady=5)

        # Описание доработки
        ctk.CTkLabel(self, text="Описание доработки:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.description_text = ctk.CTkTextbox(self, width=460, height=150)
        self.description_text.pack(anchor="w", padx=10, pady=(0, 10))

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

        # Тип доработки (платная/бесплатная)
        type_frame = ctk.CTkFrame(self)
        type_frame.pack(fill="x", padx=10, pady=10)

        self.is_paid_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            type_frame,
            text="Платная доработка",
            variable=self.is_paid_var,
            command=self._toggle_cost_field,
        ).pack(side="left", padx=10)

        # Стоимость
        self.cost_frame = ctk.CTkFrame(self)
        self.cost_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.cost_frame, text="Стоимость доработки:").pack(
            side="left", padx=5
        )
        self.cost_var = ctk.StringVar(value="0")
        self.cost_entry = ctk.CTkEntry(
            self.cost_frame, width=150, textvariable=self.cost_var
        )
        self.cost_entry.pack(side="left", padx=5)

        # Статус
        ctk.CTkLabel(self, text="Статус:").pack(anchor="w", padx=10, pady=(10, 0))
        self.status_var = ctk.StringVar(value="pending")
        statuses = {
            "pending": "В ожидании",
            "in_progress": "В работе",
            "completed": "Завершена",
            "cancelled": "Отменена",
        }

        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        for value, text in statuses.items():
            ctk.CTkRadioButton(
                status_frame, text=text, variable=self.status_var, value=value
            ).pack(side="left", padx=10)

        # Платёж
        payment_frame = ctk.CTkFrame(self)
        payment_frame.pack(fill="x", padx=10, pady=10)

        self.add_payment_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            payment_frame,
            text="Добавить платёж",
            variable=self.add_payment_var,
            command=self._toggle_payment_fields,
        ).pack(side="left", padx=10)

        # Поля для платежа
        self.payment_details_frame = ctk.CTkFrame(self)
        self.payment_details_frame.pack(fill="x", padx=10, pady=5)
        self.payment_details_frame.pack_forget()  # Скрываем изначально

        # Сумма платежа
        payment_amount_frame = ctk.CTkFrame(self.payment_details_frame)
        payment_amount_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(payment_amount_frame, text="Сумма платежа:").pack(
            side="left", padx=5
        )
        self.payment_amount_var = ctk.StringVar(value="0")
        self.payment_amount_entry = ctk.CTkEntry(
            payment_amount_frame, width=150, textvariable=self.payment_amount_var
        )
        self.payment_amount_entry.pack(side="left", padx=5)

        # Дата платежа
        payment_date_frame = ctk.CTkFrame(self.payment_details_frame)
        payment_date_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(payment_date_frame, text="Дата платежа:").pack(side="left", padx=5)
        self.payment_date = DateEntry(
            payment_date_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
        )
        self.payment_date.pack(side="left", padx=5)

        # Кнопки
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkButton(
            buttons_frame, text="Сохранить", command=self._save_modification, width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame, text="Отмена", command=self.destroy, width=120
        ).pack(side="left", padx=5)

    def _toggle_cost_field(self):
        """Переключение видимости поля стоимости"""
        if self.is_paid_var.get():
            self.cost_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.cost_frame.pack_forget()
            self.cost_var.set("0")

    def _toggle_payment_fields(self):
        """Переключение видимости полей платежа"""
        if self.add_payment_var.get():
            self.payment_details_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.payment_details_frame.pack_forget()

    def _save_modification(self):
        """Сохранение доработки"""
        try:
            # Данные доработки
            modification_data = {
                "project_id": self.project_id,
                "description": self.description_text.get("1.0", "end-1c"),
                "start_date": datetime.strptime(self.start_date.get(), "%d.%m.%Y"),
                "deadline": datetime.strptime(self.deadline.get(), "%d.%m.%Y"),
                "is_paid": self.is_paid_var.get(),
                "cost": float(self.cost_var.get()) if self.is_paid_var.get() else 0.0,
                "status": self.status_var.get(),
            }

            # Создаем доработку
            modification = self.modification_manager.add_modification(
                **modification_data
            )

            # Если нужно добавить платёж
            if self.add_payment_var.get():
                payment_data = {
                    "modification_id": modification.id,
                    "amount": float(self.payment_amount_var.get()),
                    "payment_date": datetime.strptime(
                        self.payment_date.get(), "%d.%m.%Y"
                    ),
                }
                self.modification_manager.add_modification_payment(**payment_data)

            if self.callback:
                self.callback()

            self.destroy()

        except ValueError as e:
            # Показать сообщение об ошибке
            error_window = ctk.CTkToplevel(self)
            error_window.title("Ошибка")
            error_window.geometry("300x100")

            ctk.CTkLabel(
                error_window, text=f"Ошибка при сохранении доработки:\n{str(e)}"
            ).pack(padx=20, pady=20)

            ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(
                pady=10
            )
