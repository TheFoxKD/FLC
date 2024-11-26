from typing import Callable, Optional

import customtkinter as ctk

from src.utils.plot_utils import create_modifications_chart, create_payments_chart


class ProjectDetails(ctk.CTkToplevel):
    def __init__(self, parent, project_id: int, callback: Optional[Callable] = None):
        super().__init__(parent)

        self.title("Детали проекта")
        self.geometry("800x900")

        self.project_manager = parent.project_manager
        self.payment_manager = parent.payment_manager
        self.modification_manager = parent.modification_manager
        self.project_id = project_id
        self.callback = callback

        self.project = self.project_manager.get_project(project_id)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Настройка интерфейса"""
        # Создаем notebook для вкладок
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Добавляем вкладки
        self.notebook.add("Общая информация")
        self.notebook.add("Платежи")
        self.notebook.add("Доработки")
        self.notebook.add("Аналитика")

        # Настраиваем каждую вкладку
        self._setup_general_tab()
        self._setup_payments_tab()
        self._setup_modifications_tab()
        self._setup_analytics_tab()

    def _setup_general_tab(self):
        """Настройка вкладки общей информации"""
        tab = self.notebook.tab("Общая информация")

        # Заголовок проекта
        header_frame = ctk.CTkFrame(tab)
        header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            header_frame, text=self.project.name, font=("Arial", 20, "bold")
        ).pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(
            header_frame, text=self.project.status.capitalize(), font=("Arial", 14)
        )
        self.status_label.pack(side="right", padx=10)

        # Основная информация
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=10, pady=5)

        # Даты
        dates_frame = ctk.CTkFrame(info_frame)
        dates_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            dates_frame,
            text=f"Начало: {self.project.start_date.strftime('%d.%m.%Y')} | "
            f"Дедлайн: {self.project.deadline.strftime('%d.%m.%Y')}",
        ).pack(anchor="w", padx=10)

        # Финансы
        finance_frame = ctk.CTkFrame(info_frame)
        finance_frame.pack(fill="x", pady=5)

        self.balance_label = ctk.CTkLabel(finance_frame, text="")
        self.balance_label.pack(anchor="w", padx=10)

        # Технологический стек
        tech_frame = ctk.CTkFrame(tab)
        tech_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            tech_frame, text="Технологический стек:", font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        tech_text = ctk.CTkTextbox(tech_frame, height=60)
        tech_text.pack(fill="x", padx=10, pady=(0, 5))
        tech_text.insert("1.0", self.project.tech_stack or "Не указан")
        tech_text.configure(state="disabled")

        # Описание
        desc_frame = ctk.CTkFrame(tab)
        desc_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            desc_frame, text="Описание проекта:", font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        desc_text = ctk.CTkTextbox(desc_frame, height=100)
        desc_text.pack(fill="x", padx=10, pady=(0, 5))
        desc_text.insert("1.0", self.project.description or "Описание отсутствует")
        desc_text.configure(state="disabled")

        # Контакты клиента
        contacts_frame = ctk.CTkFrame(tab)
        contacts_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            contacts_frame, text="Контакты клиента:", font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        contacts_text = ctk.CTkTextbox(contacts_frame, height=60)
        contacts_text.pack(fill="x", padx=10, pady=(0, 5))
        contacts_text.insert(
            "1.0", self.project.client_contacts or "Контакты не указаны"
        )
        contacts_text.configure(state="disabled")

    def _setup_payments_tab(self):
        """Настройка вкладки платежей"""
        tab = self.notebook.tab("Платежи")

        # Кнопка добавления платежа
        ctk.CTkButton(
            tab, text="Добавить платёж", command=lambda: self._show_payment_form()
        ).pack(anchor="w", padx=10, pady=5)

        # Список платежей
        self.payments_frame = ctk.CTkScrollableFrame(tab)
        self.payments_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _setup_modifications_tab(self):
        """Настройка вкладки доработок"""
        tab = self.notebook.tab("Доработки")

        # Кнопка добавления доработки
        ctk.CTkButton(
            tab,
            text="Добавить доработку",
            command=lambda: self._show_modification_form(),
        ).pack(anchor="w", padx=10, pady=5)

        # Список доработок
        self.modifications_frame = ctk.CTkScrollableFrame(tab)
        self.modifications_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _setup_analytics_tab(self):
        """Настройка вкладки аналитики"""
        tab = self.notebook.tab("Аналитика")

        # График платежей
        self.payments_chart = create_payments_chart(tab, self.project)
        self.payments_chart.pack(fill="x", padx=10, pady=5)

        # График доработок
        self.modifications_chart = create_modifications_chart(tab, self.project)
        self.modifications_chart.pack(fill="x", padx=10, pady=5)

    def _load_data(self):
        """Загрузка данных проекта"""
        # Обновление баланса
        balance = self.project.calculate_balance()
        self.balance_label.configure(
            text=(
                f"Стоимость проекта: {balance['total_cost']:,.2f}\n"
                f"Оплачено: {balance['total_paid']:,.2f}\n"
                f"Баланс: {balance['balance']:,.2f}\n"
                f"Стоимость доработок: {balance['mods_cost']:,.2f}"
            )
        )

        # Загрузка платежей
        self._load_payments()

        # Загрузка доработок
        self._load_modifications()

        # Обновление графиков
        self._update_analytics()

    def _load_payments(self):
        """Загрузка списка платежей"""
        # Очистка списка
        for widget in self.payments_frame.winfo_children():
            widget.destroy()

        # Получение платежей
        payments = self.payment_manager.get_project_payments(self.project_id)

        # Отображение платежей
        for payment in payments:
            self._create_payment_card(payment)

    def _load_modifications(self):
        """Загрузка списка доработок"""
        # Очистка списка
        for widget in self.modifications_frame.winfo_children():
            widget.destroy()

        # Получение доработок
        modifications = self.modification_manager.get_project_modifications(
            self.project_id
        )

        # Отображение доработок
        for modification in modifications:
            self._create_modification_card(modification)

    def _create_payment_card(self, payment):
        """Создание карточки платежа"""
        frame = ctk.CTkFrame(self.payments_frame)
        frame.pack(fill="x", padx=5, pady=5)

        # Основная информация
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            info_frame, text=f"Сумма: {payment.amount:,.2f}", font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            info_frame,
            text=payment.payment_date.strftime("%d.%m.%Y"),
            font=("Arial", 12),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            info_frame, text=payment.status.capitalize(), font=("Arial", 12)
        ).pack(side="right", padx=5)

        # Описание
        if payment.description:
            desc_text = ctk.CTkTextbox(frame, height=40)
            desc_text.pack(fill="x", padx=10, pady=(0, 5))
            desc_text.insert("1.0", payment.description)
            desc_text.configure(state="disabled")

    def _create_modification_card(self, modification):
        """Создание карточки доработки"""
        frame = ctk.CTkFrame(self.modifications_frame)
        frame.pack(fill="x", padx=5, pady=5)

        # Основная информация
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            info_frame,
            text=f"{'Платная' if modification.is_paid else 'Бесплатная'} доработка",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=5)

        if modification.is_paid:
            ctk.CTkLabel(
                info_frame,
                text=f"Стоимость: {modification.cost:,.2f}",
                font=("Arial", 12),
            ).pack(side="left", padx=5)

        ctk.CTkLabel(
            info_frame, text=modification.status.capitalize(), font=("Arial", 12)
        ).pack(side="right", padx=5)

        # Описание
        desc_text = ctk.CTkTextbox(frame, height=60)
        desc_text.pack(fill="x", padx=10, pady=(0, 5))
        desc_text.insert("1.0", modification.description)
        desc_text.configure(state="disabled")

        # Даты
        dates_frame = ctk.CTkFrame(frame)
        dates_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            dates_frame,
            text=f"Начало: {modification.start_date.strftime('%d.%m.%Y')} | "
            f"Дедлайн: {modification.deadline.strftime('%d.%m.%Y')}",
        ).pack(anchor="w")

    def _update_analytics(self):
        """Обновление графиков"""
        # Очищаем старые графики
        for widget in self.payments_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.modifications_plot_frame.winfo_children():
            widget.destroy()

        # График платежей
        payments_chart = create_payments_chart(self.payments_plot_frame, self.project)
        payments_chart.pack(fill="both", expand=True)

        # График доработок
        modifications_chart = create_modifications_chart(
            self.modifications_plot_frame, self.project
        )
        modifications_chart.pack(fill="both", expand=True)

    def _show_payment_form(self):
        """Показать форму добавления платежа"""
        from .payment_form import PaymentForm

        PaymentForm(self, self.project_id, self._load_data)

    def _show_modification_form(self):
        """Показать форму добавления доработки"""
        from .modification_form import ModificationForm

        ModificationForm(self, self.project_id, self._load_data)
