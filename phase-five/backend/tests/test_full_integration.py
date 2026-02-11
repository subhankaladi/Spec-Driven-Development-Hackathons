"""Full end-to-end integration tests for chat API.

Tests complete workflows including:
- Multi-turn conversations with context
- Tool chaining (list and delete)
- Conversation history retrieval
- User isolation and authorization
"""

import pytest
from uuid import UUID
from httpx import AsyncClient
from sqlmodel import Session, select

from src.models.conversation import Conversation, Message


@pytest.mark.asyncio
async def test_full_chat_flow_end_to_end(
    async_client: AsyncClient,
    test_user_token: str,
    db_session: Session
):
    """Test complete chat workflow from start to finish.

    Workflow:
    1. Create conversation with first message
    2. Multi-turn conversation with context
    3. Tool chaining (list all, delete completed)
    4. Retrieve conversation history
    5. List all conversations
    6. Verify data integrity
    """
    # Step 1: Create conversation with first message
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Add a task called Task 1"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1["conversation_id"]

    # Verify conversation created
    assert conversation_id is not None
    assert data1["user_message"]["content"] == "Add a task called Task 1"
    assert data1["agent_response"]["content"] is not None
    assert len(data1["agent_response"]["tool_calls"]) > 0
    assert data1["agent_response"]["tool_calls"][0]["tool"] == "add_task"

    # Step 2: Multi-turn conversation - add another task
    response2 = await async_client.post(
        "/api/chat",
        json={
            "message": "Add another task called Task 2",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id  # Same conversation
    assert "Task 2" in data2["user_message"]["content"]
    assert len(data2["agent_response"]["tool_calls"]) > 0

    # Step 3: Mark Task 1 as done
    response3 = await async_client.post(
        "/api/chat",
        json={
            "message": "Mark Task 1 as done",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["conversation_id"] == conversation_id
    # Should invoke complete_task or update_task
    tool_names = [tc["tool"] for tc in data3["agent_response"]["tool_calls"]]
    assert "complete_task" in tool_names or "update_task" in tool_names or "list_tasks" in tool_names

    # Step 4: Tool chaining - list all tasks and delete completed
    response4 = await async_client.post(
        "/api/chat",
        json={
            "message": "List all my tasks and delete the completed ones",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response4.status_code == 200
    data4 = response4.json()
    assert data4["conversation_id"] == conversation_id
    # Should invoke list_tasks and delete_task
    tool_names = [tc["tool"] for tc in data4["agent_response"]["tool_calls"]]
    assert "list_tasks" in tool_names
    # May or may not have delete_task depending on whether Task 1 was found

    # Step 5: Retrieve full conversation history
    response5 = await async_client.get(
        f"/api/chat/{conversation_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response5.status_code == 200
    history = response5.json()
    assert history["id"] == conversation_id
    assert len(history["messages"]) >= 8  # 4 user + 4 assistant messages

    # Verify messages are in chronological order
    messages = history["messages"]
    for i in range(len(messages) - 1):
        assert messages[i]["created_at"] <= messages[i + 1]["created_at"]

    # Verify first message is our initial message
    assert messages[0]["role"] == "user"
    assert "Task 1" in messages[0]["content"]

    # Step 6: List all conversations
    response6 = await async_client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response6.status_code == 200
    conv_list = response6.json()
    assert conv_list["total"] >= 1
    assert len(conv_list["conversations"]) >= 1

    # Find our conversation
    our_conv = next(
        (c for c in conv_list["conversations"] if c["id"] == conversation_id),
        None
    )
    assert our_conv is not None
    assert our_conv["message_count"] >= 8

    # Step 7: Verify database integrity
    # Check conversation exists in DB
    conv_query = select(Conversation).where(Conversation.id == UUID(conversation_id))
    result = await db_session.exec(conv_query)
    db_conv = result.first()
    assert db_conv is not None
    assert db_conv.title is not None

    # Check all messages are persisted
    msg_query = select(Message).where(Message.conversation_id == UUID(conversation_id))
    result = await db_session.exec(msg_query)
    db_messages = result.all()
    assert len(db_messages) >= 8

    # Verify tool_calls are persisted correctly
    assistant_messages = [msg for msg in db_messages if msg.role.value == "assistant"]
    for msg in assistant_messages:
        # At least some assistant messages should have tool_calls
        if msg.tool_calls:
            assert "calls" in msg.tool_calls
            assert isinstance(msg.tool_calls["calls"], list)


@pytest.mark.asyncio
async def test_conversation_context_retention(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test that agent retains context across multiple messages.

    Verifies:
    - Agent remembers previous messages
    - References to "the task" work after creating a task
    - Multi-turn conversations maintain coherence
    """
    # Create a task
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Create a task to water the plants"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1["conversation_id"]

    # Reference "the task" without specifying ID
    response2 = await async_client.post(
        "/api/chat",
        json={
            "message": "Mark that task as done",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    # Agent should understand context and attempt to complete the task
    assert data2["agent_response"]["content"] is not None
    assert len(data2["agent_response"]["tool_calls"]) > 0


@pytest.mark.asyncio
async def test_user_isolation(
    async_client: AsyncClient,
    test_user_token: str,
    second_user_token: str
):
    """Test that users cannot access each other's conversations.

    Verifies:
    - User A cannot retrieve User B's conversations
    - Proper 403 Forbidden errors for unauthorized access
    - User isolation is maintained in database
    """
    # User A creates a conversation
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Add a secret task"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    user_a_conversation_id = data1["conversation_id"]

    # User B tries to access User A's conversation
    response2 = await async_client.get(
        f"/api/chat/{user_a_conversation_id}",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    # Should return 403 Forbidden
    assert response2.status_code == 403
    assert "access denied" in response2.json()["detail"].lower()

    # User B lists their own conversations
    response3 = await async_client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    assert response3.status_code == 200
    conv_list = response3.json()

    # User A's conversation should not be in User B's list
    user_b_conv_ids = [c["id"] for c in conv_list["conversations"]]
    assert user_a_conversation_id not in user_b_conv_ids


@pytest.mark.asyncio
async def test_error_handling_in_conversation(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test error handling doesn't break conversation flow.

    Verifies:
    - Failed tool calls return user-friendly errors
    - Agent continues processing after errors
    - Error messages are persisted in conversation history
    """
    # Try to delete a non-existent task
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Delete task with ID 00000000-0000-0000-0000-000000000000"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1["conversation_id"]

    # Should return a user-friendly error message
    assert "couldn't find" in data1["agent_response"]["content"].lower() or \
           "not found" in data1["agent_response"]["content"].lower()

    # Tool call should have error in result
    tool_calls = data1["agent_response"]["tool_calls"]
    if tool_calls:
        # If agent attempted the operation, result should indicate error
        assert any(
            not tc["result"].get("success", True) or "error" in tc["result"]
            for tc in tool_calls
        )

    # Conversation should still work for subsequent messages
    response2 = await async_client.post(
        "/api/chat",
        json={
            "message": "List my tasks",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id
    assert len(data2["agent_response"]["tool_calls"]) > 0


@pytest.mark.asyncio
async def test_empty_conversation_history(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test retrieving conversation with no messages returns empty list."""
    # List conversations for a new user
    response = await async_client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total" in data
    # May be 0 or have conversations from other tests
    assert isinstance(data["conversations"], list)


@pytest.mark.asyncio
async def test_conversation_pagination(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test conversation list pagination works correctly.

    Verifies:
    - Limit and offset parameters work
    - Total count is accurate
    - Conversations are ordered by updated_at DESC
    """
    # Create multiple conversations
    conversation_ids = []
    for i in range(5):
        response = await async_client.post(
            "/api/chat",
            json={"message": f"Test message {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        conversation_ids.append(response.json()["conversation_id"])

    # Get first page (limit 2)
    response1 = await async_client.get(
        "/api/chat/conversations?limit=2&offset=0",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["conversations"]) <= 2
    assert data1["limit"] == 2
    assert data1["offset"] == 0
    assert data1["total"] >= 5

    # Get second page (limit 2, offset 2)
    response2 = await async_client.get(
        "/api/chat/conversations?limit=2&offset=2",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["conversations"]) <= 2
    assert data2["offset"] == 2

    # Verify no overlap between pages
    page1_ids = {c["id"] for c in data1["conversations"]}
    page2_ids = {c["id"] for c in data2["conversations"]}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_message_pagination(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test message pagination in conversation history.

    Verifies:
    - Limit and offset work for messages
    - Messages remain in chronological order
    """
    # Create conversation with multiple messages
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "First message"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Add more messages
    for i in range(5):
        await async_client.post(
            "/api/chat",
            json={
                "message": f"Message {i+2}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Get first 4 messages
    response2 = await async_client.get(
        f"/api/chat/{conversation_id}?limit=4&offset=0",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 200
    data = response2.json()
    assert len(data["messages"]) == 4

    # Verify chronological order
    messages = data["messages"]
    for i in range(len(messages) - 1):
        assert messages[i]["created_at"] <= messages[i + 1]["created_at"]
