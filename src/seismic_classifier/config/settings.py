"""Configuration settings for the seismic classifier."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class APIConfig:
    """API configuration settings."""

    usgs_base_url: str = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    iris_base_url: str = "https://service.iris.edu/fdsnws/dataselect/1/query"
    timeout: int = 30
    max_retries: int = 3


@dataclass
class ModelConfig:
    """Model configuration settings."""

    model_type: str = "random_forest"
    random_state: int = 42
    test_size: float = 0.2
    validation_size: float = 0.1
    n_estimators: int = 100
    max_depth: Optional[int] = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1


@dataclass
class DataConfig:
    """Data configuration settings."""

    sampling_rate: float = 100.0
    window_length: int = 30
    overlap: float = 0.5
    frequency_bands: List[tuple] = field(
        default_factory=lambda: [
            (0.1, 1.0),  # Low frequency
            (1.0, 5.0),  # Medium frequency
            (5.0, 20.0),  # High frequency
            (20.0, 50.0),  # Very high frequency
        ]
    )
    magnitude_threshold: float = 3.0


@dataclass
class ProcessingConfig:
    """Signal processing configuration."""

    filter_type: str = "bandpass"
    filter_freqmin: float = 0.1
    filter_freqmax: float = 50.0
    filter_corners: int = 4
    detrend_type: str = "linear"
    taper_percentage: float = 0.05


@dataclass
class Config:
    """Main configuration class."""

    # Sub-configurations
    api: APIConfig = field(default_factory=APIConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    # Paths
    data_dir: Path = field(default_factory=lambda: Path("data"))
    models_dir: Path = field(default_factory=lambda: Path("models"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))

    # General settings
    debug: bool = False
    verbose: bool = True
    n_jobs: int = -1

    def __post_init__(self):
        """Post-initialization setup."""
        # Convert string paths to Path objects
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.models_dir, str):
            self.models_dir = Path(self.models_dir)
        if isinstance(self.logs_dir, str):
            self.logs_dir = Path(self.logs_dir)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Config instance
        """
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls.from_dict(config_data)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create config from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Config instance
        """
        # Extract sub-configurations
        api_config = APIConfig(**config_dict.get("api", {}))
        model_config = ModelConfig(**config_dict.get("model", {}))
        data_config = DataConfig(**config_dict.get("data", {}))
        processing_config = ProcessingConfig(**config_dict.get("processing", {}))

        # Create main config
        main_config = {
            k: v
            for k, v in config_dict.items()
            if k not in ["api", "model", "data", "processing"]
        }

        return cls(
            api=api_config,
            model=model_config,
            data=data_config,
            processing=processing_config,
            **main_config,
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config instance with environment variable overrides
        """
        config = cls()

        # Override with environment variables
        debug_env = os.getenv('DEBUG')
        if debug_env:
            config.debug = debug_env.lower() == 'true'

        verbose_env = os.getenv('VERBOSE')
        if verbose_env:
            config.verbose = verbose_env.lower() == 'true'

        n_jobs_env = os.getenv('N_JOBS')
        if n_jobs_env:
            config.n_jobs = int(n_jobs_env)

        # API configuration
        usgs_url = os.getenv('USGS_API_URL')
        if usgs_url:
            config.api.usgs_base_url = usgs_url

        iris_url = os.getenv('IRIS_API_URL')
        if iris_url:
            config.api.iris_base_url = iris_url        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "api": self.api.__dict__,
            "model": self.model.__dict__,
            "data": self.data.__dict__,
            "processing": self.processing.__dict__,
            "data_dir": str(self.data_dir),
            "models_dir": str(self.models_dir),
            "logs_dir": str(self.logs_dir),
            "cache_dir": str(self.cache_dir),
            "debug": self.debug,
            "verbose": self.verbose,
            "n_jobs": self.n_jobs,
        }

    def save_yaml(self, config_path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Path to save configuration file
        """
        with open(config_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
