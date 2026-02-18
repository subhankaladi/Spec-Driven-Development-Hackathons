"""Dapr client utilities for service invocation, state management, and pub/sub."""
import asyncio
from typing import Any, Dict, Optional
from dapr.clients import DaprClient
from dapr.ext.grpc import AppCallback, Rule
import logging

logger = logging.getLogger(__name__)


class DaprServiceClient:
    """Client for interacting with Dapr runtime."""
    
    def __init__(self, dapr_client: Optional[DaprClient] = None):
        self._client = dapr_client or DaprClient()
    
    async def invoke_service(self, app_id: str, method: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Invoke a method on another service via Dapr."""
        try:
            resp = self._client.invoke_service(
                app_id=app_id,
                method_name=method,
                data=data,
                content_type='application/json'
            )
            return resp
        except Exception as e:
            logger.error(f"Error invoking service {app_id}.{method}: {str(e)}")
            raise
    
    async def save_state(self, store_name: str, key: str, value: Any) -> None:
        """Save state to Dapr state store."""
        try:
            self._client.save_state(store_name, key, value)
        except Exception as e:
            logger.error(f"Error saving state {key} to {store_name}: {str(e)}")
            raise
    
    async def get_state(self, store_name: str, key: str) -> Any:
        """Get state from Dapr state store."""
        try:
            response = self._client.get_state(store_name, key)
            return response.data
        except Exception as e:
            logger.error(f"Error getting state {key} from {store_name}: {str(e)}")
            raise
    
    async def publish_event(self, pubsub_name: str, topic_name: str, data: Any) -> None:
        """Publish an event to a Dapr pub/sub topic."""
        try:
            self._client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=data,
                data_content_type='application/json'
            )
        except Exception as e:
            logger.error(f"Error publishing event to {pubsub_name}.{topic_name}: {str(e)}")
            raise
    
    def close(self):
        """Close the Dapr client connection."""
        self._client.close()


# Global Dapr client instance
dapr_client = DaprServiceClient()


def get_dapr_client() -> DaprServiceClient:
    """Get the global Dapr client instance."""
    return dapr_client