"""
Model Context Protocol (MCP) Adapter for GreenAgent OS
Exposes tool discovery, strict permission enforcement, latency & energy telemetry,
and failure tracking for tool-augmented agent pipelines.
"""
import time
from typing import Dict, Any, List, Optional
from backend.app.core.data_contracts import MeasurementMethod
from integrations.mcp.sample_tools import TOOLS_CATALOG, execute_tool


class MCPAdapter:
    """Coordinates tool execution under GreenAgent OS governance."""

    @staticmethod
    def list_available_tools(client_permissions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Discovers tools filtered by client permission metadata."""
        tools = []
        for name, defn in TOOLS_CATALOG.items():
            perm = defn["permission_required"]
            accessible = True if client_permissions is None else (perm in client_permissions)
            tools.append({
                "name": defn["name"],
                "description": defn["description"],
                "parameters": defn["parameters"],
                "permission_required": perm,
                "risk_level": defn["risk_level"],
                "energy_overhead_j": defn["energy_overhead_j"],
                "accessible_to_client": accessible
            })
        return tools

    @staticmethod
    def invoke_tool_with_telemetry(
        tool_name: str,
        arguments: Dict[str, Any],
        client_permissions: List[str]
    ) -> Dict[str, Any]:
        """
        Executes an MCP tool with telemetry collection:
        - latency measurement
        - energy overhead accounting
        - permission verification
        - failure tracking
        """
        start_time = time.perf_counter()
        tool_def = TOOLS_CATALOG.get(tool_name)

        if not tool_def:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": False,
                "tool_name": tool_name,
                "latency_ms": round(latency_ms, 2),
                "energy_overhead_joules": 0.0,
                "error": f"Tool '{tool_name}' not found in registry",
                "failure_type": "TOOL_NOT_FOUND"
            }

        # Enforce permission policy (cannot be bypassed by optimizer)
        if tool_def["permission_required"] not in client_permissions:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": False,
                "tool_name": tool_name,
                "latency_ms": round(latency_ms, 2),
                "energy_overhead_joules": 0.0,
                "error": f"Security policy rejection: client lacks '{tool_def['permission_required']}' permission",
                "failure_type": "PERMISSION_DENIED"
            }

        # Run tool
        result = execute_tool(tool_name, arguments, client_permissions)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "success": result.get("success", False),
            "tool_name": tool_name,
            "result": result.get("result"),
            "error": result.get("error"),
            "latency_ms": round(latency_ms, 2),
            "energy_overhead_joules": tool_def["energy_overhead_j"],
            "permission_used": tool_def["permission_required"],
            "measurement_method": MeasurementMethod.ESTIMATED_ENERGY.value
        }
