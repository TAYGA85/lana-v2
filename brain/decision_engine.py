def decide_next_step(user_input: str, intent: dict, session) -> dict:
    text = user_input.lower().strip()
    intent_type = intent.get("type", "conversation")

    has_refs = session.has_references()
    mode = session.get_mode()
    pending = session.get_pending_action()
    last_action = session.get_last_action_summary()
    last_suggestion = session.get_last_suggestion()

    # Strong explicit actions
    if intent_type in {
        "file_action",
        "browser_action",
        "app_action",
        "followup",
        "correction",
        "continuity",
        "confirm",
        "deny",
    }:
        return {
            "decision": "act",
            "reason": f"explicit_{intent_type}",
            "confidence": 1.0,
        }

    # If user is vague but context is strong
    if text in {"open", "do it", "go on"} and (has_refs or pending):
        return {
            "decision": "act",
            "reason": "strong_context",
            "confidence": 0.9,
        }

    # Very short uncertain conversational input
    if intent_type == "conversation":
        if text in {"hmm", "uh", "..."}:
            return {
                "decision": "wait",
                "reason": "weak_signal",
                "confidence": 0.7,
            }

        if text in {"okay", "alright"}:
            # If we have active context → suggest
            if session.get_mode() in {"project_mode", "browser_mode", "app_mode"}:
                if session.get_last_action_summary() or session.get_last_suggestion():
                    return {
                        "decision": "suggest",
                        "reason": "soft_ack_with_context",
                        "confidence": 0.8,
                    }

            # Otherwise → wait
            return {
                "decision": "wait",
                "reason": "soft_ack_no_context",
                "confidence": 0.6,
            }

    # If there is context worth nudging on
    if intent_type == "conversation":
        if mode in {"project_mode", "browser_mode", "app_mode"} and (last_action or last_suggestion):
            return {
                "decision": "suggest",
                "reason": "active_context_available",
                "confidence": 0.75,
            }

    # If input is too vague and no context
    if intent_type == "conversation" and not has_refs and not last_action:
        return {
            "decision": "ask",
            "reason": "not_enough_context",
            "confidence": 0.8,
        }

    return {
        "decision": "wait",
        "reason": "default_safe",
        "confidence": 0.5,
    }