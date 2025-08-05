# Advanced Analytics Module

This module provides advanced seismic analytics capabilities including real-time event detection, magnitude estimation, location determination, and confidence analysis.

## Features

### Real-time Event Detection
- Combined STA/LTA and deep learning approach
- Configurable detection parameters
- Real-time processing capabilities
- Event validation using machine learning

### Magnitude Estimation
- Traditional amplitude-based methods
- Machine learning enhanced estimation
- Confidence interval calculation
- Batch processing support

### Location Determination
- Multi-station triangulation
- P and S wave arrival time analysis
- ML-based location refinement
- Uncertainty quantification

### Confidence Analysis
- Bootstrap uncertainty estimation
- Statistical confidence bounds
- Visualization tools
- Comprehensive error analysis

### Alert System
- Real-time event notifications
- Configurable alert thresholds
- Rate-limited processing
- Async/await implementation

## Usage

See `notebooks/advanced_analytics_demo.ipynb` for detailed examples and usage.

Basic usage:

```python
from seismic_classifier.advanced_analytics import (
    RealTimeDetector,
    MagnitudeEstimator,
    LocationDeterminer,
    ConfidenceAnalyzer
)

# Initialize components
detector = RealTimeDetector()
magnitude_estimator = MagnitudeEstimator()
location_determiner = LocationDeterminer(station_coords=stations)
confidence_analyzer = ConfidenceAnalyzer()

# Process seismic data
events = await detector.process_stream(stream)
magnitudes = magnitude_estimator.batch_estimate(event_waveforms)
location = location_determiner.locate_event(arrival_times)
confidence = confidence_analyzer.analyze_detection_confidence(waveform, params)
```

## Requirements

See `requirements.txt` for complete dependencies. Key requirements:

- numpy
- scipy
- tensorflow
- obspy
- plotly
- asyncio-throttle
- aiohttp
