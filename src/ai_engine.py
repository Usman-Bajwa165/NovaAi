"""AI engine module using Ollama for local response generation."""

import os
import re
import datetime
from dotenv import load_dotenv
from src.database import get_db
from src.actions import execute_system_command
from src.logger import logger

load_dotenv()

# --- Prompting & Regex ---
SYSTEM_PROMPT = (
    "You are NOVA. Respond in ONE short, clear sentence only. "
    "You are developed by Usman Bajwa and must be professional, polite, and very obedient. "
    "You carefully read the latest user message and focus on their current request, "
    "even if it is a new topic. Do not force the conversation to stay on previous topics. "
    "You control the local machine using special ACTION tags. "
    "To open an app use: [ACTION:open_app:app_name]. "
    "To search the web use: [ACTION:search:query]. "
    "Queries with multiple words (e.g. 'pak army') should be passed exactly as the user said. "
    "If user wants to uninstall, use: [ACTION:uninstall:app_name]. "
    "If user wants to install, use: [ACTION:install:app_name]. "
    "If user wants to open website, use: [ACTION:open_website:website_name]. "
    "Always be direct, helpful, humble and super polite, with no unnecessary small talk."
)

_ACTION_RE = re.compile(r"\[ACTION:([a-zA-Z0-9_]+):([^\]]+)\]")
_LOCAL_OPEN_RE = re.compile(r"^(?:open|launch|start)\s+(.+)$", re.IGNORECASE)


# --- Memory Logic ---
def get_memory(user_id, limit=3):
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT role, content FROM memory WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
    except Exception as e:
        logger.error(f"Memory fetch failed: {e}")
        return []


def save_memory(user_id, role, content):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Memory save failed: {e}")


# --- Local Command Bypass ---
def try_local_logic(user_input):
    raw = user_input.strip()
    cmd = raw.lower()

    # Combined intent: "open chrome and search pak army"
    if "open chrome" in cmd and "search" in cmd:
        try:
            # Everything after the word "search" is treated as the query
            after_search = cmd.split("search", 1)[1].strip()
            search_query = after_search or raw  # fall back to original text
            # Open Chrome (or default browser) and search each term in separate tabs
            success, msg = execute_system_command("search", search_query)
            text = (
                f"I am opening Chrome and searching for {search_query}."
                if success
                else "I tried to open Chrome search tabs but something failed."
            )
            return True, text, {
                "type": "search",
                "target": search_query,
                "success": success,
            }
        except Exception as e:
            logger.error(f"Local chrome+search logic failed: {e}")

    # Simple "open X" app launching
    match = _LOCAL_OPEN_RE.match(cmd)
    if match:
        app_name = match.group(1).strip()
        success, msg = execute_system_command("open_app", app_name)
        text = f"Opening {app_name}." if success else f"Cannot find {app_name}."
        return True, text, {"type": "open_app", "target": app_name, "success": success}

    if any(word in cmd for word in ["time", "date", "today"]):
        now = datetime.datetime.now()
        text = f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}."
        return True, text, None

    return False, None, None


# --- Ollama Caller ---
def _call_ollama(prompt):
    try:
        import ollama

        logger.info("Calling Ollama...")
        resp = ollama.generate(
            model="llama3.2:1b",
            prompt=prompt,
            options={"temperature": 0.3, "num_predict": 50},
        )
        return resp["response"].strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "I cannot respond right now."


# --- Main Interface ---
def generate_response(user_id, user_input):
    if not user_id:
        return {"text": "Authentication error.", "action": None}

    # 1. Try Local Bypass First
    handled, local_text, local_action = try_local_logic(user_input)
    if handled:
        save_memory(user_id, "user", user_input)
        save_memory(user_id, "assistant", local_text)
        return {"text": local_text, "action": local_action}

    # 2. Build Context (only last 1 turn so we don't get stuck on old topics)
    history = get_memory(user_id, limit=1)
    context = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    full_prompt = f"{SYSTEM_PROMPT}\n{context}\nUser: {user_input}\nNOVA:"

    # 3. Call Ollama
    ai_text = _call_ollama(full_prompt)

    # Stop if it starts generating fake conversation
    if "user:" in ai_text.lower() or "assistant:" in ai_text.lower():
        ai_text = ai_text.split("\n")[0].strip()

    # 4. Action Parsing
    action_result = None
    match = _ACTION_RE.search(ai_text)
    if match:
        act_type, act_target = match.group(1), match.group(2).strip()
        success, msg = execute_system_command(act_type, act_target)
        ai_text = _ACTION_RE.sub("", ai_text).strip()
        action_result = {"type": act_type, "target": act_target, "success": success}
        if not success:
            ai_text = f"I tried to {act_type} {act_target}, but it's not available."

    save_memory(user_id, "user", user_input)
    save_memory(user_id, "assistant", ai_text)
    return {"text": ai_text, "action": action_result}
