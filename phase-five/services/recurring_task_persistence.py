from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from sqlmodel import Field, SQLModel, create_engine, Session, select, update
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pytz
from enum import Enum
from task_recurrence_patterns import RecurrencePatternType, RecurrenceRule, RecurrencePatternCalculator

# Database Models
class RecurringTaskStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RecurringTaskCategory(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    FINANCE = "finance"
    EDUCATION = "education"
    OTHER = "other"

class RecurringTask(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    category: RecurringTaskCategory = RecurringTaskCategory.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    recurrence_pattern: RecurrencePatternType
    recurrence_interval: int = 1
    recurrence_params: Optional[str] = None  # JSON string of additional params
    start_date: datetime
    end_date: Optional[datetime] = None
    next_occurrence: datetime
    last_occurrence: Optional[datetime] = None
    timezone: str = "UTC"
    user_id: str
    created_by: str
    updated_by: str
    status: RecurringTaskStatus = RecurringTaskStatus.ACTIVE
    max_occurrences: Optional[int] = None
    occurrence_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskOccurrence(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="recurringtask.id")
    occurrence_date: datetime
    status: RecurringTaskStatus = RecurringTaskStatus.ACTIVE
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = None  # User ID if assigned to someone else
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskHistory(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="recurringtask.id")
    occurrence_id: Optional[str] = Field(foreign_key="taskoccurrence.id")
    action: str  # created, updated, completed, cancelled, etc.
    old_values: Optional[str] = None  # JSON string of old values
    new_values: Optional[str] = None  # JSON string of new values
    performed_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TaskDependency(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="recurringtask.id")
    depends_on_task_id: str = Field(foreign_key="recurringtask.id")
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, etc.
    lag_time: int = 0  # Minutes of lag
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class RecurringTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[RecurringTaskCategory] = RecurringTaskCategory.OTHER
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    recurrence_pattern: RecurrencePatternType
    recurrence_interval: int = 1
    recurrence_params: Optional[Dict[str, Any]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    user_id: str
    created_by: str
    max_occurrences: Optional[int] = None

class RecurringTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RecurringTaskCategory] = None
    priority: Optional[TaskPriority] = None
    recurrence_pattern: Optional[RecurrencePatternType] = None
    recurrence_interval: Optional[int] = None
    recurrence_params: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None
    status: Optional[RecurringTaskStatus] = None
    max_occurrences: Optional[int] = None

class TaskOccurrenceCreate(BaseModel):
    task_id: str
    occurrence_date: datetime
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class TaskOccurrenceUpdate(BaseModel):
    status: Optional[RecurringTaskStatus] = None
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class TaskDependencyCreate(BaseModel):
    task_id: str
    depends_on_task_id: str
    dependency_type: str = "finish_to_start"
    lag_time: int = 0

class RecurringTaskResponse(RecurringTask):
    pass

class TaskOccurrenceResponse(TaskOccurrence):
    pass

class TaskHistoryResponse(TaskHistory):
    pass

class TaskDependencyResponse(TaskDependency):
    pass

# Recurring Task Persistence Service
class RecurringTaskPersistenceService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.calculator = RecurrencePatternCalculator()

    async def create_recurring_task(self, task_data: RecurringTaskCreate) -> RecurringTaskResponse:
        """Create a new recurring task with proper initialization."""
        # Calculate first occurrence
        rule = RecurrenceRule(
            freq=task_data.recurrence_pattern,
            interval=task_data.recurrence_interval
        )

        # Add any additional parameters from recurrence_params
        if task_data.recurrence_params:
            for param, value in task_data.recurrence_params.items():
                if hasattr(rule, param):
                    setattr(rule, param, value)

        next_occurrence = self.calculator.calculate_next_occurrence(
            task_data.start_date, rule
        )

        if not next_occurrence:
            raise ValueError("Invalid recurrence pattern - could not calculate next occurrence")

        # Create the task
        task = RecurringTask(
            title=task_data.title,
            description=task_data.description,
            category=task_data.category,
            priority=task_data.priority,
            recurrence_pattern=task_data.recurrence_pattern,
            recurrence_interval=task_data.recurrence_interval,
            recurrence_params=json.dumps(task_data.recurrence_params) if task_data.recurrence_params else None,
            start_date=task_data.start_date,
            end_date=task_data.end_date,
            next_occurrence=next_occurrence,
            timezone=task_data.timezone,
            user_id=task_data.user_id,
            created_by=task_data.created_by,
            updated_by=task_data.created_by,
            max_occurrences=task_data.max_occurrences
        )

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Create history entry
        history = TaskHistory(
            task_id=task.id,
            action="created",
            new_values=json.dumps({
                "title": task.title,
                "recurrence_pattern": task.recurrence_pattern.value,
                "start_date": task.start_date.isoformat()
            }),
            performed_by=task.created_by
        )
        self.db_session.add(history)
        self.db_session.commit()

        return RecurringTaskResponse.from_orm(task)

    async def get_recurring_task(self, task_id: str) -> Optional[RecurringTaskResponse]:
        """Get a specific recurring task."""
        task = self.db_session.get(RecurringTask, task_id)
        if task:
            return RecurringTaskResponse.from_orm(task)
        return None

    async def update_recurring_task(
        self, task_id: str, task_update: RecurringTaskUpdate, updated_by: str
    ) -> Optional[RecurringTaskResponse]:
        """Update a recurring task."""
        task = self.db_session.get(RecurringTask, task_id)
        if not task:
            return None

        # Store old values for history
        old_values = {
            "title": task.title,
            "description": task.description,
            "category": task.category.value,
            "priority": task.priority.value,
            "status": task.status.value,
        }

        # Update fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'recurrence_params' and value is not None:
                setattr(task, field, json.dumps(value))
            elif value is not None:
                setattr(task, field, value)

        # If recurrence pattern changed, recalculate next occurrence
        if any(param in update_data for param in [
            'recurrence_pattern', 'recurrence_interval', 'recurrence_params',
            'start_date', 'end_date', 'timezone'
        ]):
            rule = RecurrenceRule(
                freq=task.recurrence_pattern,
                interval=task.recurrence_interval
            )

            if task.recurrence_params:
                params = json.loads(task.recurrence_params)
                for param, value in params.items():
                    if hasattr(rule, param):
                        setattr(rule, param, value)

            next_occurrence = self.calculator.calculate_next_occurrence(
                task.start_date, rule, task.next_occurrence
            )

            if next_occurrence:
                task.next_occurrence = next_occurrence

        task.updated_by = updated_by
        task.updated_at = datetime.utcnow()

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Create history entry
        new_values = {
            "title": task.title,
            "description": task.description,
            "category": task.category.value,
            "priority": task.priority.value,
            "status": task.status.value,
        }

        history = TaskHistory(
            task_id=task.id,
            action="updated",
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            performed_by=updated_by
        )
        self.db_session.add(history)
        self.db_session.commit()

        return RecurringTaskResponse.from_orm(task)

    async def delete_recurring_task(self, task_id: str, deleted_by: str) -> bool:
        """Soft delete a recurring task by marking it as cancelled."""
        task = self.db_session.get(RecurringTask, task_id)
        if not task:
            return False

        old_status = task.status
        task.status = RecurringTaskStatus.CANCELLED
        task.updated_by = deleted_by
        task.updated_at = datetime.utcnow()

        self.db_session.add(task)
        self.db_session.commit()

        # Create history entry
        history = TaskHistory(
            task_id=task.id,
            action="cancelled",
            old_values=json.dumps({"status": old_status.value}),
            new_values=json.dumps({"status": task.status.value}),
            performed_by=deleted_by
        )
        self.db_session.add(history)
        self.db_session.commit()

        return True

    async def get_user_tasks(
        self, user_id: str, status: Optional[RecurringTaskStatus] = None
    ) -> List[RecurringTaskResponse]:
        """Get all recurring tasks for a user."""
        query = select(RecurringTask).where(RecurringTask.user_id == user_id)

        if status:
            query = query.where(RecurringTask.status == status)

        tasks = self.db_session.exec(query).all()
        return [RecurringTaskResponse.from_orm(task) for task in tasks]

    async def get_due_tasks(self, as_of: datetime) -> List[RecurringTaskResponse]:
        """Get all recurring tasks that are due as of the given time."""
        tasks = self.db_session.exec(
            select(RecurringTask).where(
                RecurringTask.status == RecurringTaskStatus.ACTIVE,
                RecurringTask.next_occurrence <= as_of
            )
        ).all()
        return [RecurringTaskResponse.from_orm(task) for task in tasks]

    async def create_task_occurrence(
        self, occurrence_data: TaskOccurrenceCreate
    ) -> TaskOccurrenceResponse:
        """Create a new task occurrence."""
        occurrence = TaskOccurrence(**occurrence_data.dict())
        self.db_session.add(occurrence)
        self.db_session.commit()
        self.db_session.refresh(occurrence)

        return TaskOccurrenceResponse.from_orm(occurrence)

    async def get_task_occurrences(
        self, task_id: str, limit: int = 50, offset: int = 0
    ) -> List[TaskOccurrenceResponse]:
        """Get occurrences for a specific task."""
        occurrences = self.db_session.exec(
            select(TaskOccurrence)
            .where(TaskOccurrence.task_id == task_id)
            .offset(offset)
            .limit(limit)
        ).all()
        return [TaskOccurrenceResponse.from_orm(occ) for occ in occurrences]

    async def update_task_occurrence(
        self, occurrence_id: str, occurrence_update: TaskOccurrenceUpdate
    ) -> Optional[TaskOccurrenceResponse]:
        """Update a task occurrence."""
        occurrence = self.db_session.get(TaskOccurrence, occurrence_id)
        if not occurrence:
            return None

        update_data = occurrence_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(occurrence, field, value)

        if occurrence_update.status == RecurringTaskStatus.COMPLETED:
            occurrence.completed_at = datetime.utcnow()

        self.db_session.add(occurrence)
        self.db_session.commit()
        self.db_session.refresh(occurrence)

        return TaskOccurrenceResponse.from_orm(occurrence)

    async def get_task_history(
        self, task_id: str, limit: int = 50, offset: int = 0
    ) -> List[TaskHistoryResponse]:
        """Get history for a specific task."""
        history_records = self.db_session.exec(
            select(TaskHistory)
            .where(TaskHistory.task_id == task_id)
            .order_by(TaskHistory.timestamp.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return [TaskHistoryResponse.from_orm(hist) for hist in history_records]

    async def create_task_dependency(
        self, dependency_data: TaskDependencyCreate
    ) -> TaskDependencyResponse:
        """Create a dependency between tasks."""
        # Check for circular dependencies
        if await self._would_create_circular_dependency(dependency_data):
            raise ValueError("Creating this dependency would result in a circular dependency")

        dependency = TaskDependency(**dependency_data.dict())
        self.db_session.add(dependency)
        self.db_session.commit()
        self.db_session.refresh(dependency)

        return TaskDependencyResponse.from_orm(dependency)

    async def _would_create_circular_dependency(self, dependency_data: TaskDependencyCreate) -> bool:
        """Check if creating a dependency would result in a circular dependency."""
        # This is a simplified check - in a real implementation, you'd want a more robust algorithm
        # For now, we'll just check if the dependency creates a direct cycle

        # Check if depends_on_task_id already depends on task_id
        existing_deps = self.db_session.exec(
            select(TaskDependency).where(
                TaskDependency.task_id == dependency_data.depends_on_task_id,
                TaskDependency.depends_on_task_id == dependency_data.task_id
            )
        ).all()

        return len(existing_deps) > 0

    async def get_task_dependencies(self, task_id: str) -> List[TaskDependencyResponse]:
        """Get all dependencies for a task."""
        dependencies = self.db_session.exec(
            select(TaskDependency).where(TaskDependency.task_id == task_id)
        ).all()
        return [TaskDependencyResponse.from_orm(dep) for dep in dependencies]

    async def process_completed_occurrence(self, occurrence_id: str) -> bool:
        """Process a completed occurrence and update the recurring task."""
        occurrence = self.db_session.get(TaskOccurrence, occurrence_id)
        if not occurrence:
            return False

        task = self.db_session.get(RecurringTask, occurrence.task_id)
        if not task:
            return False

        # Update occurrence count
        task.occurrence_count += 1

        # Check if max occurrences reached
        if task.max_occurrences and task.occurrence_count >= task.max_occurrences:
            task.status = RecurringTaskStatus.COMPLETED
        else:
            # Calculate next occurrence
            rule = RecurrenceRule(
                freq=task.recurrence_pattern,
                interval=task.recurrence_interval
            )

            if task.recurrence_params:
                params = json.loads(task.recurrence_params)
                for param, value in params.items():
                    if hasattr(rule, param):
                        setattr(rule, param, value)

            next_occurrence = self.calculator.calculate_next_occurrence(
                task.start_date, rule, occurrence.occurrence_date
            )

            if next_occurrence:
                task.next_occurrence = next_occurrence
            else:
                task.status = RecurringTaskStatus.COMPLETED

        task.updated_at = datetime.utcnow()
        self.db_session.add(task)
        self.db_session.commit()

        return True

# FastAPI Application
app = FastAPI(title="Recurring Task Persistence Service", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./recurring_tasks_persistence.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    # Create tables
    SQLModel.metadata.create_all(engine)

# API Endpoints
@app.post("/tasks/", response_model=RecurringTaskResponse)
async def create_recurring_task(
    task_data: RecurringTaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new recurring task."""
    service = RecurringTaskPersistenceService(db)
    return await service.create_recurring_task(task_data)

@app.get("/tasks/{task_id}", response_model=RecurringTaskResponse)
async def get_recurring_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific recurring task."""
    service = RecurringTaskPersistenceService(db)
    task = await service.get_recurring_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=RecurringTaskResponse)
async def update_recurring_task(
    task_id: str,
    task_update: RecurringTaskUpdate,
    updated_by: str = Query(..., description="User ID performing the update"),
    db: Session = Depends(get_db)
):
    """Update a recurring task."""
    service = RecurringTaskPersistenceService(db)
    task = await service.update_recurring_task(task_id, task_update, updated_by)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
async def delete_recurring_task(
    task_id: str,
    deleted_by: str = Query(..., description="User ID performing the deletion"),
    db: Session = Depends(get_db)
):
    """Delete (cancel) a recurring task."""
    service = RecurringTaskPersistenceService(db)
    success = await service.delete_recurring_task(task_id, deleted_by)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task cancelled successfully"}

@app.get("/tasks/user/{user_id}", response_model=List[RecurringTaskResponse])
async def get_user_tasks(
    user_id: str,
    status: Optional[RecurringTaskStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all recurring tasks for a user."""
    service = RecurringTaskPersistenceService(db)
    return await service.get_user_tasks(user_id, status)

@app.get("/tasks/due", response_model=List[RecurringTaskResponse])
async def get_due_tasks(
    as_of: datetime = Query(default_factory=datetime.utcnow),
    db: Session = Depends(get_db)
):
    """Get all recurring tasks that are due as of the given time."""
    service = RecurringTaskPersistenceService(db)
    return await service.get_due_tasks(as_of)

@app.post("/occurrences/", response_model=TaskOccurrenceResponse)
async def create_task_occurrence(
    occurrence_data: TaskOccurrenceCreate,
    db: Session = Depends(get_db)
):
    """Create a new task occurrence."""
    service = RecurringTaskPersistenceService(db)
    return await service.create_task_occurrence(occurrence_data)

@app.get("/occurrences/task/{task_id}", response_model=List[TaskOccurrenceResponse])
async def get_task_occurrences(
    task_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get occurrences for a specific task."""
    service = RecurringTaskPersistenceService(db)
    return await service.get_task_occurrences(task_id, limit, offset)

@app.put("/occurrences/{occurrence_id}", response_model=TaskOccurrenceResponse)
async def update_task_occurrence(
    occurrence_id: str,
    occurrence_update: TaskOccurrenceUpdate,
    db: Session = Depends(get_db)
):
    """Update a task occurrence."""
    service = RecurringTaskPersistenceService(db)
    occurrence = await service.update_task_occurrence(occurrence_id, occurrence_update)
    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")
    return occurrence

@app.get("/history/task/{task_id}", response_model=List[TaskHistoryResponse])
async def get_task_history(
    task_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get history for a specific task."""
    service = RecurringTaskPersistenceService(db)
    return await service.get_task_history(task_id, limit, offset)

@app.post("/dependencies/", response_model=TaskDependencyResponse)
async def create_task_dependency(
    dependency_data: TaskDependencyCreate,
    db: Session = Depends(get_db)
):
    """Create a dependency between tasks."""
    service = RecurringTaskPersistenceService(db)
    try:
        return await service.create_task_dependency(dependency_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/dependencies/task/{task_id}", response_model=List[TaskDependencyResponse])
async def get_task_dependencies(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get all dependencies for a task."""
    service = RecurringTaskPersistenceService(db)
    return await service.get_task_dependencies(task_id)

@app.post("/occurrences/{occurrence_id}/complete")
async def complete_task_occurrence(
    occurrence_id: str,
    db: Session = Depends(get_db)
):
    """Mark a task occurrence as completed and process the recurring task."""
    service = RecurringTaskPersistenceService(db)
    success = await service.process_completed_occurrence(occurrence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Occurrence not found")
    return {"message": "Occurrence completed and task updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)