from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db
from enum import Enum

class LocationCategory(db.Model):
    __tablename__ = 'location_categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey('trips.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (db.UniqueConstraint('trip_id', 'name'),)