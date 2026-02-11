"""Main application entry point for NOVA."""

import os
import sys
import json
import threading
import webview
from dotenv import load_dotenv
from src.auth import login_user, signup_user
from src.ai_engine import generate_response
from src.voice_engine import listen, speak

load_dotenv()

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")


class API:
    """API class for handling frontend-backend communication."""

    def __init__(self):
        self.user_id = None
        self.email = None
        self.name = None
        self.is_scanning = False
        self._load_session()

    def _load_session(self):
        """Load saved session on startup."""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_id = data.get("user_id")
                    self.email = data.get("email")
                    self.name = data.get("name")
            except Exception:
                pass

    def _save_session(self):
        """Save session to file."""
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"user_id": self.user_id, "email": self.email, "name": self.name},
                    f,
                )
        except Exception:
            pass

    def _clear_session(self):
        """Clear saved session."""
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception:
            pass

    def get_session(self):
        """Return current session for auto-login."""
        if self.user_id and self.email:
            return {
                "success": True,
                "user_id": self.user_id,
                "email": self.email,
                "name": self.name,
            }
        return {"success": False}

    def login(self, email, password):
        """Handle user login."""
        try:
            res = login_user(email, password)
            if res["success"]:
                self.user_id = res["user_id"]
                self.email = res["email"]
                self.name = res.get("name")
                self._save_session()

                # Choose a friendly display name (prefer stored name, otherwise email without digits)
                raw_id = self.name or self.email.split("@")[0]
                clean_id = "".join(ch for ch in raw_id if not ch.isdigit())
                clean_id = clean_id or raw_id

                threading.Thread(
                    target=speak,
                    args=(f"Authorization confirmed. Welcome back, {clean_id}",),
                ).start()
            return res
        except (ValueError, TypeError, KeyError) as e:
            return {"success": False, "message": f"Encryption Error: {str(e)}"}

    def signup(self, name, email, password):
        """Handle user signup."""
        try:
            return signup_user(name, email, password)
        except (ValueError, TypeError, KeyError) as e:
            return {"success": False, "message": f"Encryption Error: {str(e)}"}

    def logout(self):
        """Handle user logout and clear session."""
        self.user_id = None
        self.email = None
        self._clear_session()
        return {"success": True}

    def verify_session(self, user_id, email):
        """Verify user session."""
        try:
            from src.database import get_db

            with get_db() as conn:
                user = conn.execute(
                    "SELECT id, email FROM users WHERE id = ? AND email = ?",
                    (user_id, email),
                ).fetchone()
            if user:
                self.user_id = user["id"]
                self.email = user["email"]
                return {"success": True}
            return {"success": False}
        except (ValueError, TypeError, KeyError) as e:
            return {"success": False, "message": str(e)}

    def start_voice_session(self):
        """Start a voice interaction session."""
        try:
            if not self.user_id:
                return {"status": "error", "message": "Not authenticated"}

            # Return listening status
            result = {"status": "listening"}

            user_input = listen()

            if user_input == "READY_STATUS":
                return {"status": "calibrating"}

            if user_input:
                result = {"status": "thinking", "user_input": user_input}

                ai_result = generate_response(self.user_id, user_input)
                ai_response = ai_result["text"]
                action = ai_result["action"]

                result = {
                    "status": "responding",
                    "user_input": user_input,
                    "ai_response": ai_response,
                    "action": action,
                }

                threading.Thread(target=speak, args=(ai_response,)).start()
                return result

            return {"status": "idle"}
        except Exception as e:
            print(f"Voice Session Error: {e}")
            return {"status": "error", "message": str(e)}


def start_reloader():
    """Watch for file changes and reload the application."""
    files_to_watch = [__file__]
    src_dir = os.path.join(os.path.dirname(__file__), "src")
    ui_dir = os.path.join(os.path.dirname(__file__), "ui")

    if os.path.exists(src_dir):
        for root, _, files in os.walk(src_dir):
            for f in files:
                if f.endswith(".py"):
                    files_to_watch.append(os.path.join(root, f))
    if os.path.exists(ui_dir):
        for root, _, files in os.walk(ui_dir):
            for f in files:
                if f.endswith((".html", ".css", ".js")):
                    files_to_watch.append(os.path.join(root, f))

    mtimes = {f: os.path.getmtime(f) for f in files_to_watch if os.path.exists(f)}

    while True:
        threading.Event().wait(1)
        for f in files_to_watch:
            if not os.path.exists(f):
                continue
            current_mtime = os.path.getmtime(f)
            if current_mtime > mtimes.get(f, 0):
                print(
                    f"\n>>> [RELOADER] Change detected in {os.path.basename(f)}. Restarting..."
                )
                os.execv(sys.executable, ["python"] + sys.argv)


def start_app():
    """Initialize and start the application."""
    api = API()
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")

    threading.Thread(target=start_reloader, daemon=True).start()

    webview.create_window(
        "NOVA - Neural Voice Interface",
        url=ui_path,
        js_api=api,
        width=1100,
        height=850,
        background_color="#02050a",
        resizable=True,
    )
    webview.start()


if __name__ == "__main__":
    start_app()
