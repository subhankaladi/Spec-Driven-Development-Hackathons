"""MCP tool adapter for OpenAI Agent integration.

This adapter converts MCP tool schemas to OpenAI function schemas and handles
tool execution results transformation.
"""

import httpx
from typing import Any, Optional


class ToolAdapter:
    """Adapter for MCP tool integration with OpenAI Agent.

    This class provides static methods for converting MCP tool results
    and executing MCP tools via HTTP.
    """

    @staticmethod
    def convert_mcp_tool_result(mcp_result: dict[str, Any]) -> dict[str, Any]:
        """Convert MCP tool result to agent-friendly format.

        Args:
            mcp_result: Raw result from MCP tool execution

        Returns:
            Transformed result suitable for agent consumption
        """
        # MCP results are already in good format, but we can add metadata
        if "error" in mcp_result:
            return {
                "success": False,
                "error": mcp_result["error"],
                "data": None
            }

        return {
            "success": True,
            "error": None,
            "data": mcp_result
        }

    @staticmethod
    async def execute_tool_call(
        tool_name: str,
        parameters: dict[str, Any],
        jwt_token: str,
        mcp_base_url: str = "http://localhost:8001"
    ) -> dict[str, Any]:
        """Execute MCP tool via HTTP and return formatted result.

        Args:
            tool_name: Name of the MCP tool to execute
            parameters: Tool parameters
            jwt_token: JWT authentication token
            mcp_base_url: Base URL for MCP server

        Returns:
            Formatted tool execution result

        Raises:
            httpx.HTTPError: If HTTP request fails
            ValueError: If tool name is unknown
        """
        # Map tool names to MCP endpoints
        endpoint_map = {
            "add_task": "/tools/add_task",
            "list_tasks": "/tools/list_tasks",
            "complete_task": "/tools/complete_task",
            "update_task": "/tools/update_task",
            "delete_task": "/tools/delete_task"
        }

        endpoint = endpoint_map.get(tool_name)
        if not endpoint:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Add JWT token to parameters
        tool_params = {**parameters, "jwt_token": jwt_token}

        # Execute HTTP request to MCP server
        url = f"{mcp_base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=tool_params)
                response.raise_for_status()
                mcp_result = response.json()

                # Convert to standardized format
                return ToolAdapter.convert_mcp_tool_result(mcp_result)

            except httpx.HTTPStatusError as e:
                # Handle HTTP errors
                error_detail = e.response.json() if e.response.text else {}
                return {
                    "success": False,
                    "error": error_detail.get("message", str(e)),
                    "data": None
                }

            except Exception as e:
                # Handle other errors
                return {
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}",
                    "data": None
                }

    @staticmethod
    async def execute_tool_sequence(
        tool_calls: list[dict[str, Any]],
        jwt_token: str,
        mcp_base_url: str = "http://localhost:8001"
    ) -> list[dict[str, Any]]:
        """Execute multiple tools in sequence for complex operations.

        This function enables tool chaining by executing tools sequentially
        and continuing even if individual tools fail.

        Args:
            tool_calls: List of tool call dicts with 'name' and 'parameters' keys
            jwt_token: JWT authentication token
            mcp_base_url: Base URL for MCP server

        Returns:
            List of results, one per tool call, with structure:
            {
                "tool": tool_name,
                "parameters": parameters_used,
                "result": tool_execution_result,
                "success": bool
            }

        Example:
            >>> tool_calls = [
            ...     {"name": "list_tasks", "parameters": {"completed": True}},
            ...     {"name": "delete_task", "parameters": {"task_id": "123"}}
            ... ]
            >>> results = await execute_tool_sequence(tool_calls, jwt_token)
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            parameters = tool_call.get("parameters", {})

            try:
                # Execute tool via MCP
                result = await ToolAdapter.execute_tool_call(
                    tool_name=tool_name,
                    parameters=parameters,
                    jwt_token=jwt_token,
                    mcp_base_url=mcp_base_url
                )

                # Append result with success flag
                results.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": result.get("data") if result.get("success") else result,
                    "success": result.get("success", False)
                })

            except Exception as e:
                # Continue execution even if tool fails
                results.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": {"error": str(e)},
                    "success": False
                })

        return results

    @staticmethod
    def aggregate_tool_results(results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate results from multiple tool calls.

        Args:
            results: List of tool execution results

        Returns:
            Aggregated result summary with success/failure counts
        """
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful

        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
