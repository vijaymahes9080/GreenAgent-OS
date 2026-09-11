"""
Sample Audited Tools with Permission Metadata for Model Context Protocol (MCP)
"""
from typing import Dict, Any, List


TOOLS_CATALOG: Dict[str, Dict[str, Any]] = {
    "calculator": {
        "name": "calculator",
        "description": "Performs exact mathematical calculations",
        "parameters": {
            "expression": {"type": "string", "description": "Math expression, e.g. '42 * 105'"}
        },
        "permission_required": "compute:math",
        "risk_level": "LOW",
        "energy_overhead_j": 0.05
    },
    "web_search": {
        "name": "web_search",
        "description": "Fetches external web content for factual queries",
        "parameters": {
            "query": {"type": "string", "description": "Search query keywords"}
        },
        "permission_required": "network:external",
        "risk_level": "MEDIUM",
        "energy_overhead_j": 1.2
    },
    "database_query": {
        "name": "database_query",
        "description": "Executes read-only SQL queries against analytics warehouse",
        "parameters": {
            "sql": {"type": "string", "description": "SELECT SQL query"}
        },
        "permission_required": "data:readonly",
        "risk_level": "HIGH",
        "energy_overhead_j": 0.8
    }
}


def execute_tool(tool_name: str, arguments: Dict[str, Any], allowed_permissions: List[str]) -> Dict[str, Any]:
    """Executes tool safely checking permission policy."""
    tool_def = TOOLS_CATALOG.get(tool_name)
    if not tool_def:
        return {"success": False, "error": f"Unknown tool: '{tool_name}'"}

    if tool_def["permission_required"] not in allowed_permissions:
        return {
            "success": False,
            "error": f"Permission denied: client lacks '{tool_def['permission_required']}' permission"
        }

    # Execute deterministic mock tool
    if tool_name == "calculator":
        try:
            expr = arguments.get("expression", "0")
            # Safe eval of numbers and operators only
            import re
            if re.match(r"^[\d\s\+\-\*\/\(\)\.]+$", expr):
                result = eval(expr)
                return {"success": True, "result": result}
            return {"success": False, "error": "Invalid arithmetic expression"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "web_search":
        q = arguments.get("query", "")
        return {
            "success": True,
            "result": f"Simulated search results for: '{q}'. Verified sustainable energy metrics found."
        }

    elif tool_name == "database_query":
        sql = arguments.get("sql", "")
        return {
            "success": True,
            "result": [{"id": 1, "carbon_intensity_g_kwh": 185.0, "status": "active"}]
        }

    return {"success": False, "error": "Unimplemented tool executor"}
