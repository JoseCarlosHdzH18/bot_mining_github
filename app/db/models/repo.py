from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), unique=True, nullable=False, index=True)
    owner = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    language = Column(String(100), nullable=True)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    __table_args__ = (
        Index("idx_repo_job", "job_id"),
        Index("idx_repo_language", "language"),
    )
