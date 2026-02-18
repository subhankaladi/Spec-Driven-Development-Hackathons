from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import asyncio
import json
import uuid
import logging
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pytz
import redis.asyncio as redis
from enum import Enum
import hashlib
import time
from dataclasses import dataclass

# Database Models
class SyncOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"

class SyncStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class InstanceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class TaskSyncRecord(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str
    operation: SyncOperation
    instance_id: str  # Originating instance
    target_instances: str  # JSON list of target instance IDs
    payload: str  # JSON payload of the change
    status: SyncStatus = SyncStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3

class InstanceRegistry(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    instance_id: str
    instance_name: str
    instance_type: str  # scheduler, api, worker, etc.
    host: str
    port: int
    status: InstanceStatus = InstanceStatus.ACTIVE
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    registered_at: datetime = Field(default_factory=datetime.utcnow)

class TaskLock(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str
    instance_id: str  # Instance holding the lock
    lock_expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Models for API
class SyncRequest(BaseModel):
    task_id: str
    operation: SyncOperation
    payload: Dict[str, Any]
    target_instances: Optional[List[str]] = None

class InstanceRegistration(BaseModel):
    instance_id: str
    instance_name: str
    instance_type: str
    host: str
    port: int

class TaskSyncResponse(BaseModel):
    sync_id: str
    task_id: str
    operation: SyncOperation
    status: SyncStatus
    message: str

class InstanceInfo(BaseModel):
    id: str
    instance_id: str
    instance_name: str
    instance_type: str
    host: str
    port: int
    status: InstanceStatus
    last_heartbeat: datetime

# Task Synchronization Service
class TaskSynchronizationService:
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.instance_id = str(uuid.uuid4())
        self.logger = logging.getLogger(self.__class__.__name__)
        self.lock_timeout = 30  # seconds

    async def register_instance(self, registration: InstanceRegistration) -> InstanceInfo:
        """Register an instance in the cluster."""
        # Check if instance already exists
        existing = self.db_session.exec(
            select(InstanceRegistry).where(InstanceRegistry.instance_id == registration.instance_id)
        ).first()

        if existing:
            # Update existing registration
            existing.instance_name = registration.instance_name
            existing.instance_type = registration.instance_type
            existing.host = registration.host
            existing.port = registration.port
            existing.status = InstanceStatus.ACTIVE
            existing.last_heartbeat = datetime.utcnow()
            self.db_session.add(existing)
        else:
            # Create new registration
            instance = InstanceRegistry(
                instance_id=registration.instance_id,
                instance_name=registration.instance_name,
                instance_type=registration.instance_type,
                host=registration.host,
                port=registration.port,
                status=InstanceStatus.ACTIVE
            )
            self.db_session.add(instance)

        self.db_session.commit()

        # Publish registration event to Redis
        await self.redis_client.publish(
            "instance_events",
            json.dumps({
                "event": "instance_registered",
                "instance_id": registration.instance_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        )

        return InstanceInfo(
            id=existing.id if existing else instance.id,
            instance_id=registration.instance_id,
            instance_name=registration.instance_name,
            instance_type=registration.instance_type,
            host=registration.host,
            port=registration.port,
            status=InstanceStatus.ACTIVE,
            last_heartbeat=existing.last_heartbeat if existing else instance.registered_at
        )

    async def heartbeat(self, instance_id: str) -> bool:
        """Update instance heartbeat."""
        instance = self.db_session.exec(
            select(InstanceRegistry).where(InstanceRegistry.instance_id == instance_id)
        ).first()

        if instance:
            instance.last_heartbeat = datetime.utcnow()
            self.db_session.add(instance)
            self.db_session.commit()
            return True
        return False

    async def get_active_instances(self) -> List[InstanceInfo]:
        """Get all active instances."""
        instances = self.db_session.exec(
            select(InstanceRegistry).where(InstanceRegistry.status == InstanceStatus.ACTIVE)
        ).all()

        # Filter out instances that haven't heartbeated recently
        active_threshold = datetime.utcnow() - timedelta(seconds=60)  # 1 minute
        active_instances = [
            InstanceInfo(
                id=inst.id,
                instance_id=inst.instance_id,
                instance_name=inst.instance_name,
                instance_type=inst.instance_type,
                host=inst.host,
                port=inst.port,
                status=inst.status,
                last_heartbeat=inst.last_heartbeat
            )
            for inst in instances
            if inst.last_heartbeat >= active_threshold
        ]

        return active_instances

    async def acquire_task_lock(self, task_id: str) -> bool:
        """Acquire a distributed lock for a task."""
        lock_key = f"task_lock:{task_id}"
        lock_value = f"{self.instance_id}:{time.time()}"

        # Try to set the lock with expiration
        acquired = await self.redis_client.set(
            lock_key, lock_value, nx=True, ex=self.lock_timeout
        )

        if acquired:
            # Store in DB as well for persistence
            lock_record = TaskLock(
                task_id=task_id,
                instance_id=self.instance_id,
                lock_expires_at=datetime.utcnow() + timedelta(seconds=self.lock_timeout)
            )
            self.db_session.add(lock_record)
            self.db_session.commit()
            return True

        return False

    async def release_task_lock(self, task_id: str) -> bool:
        """Release a distributed lock for a task."""
        lock_key = f"task_lock:{task_id}"

        # Get the lock value to ensure we're releasing our own lock
        lock_value = await self.redis_client.get(lock_key)
        if lock_value:
            lock_value_str = lock_value.decode('utf-8') if isinstance(lock_value, bytes) else lock_value
            if lock_value_str.startswith(self.instance_id):
                # Delete the lock
                await self.redis_client.delete(lock_key)

                # Remove from DB as well
                lock_record = self.db_session.exec(
                    select(TaskLock).where(TaskLock.task_id == task_id)
                ).first()

                if lock_record:
                    self.db_session.delete(lock_record)
                    self.db_session.commit()

                return True

        return False

    async def synchronize_task(self, sync_request: SyncRequest) -> TaskSyncResponse:
        """Create a synchronization request for a task."""
        # Acquire lock for the task
        if not await self.acquire_task_lock(sync_request.task_id):
            return TaskSyncResponse(
                sync_id="",  # Will be updated after acquiring lock
                task_id=sync_request.task_id,
                operation=sync_request.operation,
                status=SyncStatus.FAILED,
                message="Could not acquire lock for task"
            )

        try:
            # Get all active instances if target_instances is not specified
            if not sync_request.target_instances:
                active_instances = await self.get_active_instances()
                target_instances = [inst.instance_id for inst in active_instances if inst.instance_id != self.instance_id]
            else:
                target_instances = sync_request.target_instances

            # Create sync record
            sync_record = TaskSyncRecord(
                task_id=sync_request.task_id,
                operation=sync_request.operation,
                instance_id=self.instance_id,
                target_instances=json.dumps(target_instances),
                payload=json.dumps(sync_request.payload)
            )

            self.db_session.add(sync_record)
            self.db_session.commit()
            self.db_session.refresh(sync_record)

            # Publish sync event to Redis
            await self.redis_client.publish(
                "task_sync_events",
                json.dumps({
                    "sync_id": sync_record.id,
                    "task_id": sync_request.task_id,
                    "operation": sync_request.operation,
                    "payload": sync_request.payload,
                    "origin_instance": self.instance_id,
                    "target_instances": target_instances,
                    "timestamp": datetime.utcnow().isoformat()
                })
            )

            return TaskSyncResponse(
                sync_id=sync_record.id,
                task_id=sync_request.task_id,
                operation=sync_request.operation,
                status=SyncStatus.PENDING,
                message=f"Sync initiated for {len(target_instances)} instances"
            )

        finally:
            # Release the lock
            await self.release_task_lock(sync_request.task_id)

    async def process_sync_queue(self) -> int:
        """Process pending synchronization records."""
        pending_syncs = self.db_session.exec(
            select(TaskSyncRecord).where(TaskSyncRecord.status == SyncStatus.PENDING)
        ).all()

        processed_count = 0
        for sync_record in pending_syncs:
            await self._process_single_sync(sync_record)
            processed_count += 1

        return processed_count

    async def _process_single_sync(self, sync_record: TaskSyncRecord):
        """Process a single synchronization record."""
        try:
            # Mark as processing
            sync_record.status = SyncStatus.PROCESSING
            sync_record.attempts += 1
            sync_record.processed_at = datetime.utcnow()
            self.db_session.add(sync_record)
            self.db_session.commit()

            # Get target instances
            target_instances = json.loads(sync_record.target_instances)

            # Perform the synchronization operation
            success = await self._execute_sync_operation(
                sync_record.task_id,
                sync_record.operation,
                json.loads(sync_record.payload),
                target_instances
            )

            if success:
                sync_record.status = SyncStatus.COMPLETED
            else:
                sync_record.status = SyncStatus.FAILED
                if sync_record.attempts >= sync_record.max_attempts:
                    # Mark as failed permanently
                    pass
                else:
                    # Reset to pending for retry
                    sync_record.status = SyncStatus.PENDING

            sync_record.processed_at = datetime.utcnow()
            self.db_session.add(sync_record)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Error processing sync {sync_record.id}: {e}")
            sync_record.status = SyncStatus.FAILED
            sync_record.processed_at = datetime.utcnow()
            self.db_session.add(sync_record)
            self.db_session.commit()

    async def _execute_sync_operation(
        self,
        task_id: str,
        operation: SyncOperation,
        payload: Dict[str, Any],
        target_instances: List[str]
    ) -> bool:
        """Execute the actual synchronization operation."""
        # In a real implementation, this would make HTTP requests to other instances
        # For now, we'll simulate the operation
        self.logger.info(f"Executing {operation} operation for task {task_id} on {len(target_instances)} instances")

        # Simulate network calls to other instances
        success_count = 0
        for target_instance in target_instances:
            try:
                # In a real implementation, this would be an HTTP call to the target instance
                # await self._call_target_instance(target_instance, task_id, operation, payload)
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to sync to instance {target_instance}: {e}")

        # Return success if all instances were updated successfully
        return success_count == len(target_instances)

    async def _call_target_instance(
        self,
        target_instance: str,
        task_id: str,
        operation: SyncOperation,
        payload: Dict[str, Any]
    ) -> bool:
        """Call a target instance to perform synchronization."""
        # Get target instance info
        instance_info = self.db_session.exec(
            select(InstanceRegistry).where(InstanceRegistry.instance_id == target_instance)
        ).first()

        if not instance_info:
            return False

        # In a real implementation, make an HTTP request to the target instance
        # For simulation, we'll just return True
        return True

    async def get_sync_status(self, sync_id: str) -> Optional[TaskSyncResponse]:
        """Get the status of a synchronization request."""
        sync_record = self.db_session.get(TaskSyncRecord, sync_id)
        if sync_record:
            return TaskSyncResponse(
                sync_id=sync_record.id,
                task_id=sync_record.task_id,
                operation=sync_record.operation,
                status=sync_record.status,
                message=f"Sync {sync_record.status.value}"
            )
        return None

    async def cleanup_stale_locks(self) -> int:
        """Clean up locks that have expired."""
        expired_threshold = datetime.utcnow() - timedelta(seconds=self.lock_timeout)

        expired_locks = self.db_session.exec(
            select(TaskLock).where(TaskLock.lock_expires_at < expired_threshold)
        ).all()

        cleaned_count = 0
        for lock in expired_locks:
            # Remove from DB
            self.db_session.delete(lock)

            # Remove from Redis
            lock_key = f"task_lock:{lock.task_id}"
            await self.redis_client.delete(lock_key)

            cleaned_count += 1

        if cleaned_count > 0:
            self.db_session.commit()

        return cleaned_count

    async def broadcast_task_change(self, task_id: str, operation: SyncOperation, payload: Dict[str, Any]):
        """Broadcast a task change to all instances."""
        # Create sync request for all active instances
        active_instances = await self.get_active_instances()
        target_instances = [inst.instance_id for inst in active_instances if inst.instance_id != self.instance_id]

        if not target_instances:
            return  # No other instances to sync to

        sync_request = SyncRequest(
            task_id=task_id,
            operation=operation,
            payload=payload,
            target_instances=target_instances
        )

        # Use the existing sync mechanism
        await self.synchronize_task(sync_request)

# FastAPI Application
app = FastAPI(title="Task Synchronization Service", version="1.0.0")

# Database setup
DATABASE_URL = "sqlite:///./task_sync.db"
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

# API Endpoints
@app.post("/instances/register", response_model=InstanceInfo)
async def register_instance(
    registration: InstanceRegistration,
    db: Session = Depends(get_db)
):
    """Register an instance in the cluster."""
    service = TaskSynchronizationService(db, await redis_client)
    return await service.register_instance(registration)

@app.post("/instances/{instance_id}/heartbeat")
async def instance_heartbeat(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Update instance heartbeat."""
    service = TaskSynchronizationService(db, await redis_client)
    success = await service.heartbeat(instance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {"message": "Heartbeat updated"}

@app.get("/instances/", response_model=List[InstanceInfo])
async def get_active_instances(
    db: Session = Depends(get_db)
):
    """Get all active instances."""
    service = TaskSynchronizationService(db, await redis_client)
    return await service.get_active_instances()

@app.post("/sync/", response_model=TaskSyncResponse)
async def synchronize_task(
    sync_request: SyncRequest,
    db: Session = Depends(get_db)
):
    """Create a synchronization request for a task."""
    service = TaskSynchronizationService(db, await redis_client)
    return await service.synchronize_task(sync_request)

@app.get("/sync/{sync_id}", response_model=TaskSyncResponse)
async def get_sync_status(
    sync_id: str,
    db: Session = Depends(get_db)
):
    """Get the status of a synchronization request."""
    service = TaskSynchronizationService(db, await redis_client)
    status = await service.get_sync_status(sync_id)
    if not status:
        raise HTTPException(status_code=404, detail="Sync request not found")
    return status

@app.post("/sync/process")
async def process_sync_queue(
    db: Session = Depends(get_db)
):
    """Manually trigger processing of pending synchronization requests."""
    service = TaskSynchronizationService(db, await redis_client)
    processed_count = await service.process_sync_queue()
    return {"processed_count": processed_count}

@app.post("/locks/cleanup")
async def cleanup_stale_locks(
    db: Session = Depends(get_db)
):
    """Clean up stale task locks."""
    service = TaskSynchronizationService(db, await redis_client)
    cleaned_count = await service.cleanup_stale_locks()
    return {"cleaned_count": cleaned_count}

@app.post("/broadcast/change")
async def broadcast_task_change(
    task_id: str,
    operation: SyncOperation,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Broadcast a task change to all instances."""
    service = TaskSynchronizationService(db, await redis_client)
    await service.broadcast_task_change(task_id, operation, payload)
    return {"message": f"Change broadcasted for task {task_id}"}

# Background task for periodic cleanup
@app.on_event("startup")
async def startup_event():
    """Start background tasks."""
    async def periodic_cleanup():
        db = next(get_db())
        service = TaskSynchronizationService(db, await redis_client)

        while True:
            try:
                await service.cleanup_stale_locks()
                await asyncio.sleep(30)  # Clean up every 30 seconds
            except Exception as e:
                logging.error(f"Error in periodic cleanup: {e}")

    # Start the background task
    asyncio.create_task(periodic_cleanup())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)