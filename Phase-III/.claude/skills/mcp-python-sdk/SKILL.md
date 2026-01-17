# MCP Python SDK Skill

## Overview
Specialized skill for building Model Context Protocol (MCP) servers and clients using the official Python SDK. MCP enables applications to provide context for LLMs in a standardized way, separating context provision from LLM interaction. This skill covers both high-level FastMCP and low-level server implementations.

## Core Capabilities

### 1. Server Creation (FastMCP)
- Build MCP servers with minimal boilerplate
- Expose tools, resources, and prompts
- Automatic schema generation from Python types
- Lifespan management for startup/shutdown
- Built-in transport support (stdio, SSE, Streamable HTTP)

### 2. Resources
- Expose data to LLMs through URI-based resources
- Template-based resource URIs with parameters
- Dynamic resource generation
- Resource subscriptions and updates
- Read-only data access patterns

### 3. Tools
- Create executable functions for LLMs
- Automatic parameter validation with Pydantic
- Context access for logging and progress
- Structured output support
- Error handling and validation

### 4. Prompts
- Reusable prompt templates
- Parameterized prompts with arguments
- Multi-message prompt conversations
- Prompt argument completion

### 5. Client Development
- Connect to MCP servers via multiple transports
- Call tools and read resources
- OAuth authentication support
- Session management
- Request handling

## Installation & Setup

### Install MCP SDK
```bash
# Using uv (recommended)
uv add "mcp[cli]"

# Using pip
pip install "mcp[cli]"
```

### Set Up Project
```bash
# Create new project with uv
uv init mcp-server-demo
cd mcp-server-demo
uv add "mcp[cli]"
```

### Environment Variables
```bash
export OPENAI_API_KEY=sk-...  # If using LLM features
```

## FastMCP Quick Start

### Basic Server
```python
"""
Simple FastMCP server with tools, resources, and prompts.
Run with: uv run mcp dev server.py
"""
from mcp.server.fastmcp import FastMCP

# Create server instance
mcp = FastMCP("Demo Server")

# Add a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Add a resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}!"

# Add a prompt
@mcp.prompt()
def review_code(code: str) -> str:
    """Generate a code review prompt."""
    return f"Please review this code:\n\n{code}"
```

### Running the Server
```bash
# Development mode with inspector
uv run mcp dev server.py

# Install in Claude Desktop
uv run mcp install server.py

# Direct execution
python server.py
# or
uv run mcp run server.py
```

## Resources

### Basic Resource Definition
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Resource Server")

# Simple static resource
@mcp.resource("config://settings")
def get_settings() -> str:
    """Return application settings."""
    return '{"theme": "dark", "language": "en"}'

# Parameterized resource
@mcp.resource("file://documents/{filename}")
def read_file(filename: str) -> str:
    """Read a document by filename."""
    # In production, read from actual filesystem
    return f"Content of {filename}"

# Resource with multiple parameters
@mcp.resource("data://{category}/{id}")
def get_data(category: str, id: str) -> str:
    """Get data by category and ID."""
    return f"Data for {category}/{id}"
```

### Resource Lists and Templates
```python
# Resources are automatically discovered from decorators
# Clients can list all available resources

# For dynamic resources, use resource templates
@mcp.resource("repo://{owner}/{repo}")
def get_repo_info(owner: str, repo: str) -> str:
    """Get information about a GitHub repository."""
    return f"Repository: {owner}/{repo}"

# This creates a resource template that clients can discover
# and populate with specific owner/repo values
```

### Resource Updates
```python
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Dynamic Resources")

@mcp.tool()
async def update_config(key: str, value: str, ctx: Context) -> str:
    """Update configuration and notify clients."""
    # Update the config
    config[key] = value
    
    # Notify clients that resources changed
    await ctx.session.send_resource_list_changed()
    
    return f"Updated {key} to {value}"
```

## Tools

### Basic Tool Definition
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tool Server")

@mcp.tool()
def calculate_sum(numbers: list[int]) -> int:
    """Calculate the sum of a list of numbers."""
    return sum(numbers)

@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get weather for a city."""
    # In production, call a weather API
    return f"Weather in {city}: 22°{unit[0].upper()}"
```

### Pydantic Validation
```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Validated Tools")

class OrderRequest(BaseModel):
    product_id: str = Field(description="Product ID")
    quantity: int = Field(gt=0, le=100, description="Quantity (1-100)")
    priority: str = Field(pattern="^(low|medium|high)$")

@mcp.tool()
def place_order(order: OrderRequest) -> dict:
    """Place a product order with validation."""
    return {
        "order_id": "ORD-123",
        "product": order.product_id,
        "quantity": order.quantity,
        "status": "confirmed"
    }
```

### Context Access in Tools
```python
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Context Tools")

@mcp.tool()
async def long_task(name: str, ctx: Context, steps: int = 5) -> str:
    """Execute a long-running task with progress updates."""
    await ctx.info(f"Starting task: {name}")
    
    for i in range(steps):
        progress = (i + 1) / steps
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"Step {i + 1}/{steps}"
        )
        await ctx.debug(f"Completed step {i + 1}")
    
    return f"Task '{name}' completed successfully"

@mcp.tool()
async def read_data(ctx: Context) -> str:
    """Tool that reads from another resource."""
    from pydantic import AnyUrl
    
    # Read a resource using context
    result = await ctx.read_resource(AnyUrl("config://settings"))
    return f"Settings: {result}"
```

### Structured Output
```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Structured Output")

class WeatherData(BaseModel):
    """Weather information structure."""
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str
    wind_speed: float

@mcp.tool()
def get_weather_data(city: str) -> WeatherData:
    """Get structured weather data."""
    return WeatherData(
        temperature=22.5,
        humidity=65.0,
        condition="sunny",
        wind_speed=5.2
    )

# Also supports TypedDict, dataclasses, and dict[str, T]
from typing import TypedDict

class Location(TypedDict):
    latitude: float
    longitude: float
    name: str

@mcp.tool()
def geocode(address: str) -> Location:
    """Get location coordinates."""
    return {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "name": "London, UK"
    }
```

## Prompts

### Basic Prompt Definition
```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Prompt Server")

@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code:\n\n{code}"

@mcp.prompt(title="Debug Assistant")
def debug_help(error: str) -> list[base.Message]:
    """Generate a debugging conversation."""
    return [
        base.UserMessage("I'm encountering this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried?")
    ]

# Prompts with multiple parameters
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting in different styles."""
    styles = {
        "friendly": "write a warm, friendly greeting",
        "formal": "write a formal, professional greeting",
        "casual": "write a casual, relaxed greeting"
    }
    prompt = styles.get(style, styles["friendly"])
    return f"{prompt} for someone named {name}."
```

## Context Object

### Context Properties and Methods
```python
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Context Demo")

@mcp.tool()
async def demo_context(ctx: Context) -> dict:
    """Demonstrate context capabilities."""
    
    # Logging
    await ctx.debug("Debug message")
    await ctx.info("Info message")
    await ctx.warning("Warning message")
    await ctx.error("Error message")
    
    # Progress reporting
    await ctx.report_progress(
        progress=0.5,
        total=1.0,
        message="Halfway done"
    )
    
    # Access server info
    server_name = ctx.fastmcp.name
    debug_mode = ctx.fastmcp.settings.debug
    
    # Access request context
    request_id = ctx.request_context.request_id
    
    # Read resources
    from pydantic import AnyUrl
    resource = await ctx.read_resource(AnyUrl("config://settings"))
    
    return {
        "server": server_name,
        "debug": debug_mode,
        "request_id": request_id
    }
```

### Elicitation (User Input)
```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Elicitation Demo")

class UserPreferences(BaseModel):
    """User preference schema."""
    notify_email: bool = Field(description="Send email notifications")
    theme: str = Field(default="dark", description="UI theme")

@mcp.tool()
async def configure_settings(ctx: Context) -> str:
    """Request user preferences."""
    result = await ctx.elicit(
        message="Please configure your preferences:",
        schema=UserPreferences
    )
    
    if result.action == "accept" and result.data:
        return f"Settings saved: {result.data.model_dump()}"
    elif result.action == "decline":
        return "User declined to provide preferences"
    else:
        return "Configuration cancelled"
```

### Sampling (LLM Integration)
```python
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent

mcp = FastMCP("Sampling Demo")

@mcp.tool()
async def generate_text(topic: str, ctx: Context) -> str:
    """Generate text using LLM sampling."""
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Write a short poem about {topic}"
                )
            )
        ],
        max_tokens=100
    )
    
    if result.content.type == "text":
        return result.content.text
    return str(result.content)
```

## Lifespan Management

### Server Startup/Shutdown
```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import Context, FastMCP

# Mock database for example
class Database:
    @classmethod
    async def connect(cls) -> "Database":
        print("Database connected")
        return cls()
    
    async def disconnect(self) -> None:
        print("Database disconnected")
    
    def query(self, sql: str) -> list:
        return [{"result": "data"}]

@dataclass
class AppContext:
    """Application context with typed dependencies."""
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle."""
    # Startup
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        # Shutdown
        await db.disconnect()

# Create server with lifespan
mcp = FastMCP("Database Server", lifespan=app_lifespan)

@mcp.tool()
def query_database(sql: str, ctx: Context[AppContext]) -> list:
    """Execute database query using shared connection."""
    db = ctx.request_context.lifespan_context.db
    return db.query(sql)
```

## Transport Configuration

### Stdio Transport (Default)
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Stdio Server")

@mcp.tool()
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Stdio is default transport
    mcp.run()
    # or explicitly: mcp.run(transport="stdio")
```

### Streamable HTTP Transport
```python
from mcp.server.fastmcp import FastMCP

# Stateful server (maintains sessions)
mcp = FastMCP("HTTP Server")

# Stateless server (no session persistence)
# mcp = FastMCP("HTTP Server", stateless_http=True)

# JSON responses instead of SSE
# mcp = FastMCP("HTTP Server", stateless_http=True, json_response=True)

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### SSE Transport (Legacy)
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SSE Server")

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Mounting to Existing ASGI Server
```python
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

# Create MCP servers
api_mcp = FastMCP("API Server", stateless_http=True)
chat_mcp = FastMCP("Chat Server", stateless_http=True)

@api_mcp.tool()
def api_status() -> str:
    return "API is running"

@chat_mcp.tool()
def send_message(message: str) -> str:
    return f"Message sent: {message}"

# Configure paths
api_mcp.settings.streamable_http_path = "/"
chat_mcp.settings.streamable_http_path = "/"

# Create Starlette app
app = Starlette(
    routes=[
        Mount("/api", app=api_mcp.streamable_http_app()),
        Mount("/chat", app=chat_mcp.streamable_http_app()),
    ]
)

# Run with: uvicorn server:app
```

## MCP Client Development

### Basic Client (Stdio)
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl

async def main():
    # Configure server connection
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List resources
            resources = await session.list_resources()
            print(f"Resources: {[r.uri for r in resources.resources]}")
            
            # List tools
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool(
                "add",
                arguments={"a": 5, "b": 3}
            )
            print(f"Result: {result.content[0].text}")
            
            # Read a resource
            content = await session.read_resource(
                AnyUrl("greeting://Alice")
            )
            print(f"Content: {content.contents[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Streamable HTTP Client
```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read, write, _
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

if __name__ == "__main__":
    asyncio.run(main())
```

### OAuth Authentication
```python
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.streamable_http import streamablehttp_client
from pydantic import AnyUrl

class InMemoryTokenStorage(TokenStorage):
    """Simple in-memory token storage."""
    def __init__(self):
        self.tokens = None
        self.client_info = None
    
    async def get_tokens(self):
        return self.tokens
    
    async def set_tokens(self, tokens):
        self.tokens = tokens
    
    async def get_client_info(self):
        return self.client_info
    
    async def set_client_info(self, client_info):
        self.client_info = client_info

async def handle_redirect(auth_url: str):
    print(f"Visit: {auth_url}")

async def handle_callback():
    callback_url = input("Paste callback URL: ")
    # Parse code and state from URL
    return code, state

oauth = OAuthClientProvider(
    server_url="http://localhost:8001",
    client_metadata={
        "client_name": "My MCP Client",
        "redirect_uris": [AnyUrl("http://localhost:3000/callback")],
        "grant_types": ["authorization_code", "refresh_token"],
        "scope": "user"
    },
    storage=InMemoryTokenStorage(),
    redirect_handler=handle_redirect,
    callback_handler=handle_callback
)

async with streamablehttp_client(
    "http://localhost:8001/mcp",
    auth=oauth
) as (read, write, _):
    # Use authenticated session
    pass
```

## Low-Level Server

### Basic Low-Level Server
```python
import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions

server = Server("low-level-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "add":
        result = arguments["a"] + arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="low-level-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Structured Output (Low-Level)
```python
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_weather",
            description="Get weather data",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "condition": {"type": "string"},
                    "humidity": {"type": "number"}
                },
                "required": ["temperature", "condition"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> dict:
    """Return structured data directly."""
    if name == "get_weather":
        return {
            "temperature": 22.5,
            "condition": "sunny",
            "humidity": 65
        }
    raise ValueError(f"Unknown tool: {name}")
```

## Authentication

### OAuth Resource Server
```python
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

class MyTokenVerifier(TokenVerifier):
    """Custom token verification logic."""
    async def verify_token(self, token: str) -> AccessToken | None:
        # Verify token with your authorization server
        # Return AccessToken if valid, None if invalid
        pass

mcp = FastMCP(
    "Protected Server",
    token_verifier=MyTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("http://localhost:8001"),
        required_scopes=["user"]
    )
)

@mcp.tool()
def protected_action() -> str:
    """This tool requires authentication."""
    return "Action completed"
```

## Best Practices

### 1. Resource Design
- Keep resources read-only
- Use clear URI schemes (e.g., `file://`, `config://`)
- Implement resource templates for dynamic content
- Notify clients of resource changes
- Cache expensive resource computations

### 2. Tool Implementation
- Use descriptive names and docstrings
- Validate inputs with Pydantic
- Return structured output when possible
- Report progress for long operations
- Handle errors gracefully

### 3. Context Usage
- Use context for logging instead of print()
- Report progress for operations > 1 second
- Access shared resources via lifespan context
- Read resources through ctx.read_resource()
- Use elicitation for user input

### 4. Server Configuration
- Use lifespan for resource initialization
- Choose appropriate transport (stdio for desktop, HTTP for web)
- Enable stateless mode for scalability
- Configure CORS for browser clients
- Implement proper error handling

### 5. Client Development
- Always call initialize() before other operations
- Handle connection failures gracefully
- Parse structured output when available
- Use OAuth for protected servers
- Implement token refresh logic

## Common Patterns

### Multi-Agent Coordination
```python
# Create specialized agents as separate MCP servers
# Use resources to share state between servers
# Use tools for cross-server communication

@mcp.resource("shared://state")
def get_shared_state() -> str:
    return json.dumps(shared_state)

@mcp.tool()
async def update_shared_state(key: str, value: str, ctx: Context) -> str:
    shared_state[key] = value
    await ctx.session.send_resource_updated("shared://state")
    return "Updated"
```

### Progressive Enhancement
```python
# Start with basic tools
@mcp.tool()
def basic_search(query: str) -> list[str]:
    return simple_search(query)

# Add advanced features progressively
@mcp.tool()
def advanced_search(
    query: str,
    filters: dict | None = None,
    limit: int = 10
) -> list[dict]:
    return complex_search(query, filters, limit)
```

### Resource Pagination
```python
from mcp.types import PaginatedRequestParams

@server.list_resources()
async def list_resources(
    request: types.ListResourcesRequest
) -> types.ListResourcesResult:
    cursor = request.params.cursor if request.params else None
    start = int(cursor) if cursor else 0
    end = start + 10
    
    resources = [...]  # Your resources
    page = resources[start:end]
    next_cursor = str(end) if end < len(resources) else None
    
    return types.ListResourcesResult(
        resources=page,
        nextCursor=next_cursor
    )
```

---

**When to use this skill:**
- Building MCP servers to expose data/functionality to LLMs
- Creating tools for LLM interaction
- Developing MCP clients to consume server capabilities
- Implementing authentication for protected resources
- Building multi-server architectures
- Creating reusable prompt templates
- Integrating with Claude Desktop or other MCP clients
- Building browser-based MCP applications