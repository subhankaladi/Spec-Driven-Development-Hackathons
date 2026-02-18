"""Dapr configuration for component definitions and settings."""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DaprConfig:
    """Configuration for Dapr integration."""
    
    # Dapr app settings
    app_id: str = os.getenv("DAPR_APP_ID", "task-backend")
    app_port: int = int(os.getenv("DAPR_APP_PORT", "8000"))
    app_protocol: str = os.getenv("DAPR_APP_PROTOCOL", "http")
    
    # State store configuration
    state_store_name: str = os.getenv("DAPR_STATE_STORE_NAME", "statestore")
    state_store_component: str = os.getenv("DAPR_STATE_STORE_COMPONENT", "state.postgresql")
    
    # Pub/Sub configuration
    pubsub_name: str = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
    pubsub_component: str = os.getenv("DAPR_PUBSUB_COMPONENT", "pubsub.kafka")
    
    # Service invocation settings
    service_invocation_timeout: int = int(os.getenv("DAPR_SERVICE_INVOCATION_TIMEOUT", "30"))
    
    # Component files location
    components_path: str = os.getenv("DAPR_COMPONENTS_PATH", "./dapr/components")


# Global configuration instance
dapr_config = DaprConfig()


def get_dapr_config() -> DaprConfig:
    """Get the global Dapr configuration instance."""
    return dapr_config


# Dapr component configurations
DAPR_COMPONENTS = {
    "statestore": {
        "apiVersion": "dapr.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": dapr_config.state_store_name
        },
        "spec": {
            "type": dapr_config.state_store_component,
            "version": "v1",
            "metadata": [
                {
                    "name": "connectionString",
                    "value": os.getenv("DATABASE_URL", "")
                }
            ]
        }
    },
    "pubsub": {
        "apiVersion": "dapr.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": dapr_config.pubsub_name
        },
        "spec": {
            "type": dapr_config.pubsub_component,
            "version": "v1",
            "metadata": [
                {
                    "name": "brokers",
                    "value": os.getenv("KAFKA_BROKERS", "localhost:9092")
                },
                {
                    "name": "consumerGroup",
                    "value": os.getenv("KAFKA_CONSUMER_GROUP", "task-group")
                },
                {
                    "name": "disableTls",
                    "value": os.getenv("KAFKA_DISABLE_TLS", "true")
                }
            ]
        }
    }
}


def get_dapr_component(component_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific Dapr component configuration."""
    return DAPR_COMPONENTS.get(component_name)


def get_all_dapr_components() -> Dict[str, Any]:
    """Get all Dapr component configurations."""
    return DAPR_COMPONENTS