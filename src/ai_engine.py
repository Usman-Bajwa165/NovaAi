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
    "You are NOVA, an intelligent AI assistant developed by Usman Bajwa. "
    "You are professional, polite, helpful, and obedient. "
    "You respond in ONE clear, concise sentence. "
    "You focus on the user's CURRENT request and adapt to new topics naturally. "
    "You control the computer using ACTION tags: "
    "[ACTION:open_app:name] to open applications, "
    "[ACTION:search:query] to search the web, "
    "[ACTION:open_website:url] to open websites, "
    "[ACTION:install:name] to help install apps, "
    "[ACTION:uninstall:name] to help uninstall apps. "
    "IMPORTANT: Only claim you performed an action if you actually used an ACTION tag. "
    "Be direct, humble, and extremely helpful. No unnecessary talk."
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
            success, msg = execute_system_command("search", search_query)
            text = (
                f"I am opening Chrome and searching for {search_query} in separate tabs."
                if success
                else "I tried to open Chrome search tabs but something failed."
            )
            return True, text, {
                "type": "search",
                "target": search_query,
                "success": success,
            }
        except Exception as e:
            logger.error("Local chrome+search logic failed: %s", e)

    # General "search for X" handling anywhere in the sentence
    search_match = re.search(r"\bsearch(?: for)?\s+(.+)", cmd)
    if search_match:
        search_query = search_match.group(1).strip()
        success, msg = execute_system_command("search", search_query)
        text = (
            f"I am searching for {search_query} in your browser."
            if success
            else "I could not open the search results."
        )
        return True, text, {
            "type": "search",
            "target": search_query,
            "success": success,
        }

    # Weather / temperature queries -> open browser weather info
    if any(word in cmd for word in ["weather", "temperature"]):
        location = None
        if " in " in cmd:
            # Use the part after 'in' from the original text to preserve casing
            location = user_input.split(" in ", 1)[1].strip()
        if not location:
            location = "your location"
        query = f"weather in {location}"
        success, msg = execute_system_command("search", query)
        text = (
            f"I have opened the weather for {location} in your browser."
            if success
            else "I could not open the weather information."
        )
        return True, text, {
            "type": "search",
            "target": query,
            "success": success,
        }

    # Simple "open X" app launching (match anywhere, take last occurrence)
    open_matches = list(re.finditer(r"\b(?:open|launch|start)\s+([a-zA-Z0-9 ._-]+)", cmd))
    if open_matches:
        app_phrase = open_matches[-1].group(1).strip()
        app_name = app_phrase.split(" and ")[0].strip()
        success, msg = execute_system_command("open_app", app_name)
        text = msg
        return True, text, {
            "type": "open_app",
            "target": app_name,
            "success": success,
        }

    # Time/date shortcuts: only for short direct questions, not for long complaints
    if any(word in cmd for word in ["time", "date", "today"]) and not any(
        w in cmd for w in ["weather", "temperature"]
    ):
        if len(cmd.split()) <= 8:
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
            options={
                "temperature": 0.4,
                "num_predict": 60,
                "top_p": 0.9,
                "repeat_penalty": 1.2
            },
        )
        return resp["response"].strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "I apologize, but I cannot respond at the moment. Please try again."


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

    # 2. Build Context (only last 2 messages for better context)
    history = get_memory(user_id, limit=2)
    context = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    full_prompt = f"{SYSTEM_PROMPT}\n\nRecent context:\n{context}\n\nUser: {user_input}\nNOVA:"

    # 3. Call Ollama
    ai_text = _call_ollama(full_prompt)

    # Clean up response - remove any self-generated conversation
    lines = ai_text.split("\n")
    clean_lines = []
    for line in lines:
        line_lower = line.lower()
        if any(x in line_lower for x in ["user:", "assistant:", "nova:", "human:"]):
            break
        clean_lines.append(line)
    ai_text = " ".join(clean_lines).strip()

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
