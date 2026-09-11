# Security Architecture & Governance

## Security Principles

GreenAgent OS is built with enterprise defense-in-depth principles:

1. **Authentication & RBAC**:
   - Header-based API key authentication (`X-API-Key`).
   - Role-Based Access Control tiers:
     - `admin`: Full configuration, model registration, cache invalidation.
     - `operator`: Workload execution, scheduling control, cache invalidation.
     - `viewer`: Read-only access to metrics, telemetry, and benchmarks.

2. **Secret Redaction**:
   - Automatic regex redaction masks OpenAI/Anthropic API keys (`sk-...`), Bearer tokens, GitHub personal access tokens (`ghp_...`), AWS credentials (`AKIA...`), and raw passwords from prompts and execution traces before logging to disk or DB.

3. **Signed Webhooks**:
   - Outgoing and incoming webhooks use HMAC-SHA256 signatures (`sha256={digest}`) to prevent man-in-the-middle tampering and spoofing.

4. **Cache Poisoning Defense**:
   - Safety-critical, emergency, and adversarial queries are barred from the semantic cache.
   - Cache keys use cryptographic SHA-256 digests.

5. **Rate Limiting & Input Limits**:
   - Token bucket rate limiting (120 requests/min per client key).
   - Strict payload size boundaries prevent memory exhaustion attacks.

6. **Secure Headers**:
   - Automatic HTTP middleware enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Strict-Transport-Security`.
