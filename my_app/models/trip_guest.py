from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from my_app.models import db

class RsvpStatus(Enum):
    INVITED = "INVITED"
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"

class TripGuest(db.Model):
    __tablename__ = 'trip_guests'

    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False)
    guest_user_id: Mapped[str] = mapped_column(String(45), ForeignKey('users.user_id'), nullable=False)
    is_host: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rsvp_status: Mapped[str] = mapped_column(SQLEnum(RsvpStatus), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('trip_id', 'guest_user_id'),
    )

    def __repr__(self):
        return f"<TripGuest trip_id={self.trip_id} guest_user_id={self.guest_user_id} is_host={self.is_host}>"