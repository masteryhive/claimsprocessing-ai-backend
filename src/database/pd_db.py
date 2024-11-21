from contextlib import contextmanager
import json
import psycopg2
from psycopg2.extras import Json
from fastapi import HTTPException
from typing import Generator, List
from psycopg2._psycopg import cursor
from sqlalchemy import desc
from src.database.schemas import ClaimsReport, ConversationHistory
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
            password=env_config.password
        )
        # Create a cursor
        cur = conn.cursor()
        yield cur
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection error"
        ) from e
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        ) from e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

async def insert_chat_message(cur: cursor, room_id: str, resource_urls, sender: str, message: str) -> None:
    """
    Insert a new chat message into the database.
    
    Args:
        cur: Database cursor
        room_id: Chat room identifier
        resource_urls: URLs of associated resources
        sender: Message sender
        message: Message content
        
    Raises:
        HTTPException: If insertion fails
    """
    try:
        query = """
            INSERT INTO chat_messages (room_id, resource_urls, sender, message)
            VALUES (%s, %s, %s, %s)
        """
        resource_urls_jsonb = json.dumps(resource_urls)  # Convert resource_urls to JSON string
        cur.execute(query, (room_id, resource_urls_jsonb, sender, message))
    except psycopg2.Error as e:
        logger.error(f"Error inserting chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save chat message"
        ) from e


async def insert_conversation(
    db: Session,
    room_id: str,
    resource_urls: List[str],
    ai_message: str,
    user_message: str = "",
    system_message: str = ""
) -> None:
    """
    Insert a new chat message into the database using SQLAlchemy ORM.
    
    Args:
        db: SQLAlchemy database session
        room_id: Chat room identifier
        resource_urls: URLs of associated resources
        ai_message: AI's response message
        user_message: User's message (optional)
        system_message: System message (optional)
        
    Raises:
        HTTPException: If insertion fails
    """
    try:
        # Create new conversation history entry
        conversation = ConversationHistory(
            room_id=room_id,
            resource_urls=resource_urls,  # SQLAlchemy will handle JSON serialization
            ai_message=ai_message,
            user_message="" if system_message else user_message,
            system_message=system_message if system_message else ""
        )

        # Add and commit to database
        db.add(conversation)
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save chat message"
        ) from e


    
def get_conversation_history(db: Session, room_id: str, k: int = 48) -> str:
    """
    Retrieve chat messages for a specific room using SQLAlchemy ORM.
    
    Args:
        db: SQLAlchemy database session
        room_id: Chat room identifier
        k: Number of messages to retrieve (default: 12)
        
    Returns:
        str: Formatted conversation history
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Query messages using ORM
        messages = (
            db.query(ConversationHistory)
            .filter(ConversationHistory.room_id == room_id)
            .order_by(desc(ConversationHistory.id))
            .limit(k)
            .all()
        )

        # Format the chat history as a conversation with Human/Assistant turns
        conversation_parts = []
        
        # Process messages in reverse order for chronological display
        for message in reversed(messages):
            if message.system_message:
                conversation_parts.append(
                    message.system_message.replace('\n', '\\n')
                )
            else:
                conversation_parts.append(
                    f"Human: {message.user_message.replace('\n', '\\n')}"
                )
            conversation_parts.append(
                f"AI:{message.ai_message.replace('\n', '\\n')}"
            )
        
        return '\n'.join(conversation_parts)

    except Exception as e:
        logger.error(f"Error retrieving chat messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat messages"
        ) from e


def create_claim(db: Session, 
                fraud_score: float,
                fraud_indicators: list,
                ai_recommendation: list,
                policy_review: str) -> ClaimsReport:
    """
    Create a new claim record
    """
    claim_report = ClaimsReport(
        fraud_score=fraud_score,
        fraud_indicators=fraud_indicators,
        ai_recommendation=ai_recommendation,
        policy_review=policy_review
    )
    db.add(claim_report)
    db.commit()
    db.refresh(claim_report)
    return claim_report