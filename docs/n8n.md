# n8n Community Edition Integration

## Overview

GreenAgent OS connects with **n8n Community Edition**, allowing automated workflow pipelines to submit workloads, receive optimized execution decisions, and capture carbon telemetry.

---

## Workflow Architecture

```
[Webhook Trigger]
       │
       ▼
[GreenAgent OS POST /api/v1/integrations/n8n/workload]
       │
       ├─► (Check Idempotency & HMAC Signature)
       ├─► (Evaluate Semantic Cache)
       ├─► (Classify Complexity & Optimize)
       ├─► (Execute Model & Quality Guard)
       │
       ▼
[Check Execution Status (If Node)]
       │
       ├── SUCCESS ──► [Log Telemetry to Notification Channel]
       │
       └── FAILURE ──► [Trigger Failure Fallback Branch]
```

---

## Production Guarantees

1. **Idempotency**: Requests carrying `X-Idempotency-Key` return identical cached results upon retry, preventing double-billing and duplicate computation.
2. **HMAC Webhook Signatures**: Incoming requests can be verified via `X-GreenAgent-Signature: sha256={hmac}` using the shared secret.
3. **Timeout & Retries**: Built-in exponential backoff handles temporary backend restarts gracefully.
4. **Importable Workflow**: The production template is available at `integrations/n8n/GreenAgent_OS_Workflow.json`.
