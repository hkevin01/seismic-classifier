"""Machine Learning Models Module.

This module provides machine learning capabilities for seismic event
classification including model training, evaluation, and prediction.
"""

from .classification import (
    SeismicClassifier,
    ModelEvaluator,
    compare_models
)

__all__ = [
    'SeismicClassifier',
    'ModelEvaluator',
    'compare_models'
]
