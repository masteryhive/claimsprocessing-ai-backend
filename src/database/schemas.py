
from datetime import datetime
import enum
from src.config.db_setup import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  JSON, Column, Float, String, DateTime, Integer, Enum as SQLEnum, Text
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
    task_id = Column(String, unique=True, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    task_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    progress = Column(Integer, default=0)  # Optional: track progress percentage
    result = Column(String, nullable=True)  # Store task result if needed

class ClaimsReport(Base):
    __tablename__ = 'claim_reports'

    id = Column(Integer, primary_key=True)
    fraud_score = Column(Float(precision=2), nullable=False)  # double precision
    fraud_indicators = Column(JSON, nullable=False)  # jsonb array
    ai_recommendation = Column(JSON, nullable=False)  # jsonb array
    policy_review = Column(String(length=None))      # character varying
    created_at = Column(DateTime, nullable=False)    # timestamp without time zone
    updated_at = Column(DateTime, nullable=False)    # timestamp without time zone

    def __init__(self, 
                 fraud_score: float,
                 fraud_indicators: list,
                 ai_recommendation: list,
                 policy_review: str,
                 created_at: datetime = None,
                 updated_at: datetime = None):
        self.fraud_score = fraud_score
        self.fraud_indicators = fraud_indicators
        self.ai_recommendation = ai_recommendation
        self.policy_review = policy_review
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self):
        return f"<Claim(fraud_score={self.fraud_score}, created_at={self.created_at})>"

# Create tables
Base.metadata.create_all(bind=engine)