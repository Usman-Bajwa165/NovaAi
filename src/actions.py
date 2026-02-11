"""System actions module for executing commands."""

import os
import subprocess
import platform
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
            # Common applications mapping
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
            }

            executable = app_mapping.get(app_name)

            if executable:
                try:
                    if executable.endswith(".cmd"):
                        # For VS Code and similar
                        subprocess.Popen([executable], shell=True)
                    elif "explorer" in executable:
                        # For File Explorer
                        os.startfile(executable)
                    else:
                        # For most apps
                        os.startfile(executable)

                    logger.info(f"Successfully launched: {executable}")
                    return True, f"Opening {app_name}, sir."
                except (OSError, IOError) as e:
                    logger.error(f"Failed to launch {executable}: {e}")
                    return False, f"I couldn't find {app_name} on your system."
            else:
                # Try generic start for other apps
                try:
                    subprocess.Popen(f"start {app_name}", shell=True)
                    logger.info(f"Attempted generic launch: {app_name}")
                    return True, f"Attempting to open {app_name}."
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


def execute_system_command(command_type, target=None):
    """Central dispatcher for system actions."""
    if not command_type:
        logger.warning("execute_system_command called with no command_type")
        return False, "Invalid command."

    logger.debug(f"Executing command: {command_type} with target: {target}")

    if command_type == "open_app" and target:
        return open_app(target)

    logger.warning(f"Unknown command type: {command_type}")
    return False, "I cannot perform that action yet."


# Future expansion points:
# - file_action (create, delete, move files)
# - search_web (open browser with search)
# - system_control (shutdown, restart, sleep)
# - media_control (play, pause, volume)
