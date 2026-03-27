import os
import subprocess
from typing import List, Dict
from memory.long_memory import get_usage_score

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

EXCLUDED_DIR_NAMES = {
    "$recycle.bin",
    "system volume information",
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    ".venv"
}

ALLOWED_EXTENSIONS = {
    ".txt", ".py", ".docx", ".pdf", ".jpg", ".png",
    ".jpeg", ".mp4", ".mp3", ".json", ".csv"
}


def should_skip_dir(dir_name: str) -> bool:
    return dir_name.lower() in EXCLUDED_DIR_NAMES


def get_result_score(query: str, name: str, path: str, item_type: str) -> int:
    score = 0
    query = query.lower().strip()
    name_lower = name.lower()
    path_lower = path.lower()

    # Exact name match
    if name_lower == query:
        score += 120

    # Name starts with query
    if name_lower.startswith(query):
        score += 80

    # Query appears in name
    if query in name_lower:
        score += 50

    # Desktop priority
    if path_lower.startswith(DESKTOP_PATH.lower()):
        score += 100

    # Prefer folders slightly for broad searches
    if item_type == "folder":
        score += 15

    # Prefer useful file extensions
    ext = os.path.splitext(name_lower)[1]
    if ext in {".py", ".txt", ".docx", ".pdf", ".json"}:
        score += 20

    # Penalize deep messy paths a bit
    depth = path.count("\\")
    score -= depth
    # 🔥 Boost frequently used items
    usage = get_usage_score(path)
    score += usage * 40

    return score

def search_files(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    query = query.lower().strip()
    results = []

    if not query:
        return results

    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            try:
                folder_name_actual = os.path.basename(root)
                folder_name_lower = folder_name_actual.lower()

                if query in folder_name_lower:
                    results.append({
                        "name": folder_name_actual,
                        "path": root,
                        "type": "folder",
                        "score": get_result_score(query, folder_name_actual, root, "folder")
                    })

                for file_name in files:
                    ext = os.path.splitext(file_name)[1].lower()

                    # Skip useless system files
                    if ext and ext not in ALLOWED_EXTENSIONS:
                        continue

                    if query in file_name.lower():
                        full_path = os.path.join(root, file_name)
                        results.append({
                            "name": file_name,
                            "path": full_path,
                            "type": "file",
                            "score": get_result_score(query, file_name, full_path, "file")
                        })

            except Exception:
                continue

    # Sort first
    results.sort(key=lambda item: item["score"], reverse=True)

    # Remove duplicates by name (keep best scored)
    seen = set()
    unique_results = []

    for item in results:
        name_key = item["name"].lower()

        if name_key not in seen:
            seen.add(name_key)
            unique_results.append(item)

    # Return top unique results
    return unique_results[:max_results]


def open_path(path: str) -> str:
    try:
        os.startfile(path)
        name = os.path.basename(path.rstrip("\\/"))
        return f"Opening {name}."
    except Exception as e:
        return f"I found it, but couldn't open it: {e}"


def extract_search_query(user_input: str) -> str:
    text = user_input.strip()

    removable_phrases = [
        "find file",
        "find folder",
        "find",
        "search for",
        "search",
        "open file",
        "open folder",
        "open"
    ]

    lowered = text.lower()
    for phrase in removable_phrases:
        if lowered.startswith(phrase):
            return text[len(phrase):].strip()

    return text