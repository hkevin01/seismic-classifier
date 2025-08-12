"""Seismic Classifier Public API Service.

This module exposes key pipeline capabilities (USGS events, feature extraction,
classification, real-time detection, and magnitude estimation) through a
FastAPI application. It is intentionally lightweight and dependency-injected
friendly so components can be overridden in tests.
"""

from __future__ import annotations

import os
from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import existing project components (best‑effort; fall back gracefully)
try:  # type: ignore
    from seismic_classifier.data_pipeline.usgs_client import USGSClient
except ImportError:  # pragma: no cover
    USGSClient = None  # type: ignore

# Feature extractor symbol (optional import)
try:  # type: ignore
    from seismic_classifier.feature_engineering.feature_extraction import (  # noqa: F401
        FeatureExtractor as _FeatureExtractor,
    )
except ImportError:  # pragma: no cover
    _FeatureExtractor = None  # type: ignore

try:  # type: ignore
    from seismic_classifier.feature_engineering.signal_processing import SignalProcessor
except ImportError:  # pragma: no cover
    SignalProcessor = None  # type: ignore

try:  # type: ignore
    from seismic_classifier.ml_models.classification import SeismicClassifier
except ImportError:  # pragma: no cover
    SeismicClassifier = None  # type: ignore

try:  # type: ignore
    from seismic_classifier.advanced_analytics.event_detection import RealTimeDetector
except ImportError:  # pragma: no cover
    RealTimeDetector = None  # type: ignore

try:  # type: ignore
    from seismic_classifier.advanced_analytics.magnitude_estimation import (
        MagnitudeEstimator,
    )
except ImportError:  # pragma: no cover
    MagnitudeEstimator = None  # type: ignore


APP_ENV = os.getenv("APP_ENV", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
USGS_BASE_URL = os.getenv("USGS_BASE_URL")
USGS_RATE_LIMIT = int(os.getenv("USGS_RATE_LIMIT", "10"))

allowed_origins = [
    o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()
]

app = FastAPI(title="Seismic Classifier API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency Providers (DI so tests can override via app.dependency_overrides)
# ---------------------------------------------------------------------------


def get_usgs_client() -> Any:
    if USGSClient is None:
        raise HTTPException(status_code=503, detail="USGSClient not available")
    if USGS_BASE_URL:  # existing client already loads base_url from config
        return USGSClient()
    return USGSClient()


def get_signal_processor() -> Any:
    if SignalProcessor is None:
        raise HTTPException(status_code=503, detail="SignalProcessor not available")
    return SignalProcessor()


def get_classifier() -> Any:
    if SeismicClassifier is None:
        raise HTTPException(status_code=503, detail="SeismicClassifier not available")
    return SeismicClassifier()


def get_detector() -> Any:
    if RealTimeDetector is None:
        raise HTTPException(status_code=503, detail="RealTimeDetector not available")
    return RealTimeDetector()


def get_magnitude_estimator() -> Any:
    if MagnitudeEstimator is None:
        raise HTTPException(status_code=503, detail="MagnitudeEstimator not available")
    return MagnitudeEstimator()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str = "ok"
    env: str = APP_ENV
    message: str = "Seismic Classifier API running"


class RecentEventsQuery(BaseModel):
    hours: int = Field(48, ge=1, le=168, description="Look-back window in hours")
    min_magnitude: float = Field(4.0, ge=0.0, description="Minimum magnitude")


class WaveformInput(BaseModel):
    sampling_rate: float = Field(100.0, gt=0)
    waveform: List[float] = Field(..., description="Array-like waveform time series")


class ClassificationRequest(BaseModel):
    sampling_rate: float = Field(100.0, gt=0)
    waveform: List[float]


class DetectionRequest(BaseModel):
    sampling_rate: float = Field(100.0, gt=0)
    waveform: List[float]


class MagnitudeRequest(BaseModel):
    waveforms: List[List[float]] = Field(..., description="List of waveform segments")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/events/recent")
def recent_events(q: RecentEventsQuery, usgs=Depends(get_usgs_client)):
    try:
        events = usgs.get_recent_events(hours=q.hours, min_magnitude=q.min_magnitude)
        return {"count": len(events.get("features", [])), "data": events}
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/features/extract")
def extract_features(payload: WaveformInput, processor=Depends(get_signal_processor)):
    try:
        feats = processor.extract_features(
            payload.waveform, sampling_rate=payload.sampling_rate
        )
        return {"num_features": len(feats), "features": feats}
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/classify")
def classify(
    payload: ClassificationRequest,
    processor=Depends(get_signal_processor),
    clf=Depends(get_classifier),
):
    try:
        feats = processor.extract_features(
            payload.waveform, sampling_rate=payload.sampling_rate
        )
        preds = clf.predict([feats])
        return {"prediction": preds[0]}
    except FileNotFoundError:
        raise HTTPException(
            status_code=412,
            detail=("Trained model not found. Train and persist a model first."),
        )
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/detect")
async def detect(payload: DetectionRequest, detector=Depends(get_detector)):
    try:
        # Assuming async detect method; if sync, call directly.
        process = getattr(detector, "process_stream", None)
        if process and callable(process):  # async path
            events = await process(payload.waveform)  # type: ignore[arg-type]
        else:  # fallback to detect if available
            detect_fn = getattr(detector, "detect", None)
            if detect_fn is None:
                raise RuntimeError(
                    "Detector has neither process_stream nor detect method"
                )
            events = detect_fn(payload.waveform)
        events = events or []
        return {"num_events": len(events), "events": events}
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/magnitude")
def magnitude(req: MagnitudeRequest, estimator=Depends(get_magnitude_estimator)):
    try:
        batch_fn = getattr(estimator, "batch_estimate", None)
        if batch_fn and callable(batch_fn):
            magnitudes = batch_fn(req.waveforms)
        else:
            # Fallback: call single estimate for each waveform
            single = getattr(estimator, "estimate", None)
            if single is None:
                raise RuntimeError("MagnitudeEstimator missing batch_estimate/estimate")
            magnitudes = [single(w) for w in req.waveforms]

        norm = []
        for m in magnitudes:
            if isinstance(m, dict):
                norm.append(
                    {
                        "magnitude": m.get("magnitude"),
                        "confidence": m.get("confidence"),
                    }
                )
            else:
                norm.append({"magnitude": m, "confidence": None})
        return {"count": len(norm), "magnitudes": norm}
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


__all__ = ["app"]
