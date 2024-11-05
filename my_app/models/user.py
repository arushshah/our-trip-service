from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from my_app.models import db

class User(db.Model):
    __tablename__ = 'users'  # Optional, to specify table name

    # Defining columns with mapped_column()
    user_id: Mapped[str] = mapped_column(String(20), primary_key=True) # user id will be the phone number
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"<User("
            f"user_id/phone_number='{self.user_id}', "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}', "
            f")>"
        )