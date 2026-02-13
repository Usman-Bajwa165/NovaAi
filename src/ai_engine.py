"""AI engine module using Ollama for local response generation."""

import re
import datetime
from src.database import get_db
from src.actions import execute_system_command
from src.logger import logger

# --- NOVA Identity ---
NOVA_INFO = {
    "name": "NOVA",
    "developer": "Usman Bajwa",
    "version": "2.0",
    "purpose": "AI voice assistant that runs 100% locally for privacy and security",
    "features": ["voice control", "app launching", "web search", "offline AI processing"],
    "tech": "Python, Ollama (llama3.2:1b), Edge-TTS, SQLite"
}

SYSTEM_PROMPT = (
    "You are NOVA, an AI voice assistant created by Usman Bajwa. "
    "Respond in ONE concise sentence. Be helpful and direct. "
    "NEVER use ACTION tags unless the user explicitly asks you to DO something (open, search, launch). "
    "If asked about time/date/weather, say you cannot access real-time data. "
    "If asked who you are: 'I am NOVA, created by Usman Bajwa.' "
    "If asked general knowledge: provide brief factual answer. "
    "Do NOT make up information. Do NOT use ACTION tags for questions."
)

_ACTION_RE = re.compile(r"\[ACTION:([a-zA-Z0-9_]+):([^\]]+)\]")
_STOP_WORDS = {"for", "about", "this", "that", "the", "a", "an"}


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


def _clean_search_query(query):
    """Remove stop words from search query."""
    words = query.split()
    cleaned = [w for w in words if w.lower() not in _STOP_WORDS]
    return " ".join(cleaned) if cleaned else query


def _handle_nova_questions(cmd):
    """Handle questions about NOVA without using AI."""
    if any(q in cmd for q in ["who are you", "what are you", "about yourself", "who is nova", "what is nova"]):
        return True, f"I am {NOVA_INFO['name']}, an AI voice assistant created by {NOVA_INFO['developer']} that runs completely offline.", None
    
    if any(q in cmd for q in ["who made you", "who created you", "who developed you", "your developer", "your creator"]):
        return True, f"I was created by {NOVA_INFO['developer']}.", None
    
    if "your version" in cmd or "what version" in cmd:
        return True, f"I am running version {NOVA_INFO['version']}.", None
    
    if "what can you do" in cmd or "your features" in cmd or "your capabilities" in cmd:
        return True, f"I can open apps, search the web, and answer questions, all running locally on your computer.", None
    
    return False, None, None


def try_local_logic(user_input):
    """Fast path for common commands without AI."""
    raw = user_input.strip()
    cmd = raw.lower()

    # Check NOVA identity questions first
    handled, text, action = _handle_nova_questions(cmd)
    if handled:
        return True, text, action

    # Combined: open chrome and search
    if "open chrome" in cmd and "search" in cmd:
        try:
            after_search = cmd.split("search", 1)[1].strip()
            search_query = _clean_search_query(after_search)
            success, msg = execute_system_command("search", search_query)
            text = f"Searching for {search_query}." if success else "Search failed."
            return True, text, {"type": "search", "target": search_query, "success": success}
        except Exception as e:
            logger.error(f"Chrome+search failed: {e}")

    # General search
    search_match = re.search(r"\bsearch(?: for)?\s+(.+)", cmd)
    if search_match:
        raw_query = search_match.group(1).strip()
        search_query = _clean_search_query(raw_query)
        success, msg = execute_system_command("search", search_query)
        text = f"Searching for {search_query}." if success else "Search failed."
        return True, text, {"type": "search", "target": search_query, "success": success}

    # Weather queries
    if any(word in cmd for word in ["weather", "temperature"]):
        location = user_input.split(" in ", 1)[1].strip() if " in " in cmd else "your location"
        query = f"weather in {location}"
        success, msg = execute_system_command("search", query)
        text = f"Showing weather for {location}." if success else "Weather lookup failed."
        return True, text, {"type": "search", "target": query, "success": success}

    # App launching - with validation to prevent false positives
    open_matches = list(re.finditer(r"\b(?:open|launch|start)\s+([a-zA-Z0-9 ._-]+)", cmd))
    if open_matches:
        app_name = open_matches[-1].group(1).strip().split(" and ")[0].strip()
        # Filter out common false positives
        invalid_apps = {"name", "the", "a", "an", "it", "that", "this", "from", "to", "of", "in", "on", "at"}
        if app_name not in invalid_apps and len(app_name) > 2:
            success, msg = execute_system_command("open_app", app_name)
            return True, msg, {"type": "open_app", "target": app_name, "success": success}

    # Time/date queries
    if any(word in cmd for word in ["what time", "current time", "time is it", "what date", "today's date", "what day"]):
        now = datetime.datetime.now()
        parts = []
        if "time" in cmd:
            parts.append(f"the time is {now.strftime('%I:%M %p')}")
        if "date" in cmd or "day" in cmd or "today" in cmd:
            parts.append(f"today is {now.strftime('%A, %B %d, %Y')}")
        text = " and ".join(parts).capitalize() + "."
        return True, text, None

    return False, None, None


def _call_ollama(prompt):
    """Call Ollama AI model for response generation."""
    try:
        import ollama
        logger.info("Calling Ollama...")
        resp = ollama.generate(
            model="llama3.2:1b",
            prompt=prompt,
            options={"temperature": 0.4, "num_predict": 60, "top_p": 0.9, "repeat_penalty": 1.2},
        )
        return resp["response"].strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "I cannot respond right now. Please try again."


def generate_response(user_id, user_input):
    """Generate AI response with local bypass optimization."""
    if not user_id:
        return {"text": "Authentication error.", "action": None}

    # Fast path: local logic bypass
    handled, local_text, local_action = try_local_logic(user_input)
    if handled:
        save_memory(user_id, "user", user_input)
        save_memory(user_id, "assistant", local_text)
        return {"text": local_text, "action": local_action}

    # AI path: build context and call Ollama
    history = get_memory(user_id, limit=2)
    context = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    full_prompt = f"{SYSTEM_PROMPT}\n\nRecent context:\n{context}\n\nUser: {user_input}\nNOVA:"
    
    ai_text = _call_ollama(full_prompt)
    
    # Clean response
    lines = ai_text.split("\n")
    clean_lines = []
    for line in lines:
        if any(x in line.lower() for x in ["user:", "assistant:", "nova:", "human:"]):
            break
        clean_lines.append(line)
    ai_text = " ".join(clean_lines).strip()

    # Parse and execute actions
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
