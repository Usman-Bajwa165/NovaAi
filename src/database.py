"""Database module for NOVA application."""

import os
import sqlite3
from src.logger import logger

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "voice_ai.db")


def get_db():
    """Get a database connection with row factory."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        logger.debug("Database connection established")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {e}", exc_info=True)
        raise


def init_db():
    """Initialize the database with required tables."""
    try:
        logger.info("Initializing database...")

        with get_db() as conn:
            # User table (base schema)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Ensure optional name column exists for personalized greetings
            try:
                conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
            except sqlite3.OperationalError:
                # Column already exists; safe to ignore
                pass

            # Memory table (Conversation context)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """
            )

            # Create index for faster queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memory_user_timestamp 
                ON memory(user_id, timestamp DESC)
            """
            )

            conn.commit()

        logger.info("Database initialized successfully")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error during database initialization: {e}", exc_info=True
        )
        return False


def verify_db():
    """Verify that the database exists and has the required tables."""
    try:
        if not os.path.exists(DB_PATH):
            logger.warning("Database file does not exist")
            return False

        with get_db() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'memory')"
            )
            tables = [row[0] for row in cursor.fetchall()]

            if len(tables) != 2:
                logger.warning(f"Missing tables. Found: {tables}")
                return False

        logger.debug("Database verification passed")
        return True

    except Exception as e:
        logger.error(f"Database verification failed: {e}", exc_info=True)
        return False


def ensure_db():
    """Ensure database exists and is properly initialized."""
    if not verify_db():
        logger.info("Database verification failed, initializing...")
        return init_db()
    return True


if __name__ == "__main__":
    # Initialize database when run directly
    if init_db():
        print("Database initialized successfully.")
        print(f"Database location: {DB_PATH}")

        # Verify the initialization
        if verify_db():
            print("Database verification passed.")
        else:
            print("Database verification failed!")
    else:
        print("Database initialization failed!")
