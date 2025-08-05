"""Machine Learning Module.

This module provides machine learning capabilities for seismic event
classification including model training, evaluation, and prediction.
"""

import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Optional, Tuple, Union, Any
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, roc_auc_score, roc_curve
)
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SeismicClassifier:
    """
    Machine learning classifier for seismic event classification.
    
    This class provides methods for training, evaluating, and using
    machine learning models to classify seismic events.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize seismic classifier."""
        self.config = config or Config()
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_names = []
        self.trained_models = {}
        
        logger.info("Seismic classifier initialized")
    
    def prepare_data(
        self,
        features_df: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for machine learning.
        
        Args:
            features_df: DataFrame with features and targets
            target_column: Name of target column
            feature_columns: List of feature column names
            test_size: Fraction of data for testing
            random_state: Random seed
            
        Returns:
            X_train, X_test, y_train, y_test, feature_names, class_names
        """
        logger.info("Preparing data for machine learning")
        
        # Select features
        if feature_columns is None:
            feature_columns = [col for col in features_df.columns 
                             if col != target_column and 
                             col not in ['trace_id', 'trace_index']]
        
        X = features_df[feature_columns].values
        y = features_df[target_column].values
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Encode labels if they are strings
        if isinstance(y[0], str):
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(y)
            self.label_encoders[target_column] = label_encoder
            class_names = label_encoder.classes_
        else:
            class_names = np.unique(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Store feature names
        self.feature_names = feature_columns
        
        logger.info(f"Data prepared: {X_train.shape[0]} training samples, "
                   f"{X_test.shape[0]} test samples, {len(feature_columns)} features")
        
        return X_train, X_test, y_train, y_test, feature_columns, class_names
    
    def train_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        models_to_train: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Train multiple machine learning models.
        
        Args:
            X_train: Training features
            y_train: Training targets
            models_to_train: List of model names to train
            
        Returns:
            Dictionary of trained models
        """
        if models_to_train is None:
            models_to_train = ['random_forest', 'gradient_boosting', 'svm', 'mlp']
        
        logger.info(f"Training {len(models_to_train)} models")
        
        # Define model configurations
        model_configs = {
            'random_forest': {
                'model': RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                ),
                'param_grid': {
                    'model__n_estimators': [50, 100, 200],
                    'model__max_depth': [10, 20, None],
                    'model__min_samples_split': [2, 5, 10]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=42
                ),
                'param_grid': {
                    'model__n_estimators': [50, 100, 200],
                    'model__learning_rate': [0.01, 0.1, 0.2],
                    'model__max_depth': [3, 5, 7]
                }
            },
            'svm': {
                'model': SVC(
                    random_state=42,
                    probability=True
                ),
                'param_grid': {
                    'model__C': [0.1, 1, 10],
                    'model__gamma': ['scale', 'auto'],
                    'model__kernel': ['rbf', 'linear']
                }
            },
            'mlp': {
                'model': MLPClassifier(
                    random_state=42,
                    max_iter=1000
                ),
                'param_grid': {
                    'model__hidden_layer_sizes': [(100,), (100, 50), (200, 100)],
                    'model__alpha': [0.0001, 0.001, 0.01],
                    'model__learning_rate_init': [0.001, 0.01]
                }
            }
        }
        
        trained_models = {}
        
        for model_name in models_to_train:
            if model_name not in model_configs:
                logger.warning(f"Unknown model: {model_name}")
                continue
            
            logger.info(f"Training {model_name}")
            
            # Create pipeline with scaling
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', model_configs[model_name]['model'])
            ])
            
            # Perform grid search
            grid_search = GridSearchCV(
                pipeline,
                model_configs[model_name]['param_grid'],
                cv=5,
                scoring='accuracy',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X_train, y_train)
            
            # Store best model
            trained_models[model_name] = {
                'pipeline': grid_search.best_estimator_,
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'grid_search': grid_search
            }
            
            logger.info(f"{model_name} trained - Best CV score: "
                       f"{grid_search.best_score_:.4f}")
        
        self.trained_models = trained_models
        return trained_models
    
    def evaluate_models(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate trained models on test data.
        
        Args:
            X_test: Test features
            y_test: Test targets
            class_names: Names of classes
            
        Returns:
            Dictionary of evaluation results
        """
        if not self.trained_models:
            raise ValueError("No trained models found. Train models first.")
        
        logger.info("Evaluating models on test data")
        
        evaluation_results = {}
        
        for model_name, model_info in self.trained_models.items():
            logger.info(f"Evaluating {model_name}")
            
            pipeline = model_info['pipeline']
            
            # Make predictions
            y_pred = pipeline.predict(X_test)
            y_pred_proba = pipeline.predict_proba(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, support = precision_recall_fscore_support(
                y_test, y_pred, average='weighted'
            )
            
            # Classification report
            class_report = classification_report(
                y_test, y_pred,
                target_names=class_names,
                output_dict=True
            )
            
            # Confusion matrix
            conf_matrix = confusion_matrix(y_test, y_pred)
            
            # ROC AUC (for binary/multiclass)
            try:
                if len(np.unique(y_test)) == 2:
                    roc_auc = roc_auc_score(y_test, y_pred_proba[:, 1])
                else:
                    roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
            except ValueError:
                roc_auc = None
            
            evaluation_results[model_name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'roc_auc': roc_auc,
                'classification_report': class_report,
                'confusion_matrix': conf_matrix,
                'predictions': y_pred,
                'prediction_probabilities': y_pred_proba
            }
            
            logger.info(f"{model_name} - Accuracy: {accuracy:.4f}, "
                       f"F1: {f1:.4f}")
        
        return evaluation_results
    
    def get_feature_importance(
        self,
        model_name: str,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Get feature importance for a specific model.
        
        Args:
            model_name: Name of the model
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importance
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found")
        
        pipeline = self.trained_models[model_name]['pipeline']
        model = pipeline.named_steps['model']
        
        # Extract feature importance
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_[0])
        else:
            logger.warning(f"Model {model_name} does not support feature importance")
            return pd.DataFrame()
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df.head(top_n)
    
    def plot_evaluation_results(
        self,
        evaluation_results: Dict[str, Dict[str, Any]],
        class_names: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ):
        """
        Plot evaluation results.
        
        Args:
            evaluation_results: Results from evaluate_models
            class_names: Names of classes
            save_path: Path to save plots
        """
        n_models = len(evaluation_results)
        
        # Create subplots
        fig, axes = plt.subplots(2, n_models, figsize=(5*n_models, 10))
        if n_models == 1:
            axes = axes.reshape(-1, 1)
        
        model_names = list(evaluation_results.keys())
        
        # Plot confusion matrices
        for i, model_name in enumerate(model_names):
            conf_matrix = evaluation_results[model_name]['confusion_matrix']
            
            sns.heatmap(
                conf_matrix, annot=True, fmt='d',
                xticklabels=class_names, yticklabels=class_names,
                ax=axes[0, i], cmap='Blues'
            )
            axes[0, i].set_title(f'{model_name} - Confusion Matrix')
            axes[0, i].set_xlabel('Predicted')
            axes[0, i].set_ylabel('Actual')
        
        # Plot performance metrics
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        model_metrics = []
        
        for model_name in model_names:
            model_data = []
            for metric in metrics:
                value = evaluation_results[model_name][metric]
                model_data.append(value)
            model_metrics.append(model_data)
        
        x = np.arange(len(metrics))
        width = 0.8 / n_models
        
        for i, model_name in enumerate(model_names):
            axes[1, 0].bar(
                x + i * width, model_metrics[i],
                width, label=model_name, alpha=0.8
            )
        
        axes[1, 0].set_xlabel('Metrics')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].set_title('Model Performance Comparison')
        axes[1, 0].set_xticks(x + width * (n_models - 1) / 2)
        axes[1, 0].set_xticklabels(metrics)
        axes[1, 0].legend()
        axes[1, 0].set_ylim(0, 1)
        
        # Remove unused subplots
        for i in range(1, n_models):
            axes[1, i].remove()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plots saved to {save_path}")
        
        plt.show()
    
    def save_model(
        self,
        model_name: str,
        save_path: str
    ):
        """
        Save a trained model to disk.
        
        Args:
            model_name: Name of the model to save
            save_path: Path to save the model
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found")
        
        save_data = {
            'model': self.trained_models[model_name],
            'feature_names': self.feature_names,
            'label_encoders': self.label_encoders,
            'config': self.config
        }
        
        joblib.dump(save_data, save_path)
        logger.info(f"Model {model_name} saved to {save_path}")
    
    def load_model(
        self,
        model_path: str
    ):
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
        """
        save_data = joblib.load(model_path)
        
        self.trained_models = {'loaded_model': save_data['model']}
        self.feature_names = save_data['feature_names']
        self.label_encoders = save_data['label_encoders']
        self.config = save_data['config']
        
        logger.info(f"Model loaded from {model_path}")
    
    def predict(
        self,
        features: np.ndarray,
        model_name: str = 'loaded_model'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions using a trained model.
        
        Args:
            features: Input features
            model_name: Name of the model to use
            
        Returns:
            Predictions and prediction probabilities
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found")
        
        pipeline = self.trained_models[model_name]['pipeline']
        
        # Handle missing values
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        
        predictions = pipeline.predict(features)
        prediction_probabilities = pipeline.predict_proba(features)
        
        return predictions, prediction_probabilities


class ModelEvaluator:
    """
    Advanced model evaluation and analysis.
    """
    
    def __init__(self):
        """Initialize model evaluator."""
        self.logger = get_logger(__name__)
    
    def cross_validate_models(
        self,
        models: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray,
        cv_folds: int = 5
    ) -> pd.DataFrame:
        """
        Perform cross-validation on multiple models.
        
        Args:
            models: Dictionary of models to evaluate
            X: Features
            y: Targets
            cv_folds: Number of CV folds
            
        Returns:
            DataFrame with CV results
        """
        cv_results = []
        
        for model_name, model in models.items():
            self.logger.info(f"Cross-validating {model_name}")
            
            scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy')
            
            cv_results.append({
                'model': model_name,
                'mean_score': scores.mean(),
                'std_score': scores.std(),
                'min_score': scores.min(),
                'max_score': scores.max()
            })
        
        return pd.DataFrame(cv_results)
    
    def analyze_prediction_errors(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        features: np.ndarray,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze prediction errors to identify patterns.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            features: Feature matrix
            feature_names: Names of features
            
        Returns:
            Dictionary with error analysis
        """
        # Find misclassified samples
        misclassified = y_true != y_pred
        misclassified_indices = np.where(misclassified)[0]
        
        if len(misclassified_indices) == 0:
            return {'message': 'No misclassified samples found'}
        
        # Analyze feature distributions for misclassified samples
        correct_features = features[~misclassified]
        incorrect_features = features[misclassified]
        
        feature_analysis = {}
        for i, feature_name in enumerate(feature_names):
            feature_analysis[feature_name] = {
                'correct_mean': np.mean(correct_features[:, i]),
                'incorrect_mean': np.mean(incorrect_features[:, i]),
                'correct_std': np.std(correct_features[:, i]),
                'incorrect_std': np.std(incorrect_features[:, i])
            }
        
        return {
            'misclassified_count': len(misclassified_indices),
            'misclassified_percentage': len(misclassified_indices) / len(y_true) * 100,
            'misclassified_indices': misclassified_indices,
            'feature_analysis': feature_analysis
        }


def compare_models(
    models_results: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Compare multiple model results.
    
    Args:
        models_results: Dictionary of model evaluation results
        
    Returns:
        DataFrame with model comparison
    """
    comparison_data = []
    
    for model_name, results in models_results.items():
        comparison_data.append({
            'model': model_name,
            'accuracy': results['accuracy'],
            'precision': results['precision'],
            'recall': results['recall'],
            'f1_score': results['f1_score'],
            'roc_auc': results.get('roc_auc', None)
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('f1_score', ascending=False)
    
    return comparison_df
