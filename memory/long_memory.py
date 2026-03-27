import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")


def load_long_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"usage": {}}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "usage" not in data:
                data["usage"] = {}
            return data
    except Exception:
        return {"usage": {}}


def save_long_memory(data: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def increase_usage(path: str):
    data = load_long_memory()

    if path not in data["usage"]:
        data["usage"][path] = 0

    data["usage"][path] += 1

    save_long_memory(data)


def get_usage_score(path: str) -> int:
    data = load_long_memory()
    return data["usage"].get(path, 0)

def get_top_used_paths(limit: int = 5):
    data = load_long_memory()
    usage = data.get("usage", {})

    sorted_items = sorted(
        usage.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return sorted_items[:limit]