
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (db.UniqueConstraint('phone_number'),)

    def __repr__(self):
        return (
            f"<User("
            f"id='{self.id}', "
            f"phone_number='{self.phone_number}', "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}', "
            f")>"
        )