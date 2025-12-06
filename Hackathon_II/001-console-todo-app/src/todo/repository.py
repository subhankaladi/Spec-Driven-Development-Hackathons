from typing import List, Optional
from .task import Task

class TaskRepository:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1

    def add(self, title: str, description: str) -> Task:
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all(self) -> List[Task]:
        return self._tasks

    def get_by_id(self, task_id: int) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update(self, task_id: int, title: str, description: str) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if task:
            task.title = title
            task.description = description
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False
