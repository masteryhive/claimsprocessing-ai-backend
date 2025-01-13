from contextlib import contextmanager
import json
import psycopg2
from psycopg2.extras import Json
from fastapi import HTTPException
from typing import Generator, List
from psycopg2._psycopg import cursor
from sqlalchemy import desc
from database.schemas import ClaimsReport
from sqlalchemy.orm import Session
from config.appconfig import env_config

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

