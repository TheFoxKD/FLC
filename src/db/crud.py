from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from .models import Project, Payment, Modification, ModificationPayment


class ProjectManager:
    def __init__(self, session: Session):
        self.session = session

    def create_project(
        self,
        name: str,
        start_date: datetime,
        deadline: datetime,
        total_cost: float,
        **kwargs,
    ) -> Project:
        """Создание нового проекта"""
        project = Project(
            name=name,
            start_date=start_date,
            deadline=deadline,
            total_cost=total_cost,
            **kwargs,
        )
        self.session.add(project)
        self.session.commit()
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        """Получение проекта по ID"""
        return self.session.query(Project).get(project_id)

    def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        """Обновление данных проекта"""
        project = self.get_project(project_id)
        if project:
            for key, value in kwargs.items():
                setattr(project, key, value)
            project.updated_at = datetime.utcnow()
            self.session.commit()
        return project

    def delete_project(self, project_id: int) -> bool:
        """Удаление проекта"""
        project = self.get_project(project_id)
        if project:
            self.session.delete(project)
            self.session.commit()
            return True
        return False

    def get_project_balance(self, project_id: int) -> Dict:
        """Получение баланса проекта"""
        project = self.get_project(project_id)
        if project:
            return project.calculate_balance()
        return {}

    def get_all_projects(self, status: Optional[str] = None) -> List[Project]:
        """Получение списка всех проектов"""
        query = self.session.query(Project)
        if status:
            query = query.filter(Project.status == status)
        return query.all()


class PaymentManager:
    def __init__(self, session: Session):
        self.session = session

    def add_payment(
        self, project_id: int, amount: float, payment_date: datetime, **kwargs
    ) -> Optional[Payment]:
        """Добавление нового платежа"""
        payment = Payment(
            project_id=project_id, amount=amount, payment_date=payment_date, **kwargs
        )
        self.session.add(payment)
        self.session.commit()
        return payment

    def get_project_payments(self, project_id: int) -> List[Payment]:
        """Получение всех платежей проекта"""
        return (
            self.session.query(Payment)
            .filter(Payment.project_id == project_id)
            .order_by(Payment.payment_date)
            .all()
        )


class ModificationManager:
    def __init__(self, session: Session):
        self.session = session

    def add_modification(
        self,
        project_id: int,
        description: str,
        start_date: datetime,
        deadline: datetime,
        cost: float = 0.0,
        is_paid: bool = True,
        **kwargs,
    ) -> Modification:
        """Добавление новой доработки"""
        modification = Modification(
            project_id=project_id,
            description=description,
            start_date=start_date,
            deadline=deadline,
            cost=cost,
            is_paid=is_paid,
            **kwargs,
        )
        self.session.add(modification)
        self.session.commit()
        return modification

    def add_modification_payment(
        self, modification_id: int, amount: float, payment_date: datetime, **kwargs
    ) -> ModificationPayment:
        """Добавление платежа за доработку"""
        payment = ModificationPayment(
            modification_id=modification_id,
            amount=amount,
            payment_date=payment_date,
            **kwargs,
        )
        self.session.add(payment)
        self.session.commit()
        return payment

    def get_project_modifications(self, project_id: int) -> List[Modification]:
        """Получение всех доработок проекта"""
        return (
            self.session.query(Modification)
            .filter(Modification.project_id == project_id)
            .order_by(Modification.start_date)
            .all()
        )
