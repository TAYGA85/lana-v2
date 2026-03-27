import re
from brain.planner import make_plan, get_smart_suggestion
from actions.files import search_files, open_path, extract_search_query
from memory.long_memory import increase_usage, get_usage_score
from actions.apps import open_app
from actions.browser import open_website, search_google, search_youtube
from brain.followup_interpreter import interpret_followup
from brain.decision_engine import decide_next_step

def maybe_add_mode_note(session, target_mode: str) -> str:
    current_mode = session.get_mode()
    last_announced = session.get_last_mode_announcement()

    if current_mode != target_mode:
        session.set_mode(target_mode)

        if last_announced != target_mode:
            session.set_last_mode_announcement(target_mode)

            notes = {
                "project_mode": "You're back in project mode.",
                "browser_mode": "You're browsing now.",
                "app_mode": "Switching app context.",
                "conversation_mode": "Back to normal conversation."
            }
            return notes.get(target_mode, "")

    return ""


def get_mode_suggestion(session) -> str:
    mode = session.get_mode()
    last_action = session.get_last_action_summary()
    current_project = session.get_current_project()

    if mode == "project_mode":
        if current_project:
            return f"Want me to keep working on {current_project}?"
        return "Want me to keep working on the project?"

    if mode == "browser_mode":
        if last_action:
            return "Want me to refine the search or open another result?"
        return "Want me to search something else?"

    if mode == "app_mode":
        if last_action:
            return "Want me to switch back when you're done here?"
        return "Want me to open something else too?"

    return ""


def _finalize_suggestion(session):
    suggestion_note = get_mode_suggestion(session)
    if suggestion_note:
        session.set_last_suggestion(suggestion_note)
    else:
        session.set_last_suggestion(None)
    return suggestion_note


def _format_mode_and_suggestion(mode_note: str, suggestion_note: str) -> str:
    extras = []
    if mode_note:
        extras.append(f"LANA mode: {mode_note}")
    if suggestion_note:
        extras.append(f"LANA suggestion: {suggestion_note}")
    return "\n".join(extras)


def _open_reference_item(session, item: dict, index: int | None = None):
    item_type = item.get("type")
    item_name = item.get("name", "item")
    item_path = item.get("path")

    if index is not None:
        session.set_last_opened(item, index)
    else:
        session.set_last_opened_item(item)

    session.set_last_action_summary(f"Opened {item_name}")

    if item_type == "folder":
        session.set_current_project(item_name)

    if item_type in {"file", "folder"}:
        increase_usage(item_path)
        return open_path(item_path)

    if item_type == "web":
        return open_website(item_path)

    return f"Opening {item_name}."


def _handle_app_open(session, app_name: str, label: str, mode_note: str):
    session.set_last_action_summary(f"Opened {label}")
    response = open_app(app_name)
    suggestion_note = _finalize_suggestion(session)
    extras = _format_mode_and_suggestion(mode_note, suggestion_note)

    if extras:
        return f"{response}\n{extras}"
    return response


def _list_results(title: str, results: list, include_type: bool = True):
    lines = [title]
    for i, item in enumerate(results, start=1):
        if include_type:
            lines.append(f"{i}. [{item['type']}] {item['name']}")
        else:
            lines.append(f"{i}. {item['name']}")
    return lines


def _pick_number_index(text: str) -> int:
    number_match = re.search(r"\b(\d+)\b", text)
    if number_match:
        return int(number_match.group(1)) - 1
    if "first" in text:
        return 0
    if "second" in text:
        return 1
    if "third" in text:
        return 2
    if "fourth" in text:
        return 3
    if "fifth" in text:
        return 4
    return 0


def build_response(user_input: str, intent: dict, memory, state, session) -> str:
    text = user_input.lower().strip()
    intent_type = intent.get("type")
    state.last_intent = intent_type

    plan = make_plan(intent_type, user_input)
    decision = decide_next_step(user_input, intent, session)

    if decision["decision"] == "wait":
        return "I'm here."

    if decision["decision"] == "ask" and intent_type == "conversation":
        return "Tell me what you want me to do."

    if decision["decision"] == "suggest" and intent_type == "conversation":
        suggestion_note = get_mode_suggestion(session)
        if suggestion_note:
            session.set_last_suggestion(suggestion_note)
            return suggestion_note
        return "Go on."

    if intent_type == "confirm":
        pending = session.get_pending_action()
        last_suggestion = session.get_last_suggestion()
        mode = session.get_mode()

        if pending:
            session.clear_pending_action()

            if pending["type"] == "open_path":
                item = {
                    "name": pending["name"],
                    "path": pending["path"],
                    "type": pending.get("item_type", "folder")
                }
                session.clear_last_suggestion()
                return _open_reference_item(session, item)

            if pending["type"] == "open_web":
                item = {
                    "name": pending["name"],
                    "path": pending["path"],
                    "type": "web"
                }
                session.clear_last_suggestion()
                return _open_reference_item(session, item)

        if last_suggestion:
            if mode == "project_mode":
                current_project = session.get_current_project()

                if current_project and session.has_references():
                    for i, item in enumerate(session.last_reference_list):
                        if item["type"] == "folder" and current_project.lower() in item["name"].lower():
                            session.clear_last_suggestion()
                            return _open_reference_item(session, item, i)

            if mode == "browser_mode":
                if session.has_references():
                    item = session.get_reference(0)

                    if item and item["type"] == "web":
                        session.clear_last_suggestion()
                        return _open_reference_item(session, item, 0)

            if mode == "app_mode":
                current_project = session.get_current_project()

                if current_project and session.has_references():
                    for i, item in enumerate(session.last_reference_list):
                        if item["type"] == "folder" and current_project.lower() in item["name"].lower():
                            session.clear_last_suggestion()
                            return _open_reference_item(session, item, i)

        return "Alright."

    if intent_type == "deny":
        session.clear_pending_action()
        return "Okay."

    if intent_type == "greeting":
        maybe_add_mode_note(session, "conversation_mode")
        return "Hey. I'm here."

    if intent_type == "continuity":
        if "what was i doing" in text or "what was i working on" in text:
            last_summary = session.get_last_action_summary()
            current_project = session.get_current_project()

            if last_summary and current_project:
                return f"You were working on {current_project}. Last action: {last_summary}."
            if last_summary:
                return f"Your last action was: {last_summary}."
            return "I don't have enough recent context yet."

        if "continue" in text or "resume" in text or "go back to that" in text:
            last_item = session.get_last_opened_item()

            if last_item:
                session.set_last_action_summary(f"Reopened {last_item['name']}")
                if last_item["type"] in {"file", "folder"}:
                    increase_usage(last_item["path"])
                return _open_reference_item(session, last_item)

            return "I don't have anything recent to continue yet."

        if "open the project again" in text:
            current_project = session.get_current_project()

            if current_project and session.has_references():
                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "folder" and item["name"].lower() == current_project.lower():
                        session.set_last_action_summary(f"Reopened project {item['name']}")
                        return _open_reference_item(session, item, i)

            return "I don't have a project ready to reopen yet."

        return "Tell me what you want to continue."

    if intent_type == "file_action":
        query = extract_search_query(user_input)

        if not query:
            return "Tell me what file or folder you want me to search for."

        results = search_files(query)

        if not results:
            return f"I couldn't find anything matching '{query}'."

        session.set_reference_list(results)
        session.set_last_action_summary(f"Searched files for '{query}'")

        mode_note = maybe_add_mode_note(session, "project_mode")

        lines = _list_results("I found these results:", results, include_type=True)

        suggestion, action = get_smart_suggestion(query, session)
        if suggestion and action:
            lines.append("")
            lines.append(f"LANA note: {suggestion}")
            session.set_pending_action(action)
        else:
            session.clear_pending_action()

        suggestion_note = _finalize_suggestion(session)
        extras = _format_mode_and_suggestion(mode_note, suggestion_note)

        if extras:
            lines.append("")
            lines.append(extras)

        return "\n".join(lines)

    if intent_type == "browser_action":
        results = []

        if "youtube" in text and "search" in text:
            query = text.replace("search youtube", "").strip()
            session.set_last_search_query(query)
            results = [
                {
                    "name": f"YouTube search: {query}",
                    "path": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
                    "type": "web"
                }
            ]

        elif "search" in text:
            query = text.replace("search", "").strip()
            session.set_last_search_query(query)
            results = [
                {
                    "name": f"Google search: {query}",
                    "path": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                    "type": "web"
                }
            ]

        elif "youtube" in text:
            results = [{"name": "YouTube", "path": "https://www.youtube.com", "type": "web"}]

        elif "google" in text:
            results = [{"name": "Google", "path": "https://www.google.com", "type": "web"}]

        if not results:
            return "Tell me what to search or open."

        session.set_reference_list(results)
        session.set_last_action_summary(f"Prepared browser results for {results[0]['name']}")

        mode_note = maybe_add_mode_note(session, "browser_mode")

        lines = _list_results("Here are the results:", results, include_type=False)

        suggestion_note = _finalize_suggestion(session)
        extras = _format_mode_and_suggestion(mode_note, suggestion_note)

        if extras:
            lines.append("")
            lines.append(extras)

        return "\n".join(lines)

    if intent_type == "app_action":
        mode_note = maybe_add_mode_note(session, "app_mode")

        if "chrome" in text:
            return _handle_app_open(session, "chrome", "chrome", mode_note)

        if "opera" in text:
            return _handle_app_open(session, "opera", "opera", mode_note)

        if "notepad" in text:
            return _handle_app_open(session, "notepad", "notepad", mode_note)

        if "code" in text or "vscode" in text:
            return _handle_app_open(session, "vscode", "vscode", mode_note)

        return "Tell me which app to open."

    if intent_type == "memory_action":
        return "Okay. I'll remember that."

    if intent_type == "followup":
        parsed = interpret_followup(user_input)

        if parsed["selection_type"] == "negative_preference":
            avoid_kind = parsed["avoid_kind"]

            if avoid_kind == "file" and session.has_references():
                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "folder":
                        return _open_reference_item(session, item, i)
                return "I couldn't find a folder in the list."

            if avoid_kind == "folder" and session.has_references():
                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "file":
                        return _open_reference_item(session, item, i)
                return "I couldn't find a file in the list."

        if parsed["selection_type"] == "relative":
            current_index = session.get_last_opened_index()

            if current_index is None:
                return "I need a current result first."

            if parsed["direction"] == "next":
                target_index = current_index + 1
            else:
                target_index = current_index - 1

            item = session.get_reference(target_index)
            if not item:
                if parsed["direction"] == "next":
                    return "There is no next result."
                return "There is nothing before this one."

            return _open_reference_item(session, item, target_index)

        if parsed["selection_type"] == "filtered_index":
            target_kind = parsed["target_kind"]
            target_index = parsed["index"]
            extension = parsed.get("extension")

            filtered_items = []
            for original_index, item in enumerate(session.last_reference_list):
                if item["type"] != target_kind:
                    continue

                if extension and not item["name"].lower().endswith(extension):
                    continue

                filtered_items.append((original_index, item))

            if target_index is None or target_index < 0 or target_index >= len(filtered_items):
                return f"I couldn't find that {target_kind} in the list."

            original_index, item = filtered_items[target_index]
            return _open_reference_item(session, item, original_index)

        if parsed["selection_type"] == "index":
            item = session.get_reference(parsed["index"])
            if not item:
                return "That number doesn't exist in the list."
            return _open_reference_item(session, item, parsed["index"])

        if parsed["selection_type"] == "preferred_kind":
            target_kind = parsed["target_kind"]
            priority = parsed["priority"]
            extension = parsed.get("extension")

            if target_kind == "folder" and priority == "project":
                for i, item in enumerate(session.last_reference_list):
                    name_lower = item["name"].lower()
                    if item["type"] == "folder" and (
                        "project" in name_lower
                        or "lana" in name_lower
                        or "core" in name_lower
                    ):
                        return _open_reference_item(session, item, i)

            if target_kind == "file" and priority == "main":
                priority_names = ["main.py", "app.py", "index.py", "start.py"]

                for wanted_name in priority_names:
                    for i, item in enumerate(session.last_reference_list):
                        if item["type"] == "file" and item["name"].lower() == wanted_name:
                            if extension and not item["name"].lower().endswith(extension):
                                continue
                            return _open_reference_item(session, item, i)

                for i, item in enumerate(session.last_reference_list):
                    name_lower = item["name"].lower()
                    if item["type"] == "file" and any(
                        keyword in name_lower for keyword in ["main", "app", "index", "start"]
                    ):
                        if extension and not item["name"].lower().endswith(extension):
                            continue
                        return _open_reference_item(session, item, i)

                best_item = None
                best_index = None
                best_usage = -1

                for i, item in enumerate(session.last_reference_list):
                    if item["type"] != "file":
                        continue
                    if extension and not item["name"].lower().endswith(extension):
                        continue
                    if item["name"].lower().endswith(".py"):
                        usage = get_usage_score(item["path"])
                        if usage > best_usage:
                            best_usage = usage
                            best_item = item
                            best_index = i

                if best_item:
                    return _open_reference_item(session, best_item, best_index)

                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "file":
                        if extension and not item["name"].lower().endswith(extension):
                            continue
                        return _open_reference_item(session, item, i)

                return "I couldn't find a main file in the list."

            if target_kind == "folder":
                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "folder":
                        return _open_reference_item(session, item, i)
                return "I couldn't find a folder in the list."

            if target_kind == "file":
                for i, item in enumerate(session.last_reference_list):
                    if item["type"] == "file":
                        if extension and not item["name"].lower().endswith(extension):
                            continue
                        return _open_reference_item(session, item, i)
                return "I couldn't find a file in the list."

        index = _pick_number_index(text)
        item = session.get_reference(index)

        if not item:
            return "That number doesn't exist in the list."

        return _open_reference_item(session, item, index)
    if intent_type == "correction":
        if "show again" in text or "go back" in text:
            if not session.has_references():
                return "I don't have a list to show again."

            lines = _list_results("Here are the results again:", session.last_reference_list, include_type=True)
            return "\n".join(lines)

        if "refine" in text or "refine it" in text:
            query = session.get_last_search_query()

            if not query:
                return "I don't have a search to refine."

            refined_query = query + " best tools"
            session.set_last_action_summary(f"Refined search: {refined_query}")
            return search_google(refined_query)

        if "last one" in text or "used before" in text:
            last_item = session.get_last_opened_item()
            if not last_item:
                return "I don't have a previous item yet."

            return _open_reference_item(session, last_item)

        if "usual file" in text or "usual one" in text:
            best_item = None
            best_index = None
            best_usage = -1

            for i, item in enumerate(session.last_reference_list):
                usage = get_usage_score(item["path"])
                if usage > best_usage:
                    best_usage = usage
                    best_item = item
                    best_index = i

            if not best_item:
                return "I don't have a usual item for this yet."

            return _open_reference_item(session, best_item, best_index)

        if "next" in text or "below" in text:
            current_index = session.get_last_opened_index()

            if current_index is None:
                return "I need a current item to move from."

            next_index = current_index + 1

            if next_index < len(session.last_reference_list):
                item = session.get_reference(next_index)
                return _open_reference_item(session, item, next_index)

            return "There is nothing after this one."

        if "previous" in text or "above" in text:
            current_index = session.get_last_opened_index()

            if current_index is None:
                return "I need a current item to move from."

            prev_index = current_index - 1

            if prev_index >= 0:
                item = session.get_reference(prev_index)
                return _open_reference_item(session, item, prev_index)

            return "There is nothing before this one."

        if "another" in text or "other one" in text:
            current_index = session.get_last_opened_index()

            if current_index is None:
                return "I need a current result first."

            next_index = current_index + 1

            if next_index < len(session.last_reference_list):
                item = session.get_reference(next_index)
                return _open_reference_item(session, item, next_index)

            return "There is no next result."

        number_match = re.search(r"\b(\d+)\b", text)
        if number_match:
            index = int(number_match.group(1)) - 1
            item = session.get_reference(index)

            if not item:
                return "That number doesn't exist in the list."

            return _open_reference_item(session, item, index)

        if "not that" in text or "instead" in text:
            return "Alright. Tell me which one you want."

        return "Okay. Tell me which result you want instead."

    return f"I understand. {user_input}"