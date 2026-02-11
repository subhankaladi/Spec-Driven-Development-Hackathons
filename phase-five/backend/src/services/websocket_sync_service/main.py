"""WebSocket Sync Service - Microservice for real-time multi-client task synchronization.

Maintains WebSocket connections from frontend clients and broadcasts task state changes
to all connected clients for the same user in real-time.

Access Pattern:
- Consumes from: task-updates topic (real-time sync events)
- Produces to: None
- Connections: WebSocket to frontend clients
"""
import logging
import json
from typing import Dict, Set, Any, Optional
from uuid import UUID
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
import asyncio
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Connection management
class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        # Format: {user_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Register new connection."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"Client connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Unregister connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(f"Client disconnected for user {user_id}")

    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections for a user."""
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to connection: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect(user_id, connection)

    def get_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user."""
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """Get total active connections."""
        return sum(len(conns) for conns in self.active_connections.values())


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting WebSocket Sync Service...")
    yield
    logger.info("Shutting down WebSocket Sync Service...")
    logger.info(f"Closing {manager.get_total_connections()} active connections")


# FastAPI app
app = FastAPI(
    title="WebSocket Sync Service",
    description="Real-time task synchronization across connected clients",
    version="1.0.0",
    lifespan=lifespan
)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time task updates.

    Usage from frontend:
        const ws = new WebSocket('ws://localhost:8004/ws/user-uuid')
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data)
            // Handle task-state-changed event
            // message.payload.operation: 'create', 'update', 'delete'
            // message.payload.full_task: complete task object
        }
    """
    await manager.connect(user_id, websocket)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "Connected to WebSocket sync service"
        })

        # Keep connection alive and receive messages
        while True:
            data = await websocket.receive_text()

            # Echo back (for testing/keepalive)
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                logger.debug(f"Received non-JSON message: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
        logger.info(f"WebSocket connection closed for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
        await manager.disconnect(user_id, websocket)


@app.post("/broadcast/task-update")
async def broadcast_task_update(
    user_id: str,
    task_id: str,
    operation: str,
    full_task: Dict[str, Any],
    changed_fields: Optional[list] = None,
):
    """Internal endpoint to broadcast task update to connected clients.

    This would be called by the task-updates consumer or the Dapr webhook handler.
    """
    try:
        message = {
            "type": "task-update",
            "event_type": "task-state-changed",
            "timestamp": None,  # Will be set by handler
            "task_id": task_id,
            "user_id": user_id,
            "payload": {
                "operation": operation,  # create, update, delete
                "changed_fields": changed_fields or [],
                "full_task": full_task,
            }
        }

        await manager.broadcast_to_user(user_id, message)

        connection_count = manager.get_connection_count(user_id)
        logger.info(f"Broadcasted task update to {connection_count} clients for user {user_id}")

        return {
            "status": "broadcasted",
            "user_id": user_id,
            "clients_notified": connection_count,
        }

    except Exception as e:
        logger.error(f"Error broadcasting task update: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500


@app.post("/task-updates")
async def task_updates_handler(event_data: Dict[str, Any]):
    """Dapr pub/sub subscription handler for task-updates events.

    This handler receives events from the task-updates Kafka topic
    and broadcasts them to connected WebSocket clients.
    """
    try:
        # Extract event from Dapr envelope
        event = event_data.get("data", {})
        if not event:
            event = event_data

        user_id = event.get("user_id")
        task_id = event.get("task_id")
        operation = event.get("payload", {}).get("operation", "update")
        full_task = event.get("payload", {}).get("full_task", {})
        changed_fields = event.get("payload", {}).get("changed_fields", [])

        logger.debug(f"Received task-update event: user={user_id}, task={task_id}, operation={operation}")

        await broadcast_task_update(
            user_id=user_id,
            task_id=task_id,
            operation=operation,
            full_task=full_task,
            changed_fields=changed_fields,
        )

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Error in task_updates_handler: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "websocket-sync-service",
        "active_connections": manager.get_total_connections()
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "ready": True,
        "service": "websocket-sync-service",
        "active_connections": manager.get_total_connections()
    }


@app.get("/stats", tags=["monitoring"])
async def get_stats():
    """Get WebSocket service statistics."""
    return {
        "service": "websocket-sync-service",
        "total_connections": manager.get_total_connections(),
        "connected_users": len(manager.active_connections),
        "users": {
            user_id: len(conns)
            for user_id, conns in manager.active_connections.items()
        }
    }


@app.get("/test-client", tags=["testing"])
async def test_client():
    """Simple HTML client for testing WebSocket (for development only)."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Test Client</title>
        </head>
        <body>
            <h1>WebSocket Sync Service - Test Client</h1>
            <div>
                <label for="user-id">User ID:</label>
                <input type="text" id="user-id" placeholder="Enter user UUID" />
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
            </div>
            <div>
                <label for="message">Message:</label>
                <input type="text" id="message" placeholder='{"type": "ping"}' />
                <button onclick="send()">Send</button>
            </div>
            <h3>Messages:</h3>
            <div id="messages" style="border: 1px solid black; padding: 10px; height: 300px; overflow-y: auto;"></div>
            <script>
                var ws = null;
                function connect() {
                    const userId = document.getElementById('user-id').value;
                    ws = new WebSocket(`ws://${window.location.host}/ws/${userId}`);
                    ws.onmessage = (event) => {
                        const msg = document.getElementById('messages');
                        msg.innerHTML += `<div>${new Date().toLocaleTimeString()}: ${event.data}</div>`;
                        msg.scrollTop = msg.scrollHeight;
                    };
                    ws.onopen = () => {
                        document.getElementById('messages').innerHTML = '<div style="color:green;">Connected!</div>';
                    };
                }
                function disconnect() {
                    if (ws) ws.close();
                }
                function send() {
                    if (ws) ws.send(document.getElementById('message').value);
                }
            </script>
        </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting WebSocket Sync Service...")
    # Run with Dapr sidecar: dapr run --app-id websocket-sync-service --app-port 8004 python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )
