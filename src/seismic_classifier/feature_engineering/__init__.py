"""Feature Engineering Module.

This module provides comprehensive feature engineering capabilities for
seismic waveform classification including signal processing, feature
extraction, and data transformation.
"""

from .signal_processing import (
    SignalProcessor,
    calculate_spectral_features,
    calculate_time_domain_features,
    estimate_noise_level
)

from .feature_extraction import (
    FeatureExtractor,
    extract_features_from_stream
)

__all__ = [
    'SignalProcessor',
    'FeatureExtractor',
    'calculate_spectral_features',
    'calculate_time_domain_features',
    'estimate_noise_level',
    'extract_features_from_stream'
]
