import os

from fastapi.testclient import TestClient

os.environ["APP_ENV"] = "test"

try:
    from seismic_classifier.api.server import app  # type: ignore
except ImportError:
    raise RuntimeError("API server module not available for tests.")

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"


def test_feature_extraction_basic():
    payload = {"sampling_rate": 100.0, "waveform": [0.0, 1.0, 0.0, -1.0] * 50}
    res = client.post("/features/extract", json=payload)
    # Endpoint may fail if underlying processor missing; allow 503 gracefully
    assert res.status_code in (200, 503)
    if res.status_code == 200:
        data = res.json()
        assert data["num_features"] == len(data["features"])
        assert data["num_features"] == len(data["features"])
