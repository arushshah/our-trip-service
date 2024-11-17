from datetime import datetime
from sqlalchemy import DateTime, String, Integer, ForeignKey, PrimaryKeyConstraint, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db

class TripTodo(db.Model):
    __tablename__ = 'trip_todos'

    id: Mapped[str] = mapped_column(String(45), primary_key=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_updated_by = mapped_column(String(20), ForeignKey('users.id'), nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self):
        return f"<TripTodo(id={self.id}, trip_id={self.trip_id}, text='{self.text}', checked={self.checked}, last_updated_by='{self.last_updated_by}', last_updated_at='{self.last_updated_at}')>"