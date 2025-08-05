"""Feature Extraction Module.

This module provides comprehensive feature extraction capabilities for
seismic waveform classification including time-domain, frequency-domain,
and wavelet-based features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from scipy import signal, stats
from scipy.fft import fft, fftfreq
import pywt
from obspy import Stream, Trace

from ..config.settings import Config
from ..utils.logger import get_logger
from .signal_processing import (
    calculate_spectral_features,
    calculate_time_domain_features,
    estimate_noise_level
)

logger = get_logger(__name__)


class FeatureExtractor:
    """
    Comprehensive feature extraction for seismic waveform classification.
    
    This class extracts time-domain, frequency-domain, and wavelet features
    from seismic waveforms for machine learning applications.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize feature extractor."""
        self.config = config or Config()
        self.feature_names = []
        logger.info("Feature extractor initialized")
    
    def extract_all_features(
        self,
        stream: Stream,
        window_length: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Extract comprehensive feature set from waveform stream.
        
        Args:
            stream: Input ObsPy Stream
            window_length: Window length in seconds for analysis
            
        Returns:
            DataFrame with extracted features
        """
        features_list = []
        
        for i, trace in enumerate(stream):
            logger.debug(f"Extracting features from trace {i+1}/{len(stream)}")
            
            # Get waveform data
            data = trace.data
            sampling_rate = trace.stats.sampling_rate
            
            # Apply windowing if specified
            if window_length:
                window_samples = int(window_length * sampling_rate)
                if len(data) > window_samples:
                    # Use central window
                    start_idx = (len(data) - window_samples) // 2
                    data = data[start_idx:start_idx + window_samples]
            
            # Extract different feature groups
            trace_features = {}
            
            # Basic metadata
            trace_features.update(self._extract_metadata_features(trace))
            
            # Time-domain features
            trace_features.update(
                self._extract_time_domain_features(data, sampling_rate)
            )
            
            # Frequency-domain features
            trace_features.update(
                self._extract_frequency_domain_features(data, sampling_rate)
            )
            
            # Wavelet features
            trace_features.update(
                self._extract_wavelet_features(data, sampling_rate)
            )
            
            # Statistical features
            trace_features.update(
                self._extract_statistical_features(data)
            )
            
            # Add trace identifier
            trace_features['trace_id'] = trace.id
            trace_features['trace_index'] = i
            
            features_list.append(trace_features)
        
        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        
        logger.info(f"Extracted {len(features_df.columns)} features from "
                   f"{len(features_df)} traces")
        
        return features_df
    
    def _extract_metadata_features(self, trace: Trace) -> Dict[str, float]:
        """Extract metadata-based features."""
        features = {}
        
        # Sampling parameters
        features['sampling_rate'] = float(trace.stats.sampling_rate)
        features['npts'] = float(trace.stats.npts)
        features['duration'] = float(trace.stats.npts / trace.stats.sampling_rate)
        
        # Station information (if available)
        if hasattr(trace.stats, 'distance'):
            features['distance'] = float(trace.stats.distance)
        
        if hasattr(trace.stats, 'back_azimuth'):
            features['back_azimuth'] = float(trace.stats.back_azimuth)
        
        return features
    
    def _extract_time_domain_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract comprehensive time-domain features."""
        features = {}
        
        # Basic statistical features
        basic_features = calculate_time_domain_features(data)
        features.update({f'td_{k}': v for k, v in basic_features.items()})
        
        # Arrival time features
        arrival_features = self._extract_arrival_features(data, sampling_rate)
        features.update(arrival_features)
        
        # Envelope features
        envelope_features = self._extract_envelope_features(data)
        features.update(envelope_features)
        
        # Autocorrelation features
        autocorr_features = self._extract_autocorrelation_features(data)
        features.update(autocorr_features)
        
        return features
    
    def _extract_frequency_domain_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract frequency-domain features."""
        features = {}
        
        # Basic spectral features
        spectral_features = calculate_spectral_features(data, sampling_rate)
        features.update({f'fd_{k}': v for k, v in spectral_features.items()})
        
        # FFT-based features
        fft_features = self._extract_fft_features(data, sampling_rate)
        features.update(fft_features)
        
        # Spectrogram features
        spectrogram_features = self._extract_spectrogram_features(
            data, sampling_rate
        )
        features.update(spectrogram_features)
        
        return features
    
    def _extract_wavelet_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract wavelet-based features."""
        features = {}
        
        # Continuous Wavelet Transform features
        cwt_features = self._extract_cwt_features(data, sampling_rate)
        features.update(cwt_features)
        
        # Discrete Wavelet Transform features
        dwt_features = self._extract_dwt_features(data)
        features.update(dwt_features)
        
        return features
    
    def _extract_statistical_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract advanced statistical features."""
        features = {}
        
        # Higher-order moments
        features['stat_skewness'] = float(stats.skew(data))
        features['stat_kurtosis'] = float(stats.kurtosis(data))
        
        # Entropy measures
        features['stat_entropy'] = self._calculate_entropy(data)
        
        # Percentile features
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        for p in percentiles:
            features[f'stat_percentile_{p}'] = float(np.percentile(data, p))
        
        # Distribution tests
        features['stat_normality_pvalue'] = float(stats.normaltest(data)[1])
        
        return features
    
    def _extract_arrival_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract P-wave and S-wave arrival features."""
        features = {}
        
        # STA/LTA ratio for arrival detection
        sta_window = int(1.0 * sampling_rate)  # 1 second
        lta_window = int(10.0 * sampling_rate)  # 10 seconds
        
        if len(data) > lta_window:
            sta_lta = self._calculate_sta_lta(data, sta_window, lta_window)
            
            # Find potential arrivals
            threshold = 3.0
            arrival_indices = np.where(sta_lta > threshold)[0]
            
            if len(arrival_indices) > 0:
                features['arrival_time'] = float(arrival_indices[0] / sampling_rate)
                features['max_sta_lta'] = float(np.max(sta_lta))
                features['num_arrivals'] = float(len(arrival_indices))
            else:
                features['arrival_time'] = 0.0
                features['max_sta_lta'] = float(np.max(sta_lta))
                features['num_arrivals'] = 0.0
        
        return features
    
    def _extract_envelope_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract envelope-based features."""
        features = {}
        
        # Calculate envelope using Hilbert transform
        analytic_signal = signal.hilbert(data)
        envelope = np.abs(analytic_signal)
        
        # Envelope statistics
        features['env_mean'] = float(np.mean(envelope))
        features['env_std'] = float(np.std(envelope))
        features['env_max'] = float(np.max(envelope))
        features['env_skewness'] = float(stats.skew(envelope))
        
        # Envelope shape features
        envelope_norm = envelope / np.max(envelope)
        features['env_rise_time'] = self._calculate_rise_time(envelope_norm)
        features['env_decay_time'] = self._calculate_decay_time(envelope_norm)
        
        return features
    
    def _extract_autocorrelation_features(
        self,
        data: np.ndarray
    ) -> Dict[str, float]:
        """Extract autocorrelation-based features."""
        features = {}
        
        # Calculate autocorrelation
        autocorr = np.correlate(data, data, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        autocorr = autocorr / autocorr[0]  # Normalize
        
        # Find first zero crossing
        zero_crossings = np.where(np.diff(np.sign(autocorr)))[0]
        if len(zero_crossings) > 0:
            features['autocorr_first_zero'] = float(zero_crossings[0])
        else:
            features['autocorr_first_zero'] = float(len(autocorr))
        
        # Autocorrelation decay rate
        if len(autocorr) > 10:
            features['autocorr_decay'] = float(np.mean(autocorr[1:11]))
        
        return features
    
    def _extract_fft_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract FFT-based features."""
        features = {}
        
        # Calculate FFT
        fft_vals = fft(data)
        freqs = fftfreq(len(data), 1/sampling_rate)
        
        # Use only positive frequencies
        positive_freq_idx = freqs > 0
        freqs = freqs[positive_freq_idx]
        fft_magnitude = np.abs(fft_vals[positive_freq_idx])
        
        # Frequency band power
        bands = {
            'very_low': (0.1, 1.0),
            'low': (1.0, 5.0),
            'mid': (5.0, 15.0),
            'high': (15.0, 50.0)
        }
        
        for band_name, (f_min, f_max) in bands.items():
            band_mask = (freqs >= f_min) & (freqs <= f_max)
            if np.any(band_mask):
                band_power = np.sum(fft_magnitude[band_mask] ** 2)
                features[f'fft_power_{band_name}'] = float(band_power)
            else:
                features[f'fft_power_{band_name}'] = 0.0
        
        # Frequency ratios
        total_power = np.sum(fft_magnitude ** 2)
        if total_power > 0:
            for band_name in bands.keys():
                power_key = f'fft_power_{band_name}'
                if power_key in features:
                    ratio_key = f'fft_ratio_{band_name}'
                    features[ratio_key] = features[power_key] / total_power
        
        return features
    
    def _extract_spectrogram_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract spectrogram-based features."""
        features = {}
        
        # Calculate spectrogram
        nperseg = min(256, len(data) // 4)
        freqs, times, Sxx = signal.spectrogram(
            data, sampling_rate, nperseg=nperseg
        )
        
        # Time-frequency features
        features['spec_bandwidth_mean'] = float(np.mean(np.std(Sxx, axis=0)))
        features['spec_centroid_std'] = float(np.std(np.mean(Sxx, axis=0)))
        features['spec_rolloff_mean'] = float(np.mean(np.max(Sxx, axis=0)))
        
        # Spectral flux (measure of spectral change)
        if Sxx.shape[1] > 1:
            spectral_flux = np.mean(np.diff(Sxx, axis=1) ** 2)
            features['spec_flux'] = float(spectral_flux)
        
        return features
    
    def _extract_cwt_features(
        self,
        data: np.ndarray,
        sampling_rate: float
    ) -> Dict[str, float]:
        """Extract Continuous Wavelet Transform features."""
        features = {}
        
        # Define scales for analysis
        scales = np.arange(1, 32)
        
        # Perform CWT with Morlet wavelet
        coefficients, freqs = pywt.cwt(data, scales, 'morl')
        
        # Energy at different scales
        energy_per_scale = np.mean(np.abs(coefficients) ** 2, axis=1)
        
        features['cwt_energy_low'] = float(np.mean(energy_per_scale[:8]))
        features['cwt_energy_mid'] = float(np.mean(energy_per_scale[8:16]))
        features['cwt_energy_high'] = float(np.mean(energy_per_scale[16:]))
        
        # Dominant scale
        dominant_scale_idx = np.argmax(energy_per_scale)
        features['cwt_dominant_scale'] = float(scales[dominant_scale_idx])
        
        return features
    
    def _extract_dwt_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract Discrete Wavelet Transform features."""
        features = {}
        
        # Perform multi-level DWT
        wavelet = 'db4'
        max_level = min(5, pywt.dwt_max_level(len(data), wavelet))
        
        coeffs = pywt.wavedec(data, wavelet, level=max_level)
        
        # Energy and statistics for each level
        for i, coeff in enumerate(coeffs):
            level_name = 'approx' if i == 0 else f'detail_{i}'
            
            features[f'dwt_{level_name}_energy'] = float(np.sum(coeff ** 2))
            features[f'dwt_{level_name}_std'] = float(np.std(coeff))
            features[f'dwt_{level_name}_mean'] = float(np.mean(coeff))
            
            if len(coeff) > 0:
                features[f'dwt_{level_name}_max'] = float(np.max(np.abs(coeff)))
        
        return features
    
    def _calculate_sta_lta(
        self,
        data: np.ndarray,
        sta_window: int,
        lta_window: int
    ) -> np.ndarray:
        """Calculate STA/LTA ratio for arrival detection."""
        sta_lta = np.zeros(len(data))
        
        for i in range(lta_window, len(data)):
            # Short-term average
            sta = np.mean(data[i-sta_window:i] ** 2)
            
            # Long-term average
            lta = np.mean(data[i-lta_window:i] ** 2)
            
            if lta > 0:
                sta_lta[i] = sta / lta
        
        return sta_lta
    
    def _calculate_rise_time(self, envelope: np.ndarray) -> float:
        """Calculate envelope rise time."""
        max_idx = np.argmax(envelope)
        
        # Find 10% and 90% of maximum
        threshold_10 = 0.1
        threshold_90 = 0.9
        
        idx_10 = np.where(envelope[:max_idx] >= threshold_10)[0]
        idx_90 = np.where(envelope[:max_idx] >= threshold_90)[0]
        
        if len(idx_10) > 0 and len(idx_90) > 0:
            return float(idx_90[0] - idx_10[0])
        else:
            return 0.0
    
    def _calculate_decay_time(self, envelope: np.ndarray) -> float:
        """Calculate envelope decay time."""
        max_idx = np.argmax(envelope)
        
        if max_idx >= len(envelope) - 1:
            return 0.0
        
        # Find 90% and 10% of maximum after peak
        threshold_90 = 0.9
        threshold_10 = 0.1
        
        post_peak = envelope[max_idx:]
        idx_90 = np.where(post_peak <= threshold_90)[0]
        idx_10 = np.where(post_peak <= threshold_10)[0]
        
        if len(idx_90) > 0 and len(idx_10) > 0:
            return float(idx_10[0] - idx_90[0])
        else:
            return float(len(post_peak))
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of the signal."""
        # Bin the data
        hist, _ = np.histogram(data, bins=50, density=True)
        hist = hist[hist > 0]  # Remove zero bins
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        return float(entropy)


def extract_features_from_stream(
    stream: Stream,
    feature_config: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Convenience function to extract features from a stream.
    
    Args:
        stream: Input ObsPy Stream
        feature_config: Configuration for feature extraction
        
    Returns:
        DataFrame with extracted features
    """
    extractor = FeatureExtractor()
    
    if feature_config:
        # Apply any custom configuration
        for key, value in feature_config.items():
            if hasattr(extractor.config.feature_extraction, key):
                setattr(extractor.config.feature_extraction, key, value)
    
    return extractor.extract_all_features(stream)
