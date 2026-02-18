from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis.asyncio as redis
import logging
from enum import Enum
import httpx

# Database Models
class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"

class Reminder(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="recurringtask.id")
    occurrence_id: str = Field(foreign_key="taskoccurrence.id")
    notification_type: NotificationType
    recipient: str  # Email, phone number, device token, etc.
    message: str
    scheduled_time: datetime
    sent_time: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationTemplate(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    notification_type: NotificationType
    subject: Optional[str] = None
    body: str
    variables: Optional[str] = None  # JSON string of available variables
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class ReminderCreate(BaseModel):
    task_id: str
    occurrence_id: str
    notification_type: NotificationType
    recipient: str
    message: str
    scheduled_time: datetime

class ReminderUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    retry_count: Optional[int] = None

class ReminderResponse(Reminder):
    pass

class NotificationTemplateCreate(BaseModel):
    name: str
    notification_type: NotificationType
    subject: Optional[str] = None
    body: str
    variables: Optional[Dict[str, str]] = None
    is_default: bool = False

class NotificationTemplateResponse(NotificationTemplate):
    pass

# Notification Providers
class EmailProvider:
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            async with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False

class SMSProvider:
    def __init__(self, api_key: str, sender_id: str):
        self.api_key = api_key
        self.sender_id = sender_id

    async def send_sms(self, to_phone: str, message: str) -> bool:
        # In a real implementation, this would call an SMS API
        # For example, Twilio, AWS SNS, etc.
        print(f"Sending SMS to {to_phone}: {message}")
        return True  # Simulate successful send

class PushNotificationProvider:
    def __init__(self, fcm_server_key: str):
        self.fcm_server_key = fcm_server_key

    async def send_push(self, device_token: str, title: str, body: str) -> bool:
        # In a real implementation, this would call Firebase Cloud Messaging
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "to": device_token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers=headers,
                    json=payload
                )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to send push notification: {e}")
            return False

class WebhookProvider:
    async def send_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logging.error(f"Failed to send webhook: {e}")
            return False

# Reminder Service
class ReminderService:
    def __init__(
        self,
        db_session: Session,
        redis_client: redis.Redis,
        email_provider: Optional[EmailProvider] = None,
        sms_provider: Optional[SMSProvider] = None,
        push_provider: Optional[PushNotificationProvider] = None,
        webhook_provider: Optional[WebhookProvider] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.email_provider = email_provider
        self.sms_provider = sms_provider
        self.push_provider = push_provider
        self.webhook_provider = webhook_provider
        self.logger = logging.getLogger(__name__)

    async def process_pending_reminders(self):
        """Process all pending reminders that are due."""
        try:
            # Find all pending reminders that are due
            due_reminders = self.db_session.exec(
                select(Reminder).where(
                    Reminder.status == NotificationStatus.PENDING,
                    Reminder.scheduled_time <= datetime.utcnow(),
                    Reminder.retry_count < Reminder.max_retries
                )
            ).all()

            for reminder in due_reminders:
                await self.send_reminder(reminder)

        except Exception as e:
            self.logger.error(f"Error processing pending reminders: {e}")

    async def send_reminder(self, reminder: Reminder) -> bool:
        """Send a single reminder using the appropriate provider."""
        try:
            success = False

            if reminder.notification_type == NotificationType.EMAIL:
                if self.email_provider:
                    success = await self.email_provider.send_email(
                        reminder.recipient,
                        f"Reminder: {reminder.message[:50]}...",
                        reminder.message
                    )
            elif reminder.notification_type == NotificationType.SMS:
                if self.sms_provider:
                    success = await self.sms_provider.send_sms(
                        reminder.recipient,
                        reminder.message
                    )
            elif reminder.notification_type == NotificationType.PUSH:
                if self.push_provider:
                    success = await self.push_provider.send_push(
                        reminder.recipient,
                        "Task Reminder",
                        reminder.message
                    )
            elif reminder.notification_type == NotificationType.WEBHOOK:
                if self.webhook_provider:
                    success = await self.webhook_provider.send_webhook(
                        reminder.recipient,
                        {
                            "task_id": reminder.task_id,
                            "occurrence_id": reminder.occurrence_id,
                            "message": reminder.message,
                            "scheduled_time": reminder.scheduled_time.isoformat()
                        }
                    )

            # Update reminder status
            if success:
                reminder.status = NotificationStatus.SENT
                reminder.sent_time = datetime.utcnow()
            else:
                reminder.retry_count += 1
                if reminder.retry_count >= reminder.max_retries:
                    reminder.status = NotificationStatus.FAILED

            self.db_session.add(reminder)
            self.db_session.commit()

            return success

        except Exception as e:
            self.logger.error(f"Error sending reminder {reminder.id}: {e}")
            # Mark as failed after exception
            reminder.retry_count += 1
            if reminder.retry_count >= reminder.max_retries:
                reminder.status = NotificationStatus.FAILED
            self.db_session.add(reminder)
            self.db_session.commit()
            return False

    async def schedule_reminder(
        self,
        task_id: str,
        occurrence_id: str,
        notification_type: NotificationType,
        recipient: str,
        message: str,
        scheduled_time: datetime
    ) -> Reminder:
        """Schedule a new reminder."""
        reminder = Reminder(
            task_id=task_id,
            occurrence_id=occurrence_id,
            notification_type=notification_type,
            recipient=recipient,
            message=message,
            scheduled_time=scheduled_time
        )

        self.db_session.add(reminder)
        self.db_session.commit()
        self.db_session.refresh(reminder)

        return reminder

    async def get_reminder_templates(self, notification_type: Optional[NotificationType] = None) -> List[NotificationTemplate]:
        """Get available notification templates."""
        query = select(NotificationTemplate)
        if notification_type:
            query = query.where(NotificationTemplate.notification_type == notification_type)

        return self.db_session.exec(query).all()

    async def render_template(self, template_name: str, variables: Dict[str, Any]) -> tuple[str, str]:
        """Render a notification template with variables."""
        template = self.db_session.exec(
            select(NotificationTemplate).where(NotificationTemplate.name == template_name)
        ).first()

        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Replace variables in the template
        body = template.body
        subject = template.subject or ""

        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            body = body.replace(placeholder, str(var_value))
            subject = subject.replace(placeholder, str(var_value))

        return subject, body

# FastAPI Application
app = FastAPI(title="Reminder Notification System", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./reminders.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session

# Redis setup
redis_client = redis.from_url("redis://localhost:6379/0")

@app.on_event("startup")
async def on_startup():
    # Create tables
    SQLModel.metadata.create_all(engine)

    # Initialize with default templates
    async with Session(engine) as db:
        existing = db.exec(select(NotificationTemplate)).first()
        if not existing:
            # Add default templates
            default_templates = [
                NotificationTemplate(
                    name="task_reminder_email",
                    notification_type=NotificationType.EMAIL,
                    subject="Task Reminder: {task_title}",
                    body="<h2>Task Reminder</h2><p>You have a task due soon:</p><p><strong>{task_title}</strong></p><p>{task_description}</p><p>Scheduled for: {occurrence_date}</p>",
                    variables='{"task_title": "Task Title", "task_description": "Task Description", "occurrence_date": "Occurrence Date"}',
                    is_default=True
                ),
                NotificationTemplate(
                    name="task_reminder_sms",
                    notification_type=NotificationType.SMS,
                    subject=None,
                    body="REMINDER: {task_title} - {task_description}. Due: {occurrence_date}",
                    variables='{"task_title": "Task Title", "task_description": "Task Description", "occurrence_date": "Occurrence Date"}',
                    is_default=True
                )
            ]

            for template in default_templates:
                db.add(template)
            db.commit()

# API Endpoints
@app.post("/reminders/", response_model=ReminderResponse)
async def create_reminder(reminder_data: ReminderCreate, db: Session = Depends(get_db)):
    """Create a new reminder."""
    # Validate scheduled time is in the future
    if reminder_data.scheduled_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    reminder = Reminder(
        task_id=reminder_data.task_id,
        occurrence_id=reminder_data.occurrence_id,
        notification_type=reminder_data.notification_type,
        recipient=reminder_data.recipient,
        message=reminder_data.message,
        scheduled_time=reminder_data.scheduled_time
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder

@app.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str, db: Session = Depends(get_db)):
    """Get a specific reminder."""
    reminder = db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@app.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_db)
):
    """Update a reminder."""
    reminder = db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Update fields that were provided
    update_data = reminder_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder

@app.get("/reminders/task/{task_id}", response_model=List[ReminderResponse])
async def get_task_reminders(task_id: str, db: Session = Depends(get_db)):
    """Get all reminders for a specific task."""
    reminders = db.exec(
        select(Reminder).where(Reminder.task_id == task_id)
    ).all()
    return reminders

@app.get("/reminders/user/{user_id}", response_model=List[ReminderResponse])
async def get_user_reminders(user_id: str, db: Session = Depends(get_db)):
    """Get all reminders for a user (through task associations)."""
    # This would require joining with tasks table in a real implementation
    # For now, returning all reminders - in a real app, this would be filtered by user
    reminders = db.exec(select(Reminder)).all()
    return reminders

@app.post("/reminders/{reminder_id}/resend")
async def resend_reminder(reminder_id: str, db: Session = Depends(get_db)):
    """Resend a specific reminder."""
    reminder = db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Reset status and retry count to allow resending
    reminder.status = NotificationStatus.PENDING
    reminder.retry_count = 0
    reminder.sent_time = None

    db.add(reminder)
    db.commit()

    return {"message": "Reminder reset for resending"}

@app.get("/templates/", response_model=List[NotificationTemplateResponse])
async def get_templates(
    notification_type: Optional[NotificationType] = None,
    db: Session = Depends(get_db)
):
    """Get available notification templates."""
    query = select(NotificationTemplate)
    if notification_type:
        query = query.where(NotificationTemplate.notification_type == notification_type)

    templates = db.exec(query).all()
    return templates

@app.post("/templates/", response_model=NotificationTemplateResponse)
async def create_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification template."""
    template = NotificationTemplate(
        name=template_data.name,
        notification_type=template_data.notification_type,
        subject=template_data.subject,
        body=template_data.body,
        variables=json.dumps(template_data.variables) if template_data.variables else None,
        is_default=template_data.is_default
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template

@app.post("/notifications/process")
async def process_notifications(db: Session = Depends(get_db)):
    """Manually trigger the notification processor."""
    # In a real implementation, you would inject actual providers
    # For now, we'll create dummy providers for demonstration
    email_provider = EmailProvider("smtp.example.com", 587, "user@example.com", "password")
    sms_provider = SMSProvider("api_key", "sender")
    push_provider = PushNotificationProvider("server_key")
    webhook_provider = WebhookProvider()

    service = ReminderService(
        db_session=db,
        redis_client=await redis_client,
        email_provider=email_provider,
        sms_provider=sms_provider,
        push_provider=push_provider,
        webhook_provider=webhook_provider
    )

    await service.process_pending_reminders()
    return {"message": "Pending notifications processed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)