"""
API Integration Tests for GreenAgent OS
Tests all REST endpoints using FastAPI TestClient.
"""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)
AUTH_HEADERS = {settings.API_KEY_HEADER_NAME: settings.DEFAULT_API_KEY}


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["gpu_required"] is False


def test_list_models_api():
    resp = client.get(f"{settings.API_PREFIX}/models", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5
    assert any(m["name"] == "llama3.2:1b" for m in data)


def test_deterministic_model_selection_api():
    payload = {
        "complexity": "EASY",
        "min_quality": 0.50,
        "max_latency_ms": 3000.0,
        "prefer_efficiency": True
    }
    resp = client.post(f"{settings.API_PREFIX}/models/select", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    selected = resp.json()
    assert selected["name"] in ["llama3.2:1b", "llama3.2:3b"]


def test_optimizer_plan_api():
    wl_payload = {
        "name": "API Test",
        "prompt": "Summarize this quarterly earnings statement.",
        "priority": "NORMAL",
        "deadline_seconds": 60.0
    }
    resp = client.post(f"{settings.API_PREFIX}/optimizer/optimize", json=wl_payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    plan = resp.json()
    assert "selected_model" in plan
    assert "target_region" in plan
    assert plan["predicted_latency_ms"] > 0


def test_optimizer_execute_api():
    wl_payload = {
        "name": "API Execute Test",
        "prompt": "Generate a three-bullet summary of solar energy benefits.",
        "priority": "LOW",
        "deadline_seconds": 90.0
    }
    resp = client.post(f"{settings.API_PREFIX}/optimizer/execute", json=wl_payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] in ["COMPLETED", "CACHED"]
    assert "response" in res
    assert "trace_id" in res


def test_telemetry_get_api():
    resp = client.get(f"{settings.API_PREFIX}/telemetry", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    traces = resp.json()
    assert isinstance(traces, list)


def test_scheduler_regions_api():
    resp = client.get(f"{settings.API_PREFIX}/scheduler/regions", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    regions = resp.json()
    assert len(regions) >= 4
    assert any(r["region_id"] == "us-east" for r in regions)
    assert any(r["region_id"] == "eu-north" for r in regions)


def test_cache_stats_api():
    resp = client.get(f"{settings.API_PREFIX}/cache", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_entries" in data
    assert "total_tokens_saved" in data


def test_n8n_webhook_api():
    n8n_payload = {
        "name": "n8n-api-test",
        "prompt": "Extract date from: Meeting held on October 12, 2026.",
        "priority": "NORMAL",
        "deadline_seconds": 45.0
    }
    headers = {
        **AUTH_HEADERS,
        "X-Idempotency-Key": "n8n-test-key-01"
    }
    resp = client.post(f"{settings.API_PREFIX}/integrations/n8n/workload", json=n8n_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["status"] == "SUCCESS"


def test_mcp_tools_api():
    resp = client.get(f"{settings.API_PREFIX}/integrations/mcp/tools", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    tools = resp.json()
    assert len(tools) >= 3


def test_benchmarks_latest_api():
    resp = client.get(f"{settings.API_PREFIX}/benchmarks/latest", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    bench = resp.json()
    assert bench["benchmark_name"] == "GreenAgent-OS-Standard-100"
    assert bench["total_workloads"] == 100
    assert bench["verdict"] == "PASSED_ALL_TARGETS"


def test_security_unauthorized_when_configured():
    # Test with invalid key
    resp = client.get(f"{settings.API_PREFIX}/models", headers={"X-API-Key": "completely-fake-key"})
    assert resp.status_code == 401
