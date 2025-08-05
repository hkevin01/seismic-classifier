"""IRIS Data Client with ObsPy Integration.

This module provides a client for accessing seismic waveform data from IRIS
Data Management Center using ObsPy with error handling and data validation.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import obspy
from obspy import UTCDateTime, Stream, Trace
from obspy.clients.fdsn import Client as FDSNClient
from obspy.core.event import Event, Catalog

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IRISClientError(Exception):
    """Base exception for IRIS client related errors."""
    pass


class IRISDataError(IRISClientError):
    """Raised when IRIS returns invalid or unexpected data."""
    pass


class IRISNetworkError(IRISClientError):
    """Raised for network-related errors with IRIS."""
    pass


class IRISClient:
    """
    IRIS Data Management Center client with ObsPy integration.
    
    This client provides methods to fetch seismic waveform data, station
    metadata, and event information from IRIS with built-in error handling
    and data quality validation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize IRIS client.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.timeout = self.config.api.timeout
        self.max_retries = self.config.api.max_retries
        
        # Initialize FDSN clients for different services
        try:
            self.waveform_client = FDSNClient("IRIS", timeout=self.timeout)
            self.event_client = FDSNClient("IRIS", timeout=self.timeout)
            self.station_client = FDSNClient("IRIS", timeout=self.timeout)
            logger.info("Initialized IRIS FDSN clients successfully")
        except Exception as e:
            raise IRISClientError(f"Failed to initialize IRIS clients: {e}")
        
        # Cache directory for waveform data
        self.cache_dir = self.config.cache_dir / "iris"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting (IRIS has more lenient limits than USGS)
        self.rate_limit = 0.5  # 2 requests per second
        self.last_request_time = 0.0
        
        logger.info("IRIS client initialized with ObsPy integration")
    
    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _validate_waveform_data(self, stream: Stream) -> bool:
        """
        Validate waveform data quality.
        
        Args:
            stream: ObsPy Stream object
            
        Returns:
            True if data passes quality checks
        """
        if not stream:
            logger.warning("Empty stream received")
            return False
        
        for trace in stream:
            # Check for gaps
            if len(trace.get_gaps()) > 0:
                logger.warning(f"Gaps found in trace {trace.id}")
            
            # Check sampling rate consistency
            expected_sr = self.config.data.sampling_rate
            if abs(trace.stats.sampling_rate - expected_sr) > 0.1:
                logger.warning(
                    f"Sampling rate mismatch: expected {expected_sr}, "
                    f"got {trace.stats.sampling_rate} for {trace.id}"
                )
            
            # Check for minimum data length
            min_length = self.config.data.window_length
            if trace.stats.npts < min_length * trace.stats.sampling_rate:
                logger.warning(
                    f"Trace {trace.id} too short: {trace.stats.npts} samples"
                )
        
        return True
    
    def get_waveforms(
        self,
        network: str,
        station: str,
        start_time: Union[str, datetime, UTCDateTime],
        end_time: Union[str, datetime, UTCDateTime],
        location: str = "*",
        channel: str = "*",
        attach_response: bool = True,
        remove_response: bool = False
    ) -> Stream:
        """
        Fetch seismic waveform data from IRIS.
        
        Args:
            network: Network code (e.g., 'IU', 'US')
            station: Station code (e.g., 'ANMO', 'COLA')
            location: Location code (default '*')
            channel: Channel code (e.g., 'BHZ', 'HHZ', default '*')
            start_time: Start time for data request
            end_time: End time for data request
            attach_response: Whether to attach instrument response
            remove_response: Whether to remove instrument response
            
        Returns:
            ObsPy Stream object containing waveform data
            
        Raises:
            IRISClientError: For client-related errors
            IRISDataError: For data-related errors
        """
        # Convert time parameters to UTCDateTime
        if not isinstance(start_time, UTCDateTime):
            start_time = UTCDateTime(start_time)
        if not isinstance(end_time, UTCDateTime):
            end_time = UTCDateTime(end_time)
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        logger.info(
            f"Fetching waveforms: {network}.{station}.{location}.{channel} "
            f"from {start_time} to {end_time}"
        )
        
        # Attempt to fetch data with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                stream = self.waveform_client.get_waveforms(
                    network=network,
                    station=station,
                    location=location,
                    channel=channel,
                    starttime=start_time,
                    endtime=end_time,
                    attach_response=attach_response
                )
                
                # Validate data quality
                if not self._validate_waveform_data(stream):
                    logger.warning("Waveform data failed quality validation")
                
                # Remove instrument response if requested
                if remove_response and attach_response:
                    try:
                        stream.remove_response(output="VEL")
                        logger.info("Instrument response removed successfully")
                    except Exception as e:
                        logger.warning(f"Failed to remove response: {e}")
                
                logger.info(f"Successfully fetched {len(stream)} traces")
                return stream
                
            except Exception as e:
                last_exception = IRISNetworkError(f"Request failed: {e}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Waveform request failed, retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
        
        # All retries failed
        raise last_exception
    
    def get_events(
        self,
        start_time: Union[str, datetime, UTCDateTime],
        end_time: Union[str, datetime, UTCDateTime],
        min_magnitude: Optional[float] = None,
        max_magnitude: Optional[float] = None,
        min_latitude: Optional[float] = None,
        max_latitude: Optional[float] = None,
        min_longitude: Optional[float] = None,
        max_longitude: Optional[float] = None,
        limit: Optional[int] = None
    ) -> Catalog:
        """
        Fetch earthquake events from IRIS.
        
        Args:
            start_time: Start time for search
            end_time: End time for search
            min_magnitude: Minimum magnitude
            max_magnitude: Maximum magnitude
            min_latitude: Minimum latitude
            max_latitude: Maximum latitude
            min_longitude: Minimum longitude
            max_longitude: Maximum longitude
            limit: Maximum number of events
            
        Returns:
            ObsPy Catalog object containing events
            
        Raises:
            IRISClientError: For client-related errors
        """
        # Convert time parameters
        if not isinstance(start_time, UTCDateTime):
            start_time = UTCDateTime(start_time)
        if not isinstance(end_time, UTCDateTime):
            end_time = UTCDateTime(end_time)
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        logger.info(f"Fetching events from {start_time} to {end_time}")
        
        try:
            catalog = self.event_client.get_events(
                starttime=start_time,
                endtime=end_time,
                minmagnitude=min_magnitude,
                maxmagnitude=max_magnitude,
                minlatitude=min_latitude,
                maxlatitude=max_latitude,
                minlongitude=min_longitude,
                maxlongitude=max_longitude,
                limit=limit
            )
            
            logger.info(f"Successfully fetched {len(catalog)} events")
            return catalog
            
        except Exception as e:
            raise IRISClientError(f"Failed to fetch events: {e}")
    
    def get_stations(
        self,
        network: str = "*",
        station: str = "*",
        location: str = "*",
        channel: str = "*",
        start_time: Optional[Union[str, datetime, UTCDateTime]] = None,
        end_time: Optional[Union[str, datetime, UTCDateTime]] = None,
        min_latitude: Optional[float] = None,
        max_latitude: Optional[float] = None,
        min_longitude: Optional[float] = None,
        max_longitude: Optional[float] = None
    ) -> obspy.Inventory:
        """
        Fetch station metadata from IRIS.
        
        Args:
            network: Network code pattern
            station: Station code pattern
            location: Location code pattern
            channel: Channel code pattern
            start_time: Start time for station operation
            end_time: End time for station operation
            min_latitude: Minimum latitude
            max_latitude: Maximum latitude
            min_longitude: Minimum longitude
            max_longitude: Maximum longitude
            
        Returns:
            ObsPy Inventory object containing station metadata
            
        Raises:
            IRISClientError: For client-related errors
        """
        # Convert time parameters if provided
        if start_time and not isinstance(start_time, UTCDateTime):
            start_time = UTCDateTime(start_time)
        if end_time and not isinstance(end_time, UTCDateTime):
            end_time = UTCDateTime(end_time)
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        logger.info(f"Fetching stations: {network}.{station}.{location}.{channel}")
        
        try:
            inventory = self.station_client.get_stations(
                network=network,
                station=station,
                location=location,
                channel=channel,
                starttime=start_time,
                endtime=end_time,
                minlatitude=min_latitude,
                maxlatitude=max_latitude,
                minlongitude=min_longitude,
                maxlongitude=max_longitude,
                level="response"
            )
            
            logger.info(f"Successfully fetched station metadata")
            return inventory
            
        except Exception as e:
            raise IRISClientError(f"Failed to fetch stations: {e}")
    
    def get_waveforms_for_event(
        self,
        event: Event,
        networks: List[str] = ["IU", "US", "N4"],
        channels: List[str] = ["BHZ", "HHZ"],
        time_before: float = 60.0,
        time_after: float = 300.0,
        max_distance_km: float = 1000.0
    ) -> Stream:
        """
        Fetch waveforms for a specific earthquake event.
        
        Args:
            event: ObsPy Event object
            networks: List of network codes to search
            channels: List of channel codes to fetch
            time_before: Seconds before event origin time
            time_after: Seconds after event origin time
            max_distance_km: Maximum station distance from event
            
        Returns:
            ObsPy Stream object with waveforms
            
        Raises:
            IRISClientError: For client-related errors
        """
        origin = event.preferred_origin() or event.origins[0]
        origin_time = origin.time
        
        start_time = origin_time - time_before
        end_time = origin_time + time_after
        
        logger.info(
            f"Fetching waveforms for event at {origin_time} "
            f"({origin.latitude}, {origin.longitude})"
        )
        
        # Get nearby stations
        inventory = self.get_stations(
            network=",".join(networks),
            channel=",".join(channels),
            start_time=start_time,
            end_time=end_time,
            min_latitude=origin.latitude - 10,
            max_latitude=origin.latitude + 10,
            min_longitude=origin.longitude - 10,
            max_longitude=origin.longitude + 10
        )
        
        # Fetch waveforms from available stations
        combined_stream = Stream()
        
        for network in inventory:
            for station in network:
                try:
                    stream = self.get_waveforms(
                        network=network.code,
                        station=station.code,
                        location="*",
                        channel=",".join(channels),
                        start_time=start_time,
                        end_time=end_time,
                        attach_response=True
                    )
                    combined_stream += stream
                    
                except Exception as e:
                    logger.debug(f"Failed to get waveforms for {network.code}.{station.code}: {e}")
                    continue
        
        logger.info(f"Collected {len(combined_stream)} traces for event")
        return combined_stream
    
    def save_waveforms(
        self,
        stream: Stream,
        filepath: Union[str, Path],
        format_type: str = "MSEED"
    ) -> None:
        """
        Save waveform data to file.
        
        Args:
            stream: ObsPy Stream object
            filepath: Output file path
            format_type: File format ('MSEED', 'SAC', 'PICKLE')
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            stream.write(str(filepath), format=format_type)
            logger.info(f"Saved {len(stream)} traces to {filepath}")
        except Exception as e:
            raise IRISDataError(f"Failed to save waveforms: {e}")
    
    def load_waveforms(
        self,
        filepath: Union[str, Path],
        format_type: str = "MSEED"
    ) -> Stream:
        """
        Load waveform data from file.
        
        Args:
            filepath: Input file path
            format_type: File format ('MSEED', 'SAC', 'PICKLE')
            
        Returns:
            ObsPy Stream object
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise IRISDataError(f"File not found: {filepath}")
        
        try:
            stream = obspy.read(str(filepath), format=format_type)
            logger.info(f"Loaded {len(stream)} traces from {filepath}")
            return stream
        except Exception as e:
            raise IRISDataError(f"Failed to load waveforms: {e}")


def preprocess_waveform(
    stream: Stream,
    filter_type: str = "bandpass",
    freqmin: float = 0.1,
    freqmax: float = 50.0,
    detrend_type: str = "linear",
    taper_percentage: float = 0.05
) -> Stream:
    """
    Apply basic preprocessing to waveform data.
    
    Args:
        stream: Input ObsPy Stream
        filter_type: Filter type ('bandpass', 'highpass', 'lowpass')
        freqmin: Minimum frequency for bandpass filter
        freqmax: Maximum frequency for bandpass filter
        detrend_type: Detrending method ('linear', 'constant', 'polynomial')
        taper_percentage: Taper percentage (0.0 to 1.0)
        
    Returns:
        Preprocessed ObsPy Stream
    """
    # Make a copy to avoid modifying original
    processed_stream = stream.copy()
    
    try:
        # Remove mean and trend
        processed_stream.detrend(type=detrend_type)
        
        # Apply taper
        processed_stream.taper(max_percentage=taper_percentage)
        
        # Apply filter
        if filter_type == "bandpass":
            processed_stream.filter("bandpass", freqmin=freqmin, freqmax=freqmax)
        elif filter_type == "highpass":
            processed_stream.filter("highpass", freq=freqmin)
        elif filter_type == "lowpass":
            processed_stream.filter("lowpass", freq=freqmax)
        
        logger.info(f"Applied {filter_type} preprocessing to {len(processed_stream)} traces")
        return processed_stream
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise IRISDataError(f"Waveform preprocessing failed: {e}")
