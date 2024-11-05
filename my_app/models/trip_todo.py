from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from my_app.models import db

class TripTodo(db.Model):
    __tablename__ = 'trip_todos'

    id: Mapped[str] = mapped_column(String(45), nullable=False)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('trip_id', 'id'),
    )