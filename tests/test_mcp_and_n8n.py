"""
Tests for MCP and n8n Integrations
"""
from backend.app.services.mcp_adapter import MCPAdapter
from backend.app.services.n8n_adapter import N8NAdapter
from backend.app.core.database import init_db

init_db()


def test_mcp_tool_discovery():
    tools = MCPAdapter.list_available_tools(client_permissions=["compute:math"])
    assert len(tools) >= 3
    calc = next(t for t in tools if t["name"] == "calculator")
    assert calc["accessible_to_client"] is True
    db_tool = next(t for t in tools if t["name"] == "database_query")
    assert db_tool["accessible_to_client"] is False


def test_mcp_permission_enforcement():
    # Attempting to call db without data:readonly permission
    res = MCPAdapter.invoke_tool_with_telemetry(
        tool_name="database_query",
        arguments={"sql": "SELECT 1"},
        client_permissions=["compute:math"]
    )
    assert res["success"] is False
    assert res["failure_type"] == "PERMISSION_DENIED"


def test_mcp_successful_execution():
    res = MCPAdapter.invoke_tool_with_telemetry(
        tool_name="calculator",
        arguments={"expression": "12 * 12"},
        client_permissions=["compute:math"]
    )
    assert res["success"] is True
    assert res["result"] == 144
    assert res["latency_ms"] >= 0.0


def test_n8n_idempotent_webhook():
    payload = {"name": "n8n-test", "prompt": "Summarize grid load.", "priority": "NORMAL"}
    key = "idem-key-999"

    # First run
    res1 = N8NAdapter.process_n8n_workload(payload, idempotency_key=key)
    assert res1["idempotent_replay"] is False
    assert res1["data"]["status"] == "SUCCESS"

    # Second run with same idempotency key
    res2 = N8NAdapter.process_n8n_workload(payload, idempotency_key=key)
    assert res2["idempotent_replay"] is True
    assert res2["data"]["workload_id"] == res1["data"]["workload_id"]
