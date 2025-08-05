"""Data Pipeline Module.

This module provides comprehensive data collection, validation, and storage
capabilities for seismic data from USGS and IRIS sources.
"""

from .usgs_client import USGSClient, AsyncUSGSClient, USGSAPIError
from .iris_client import IRISClient, IRISClientError, preprocess_waveform
from .validators import (
    DataValidator,
    ValidationError,
    DataQualityError,
    DataFormatError,
    validate_earthquake_parameters,
    sanitize_station_code
)
from .database import SeismicDatabase, DatabaseError
from .error_handling import (
    SeismicError,
    RetryableError,
    NonRetryableError,
    CircuitBreakerOpenError,
    ErrorSeverity,
    RetryPolicy,
    CircuitBreaker,
    retry,
    retry_with_policy,
    error_handler,
    health_checker,
    safe_execute,
    validate_and_convert
)

__all__ = [
    # USGS Client
    'USGSClient',
    'AsyncUSGSClient',
    'USGSAPIError',
    
    # IRIS Client
    'IRISClient',
    'IRISClientError',
    'preprocess_waveform',
    
    # Validation
    'DataValidator',
    'ValidationError',
    'DataQualityError',
    'DataFormatError',
    'validate_earthquake_parameters',
    'sanitize_station_code',
    
    # Database
    'SeismicDatabase',
    'DatabaseError',
    
    # Error Handling
    'SeismicError',
    'RetryableError',
    'NonRetryableError',
    'CircuitBreakerOpenError',
    'ErrorSeverity',
    'RetryPolicy',
    'CircuitBreaker',
    'retry',
    'retry_with_policy',
    'error_handler',
    'health_checker',
    'safe_execute',
    'validate_and_convert',
]
