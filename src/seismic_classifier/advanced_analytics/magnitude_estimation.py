"""Seismic magnitude estimation module using machine learning and waveform analysis."""

from typing import Dict, List, Optional, Union

import numpy as np
from obspy import Stream, Trace
from scipy.signal import welch
from tensorflow import keras


class MagnitudeEstimator:
    """Estimate earthquake magnitude using ML and waveform characteristics."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        sampling_rate: float = 100.0,
        window_size: float = 60.0,
        min_freq: float = 0.1,
        max_freq: float = 25.0
    ):
        """
        Initialize the magnitude estimator.

        Args:
            model_path: Path to trained magnitude estimation model
            sampling_rate: Sampling rate of the seismic data in Hz
            window_size: Analysis window size in seconds
            min_freq: Minimum frequency for spectral analysis
            max_freq: Maximum frequency for spectral analysis
        """
        self.sampling_rate = sampling_rate
        self.window_size = int(window_size * sampling_rate)
        self.min_freq = min_freq
        self.max_freq = max_freq

        # Load ML model if provided
        self.model = None
        if model_path:
            self.model = keras.models.load_model(model_path)

    def estimate_magnitude(
        self,
        waveform: Union[np.ndarray, Stream, Trace],
        **kwargs
    ) -> Dict[str, float]:
        """
        Estimate earthquake magnitude from waveform data.

        Args:
            waveform: Seismic waveform data
            **kwargs: Additional parameters for estimation

        Returns:
            Dictionary containing magnitude estimate and confidence
        """
        # Convert input to numpy array
        if isinstance(waveform, (Stream, Trace)):
            data = waveform.data
        else:
            data = waveform

        # Calculate waveform features
        features = self._extract_features(data)

        # Initial magnitude estimate from signal characteristics
        traditional_estimate = self._estimate_from_amplitude(data)

        result = {
            'magnitude': traditional_estimate,
            'confidence': 0.8,  # Default confidence
            'uncertainty': 0.5  # Default uncertainty
        }

        # Refine estimate with ML model if available
        if self.model:
            # Preprocess features for model
            model_input = self._preprocess_for_model(features)

            # Get model prediction and uncertainty
            prediction = self.model.predict(model_input)

            if isinstance(prediction, (list, tuple)):
                # Model outputs both magnitude and uncertainty
                ml_magnitude = float(prediction[0])
                uncertainty = float(prediction[1])
            else:
                # Model outputs only magnitude
                ml_magnitude = float(prediction)
                uncertainty = 0.3  # Default uncertainty for ML estimate

            # Combine traditional and ML estimates
            combined_magnitude = (traditional_estimate + ml_magnitude) / 2

            result.update({
                'magnitude': combined_magnitude,
                'ml_magnitude': ml_magnitude,
                'traditional_magnitude': traditional_estimate,
                'uncertainty': uncertainty,
                'confidence': 0.9  # Higher confidence with ML
            })

        return result

    def _extract_features(self, data: np.ndarray) -> Dict[str, float]:
        """
        Extract relevant features from waveform for magnitude estimation.

        Args:
            data: Seismic waveform data

        Returns:
            Dictionary of extracted features
        """
        # Calculate basic statistics
        max_amp = np.max(np.abs(data))
        rms_amp = np.sqrt(np.mean(np.square(data)))

        # Calculate spectral features
        freqs, psd = welch(
            data,
            fs=self.sampling_rate,
            nperseg=min(len(data), self.window_size)
        )

        # Get relevant frequency band
        mask = (freqs >= self.min_freq) & (freqs <= self.max_freq)
        peak_freq = freqs[mask][np.argmax(psd[mask])]
        total_energy = np.sum(psd[mask])

        return {
            'max_amplitude': max_amp,
            'rms_amplitude': rms_amp,
            'peak_frequency': peak_freq,
            'total_energy': total_energy,
            'duration': len(data) / self.sampling_rate
        }

    def _estimate_from_amplitude(self, data: np.ndarray) -> float:
        """
        Estimate magnitude using traditional amplitude-based method.

        Args:
            data: Seismic waveform data

        Returns:
            Estimated magnitude
        """
        # Simple magnitude estimation based on log of max amplitude
        max_amp = np.max(np.abs(data))
        return np.log10(max_amp) + 1.0  # Basic magnitude scale

    def _preprocess_for_model(self, features: Dict[str, float]) -> np.ndarray:
        """
        Preprocess features for ML model input.

        Args:
            features: Dictionary of extracted features

        Returns:
            Array of preprocessed features ready for model input
        """
        # Convert features to array in expected order
        feature_array = np.array([
            features['max_amplitude'],
            features['rms_amplitude'],
            features['peak_frequency'],
            features['total_energy'],
            features['duration']
        ]).reshape(1, -1)

        return feature_array

    def batch_estimate(
        self,
        waveforms: List[Union[np.ndarray, Stream, Trace]],
        **kwargs
    ) -> List[Dict[str, float]]:
        """
        Estimate magnitudes for multiple waveforms.

        Args:
            waveforms: List of seismic waveforms
            **kwargs: Additional parameters for estimation

        Returns:
            List of dictionaries containing magnitude estimates and confidence
        """
        return [self.estimate_magnitude(w, **kwargs) for w in waveforms]
        """
        return [self.estimate_magnitude(w, **kwargs) for w in waveforms]
