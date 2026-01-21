"""Validation script to verify Phase 5 implementation."""

import sys
import importlib.util

def validate_imports():
    """Verify all modules can be imported."""
    print("Validating imports...")

    try:
        # Check agent_service
        from src.services.agent_service import AgentService, translate_mcp_error
        print("✓ agent_service imports successful")

        # Check tool_adapter
        from src.services.tool_adapter import ToolAdapter
        print("✓ tool_adapter imports successful")

        # Check chat routes
        from src.api.routes.chat import router
        print("✓ chat routes import successful")

        # Check auth dependencies
        from src.api.dependencies.auth import AuthenticationError, get_current_user
        print("✓ auth dependencies import successful")

        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def validate_error_translation():
    """Verify error translation function."""
    print("\nValidating error translation...")

    from src.services.agent_service import translate_mcp_error

    test_cases = [
        ("AUTHENTICATION_ERROR", "Token expired", "expired"),
        ("AUTHORIZATION_ERROR", "Access denied", "don't see"),
        ("NOT_FOUND_ERROR", "Task not found", "couldn't find"),
        ("VALIDATION_ERROR", "Invalid input", "doesn't seem"),
        ("DATABASE_ERROR", "Connection failed", "database"),
    ]

    for error_code, error_msg, expected_keyword in test_cases:
        result = translate_mcp_error(error_code, error_msg)
        if expected_keyword.lower() in result.lower():
            print(f"✓ {error_code} translates correctly")
        else:
            print(f"✗ {error_code} translation failed: got '{result}'")
            return False

    return True


def validate_tool_adapter():
    """Verify tool_adapter has required methods."""
    print("\nValidating tool_adapter...")

    from src.services.tool_adapter import ToolAdapter

    # Check for execute_tool_sequence method
    if hasattr(ToolAdapter, 'execute_tool_sequence'):
        print("✓ execute_tool_sequence method exists")
    else:
        print("✗ execute_tool_sequence method missing")
        return False

    # Check for aggregate_tool_results method
    if hasattr(ToolAdapter, 'aggregate_tool_results'):
        print("✓ aggregate_tool_results method exists")
    else:
        print("✗ aggregate_tool_results method missing")
        return False

    return True


def validate_system_prompt():
    """Verify system prompt includes tool chaining instructions."""
    print("\nValidating system prompt...")

    from src.services.agent_service import AgentService
    import os

    # Create dummy service instance
    os.environ.setdefault("OPENAI_API_KEY", "dummy-key")
    service = AgentService(api_key="dummy-key")

    system_prompt = service.system_prompt.lower()

    required_keywords = [
        "tool chaining",
        "multiple tools",
        "sequence",
        "continue",
    ]

    for keyword in required_keywords:
        if keyword in system_prompt:
            print(f"✓ System prompt includes '{keyword}'")
        else:
            print(f"✗ System prompt missing '{keyword}'")
            return False

    return True


def main():
    """Run all validations."""
    print("=" * 60)
    print("Phase 5 Implementation Validation")
    print("=" * 60)

    results = []

    results.append(("Imports", validate_imports()))
    results.append(("Error Translation", validate_error_translation()))
    results.append(("Tool Adapter", validate_tool_adapter()))
    results.append(("System Prompt", validate_system_prompt()))

    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("ALL VALIDATIONS PASSED ✓")
        return 0
    else:
        print("SOME VALIDATIONS FAILED ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
