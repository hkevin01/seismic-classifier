"""USGS Earthquake API Client.

This module provides a comprehensive client for interacting with the USGS
Earthquake Hazards Program API with rate limiting, caching, and error handling.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

import aiohttp
import requests
from asyncio_throttle import Throttler

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class USGSAPIError(Exception):
    """Base exception for USGS API related errors."""

    pass


class USGSRateLimitError(USGSAPIError):
    """Raised when API rate limit is exceeded."""

    pass


class USGSDataError(USGSAPIError):
    """Raised when API returns invalid or unexpected data."""

    pass


class USGSClient:
    """
    USGS Earthquake API Client with rate limiting and caching.

    This client provides methods to fetch earthquake data from the USGS
    Earthquake Hazards Program API with built-in rate limiting, error
    handling, and local caching capabilities.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize USGS API client.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.base_url = self.config.api.usgs_base_url
        self.timeout = self.config.api.timeout
        self.max_retries = self.config.api.max_retries

        # Rate limiting (USGS allows ~600 requests per 10 minutes)
        self.rate_limit = 1.0  # 1 request per second
        self.last_request_time = 0.0

        # Caching
        self.cache_dir = self.config.cache_dir / "usgs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "seismic-classifier/1.0.0 (Research/Educational)"}
        )

        logger.info(f"Initialized USGS client with base URL: {self.base_url}")

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached data is still valid."""
        if not cache_path.exists():
            return False

        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < self.cache_duration

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved data to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_key}: {e}")

    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load data from cache if valid."""
        cache_path = self._get_cache_path(cache_key)

        if not self._is_cache_valid(cache_path):
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            logger.debug(f"Loaded data from cache: {cache_key}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to USGS API with error handling and retries.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data

        Raises:
            USGSAPIError: For API-related errors
            USGSRateLimitError: For rate limit violations
            USGSDataError: For invalid response data
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Generate cache key
        cache_key = f"{endpoint}_{hash(str(sorted(params.items())))}"

        # Try cache first
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data

        # Enforce rate limiting
        self._enforce_rate_limit()

        # Make request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making request to {url} (attempt {attempt + 1})")

                response = self.session.get(url, params=params, timeout=self.timeout)

                # Check for rate limiting
                if response.status_code == 429:
                    raise USGSRateLimitError("API rate limit exceeded")

                # Check for other HTTP errors
                response.raise_for_status()

                # Parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    raise USGSDataError(f"Invalid JSON response: {e}")

                # Validate response structure
                if not isinstance(data, dict):
                    raise USGSDataError("Response is not a valid JSON object")

                # Cache successful response
                self._save_to_cache(cache_key, data)

                logger.info(f"Successfully fetched data from {endpoint}")
                return data

            except requests.exceptions.Timeout:
                last_exception = USGSAPIError(f"Request timeout after {self.timeout}s")
            except requests.exceptions.ConnectionError:
                last_exception = USGSAPIError("Connection error")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    last_exception = USGSRateLimitError("Rate limit exceeded")
                else:
                    last_exception = USGSAPIError(f"HTTP error: {e}")
            except (USGSRateLimitError, USGSDataError):
                raise  # Don't retry these
            except Exception as e:
                last_exception = USGSAPIError(f"Unexpected error: {e}")

            if attempt < self.max_retries:
                wait_time = 2**attempt  # Exponential backoff
                logger.warning(
                    f"Request failed, retrying in {wait_time}s: {last_exception}"
                )
                time.sleep(wait_time)

        # All retries failed
        raise last_exception

    def get_events(
        self,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        min_magnitude: Optional[float] = None,
        max_magnitude: Optional[float] = None,
        min_depth: Optional[float] = None,
        max_depth: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        max_radius_km: Optional[float] = None,
        limit: int = 20000,
        order_by: str = "time",
        format_type: str = "geojson",
    ) -> Dict[str, Any]:
        """
        Fetch earthquake events from USGS API.

        Args:
            start_time: Start time for search (ISO format or datetime)
            end_time: End time for search (ISO format or datetime)
            min_magnitude: Minimum magnitude threshold
            max_magnitude: Maximum magnitude threshold
            min_depth: Minimum depth in km
            max_depth: Maximum depth in km
            latitude: Center latitude for circular search
            longitude: Center longitude for circular search
            max_radius_km: Maximum radius in km for circular search
            limit: Maximum number of events to return
            order_by: Order results by 'time', 'magnitude', etc.
            format_type: Response format ('geojson', 'csv', 'xml')

        Returns:
            Dictionary containing earthquake event data

        Raises:
            USGSAPIError: For API-related errors
            ValueError: For invalid parameter combinations
        """
        # Build query parameters
        params = {"format": format_type, "orderby": order_by, "limit": limit}

        # Time parameters
        if start_time:
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            params["starttime"] = start_time

        if end_time:
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            params["endtime"] = end_time

        # Magnitude parameters
        if min_magnitude is not None:
            params["minmagnitude"] = min_magnitude
        if max_magnitude is not None:
            params["maxmagnitude"] = max_magnitude

        # Depth parameters
        if min_depth is not None:
            params["mindepth"] = min_depth
        if max_depth is not None:
            params["maxdepth"] = max_depth

        # Geographic parameters
        if latitude is not None and longitude is not None:
            params["latitude"] = latitude
            params["longitude"] = longitude
            if max_radius_km is not None:
                params["maxradiuskm"] = max_radius_km
        elif any(x is not None for x in [latitude, longitude, max_radius_km]):
            raise ValueError(
                "Geographic search requires latitude, longitude, and optionally max_radius_km"
            )

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        logger.info(f"Fetching events with parameters: {params}")

        return self._make_request("query", params)

    def get_recent_events(
        self, hours: int = 24, min_magnitude: float = 2.5
    ) -> Dict[str, Any]:
        """
        Get recent earthquake events.

        Args:
            hours: Number of hours to look back
            min_magnitude: Minimum magnitude threshold

        Returns:
            Dictionary containing recent earthquake events
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        return self.get_events(
            start_time=start_time,
            end_time=end_time,
            min_magnitude=min_magnitude,
            order_by="time-asc",
        )

    def get_significant_events(
        self, days: int = 30, min_magnitude: float = 6.0
    ) -> Dict[str, Any]:
        """
        Get significant earthquake events.

        Args:
            days: Number of days to look back
            min_magnitude: Minimum magnitude for significant events

        Returns:
            Dictionary containing significant earthquake events
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        return self.get_events(
            start_time=start_time,
            end_time=end_time,
            min_magnitude=min_magnitude,
            order_by="magnitude-desc",
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
        logger.info("USGS client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncUSGSClient:
    """
    Async version of USGS API client for high-performance applications.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize async USGS client."""
        self.config = config or Config()
        self.base_url = self.config.api.usgs_base_url
        self.timeout = self.config.api.timeout
        self.max_retries = self.config.api.max_retries

        # Rate limiting
        self.throttler = Throttler(rate_limit=1, period=1)  # 1 req/sec

        # Caching
        self.cache_dir = self.config.cache_dir / "usgs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(minutes=5)

        self.session: Optional[aiohttp.ClientSession] = None

        logger.info("Initialized async USGS client")

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={"User-Agent": "seismic-classifier/1.0.0 (Research/Educational)"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        logger.info("Async USGS client session closed")

    async def get_events_async(self, **kwargs) -> Dict[str, Any]:
        """
        Async version of get_events.

        Args:
            **kwargs: Same parameters as USGSClient.get_events()

        Returns:
            Dictionary containing earthquake event data
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Build parameters (same logic as sync version)
        params = self._build_params(**kwargs)

        # Rate limiting
        async with self.throttler:
            # Make async request
            url = f"{self.base_url.rstrip('/')}/query"

            try:
                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    logger.info(
                        f"Successfully fetched {len(data.get('features', []))} events"
                    )
                    return data

            except aiohttp.ClientError as e:
                raise USGSAPIError(f"Async request failed: {e}")

    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """Build query parameters from keyword arguments."""
        # Implementation similar to sync version
        params = {
            "format": kwargs.get("format_type", "geojson"),
            "orderby": kwargs.get("order_by", "time"),
            "limit": kwargs.get("limit", 20000),
        }

        # Add other parameters as needed
        for key, value in kwargs.items():
            if value is not None and key not in ["format_type", "order_by", "limit"]:
                params[key] = value

        return {k: v for k, v in params.items() if v is not None}
