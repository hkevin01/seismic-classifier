"""Real-time seismic event detection module using STA/LTA and deep learning approaches."""

import asyncio
from typing import Dict, List, Optional, Union

import numpy as np
from obspy import Stream
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
from tensorflow import keras


class RealTimeDetector:
    """Real-time seismic event detector using combined STA/LTA and deep learning approach."""

    def __init__(
        self,
        sta_length: float = 1.0,
        lta_length: float = 20.0,
        sta_lta_threshold: float = 3.0,
        trigger_off_threshold: float = 1.5,
        sampling_rate: float = 100.0,
        model_path: Optional[str] = None
    ):
        """
        Initialize the real-time detector.

        Args:
            sta_length: Short-term average window length in seconds
            lta_length: Long-term average window length in seconds
            sta_lta_threshold: STA/LTA ratio threshold for detection
            trigger_off_threshold: STA/LTA ratio threshold for ending detection
            sampling_rate: Sampling rate of the seismic data in Hz
            model_path: Optional path to a trained deep learning model
        """
        self.sta_length = int(sta_length * sampling_rate)
        self.lta_length = int(lta_length * sampling_rate)
        self.sta_lta_threshold = sta_lta_threshold
        self.trigger_off_threshold = trigger_off_threshold
        self.sampling_rate = sampling_rate

        # Load deep learning model if provided
        self.model = None
        if model_path:
            self.model = keras.models.load_model(model_path)

        # Initialize detection state
        self.is_detecting = False
        self.current_event = None
        self.detection_buffer = []

    async def process_stream(
        self,
        stream: Stream,
        window_size: float = 60.0,
        overlap: float = 10.0
    ) -> List[Dict[str, Union[float, str, bool]]]:
        """
        Process a continuous stream of seismic data for event detection.

        Args:
            stream: ObsPy Stream object containing seismic data
            window_size: Processing window size in seconds
            overlap: Overlap between consecutive windows in seconds

        Returns:
            List of detected events with their properties
        """
        events = []
        window_samples = int(window_size * self.sampling_rate)
        overlap_samples = int(overlap * self.sampling_rate)

        for trace in stream:
            data = trace.data
            for i in range(0, len(data) - window_samples, window_samples - overlap_samples):
                window = data[i:i+window_samples]

                # Perform STA/LTA detection
                sta_lta = recursive_sta_lta(
                    window,
                    self.sta_length,
                    self.lta_length
                )

                # Get trigger times
                triggers = trigger_onset(
                    sta_lta,
                    self.sta_lta_threshold,
                    self.trigger_off_threshold
                )

                # Process each trigger
                for trig_on, trig_off in triggers:
                    event = {
                        'start_time': trace.stats.starttime + i/self.sampling_rate + trig_on/self.sampling_rate,
                        'end_time': trace.stats.starttime + i/self.sampling_rate + trig_off/self.sampling_rate,
                        'max_sta_lta': float(max(sta_lta[trig_on:trig_off])),
                        'confidence': 0.0
                    }

                    # If deep learning model is available, validate the detection
                    if self.model:
                        event_window = window[trig_on:trig_off]
                        if len(event_window) > 0:
                            # Preprocess for model
                            processed_window = self._preprocess_for_model(event_window)

                            # Get model prediction
                            confidence = float(self.model.predict(processed_window)[0])
                            event['confidence'] = confidence

                            # Only keep events with high confidence
                            if confidence > 0.8:
                                events.append(event)
                    else:
                        events.append(event)

                await asyncio.sleep(0)  # Allow other tasks to run

        return events

    def _preprocess_for_model(self, data: np.ndarray) -> np.ndarray:
        """
        Preprocess seismic data for the deep learning model.

        Args:
            data: Raw seismic data array

        Returns:
            Preprocessed data ready for model input
        """
        # Normalize
        data = (data - np.mean(data)) / (np.std(data) + 1e-8)

        # Reshape for model input (assuming CNN model)
        data = data.reshape(1, -1, 1)

        return data

    async def start_realtime_detection(
        self,
        callback: callable,
        buffer_size: int = 1000
    ):
        """
        Start real-time detection on streaming data.

        Args:
            callback: Function to call when an event is detected
            buffer_size: Size of the detection buffer in samples
        """
        self.is_detecting = True
        self.detection_buffer = []

        while self.is_detecting:
            if len(self.detection_buffer) >= buffer_size:
                data = np.array(self.detection_buffer[-buffer_size:])

                # Perform STA/LTA detection
                sta_lta = recursive_sta_lta(
                    data,
                    self.sta_length,
                    self.lta_length
                )

                # Check for triggers
                triggers = trigger_onset(
                    sta_lta,
                    self.sta_lta_threshold,
                    self.trigger_off_threshold
                )

                if len(triggers) > 0:
                    # Process the latest trigger
                    trig_on, trig_off = triggers[-1]
                    event_data = data[trig_on:trig_off]

                    event = {
                        'timestamp': trig_on / self.sampling_rate,
                        'duration': (trig_off - trig_on) / self.sampling_rate,
                        'max_sta_lta': float(max(sta_lta[trig_on:trig_off])),
                        'waveform': event_data.copy()
                    }

                    # Deep learning validation if model is available
                    if self.model and len(event_data) > 0:
                        processed_data = self._preprocess_for_model(event_data)
                        confidence = float(self.model.predict(processed_data)[0])
                        event['confidence'] = confidence

                        if confidence > 0.8:
                            await callback(event)
                    else:
                        await callback(event)

                # Remove old data
                self.detection_buffer = self.detection_buffer[-buffer_size:]

            await asyncio.sleep(0.01)  # Small delay to prevent CPU overload

    def stop_realtime_detection(self):
        """Stop real-time detection."""
        self.is_detecting = False

    async def add_samples(self, samples: Union[List[float], np.ndarray]):
        """
        Add new samples to the detection buffer.

        Args:
            samples: List or array of new samples to add
        """
        self.detection_buffer.extend(samples)
        """
        self.detection_buffer.extend(samples)
