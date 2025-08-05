"""Data Validation and Quality Control.

This module provides comprehensive validation and quality control for
seismic data from USGS and IRIS sources.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

import numpy as np
import pandas as pd
from obspy import Stream, Trace, UTCDateTime

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Base exception for data validation errors."""
    pass


class DataQualityError(ValidationError):
    """Raised when data fails quality checks."""
    pass


class DataFormatError(ValidationError):
    """Raised when data format is invalid."""
    pass


class DataValidator:
    """
    Comprehensive data validation and quality control system.
    
    This class provides methods to validate seismic data from various
    sources and ensure data integrity and quality standards.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize data validator."""
        self.config = config or Config()
        self.quality_thresholds = {
            'min_sampling_rate': 1.0,
            'max_sampling_rate': 1000.0,
            'min_duration': 10.0,  # seconds
            'max_gap_ratio': 0.1,  # 10% gaps allowed
            'min_snr': 3.0,  # Signal-to-noise ratio
            'max_std_ratio': 5.0,  # Standard deviation ratio
        }
        
        logger.info("Data validator initialized")
    
    def validate_usgs_response(self, data: Dict[str, Any]) -> bool:
        """
        Validate USGS API response data.
        
        Args:
            data: USGS API response dictionary
            
        Returns:
            True if data is valid
            
        Raises:
            DataFormatError: If data format is invalid
            DataQualityError: If data quality is poor
        """
        logger.debug("Validating USGS response data")
        
        # Check basic structure
        if not isinstance(data, dict):
            raise DataFormatError("USGS response must be a dictionary")
        
        # Check for required fields
        required_fields = ['type', 'features']
        for field in required_fields:
            if field not in data:
                raise DataFormatError(f"Missing required field: {field}")
        
        # Validate GeoJSON structure
        if data.get('type') != 'FeatureCollection':
            raise DataFormatError("Invalid GeoJSON type")
        
        features = data.get('features', [])
        if not isinstance(features, list):
            raise DataFormatError("Features must be a list")
        
        # Validate individual events
        valid_events = 0
        for i, feature in enumerate(features):
            try:
                self._validate_usgs_event(feature)
                valid_events += 1
            except ValidationError as e:
                logger.warning(f"Event {i} validation failed: {e}")
        
        # Check if we have enough valid events
        valid_ratio = valid_events / len(features) if features else 0
        if valid_ratio < 0.8:  # 80% threshold
            raise DataQualityError(
                f"Only {valid_ratio:.1%} of events are valid"
            )
        
        logger.info(f"USGS validation passed: {valid_events}/{len(features)} events valid")
        return True
    
    def _validate_usgs_event(self, event: Dict[str, Any]) -> bool:
        """Validate individual USGS event."""
        # Check event structure
        if not isinstance(event, dict):
            raise DataFormatError("Event must be a dictionary")
        
        if event.get('type') != 'Feature':
            raise DataFormatError("Event type must be 'Feature'")
        
        # Check geometry
        geometry = event.get('geometry')
        if not geometry:
            raise DataFormatError("Missing geometry")
        
        coordinates = geometry.get('coordinates')
        if not coordinates or len(coordinates) < 3:
            raise DataFormatError("Invalid coordinates")
        
        longitude, latitude, depth = coordinates[:3]
        
        # Validate coordinate ranges
        if not (-180 <= longitude <= 180):
            raise DataQualityError(f"Invalid longitude: {longitude}")
        
        if not (-90 <= latitude <= 90):
            raise DataQualityError(f"Invalid latitude: {latitude}")
        
        if depth < -10 or depth > 1000:  # km
            raise DataQualityError(f"Suspicious depth: {depth} km")
        
        # Check properties
        properties = event.get('properties', {})
        
        # Validate magnitude
        magnitude = properties.get('mag')
        if magnitude is not None:
            if not (-2 <= magnitude <= 10):
                raise DataQualityError(f"Suspicious magnitude: {magnitude}")
        
        # Validate time
        event_time = properties.get('time')
        if event_time:
            try:
                # Convert from milliseconds to datetime
                dt = datetime.fromtimestamp(event_time / 1000.0)
                # Check if event is too far in the future
                if dt > datetime.now():
                    raise DataQualityError("Event time in the future")
            except (ValueError, TypeError):
                raise DataFormatError("Invalid event time format")
        
        return True
    
    def validate_waveform_stream(self, stream: Stream) -> bool:
        """
        Validate ObsPy Stream object.
        
        Args:
            stream: ObsPy Stream to validate
            
        Returns:
            True if stream passes validation
            
        Raises:
            DataFormatError: If stream format is invalid
            DataQualityError: If stream quality is poor
        """
        logger.debug(f"Validating stream with {len(stream)} traces")
        
        if not isinstance(stream, Stream):
            raise DataFormatError("Input must be an ObsPy Stream object")
        
        if len(stream) == 0:
            raise DataFormatError("Stream is empty")
        
        valid_traces = 0
        for trace in stream:
            try:
                self._validate_trace(trace)
                valid_traces += 1
            except ValidationError as e:
                logger.warning(f"Trace {trace.id} validation failed: {e}")
        
        # Check if we have enough valid traces
        valid_ratio = valid_traces / len(stream)
        if valid_ratio < 0.7:  # 70% threshold
            raise DataQualityError(
                f"Only {valid_ratio:.1%} of traces are valid"
            )
        
        logger.info(f"Stream validation passed: {valid_traces}/{len(stream)} traces valid")
        return True
    
    def _validate_trace(self, trace: Trace) -> bool:
        """Validate individual trace."""
        stats = trace.stats
        data = trace.data
        
        # Check sampling rate
        sr = stats.sampling_rate
        if not (self.quality_thresholds['min_sampling_rate'] <= sr <= 
                self.quality_thresholds['max_sampling_rate']):
            raise DataQualityError(f"Invalid sampling rate: {sr} Hz")
        
        # Check duration
        duration = stats.npts / sr
        if duration < self.quality_thresholds['min_duration']:
            raise DataQualityError(f"Trace too short: {duration:.1f}s")
        
        # Check for data availability
        if len(data) == 0:
            raise DataFormatError("Trace has no data")
        
        # Check for NaN or infinite values
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise DataQualityError("Trace contains NaN or infinite values")
        
        # Check for constant data (likely sensor failure)
        if np.std(data) == 0:
            raise DataQualityError("Trace has constant values")
        
        # Check for extreme values (possible clipping)
        data_range = np.ptp(data)  # peak-to-peak
        if data_range == 0:
            raise DataQualityError("No signal variation detected")
        
        # Check signal-to-noise ratio (simplified)
        signal_power = np.var(data)
        noise_estimate = np.var(data[:int(0.1 * len(data))])  # First 10%
        if noise_estimate > 0:
            snr = signal_power / noise_estimate
            if snr < self.quality_thresholds['min_snr']:
                raise DataQualityError(f"Low SNR: {snr:.2f}")
        
        return True
    
    def check_data_gaps(self, stream: Stream) -> Dict[str, Any]:
        """
        Check for gaps in waveform data.
        
        Args:
            stream: ObsPy Stream to check
            
        Returns:
            Dictionary with gap information
        """
        gap_info = {
            'total_gaps': 0,
            'gap_ratio': 0.0,
            'gap_details': []
        }
        
        total_expected_samples = 0
        total_actual_samples = 0
        
        for trace in stream:
            gaps = trace.get_gaps()
            gap_info['total_gaps'] += len(gaps)
            
            # Calculate expected vs actual samples
            start_time = trace.stats.starttime
            end_time = trace.stats.endtime
            expected_duration = end_time - start_time
            expected_samples = int(expected_duration * trace.stats.sampling_rate)
            actual_samples = trace.stats.npts
            
            total_expected_samples += expected_samples
            total_actual_samples += actual_samples
            
            for gap in gaps:
                gap_info['gap_details'].append({
                    'trace_id': trace.id,
                    'start_time': str(gap[4]),
                    'end_time': str(gap[5]),
                    'duration': gap[6],
                    'samples': gap[7]
                })
        
        # Calculate overall gap ratio
        if total_expected_samples > 0:
            gap_info['gap_ratio'] = 1.0 - (total_actual_samples / total_expected_samples)
        
        logger.info(f"Gap analysis: {gap_info['total_gaps']} gaps, "
                   f"{gap_info['gap_ratio']:.1%} missing data")
        
        return gap_info
    
    def calculate_data_quality_score(self, stream: Stream) -> float:
        """
        Calculate overall data quality score (0-100).
        
        Args:
            stream: ObsPy Stream to evaluate
            
        Returns:
            Quality score between 0 and 100
        """
        if len(stream) == 0:
            return 0.0
        
        scores = []
        
        for trace in stream:
            trace_score = 100.0
            
            try:
                # Check basic validation
                self._validate_trace(trace)
            except ValidationError:
                trace_score *= 0.5  # 50% penalty for failed validation
            
            # Check gaps
            gaps = trace.get_gaps()
            if gaps:
                gap_penalty = min(len(gaps) * 10, 50)  # Max 50% penalty
                trace_score -= gap_penalty
            
            # Check sampling rate consistency
            expected_sr = self.config.data.sampling_rate
            sr_diff = abs(trace.stats.sampling_rate - expected_sr)
            if sr_diff > 0.1:
                trace_score -= min(sr_diff * 5, 20)  # Max 20% penalty
            
            # Check duration
            duration = trace.stats.npts / trace.stats.sampling_rate
            min_duration = self.quality_thresholds['min_duration']
            if duration < min_duration:
                duration_penalty = (1 - duration / min_duration) * 30
                trace_score -= duration_penalty
            
            scores.append(max(0, trace_score))
        
        overall_score = np.mean(scores)
        logger.info(f"Data quality score: {overall_score:.1f}/100")
        
        return overall_score
    
    def generate_validation_report(
        self,
        stream: Stream,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.
        
        Args:
            stream: ObsPy Stream to analyze
            output_path: Optional path to save report
            
        Returns:
            Validation report dictionary
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'stream_info': {
                'num_traces': len(stream),
                'trace_ids': [tr.id for tr in stream],
                'sampling_rates': [tr.stats.sampling_rate for tr in stream],
                'durations': [tr.stats.npts / tr.stats.sampling_rate for tr in stream]
            },
            'validation_results': {},
            'quality_metrics': {},
            'recommendations': []
        }
        
        # Run validation checks
        try:
            self.validate_waveform_stream(stream)
            report['validation_results']['overall'] = 'PASSED'
        except ValidationError as e:
            report['validation_results']['overall'] = 'FAILED'
            report['validation_results']['error'] = str(e)
        
        # Calculate quality metrics
        report['quality_metrics']['quality_score'] = self.calculate_data_quality_score(stream)
        report['quality_metrics']['gap_info'] = self.check_data_gaps(stream)
        
        # Generate recommendations
        if report['quality_metrics']['quality_score'] < 70:
            report['recommendations'].append("Consider filtering or reprocessing data")
        
        if report['quality_metrics']['gap_info']['gap_ratio'] > 0.1:
            report['recommendations'].append("Significant data gaps detected - consider interpolation")
        
        # Save report if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Validation report saved to {output_path}")
        
        return report


def validate_earthquake_parameters(
    magnitude: Optional[float] = None,
    depth: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> bool:
    """
    Validate earthquake parameter ranges.
    
    Args:
        magnitude: Earthquake magnitude
        depth: Depth in kilometers
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        
    Returns:
        True if all parameters are valid
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    if magnitude is not None:
        if not (-2 <= magnitude <= 10):
            raise ValidationError(f"Invalid magnitude: {magnitude}")
    
    if depth is not None:
        if not (0 <= depth <= 800):
            raise ValidationError(f"Invalid depth: {depth} km")
    
    if latitude is not None:
        if not (-90 <= latitude <= 90):
            raise ValidationError(f"Invalid latitude: {latitude}")
    
    if longitude is not None:
        if not (-180 <= longitude <= 180):
            raise ValidationError(f"Invalid longitude: {longitude}")
    
    return True


def sanitize_station_code(code: str) -> str:
    """
    Sanitize and validate station codes.
    
    Args:
        code: Station code to sanitize
        
    Returns:
        Cleaned station code
        
    Raises:
        ValidationError: If code is invalid
    """
    if not isinstance(code, str):
        raise ValidationError("Station code must be a string")
    
    # Remove whitespace and convert to uppercase
    code = code.strip().upper()
    
    # Check length (typically 3-5 characters)
    if not (1 <= len(code) <= 10):
        raise ValidationError(f"Invalid station code length: {code}")
    
    # Check for valid characters (alphanumeric and some symbols)
    if not code.replace('*', '').replace('?', '').isalnum():
        raise ValidationError(f"Invalid characters in station code: {code}")
    
    return code
