"""Signal Processing Module.

This module provides comprehensive signal processing capabilities for
seismic waveform data including filtering, detrending, and preprocessing.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import signal
from obspy import Stream, Trace

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SignalProcessor:
    """
    Comprehensive signal processing for seismic waveforms.
    
    This class provides methods for filtering, detrending, noise reduction,
    and other signal processing operations on seismic data.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize signal processor."""
        self.config = config or Config()
        logger.info("Signal processor initialized")
    
    def apply_bandpass_filter(
        self,
        data: Union[np.ndarray, Stream],
        freqmin: float,
        freqmax: float,
        sampling_rate: Optional[float] = None,
        corners: int = 4,
        filter_type: str = 'butter'
    ) -> Union[np.ndarray, Stream]:
        """
        Apply bandpass filter to data.
        
        Args:
            data: Input data (numpy array or ObsPy Stream)
            freqmin: Minimum frequency (Hz)
            freqmax: Maximum frequency (Hz)
            sampling_rate: Sampling rate (required for numpy arrays)
            corners: Filter order
            filter_type: Filter type ('butter', 'bessel', 'ellip')
            
        Returns:
            Filtered data in same format as input
        """
        if isinstance(data, Stream):
            filtered_stream = data.copy()
            for trace in filtered_stream:
                trace.filter(
                    'bandpass',
                    freqmin=freqmin,
                    freqmax=freqmax,
                    corners=corners
                )
            logger.info(f"Applied bandpass filter ({freqmin}-{freqmax} Hz) to stream")
            return filtered_stream
        
        elif isinstance(data, np.ndarray):
            if sampling_rate is None:
                raise ValueError("Sampling rate required for numpy array input")
            
            nyquist = sampling_rate / 2
            low = freqmin / nyquist
            high = freqmax / nyquist
            
            if filter_type == 'butter':
                b, a = signal.butter(corners, [low, high], btype='band')
            elif filter_type == 'bessel':
                b, a = signal.bessel(corners, [low, high], btype='band')
            elif filter_type == 'ellip':
                b, a = signal.ellip(corners, 1, 40, [low, high], btype='band')
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")
            
            filtered_data = signal.filtfilt(b, a, data)
            logger.info(f"Applied {filter_type} bandpass filter to array")
            return filtered_data
        
        else:
            raise TypeError("Data must be numpy array or ObsPy Stream")
    
    def remove_trend(
        self,
        data: Union[np.ndarray, Stream],
        method: str = 'linear'
    ) -> Union[np.ndarray, Stream]:
        """
        Remove trend from data.
        
        Args:
            data: Input data
            method: Detrending method ('linear', 'constant', 'polynomial')
            
        Returns:
            Detrended data
        """
        if isinstance(data, Stream):
            detrended_stream = data.copy()
            detrended_stream.detrend(type=method)
            logger.info(f"Applied {method} detrending to stream")
            return detrended_stream
        
        elif isinstance(data, np.ndarray):
            if method == 'linear':
                detrended = signal.detrend(data, type='linear')
            elif method == 'constant':
                detrended = signal.detrend(data, type='constant')
            elif method == 'polynomial':
                # Polynomial detrending (order 2)
                x = np.arange(len(data))
                p = np.polyfit(x, data, 2)
                trend = np.polyval(p, x)
                detrended = data - trend
            else:
                raise ValueError(f"Unknown detrending method: {method}")
            
            logger.info(f"Applied {method} detrending to array")
            return detrended
        
        else:
            raise TypeError("Data must be numpy array or ObsPy Stream")
    
    def apply_taper(
        self,
        data: Union[np.ndarray, Stream],
        taper_percentage: float = 0.05,
        taper_type: str = 'hann'
    ) -> Union[np.ndarray, Stream]:
        """
        Apply taper to data edges.
        
        Args:
            data: Input data
            taper_percentage: Percentage of data to taper (0.0 to 1.0)
            taper_type: Taper type ('hann', 'hamming', 'tukey')
            
        Returns:
            Tapered data
        """
        if isinstance(data, Stream):
            tapered_stream = data.copy()
            tapered_stream.taper(max_percentage=taper_percentage, type=taper_type)
            logger.info(f"Applied {taper_type} taper ({taper_percentage:.1%}) to stream")
            return tapered_stream
        
        elif isinstance(data, np.ndarray):
            taper_samples = int(len(data) * taper_percentage)
            
            if taper_type == 'hann':
                window = signal.hann(2 * taper_samples)
            elif taper_type == 'hamming':
                window = signal.hamming(2 * taper_samples)
            elif taper_type == 'tukey':
                window = signal.tukey(len(data), alpha=2 * taper_percentage)
                tapered_data = data * window
                logger.info(f"Applied {taper_type} taper to array")
                return tapered_data
            else:
                raise ValueError(f"Unknown taper type: {taper_type}")
            
            tapered_data = data.copy()
            # Apply taper to beginning and end
            tapered_data[:taper_samples] *= window[:taper_samples]
            tapered_data[-taper_samples:] *= window[taper_samples:]
            
            logger.info(f"Applied {taper_type} taper to array")
            return tapered_data
        
        else:
            raise TypeError("Data must be numpy array or ObsPy Stream")
    
    def calculate_snr(
        self,
        data: np.ndarray,
        noise_window: Tuple[int, int],
        signal_window: Tuple[int, int]
    ) -> float:
        """
        Calculate signal-to-noise ratio.
        
        Args:
            data: Input data array
            noise_window: (start, end) indices for noise estimation
            signal_window: (start, end) indices for signal
            
        Returns:
            SNR value in dB
        """
        noise_start, noise_end = noise_window
        signal_start, signal_end = signal_window
        
        # Calculate power in noise and signal windows
        noise_power = np.var(data[noise_start:noise_end])
        signal_power = np.var(data[signal_start:signal_end])
        
        if noise_power == 0:
            return float('inf')
        
        snr_linear = signal_power / noise_power
        snr_db = 10 * np.log10(snr_linear)
        
        logger.debug(f"Calculated SNR: {snr_db:.2f} dB")
        return snr_db
    
    def preprocess_waveform(
        self,
        stream: Stream,
        apply_filter: bool = True,
        apply_detrend: bool = True,
        apply_taper: bool = True,
        resample_rate: Optional[float] = None
    ) -> Stream:
        """
        Apply comprehensive preprocessing to waveform stream.
        
        Args:
            stream: Input ObsPy Stream
            apply_filter: Whether to apply bandpass filter
            apply_detrend: Whether to remove trend
            apply_taper: Whether to apply taper
            resample_rate: Target sampling rate for resampling
            
        Returns:
            Preprocessed Stream
        """
        processed_stream = stream.copy()
        
        logger.info(f"Starting preprocessing of {len(processed_stream)} traces")
        
        for trace in processed_stream:
            # Remove mean
            trace.detrend(type='constant')
            
            # Apply detrending
            if apply_detrend:
                trace.detrend(type=self.config.processing.detrend_type)
            
            # Apply taper
            if apply_taper:
                trace.taper(
                    max_percentage=self.config.processing.taper_percentage,
                    type='hann'
                )
            
            # Apply filter
            if apply_filter:
                trace.filter(
                    self.config.processing.filter_type,
                    freqmin=self.config.processing.filter_freqmin,
                    freqmax=self.config.processing.filter_freqmax,
                    corners=self.config.processing.filter_corners
                )
            
            # Resample if requested
            if resample_rate and abs(trace.stats.sampling_rate - resample_rate) > 0.1:
                trace.resample(resample_rate)
                logger.debug(f"Resampled {trace.id} to {resample_rate} Hz")
        
        logger.info("Preprocessing completed")
        return processed_stream


def calculate_spectral_features(
    data: np.ndarray,
    sampling_rate: float,
    nperseg: Optional[int] = None
) -> Dict[str, float]:
    """
    Calculate spectral features from waveform data.
    
    Args:
        data: Input waveform data
        sampling_rate: Sampling rate in Hz
        nperseg: Length of each segment for spectrogram
        
    Returns:
        Dictionary of spectral features
    """
    if nperseg is None:
        nperseg = min(256, len(data) // 4)
    
    # Calculate power spectral density
    freqs, psd = signal.welch(data, sampling_rate, nperseg=nperseg)
    
    # Calculate features
    features = {}
    
    # Dominant frequency
    dominant_freq_idx = np.argmax(psd)
    features['dominant_frequency'] = freqs[dominant_freq_idx]
    
    # Mean frequency
    features['mean_frequency'] = np.sum(freqs * psd) / np.sum(psd)
    
    # Spectral centroid
    features['spectral_centroid'] = np.sum(freqs * psd) / np.sum(psd)
    
    # Spectral bandwidth
    centroid = features['spectral_centroid']
    features['spectral_bandwidth'] = np.sqrt(
        np.sum(((freqs - centroid) ** 2) * psd) / np.sum(psd)
    )
    
    # Spectral rolloff (95% of energy)
    cumulative_energy = np.cumsum(psd)
    total_energy = cumulative_energy[-1]
    rolloff_idx = np.where(cumulative_energy >= 0.95 * total_energy)[0]
    if len(rolloff_idx) > 0:
        features['spectral_rolloff'] = freqs[rolloff_idx[0]]
    else:
        features['spectral_rolloff'] = freqs[-1]
    
    # Zero crossing rate (approximate from frequency domain)
    features['zero_crossing_rate'] = np.sum(np.diff(np.signbit(data))) / len(data)
    
    logger.debug(f"Calculated {len(features)} spectral features")
    return features


def calculate_time_domain_features(data: np.ndarray) -> Dict[str, float]:
    """
    Calculate time-domain features from waveform data.
    
    Args:
        data: Input waveform data
        
    Returns:
        Dictionary of time-domain features
    """
    features = {}
    
    # Basic statistics
    features['mean'] = np.mean(data)
    features['std'] = np.std(data)
    features['var'] = np.var(data)
    features['min'] = np.min(data)
    features['max'] = np.max(data)
    features['range'] = features['max'] - features['min']
    
    # Peak-to-peak amplitude
    features['peak_to_peak'] = np.ptp(data)
    
    # RMS (Root Mean Square)
    features['rms'] = np.sqrt(np.mean(data ** 2))
    
    # Energy
    features['energy'] = np.sum(data ** 2)
    
    # Higher order moments
    if features['std'] > 0:
        features['skewness'] = np.mean(((data - features['mean']) / features['std']) ** 3)
        features['kurtosis'] = np.mean(((data - features['mean']) / features['std']) ** 4)
    else:
        features['skewness'] = 0.0
        features['kurtosis'] = 0.0
    
    # Peak indices and values
    peaks, _ = signal.find_peaks(np.abs(data), height=features['std'])
    features['num_peaks'] = len(peaks)
    
    if len(peaks) > 0:
        features['max_peak_amplitude'] = np.max(np.abs(data[peaks]))
        features['mean_peak_amplitude'] = np.mean(np.abs(data[peaks]))
    else:
        features['max_peak_amplitude'] = 0.0
        features['mean_peak_amplitude'] = 0.0
    
    logger.debug(f"Calculated {len(features)} time-domain features")
    return features


def estimate_noise_level(
    data: np.ndarray,
    method: str = 'std',
    window_fraction: float = 0.1
) -> float:
    """
    Estimate noise level in waveform data.
    
    Args:
        data: Input waveform data
        method: Estimation method ('std', 'mad', 'percentile')
        window_fraction: Fraction of data to use for estimation
        
    Returns:
        Estimated noise level
    """
    # Use first portion of data for noise estimation
    window_size = int(len(data) * window_fraction)
    noise_window = data[:window_size]
    
    if method == 'std':
        noise_level = np.std(noise_window)
    elif method == 'mad':
        # Median Absolute Deviation
        median = np.median(noise_window)
        noise_level = np.median(np.abs(noise_window - median))
    elif method == 'percentile':
        # Use 90th percentile of absolute values
        noise_level = np.percentile(np.abs(noise_window), 90)
    else:
        raise ValueError(f"Unknown noise estimation method: {method}")
    
    logger.debug(f"Estimated noise level: {noise_level:.6f} using {method}")
    return noise_level
