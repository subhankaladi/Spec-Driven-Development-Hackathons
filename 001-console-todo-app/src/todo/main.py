from .repository import TaskRepository

def add_task(repository: TaskRepository):
    title = input("Enter task title: ")
    description = input("Enter task description: ")
    if title:
        task = repository.add(title, description)
        print(f"Task '{task.title}' added.")
    else:
        print("Title cannot be empty.")

def view_tasks(repository: TaskRepository):
    tasks = repository.get_all()
    if not tasks:
        print("No tasks found.")
    else:
        for task in tasks:
            print(task)

def toggle_task_status(repository: TaskRepository):
    try:
        task_id = int(input("Enter task ID to toggle status: "))
        task = repository.get_by_id(task_id)
        if task:
            task.completed = not task.completed
            print(f"Task #{task_id} status updated.")
        else:
            print("Task not found.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def update_task(repository: TaskRepository):
    try:
        task_id = int(input("Enter task ID to update: "))
        task = repository.get_by_id(task_id)
        if task:
            title = input(f"Enter new title (current: {task.title}): ")
            description = input(f"Enter new description (current: {task.description}): ")
            repository.update(task_id, title, description)
            print(f"Task #{task_id} updated.")
        else:
            print("Task not found.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def delete_task(repository: TaskRepository):
    try:
        task_id = int(input("Enter task ID to delete: "))
        if repository.delete(task_id):
            print(f"Task #{task_id} deleted.")
        else:
            print("Task not found.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def main():
    repository = TaskRepository()
    while True:
        print("\nMenu:")
        print("1. Add task")
        print("2. View tasks")
        print("3. Mark task as complete/incomplete")
        print("4. Update task")
        print("5. Delete task")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_task(repository)
        elif choice == '2':
            view_tasks(repository)
        elif choice == '3':
            toggle_task_status(repository)
        elif choice == '4':
            update_task(repository)
        elif choice == '5':
            delete_task(repository)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
