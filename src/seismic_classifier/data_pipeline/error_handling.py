"""Error Handling and Resilience Patterns.

This module provides comprehensive error handling, retry mechanisms,
circuit breakers, and resilience patterns for the seismic classifier system.
"""

import asyncio
import functools
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class SeismicError(Exception):
    """Base exception for seismic classifier errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()


class RetryableError(SeismicError):
    """Exception that can be retried."""

    pass


class NonRetryableError(SeismicError):
    """Exception that should not be retried."""

    pass


class CircuitBreakerOpenError(SeismicError):
    """Raised when circuit breaker is open."""

    pass


class RetryPolicy:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [
            RetryableError,
            ConnectionError,
            TimeoutError,
        ]

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should trigger a retry."""
        if attempt >= self.max_attempts:
            return False

        if isinstance(exception, NonRetryableError):
            return False

        return any(
            isinstance(exception, exc_type) for exc_type in self.retryable_exceptions
        )

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt."""
        delay = self.base_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            import random

            delay *= 0.5 + random.random() * 0.5  # ±50% jitter

        return delay


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.

    Prevents cascading failures by temporarily disabling failing services.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED

        logger.info(
            f"Circuit breaker initialized: threshold={failure_threshold}, timeout={timeout}s"
        )

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._call(func, *args, **kwargs)

        return wrapper

    def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.last_failure_time is None:
            return True

        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)

    def _on_success(self) -> None:
        """Handle successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker reset to CLOSED")

        self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )


def retry_with_policy(policy: RetryPolicy):
    """Decorator to add retry logic with custom policy."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(policy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if not policy.should_retry(e, attempt):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise

                    if attempt < policy.max_attempts - 1:  # Don't sleep on last attempt
                        delay = policy.calculate_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s"
                        )
                        time.sleep(delay)

            # All attempts failed
            logger.error(
                f"All {policy.max_attempts} attempts failed for {func.__name__}"
            )
            raise last_exception

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
):
    """Simple retry decorator with exponential backoff."""
    policy = RetryPolicy(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
    )
    return retry_with_policy(policy)


async def async_retry_with_policy(policy: RetryPolicy):
    """Async decorator to add retry logic with custom policy."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(policy.max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if not policy.should_retry(e, attempt):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise

                    if attempt < policy.max_attempts - 1:
                        delay = policy.calculate_delay(attempt)
                        logger.warning(
                            f"Async attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s"
                        )
                        await asyncio.sleep(delay)

            logger.error(
                f"All {policy.max_attempts} async attempts failed for {func.__name__}"
            )
            raise last_exception

        return wrapper

    return decorator


class ErrorHandler:
    """
    Centralized error handling and reporting system.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 1000

        logger.info("Error handler initialized")

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> None:
        """
        Handle and log error with context information.

        Args:
            error: Exception that occurred
            context: Additional context information
            severity: Error severity level
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "severity": severity.value,
            "context": context or {},
        }

        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        # Update error counts
        error_key = f"{type(error).__name__}:{severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error}", extra={"context": context})
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY: {error}", extra={"context": context})
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY: {error}", extra={"context": context})
        else:
            logger.info(f"LOW SEVERITY: {error}", extra={"context": context})

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error statistics."""
        total_errors = len(self.error_history)
        recent_errors = [
            e
            for e in self.error_history
            if datetime.fromisoformat(e["timestamp"])
            > datetime.now() - timedelta(hours=1)
        ]

        severity_counts = {}
        for error in self.error_history:
            severity = error["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_errors": total_errors,
            "recent_errors_1h": len(recent_errors),
            "error_counts_by_type": self.error_counts.copy(),
            "severity_distribution": severity_counts,
            "most_recent_errors": (
                self.error_history[-10:] if self.error_history else []
            ),
        }


class HealthChecker:
    """
    System health monitoring and reporting.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.checks: Dict[str, Callable] = {}
        self.last_check_results: Dict[str, Dict[str, Any]] = {}

        # Register default health checks
        self._register_default_checks()

        logger.info("Health checker initialized")

    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    def _register_default_checks(self) -> None:
        """Register default system health checks."""

        def check_disk_space() -> Dict[str, Any]:
            """Check available disk space."""
            import shutil

            try:
                total, used, free = shutil.disk_usage(self.config.data_dir)
                free_percent = (free / total) * 100

                return {
                    "status": "healthy" if free_percent > 10 else "warning",
                    "free_space_gb": free / (1024**3),
                    "free_percent": free_percent,
                    "message": f"{free_percent:.1f}% disk space available",
                }
            except Exception as e:
                return {"status": "error", "message": f"Disk check failed: {e}"}

        def check_memory_usage() -> Dict[str, Any]:
            """Check memory usage."""
            import psutil

            try:
                memory = psutil.virtual_memory()
                return {
                    "status": "healthy" if memory.percent < 90 else "warning",
                    "memory_percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "message": f"{memory.percent:.1f}% memory used",
                }
            except Exception as e:
                return {"status": "error", "message": f"Memory check failed: {e}"}

        self.register_check("disk_space", check_disk_space)
        self.register_check("memory_usage", check_memory_usage)

    def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks."""
        results = {}

        for name, check_func in self.checks.items():
            try:
                result = check_func()
                result["timestamp"] = datetime.now().isoformat()
                results[name] = result

                # Log warnings and errors
                if result.get("status") == "warning":
                    logger.warning(
                        f"Health check warning ({name}): {result.get('message')}"
                    )
                elif result.get("status") == "error":
                    logger.error(
                        f"Health check error ({name}): {result.get('message')}"
                    )

            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": f"Health check failed: {e}",
                    "timestamp": datetime.now().isoformat(),
                }
                logger.error(f"Health check {name} failed: {e}")

        self.last_check_results = results
        return results

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.last_check_results:
            self.run_checks()

        healthy_count = sum(
            1 for r in self.last_check_results.values() if r.get("status") == "healthy"
        )
        warning_count = sum(
            1 for r in self.last_check_results.values() if r.get("status") == "warning"
        )
        error_count = sum(
            1 for r in self.last_check_results.values() if r.get("status") == "error"
        )

        total_checks = len(self.last_check_results)

        if error_count > 0:
            overall_status = "unhealthy"
        elif warning_count > total_checks * 0.5:  # More than 50% warnings
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "healthy_checks": healthy_count,
            "warning_checks": warning_count,
            "error_checks": error_count,
            "total_checks": total_checks,
            "health_score": (
                (healthy_count / total_checks * 100) if total_checks > 0 else 0
            ),
            "last_check_time": datetime.now().isoformat(),
        }


# Global instances
error_handler = ErrorHandler()
health_checker = HealthChecker()


# Utility functions for common error handling patterns
def safe_execute(
    func: Callable, default_return: Any = None, log_errors: bool = True, **kwargs
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        default_return: Value to return on error
        log_errors: Whether to log errors
        **kwargs: Arguments to pass to function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(**kwargs)
    except Exception as e:
        if log_errors:
            error_handler.handle_error(e, context={"function": func.__name__})
        return default_return


def validate_and_convert(
    value: Any,
    target_type: Type,
    default: Any = None,
    validator: Optional[Callable] = None,
) -> Any:
    """
    Validate and convert value to target type with error handling.

    Args:
        value: Value to convert
        target_type: Target type
        default: Default value on conversion failure
        validator: Optional validation function

    Returns:
        Converted value or default
    """
    try:
        converted = target_type(value)

        if validator and not validator(converted):
            raise ValueError(f"Validation failed for {converted}")

        return converted
    except Exception as e:
        logger.warning(f"Conversion failed for {value} to {target_type}: {e}")
        return default
