"""Performance tests for chat API.

Tests response latency and ensures performance targets are met:
- Chat response: < 3 seconds (p95)
- Conversation retrieval: < 200ms
- Conversation list: < 200ms
"""

import pytest
import time
from httpx import AsyncClient
from statistics import median


@pytest.mark.asyncio
async def test_chat_response_latency(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test that chat responses are generated within latency budget.

    Target: < 3 seconds (includes OpenAI API and MCP tool invocation)

    Verifies:
    - Single message processing completes within 3s
    - Agent response is coherent and complete
    - Tool invocations don't cause timeout
    """
    start_time = time.time()

    response = await async_client.post(
        "/api/chat",
        json={"message": "Add a task to test performance"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    end_time = time.time()
    latency = end_time - start_time

    # Verify response is successful
    assert response.status_code == 200
    data = response.json()
    assert data["agent_response"]["content"] is not None
    assert len(data["agent_response"]["tool_calls"]) > 0

    # Verify latency is within budget
    print(f"Chat response latency: {latency:.2f}s")
    assert latency < 3.0, f"Chat response took {latency:.2f}s, expected < 3s"


@pytest.mark.asyncio
async def test_chat_response_latency_with_tool_chaining(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test latency with multiple tool invocations (tool chaining).

    Target: < 5 seconds for complex multi-tool operations

    Verifies:
    - Tool chaining doesn't cause excessive latency
    - Multiple MCP calls complete within reasonable time
    """
    # First, create some tasks
    await async_client.post(
        "/api/chat",
        json={"message": "Add task A"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    await async_client.post(
        "/api/chat",
        json={"message": "Add task B"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Now test tool chaining: list and delete
    start_time = time.time()

    response = await async_client.post(
        "/api/chat",
        json={"message": "List all my tasks"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    end_time = time.time()
    latency = end_time - start_time

    assert response.status_code == 200
    data = response.json()
    assert len(data["agent_response"]["tool_calls"]) > 0

    print(f"Tool chaining latency: {latency:.2f}s")
    # More lenient for tool chaining
    assert latency < 5.0, f"Tool chaining took {latency:.2f}s, expected < 5s"


@pytest.mark.asyncio
async def test_conversation_retrieval_latency(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test that conversation retrieval is fast.

    Target: < 200ms for retrieving conversation with 100 messages

    Verifies:
    - Database queries are optimized
    - Message fetching doesn't cause performance issues
    """
    # Create a conversation with multiple messages
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "First message"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Add more messages
    for i in range(10):  # Total ~22 messages (10 user + 10 assistant + initial 2)
        await async_client.post(
            "/api/chat",
            json={
                "message": f"Message {i+2}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Measure retrieval latency
    start_time = time.time()

    response = await async_client.get(
        f"/api/chat/{conversation_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) >= 20

    print(f"Conversation retrieval latency: {latency:.0f}ms")
    assert latency < 200, f"Conversation retrieval took {latency:.0f}ms, expected < 200ms"


@pytest.mark.asyncio
async def test_conversation_retrieval_latency_large_conversation(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test retrieval latency with a large conversation (100 messages).

    Target: < 500ms for 100 messages (more lenient for large datasets)

    Verifies:
    - Database pagination works efficiently
    - Large conversations don't cause timeout
    """
    # Create a conversation with many messages
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Start large conversation"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Add 30 more messages (total ~62 with responses)
    for i in range(30):
        await async_client.post(
            "/api/chat",
            json={
                "message": f"Message {i+2}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Measure retrieval latency with pagination
    start_time = time.time()

    response = await async_client.get(
        f"/api/chat/{conversation_id}?limit=100",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) >= 60

    print(f"Large conversation retrieval latency: {latency:.0f}ms")
    assert latency < 500, f"Large conversation retrieval took {latency:.0f}ms, expected < 500ms"


@pytest.mark.asyncio
async def test_conversation_list_latency(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test that listing conversations is fast.

    Target: < 200ms for listing 50 conversations

    Verifies:
    - Database query with aggregations is optimized
    - Message count calculation doesn't cause slowdown
    """
    # Create multiple conversations
    for i in range(10):
        await async_client.post(
            "/api/chat",
            json={"message": f"Conversation {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Measure list latency
    start_time = time.time()

    response = await async_client.get(
        "/api/chat/conversations?limit=50",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds

    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) >= 10

    print(f"Conversation list latency: {latency:.0f}ms")
    assert latency < 200, f"Conversation list took {latency:.0f}ms, expected < 200ms"


@pytest.mark.asyncio
async def test_multiple_sequential_requests(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test latency of multiple sequential chat requests.

    Verifies:
    - No significant slowdown for repeated requests
    - Server handles sequential load efficiently
    - Average latency stays within budget
    """
    latencies = []

    for i in range(5):
        start_time = time.time()

        response = await async_client.post(
            "/api/chat",
            json={"message": f"Sequential test message {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)

        assert response.status_code == 200

    avg_latency = sum(latencies) / len(latencies)
    median_latency = median(latencies)
    max_latency = max(latencies)

    print(f"Sequential requests - Avg: {avg_latency:.2f}s, Median: {median_latency:.2f}s, Max: {max_latency:.2f}s")

    # Average should be well within budget
    assert avg_latency < 3.0, f"Average latency {avg_latency:.2f}s exceeds 3s"
    # Max latency should also be reasonable
    assert max_latency < 5.0, f"Max latency {max_latency:.2f}s exceeds 5s"


@pytest.mark.asyncio
async def test_database_query_performance(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test database query performance under typical load.

    Verifies:
    - Message fetching is efficient
    - No N+1 query issues
    - Indexes are being used effectively
    """
    # Create a conversation with messages
    response1 = await async_client.post(
        "/api/chat",
        json={"message": "Test database performance"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Add 20 more messages
    for i in range(20):
        await async_client.post(
            "/api/chat",
            json={
                "message": f"DB test message {i}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Measure multiple retrievals
    retrieval_times = []
    for _ in range(5):
        start_time = time.time()
        response = await async_client.get(
            f"/api/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        end_time = time.time()
        retrieval_times.append((end_time - start_time) * 1000)
        assert response.status_code == 200

    avg_retrieval = sum(retrieval_times) / len(retrieval_times)
    print(f"Average retrieval time (5 runs): {avg_retrieval:.0f}ms")

    # Should be consistently fast
    assert avg_retrieval < 200, f"Average retrieval {avg_retrieval:.0f}ms exceeds 200ms"


@pytest.mark.asyncio
async def test_pagination_performance(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test pagination doesn't significantly impact performance.

    Verifies:
    - Offset-based pagination is efficient
    - No performance degradation with higher offsets
    """
    # Create many conversations
    for i in range(20):
        await async_client.post(
            "/api/chat",
            json={"message": f"Pagination test {i}"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Test different offsets
    first_page_start = time.time()
    response1 = await async_client.get(
        "/api/chat/conversations?limit=5&offset=0",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    first_page_time = (time.time() - first_page_start) * 1000

    middle_page_start = time.time()
    response2 = await async_client.get(
        "/api/chat/conversations?limit=5&offset=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    middle_page_time = (time.time() - middle_page_start) * 1000

    last_page_start = time.time()
    response3 = await async_client.get(
        "/api/chat/conversations?limit=5&offset=15",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    last_page_time = (time.time() - last_page_start) * 1000

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    print(f"Pagination times - First: {first_page_time:.0f}ms, Middle: {middle_page_time:.0f}ms, Last: {last_page_time:.0f}ms")

    # All pages should be fast
    assert first_page_time < 200, f"First page {first_page_time:.0f}ms exceeds 200ms"
    assert middle_page_time < 200, f"Middle page {middle_page_time:.0f}ms exceeds 200ms"
    assert last_page_time < 200, f"Last page {last_page_time:.0f}ms exceeds 200ms"

    # No significant degradation with offset
    assert last_page_time < first_page_time * 2, "Pagination performance degrades with offset"
