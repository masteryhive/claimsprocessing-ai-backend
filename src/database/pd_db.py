from contextlib import contextmanager
import json
import psycopg2
from psycopg2.extras import Json
from fastapi import HTTPException
from typing import Generator, List
from psycopg2._psycopg import cursor
from sqlalchemy import desc
from src.database.schemas import ClaimsReport
from sqlalchemy.orm import Session
from src.config.appconfig import env_config

import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db() -> Generator[cursor, None, None]:
    """
    Database connection context manager.
    Yields a database cursor and handles proper connection cleanup.

    Raises:
        HTTPException: If database connection fails
    """
    conn = None
    cur = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=env_config.host,
            database=env_config.database,
            user=env_config.user,
            password=env_config.password,
        )
        # Create a cursor
        cur = conn.cursor()
        yield cur
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error") from e
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        ) from e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def create_claim_report(
    db: Session,
    id: str,
    fraud_score: float,
    fraud_indicators: list,
    discoveries: list,
    ai_recommendation: list,
    policy_review: str,
    evidence_provided: list,
    coverage_status: str,
    type_of_incident: str,
    details: str,
):
    """
    Create a new claim record
    """
    claim_report = ClaimsReport(
        id=id,
        fraud_score=fraud_score,
        discoveries=discoveries,
        fraud_indicators=fraud_indicators,
        ai_recommendation=ai_recommendation,
        policy_review=policy_review,
        evidence_provided=evidence_provided,
        coverage_status=coverage_status,
        details=details,
        type_of_incident=type_of_incident,
    )
    db.add(claim_report)
    db.commit()
    db.refresh(claim_report)
    db.close()
