from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from my_app.models import db

class UserUpload(db.Model):
    __tablename__ = "user_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(45), ForeignKey("users.username"), nullable=False)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_url: Mapped[str] = mapped_column(String(512), nullable=False)
    upload_timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(6), nullable=False, server_default=func.now())
