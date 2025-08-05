import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

from seismic_classifier.advanced_analytics.confidence_analysis import ConfidenceAnalyzer
from seismic_classifier.advanced_analytics.event_detection import EventDetector
from seismic_classifier.advanced_analytics.location_determination import (
    LocationDeterminer,
)
from seismic_classifier.advanced_analytics.magnitude_estimation import (
    MagnitudeEstimator,
)

# Initialize FastAPI app
app = FastAPI(
    title="Seismic Classifier API",
    description="API for real-time seismic event classification and analysis",
    version="1.0.0"
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")

# Metrics
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request duration", ["endpoint"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
event_detector = EventDetector()
magnitude_estimator = MagnitudeEstimator()
location_determiner = LocationDeterminer()
confidence_analyzer = ConfidenceAnalyzer()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUESTS.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    LATENCY.labels(endpoint=request.url.path).observe(duration)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/auth/token")
async def login(username: str, password: str):
    # In production, implement proper authentication
    if username == "demo" and password == "demo":
        access_token = create_access_token({"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/analyze")
async def analyze_seismic_data(
    data: Dict[str, Any],
    token: Dict[str, Any] = Depends(verify_token)
):
    try:
        # Event detection
        event = event_detector.detect(data["waveform"])
        if not event:
            return JSONResponse(
                status_code=200,
                content={"message": "No seismic event detected"}
            )

        # Analysis
        magnitude = magnitude_estimator.estimate(data["waveform"])
        location = location_determiner.determine(data["waveform"])
        confidence = confidence_analyzer.analyze(
            event=event,
            magnitude=magnitude,
            location=location
        )

        return {
            "event_detected": True,
            "magnitude": magnitude,
            "location": location,
            "confidence": confidence,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Error analyzing seismic data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing seismic data"
        )

@app.get("/status")
async def get_system_status(token: Dict[str, Any] = Depends(verify_token)):
    return {
        "status": "operational",
        "components": {
            "event_detector": "healthy",
            "magnitude_estimator": "healthy",
            "location_determiner": "healthy",
            "confidence_analyzer": "healthy"
        },
        "timestamp": datetime.utcnow()
    }
            "location_determiner": "healthy",
            "confidence_analyzer": "healthy"
        },
        "timestamp": datetime.utcnow()
    }
