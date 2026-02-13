"""Authentication module for user management."""

import re
import bcrypt
from .database import get_db


def is_valid_email(email):
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def signup_user(name: str, email: str, password: str):
    """Create a new user account."""
    if not name or not email or not password:
        return {
            "success": False,
            "message": "Name, email and password are all required.",
        }

    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address."}

    if len(password) < 7:
        return {
            "success": False,
            "message": "Password must be at least 7 characters long.",
        }

    try:
        hashed = hash_password(password)

        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name.strip(), email, hashed),
            )
            conn.commit()

        return {"success": True, "message": "Signup successful."}

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return {
                "success": False,
                "message": "Account already exists with this email.",
            }
        return {"success": False, "message": "Signup failed. Please try again."}


def login_user(email: str, password: str):
    """Authenticate a user."""
    if not email or not password:
        return {"success": False, "message": "Email and password are required."}

    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address."}

    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

        if user and verify_password(password, user["password_hash"]):
            return {
                "success": True,
                "user_id": user["id"],
                "email": user["email"],
                "name": user["name"] if "name" in user.keys() else None,
            }
        
        if not user:
            return {
                "success": False,
                "message": "No account found. Please sign up.",
                "needs_signup": True,
            }

        return {"success": False, "message": "Invalid password."}

    except Exception:
        return {"success": False, "message": "Login failed. Please try again."}
