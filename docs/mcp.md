# Model Context Protocol (MCP) Integration

## Overview

GreenAgent OS provides an adapter for Anthropic's open **Model Context Protocol (MCP)**, standardizing tool discovery, security permission enforcement, and energy telemetry for agent tool calls.

---

## Tool Discovery & Metadata

The MCP server exposes tool capabilities along with security risk tiers and energy overhead estimates:

```json
{
  "name": "calculator",
  "description": "Performs exact mathematical calculations",
  "parameters": {
    "expression": {"type": "string", "description": "Math expression"}
  },
  "permission_required": "compute:math",
  "risk_level": "LOW",
  "energy_overhead_j": 0.05
}
```

---

## Security Governance & Policy Enforcement

GreenAgent OS enforces strict RBAC and permission scopes on MCP tool executions:
1. **Permission Validation**: Every client request must possess the required scope (e.g. `compute:math`, `network:external`, `data:readonly`).
2. **Optimizer Cannot Bypass Security**: The multi-objective optimizer cannot downgrade permission requirements or execute unvetted tools to save energy.
3. **Telemetry Tracking**: Tool invocation wall-clock latency, failure events, and estimated Joules overhead are automatically recorded in the workload's execution trace.

---

## API Endpoints

- `GET /api/v1/integrations/mcp/tools`: Discovers all tools accessible to the client.
- `POST /api/v1/integrations/mcp/invoke`: Dispatches an audited tool invocation with telemetry collection.
