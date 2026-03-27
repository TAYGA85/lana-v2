import re


def detect_intent(user_input: str, memory, session=None) -> dict:
    text = user_input.lower().strip()

    number_match = re.search(r"\b\d+\b", text)

    followup_words = [
        "first", "second", "third", "fourth", "fifth",
        "that", "it", "the one", "this one", "one",
        "folder", "file",
        "project", "main", "entry",
        "not the file", "not file",
        "not the folder", "not folder",
        "open"
    ]

    correction_words = [
        "another", "other one", "instead", "not that",
        "wrong one", "show again", "go back",
        "next", "previous", "above", "below",
        "last one", "used before", "usual file", "usual one",
        "refine", "refine it"
    ]

    continuity_words = [
        "continue", "what was i doing", "what was i working on",
        "go back to that", "open the project again", "resume"
    ]

    if text in ["yes", "yeah", "yep", "do it", "open it", "go ahead"]:
        return {"type": "confirm", "confidence": 1.0}

    if text in ["no", "nah", "not now"]:
        return {"type": "deny", "confidence": 1.0}

    if any(word in text for word in continuity_words):
        return {"type": "continuity", "confidence": 1.0}

    if session and session.has_references():
        if any(word in text for word in correction_words):
            return {"type": "correction", "confidence": 1.0}

        if text == "open":
            return {"type": "followup", "confidence": 1.0}

        if number_match or any(word in text for word in followup_words):
            return {"type": "followup", "confidence": 1.0}

    browser_words = ["search", "google", "youtube", "browser", "website"]
    app_words = ["open chrome", "open opera", "open vscode", "open notepad"]

    if any(word in text for word in app_words):
        return {"type": "app_action", "confidence": 1.0}

    if any(word in text for word in browser_words):
        return {"type": "browser_action", "confidence": 0.9}

    file_words = [
        "open", "find", "file", "folder", "document",
        ".txt", ".py", ".docx", ".pdf"
    ]
    if any(word in text for word in file_words):
        return {"type": "file_action", "confidence": 0.9}

    if any(word in text for word in ["remember", "note this"]):
        return {"type": "memory_action", "confidence": 0.95}

    if any(word in text for word in ["hi", "hello", "hey"]):
        return {"type": "greeting", "confidence": 1.0}

    return {"type": "conversation", "confidence": 0.5}