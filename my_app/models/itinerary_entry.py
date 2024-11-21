from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db
from enum import Enum

class ItineraryEntry(db.Model):
    __tablename__ = 'itinerary_entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (db.UniqueConstraint('trip_id', 'name'),)