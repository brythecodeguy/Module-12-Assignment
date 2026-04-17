from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    result = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="calculations")

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "calculation",
    }

    @classmethod
    def create(cls, calculation_type: str, user_id, a: float, b: float) -> "Calculation":
        calculation_classes = {
            "addition": Addition,
            "subtraction": Subtraction,
            "multiplication": Multiplication,
            "division": Division,
        }

        calculation_class = calculation_classes.get(calculation_type.lower())
        if not calculation_class:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")

        calculation = calculation_class(user_id=user_id, a=a, b=b)
        calculation.result = calculation.get_result()
        return calculation

    def get_result(self) -> float:
        raise NotImplementedError("Subclasses must implement get_result()")

    def __repr__(self):
        return f"<Calculation(type={self.type}, a={self.a}, b={self.b}, result={self.result})>"


class Addition(Calculation):
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self) -> float:
        return self.a + self.b


class Subtraction(Calculation):
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self) -> float:
        return self.a - self.b


class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self) -> float:
        return self.a * self.b


class Division(Calculation):
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self) -> float:
        if self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self.a / self.b