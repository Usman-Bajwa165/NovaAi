"""Main application entry point for JARVIS."""

import os
import sys
import threading
import webview
from dotenv import load_dotenv
from src.auth import login_user, signup_user
from src.ai_engine import generate_response
from src.voice_engine import listen, speak

load_dotenv()


class API:
    """API class for handling frontend-backend communication."""

    def __init__(self):
        self.user_id = None
        self.email = None
        self.is_scanning = False

    def login(self, email, password):
        """Handle user login."""
        try:
            res = login_user(email, password)
            if res["success"]:
                self.user_id = res["user_id"]
                self.email = res["email"]
                # Greet user
                threading.Thread(
                    target=speak,
                    args=(
                        f"Authorization confirmed. Welcome back, {self.email.split('@')[0]}",
                    ),
                ).start()
            return res
        except (ValueError, TypeError, KeyError) as e:
            return {"success": False, "message": f"Encryption Error: {str(e)}"}

    def signup(self, email, password):
        """Handle user signup."""
        try:
            return signup_user(email, password)
        except (ValueError, TypeError, KeyError) as e:
            return {"success": False, "message": f"Encryption Error: {str(e)}"}

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
                return None

            user_input = listen()

            if user_input == "READY_STATUS":
                return {"scanning": True}

            if user_input:
                result = generate_response(self.user_id, user_input)
                ai_response = result["text"]
                action = result["action"]

                threading.Thread(target=speak, args=(ai_response,)).start()

                return {
                    "user_input": user_input,
                    "ai_response": ai_response,
                    "action": action,
                }
            return None
        except (ValueError, TypeError, KeyError) as e:
            print(f"Voice Session Error: {e}")
            return None


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
        "JARVIS - Neural Voice Interface",
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
