import re


def interpret_followup(user_input: str) -> dict:
    text = user_input.lower().strip()

    result = {
        "selection_type": "default",
        "index": None,
        "target_kind": None,
        "priority": None,
        "direction": None,
        "avoid_kind": None,
        "extension": None,
    }

    if "not the file" in text or "not file" in text:
        result["selection_type"] = "negative_preference"
        result["avoid_kind"] = "file"
        return result

    if "not the folder" in text or "not folder" in text:
        result["selection_type"] = "negative_preference"
        result["avoid_kind"] = "folder"
        return result

    if "next" in text or "below" in text:
        result["selection_type"] = "relative"
        result["direction"] = "next"
        return result

    if "previous" in text or "above" in text:
        result["selection_type"] = "relative"
        result["direction"] = "previous"
        return result

    if "another" in text or "other one" in text:
        result["selection_type"] = "relative"
        result["direction"] = "next"
        return result

    number_match = re.search(r"\b(\d+)\b", text)
    if number_match:
        result["index"] = int(number_match.group(1)) - 1

    ordinal_map = {
        "first": 0,
        "second": 1,
        "third": 2,
        "fourth": 3,
        "fifth": 4,
    }

    if result["index"] is None:
        for word, index in ordinal_map.items():
            if word in text:
                result["index"] = index
                break

    if "folder" in text:
        result["target_kind"] = "folder"

    if "file" in text:
        result["target_kind"] = "file"

    if ".py" in text:
        result["target_kind"] = "file"
        result["extension"] = ".py"

    if ".txt" in text:
        result["target_kind"] = "file"
        result["extension"] = ".txt"

    if "python file" in text or "python one" in text:
        result["target_kind"] = "file"
        result["extension"] = ".py"

    if "project" in text:
        result["target_kind"] = "folder"
        result["priority"] = "project"

    if "main" in text or "entry" in text:
        result["priority"] = "main"
        if result["target_kind"] is None:
            result["target_kind"] = "file"

    if result["index"] is not None and result["target_kind"] is not None:
        result["selection_type"] = "filtered_index"
        return result

    if result["index"] is not None:
        result["selection_type"] = "index"
        return result

    if result["target_kind"] or result["priority"] or result["extension"]:
        result["selection_type"] = "preferred_kind"
        return result

    return result