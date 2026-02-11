"""Integration tests for recurring task functionality."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from src.models.task import Task
from src.models.reminder import Reminder
from src.models.audit_log import AuditLog
from src.services.recurrence_service import RecurrenceService


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


def test_recurring_daily_task(session: Session):
    """Test daily recurring task generation."""
    user_id = uuid4()

    # Create recurring daily task
    task = Task(
        user_id=user_id,
        title="Daily standup",
        priority="medium",
        recurrence_rule={"frequency": "daily"},
    )
    session.add(task)
    session.commit()

    # Calculate next occurrence
    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)

    assert next_occ is not None
    # Should be approximately 24 hours from now
    now = datetime.utcnow()
    assert (next_occ - now).days == 1 or (next_occ - now).days == 0


def test_recurring_weekly_task(session: Session):
    """Test weekly recurring task generation."""
    user_id = uuid4()

    task = Task(
        user_id=user_id,
        title="Weekly review",
        priority="medium",
        recurrence_rule={"frequency": "weekly"},
    )
    session.add(task)
    session.commit()

    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)

    assert next_occ is not None
    # Should be approximately 7 days from now
    now = datetime.utcnow()
    days_diff = (next_occ - now).days
    assert days_diff >= 6 and days_diff <= 8


def test_recurring_monthly_task(session: Session):
    """Test monthly recurring task generation."""
    user_id = uuid4()

    task = Task(
        user_id=user_id,
        title="Monthly report",
        priority="high",
        recurrence_rule={"frequency": "monthly"},
    )
    session.add(task)
    session.commit()

    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)

    assert next_occ is not None
    # Should be approximately 1 month from now
    now = datetime.utcnow()
    assert next_occ.month != now.month or next_occ.year != now.year


def test_recurring_task_with_end_date(session: Session):
    """Test recurring task with end date constraint."""
    user_id = uuid4()
    today = datetime.utcnow()
    end_date = today + timedelta(days=3)  # End in 3 days

    task = Task(
        user_id=user_id,
        title="Short recurring task",
        recurrence_rule={"frequency": "daily", "end_date": end_date.date().isoformat()},
    )
    session.add(task)
    session.commit()

    # First occurrence should be calculated
    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)
    assert next_occ is not None
    assert next_occ <= end_date

    # After end date, should return None
    end_exceeded_rule = {
        "frequency": "daily",
        "end_date": (today - timedelta(days=1)).date().isoformat()
    }
    next_occ = RecurrenceService.calculate_next_occurrence(end_exceeded_rule)
    assert next_occ is None


def test_recurring_task_end_date_passed(session: Session):
    """Test that recurrence stops after end date."""
    user_id = uuid4()
    past_date = datetime.utcnow() - timedelta(days=5)

    task = Task(
        user_id=user_id,
        title="Past recurring task",
        recurrence_rule={"frequency": "daily", "end_date": past_date.date().isoformat()},
    )
    session.add(task)
    session.commit()

    # Should return None because end date has passed
    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)
    assert next_occ is None


def test_non_recurring_task(session: Session):
    """Test that non-recurring tasks return None."""
    user_id = uuid4()

    task = Task(
        user_id=user_id,
        title="One-time task",
        priority="low",
        recurrence_rule=None,
    )
    session.add(task)
    session.commit()

    assert not RecurrenceService.is_recurring(task.recurrence_rule)
    next_occ = RecurrenceService.calculate_next_occurrence(task.recurrence_rule)
    assert next_occ is None


def test_validate_recurrence_rule():
    """Test recurrence rule validation."""
    # Valid rules
    valid, msg = RecurrenceService.validate_recurrence_rule({"frequency": "daily"})
    assert valid and msg == ""

    valid, msg = RecurrenceService.validate_recurrence_rule({
        "frequency": "weekly",
        "end_date": "2026-12-31"
    })
    assert valid and msg == ""

    # Invalid frequency
    valid, msg = RecurrenceService.validate_recurrence_rule({"frequency": "invalid"})
    assert not valid and "Invalid frequency" in msg

    # Invalid end_date
    valid, msg = RecurrenceService.validate_recurrence_rule({
        "frequency": "daily",
        "end_date": "not-a-date"
    })
    assert not valid and "Invalid end_date" in msg


def test_task_with_all_phase_v_fields(session: Session):
    """Test creating task with all Phase V fields."""
    user_id = uuid4()

    task = Task(
        user_id=user_id,
        title="Complex recurring task",
        description="A task with all Phase V features",
        priority="high",
        tags=["urgent", "work"],
        due_at=datetime.utcnow() + timedelta(days=1),
        remind_at=datetime.utcnow() + timedelta(hours=1),
        recurrence_rule={"frequency": "weekly", "end_date": "2026-12-31"},
        next_occurrence_at=datetime.utcnow() + timedelta(weeks=1),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Verify all fields persisted
    assert task.title == "Complex recurring task"
    assert task.priority == "high"
    assert "urgent" in task.tags
    assert task.due_at is not None
    assert task.remind_at is not None
    assert task.recurrence_rule["frequency"] == "weekly"
    assert task.next_occurrence_at is not None


def test_monthly_edge_case_feb_31(session: Session):
    """Test monthly recurrence edge case (e.g., Jan 31 -> Feb)."""
    # Create task on Jan 31
    jan_31 = datetime(2026, 1, 31, 10, 0, 0)
    rule = {"frequency": "monthly"}

    next_occ = RecurrenceService.calculate_next_occurrence(rule, jan_31)

    # Should be Feb 28 or 29 (not March 3 or error)
    assert next_occ is not None
    assert next_occ.month == 2
    assert next_occ.day <= 29  # Valid day for February


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
