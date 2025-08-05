"""Seismic event location determination module using advanced algorithms."""

from typing import Dict, Optional, Tuple, Union

import numpy as np
import tensorflow as tf
from obspy import Stream, Trace
from scipy.optimize import minimize


class LocationDeterminer:
    """Determine seismic event location using multiple methods."""

    def __init__(
        self,
        station_coords: Dict[str, Tuple[float, float, float]],
        velocity_model: Optional[Dict[str, float]] = None,
        model_path: Optional[str] = None,
    ):
        """
        Initialize the location determiner.

        Args:
            station_coords: Dictionary of station coordinates (lat, lon, depth)
            velocity_model: Optional velocity model for different phases
            model_path: Optional path to trained ML model
        """
        self.station_coords = station_coords
        self.velocity_model = velocity_model or {
            "P": 6.0,  # P-wave velocity in km/s
            "S": 3.5,  # S-wave velocity in km/s
        }

        # Load ML model if provided
        self.model = None
        if model_path:
            self.model = tf.keras.models.load_model(model_path)

    def locate_event(
        self,
        picks: Dict[str, Dict[str, float]],
        initial_guess: Optional[Tuple[float, float, float]] = None,
    ) -> Dict[str, Union[float, list]]:
        """
        Locate seismic event using arrival times.

        Args:
            picks: Dictionary of P and S wave arrival times for each station
            initial_guess: Optional initial location guess (lat, lon, depth)

        Returns:
            Dictionary containing estimated location and uncertainty
        """
        if not picks:
            raise ValueError("No phase picks provided")

        if not initial_guess:
            initial_guess = self._get_initial_guess(picks)

        # Optimize location using arrival times
        result = minimize(
            self._objective_function,
            initial_guess,
            args=(picks,),
            method="Nelder-Mead",
            options={"maxiter": 1000},
        )

        if not result.success:
            raise RuntimeError("Location optimization failed to converge")

        # Calculate location uncertainty
        uncertainty = self._estimate_uncertainty(result.x, picks)

        return {
            "latitude": float(result.x[0]),
            "longitude": float(result.x[1]),
            "depth": float(result.x[2]),
            "uncertainty": uncertainty,
            "confidence": 1.0 - result.fun / len(picks),  # Normalize misfit
            "stations_used": list(picks.keys()),
        }

    def locate_event_ml(
        self, waveforms: Dict[str, Union[np.ndarray, Stream, Trace]]
    ) -> Dict[str, Union[float, list]]:
        """
        Locate event using ML approach on waveforms.

        Args:
            waveforms: Dictionary of waveforms from different stations

        Returns:
            Dictionary containing estimated location and uncertainty
        """
        if not self.model:
            raise ValueError("No ML model loaded for location")

        # Prepare features from waveforms
        features = []
        for station_id, waveform in waveforms.items():
            if isinstance(waveform, (Stream, Trace)):
                data = waveform.data
            else:
                data = waveform

            # Extract features from waveform
            station_features = self._extract_ml_features(data)
            features.append(station_features)

        # Combine features and get prediction
        combined_features = np.array(features)
        prediction = self.model.predict(combined_features)

        # Extract location and uncertainty
        if len(prediction) == 4:  # Model outputs uncertainty
            lat, lon, depth, uncertainty = prediction
        else:
            lat, lon, depth = prediction
            uncertainty = 5.0  # Default uncertainty in km

        return {
            "latitude": float(lat),
            "longitude": float(lon),
            "depth": float(depth),
            "uncertainty": float(uncertainty),
            "confidence": 0.9,  # Default confidence for ML approach
            "stations_used": list(waveforms.keys()),
        }

    def _objective_function(
        self, location: Tuple[float, float, float], picks: Dict[str, Dict[str, float]]
    ) -> float:
        """
        Calculate misfit between observed and theoretical arrival times.

        Args:
            location: Trial location (lat, lon, depth)
            picks: Observed arrival times

        Returns:
            Total misfit value
        """
        total_misfit = 0.0

        for station_id, station_picks in picks.items():
            station_coord = self.station_coords[station_id]

            # Calculate theoretical arrival times
            theoretical_times = self._calculate_theoretical_times(
                location, station_coord
            )

            # Add misfit for each phase
            for phase in ["P", "S"]:
                if phase in station_picks:
                    residual = station_picks[phase] - theoretical_times[phase]
                    total_misfit += residual**2

        return total_misfit

    def _calculate_theoretical_times(
        self,
        event_loc: Tuple[float, float, float],
        station_loc: Tuple[float, float, float],
    ) -> Dict[str, float]:
        """
        Calculate theoretical arrival times for P and S waves.

        Args:
            event_loc: Event location (lat, lon, depth)
            station_loc: Station location (lat, lon, depth)

        Returns:
            Dictionary of theoretical arrival times
        """
        # Calculate distance (simple spherical approximation)
        distance = np.sqrt(
            (event_loc[0] - station_loc[0]) ** 2
            + (event_loc[1] - station_loc[1]) ** 2
            + (event_loc[2] - station_loc[2]) ** 2
        )

        return {
            "P": distance / self.velocity_model["P"],
            "S": distance / self.velocity_model["S"],
        }

    def _get_initial_guess(
        self, picks: Dict[str, Dict[str, float]]
    ) -> Tuple[float, float, float]:
        """
        Get initial location guess using station geometry.

        Args:
            picks: Dictionary of arrival times

        Returns:
            Initial location guess (lat, lon, depth)
        """
        # Use center of stations as initial guess
        stations = list(picks.keys())
        coords = np.array([self.station_coords[s] for s in stations])

        return (
            np.mean(coords[:, 0]),  # latitude
            np.mean(coords[:, 1]),  # longitude
            10.0,  # default depth in km
        )

    def _estimate_uncertainty(
        self, location: np.ndarray, picks: Dict[str, Dict[str, float]]
    ) -> float:
        """
        Estimate location uncertainty using bootstrap.

        Args:
            location: Estimated location
            picks: Phase picks used for location

        Returns:
            Estimated uncertainty in kilometers
        """
        # Perform bootstrap uncertainty estimation
        n_bootstrap = 100
        bootstrap_locations = []

        for _ in range(n_bootstrap):
            # Randomly resample picks
            sampled_picks = dict(
                (k, picks[k])
                for k in np.random.choice(
                    list(picks.keys()), size=len(picks), replace=True
                )
            )

            # Relocate using resampled picks
            try:
                result = minimize(
                    self._objective_function,
                    location,
                    args=(sampled_picks,),
                    method="Nelder-Mead",
                )
                if result.success:
                    bootstrap_locations.append(result.x)
            except:
                continue

        if not bootstrap_locations:
            return 10.0  # Default uncertainty if bootstrap fails

        # Calculate standard deviation of bootstrap locations
        bootstrap_locations = np.array(bootstrap_locations)
        uncertainty = np.std(bootstrap_locations, axis=0)

        # Return average uncertainty across dimensions
        return float(np.mean(uncertainty))

    def _extract_ml_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract features from waveform for ML location.

        Args:
            data: Waveform data

        Returns:
            Array of features for ML model
        """
        # Implement feature extraction for ML model
        # This is a placeholder - actual implementation would depend on model
        features = np.array(
            [
                np.max(np.abs(data)),
                np.std(data),
                np.mean(np.abs(data)),
                # Add more features as needed
            ]
        )

        return features.reshape(1, -1)

        return features.reshape(1, -1)
