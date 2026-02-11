"""Integration tests for reminder functionality."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from src.models.task import Task
from src.models.reminder import Reminder


@pytest.fixture
def session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_reminder(session: Session):
    """Test creating a reminder."""
    user_id = uuid4()
    task_id = uuid4()
    remind_at = datetime.utcnow() + timedelta(hours=1)

    reminder = Reminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        notification_method="default",
        status="scheduled",
    )
    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    assert reminder.id is not None
    assert reminder.task_id == task_id
    assert reminder.user_id == user_id
    assert reminder.remind_at == remind_at
    assert reminder.status == "scheduled"
    assert reminder.created_at is not None


def test_reminder_status_transitions(session: Session):
    """Test reminder status transitions."""
    user_id = uuid4()
    task_id = uuid4()
    remind_at = datetime.utcnow() + timedelta(hours=1)

    reminder = Reminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        status="scheduled",
    )
    session.add(reminder)
    session.commit()

    # Transition to triggered
    reminder.status = "triggered"
    reminder.triggered_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    assert reminder.status == "triggered"
    assert reminder.triggered_at is not None


def test_task_with_reminder(session: Session):
    """Test creating task with reminder."""
    user_id = uuid4()
    due_at = datetime.utcnow() + timedelta(days=1)
    remind_at = due_at - timedelta(minutes=10)

    task = Task(
        user_id=user_id,
        title="Task with reminder",
        due_at=due_at,
        remind_at=remind_at,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Create reminder
    reminder = Reminder(
        task_id=task.id,
        user_id=user_id,
        remind_at=remind_at,
    )
    session.add(reminder)
    session.commit()

    # Query back
    reminder_query = select(Reminder).where(Reminder.task_id == task.id)
    found_reminder = session.exec(reminder_query).first()

    assert found_reminder is not None
    assert found_reminder.task_id == task.id
    assert found_reminder.remind_at == remind_at


def test_multiple_reminders_for_task(session: Session):
    """Test creating multiple reminders for different tasks."""
    user_id = uuid4()

    # Create 3 tasks
    task_ids = []
    for i in range(3):
        task = Task(
            user_id=user_id,
            title=f"Task {i+1}",
            remind_at=datetime.utcnow() + timedelta(hours=i+1),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        task_ids.append(task.id)

    # Create reminders
    for i, task_id in enumerate(task_ids):
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            remind_at=datetime.utcnow() + timedelta(hours=i+1),
        )
        session.add(reminder)
    session.commit()

    # Query reminders for user
    reminders_query = select(Reminder).where(Reminder.user_id == user_id)
    reminders = session.exec(reminders_query).all()

    assert len(reminders) == 3
    for i, reminder in enumerate(sorted(reminders, key=lambda r: r.remind_at)):
        assert reminder.user_id == user_id


def test_reminder_query_by_time_range(session: Session):
    """Test querying reminders within a time range."""
    user_id = uuid4()
    now = datetime.utcnow()

    # Create reminders at different times
    for i in range(5):
        reminder = Reminder(
            task_id=uuid4(),
            user_id=user_id,
            remind_at=now + timedelta(hours=i),
            status="scheduled" if i % 2 == 0 else "triggered",
        )
        session.add(reminder)
    session.commit()

    # Query scheduled reminders in next 3 hours
    future = now + timedelta(hours=3)
    query = select(Reminder).where(
        (Reminder.user_id == user_id) &
        (Reminder.remind_at <= future) &
        (Reminder.status == "scheduled")
    )
    reminders = session.exec(query).all()

    # Should have at least 2 (hours 0 and 2)
    assert len(reminders) >= 2
    for reminder in reminders:
        assert reminder.remind_at <= future
        assert reminder.status == "scheduled"


def test_reminder_with_different_notification_methods(session: Session):
    """Test reminders with different notification methods."""
    user_id = uuid4()
    task_id = uuid4()
    remind_at = datetime.utcnow() + timedelta(hours=1)

    methods = ["default", "email", "sms", "push"]

    for method in methods:
        reminder = Reminder(
            task_id=uuid4(),  # Different task for each method
            user_id=user_id,
            remind_at=remind_at,
            notification_method=method,
        )
        session.add(reminder)
    session.commit()

    # Verify all created
    query = select(Reminder).where(Reminder.user_id == user_id)
    reminders = session.exec(query).all()

    assert len(reminders) == 4
    notification_methods = {r.notification_method for r in reminders}
    assert notification_methods == set(methods)


def test_reminder_timestamps(session: Session):
    """Test reminder timestamp tracking."""
    user_id = uuid4()
    task_id = uuid4()
    remind_at = datetime.utcnow() + timedelta(hours=1)

    before_create = datetime.utcnow()
    reminder = Reminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        status="scheduled",
    )
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    after_create = datetime.utcnow()

    # created_at should be between before_create and after_create
    assert before_create <= reminder.created_at <= after_create

    # triggered_at should be None initially
    assert reminder.triggered_at is None

    # Mark as triggered
    before_trigger = datetime.utcnow()
    reminder.status = "triggered"
    reminder.triggered_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    after_trigger = datetime.utcnow()

    assert reminder.status == "triggered"
    assert before_trigger <= reminder.triggered_at <= after_trigger


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
