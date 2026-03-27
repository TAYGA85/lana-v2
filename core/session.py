class SessionManager:
    def __init__(self):
        self.active_topic = None
        self.last_reference_list = []
        self.pending_action = None

        self.last_opened_item = None
        self.last_opened_index = None

        self.current_project = None
        self.last_action_summary = None

        self.current_mode = "conversation_mode"
        self.last_mode_announcement = None

        self.last_suggestion = None
        self.last_search_query = None

    def set_reference_list(self, items: list):
        self.last_reference_list = items or []

    def clear_reference_list(self):
        self.last_reference_list = []

    def get_reference(self, index: int):
        if 0 <= index < len(self.last_reference_list):
            return self.last_reference_list[index]
        return None

    def has_references(self) -> bool:
        return len(self.last_reference_list) > 0

    def set_pending_action(self, action: dict | None):
        self.pending_action = action

    def get_pending_action(self):
        return self.pending_action

    def clear_pending_action(self):
        self.pending_action = None

    def set_last_opened_item(self, item: dict):
        self.last_opened_item = item
        self.last_opened_index = None

    def get_last_opened_item(self):
        return self.last_opened_item

    def set_last_opened(self, item: dict, index: int):
        self.last_opened_item = item
        self.last_opened_index = index

    def get_last_opened_index(self):
        return self.last_opened_index

    def clear_last_opened(self):
        self.last_opened_item = None
        self.last_opened_index = None

    def set_current_project(self, project_name: str | None):
        self.current_project = project_name

    def get_current_project(self):
        return self.current_project

    def set_last_action_summary(self, summary: str | None):
        self.last_action_summary = summary

    def get_last_action_summary(self):
        return self.last_action_summary

    def set_mode(self, mode: str):
        self.current_mode = mode

    def get_mode(self):
        return self.current_mode

    def set_last_mode_announcement(self, mode: str | None):
        self.last_mode_announcement = mode

    def get_last_mode_announcement(self):
        return self.last_mode_announcement

    def set_last_suggestion(self, suggestion: str | None):
        self.last_suggestion = suggestion

    def get_last_suggestion(self):
        return self.last_suggestion

    def clear_last_suggestion(self):
        self.last_suggestion = None

    def set_last_search_query(self, query: str | None):
        self.last_search_query = query

    def get_last_search_query(self):
        return self.last_search_query

    def reset_context(self):
        self.clear_pending_action()
        self.clear_last_suggestion()