from datetime import datetime
import enum
from src.config.db_setup import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    JSON,
    Column,
    Float,
    String,
    DateTime,
    Integer,
    Enum as SQLEnum,
    Text,
)

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Task model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, unique=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    task_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    progress = Column(Integer, default=0)  # Optional: track progress percentage
    result = Column(String, nullable=True)  # Store task result if needed


# Create tables
Base.metadata.create_all(bind=engine)
