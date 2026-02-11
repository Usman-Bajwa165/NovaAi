"""System actions module for executing commands."""

import os
import subprocess
import platform
import webbrowser
from urllib.parse import quote_plus
from .logger import logger


def open_app(app_name):
    """Opens a system application based on the name provided."""
    if not app_name or not isinstance(app_name, str):
        logger.warning(f"Invalid app_name: {app_name}")
        return False, "Invalid application name."

    system = platform.system()
    app_name = app_name.lower().strip()

    logger.info(f"Opening application: {app_name} on {system}")

    try:
        if system == "Windows":
            # Common applications mapping (extendable)
            app_mapping = {
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "edge": "msedge.exe",
                "microsoft edge": "msedge.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "excel": "excel.exe",
                "word": "winword.exe",
                "powerpoint": "powerpnt.exe",
                "outlook": "outlook.exe",
                "vscode": "code.cmd",
                "vs code": "code.cmd",
                "visual studio code": "code.cmd",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "paint": "mspaint.exe",
                "spotify": "spotify.exe",
                "discord": "discord.exe",
                "teams": "teams.exe",
                "firefox": "firefox.exe",
                "brave": "brave.exe",
                # Extra apps requested
                "whatsapp": "WhatsApp.exe",
                "cursor": "cursor.exe",
                # SoundCloud is primarily web-based; open via browser
                "soundcloud": "https://soundcloud.com",
            }

            executable = app_mapping.get(app_name)

            if executable:
                try:
                    if executable.endswith(".cmd"):
                        # For VS Code and similar
                        subprocess.Popen([executable], shell=True)
                    elif executable.startswith("http"):
                        # Open URLs (e.g. SoundCloud) in default browser
                        os.startfile(executable)
                    elif "explorer" in executable:
                        # For File Explorer
                        os.startfile(executable)
                    else:
                        # For most apps
                        os.startfile(executable)

                    logger.info(f"Successfully launched: {executable}")
                    return True, f"Trying to open {app_name}. If it is not installed, Windows may show an error."
                except (OSError, IOError) as e:
                    logger.error(f"Failed to launch {executable}: {e}")
                    return False, f"I couldn't find {app_name} on your system."
            else:
                # Try generic start for other apps (best-effort)
                try:
                    subprocess.Popen(f"start {app_name}", shell=True)
                    logger.info(f"Attempted generic launch: {app_name}")
                    return True, (
                        f"Trying to open {app_name}. If it is not installed, Windows may show an error."
                    )
                except (OSError, IOError) as e:
                    logger.error(f"Failed generic launch for {app_name}: {e}")
                    return False, f"I couldn't find {app_name} on your system."

        elif system == "Darwin":  # macOS
            try:
                subprocess.Popen(["open", "-a", app_name])
                logger.info(f"Launched {app_name} on macOS")
                return True, f"Opening {app_name} now."
            except (OSError, IOError) as e:
                logger.error(f"Failed to launch {app_name} on macOS: {e}")
                return False, f"I couldn't find {app_name} on your system."

        elif system == "Linux":
            # Common Linux applications
            try:
                subprocess.Popen([app_name])
                logger.info(f"Launched {app_name} on Linux")
                return True, f"Opening {app_name} now."
            except (OSError, IOError) as e:
                logger.error(f"Failed to launch {app_name} on Linux: {e}")
                return False, f"I couldn't find {app_name} on your system."
        else:
            logger.warning(f"Unsupported OS: {system}")
            return (
                False,
                "I am sorry, but application control is not fully supported on this OS yet.",
            )

    except (OSError, IOError, ValueError) as e:
        logger.error(f"Unexpected error while opening {app_name}: {e}", exc_info=True)
        return (
            False,
            f"I encountered an error while trying to open {app_name}: {str(e)}",
        )


def search_web(query: str):
    """Open web search tabs for the given query (can contain multiple terms)."""
    if not query or not isinstance(query, str):
        logger.warning(f"Invalid search query: {query}")
        return False, "Invalid search query."

    # Strategy:
    # - If there are commas, treat comma-separated parts as separate searches (multi-tab)
    # - Otherwise, treat the whole string as one search phrase
    query = query.strip()
    if "," in query:
        terms = [part.strip() for part in query.split(",") if part.strip()]
    else:
        terms = [query]

    if not terms:
        return False, "Nothing to search for."

    logger.info(f"Opening search tabs for terms: {terms}")

    try:
        system = platform.system()
        success_any = False

        for term in terms:
            url = f"https://www.google.com/search?q={quote_plus(term)}"

            # Prefer system default browser for stability
            if system == "Windows":
                os.startfile(url)
            else:
                webbrowser.open_new_tab(url)

            success_any = True

        if success_any:
            return True, "Opening search results."
        return False, "Failed to open browser."
    except Exception as e:
        logger.error(f"Search error for query '{query}': {e}", exc_info=True)
        return False, "Search failed due to an internal error."


def open_website(website: str):
    """Open a website in the default browser."""
    if not website or not isinstance(website, str):
        logger.warning(f"Invalid website: {website}")
        return False, "Invalid website address."

    website = website.strip()
    # If user says things like "google" or "youtube", turn into full URL
    if not website.startswith(("http://", "https://")):
        # Heuristic: if it contains a dot, treat as domain; otherwise append .com
        if "." in website:
            url = f"https://{website}"
        else:
            url = f"https://{website}.com"
    else:
        url = website

    try:
        if platform.system() == "Windows":
            os.startfile(url)
        else:
            webbrowser.open_new_tab(url)
        logger.info(f"Opened website: {url}")
        return True, f"Opening {url} in your browser."
    except Exception as e:
        logger.error(f"Failed to open website '{website}': {e}", exc_info=True)
        return False, "I could not open that website."


def install_app(app_name: str):
    """Assist with installing an application (opens download/search page)."""
    if not app_name or not isinstance(app_name, str):
        logger.warning(f"Invalid app name for install: {app_name}")
        return False, "Invalid application name."

    app_name = app_name.strip()
    try:
        # For safety and reliability, open a browser search for downloading the app
        query = f"download {app_name} for Windows"
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        if platform.system() == "Windows":
            os.startfile(url)
        else:
            webbrowser.open_new_tab(url)
        logger.info(f"Opened install search for: {app_name}")
        return True, f"I have opened a download page so you can install {app_name}."
    except Exception as e:
        logger.error(f"Failed to assist install for '{app_name}': {e}", exc_info=True)
        return False, "I could not open the install page."


def uninstall_app(app_name: str):
    """Assist with uninstalling an application (opens Apps & Features panel)."""
    if not app_name or not isinstance(app_name, str):
        logger.warning(f"Invalid app name for uninstall: {app_name}")
        return False, "Invalid application name."

    system = platform.system()
    try:
        if system == "Windows":
            # Open Apps & Features or classic Programs and Features
            try:
                os.startfile("ms-settings:appsfeatures")
            except OSError:
                os.startfile("appwiz.cpl")
            logger.info(f"Opened uninstall panel for manual removal of: {app_name}")
            return (
                True,
                f"I opened the Windows apps panel. Please uninstall {app_name} from there.",
            )

        # Fallback for other OSes: open a help search
        query = f"uninstall {app_name} on {system}"
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        webbrowser.open_new_tab(url)
        return True, f"I opened instructions for uninstalling {app_name}."
    except Exception as e:
        logger.error(f"Failed to assist uninstall for '{app_name}': {e}", exc_info=True)
        return False, "I could not open the uninstall options."


def execute_system_command(command_type, target=None):
    """Central dispatcher for system actions."""
    if not command_type:
        logger.warning("execute_system_command called with no command_type")
        return False, "Invalid command."

    logger.debug(f"Executing command: {command_type} with target: {target}")

    if command_type == "open_app" and target:
        return open_app(target)
    if command_type == "search" and target:
        return search_web(target)
    if command_type == "open_website" and target:
        return open_website(target)
    if command_type == "install" and target:
        return install_app(target)
    if command_type == "uninstall" and target:
        return uninstall_app(target)

    logger.warning(f"Unknown command type: {command_type}")
    return False, "I cannot perform that action yet."


# Future expansion points:
# - file_action (create, delete, move files)
# - search_web (open browser with search)
# - system_control (shutdown, restart, sleep)
# - media_control (play, pause, volume)
