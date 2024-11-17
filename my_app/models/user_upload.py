from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from models import db

class DocumentCategory(Enum):
    TRAVEL="travel"
    ACCOMMODATION="accommodation"

class UserUpload(db.Model):
    __tablename__ = "user_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    document_category = mapped_column(SQLEnum(DocumentCategory), nullable=False)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_url: Mapped[str] = mapped_column(String(512), nullable=False)
    upload_timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(6), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<UserUpload(id={self.id}, upload_user_id='{self.upload_user_id}', document_category='{self.document_category}', trip_id={self.trip_id}, file_name='{self.file_name}', s3_url='{self.s3_url}', upload_timestamp='{self.upload_timestamp}')>"