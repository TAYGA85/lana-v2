import os
import subprocess


APP_MAP = {
    "chrome": [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ],
    "opera": [
        "C:\\Users\\arenh\\AppData\\Local\\Programs\\Opera\\launcher.exe",
        "C:\\Users\\arenh\\AppData\\Local\\Programs\\Opera GX\\launcher.exe",
    ],
    "notepad": [
        "notepad.exe",
    ],
    "vscode": [
        "code",
        "Code.exe",
    ],
}


def _try_open_target(target: str) -> bool:
    try:
        subprocess.Popen(target)
        return True
    except Exception:
        return False


def open_app(app_name: str) -> str:
    app_name = app_name.lower().strip()

    if app_name not in APP_MAP:
        return f"I don't know how to open {app_name} yet."

    for target in APP_MAP[app_name]:
        if os.path.isabs(target):
            if os.path.exists(target) and _try_open_target(target):
                return f"Opening {app_name}."
        else:
            if _try_open_target(target):
                return f"Opening {app_name}."

    return f"I couldn't open {app_name}."