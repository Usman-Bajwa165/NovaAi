"""AI engine module for Jarvis-style reasoning and actions."""

import os
import re
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIError
from src.database import get_db
from src.actions import execute_system_command
from src.logger import logger

load_dotenv()

# -----------------
# OpenAI primary
# -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except APIError:
        logger.error("Failed to initialize OpenAI client", exc_info=True)
else:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# -----------------
# Gemini fallback initialization (try new google.genai then legacy google.generativeai)
# -----------------
GEMINI_AVAILABLE = False
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai = None
_genai_type = None  # "new" for google.genai, "legacy" for google.generativeai

if GEMINI_API_KEY:
    try:
        # Try the new package first
        import google.genai as genai_new  # type: ignore

        genai = genai_new
        _genai_type = "new"
        # Some new clients need explicit client creation; we'll try configuring below if needed
        # (we won't crash here; actual call logic will adapt)
        GEMINI_AVAILABLE = True
        logger.info("Detected google.genai (new) package for Gemini fallback")
    except Exception:
        try:
            # Fallback to legacy package if available
            import google.generativeai as genai_legacy  # type: ignore

            genai = genai_legacy
            _genai_type = "legacy"
            # The legacy package typically uses genai.configure(api_key=...)
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                GEMINI_AVAILABLE = True
                logger.info(
                    "Detected legacy google.generativeai package and configured it"
                )
            except Exception:
                GEMINI_AVAILABLE = False
                logger.warning(
                    "Legacy google.generativeai present but configuration failed",
                    exc_info=True,
                )
        except Exception:
            GEMINI_AVAILABLE = False
            logger.info(
                "No google.genai / google.generativeai package available for Gemini fallback"
            )
else:
    logger.info("GEMINI_API_KEY not set; skipping Gemini fallback setup")

# -----------------
# Prompts & regex
# -----------------
SYSTEM_PROMPT = (
    "You are JARVIS, a professional, intelligent, and loyal AI voice agent. "
    "You respond concisely because your responses are spoken aloud. "
    "You understand user context and remember previous conversations.\n\n"
    "ACTIONS:\nIf the user asks to perform a system action, include a tag exactly like: [ACTION:open_app:chrome]\n"
)

_ACTION_RE = re.compile(r"\[ACTION:([a-zA-Z0-9_]+):([^\]]+)\]")


# -----------------
# Memory helpers
# -----------------
def get_memory(user_id, limit=5):
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT role, content FROM memory WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
    except Exception:
        logger.error("Memory fetch failed", exc_info=True)
        return []


def save_memory(user_id, role, content):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
            conn.commit()
        prune_memory(user_id, keep_last=200)
    except Exception:
        logger.error("Memory save failed", exc_info=True)


def prune_memory(user_id, keep_last=200):
    try:
        with get_db() as conn:
            conn.execute(
                """
                DELETE FROM memory
                WHERE id NOT IN (
                  SELECT id FROM memory
                  WHERE user_id = ?
                  ORDER BY timestamp DESC
                  LIMIT ?
                ) AND user_id = ?
                """,
                (user_id, keep_last, user_id),
            )
            conn.commit()
    except Exception:
        logger.warning("Memory pruning issue", exc_info=True)


# -----------------
# Local simple command parser (works offline)
# -----------------
_OPEN_CMD_RE = re.compile(r"^(?:open|launch|start)\s+(.+)$", re.IGNORECASE)
_TIME_RE = re.compile(r"\btime\b|\bwhat time\b", re.IGNORECASE)
_DATE_RE = re.compile(r"\bdate\b|\btoday\b", re.IGNORECASE)


def try_local_commands(user_input):
    """Handle very simple local actions without LLM. Returns (handled_bool, result_text, action_dict|None)."""
    if not isinstance(user_input, str):
        return False, None, None

    trimmed = user_input.strip()

    # Open app pattern
    m = _OPEN_CMD_RE.match(trimmed)
    if m:
        app_name = m.group(1).strip().lower()
        success, msg = execute_system_command("open_app", app_name)
        text = (
            f"Opening {app_name}." if success else f"I couldn't open {app_name}. {msg}"
        )
        action = {"type": "open_app", "target": app_name, "success": success}
        return True, text, action

    # Time query
    if _TIME_RE.search(trimmed):
        import datetime

        now = datetime.datetime.now()
        text = f"The time is {now.strftime('%I:%M %p')}."
        return True, text, None

    # Date query
    if _DATE_RE.search(trimmed):
        import datetime

        today = datetime.date.today()
        text = f"Today is {today.strftime('%A, %B %d, %Y')}."
        return True, text, None

    return False, None, None


# -----------------
# Model callers
# -----------------
def _build_prompt_text(system_prompt, history, user_input):
    parts = [f"SYSTEM: {system_prompt.strip()}"]
    for h in history:
        parts.append(f"{h.get('role','user').upper()}: {h.get('content','').strip()}")
    parts.append(f"USER: {user_input.strip()}")
    parts.append("JARVIS:")
    return "\n".join(parts)


def _call_openai(prompt_text):
    if not openai_client:
        raise RuntimeError("OpenAI client not configured")
    try:
        resp = openai_client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=prompt_text,
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.35")),
        )
        # prefer output_text if available
        if hasattr(resp, "output_text") and resp.output_text:
            return str(resp.output_text).strip()
        # else try to parse
        try:
            return str(resp.choices[0].message.content).strip()
        except Exception:
            return str(getattr(resp, "text", "")).strip()
    except RateLimitError:
        # re-raise to be handled by caller
        logger.warning("OpenAI rate limit / quota error", exc_info=True)
        raise
    except APIError:
        logger.error("OpenAI call error", exc_info=True)
        raise


def _call_gemini(prompt_text):
    """Call whichever genai module is available (new google.genai or legacy google.generativeai)."""
    if not GEMINI_AVAILABLE or genai is None:
        raise RuntimeError("Gemini client not available")
    try:
        # New google.genai (best-effort handling)
        if _genai_type == "new":
            try:
                # some versions provide a Client class
                if hasattr(genai, "Client"):
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    # assume method generate_text or generate
                    if hasattr(client, "generate_text"):
                        resp = client.generate_text(
                            model=GEMINI_MODEL, prompt=prompt_text
                        )
                        # try to extract text fields
                        return (
                            getattr(resp, "text", "")
                            or getattr(resp, "output_text", "")
                            or str(resp)
                        )
                    if hasattr(client, "generate"):
                        resp = client.generate(model=GEMINI_MODEL, input=prompt_text)
                        return getattr(resp, "text", "") or str(resp)
                # fallback to top-level generate functions
                if hasattr(genai, "generate_text"):
                    resp = genai.generate_text(model=GEMINI_MODEL, prompt=prompt_text)
                    return getattr(resp, "text", "") or str(resp)
                if hasattr(genai, "generate"):
                    resp = genai.generate(model=GEMINI_MODEL, input=prompt_text)
                    # new API might put output in resp.output[0].content or similar
                    return (
                        getattr(resp, "text", "")
                        or getattr(resp, "output_text", "")
                        or str(resp)
                    )
            except Exception:
                logger.info(
                    "google.genai path failed, will try legacy if available",
                    exc_info=True,
                )

        # Legacy google.generativeai interface (best-effort)
        if _genai_type == "legacy":
            if hasattr(genai, "GenerativeModel"):
                model = genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content(prompt_text)
                txt = getattr(response, "text", None) or getattr(
                    response, "content", None
                )
                return (txt or "").strip()
            # some legacy variants expose generate_text
            if hasattr(genai, "generate_text"):
                response = genai.generate_text(model=GEMINI_MODEL, prompt=prompt_text)
                return getattr(response, "text", "") or str(response)

        # If none of the above matched, raise
        raise RuntimeError(
            "No compatible Gemini call path available for installed genai package"
        )
    except Exception:
        logger.error("Gemini call failed", exc_info=True)
        raise


# -----------------
# Public API
# -----------------
def generate_response(user_id, user_input):
    # Basic validation
    if not user_id:
        return {"text": "Authentication error. Please log in again.", "action": None}
    if not user_input or not isinstance(user_input, str):
        return {"text": "I didn't catch that. Please repeat.", "action": None}
    if len(user_input) > 2000:
        return {"text": "Please keep your request shorter.", "action": None}

    # 1) Try local commands first (so offline actions work)
    handled, local_text, local_action = try_local_commands(user_input)
    if handled:
        save_memory(user_id, "user", user_input)
        save_memory(user_id, "assistant", local_text)
        return {"text": local_text, "action": local_action}

    # 2) Build prompt
    history = get_memory(user_id)
    prompt_text = _build_prompt_text(SYSTEM_PROMPT, history, user_input)

    ai_text = None

    # 3) Try OpenAI -> if RateLimitError or other failure, attempt Gemini if available
    try:
        ai_text = _call_openai(prompt_text)
        logger.info("OpenAI responded successfully")
    except RateLimitError:
        logger.warning(
            "OpenAI RateLimit/Quota hit. See OpenAI dashboard for usage and billing."
        )
        # Try Gemini next (if available)
        if GEMINI_AVAILABLE:
            try:
                ai_text = _call_gemini(prompt_text)
                logger.info(
                    "Gemini fallback responded successfully (after OpenAI rate limit)"
                )
            except Exception:
                logger.error(
                    "Gemini fallback after OpenAI quota also failed", exc_info=True
                )
                return {
                    "text": (
                        "Both cloud intelligence engines are currently unavailable "
                        "— please check OpenAI billing/quota and Gemini configuration. "
                        "I can still perform simple local actions if you ask (e.g., 'open chrome')."
                    ),
                    "action": None,
                }
        else:
            return {
                "text": (
                    "OpenAI quota exceeded. Please check your OpenAI account usage/billing. "
                    "I can still perform simple local actions if you ask (e.g., 'open chrome')."
                ),
                "action": None,
            }
    except APIError:
        logger.warning(
            "OpenAI call failed, attempting Gemini (if available)", exc_info=True
        )
        if GEMINI_AVAILABLE:
            try:
                ai_text = _call_gemini(prompt_text)
                logger.info(
                    "Gemini fallback responded successfully (after OpenAI error)"
                )
            except Exception:
                logger.error("Gemini fallback failed", exc_info=True)
                return {
                    "text": (
                        "I couldn't reach my intelligence engines right now. "
                        "Please check API keys/configuration. I can still perform simple local actions."
                    ),
                    "action": None,
                }
        else:
            return {
                "text": (
                    "My intelligence core is offline. Please check your API configuration."
                ),
                "action": None,
            }

    if not ai_text:
        return {"text": "I couldn't generate a response. Try again.", "action": None}

    # 4) Parse and execute action if present
    action_match = _ACTION_RE.search(ai_text)
    action_result = None
    if action_match:
        try:
            action_type = action_match.group(1)
            action_target = action_match.group(2).strip()
            success, msg = execute_system_command(action_type, action_target)
            ai_text = _ACTION_RE.sub("", ai_text).strip()
            if not success:
                ai_text = f"{ai_text} (Note: {msg})"
            action_result = {
                "type": action_type,
                "target": action_target,
                "success": success,
            }
            logger.info(
                f"Action executed: {action_type}:{action_target} success={success}"
            )
        except Exception:
            logger.exception("Action execution error")

    # 5) Save memory
    save_memory(user_id, "user", user_input)
    save_memory(user_id, "assistant", ai_text)

    return {"text": ai_text, "action": action_result}


def list_gemini_models():
    """If a Gemini client is installed & configured, attempt to list available models."""
    if not GEMINI_AVAILABLE or genai is None:
        return []
    try:
        # try new client listing
        if _genai_type == "new" and hasattr(genai, "Client"):
            client = genai.Client(api_key=GEMINI_API_KEY)
            if hasattr(client, "list_models"):
                return client.list_models()
        # legacy listing
        if _genai_type == "legacy" and hasattr(genai, "list_models"):
            return genai.list_models()
    except Exception:
        logger.error("Failed to list Gemini models", exc_info=True)
    return []
