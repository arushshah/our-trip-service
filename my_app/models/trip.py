from sqlalchemy import ForeignKey, String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from models import db

class Trip(db.Model):
    __tablename__ = 'trips'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    host_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self):
        return f"<Trip(id={self.id}, name='{self.name}', host='{self.host_id}', start_date='{self.start_date}', end_date='{self.end_date}')>"
