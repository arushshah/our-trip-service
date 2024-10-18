from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from my_app.models import db

class Trip(db.Model):
    __tablename__ = 'trips'  # Optional, to specify table name

    # Defining columns with mapped_column()
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)  # Part of composite key
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    host_username: Mapped[str] = mapped_column(String(45), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Trip(id={self.id}, name='{self.name}', host='{self.host_username}', start_date='{self.start_date}', end_date='{self.end_date}')>"
