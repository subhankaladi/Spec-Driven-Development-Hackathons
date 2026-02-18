from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import pytz
from enum import Enum
from task_recurrence_patterns import RecurrencePatternType, RecurrenceRule, RecurrencePatternCalculator

# Database Models
class ReminderMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

class ReminderFrequency(str, Enum):
    ONETIME = "onetime"
    RECURRING = "recurring"

class ReminderPreference(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str
    reminder_method: ReminderMethod
    is_enabled: bool = True
    lead_time_minutes: int = 15  # How early to send reminder
    timezone: str = "UTC"
    custom_message_template: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReminderConfiguration(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str
    user_id: str
    reminder_method: ReminderMethod
    frequency: ReminderFrequency
    lead_time_minutes: int = 15
    timezone: str = "UTC"
    custom_message: Optional[str] = None
    recurrence_rule: Optional[str] = None  # JSON string of RecurrenceRule
    is_active: bool = True
    next_reminder_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserNotificationSettings(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str
    email_notifications: bool = True
    sms_notifications: bool = True
    push_notifications: bool = True
    webhook_notifications: bool = True
    in_app_notifications: bool = True
    quiet_hours_start: Optional[str] = "22:00"  # HH:MM format
    quiet_hours_end: Optional[str] = "07:00"    # HH:MM format
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class ReminderPreferenceCreate(BaseModel):
    user_id: str
    reminder_method: ReminderMethod
    is_enabled: bool = True
    lead_time_minutes: int = 15
    timezone: str = "UTC"
    custom_message_template: Optional[str] = None

class ReminderPreferenceUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    lead_time_minutes: Optional[int] = None
    timezone: Optional[str] = None
    custom_message_template: Optional[str] = None

class ReminderConfigurationCreate(BaseModel):
    task_id: str
    user_id: str
    reminder_method: ReminderMethod
    frequency: ReminderFrequency
    lead_time_minutes: int = 15
    timezone: str = "UTC"
    custom_message: Optional[str] = None
    recurrence_rule: Optional[Dict[str, Any]] = None  # Will be converted to JSON

class ReminderConfigurationUpdate(BaseModel):
    is_active: Optional[bool] = None
    lead_time_minutes: Optional[int] = None
    timezone: Optional[str] = None
    custom_message: Optional[str] = None
    recurrence_rule: Optional[Dict[str, Any]] = None

class UserNotificationSettingsCreate(BaseModel):
    user_id: str
    email_notifications: bool = True
    sms_notifications: bool = True
    push_notifications: bool = True
    webhook_notifications: bool = True
    in_app_notifications: bool = True
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "07:00"
    timezone: str = "UTC"

class UserNotificationSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    webhook_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class ReminderPreferenceResponse(ReminderPreference):
    pass

class ReminderConfigurationResponse(ReminderConfiguration):
    pass

class UserNotificationSettingsResponse(UserNotificationSettings):
    pass

# Reminder Configuration Service
class ReminderConfigService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_user_preferences(self, user_id: str) -> List[ReminderPreferenceResponse]:
        """Get all reminder preferences for a user."""
        preferences = self.db_session.exec(
            select(ReminderPreference).where(ReminderPreference.user_id == user_id)
        ).all()
        return [ReminderPreferenceResponse.from_orm(p) for p in preferences]

    async def get_user_preference(
        self, user_id: str, method: ReminderMethod
    ) -> Optional[ReminderPreferenceResponse]:
        """Get specific reminder preference for a user."""
        preference = self.db_session.exec(
            select(ReminderPreference).where(
                ReminderPreference.user_id == user_id,
                ReminderPreference.reminder_method == method
            )
        ).first()

        if preference:
            return ReminderPreferenceResponse.from_orm(preference)
        return None

    async def set_user_preference(
        self, preference_data: ReminderPreferenceCreate
    ) -> ReminderPreferenceResponse:
        """Set or update reminder preference for a user."""
        # Check if preference already exists
        existing = self.db_session.exec(
            select(ReminderPreference).where(
                ReminderPreference.user_id == preference_data.user_id,
                ReminderPreference.reminder_method == preference_data.reminder_method
            )
        ).first()

        if existing:
            # Update existing
            for field, value in preference_data.dict().items():
                if field != 'user_id' and field != 'reminder_method':
                    setattr(existing, field, value)
            self.db_session.add(existing)
            self.db_session.commit()
            self.db_session.refresh(existing)
            return ReminderPreferenceResponse.from_orm(existing)
        else:
            # Create new
            preference = ReminderPreference(**preference_data.dict())
            self.db_session.add(preference)
            self.db_session.commit()
            self.db_session.refresh(preference)
            return ReminderPreferenceResponse.from_orm(preference)

    async def get_task_reminders(self, task_id: str) -> List[ReminderConfigurationResponse]:
        """Get all reminder configurations for a task."""
        configs = self.db_session.exec(
            select(ReminderConfiguration).where(ReminderConfiguration.task_id == task_id)
        ).all()
        return [ReminderConfigurationResponse.from_orm(c) for c in configs]

    async def get_user_task_reminders(
        self, user_id: str, task_id: str
    ) -> List[ReminderConfigurationResponse]:
        """Get reminder configurations for a specific user's task."""
        configs = self.db_session.exec(
            select(ReminderConfiguration).where(
                ReminderConfiguration.user_id == user_id,
                ReminderConfiguration.task_id == task_id
            )
        ).all()
        return [ReminderConfigurationResponse.from_orm(c) for c in configs]

    async def create_reminder_configuration(
        self, config_data: ReminderConfigurationCreate
    ) -> ReminderConfigurationResponse:
        """Create a new reminder configuration."""
        # Convert recurrence rule to JSON string if provided
        recurrence_json = None
        if config_data.recurrence_rule:
            recurrence_json = json.dumps(config_data.recurrence_rule)

        config = ReminderConfiguration(
            task_id=config_data.task_id,
            user_id=config_data.user_id,
            reminder_method=config_data.reminder_method,
            frequency=config_data.frequency,
            lead_time_minutes=config_data.lead_time_minutes,
            timezone=config_data.timezone,
            custom_message=config_data.custom_message,
            recurrence_rule=recurrence_json
        )

        # Calculate next reminder time if recurring
        if config.frequency == ReminderFrequency.RECURRING and recurrence_json:
            try:
                rule_dict = json.loads(recurrence_json)
                rule = RecurrenceRule(**rule_dict)
                calc = RecurrencePatternCalculator(timezone=config.timezone)

                # Calculate next occurrence based on task schedule
                # For now, we'll use current time as start point
                start_time = datetime.now(pytz.timezone(config.timezone)) + timedelta(minutes=config.lead_time_minutes)
                next_time = calc.calculate_next_occurrence(start_time, rule)
                config.next_reminder_time = next_time
            except Exception as e:
                print(f"Error calculating next reminder time: {e}")

        self.db_session.add(config)
        self.db_session.commit()
        self.db_session.refresh(config)

        return ReminderConfigurationResponse.from_orm(config)

    async def update_reminder_configuration(
        self, config_id: str, config_update: ReminderConfigurationUpdate
    ) -> ReminderConfigurationResponse:
        """Update a reminder configuration."""
        config = self.db_session.get(ReminderConfiguration, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Reminder configuration not found")

        # Update fields
        update_data = config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'recurrence_rule' and value is not None:
                setattr(config, field, json.dumps(value))
            else:
                setattr(config, field, value)

        # Recalculate next reminder time if recurrence rule changed
        if 'recurrence_rule' in update_data and config.frequency == ReminderFrequency.RECURRING:
            try:
                rule_dict = json.loads(config.recurrence_rule)
                rule = RecurrenceRule(**rule_dict)
                calc = RecurrencePatternCalculator(timezone=config.timezone)

                start_time = datetime.now(pytz.timezone(config.timezone)) + timedelta(minutes=config.lead_time_minutes)
                next_time = calc.calculate_next_occurrence(start_time, rule)
                config.next_reminder_time = next_time
            except Exception as e:
                print(f"Error recalculating next reminder time: {e}")

        self.db_session.add(config)
        self.db_session.commit()
        self.db_session.refresh(config)

        return ReminderConfigurationResponse.from_orm(config)

    async def get_user_notification_settings(
        self, user_id: str
    ) -> Optional[UserNotificationSettingsResponse]:
        """Get notification settings for a user."""
        settings = self.db_session.exec(
            select(UserNotificationSettings).where(UserNotificationSettings.user_id == user_id)
        ).first()

        if settings:
            return UserNotificationSettingsResponse.from_orm(settings)
        return None

    async def set_user_notification_settings(
        self, settings_data: UserNotificationSettingsCreate
    ) -> UserNotificationSettingsResponse:
        """Set or update notification settings for a user."""
        # Check if settings already exist
        existing = self.db_session.exec(
            select(UserNotificationSettings).where(
                UserNotificationSettings.user_id == settings_data.user_id
            )
        ).first()

        if existing:
            # Update existing
            for field, value in settings_data.dict().items():
                if field != 'user_id':
                    setattr(existing, field, value)
            self.db_session.add(existing)
            self.db_session.commit()
            self.db_session.refresh(existing)
            return UserNotificationSettingsResponse.from_orm(existing)
        else:
            # Create new
            settings = UserNotificationSettings(**settings_data.dict())
            self.db_session.add(settings)
            self.db_session.commit()
            self.db_session.refresh(settings)
            return UserNotificationSettingsResponse.from_orm(settings)

    async def should_send_notification(
        self, user_id: str, method: ReminderMethod, current_time: datetime = None
    ) -> bool:
        """Check if notification should be sent based on user settings."""
        if current_time is None:
            current_time = datetime.now()

        # Get user settings
        settings = await self.get_user_notification_settings(user_id)
        if not settings:
            # Default to allowing all notifications
            return True

        # Check if this notification method is enabled
        method_enabled = getattr(settings, f"{method.value.lower()}_notifications", True)
        if not method_enabled:
            return False

        # Check quiet hours
        if settings.quiet_hours_start and settings.quiet_hours_end:
            tz = pytz.timezone(settings.timezone)

            # Convert current time to user's timezone
            if current_time.tzinfo is None:
                current_time = pytz.UTC.localize(current_time)
            current_time = current_time.astimezone(tz)

            current_hour_min = current_time.strftime("%H:%M")

            # Parse quiet hours
            start_hour_min = settings.quiet_hours_start
            end_hour_min = settings.quiet_hours_end

            # Check if current time is in quiet hours
            if start_hour_min <= end_hour_min:
                # Normal range (e.g., 22:00 to 07:00)
                if start_hour_min <= current_hour_min <= end_hour_min:
                    return False
            else:
                # Overnight range (e.g., 22:00 to 07:00 next day)
                if current_hour_min >= start_hour_min or current_hour_min <= end_hour_min:
                    return False

        return True

# FastAPI Application
app = FastAPI(title="Reminder Configuration API", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./reminder_config.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    # Create tables
    SQLModel.metadata.create_all(engine)

# API Endpoints for Reminder Preferences
@app.post("/users/{user_id}/preferences/", response_model=ReminderPreferenceResponse)
async def create_reminder_preference(
    user_id: str,
    preference_data: ReminderPreferenceCreate,
    db: Session = Depends(get_db)
):
    """Create or update a reminder preference for a user."""
    service = ReminderConfigService(db)

    # Verify user_id matches in path and body
    if user_id != preference_data.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")

    return await service.set_user_preference(preference_data)

@app.get("/users/{user_id}/preferences/", response_model=List[ReminderPreferenceResponse])
async def get_user_reminder_preferences(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all reminder preferences for a user."""
    service = ReminderConfigService(db)
    return await service.get_user_preferences(user_id)

@app.get("/users/{user_id}/preferences/{method}", response_model=ReminderPreferenceResponse)
async def get_user_reminder_preference(
    user_id: str,
    method: ReminderMethod,
    db: Session = Depends(get_db)
):
    """Get specific reminder preference for a user."""
    service = ReminderConfigService(db)
    preference = await service.get_user_preference(user_id, method)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preference

@app.put("/users/{user_id}/preferences/{method}", response_model=ReminderPreferenceResponse)
async def update_reminder_preference(
    user_id: str,
    method: ReminderMethod,
    preference_update: ReminderPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """Update a reminder preference for a user."""
    service = ReminderConfigService(db)

    # Get existing preference
    existing = await service.get_user_preference(user_id, method)
    if not existing:
        raise HTTPException(status_code=404, detail="Preference not found")

    # Update the preference
    update_data = preference_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    db.add(existing)
    db.commit()
    db.refresh(existing)

    return ReminderPreferenceResponse.from_orm(existing)

# API Endpoints for Reminder Configurations
@app.post("/reminders/config/", response_model=ReminderConfigurationResponse)
async def create_reminder_configuration(
    config_data: ReminderConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create a new reminder configuration."""
    service = ReminderConfigService(db)
    return await service.create_reminder_configuration(config_data)

@app.get("/reminders/config/{config_id}", response_model=ReminderConfigurationResponse)
async def get_reminder_configuration(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific reminder configuration."""
    config = db.get(ReminderConfiguration, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Reminder configuration not found")
    return ReminderConfigurationResponse.from_orm(config)

@app.put("/reminders/config/{config_id}", response_model=ReminderConfigurationResponse)
async def update_reminder_configuration(
    config_id: str,
    config_update: ReminderConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Update a reminder configuration."""
    service = ReminderConfigService(db)
    return await service.update_reminder_configuration(config_id, config_update)

@app.get("/reminders/config/task/{task_id}", response_model=List[ReminderConfigurationResponse])
async def get_task_reminder_configurations(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get all reminder configurations for a task."""
    service = ReminderConfigService(db)
    return await service.get_task_reminders(task_id)

@app.get("/reminders/config/user/{user_id}/task/{task_id}", response_model=List[ReminderConfigurationResponse])
async def get_user_task_reminder_configurations(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get reminder configurations for a specific user's task."""
    service = ReminderConfigService(db)
    return await service.get_user_task_reminders(user_id, task_id)

# API Endpoints for User Notification Settings
@app.post("/users/{user_id}/notification-settings/", response_model=UserNotificationSettingsResponse)
async def create_user_notification_settings(
    user_id: str,
    settings_data: UserNotificationSettingsCreate,
    db: Session = Depends(get_db)
):
    """Create or update notification settings for a user."""
    service = ReminderConfigService(db)

    # Verify user_id matches in path and body
    if user_id != settings_data.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")

    return await service.set_user_notification_settings(settings_data)

@app.get("/users/{user_id}/notification-settings/", response_model=UserNotificationSettingsResponse)
async def get_user_notification_settings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get notification settings for a user."""
    service = ReminderConfigService(db)
    settings = await service.get_user_notification_settings(user_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Notification settings not found")
    return settings

@app.put("/users/{user_id}/notification-settings/", response_model=UserNotificationSettingsResponse)
async def update_user_notification_settings(
    user_id: str,
    settings_update: UserNotificationSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update notification settings for a user."""
    service = ReminderConfigService(db)

    # Get existing settings
    existing = await service.get_user_notification_settings(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Notification settings not found")

    # Update the settings
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    db.add(existing)
    db.commit()
    db.refresh(existing)

    return UserNotificationSettingsResponse.from_orm(existing)

# Utility endpoint to check if notification should be sent
@app.get("/users/{user_id}/should-notify/{method}")
async def check_notification_permission(
    user_id: str,
    method: ReminderMethod,
    db: Session = Depends(get_db)
):
    """Check if notification should be sent based on user settings."""
    service = ReminderConfigService(db)
    should_send = await service.should_send_notification(user_id, method)
    return {"should_send": should_send}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)