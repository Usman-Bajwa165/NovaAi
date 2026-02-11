"""Authentication module for user management."""

import re
import bcrypt
from .database import get_db
from .logger import logger


def is_valid_email(email):
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        # bcrypt requires bytes
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Password hashing error: {e}", exc_info=True)
        raise


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        result = bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )
        logger.debug(f"Password verification: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}", exc_info=True)
        return False


def signup_user(email: str, password: str):
    """Create a new user account."""
    # Input validation
    if not email or not password:
        logger.warning("Signup attempted with empty email or password")
        return {"success": False, "message": "Email and password are required."}

    # Email validation
    if not is_valid_email(email):
        logger.warning(f"Signup attempted with invalid email: {email}")
        return {"success": False, "message": "Please enter a valid email address."}

    # Password validation
    if len(password) < 7:
        logger.warning("Signup attempted with short password")
        return {
            "success": False,
            "message": "Password must be at least 7 characters long.",
        }

    # Additional password strength checks
    if len(password) > 128:
        logger.warning("Signup attempted with too long password")
        return {
            "success": False,
            "message": "Password must be less than 128 characters.",
        }

    try:
        hashed = hash_password(password)

        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, hashed),
            )
            conn.commit()

        logger.info(f"User created successfully: {email}")
        return {"success": True, "message": "Signup successful."}

    except Exception as e:
        error_msg = str(e)

        if "UNIQUE constraint failed" in error_msg:
            logger.warning(f"Signup failed - email already exists: {email}")
            return {
                "success": False,
                "message": "Account already exists with this email.",
            }

        logger.error(f"Signup error for {email}: {e}", exc_info=True)
        return {"success": False, "message": "Signup failed. Please try again."}


def login_user(email: str, password: str):
    """Authenticate a user."""
    # Input validation
    if not email or not password:
        logger.warning("Login attempted with empty email or password")
        return {"success": False, "message": "Email and password are required."}

    # Email validation
    if not is_valid_email(email):
        logger.warning(f"Login attempted with invalid email: {email}")
        return {"success": False, "message": "Please enter a valid email address."}

    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

        if user and verify_password(password, user["password_hash"]):
            logger.info(f"Login successful: {email}")
            return {"success": True, "user_id": user["id"], "email": user["email"]}
        else:
            if not user:
                logger.warning(f"Login failed - user not found: {email}")
                return {
                    "success": False,
                    "message": "No account found. Please sign up.",
                    "needs_signup": True,
                }

            logger.warning(f"Login failed - invalid password: {email}")
            return {"success": False, "message": "Invalid password."}

    except Exception as e:
        logger.error(f"Login error for {email}: {e}", exc_info=True)
        return {"success": False, "message": "Login failed. Please try again."}


# Future enhancements:
# - Password reset functionality
# - Rate limiting for failed login attempts
# - Two-factor authentication
# - Session management with tokens
# - Password strength meter
