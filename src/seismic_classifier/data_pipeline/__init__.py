"""Data Pipeline Module.

This module provides comprehensive data collection, validation, and storage
capabilities for seismic data from USGS and IRIS sources.
"""

from .database import DatabaseError, SeismicDatabase
from .error_handling import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    ErrorSeverity,
    NonRetryableError,
    RetryableError,
    RetryPolicy,
    SeismicError,
    error_handler,
    health_checker,
    retry,
    retry_with_policy,
    safe_execute,
    validate_and_convert,
)
from .iris_client import IRISClient, IRISClientError, preprocess_waveform
from .usgs_client import AsyncUSGSClient, USGSAPIError, USGSClient
from .validators import (
    DataFormatError,
    DataQualityError,
    DataValidator,
    ValidationError,
    sanitize_station_code,
    validate_earthquake_parameters,
)

__all__ = [
    # USGS Client
    "USGSClient",
    "AsyncUSGSClient",
    "USGSAPIError",
    # IRIS Client
    "IRISClient",
    "IRISClientError",
    "preprocess_waveform",
    # Validation
    "DataValidator",
    "ValidationError",
    "DataQualityError",
    "DataFormatError",
    "validate_earthquake_parameters",
    "sanitize_station_code",
    # Database
    "SeismicDatabase",
    "DatabaseError",
    # Error Handling
    "SeismicError",
    "RetryableError",
    "NonRetryableError",
    "CircuitBreakerOpenError",
    "ErrorSeverity",
    "RetryPolicy",
    "CircuitBreaker",
    "retry",
    "retry_with_policy",
    "error_handler",
    "health_checker",
    "safe_execute",
    "validate_and_convert",
]
