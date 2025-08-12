import os
from typing import Any, List

from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")

try:
    from seismic_classifier.api import server  # type: ignore
except ImportError as e:  # pragma: no cover
    raise RuntimeError(f"API server module not available: {e}")

app = server.app


class StubSignalProcessor:
    def extract_features(
        self, waveform: List[float], sampling_rate: float
    ) -> List[float]:  # noqa: D401,E501
        _ = sampling_rate  # acknowledge param for lint
        if not waveform:
            return [0.0, 0.0, 0.0]
        mean = sum(waveform) / len(waveform)
        mx = max(waveform)
        mn = min(waveform)
        return [mean, mx, mn]


class StubClassifier:
    def predict(self, X: List[List[float]]) -> List[str]:  # noqa: D401,E501
        return ["earthquake" for _ in X]


class StubDetector:
    def detect(self, waveform: List[float]) -> List[Any]:  # noqa: D401,E501
        if not waveform:
            return []
        return [
            {
                "id": "evt-1",
                "start_index": 0,
                "end_index": min(len(waveform), 10),
                "confidence": 0.95,
            }
        ]


class StubMagnitudeEstimator:
    def batch_estimate(self, waves: List[List[float]]):  # noqa: D401,E501
        out = []
        for w in waves:
            mag = 3.0 + (len(w) % 100) / 100.0
            out.append({"magnitude": round(mag, 2), "confidence": 0.8})
        return out


def _signal_processor():  # noqa: D401
    return StubSignalProcessor()


def _classifier():  # noqa: D401
    return StubClassifier()


def _detector():  # noqa: D401
    return StubDetector()


def _mag_est():  # noqa: D401
    return StubMagnitudeEstimator()


app.dependency_overrides[server.get_signal_processor] = _signal_processor
app.dependency_overrides[server.get_classifier] = _classifier
app.dependency_overrides[server.get_detector] = _detector
app.dependency_overrides[server.get_magnitude_estimator] = _mag_est

client = TestClient(app)


def test_classify_endpoint_stub():
    payload = {"sampling_rate": 100.0, "waveform": [0.0, 1.0, -1.0, 0.5] * 5}
    res = client.post("/classify", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["prediction"] == "earthquake"


def test_detect_endpoint_stub():
    payload = {"sampling_rate": 100.0, "waveform": [0.1] * 50}
    res = client.post("/detect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["num_events"] == 1
    evt = data["events"][0]
    assert evt["id"] == "evt-1"
    assert 0 <= evt["confidence"] <= 1


def test_magnitude_endpoint_stub():
    payload = {"waveforms": [[0.0] * 120, [0.0] * 80]}
    res = client.post("/magnitude", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 2
    mags = data["magnitudes"]
    assert all("magnitude" in m for m in mags)
    assert all("confidence" in m for m in mags)
