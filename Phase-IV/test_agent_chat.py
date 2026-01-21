#!/usr/bin/env python
"""
Test script for AI Agent Chat API
Tests natural language task creation using OpenAI Agent with MCP tools
"""

import asyncio
import os
import sys
import json
from datetime import datetime
import httpx

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def test_chat_endpoint():
    """Test the chat API endpoint with natural language task creation"""

    print("\n" + "="*70)
    print("🤖 AI AGENT CHAT API - NATURAL LANGUAGE TASK CREATION TEST")
    print("="*70)

    # Configuration
    API_BASE_URL = "http://localhost:8000"
    CHAT_ENDPOINT = f"{API_BASE_URL}/api/chat"

    # Test user JWT token (you'll need to get this from your auth endpoint)
    # For now, we'll create a test token
    from backend.src.services.auth_service import BetterAuthIntegration

    try:
        # Initialize auth service
        auth_service = BetterAuthIntegration()

        # Create a test JWT token for testing
        # In real usage, this would come from authentication
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"  # UUID for testing
        test_token = auth_service.create_jwt_token(test_user_id)

        print(f"\n✅ Created test JWT token for user: {test_user_id}")

    except Exception as e:
        print(f"⚠️  Could not create JWT token: {e}")
        print("Using mock token for testing...")
        test_token = "mock-jwt-token-for-testing"

    # Test cases for natural language task creation
    test_cases = [
        {
            "name": "Simple task creation",
            "message": "Add a task to buy groceries",
            "expected_keywords": ["task", "buy", "groceries"]
        },
        {
            "name": "Task with description",
            "message": "Create a task called 'Prepare presentation' with description 'For tomorrow's meeting'",
            "expected_keywords": ["presentation", "task"]
        },
        {
            "name": "List tasks",
            "message": "Show me all my tasks",
            "expected_keywords": ["task", "list"]
        },
        {
            "name": "Complete a task",
            "message": "Mark my grocery task as done",
            "expected_keywords": ["done", "complete", "grocery"]
        },
        {
            "name": "Multi-turn conversation",
            "message": "Add a new task",
            "expected_keywords": ["task", "add"]
        }
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        conversation_id = None

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'─'*70}")
            print(f"📝 Test {i}: {test_case['name']}")
            print(f"{'─'*70}")
            print(f"User: {test_case['message']}")

            try:
                # Prepare request
                request_data = {
                    "message": test_case['message'],
                    "conversation_id": conversation_id
                }

                headers = {
                    "Authorization": f"Bearer {test_token}",
                    "Content-Type": "application/json"
                }

                print(f"\n⏳ Sending to agent...")

                # Send request
                response = await client.post(
                    CHAT_ENDPOINT,
                    json=request_data,
                    headers=headers
                )

                print(f"📊 Response Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    # Extract conversation ID for multi-turn
                    if "conversation_id" in data:
                        conversation_id = data["conversation_id"]
                        print(f"✅ Conversation ID: {conversation_id}")

                    # Display user message
                    if "user_message" in data:
                        user_msg = data["user_message"]
                        print(f"\n👤 User Message:")
                        print(f"   Role: {user_msg.get('role')}")
                        print(f"   Content: {user_msg.get('content')[:100]}...")

                    # Display agent response
                    if "agent_response" in data:
                        agent_msg = data["agent_response"]
                        print(f"\n🤖 Agent Response:")
                        print(f"   Role: {agent_msg.get('role')}")
                        print(f"   Content: {agent_msg.get('content')}")

                        # Display tool calls if any
                        if agent_msg.get('tool_calls'):
                            print(f"   Tool Calls: {len(agent_msg['tool_calls'])} tool(s) invoked")
                            for tool_call in agent_msg['tool_calls']:
                                print(f"     - {tool_call.get('tool')}: {tool_call.get('parameters')}")
                                if tool_call.get('result'):
                                    print(f"       Result: {str(tool_call['result'])[:100]}...")

                        print(f"\n✅ Test PASSED")
                    else:
                        print(f"⚠️  No agent response in data")
                        print(f"Response: {json.dumps(data, indent=2)[:500]}")

                elif response.status_code == 401:
                    print(f"❌ Authentication Error: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    print(f"   → Make sure your JWT token is valid")

                elif response.status_code == 429:
                    print(f"⚠️  Rate Limited: {response.status_code}")
                    print(f"   → Too many requests. Waiting before retry...")
                    await asyncio.sleep(5)

                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   Response: {response.text[:300]}")

            except httpx.ConnectError as e:
                print(f"❌ Connection Error: Could not connect to {API_BASE_URL}")
                print(f"   Make sure the backend API is running on port 8000")
                print(f"   Start it with: cd backend && python -m uvicorn src.main:app --reload")
                break

            except Exception as e:
                print(f"❌ Error: {e}")

            # Add delay between requests
            await asyncio.sleep(1)

    print(f"\n{'='*70}")
    print("✅ Testing Complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    print("\n🚀 Starting AI Agent Chat API Tests...\n")

    # Check if backend is running
    try:
        import httpx
        response = httpx.get("http://localhost:8000/docs", timeout=2)
        print("✅ Backend API is running at http://localhost:8000")
    except Exception as e:
        print("❌ Backend API is NOT running!")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  python -m uvicorn src.main:app --reload")
        sys.exit(1)

    # Run tests
    asyncio.run(test_chat_endpoint())
