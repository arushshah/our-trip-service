from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db
from enum import Enum

class TripLocation(db.Model):
    __tablename__ = 'trip_locations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place_id: Mapped[str] = mapped_column(String(200), nullable=False)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(200), nullable=False)

    def __repr__(self):
        return f"<TripLocation(id={self.id}, trip_id={self.trip_id}, user_id='{self.user_id}', name='{self.name}')>"