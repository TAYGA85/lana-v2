class ShortMemory:
    def __init__(self):
        self.history = []

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "text": message})

    def add_lana_message(self, message: str):
        self.history.append({"role": "lana", "text": message})

    def get_recent(self, limit: int = 6):
        return self.history[-limit:]