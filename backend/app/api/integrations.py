"""
Integration Endpoints for n8n and MCP (Model Context Protocol)
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from typing import Dict, Any, Optional, List

from backend.app.services.n8n_adapter import N8NAdapter
from backend.app.services.mcp_adapter import MCPAdapter
from backend.app.core.security import get_current_user, SecurityManager
from backend.app.config import settings

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/n8n/workload")
async def n8n_workload_webhook(
    request: Request,
    payload: Dict[str, Any],
    x_idempotency_key: Optional[str] = Header(None),
    x_greenagent_signature: Optional[str] = Header(None)
):
    """
    Webhook receiver for n8n Community Edition pipelines.
    Supports idempotency caching, signed webhook verification, and automated optimization.
    """
    raw_body = await request.body()
    # If signature is provided, verify it
    if x_greenagent_signature:
        valid = SecurityManager.verify_webhook_signature(
            payload=raw_body,
            signature_header=x_greenagent_signature,
            secret=settings.SECRET_KEY
        )
        if not valid:
            raise HTTPException(status_code=401, detail="Invalid HMAC webhook signature")

    result = N8NAdapter.process_n8n_workload(
        payload=payload,
        idempotency_key=x_idempotency_key,
        signature=x_greenagent_signature,
        raw_body=raw_body
    )
    return result


@router.get("/mcp/tools")
async def list_mcp_tools(user: Dict[str, Any] = Depends(get_current_user)):
    """Discovers available tools registered in the Model Context Protocol (MCP) server."""
    # Standard client permissions
    client_perms = ["compute:math", "network:external", "data:readonly"]
    return MCPAdapter.list_available_tools(client_permissions=client_perms)


@router.post("/mcp/invoke")
async def invoke_mcp_tool(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes an MCP tool through GreenAgent governance, collecting latency,
    energy overhead, and enforcing strict permission policies.
    """
    tool_name = payload.get("tool_name", "")
    args = payload.get("arguments", {})
    client_perms = payload.get("client_permissions", ["compute:math"])

    result = MCPAdapter.invoke_tool_with_telemetry(
        tool_name=tool_name,
        arguments=args,
        client_permissions=client_perms
    )
    return result
