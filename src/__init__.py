"""
Seismic Event Classification System

A comprehensive Python package for real-time seismic event classification
using machine learning and deep learning techniques.

Author: Seismic Classification Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Seismic Classification Team"
__email__ = "contact@seismic-classifier.org"

# Core imports
from .utils.logger import get_logger
from .utils.helpers import load_config

# Make core functionality available at package level
logger = get_logger(__name__)

__all__ = [
    "logger",
    "load_config",
    "__version__",
    "__author__",
    "__email__"
]
