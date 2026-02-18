from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import croniter
from enum import Enum
import logging

# Database Models
class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class TaskStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RecurringTask(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    recurrence_pattern: RecurrencePattern
    recurrence_interval: int = 1  # For custom patterns
    recurrence_days: Optional[str] = None  # For weekly patterns (comma-separated day numbers)
    recurrence_month_day: Optional[int] = None  # For monthly patterns
    recurrence_week_of_month: Optional[int] = None  # For monthly patterns (1st, 2nd, etc.)
    recurrence_month: Optional[int] = None  # For yearly patterns
    start_date: datetime
    end_date: Optional[datetime] = None
    next_occurrence: datetime
    last_occurrence: Optional[datetime] = None
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.ACTIVE
    user_id: str
    reminder_offset_minutes: int = 0  # Minutes before occurrence to send reminder

class TaskOccurrence(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="recurringtask.id")
    occurrence_date: datetime
    status: TaskStatus = TaskStatus.ACTIVE
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class RecurringTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    recurrence_pattern: RecurrencePattern
    recurrence_interval: int = 1
    recurrence_days: Optional[List[int]] = None  # For weekly (0=Sunday, 6=Saturday)
    recurrence_month_day: Optional[int] = None
    recurrence_week_of_month: Optional[int] = None  # 1-5 for first through fifth
    recurrence_month: Optional[int] = None  # 1-12 for January through December
    start_date: datetime
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    user_id: str
    reminder_offset_minutes: int = 0

class RecurringTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None
    recurrence_days: Optional[List[int]] = None
    recurrence_month_day: Optional[int] = None
    recurrence_week_of_month: Optional[int] = None
    recurrence_month: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None
    status: Optional[TaskStatus] = None
    reminder_offset_minutes: Optional[int] = None

class RecurringTaskResponse(RecurringTask):
    pass

class TaskOccurrenceResponse(TaskOccurrence):
    pass

# Recurrence Pattern Handler
class RecurrenceHandler:
    @staticmethod
    def calculate_next_occurrence(task: RecurringTask, from_date: datetime) -> Optional[datetime]:
        """Calculate the next occurrence date based on recurrence pattern."""
        if task.status != TaskStatus.ACTIVE:
            return None

        # Convert to task timezone if needed
        from_date_local = from_date

        # Handle different recurrence patterns
        if task.recurrence_pattern == RecurrencePattern.DAILY:
            next_date = from_date_local + timedelta(days=task.recurrence_interval)
        elif task.recurrence_pattern == RecurrencePattern.WEEKLY:
            # Calculate next weekday occurrence
            days_ahead = 0
            current_weekday = from_date_local.weekday()

            if task.recurrence_days:
                # Convert string to list of integers if needed
                if isinstance(task.recurrence_days, str):
                    recurrence_days = [int(d.strip()) for d in task.recurrence_days.split(',')]
                else:
                    recurrence_days = task.recurrence_days

                # Find next occurrence
                next_date = None
                for day in sorted(recurrence_days):
                    days_diff = (day - current_weekday) % 7
                    if days_diff == 0:  # Same day as today
                        if from_date_local.time().hour >= 0:  # If it's already past midnight today
                            days_diff = 7  # Move to next week
                    candidate_date = from_date_local + timedelta(days=days_diff)

                    if next_date is None or candidate_date < next_date:
                        next_date = candidate_date

                if next_date is None:
                    # If no suitable day found, move to next week
                    next_date = from_date_local + timedelta(days=7)
            else:
                # Default to same weekday
                next_date = from_date_local + timedelta(weeks=task.recurrence_interval)

        elif task.recurrence_pattern == RecurrencePattern.MONTHLY:
            # Calculate next month occurrence
            if task.recurrence_month_day:
                # Fixed day of month
                next_date = from_date_local.replace(day=task.recurrence_month_day)
                if next_date <= from_date_local:
                    # Move to next month
                    if next_date.month == 12:
                        next_date = next_date.replace(year=next_date.year + 1, month=1)
                    else:
                        next_date = next_date.replace(month=next_date.month + 1)
            elif task.recurrence_week_of_month and task.recurrence_days:
                # Specific weekday of month (e.g., first Monday)
                if isinstance(task.recurrence_days, str):
                    day_of_week = int(task.recurrence_days.split(',')[0])
                else:
                    day_of_week = task.recurrence_days[0]

                # Find the nth occurrence of the day in the month
                next_date = RecurrenceHandler._nth_weekday_of_month(
                    from_date_local.year,
                    from_date_local.month,
                    task.recurrence_week_of_month,
                    day_of_week
                )
                if next_date <= from_date_local:
                    # Move to next month
                    if from_date_local.month == 12:
                        next_date = RecurrenceHandler._nth_weekday_of_month(
                            from_date_local.year + 1, 1,
                            task.recurrence_week_of_month, day_of_week
                        )
                    else:
                        next_date = RecurrenceHandler._nth_weekday_of_month(
                            from_date_local.year,
                            from_date_local.month + 1,
                            task.recurrence_week_of_month, day_of_week
                        )
            else:
                # Same day of month as start date
                next_date = from_date_local + timedelta(days=30*task.recurrence_interval)

        elif task.recurrence_pattern == RecurrencePattern.YEARLY:
            # Calculate next year occurrence
            if task.recurrence_month and task.recurrence_month_day:
                # Specific month and day
                next_date = from_date_local.replace(
                    year=from_date_local.year,
                    month=task.recurrence_month,
                    day=task.recurrence_month_day
                )
                if next_date <= from_date_local:
                    # Move to next year
                    next_date = next_date.replace(year=next_date.year + 1)
            else:
                # Same date next year
                next_date = from_date_local.replace(year=from_date_local.year + task.recurrence_interval)

        elif task.recurrence_pattern == RecurrencePattern.CUSTOM:
            # Use cron-like pattern if available
            # For now, treat as daily with custom interval
            next_date = from_date_local + timedelta(days=task.recurrence_interval)
        else:
            return None

        # Check if next occurrence is beyond end date
        if task.end_date and next_date > task.end_date:
            return None

        return next_date

    @staticmethod
    def _nth_weekday_of_month(year: int, month: int, n: int, weekday: int) -> datetime:
        """Get the nth occurrence of a weekday in a month."""
        import calendar
        cal = calendar.monthcalendar(year, month)

        # Count occurrences of the weekday in the month
        count = 0
        for week in cal:
            if week[weekday] != 0:  # 0 means the day is in the previous/next month
                count += 1
                if count == n:
                    return datetime(year, month, week[weekday])

        # If nth occurrence doesn't exist (e.g., 5th Monday in Feb with only 4 Mondays),
        # return the last occurrence
        for week in reversed(cal):
            if week[weekday] != 0:
                return datetime(year, month, week[weekday])

        raise ValueError(f"Could not find {n}th {weekday} of {month}/{year}")

# Scheduler Service
class RecurringTaskScheduler:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def process_scheduled_tasks(self):
        """Process tasks that are due and create new occurrences."""
        try:
            # Find all active recurring tasks
            active_tasks = self.db_session.exec(
                select(RecurringTask).where(
                    RecurringTask.status == TaskStatus.ACTIVE,
                    RecurringTask.next_occurrence <= datetime.utcnow()
                )
            ).all()

            for task in active_tasks:
                await self.process_task_occurrence(task)

        except Exception as e:
            self.logger.error(f"Error processing scheduled tasks: {e}")

    async def process_task_occurrence(self, task: RecurringTask):
        """Process a single task occurrence and schedule the next one."""
        try:
            # Create occurrence record
            occurrence = TaskOccurrence(
                task_id=task.id,
                occurrence_date=task.next_occurrence,
                status=TaskStatus.ACTIVE
            )
            self.db_session.add(occurrence)

            # Update task with last occurrence and calculate next occurrence
            task.last_occurrence = task.next_occurrence
            next_occurrence = RecurrenceHandler.calculate_next_occurrence(task, task.next_occurrence)

            if next_occurrence:
                task.next_occurrence = next_occurrence
            else:
                # No more occurrences, mark task as completed
                task.status = TaskStatus.COMPLETED

            self.db_session.add(task)
            self.db_session.commit()

            # Trigger reminder if configured
            if task.reminder_offset_minutes > 0:
                await self.schedule_reminder(task, occurrence)

        except Exception as e:
            self.logger.error(f"Error processing task occurrence {task.id}: {e}")
            self.db_session.rollback()

    async def schedule_reminder(self, task: RecurringTask, occurrence: TaskOccurrence):
        """Schedule a reminder for the upcoming occurrence."""
        try:
            # Calculate reminder time
            reminder_time = occurrence.occurrence_date - timedelta(minutes=task.reminder_offset_minutes)

            # In a real implementation, this would publish to a message queue
            # or schedule with a job scheduler like Celery
            print(f"Scheduled reminder for task {task.id} at {reminder_time}")

        except Exception as e:
            self.logger.error(f"Error scheduling reminder for task {task.id}: {e}")

# FastAPI Application
app = FastAPI(title="Recurring Task Scheduler Service", version="1.0.0")

# Database setup (in a real app, this would come from dependency injection)
DATABASE_URL = "sqlite:///./recurring_tasks.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    # Create tables
    SQLModel.metadata.create_all(engine)

# API Endpoints
@app.post("/recurring-tasks/", response_model=RecurringTaskResponse)
async def create_recurring_task(task_data: RecurringTaskCreate, db: Session = Depends(get_db)):
    """Create a new recurring task."""
    # Calculate first occurrence
    next_occurrence = RecurrenceHandler.calculate_next_occurrence(
        RecurringTask(
            recurrence_pattern=task_data.recurrence_pattern,
            recurrence_interval=task_data.recurrence_interval,
            recurrence_days=str(task_data.recurrence_days) if task_data.recurrence_days else None,
            recurrence_month_day=task_data.recurrence_month_day,
            recurrence_week_of_month=task_data.recurrence_week_of_month,
            recurrence_month=task_data.recurrence_month,
            start_date=task_data.start_date,
            end_date=task_data.end_date,
            timezone=task_data.timezone
        ),
        task_data.start_date
    )

    if not next_occurrence:
        raise HTTPException(status_code=400, detail="Invalid recurrence pattern or dates")

    # Create task record
    task = RecurringTask(
        title=task_data.title,
        description=task_data.description,
        recurrence_pattern=task_data.recurrence_pattern,
        recurrence_interval=task_data.recurrence_interval,
        recurrence_days=str(task_data.recurrence_days) if task_data.recurrence_days else None,
        recurrence_month_day=task_data.recurrence_month_day,
        recurrence_week_of_month=task_data.recurrence_week_of_month,
        recurrence_month=task_data.recurrence_month,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        next_occurrence=next_occurrence,
        timezone=task_data.timezone,
        user_id=task_data.user_id,
        reminder_offset_minutes=task_data.reminder_offset_minutes
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@app.get("/recurring-tasks/{task_id}", response_model=RecurringTaskResponse)
async def get_recurring_task(task_id: str, db: Session = Depends(get_db)):
    """Get a specific recurring task."""
    task = db.get(RecurringTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/recurring-tasks/{task_id}", response_model=RecurringTaskResponse)
async def update_recurring_task(
    task_id: str,
    task_update: RecurringTaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a recurring task."""
    task = db.get(RecurringTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields that were provided
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'recurrence_days' and value is not None:
            # Convert list to string for storage
            setattr(task, field, str(value) if isinstance(value, list) else value)
        else:
            setattr(task, field, value)

    # If recurrence pattern changed, recalculate next occurrence
    if any(field in update_data for field in [
        'recurrence_pattern', 'recurrence_interval', 'recurrence_days',
        'recurrence_month_day', 'recurrence_week_of_month', 'recurrence_month',
        'start_date', 'end_date'
    ]):
        next_occurrence = RecurrenceHandler.calculate_next_occurrence(task, task.next_occurrence)
        if next_occurrence:
            task.next_occurrence = next_occurrence

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@app.delete("/recurring-tasks/{task_id}")
async def delete_recurring_task(task_id: str, db: Session = Depends(get_db)):
    """Delete a recurring task."""
    task = db.get(RecurringTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.CANCELLED
    db.add(task)
    db.commit()

    return {"message": "Task cancelled"}

@app.get("/recurring-tasks/user/{user_id}", response_model=List[RecurringTaskResponse])
async def get_user_recurring_tasks(user_id: str, db: Session = Depends(get_db)):
    """Get all recurring tasks for a user."""
    tasks = db.exec(
        select(RecurringTask).where(RecurringTask.user_id == user_id)
    ).all()
    return tasks

@app.get("/recurring-tasks/{task_id}/occurrences", response_model=List[TaskOccurrenceResponse])
async def get_task_occurrences(task_id: str, db: Session = Depends(get_db)):
    """Get all occurrences of a recurring task."""
    occurrences = db.exec(
        select(TaskOccurrence).where(TaskOccurrence.task_id == task_id)
    ).all()
    return occurrences

@app.post("/scheduler/process")
async def process_scheduled_tasks(db: Session = Depends(get_db)):
    """Manually trigger the scheduler to process due tasks."""
    scheduler = RecurringTaskScheduler(db)
    await scheduler.process_scheduled_tasks()
    return {"message": "Scheduled tasks processed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)