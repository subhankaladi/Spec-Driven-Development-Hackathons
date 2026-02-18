from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import asyncio
import json
import uuid
import logging
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pytz
import httpx
from enum import Enum
from abc import ABC, abstractmethod
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis.asyncio as redis

# Database Models
class DeliveryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"

class DeliveryMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

class ReminderDelivery(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str
    occurrence_id: str
    delivery_method: DeliveryMethod
    recipient: str  # Email address, phone number, device token, etc.
    subject: Optional[str] = None
    message: str
    scheduled_time: datetime
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 1  # 1-5, 5 being highest priority
    channel_specific_data: Optional[str] = None  # JSON for method-specific data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryChannelConfig(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    channel_type: DeliveryMethod
    config_data: str  # JSON configuration
    is_enabled: bool = True
    rate_limit_per_minute: int = 10
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class ReminderDeliveryCreate(BaseModel):
    task_id: str
    occurrence_id: str
    delivery_method: DeliveryMethod
    recipient: str
    subject: Optional[str] = None
    message: str
    scheduled_time: datetime
    priority: int = 1

class ReminderDeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    retry_count: Optional[int] = None

class DeliveryChannelConfigCreate(BaseModel):
    channel_type: DeliveryMethod
    config_data: Dict[str, Any]
    is_enabled: bool = True
    rate_limit_per_minute: int = 10

class DeliveryChannelConfigUpdate(BaseModel):
    config_data: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = None

class ReminderDeliveryResponse(ReminderDelivery):
    pass

class DeliveryChannelConfigResponse(DeliveryChannelConfig):
    pass

# Abstract Base Classes for Delivery Channels
class DeliveryChannel(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send the reminder using this channel."""
        pass

    @abstractmethod
    async def validate_recipient(self, recipient: str) -> bool:
        """Validate if the recipient is valid for this channel."""
        pass

class EmailDeliveryChannel(DeliveryChannel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_host = config.get('smtp_host', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username')
        self.smtp_password = config.get('smtp_password')
        self.smtp_tls = config.get('smtp_tls', True)
        self.from_address = config.get('from_address')

    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send email reminder."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_address
            msg['To'] = delivery.recipient
            msg['Subject'] = delivery.subject or f"Reminder: {delivery.message[:50]}..."

            msg.attach(MIMEText(delivery.message, 'html'))

            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_tls
            ) as server:
                if self.smtp_username and self.smtp_password:
                    await server.login(self.smtp_username, self.smtp_password)

                await server.send_message(msg)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, recipient) is not None

class SMSTextDeliveryChannel(DeliveryChannel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.sender_id = config.get('sender_id', 'TODOAPP')
        self.provider_url = config.get('provider_url', 'https://api.smsprovider.com/send')

    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send SMS reminder."""
        try:
            payload = {
                'to': delivery.recipient,
                'message': delivery.message,
                'sender': self.sender_id,
                'api_key': self.api_key
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.provider_url,
                    json=payload,
                    headers={'Authorization': f'Bearer {self.api_secret}'}
                )

            return response.status_code in [200, 201]
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format."""
        import re
        # Simple validation for international format (+1234567890)
        pattern = r'^\+\d{10,15}$'
        return re.match(pattern, recipient) is not None

class PushNotificationDeliveryChannel(DeliveryChannel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fcm_server_key = config.get('fcm_server_key')
        self.apn_auth_key = config.get('apn_auth_key')
        self.apn_team_id = config.get('apn_team_id')
        self.apn_key_id = config.get('apn_key_id')

    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send push notification."""
        try:
            # Determine if it's FCM (Android) or APN (iOS) based on token format
            if delivery.recipient.startswith('e') or len(delivery.recipient) > 100:
                # Likely FCM token
                return await self._send_fcm_push(delivery)
            else:
                # Likely APN token
                return await self._send_apn_push(delivery)
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {e}")
            return False

    async def _send_fcm_push(self, delivery: ReminderDelivery) -> bool:
        """Send FCM push notification."""
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "registration_ids": [delivery.recipient],
            "notification": {
                "title": "Task Reminder",
                "body": delivery.message
            },
            "data": {
                "task_id": delivery.task_id,
                "occurrence_id": delivery.occurrence_id,
                "timestamp": delivery.scheduled_time.isoformat()
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fcm.googleapis.com/fcm/send",
                headers=headers,
                json=payload
            )

        return response.status_code == 200

    async def _send_apn_push(self, delivery: ReminderDelivery) -> bool:
        """Send APN push notification."""
        # This would require more complex implementation with JWT authentication
        # For now, we'll simulate the call
        self.logger.info(f"Simulating APN push to {delivery.recipient}")
        return True

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate push notification token format."""
        # FCM tokens are typically long alphanumeric strings
        # APN tokens are typically 64-character hex strings
        return len(recipient) >= 32 and len(recipient) <= 256

class WebhookDeliveryChannel(DeliveryChannel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.auth_header = config.get('auth_header')
        self.auth_token = config.get('auth_token')

    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send webhook reminder."""
        try:
            payload = {
                "task_id": delivery.task_id,
                "occurrence_id": delivery.occurrence_id,
                "message": delivery.message,
                "scheduled_time": delivery.scheduled_time.isoformat(),
                "recipient": delivery.recipient
            }

            headers = {'Content-Type': 'application/json'}
            if self.auth_token:
                headers[self.auth_header or 'Authorization'] = f'Bearer {self.auth_token}'

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    delivery.recipient,  # URL is stored in recipient for webhooks
                    json=payload,
                    headers=headers
                )

            return response.status_code in [200, 201, 202]
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            return False

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate webhook URL."""
        import re
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+$'
        return re.match(pattern, recipient) is not None

class InAppDeliveryChannel(DeliveryChannel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # In-app notifications might use a message queue or database
        self.message_queue_url = config.get('message_queue_url')

    async def send(self, delivery: ReminderDelivery) -> bool:
        """Send in-app notification."""
        try:
            # For in-app notifications, we might store in a database or message queue
            # This is a simplified implementation
            self.logger.info(f"In-app notification sent to user: {delivery.recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send in-app notification: {e}")
            return False

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate in-app recipient (user ID)."""
        # For in-app notifications, recipient is typically a user ID
        return len(recipient) > 0

# Delivery Manager
class ReminderDeliveryManager:
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.channels: Dict[DeliveryMethod, DeliveryChannel] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize channels from configuration
        self._initialize_channels()

    def _initialize_channels(self):
        """Initialize delivery channels from database configuration."""
        configs = self.db_session.exec(select(DeliveryChannelConfig)).all()

        for config in configs:
            if not config.is_enabled:
                continue

            config_data = json.loads(config.config_data)

            if config.channel_type == DeliveryMethod.EMAIL:
                self.channels[config.channel_type] = EmailDeliveryChannel(config_data)
            elif config.channel_type == DeliveryMethod.SMS:
                self.channels[config.channel_type] = SMSTextDeliveryChannel(config_data)
            elif config.channel_type == DeliveryMethod.PUSH:
                self.channels[config.channel_type] = PushNotificationDeliveryChannel(config_data)
            elif config.channel_type == DeliveryMethod.WEBHOOK:
                self.channels[config.channel_type] = WebhookDeliveryChannel(config_data)
            elif config.channel_type == DeliveryMethod.IN_APP:
                self.channels[config.channel_type] = InAppDeliveryChannel(config_data)

    async def schedule_delivery(self, delivery_data: ReminderDeliveryCreate) -> ReminderDeliveryResponse:
        """Schedule a reminder for delivery."""
        # Validate recipient for the specified delivery method
        channel = self.channels.get(delivery_data.delivery_method)
        if channel:
            is_valid = await channel.validate_recipient(delivery_data.recipient)
            if not is_valid:
                raise ValueError(f"Invalid recipient for {delivery_data.delivery_method}: {delivery_data.recipient}")

        delivery = ReminderDelivery(
            task_id=delivery_data.task_id,
            occurrence_id=delivery_data.occurrence_id,
            delivery_method=delivery_data.delivery_method,
            recipient=delivery_data.recipient,
            subject=delivery_data.subject,
            message=delivery_data.message,
            scheduled_time=delivery_data.scheduled_time,
            priority=delivery_data.priority
        )

        self.db_session.add(delivery)
        self.db_session.commit()
        self.db_session.refresh(delivery)

        return ReminderDeliveryResponse.from_orm(delivery)

    async def process_deliveries(self, batch_size: int = 10):
        """Process pending deliveries."""
        # Get pending deliveries ordered by priority and scheduled time
        pending_deliveries = self.db_session.exec(
            select(ReminderDelivery)
            .where(
                ReminderDelivery.status.in_([DeliveryStatus.PENDING, DeliveryStatus.PROCESSING]),
                ReminderDelivery.scheduled_time <= datetime.utcnow(),
                ReminderDelivery.retry_count < ReminderDelivery.max_retries
            )
            .order_by(ReminderDelivery.priority.desc(), ReminderDelivery.scheduled_time.asc())
            .limit(batch_size)
        ).all()

        for delivery in pending_deliveries:
            await self._process_single_delivery(delivery)

    async def _process_single_delivery(self, delivery: ReminderDelivery):
        """Process a single delivery."""
        try:
            # Mark as processing
            delivery.status = DeliveryStatus.PROCESSING
            delivery.updated_at = datetime.utcnow()
            self.db_session.add(delivery)
            self.db_session.commit()

            # Get the appropriate channel
            channel = self.channels.get(delivery.delivery_method)
            if not channel:
                self.logger.error(f"No channel found for method: {delivery.delivery_method}")
                delivery.status = DeliveryStatus.FAILED
                delivery.retry_count += 1
                self.db_session.add(delivery)
                self.db_session.commit()
                return

            # Send the delivery
            success = await channel.send(delivery)

            if success:
                delivery.status = DeliveryStatus.SENT
                delivery.sent_time = datetime.utcnow()
            else:
                delivery.status = DeliveryStatus.FAILED
                delivery.retry_count += 1

            delivery.updated_at = datetime.utcnow()
            self.db_session.add(delivery)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Error processing delivery {delivery.id}: {e}")
            # Increment retry count and mark as failed
            delivery.retry_count += 1
            if delivery.retry_count >= delivery.max_retries:
                delivery.status = DeliveryStatus.FAILED
            else:
                delivery.status = DeliveryStatus.PENDING  # Will be retried

            delivery.updated_at = datetime.utcnow()
            self.db_session.add(delivery)
            self.db_session.commit()

    async def update_delivery_status(self, delivery_id: str, status: DeliveryStatus):
        """Update the status of a delivery."""
        delivery = self.db_session.get(ReminderDelivery, delivery_id)
        if delivery:
            delivery.status = status
            delivery.updated_at = datetime.utcnow()
            self.db_session.add(delivery)
            self.db_session.commit()

    async def get_channel_config(self, channel_type: DeliveryMethod) -> Optional[DeliveryChannelConfigResponse]:
        """Get configuration for a specific delivery channel."""
        config = self.db_session.exec(
            select(DeliveryChannelConfig)
            .where(DeliveryChannelConfig.channel_type == channel_type)
        ).first()

        if config:
            return DeliveryChannelConfigResponse.from_orm(config)
        return None

    async def update_channel_config(self, channel_type: DeliveryMethod, config_data: Dict[str, Any]) -> DeliveryChannelConfigResponse:
        """Update configuration for a delivery channel."""
        config = self.db_session.exec(
            select(DeliveryChannelConfig)
            .where(DeliveryChannelConfig.channel_type == channel_type)
        ).first()

        if config:
            config.config_data = json.dumps(config_data)
            config.updated_at = datetime.utcnow()
        else:
            config = DeliveryChannelConfig(
                channel_type=channel_type,
                config_data=json.dumps(config_data)
            )
            self.db_session.add(config)

        self.db_session.commit()
        self.db_session.refresh(config)

        # Reinitialize the channel with new config
        self._initialize_channels()

        return DeliveryChannelConfigResponse.from_orm(config)

# FastAPI Application
app = FastAPI(title="Reminder Delivery Mechanism", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./reminder_delivery.db"
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

    # Initialize with default channel configurations
    async with Session(engine) as db:
        existing = db.exec(select(DeliveryChannelConfig)).first()
        if not existing:
            # Add default configurations
            default_configs = [
                DeliveryChannelConfig(
                    channel_type=DeliveryMethod.EMAIL,
                    config_data=json.dumps({
                        "smtp_host": "localhost",
                        "smtp_port": 587,
                        "smtp_tls": True,
                        "from_address": "noreply@todoapp.com"
                    }),
                    is_enabled=False  # Disabled by default
                ),
                DeliveryChannelConfig(
                    channel_type=DeliveryMethod.SMS,
                    config_data=json.dumps({
                        "provider_url": "https://api.smsprovider.com/send",
                        "sender_id": "TODOAPP"
                    }),
                    is_enabled=False  # Disabled by default
                ),
                DeliveryChannelConfig(
                    channel_type=DeliveryMethod.PUSH,
                    config_data=json.dumps({
                        "fcm_server_key": "your_fcm_server_key_here"
                    }),
                    is_enabled=False  # Disabled by default
                )
            ]

            for config in default_configs:
                db.add(config)
            db.commit()

# API Endpoints
@app.post("/deliveries/", response_model=ReminderDeliveryResponse)
async def schedule_reminder_delivery(
    delivery_data: ReminderDeliveryCreate,
    db: Session = Depends(get_db)
):
    """Schedule a reminder for delivery."""
    manager = ReminderDeliveryManager(db, await redis_client)
    return await manager.schedule_delivery(delivery_data)

@app.get("/deliveries/{delivery_id}", response_model=ReminderDeliveryResponse)
async def get_reminder_delivery(
    delivery_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific delivery."""
    delivery = db.get(ReminderDelivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return ReminderDeliveryResponse.from_orm(delivery)

@app.put("/deliveries/{delivery_id}", response_model=ReminderDeliveryResponse)
async def update_delivery_status(
    delivery_id: str,
    status: DeliveryStatus = None,
    db: Session = Depends(get_db)
):
    """Update the status of a delivery."""
    delivery = db.get(ReminderDelivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    if status:
        delivery.status = status
        delivery.updated_at = datetime.utcnow()
        db.add(delivery)
        db.commit()
        db.refresh(delivery)

    return ReminderDeliveryResponse.from_orm(delivery)

@app.get("/deliveries/pending", response_model=List[ReminderDeliveryResponse])
async def get_pending_deliveries(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get pending deliveries."""
    deliveries = db.exec(
        select(ReminderDelivery)
        .where(ReminderDelivery.status == DeliveryStatus.PENDING)
        .order_by(ReminderDelivery.priority.desc(), ReminderDelivery.scheduled_time.asc())
        .limit(limit)
    ).all()
    return [ReminderDeliveryResponse.from_orm(d) for d in deliveries]

@app.post("/channels/{channel_type}/config", response_model=DeliveryChannelConfigResponse)
async def update_channel_config(
    channel_type: DeliveryMethod,
    config_data: DeliveryChannelConfigCreate,
    db: Session = Depends(get_db)
):
    """Update configuration for a delivery channel."""
    manager = ReminderDeliveryManager(db, await redis_client)
    return await manager.update_channel_config(channel_type, config_data.config_data)

@app.get("/channels/{channel_type}/config", response_model=DeliveryChannelConfigResponse)
async def get_channel_config(
    channel_type: DeliveryMethod,
    db: Session = Depends(get_db)
):
    """Get configuration for a delivery channel."""
    manager = ReminderDeliveryManager(db, await redis_client)
    config = await manager.get_channel_config(channel_type)
    if not config:
        raise HTTPException(status_code=404, detail="Channel configuration not found")
    return config

@app.post("/deliveries/process")
async def process_deliveries(
    batch_size: int = 10,
    db: Session = Depends(get_db)
):
    """Manually trigger processing of pending deliveries."""
    manager = ReminderDeliveryManager(db, await redis_client)
    await manager.process_deliveries(batch_size)
    return {"message": f"Processing completed for up to {batch_size} deliveries"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)