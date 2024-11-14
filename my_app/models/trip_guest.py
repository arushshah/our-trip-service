from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db

class RsvpStatus(Enum):
    INVITED = "INVITED"
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"

class TripGuest(db.Model):
    __tablename__ = 'trip_guests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    guest_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False, index=True)
    is_host: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rsvp_status: Mapped[str] = mapped_column(SQLEnum(RsvpStatus), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('trip_id', 'guest_id'),
    )

    def __repr__(self):
        return f"<TripGuest(trip_id={self.trip_id}, guest_id='{self.guest_id}', is_host={self.is_host}, rsvp_status='{self.rsvp_status}')>"