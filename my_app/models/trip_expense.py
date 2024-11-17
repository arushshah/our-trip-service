from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db
from enum import Enum

class TripExpense(db.Model):
    __tablename__ = 'trip_expenses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    settled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    

    def __repr__(self):
        return f"<TripExpense(id={self.id}, trip_id={self.trip_id}, payer_id='{self.payer_id}', description='{self.description}')>"