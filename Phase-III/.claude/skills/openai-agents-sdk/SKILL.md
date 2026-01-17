# OpenAI Agents SDK Skill

## Overview
Specialized skill for building intelligent multi-agent systems using the OpenAI Agents SDK (Python). This production-ready framework enables agent orchestration, function calling, handoffs, guardrails, and stateful conversations. It's the official successor to OpenAI's Swarm framework.

## Core Capabilities

### 1. Agent Creation & Configuration
- Define specialized agents with custom instructions
- Configure agent models and parameters
- Set up agent-specific tools and functions
- Implement agent handoff logic
- Define structured output types with Pydantic

### 2. Function Tools
- Create type-safe function definitions
- Automatic schema generation from Python functions
- Implement tool execution handlers
- Handle function call errors gracefully
- Pydantic-powered parameter validation

### 3. Multi-Agent Orchestration (Handoffs)
- Coordinate multiple specialized agents
- Implement agent routing and delegation
- Handle context transfer between agents
- Build agent hierarchies and workflows
- Manage conversation state across agents

### 4. Guardrails
- Input validation before agent execution
- Output validation after agent responses
- Custom guardrail logic with functions
- Tripwire mechanism to halt execution
- Parallel guardrail execution

### 5. Sessions & State Management
- Automatic conversation history management
- Persistent session storage (SQLAlchemy, SQLite)
- Encrypted session support
- Context variables across runs
- Session lifecycle management

### 6. Tracing & Monitoring
- Built-in tracing for all agent runs
- Visualize agent workflows and decisions
- Debug tool calls and handoffs
- Integration with external platforms (Logfire, AgentOps, Braintrust)
- Performance monitoring and optimization

## Installation & Setup

### Install OpenAI Agents SDK
```bash
pip install openai-agents
```

### Set API Key
```bash
export OPENAI_API_KEY=sk-...
```

### Basic Configuration
```python
# config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # or "gpt-4-turbo", "gpt-4o-mini"
```

## Basic Agent Example

### Hello World
```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)

# Synchronous execution
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Async execution
import asyncio

async def main():
    result = await Runner.run(agent, "What is the meaning of life?")
    print(result.final_output)

asyncio.run(main())
```

## Agent Architecture

### Agent Definition
```python
from agents import Agent

math_tutor_agent = Agent(
    name="Math Tutor",
    model="gpt-4o",
    instructions="""You are an expert math tutor.
    - Explain concepts step-by-step
    - Provide clear examples
    - Check student understanding
    - Adapt explanations to student level""",
    
    # Optional parameters
    temperature=0.7,
    max_tokens=1000,
)
```

### Dynamic Instructions with Context
```python
def get_instructions(context_variables: dict) -> str:
    user_level = context_variables.get("user_level", "beginner")
    return f"""You are a math tutor teaching at a {user_level} level.
    Adjust your explanations accordingly."""

agent = Agent(
    name="Adaptive Math Tutor",
    instructions=get_instructions,  # Function that takes context
)

# Run with context
result = await Runner.run(
    agent,
    "Explain calculus",
    context_variables={"user_level": "advanced"}
)
```

## Function Tools

### Creating Tools from Python Functions
```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: City name or zip code
    """
    # Simulate API call
    return f"The weather in {location} is sunny and 72°F"

@function_tool
def calculate_tip(bill_amount: float, tip_percentage: float = 20.0) -> dict:
    """Calculate tip amount.
    
    Args:
        bill_amount: Total bill amount in dollars
        tip_percentage: Tip percentage (default 20%)
    """
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    return {
        "tip_amount": round(tip, 2),
        "total_amount": round(total, 2)
    }

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant with access to tools.",
    tools=[get_weather, calculate_tip],
)

result = await Runner.run(agent, "What's the weather in San Francisco?")
print(result.final_output)
```

**Important**: The `@function_tool` decorator is **required** for all tool functions. It enables automatic schema generation and proper integration with the agent system.

### Pydantic Models for Validation
```python
from pydantic import BaseModel, Field
from typing import Literal
from agents import function_tool

class OrderInput(BaseModel):
    product_id: str = Field(description="Product ID to order")
    quantity: int = Field(gt=0, description="Quantity to order")
    priority: Literal["low", "medium", "high"] = "medium"

@function_tool
def place_order(order: OrderInput) -> dict:
    """Place an order for a product."""
    return {
        "order_id": "ORD-12345",
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "confirmed"
    }

agent = Agent(
    name="Sales Agent",
    instructions="Help customers place orders",
    tools=[place_order],
)
```

### Accessing Context in Tools
```python
from agents import ToolContext, function_tool

@function_tool
def get_user_info(context: ToolContext) -> dict:
    """Get information about the current user."""
    user_id = context.context_variables.get("user_id")
    
    # Access database or external API
    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }

agent = Agent(
    name="Assistant",
    tools=[get_user_info],
)

result = await Runner.run(
    agent,
    "What's my email address?",
    context_variables={"user_id": "user_123"}
)
```

## Handoffs (Multi-Agent Orchestration)

### Basic Handoff Pattern
```python
from agents import Agent, Runner

# Define specialist agents
history_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist for historical questions",
    instructions="You are an expert in history. Explain historical events clearly.",
)

math_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist for math questions",
    instructions="You are an expert in mathematics. Explain step-by-step.",
)

# Triage agent that routes to specialists
triage_agent = Agent(
    name="Triage Agent",
    instructions="Determine which specialist agent to use based on the question",
    handoffs=[history_agent, math_agent],
)

# Run - agent will automatically handoff
result = await Runner.run(
    triage_agent,
    "Who was the first president of the United States?"
)
print(result.final_output)
# The history agent will answer this
```

### Customizing Handoffs
```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing Agent")
refund_agent = Agent(name="Refund Agent")

# Custom handoff with overrides
custom_handoff = handoff(
    agent=refund_agent,
    tool_name_override="escalate_to_refunds",
    tool_description_override="Transfer to refund specialist for refund requests",
    
    # Callback when handoff occurs
    on_handoff=lambda ctx: print(f"Transferring to {ctx.agent.name}"),
)

triage_agent = Agent(
    name="Customer Service",
    handoffs=[billing_agent, custom_handoff],
)
```

### Handoff with Input Filtering
```python
from agents import handoff, HandoffInputData
from agents.extensions import handoff_filters

# Remove all tool calls from history when handing off
clean_handoff = handoff(
    agent=specialist_agent,
    input_filter=handoff_filters.remove_all_tools,
)

# Custom input filter
def summarize_conversation(input_data: HandoffInputData) -> HandoffInputData:
    """Summarize conversation before handoff."""
    # Collapse history into summary
    summary = "Previous conversation covered: order status inquiry"
    
    return HandoffInputData(
        input=input_data.input,
        messages=[{"role": "system", "content": summary}],
    )

custom_handoff = handoff(
    agent=agent,
    input_filter=summarize_conversation,
)
```

### Bi-directional Handoffs
```python
# Agent A can hand off to Agent B
# Agent B can hand back to Agent A

agent_a = Agent(name="Agent A")
agent_b = Agent(name="Agent B")

# Set up bi-directional handoffs
agent_a.handoffs = [agent_b]
agent_b.handoffs = [agent_a]
```

## Guardrails

### Input Guardrails
```python
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class HomeworkCheck(BaseModel):
    is_homework: bool
    reasoning: str

# Guardrail agent to check input
guardrail_agent = Agent(
    name="Homework Checker",
    instructions="Determine if the user is asking for homework help",
    output_type=HomeworkCheck,
)

async def homework_guardrail(ctx, agent, input_data):
    """Check if input is homework related."""
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    output = result.final_output_as(HomeworkCheck)
    
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_homework,  # Block if homework
    )

# Main agent with input guardrail
main_agent = Agent(
    name="Tutor",
    instructions="Help students learn, but don't do their homework",
    input_guardrails=[InputGuardrail(guardrail_function=homework_guardrail)],
)

# This will trigger the guardrail
try:
    result = await Runner.run(main_agent, "What's the answer to question 5?")
except InputGuardrailTripwireTriggered as e:
    print("Request blocked:", e)
```

### Output Guardrails
```python
from agents import OutputGuardrail

class ContentCheck(BaseModel):
    is_appropriate: bool
    reason: str

checker_agent = Agent(
    name="Content Checker",
    instructions="Check if content is appropriate and professional",
    output_type=ContentCheck,
)

async def content_guardrail(ctx, agent, output):
    """Validate agent output is appropriate."""
    result = await Runner.run(
        checker_agent,
        f"Check this response: {output}",
        context=ctx.context
    )
    check = result.final_output_as(ContentCheck)
    
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_appropriate,
    )

agent = Agent(
    name="Assistant",
    output_guardrails=[OutputGuardrail(guardrail_function=content_guardrail)],
)
```

## Structured Outputs

### Using Pydantic Models
```python
from pydantic import BaseModel, Field
from typing import List

class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    instructions: List[str]
    prep_time_minutes: int = Field(gt=0)
    
class RecipeAgent(BaseModel):
    recipes: List[Recipe]
    total_recipes: int

agent = Agent(
    name="Recipe Generator",
    instructions="Generate recipes based on user preferences",
    output_type=RecipeAgent,
)

result = await Runner.run(agent, "Give me 2 quick pasta recipes")
output = result.final_output_as(RecipeAgent)

for recipe in output.recipes:
    print(f"{recipe.name}: {recipe.prep_time_minutes} minutes")
```

## Sessions & State Management

### In-Memory Sessions
```python
from agents import Agent, Runner, InMemorySession

agent = Agent(name="Assistant", instructions="You are helpful")

# Create session
session = InMemorySession()

# First interaction
result1 = await Runner.run(
    agent,
    "My name is Alice",
    session=session
)

# Session remembers context
result2 = await Runner.run(
    agent,
    "What's my name?",
    session=session
)
print(result2.final_output)  # "Your name is Alice"
```

### SQLAlchemy Persistent Sessions
```python
from agents.extensions.memory import SQLAlchemySession
from sqlalchemy import create_engine

# Setup database
engine = create_engine("sqlite:///sessions.db")

# Create session
session = SQLAlchemySession(
    session_id="user_123",
    engine=engine,
)

# Use session across runs
result = await Runner.run(agent, "Hello", session=session)

# Session persists in database
# Can be retrieved later with same session_id
session2 = SQLAlchemySession(session_id="user_123", engine=engine)
result2 = await Runner.run(agent, "Continue our chat", session=session2)
```

### Context Variables
```python
# Pass context that persists across agent runs
result = await Runner.run(
    agent,
    "Process my order",
    context_variables={
        "user_id": "user_123",
        "user_tier": "premium",
        "location": "US",
    }
)

# Context is available to all tools and agents
# Updated context is returned in result
updated_context = result.context_variables
```

## Streaming

### Stream Agent Responses
```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are helpful")

async for event in Runner.run_streamed(agent, "Write a long story"):
    if event.type == "text_delta":
        print(event.text_delta, end="", flush=True)
    elif event.type == "tool_call_started":
        print(f"\nCalling tool: {event.tool_name}")
    elif event.type == "handoff":
        print(f"\nHandoff to: {event.agent.name}")
```

### Stream Events
```python
async for event in Runner.run_streamed(agent, "Hello"):
    match event.type:
        case "text_delta":
            # Partial text from agent
            print(event.text_delta, end="")
            
        case "tool_call_started":
            # Tool execution started
            print(f"Tool: {event.tool_name}")
            
        case "tool_call_completed":
            # Tool execution finished
            print(f"Result: {event.result}")
            
        case "handoff":
            # Agent handoff occurred
            print(f"Handoff to {event.agent.name}")
            
        case "run_completed":
            # Run finished
            print(f"Final: {event.final_output}")
```

## Tracing & Debugging

### Built-in Tracing
```python
from agents import Agent, Runner

# Tracing is enabled by default
result = await Runner.run(agent, "Hello")

# Access trace
trace = result.trace

# View all spans
for span in trace.spans:
    print(f"{span.name}: {span.duration_ms}ms")
```

### Custom Tracing
```python
from agents.tracing import trace

async def my_function():
    with trace.span("custom_operation"):
        # Your code here
        result = await some_operation()
        
        # Add span attributes
        trace.current_span().set_attribute("result_size", len(result))
        
        return result
```

### External Tracing Integration
```python
from agents.tracing import setup_tracing
from agents.tracing.processors import LogfireProcessor

# Setup Logfire tracing
setup_tracing(processors=[LogfireProcessor()])

# All agent runs now traced to Logfire
result = await Runner.run(agent, "Hello")
```

## Advanced Patterns

### Agent Loop with Max Turns
```python
from agents import Agent, Runner, RunConfig

config = RunConfig(max_turns=5)

result = await Runner.run(
    agent,
    "Solve this complex problem",
    config=config
)

print(f"Took {result.num_turns} turns")
```

### Multi-Step Workflow
```python
# Step 1: Research
research_agent = Agent(
    name="Researcher",
    instructions="Research the topic thoroughly",
)

# Step 2: Write
writer_agent = Agent(
    name="Writer",
    instructions="Write a comprehensive article",
)

# Step 3: Edit
editor_agent = Agent(
    name="Editor",
    instructions="Edit and polish the content",
)

# Execute workflow
research_result = await Runner.run(research_agent, "AI trends 2024")
draft_result = await Runner.run(
    writer_agent,
    f"Write article based on: {research_result.final_output}"
)
final_result = await Runner.run(
    editor_agent,
    f"Edit this: {draft_result.final_output}"
)
```

### Parallel Tool Execution
```python
agent = Agent(
    name="Assistant",
    tools=[tool1, tool2, tool3],
    parallel_tool_calls=True,  # Enable parallel execution
)

# Agent can call multiple tools simultaneously
```

### Error Handling
```python
from agents.exceptions import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
)

try:
    result = await Runner.run(agent, user_input)
except InputGuardrailTripwireTriggered as e:
    print("Input blocked by guardrail:", e.guardrail_info)
except OutputGuardrailTripwireTriggered as e:
    print("Output blocked by guardrail:", e.guardrail_info)
except MaxTurnsExceeded:
    print("Agent exceeded maximum turns")
```

## Real-World Examples

### Customer Service Agent
```python
from agents import function_tool

@function_tool
def lookup_order(order_id: str) -> dict:
    """Look up order status."""
    return {"order_id": order_id, "status": "shipped"}

@function_tool
def process_refund(order_id: str, reason: str) -> dict:
    """Process a refund."""
    return {"refund_id": "REF-123", "status": "approved"}

refund_agent = Agent(
    name="Refund Specialist",
    instructions="Handle refund requests professionally",
    tools=[process_refund],
)

support_agent = Agent(
    name="Customer Support",
    instructions="""Help customers with orders and issues.
    - Be polite and professional
    - Look up order information
    - Transfer to refund specialist if needed""",
    tools=[lookup_order],
    handoffs=[refund_agent],
)

result = await Runner.run(
    support_agent,
    "I want a refund for order ORD-123"
)
```

### Data Analysis Agent
```python
import pandas as pd
from agents import function_tool, ToolContext

@function_tool
def analyze_data(query: str, context: ToolContext) -> str:
    """Analyze dataset based on query."""
    df = context.context_variables.get("dataframe")
    
    # Perform analysis
    if "average" in query.lower():
        return f"Average: {df['value'].mean()}"
    elif "total" in query.lower():
        return f"Total: {df['value'].sum()}"
    
    return "Analysis complete"

analyst_agent = Agent(
    name="Data Analyst",
    instructions="Analyze data and provide insights",
    tools=[analyze_data],
)

# Load data
df = pd.read_csv("data.csv")

result = await Runner.run(
    analyst_agent,
    "What's the average value?",
    context_variables={"dataframe": df}
)
```

## Best Practices

### 1. Agent Instructions
- Be specific and clear about agent's role
- Include behavioral guidelines
- Specify output format expectations
- Provide examples when helpful

### 2. Tool Design
- Keep tools focused (single responsibility)
- Use clear function names and descriptions
- Leverage Pydantic for validation
- Return structured data when possible

### 3. Handoff Strategy
- Create specialized agents for distinct tasks
- Use triage agents for routing
- Provide clear handoff descriptions
- Filter history when appropriate

### 4. Guardrails
- Implement input validation early
- Use output guardrails for safety
- Keep guardrail logic simple and fast
- Log guardrail triggers for monitoring

### 5. Session Management
- Use persistent sessions for user conversations
- Clean up old sessions periodically
- Store minimal context (avoid bloat)
- Encrypt sensitive session data

### 6. Performance
- Use appropriate models (smaller for simple tasks)
- Enable parallel tool calls when possible
- Set reasonable max_turns limits
- Monitor token usage via tracing

### 7. Error Handling
- Always handle guardrail exceptions
- Implement tool error handling
- Provide user-friendly error messages
- Log errors for debugging

---

**When to use this skill:**
- Building multi-agent systems
- Implementing conversational AI
- Creating specialized AI workflows
- Orchestrating complex agent interactions
- Building production-grade AI applications
- Implementing safety guardrails
- Managing stateful conversations
- Creating customer service automation
- Building AI assistants with tool use