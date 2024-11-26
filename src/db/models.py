from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(50), default="active")
    total_cost = Column(Float, nullable=False)
    tech_stack = Column(Text)
    description = Column(Text)
    client_contacts = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = relationship(
        "Payment", back_populates="project", cascade="all, delete-orphan"
    )
    modifications = relationship(
        "Modification", back_populates="project", cascade="all, delete-orphan"
    )

    def calculate_balance(self) -> dict:
        """Расчет текущего баланса проекта"""
        total_paid = sum(
            payment.amount for payment in self.payments if payment.status == "completed"
        )
        mods_cost = sum(mod.cost for mod in self.modifications if mod.is_paid)
        total_cost = self.total_cost + mods_cost
        balance = total_paid - total_cost

        return {
            "total_cost": total_cost,
            "total_paid": total_paid,
            "balance": balance,
            "mods_cost": mods_cost,
            "original_cost": self.total_cost,
        }


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_type = Column(String(50))
    description = Column(Text)
    status = Column(String(50), default="pending")

    # Relationships
    project = relationship("Project", back_populates="payments")


class Modification(Base):
    __tablename__ = "modifications"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    is_paid = Column(Boolean, default=True)

    # Relationships
    project = relationship("Project", back_populates="modifications")
    payments = relationship(
        "ModificationPayment",
        back_populates="modification",
        cascade="all, delete-orphan",
    )


class ModificationPayment(Base):
    __tablename__ = "modification_payments"

    id = Column(Integer, primary_key=True)
    modification_id = Column(Integer, ForeignKey("modifications.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")

    # Relationships
    modification = relationship("Modification", back_populates="payments")


# Database initialization
def init_db(db_path: str = "flc.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
