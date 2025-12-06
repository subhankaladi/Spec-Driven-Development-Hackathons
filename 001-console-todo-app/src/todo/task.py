class Task:
    def __init__(self, id: int, title: str, description: str, completed: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed

    def __repr__(self):
        status = "✓" if self.completed else "✗"
        return f"[{status}] #{self.id}: {self.title} - {self.description}"
