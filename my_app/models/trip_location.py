from sqlalchemy import Float, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from models import db

class TripLocation(db.Model):
    __tablename__ = 'trip_locations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    guest_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('trip_id', 'guest_id'),
    )

    def __repr__(self):
        return f"<TripLocation(trip_id={self.trip_id}, guest_id='{self.guest_id}', latitude={self.latitude}, longitude={self.longitude})>"