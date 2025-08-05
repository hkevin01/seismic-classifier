from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SeismicData(BaseModel):
    waveform: List[float]
    metadata: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    event_detected: bool
    magnitude: Optional[float] = None
    location: Optional[Dict[str, float]] = None
    confidence: Optional[Dict[str, float]] = None
    timestamp: datetime


class SystemStatus(BaseModel):
    status: str
    components: Dict[str, str]
    timestamp: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    token_type: str
