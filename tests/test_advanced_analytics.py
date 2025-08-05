"""Tests for advanced analytics module."""

import asyncio

import numpy as np
import pytest
from obspy import Stream, Trace

from ..advanced_analytics.confidence_analysis import ConfidenceAnalyzer
from ..advanced_analytics.event_detection import RealTimeDetector
from ..advanced_analytics.location_determination import LocationDeterminer
from ..advanced_analytics.magnitude_estimation import MagnitudeEstimator


@pytest.fixture
def sample_waveform():
    """Create a sample waveform for testing."""
    # Create synthetic waveform with P and S arrivals
    t = np.linspace(0, 60, 6000)  # 60 seconds at 100 Hz
    p_arrival = np.exp(-((t - 20) ** 2))  # P wave at 20s
    s_arrival = 2 * np.exp(-((t - 25) ** 2))  # S wave at 25s
    noise = 0.1 * np.random.randn(len(t))
    waveform = p_arrival + s_arrival + noise
    return waveform


@pytest.fixture
def sample_stream(sample_waveform):
    """Create a sample ObsPy Stream for testing."""
    trace = Trace(data=sample_waveform)
    trace.stats.sampling_rate = 100
    return Stream([trace])


@pytest.fixture
def detector():
    """Create a RealTimeDetector instance."""
    return RealTimeDetector(sta_length=1.0, lta_length=20.0, sta_lta_threshold=3.0)


@pytest.fixture
def magnitude_estimator():
    """Create a MagnitudeEstimator instance."""
    return MagnitudeEstimator(sampling_rate=100.0, window_size=60.0)


@pytest.fixture
def location_determiner():
    """Create a LocationDeterminer instance."""
    station_coords = {
        "STA1": (0.0, 0.0, 0.0),
        "STA2": (1.0, 0.0, 0.0),
        "STA3": (0.0, 1.0, 0.0),
    }
    return LocationDeterminer(station_coords=station_coords)


@pytest.fixture
def confidence_analyzer():
    """Create a ConfidenceAnalyzer instance."""
    return ConfidenceAnalyzer(bootstrap_iterations=100, confidence_level=0.95)


class TestRealTimeDetector:
    """Test cases for RealTimeDetector class."""

    @pytest.mark.asyncio
    async def test_process_stream(self, detector, sample_stream):
        """Test processing a seismic stream."""
        events = await detector.process_stream(sample_stream)
        assert len(events) > 0

        # Check event properties
        event = events[0]
        assert "start_time" in event
        assert "end_time" in event
        assert "max_sta_lta" in event

    @pytest.mark.asyncio
    async def test_realtime_detection(self, detector, sample_waveform):
        """Test real-time detection functionality."""
        detected_events = []

        async def callback(event):
            detected_events.append(event)

        # Start detection in background
        detection_task = asyncio.create_task(
            detector.start_realtime_detection(callback)
        )

        # Add samples in chunks
        chunk_size = 100
        for i in range(0, len(sample_waveform), chunk_size):
            chunk = sample_waveform[i : i + chunk_size]
            await detector.add_samples(chunk)
            await asyncio.sleep(0.1)

        # Stop detection
        detector.stop_realtime_detection()
        await detection_task

        assert len(detected_events) > 0


class TestMagnitudeEstimator:
    """Test cases for MagnitudeEstimator class."""

    def test_estimate_magnitude(self, magnitude_estimator, sample_waveform):
        """Test magnitude estimation."""
        result = magnitude_estimator.estimate_magnitude(sample_waveform)

        assert "magnitude" in result
        assert "confidence" in result
        assert isinstance(result["magnitude"], float)
        assert 0 <= result["confidence"] <= 1

    def test_batch_estimate(self, magnitude_estimator, sample_waveform):
        """Test batch magnitude estimation."""
        waveforms = [sample_waveform] * 3
        results = magnitude_estimator.batch_estimate(waveforms)

        assert len(results) == 3
        for result in results:
            assert "magnitude" in result
            assert "confidence" in result


class TestLocationDeterminer:
    """Test cases for LocationDeterminer class."""

    def test_locate_event(self, location_determiner):
        """Test event location determination."""
        picks = {
            "STA1": {"P": 0.0, "S": 0.5},
            "STA2": {"P": 0.2, "S": 0.7},
            "STA3": {"P": 0.3, "S": 0.8},
        }

        result = location_determiner.locate_event(picks)

        assert "latitude" in result
        assert "longitude" in result
        assert "depth" in result
        assert "uncertainty" in result
        assert "confidence" in result

    def test_invalid_picks(self, location_determiner):
        """Test location determination with invalid picks."""
        with pytest.raises(ValueError):
            location_determiner.locate_event({})


class TestConfidenceAnalyzer:
    """Test cases for ConfidenceAnalyzer class."""

    def test_detection_confidence(self, confidence_analyzer, sample_waveform):
        """Test detection confidence analysis."""
        detection_params = {"sta_lta": 5.0, "snr": 10.0}

        result = confidence_analyzer.analyze_detection_confidence(
            sample_waveform, detection_params
        )

        assert "confidence_intervals" in result
        assert "overall_confidence" in result

    def test_magnitude_confidence(self, confidence_analyzer, sample_waveform):
        """Test magnitude confidence analysis."""
        result = confidence_analyzer.analyze_magnitude_confidence(
            magnitude=3.0, waveform=sample_waveform, noise_level=0.1
        )

        assert "confidence_interval" in result
        assert "uncertainty" in result
        assert "confidence" in result

    def test_location_confidence(self, confidence_analyzer):
        """Test location confidence analysis."""
        location = {"latitude": 0.5, "longitude": 0.5, "depth": 10.0}
        arrival_times = {"STA1": {"P": 0.0, "S": 0.5}, "STA2": {"P": 0.2, "S": 0.7}}
        velocity_model = {"P": 6.0, "S": 3.5}

        result = confidence_analyzer.analyze_location_confidence(
            location, arrival_times, velocity_model
        )

        assert "confidence_intervals" in result
        assert "uncertainties" in result
        assert "confidence" in result
        assert "confidence_intervals" in result
        assert "uncertainties" in result
        assert "confidence" in result
