"""Confidence interval analysis for seismic event parameters."""

from typing import Dict, List, Optional, Union

import numpy as np
import plotly.graph_objects as go
import tensorflow as tf


class ConfidenceAnalyzer:
    """Analyze and quantify confidence in seismic event parameters."""

    def __init__(
        self,
        confidence_model_path: Optional[str] = None,
        bootstrap_iterations: int = 1000,
        confidence_level: float = 0.95,
    ):
        """
        Initialize the confidence analyzer.

        Args:
            confidence_model_path: Optional path to ML confidence model
            bootstrap_iterations: Number of bootstrap iterations
            confidence_level: Confidence level (e.g., 0.95 for 95%)
        """
        self.bootstrap_iterations = bootstrap_iterations
        self.confidence_level = confidence_level

        # Load confidence model if provided
        self.model = None
        if confidence_model_path:
            self.model = tf.keras.models.load_model(confidence_model_path)

    def analyze_detection_confidence(
        self, waveform: np.ndarray, detection_params: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Analyze confidence in event detection.

        Args:
            waveform: Seismic waveform data
            detection_params: Parameters from detection algorithm

        Returns:
            Dictionary of confidence metrics
        """
        # Bootstrap analysis of detection parameters
        bootstrap_stats = self._bootstrap_detection(waveform, detection_params)

        # Calculate confidence intervals
        confidence_intervals = {
            param: self._calculate_confidence_interval(values)
            for param, values in bootstrap_stats.items()
        }

        # Get ML-based confidence if model available
        ml_confidence = None
        if self.model:
            features = self._extract_confidence_features(waveform, detection_params)
            ml_confidence = float(self.model.predict(features)[0])

        return {
            "confidence_intervals": confidence_intervals,
            "ml_confidence": ml_confidence,
            "overall_confidence": self._combine_confidence_metrics(
                confidence_intervals, ml_confidence
            ),
        }

    def analyze_magnitude_confidence(
        self,
        magnitude: float,
        waveform: np.ndarray,
        noise_level: Optional[float] = None,
    ) -> Dict[str, Union[float, tuple]]:
        """
        Analyze confidence in magnitude estimation.

        Args:
            magnitude: Estimated magnitude
            waveform: Seismic waveform data
            noise_level: Optional background noise level

        Returns:
            Dictionary of confidence metrics
        """
        # Bootstrap analysis of magnitude estimation
        magnitude_samples = self._bootstrap_magnitude(waveform, magnitude, noise_level)

        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(magnitude_samples)

        # Estimate uncertainty
        uncertainty = np.std(magnitude_samples)

        # Calculate signal-to-noise ratio if noise level provided
        snr = None
        if noise_level:
            signal_power = np.mean(np.square(waveform))
            snr = 10 * np.log10(signal_power / (noise_level**2))

        return {
            "confidence_interval": confidence_interval,
            "uncertainty": uncertainty,
            "snr": snr,
            "confidence": 1.0 - (uncertainty / abs(magnitude)),
        }

    def analyze_location_confidence(
        self,
        location: Dict[str, float],
        arrival_times: Dict[str, Dict[str, float]],
        velocity_model: Dict[str, float],
    ) -> Dict[str, Union[float, Dict[str, tuple]]]:
        """
        Analyze confidence in location determination.

        Args:
            location: Estimated location parameters
            arrival_times: P and S wave arrival times
            velocity_model: Seismic velocity model

        Returns:
            Dictionary of confidence metrics
        """
        # Bootstrap analysis of location parameters
        location_samples = self._bootstrap_location(
            location, arrival_times, velocity_model
        )

        # Calculate confidence intervals for each parameter
        confidence_intervals = {}
        uncertainties = {}

        for param in ["latitude", "longitude", "depth"]:
            samples = [loc[param] for loc in location_samples]
            confidence_intervals[param] = self._calculate_confidence_interval(samples)
            uncertainties[param] = np.std(samples)

        # Calculate overall confidence metric
        average_uncertainty = np.mean(list(uncertainties.values()))
        max_uncertainty = np.max(list(uncertainties.values()))

        return {
            "confidence_intervals": confidence_intervals,
            "uncertainties": uncertainties,
            "average_uncertainty": average_uncertainty,
            "max_uncertainty": max_uncertainty,
            "confidence": 1.0 - (average_uncertainty / max_uncertainty),
        }

    def _bootstrap_detection(
        self, waveform: np.ndarray, detection_params: Dict[str, float]
    ) -> Dict[str, List[float]]:
        """
        Perform bootstrap analysis of detection parameters.

        Args:
            waveform: Seismic waveform data
            detection_params: Detection parameters

        Returns:
            Dictionary of bootstrapped parameter values
        """
        bootstrap_stats = {param: [] for param in detection_params}

        for _ in range(self.bootstrap_iterations):
            # Resample waveform with replacement
            indices = np.random.choice(len(waveform), size=len(waveform), replace=True)
            resampled = waveform[indices]

            # Recalculate detection parameters
            for param in detection_params:
                if param == "sta_lta":
                    # Recalculate STA/LTA
                    bootstrap_stats[param].append(
                        np.max(np.abs(resampled)) / np.mean(np.abs(resampled))
                    )
                else:
                    # Add other parameter calculations as needed
                    bootstrap_stats[param].append(detection_params[param])

        return bootstrap_stats

    def _bootstrap_magnitude(
        self, waveform: np.ndarray, magnitude: float, noise_level: Optional[float]
    ) -> List[float]:
        """
        Perform bootstrap analysis of magnitude estimation.

        Args:
            waveform: Seismic waveform data
            magnitude: Original magnitude estimate
            noise_level: Optional noise level

        Returns:
            List of bootstrap magnitude estimates
        """
        magnitude_samples = []

        for _ in range(self.bootstrap_iterations):
            # Resample waveform with replacement
            indices = np.random.choice(len(waveform), size=len(waveform), replace=True)
            resampled = waveform[indices]

            # Add noise if noise level provided
            if noise_level:
                noise = np.random.normal(0, noise_level, size=len(resampled))
                resampled += noise

            # Simple magnitude estimation based on max amplitude
            max_amp = np.max(np.abs(resampled))
            mag_sample = np.log10(max_amp) + 1.0

            magnitude_samples.append(mag_sample)

        return magnitude_samples

    def _bootstrap_location(
        self,
        location: Dict[str, float],
        arrival_times: Dict[str, Dict[str, float]],
        velocity_model: Dict[str, float],
    ) -> List[Dict[str, float]]:
        """
        Perform bootstrap analysis of location determination.

        Args:
            location: Original location estimate
            arrival_times: P and S wave arrival times
            velocity_model: Seismic velocity model

        Returns:
            List of bootstrap location estimates
        """
        location_samples = []

        for _ in range(self.bootstrap_iterations):
            # Resample arrival times with noise
            resampled_times = {}
            for station, phases in arrival_times.items():
                resampled_times[station] = {}
                for phase, time in phases.items():
                    # Add random timing error
                    error = np.random.normal(0, 0.1)  # 0.1s standard deviation
                    resampled_times[station][phase] = time + error

            # Simple location estimate using timing differences
            # This is a placeholder - actual implementation would be more complex
            sample = {
                "latitude": location["latitude"] + np.random.normal(0, 0.1),
                "longitude": location["longitude"] + np.random.normal(0, 0.1),
                "depth": location["depth"] + np.random.normal(0, 1.0),
            }

            location_samples.append(sample)

        return location_samples

    def _calculate_confidence_interval(
        self, samples: List[float]
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval from bootstrap samples.

        Args:
            samples: List of bootstrap samples

        Returns:
            Tuple of (lower bound, upper bound)
        """
        alpha = 1 - self.confidence_level
        lower = np.percentile(samples, alpha * 100 / 2)
        upper = np.percentile(samples, (1 - alpha / 2) * 100)

        return (float(lower), float(upper))

    def _combine_confidence_metrics(
        self, confidence_intervals: Dict[str, tuple], ml_confidence: Optional[float]
    ) -> float:
        """
        Combine multiple confidence metrics into overall confidence.

        Args:
            confidence_intervals: Dictionary of confidence intervals
            ml_confidence: Optional ML-based confidence score

        Returns:
            Combined confidence score
        """
        # Calculate average interval width relative to parameter magnitude
        interval_confidences = []
        for param, (lower, upper) in confidence_intervals.items():
            width = upper - lower
            magnitude = abs(upper + lower) / 2
            if magnitude > 0:
                interval_confidences.append(1.0 - (width / magnitude))

        # Average interval-based confidence
        interval_confidence = np.mean(interval_confidences)

        if ml_confidence is not None:
            # Combine with ML confidence if available
            return (interval_confidence + ml_confidence) / 2
        else:
            return interval_confidence

    def _extract_confidence_features(
        self, waveform: np.ndarray, detection_params: Dict[str, float]
    ) -> np.ndarray:
        """
        Extract features for confidence estimation.

        Args:
            waveform: Seismic waveform data
            detection_params: Detection parameters

        Returns:
            Feature array for confidence model
        """
        # Calculate waveform features
        features = [
            np.max(np.abs(waveform)),
            np.std(waveform),
            np.mean(np.abs(waveform)),
        ]

        # Add detection parameters
        features.extend(detection_params.values())

        return np.array(features).reshape(1, -1)

    def plot_confidence_intervals(
        self, data: Dict[str, Union[float, tuple]], title: str = "Confidence Intervals"
    ) -> go.Figure:
        """
        Create interactive plot of confidence intervals.

        Args:
            data: Dictionary of parameters and their confidence intervals
            title: Plot title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        for param, (lower, upper) in data["confidence_intervals"].items():
            mean = (upper + lower) / 2

            # Add error bars
            fig.add_trace(
                go.Scatter(
                    name=param,
                    x=[mean],
                    y=[param],
                    error_x=dict(
                        type="data",
                        symmetric=False,
                        array=[mean - lower],
                        arrayminus=[upper - mean],
                    ),
                    mode="markers",
                )
            )

        fig.update_layout(
            title=title, xaxis_title="Value", yaxis_title="Parameter", showlegend=True
        )

        return fig

        return fig
