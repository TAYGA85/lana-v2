import os
from memory.long_memory import get_top_used_paths, get_usage_score


def make_plan(intent: str, user_input: str) -> dict:
    text = user_input.lower().strip()

    return {
        "intent": intent,
        "input": user_input,
        "normalized_input": text,
        "asks_for_main_file": "main" in text or "entry" in text,
        "asks_for_folder": "folder" in text or "project" in text,
        "asks_for_file": "file" in text or ".py" in text or ".txt" in text,
    }


def _matches_text(text: str, name_lower: str) -> bool:
    if not text:
        return False

    if text == name_lower:
        return True

    if text in name_lower:
        return True

    if name_lower in text:
        return True

    words = [word for word in text.split() if len(word) >= 3]
    return any(word in name_lower for word in words)


def get_smart_suggestion(user_input: str, session) -> tuple[str | None, dict | None]:
    text = user_input.lower().strip()

    prefer_folder = "folder" in text or "project" in text
    prefer_file = "file" in text or ".py" in text or ".txt" in text
    prefer_main = "main" in text or "entry" in text

    top_used = get_top_used_paths(limit=10)

    best_match = None
    best_score = -1

    for path, count in top_used:
        name = os.path.basename(path)
        name_lower = name.lower()

        if count < 2:
            continue

        is_file = os.path.isfile(path)
        is_folder = os.path.isdir(path)

        if prefer_folder and not is_folder:
            continue

        if prefer_file and not is_file:
            continue

        if prefer_main and is_file:
            if name_lower not in {"main.py", "app.py", "index.py", "start.py"} and not any(
                key in name_lower for key in ["main", "app", "index", "start"]
            ):
                continue

        if not _matches_text(text, name_lower):
            continue

        score = count

        if prefer_main and name_lower == "main.py":
            score += 5
        elif prefer_main and name_lower in {"app.py", "index.py", "start.py"}:
            score += 3

        if is_folder and prefer_folder:
            score += 2

        if is_file and prefer_file:
            score += 2

        if score > best_score:
            best_score = score
            best_match = {
                "type": "open_path",
                "path": path,
                "name": name,
                "item_type": "folder" if is_folder else "file"
            }

    if best_match:
        return (
            f"You usually open {best_match['name']}. Want me to open it?",
            best_match
        )

    if session.has_references():
        current_project = session.get_current_project()

        if current_project:
            for item in session.last_reference_list:
                if item["type"] == "folder" and current_project.lower() in item["name"].lower():
                    return (
                        f"I found {item['name']} again. Want me to open it?",
                        {
                            "type": "open_path",
                            "path": item["path"],
                            "name": item["name"],
                            "item_type": item["type"]
                        }
                    )

    return None, None