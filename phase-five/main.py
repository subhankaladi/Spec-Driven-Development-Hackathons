from fastapi import FastAPI
from services.recurring_task_scheduler import app as recurring_task_app
from services.reminder_notification_system import app as reminder_notification_app
from services.reminder_config_api import app as reminder_config_app
from services.recurring_task_persistence import app as recurring_task_persistence_app
from services.reminder_delivery_mechanism import app as reminder_delivery_app
from services.task_synchronization import app as task_sync_app

# Main integrated application
app = FastAPI(title="Phase 5: Recurring Tasks & Reminders System", version="1.0.0")

# Include all service routers with prefixes
app.mount("/recurring-tasks", recurring_task_app)
app.mount("/reminders", reminder_notification_app)
app.mount("/reminder-config", reminder_config_app)
app.mount("/persistence", recurring_task_persistence_app)
app.mount("/delivery", reminder_delivery_app)
app.mount("/sync", task_sync_app)

@app.get("/")
async def root():
    return {
        "message": "Phase 5: Recurring Tasks & Reminders System",
        "services": [
            "recurring-tasks - Recurring Task Scheduler Service",
            "reminders - Reminder Notification System",
            "reminder-config - Reminder Configuration API",
            "persistence - Recurring Task Persistence",
            "delivery - Reminder Delivery Mechanism",
            "sync - Task Synchronization Across Instances"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "datetime.utcnow()"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)