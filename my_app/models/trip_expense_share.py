from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db

class TripExpenseShare(db.Model):
    __tablename__ = 'trip_expense_shares'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    expense_id: Mapped[int] = mapped_column(Integer, ForeignKey('trip_expenses.id'), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)

    def __repr__(self):
        return f"<TripExpenseShare(id={self.id}, expense_id={self.expense_id}, user_id='{self.user_id}', amount={self.amount})>"