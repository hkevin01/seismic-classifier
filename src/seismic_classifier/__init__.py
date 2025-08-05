"""Seismic Classifier Package.

A real-time seismic event classification system using machine learning.
"""

__version__ = "0.1.0"
__author__ = "Seismic AI Team"
__email__ = "team@seismic-ai.example.com"

from .config.settings import Config
from .utils.logger import get_logger

# Package-level logger
logger = get_logger(__name__)

# Default configuration
config = Config()

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "logger",
    "config",
]
