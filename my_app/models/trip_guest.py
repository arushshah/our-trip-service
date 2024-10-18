from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from my_app.models import db

class TripGuest(db.Model):
    __tablename__ = 'trip_guests'

    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False)
    guest_username: Mapped[str] = mapped_column(String(45), ForeignKey('users.username'), nullable=False)
    is_host: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('trip_id', 'guest_username'),
    )

    def __repr__(self):
        return f"<TripGuest trip_id={self.trip_id} guest_username={self.guest_username} is_host={self.is_host}>"