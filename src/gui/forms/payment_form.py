import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from typing import Optional, Callable


class PaymentForm(ctk.CTkToplevel):
    def __init__(self, parent, project_id: int, callback: Optional[Callable] = None):
        super().__init__(parent)

        self.title("Добавление платежа")
        self.geometry("400x500")

        self.project_manager = parent.project_manager
        self.payment_manager = parent.payment_manager
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

        balance = self.project.calculate_balance()
        ctk.CTkLabel(
            project_frame, text=f"Остаток к оплате: {abs(balance['balance']):,.2f}"
        ).pack(anchor="w", padx=10, pady=5)

        # Сумма платежа
        ctk.CTkLabel(self, text="Сумма платежа:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        self.amount_var = ctk.StringVar(value="0")
        self.amount_entry = ctk.CTkEntry(self, width=200, textvariable=self.amount_var)
        self.amount_entry.pack(anchor="w", padx=10, pady=(0, 10))

        # Дата платежа
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(date_frame, text="Дата платежа:").pack(side="left", padx=5)
        self.payment_date = DateEntry(
            date_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd.mm.yyyy",
        )
        self.payment_date.pack(side="left", padx=5)

        # Тип платежа
        ctk.CTkLabel(self, text="Тип платежа:").pack(anchor="w", padx=10, pady=(10, 0))
        self.payment_type_var = ctk.StringVar(value="transfer")
        payment_types = {"transfer": "Перевод", "cash": "Наличные", "card": "Карта"}

        type_frame = ctk.CTkFrame(self)
        type_frame.pack(fill="x", padx=10, pady=5)

        for value, text in payment_types.items():
            ctk.CTkRadioButton(
                type_frame, text=text, variable=self.payment_type_var, value=value
            ).pack(side="left", padx=10)

        # Статус платежа
        ctk.CTkLabel(self, text="Статус:").pack(anchor="w", padx=10, pady=(10, 0))
        self.status_var = ctk.StringVar(value="completed")
        statuses = {
            "pending": "Ожидается",
            "completed": "Выполнен",
            "cancelled": "Отменён",
        }

        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        for value, text in statuses.items():
            ctk.CTkRadioButton(
                status_frame, text=text, variable=self.status_var, value=value
            ).pack(side="left", padx=10)

        # Описание
        ctk.CTkLabel(self, text="Описание:").pack(anchor="w", padx=10, pady=(10, 0))
        self.description_text = ctk.CTkTextbox(self, width=360, height=100)
        self.description_text.pack(anchor="w", padx=10, pady=(0, 10))

        # Кнопки
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkButton(
            buttons_frame, text="Сохранить", command=self._save_payment, width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame, text="Отмена", command=self.destroy, width=120
        ).pack(side="left", padx=5)

    def _save_payment(self):
        """Сохранение платежа"""
        try:
            payment_data = {
                "project_id": self.project_id,
                "amount": float(self.amount_var.get()),
                "payment_date": datetime.strptime(self.payment_date.get(), "%d.%m.%Y"),
                "payment_type": self.payment_type_var.get(),
                "status": self.status_var.get(),
                "description": self.description_text.get("1.0", "end-1c"),
            }

            self.payment_manager.add_payment(**payment_data)

            if self.callback:
                self.callback()

            self.destroy()

        except ValueError as e:
            # Показать сообщение об ошибке
            error_window = ctk.CTkToplevel(self)
            error_window.title("Ошибка")
            error_window.geometry("300x100")

            ctk.CTkLabel(
                error_window, text=f"Ошибка при сохранении платежа:\n{str(e)}"
            ).pack(padx=20, pady=20)

            ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(
                pady=10
            )
