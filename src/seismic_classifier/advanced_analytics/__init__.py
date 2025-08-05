"""
Advanced Analytics module for real-time seismic event detection and analysis.
This module provides tools for event detection, magnitude estimation,
location determination, and confidence interval analysis.
"""

from .confidence_analysis import ConfidenceAnalyzer
from .event_detection import RealTimeDetector
from .location_determination import LocationDeterminer
from .magnitude_estimation import MagnitudeEstimator

__all__ = [
    "RealTimeDetector",
    "MagnitudeEstimator",
    "LocationDeterminer",
    "ConfidenceAnalyzer",
]
