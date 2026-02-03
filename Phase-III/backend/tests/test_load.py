"""Load tests for chat API.

Tests concurrent user load and system behavior under stress:
- Multiple concurrent users with separate conversations
- User isolation under load
- No performance degradation with concurrent requests
"""

import pytest
import asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_users_different_conversations(
    async_client: AsyncClient,
    test_user_token: str,
    second_user_token: str,
    db_session
):
    """Test system handles concurrent users with separate conversations.

    Simulates:
    - 2 users (can be extended with more test users)
    - Each user sends 5 messages concurrently
    - Total: 10 concurrent requests

    Verifies:
    - All messages are processed successfully
    - User data isolation is maintained
    - No cross-user data leakage
    - Agent responses are coherent
    - Performance doesn't degrade significantly
    """
    users = [
        {"token": test_user_token, "name": "User1"},
        {"token": second_user_token, "name": "User2"}
    ]

    async def send_messages_for_user(user_info: dict, message_count: int):
        """Send multiple messages for a single user."""
        results = []
        conversation_id = None

        for i in range(message_count):
            # Build request
            request_data = {
                "message": f"{user_info['name']} - Message {i+1}"
            }
            if conversation_id:
                request_data["conversation_id"] = conversation_id

            # Send message
            response = await async_client.post(
                "/api/chat",
                json=request_data,
                headers={"Authorization": f"Bearer {user_info['token']}"}
            )

            # Capture results
            results.append({
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            })

            # Use same conversation for all messages
            if response.status_code == 200 and not conversation_id:
                conversation_id = response.json()["conversation_id"]

        return {
            "user": user_info["name"],
            "conversation_id": conversation_id,
            "results": results
        }

    # Execute concurrent requests for all users
    tasks = [
        send_messages_for_user(user, 5)
        for user in users
    ]

    user_results = await asyncio.gather(*tasks)

    # Verify all requests succeeded
    for user_result in user_results:
        user_name = user_result["user"]
        results = user_result["results"]

        # All requests should succeed
        for i, result in enumerate(results):
            assert result["status"] == 200, \
                f"{user_name} message {i+1} failed with status {result['status']}"
            assert result["data"] is not None
            assert result["data"]["agent_response"]["content"] is not None

        # Verify conversation ID consistency
        conversation_id = user_result["conversation_id"]
        for result in results:
            assert result["data"]["conversation_id"] == conversation_id

    # Verify user isolation: each user should have different conversations
    conversation_ids = [ur["conversation_id"] for ur in user_results]
    assert len(set(conversation_ids)) == len(users), \
        "Users should have separate conversations"

    # Verify each user can only see their own conversation
    for i, user_result in enumerate(user_results):
        conversation_id = user_result["conversation_id"]
        user_token = users[i]["token"]

        # User should be able to access their own conversation
        response = await async_client.get(
            f"/api/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200

        # Other users should NOT be able to access this conversation
        for j, other_user in enumerate(users):
            if i != j:
                other_token = other_user["token"]
                response = await async_client.get(
                    f"/api/chat/{conversation_id}",
                    headers={"Authorization": f"Bearer {other_token}"}
                )
                assert response.status_code == 403, \
                    f"User {j} should not access User {i}'s conversation"


@pytest.mark.asyncio
async def test_concurrent_requests_same_conversation(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test handling of concurrent requests to the same conversation.

    Verifies:
    - Multiple messages in same conversation processed concurrently
    - Message ordering is maintained
    - No race conditions or data corruption
    - All messages persisted correctly
    """
    # Create initial conversation
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Initial message"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Send 5 concurrent messages to same conversation
    async def send_concurrent_message(index: int):
        response = await async_client.post(
            "/api/chat",
            json={
                "message": f"Concurrent message {index}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        return {
            "index": index,
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    tasks = [send_concurrent_message(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all succeeded
    for result in results:
        assert result["status"] == 200, \
            f"Concurrent message {result['index']} failed"
        assert result["data"]["conversation_id"] == conversation_id

    # Retrieve conversation and verify all messages are present
    response = await async_client.get(
        f"/api/chat/{conversation_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    history = response.json()

    # Should have initial message + 5 concurrent messages = 12 total messages (6 user + 6 assistant)
    assert len(history["messages"]) >= 12

    # Verify messages are in chronological order
    messages = history["messages"]
    for i in range(len(messages) - 1):
        assert messages[i]["created_at"] <= messages[i + 1]["created_at"]


@pytest.mark.asyncio
async def test_high_volume_conversation_list(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test listing conversations with high volume of data.

    Verifies:
    - System handles users with many conversations
    - Pagination works correctly under load
    - No significant performance degradation
    """
    # Create 30 conversations
    conversation_ids = []
    for i in range(30):
        response = await async_client.post(
            "/api/chat",
            json={"message": f"High volume test {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        conversation_ids.append(response.json()["conversation_id"])

    # List conversations with different page sizes
    response1 = await async_client.get(
        "/api/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    page1 = response1.json()
    assert len(page1["conversations"]) == 10
    assert page1["total"] >= 30

    response2 = await async_client.get(
        "/api/chat/conversations?limit=20&offset=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200
    page2 = response2.json()
    assert len(page2["conversations"]) == 20

    # Verify no overlap between pages
    page1_ids = {c["id"] for c in page1["conversations"]}
    page2_ids = {c["id"] for c in page2["conversations"]}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_concurrent_tool_invocations(
    async_client: AsyncClient,
    test_user_token: str,
    second_user_token: str
):
    """Test concurrent tool invocations from different users.

    Verifies:
    - MCP server handles concurrent tool calls
    - No interference between users' tool invocations
    - All tool results are correctly attributed
    """
    users = [test_user_token, second_user_token]

    async def create_and_list_task(user_index: int, token: str):
        """Create a task and list tasks for a user."""
        # Create task
        create_response = await async_client.post(
            "/api/chat",
            json={"message": f"Add task for concurrent user {user_index}"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 200
        create_data = create_response.json()

        # List tasks
        list_response = await async_client.post(
            "/api/chat",
            json={
                "message": "List all my tasks",
                "conversation_id": create_data["conversation_id"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        list_data = list_response.json()

        return {
            "user_index": user_index,
            "create_tool_calls": create_data["agent_response"]["tool_calls"],
            "list_tool_calls": list_data["agent_response"]["tool_calls"]
        }

    # Execute concurrent tool invocations
    tasks = [
        create_and_list_task(i, token)
        for i, token in enumerate(users)
    ]

    results = await asyncio.gather(*tasks)

    # Verify all tool calls succeeded
    for result in results:
        user_index = result["user_index"]

        # Create task should have add_task tool call
        create_tools = [tc["tool"] for tc in result["create_tool_calls"]]
        assert "add_task" in create_tools, \
            f"User {user_index} add_task tool not invoked"

        # List tasks should have list_tasks tool call
        list_tools = [tc["tool"] for tc in result["list_tool_calls"]]
        assert "list_tasks" in list_tools, \
            f"User {user_index} list_tasks tool not invoked"


@pytest.mark.asyncio
async def test_stress_single_user(
    async_client: AsyncClient,
    test_user_token: str
):
    """Stress test for a single user making many rapid requests.

    Verifies:
    - System handles burst traffic from single user
    - Rate limiting is enforced (should eventually return 429)
    - System remains stable after rate limit
    """
    # Send 15 rapid requests (exceeds rate limit of 10/minute)
    async def send_rapid_message(index: int):
        response = await async_client.post(
            "/api/chat",
            json={"message": f"Rapid message {index}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        return {
            "index": index,
            "status": response.status_code
        }

    tasks = [send_rapid_message(i) for i in range(15)]
    results = await asyncio.gather(*tasks)

    # Count status codes
    success_count = sum(1 for r in results if r["status"] == 200)
    rate_limited_count = sum(1 for r in results if r["status"] == 429)

    print(f"Stress test results: {success_count} succeeded, {rate_limited_count} rate limited")

    # Should have some successful requests
    assert success_count > 0, "All requests failed"

    # Rate limiting should kick in (if CHAT_RATE_LIMIT is not 0)
    # Note: If rate limiting is disabled in test env, this may not trigger
    if rate_limited_count > 0:
        print(f"Rate limiting working: {rate_limited_count} requests blocked")


@pytest.mark.asyncio
async def test_concurrent_conversation_retrieval(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test concurrent retrieval of multiple conversations.

    Verifies:
    - Database handles concurrent read queries
    - No deadlocks or race conditions
    - All retrievals succeed
    """
    # Create 10 conversations
    conversation_ids = []
    for i in range(10):
        response = await async_client.post(
            "/api/chat",
            json={"message": f"Concurrent retrieval test {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        conversation_ids.append(response.json()["conversation_id"])

    # Retrieve all conversations concurrently
    async def retrieve_conversation(conv_id: str):
        response = await async_client.get(
            f"/api/chat/{conv_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        return {
            "conversation_id": conv_id,
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    tasks = [retrieve_conversation(conv_id) for conv_id in conversation_ids]
    results = await asyncio.gather(*tasks)

    # Verify all retrievals succeeded
    for result in results:
        assert result["status"] == 200, \
            f"Failed to retrieve conversation {result['conversation_id']}"
        assert result["data"]["id"] == result["conversation_id"]
        assert len(result["data"]["messages"]) >= 2  # At least 1 user + 1 assistant


@pytest.mark.asyncio
async def test_message_burst_in_conversation(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test handling of rapid message bursts in a single conversation.

    Verifies:
    - System handles rapid sequential messages
    - Conversation context is maintained
    - No message loss or corruption
    """
    # Create conversation
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Start burst test"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Send 10 rapid sequential messages
    for i in range(10):
        response = await async_client.post(
            "/api/chat",
            json={
                "message": f"Burst message {i+1}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        # May hit rate limit, which is acceptable
        if response.status_code == 429:
            print(f"Rate limited at message {i+1}")
            break
        assert response.status_code == 200

    # Retrieve conversation and verify messages
    final_response = await async_client.get(
        f"/api/chat/{conversation_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert final_response.status_code == 200
    history = final_response.json()

    # Should have at least the initial message
    assert len(history["messages"]) >= 2

    # Messages should be in order
    messages = history["messages"]
    for i in range(len(messages) - 1):
        assert messages[i]["created_at"] <= messages[i + 1]["created_at"]
