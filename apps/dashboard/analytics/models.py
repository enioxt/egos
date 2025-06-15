#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_analytics_models.py

Predictive modeling component for the EGOS Diagnostic Analytics module.
Provides machine learning models for issue resolution time prediction,
risk assessment, and prioritization.

@module: DIAG-AN-MODEL
@author: EGOS Team
@version: 1.0.0
@date: 2025-05-04
@status: development

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Data source
  - [diagnostic_analytics_preprocessor.py](mdc:./diagnostic_analytics_preprocessor.py) - Data preprocessing
  - [diagnostic_analytics_timeseries.py](mdc:./diagnostic_analytics_timeseries.py) - Time series analysis
  - [diagnostic_analytics_core.py](mdc:./diagnostic_analytics_core.py) - Core integration (Planned)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAnalytics.Models")


class PredictiveModel:
    """Predictive models for issue resolution time, risk assessment, and prioritization.
    
    This class provides functionality for training, evaluating, and using machine learning
    models to predict various aspects of diagnostic issues, including resolution time,
    risk levels, and priority scoring.
    
    Attributes:
        model_dir: Directory to store trained models
        models: Dictionary of trained models
    """
    
    def __init__(self, model_dir: Optional[str] = "models"):
        """Initialize the predictive model.
        
        Args:
            model_dir: Directory to store trained models
        """
        self.logger = logger.getChild("PredictiveModel")
        self.model_dir = Path(model_dir)
        self.models = {}
        
        # Create model directory if it doesn't exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def train_resolution_time_model(self, X: np.ndarray, y: np.ndarray,
                                  model_type: str = 'random_forest') -> Dict[str, Any]:
        """Train a model to predict issue resolution time.
        
        Args:
            X: Feature matrix
            y: Target values (resolution time)
            model_type: Type of model to train
            
        Returns:
            Dictionary with training results
        """
        if X.shape[0] == 0 or y.shape[0] == 0:
            self.logger.error("Empty training data")
            return {}
        
        self.logger.info(f"Training {model_type} model for resolution time prediction")
        
        try:
            # Import necessary libraries
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Initialize model
            model = self._create_regression_model(model_type)
            
            if model is None:
                self.logger.error(f"Unsupported model type: {model_type}")
                return {}
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            model_path = self.model_dir / f"resolution_time_{model_type}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Save to models dictionary
            self.models['resolution_time'] = model
            
            self.logger.info(f"Model trained and saved: RMSE={rmse:.2f}, R²={r2:.2f}")
            
            return {
                'model': model,
                'metrics': {
                    'rmse': rmse,
                    'mse': mse,
                    'r2': r2
                },
                'model_type': model_type,
                'model_path': str(model_path),
                'feature_count': X.shape[1]
            }
        except ImportError as e:
            self.logger.error(f"Required library not available: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error training resolution time model: {e}")
            return {}
    
    def _create_regression_model(self, model_type: str):
        """Create a regression model based on the specified type.
        
        Args:
            model_type: Type of model to create
            
        Returns:
            Regression model or None if type not supported
        """
        try:
            if model_type == 'linear':
                from sklearn.linear_model import LinearRegression
                return LinearRegression()
            elif model_type == 'random_forest':
                from sklearn.ensemble import RandomForestRegressor
                return RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingRegressor
                return GradientBoostingRegressor(random_state=42)
            elif model_type == 'svr':
                from sklearn.svm import SVR
                return SVR()
            else:
                return None
        except ImportError:
            self.logger.error(f"Required library for {model_type} not available")
            return None
    
    def train_risk_model(self, X: np.ndarray, y: np.ndarray,
                        model_type: str = 'random_forest') -> Dict[str, Any]:
        """Train a risk assessment model.
        
        Args:
            X: Feature matrix
            y: Target values (risk level)
            model_type: Type of model to train
            
        Returns:
            Dictionary with training results
        """
        if X.shape[0] == 0 or y.shape[0] == 0:
            self.logger.error("Empty training data")
            return {}
        
        self.logger.info(f"Training {model_type} model for risk assessment")
        
        try:
            # Import necessary libraries
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Initialize model
            model = self._create_classification_model(model_type)
            
            if model is None:
                self.logger.error(f"Unsupported model type: {model_type}")
                return {}
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Save model
            model_path = self.model_dir / f"risk_{model_type}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Save to models dictionary
            self.models['risk'] = model
            
            self.logger.info(f"Model trained and saved: Accuracy={accuracy:.2f}, F1={f1:.2f}")
            
            return {
                'model': model,
                'metrics': {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1
                },
                'model_type': model_type,
                'model_path': str(model_path),
                'feature_count': X.shape[1],
                'classes': np.unique(y)
            }
        except ImportError as e:
            self.logger.error(f"Required library not available: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error training risk model: {e}")
            return {}
    
    def _create_classification_model(self, model_type: str):
        """Create a classification model based on the specified type.
        
        Args:
            model_type: Type of model to create
            
        Returns:
            Classification model or None if type not supported
        """
        try:
            if model_type == 'logistic':
                from sklearn.linear_model import LogisticRegression
                return LogisticRegression(max_iter=1000, random_state=42)
            elif model_type == 'random_forest':
                from sklearn.ensemble import RandomForestClassifier
                return RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingClassifier
                return GradientBoostingClassifier(random_state=42)
            elif model_type == 'svm':
                from sklearn.svm import SVC
                return SVC(probability=True, random_state=42)
            else:
                return None
        except ImportError:
            self.logger.error(f"Required library for {model_type} not available")
            return None
    
    def load_model(self, model_name: str) -> bool:
        """Load a trained model from disk.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        # Check for resolution time models
        res_time_path = self.model_dir / f"{model_name}.pkl"
        
        if not res_time_path.exists():
            self.logger.error(f"Model file not found: {res_time_path}")
            return False
        
        try:
            with open(res_time_path, 'rb') as f:
                model = pickle.load(f)
            
            self.models[model_name] = model
            self.logger.info(f"Loaded model from {res_time_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def predict_resolution_time(self, X: np.ndarray) -> np.ndarray:
        """Predict resolution time for issues.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of predicted resolution times
        """
        if 'resolution_time' not in self.models:
            self.logger.error("Resolution time model not available")
            return np.array([])
        
        try:
            self.logger.info(f"Predicting resolution time for {X.shape[0]} issues")
            return self.models['resolution_time'].predict(X)
        except Exception as e:
            self.logger.error(f"Error predicting resolution time: {e}")
            return np.array([])
    
    def predict_risk(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict risk level for issues.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predicted classes, prediction probabilities)
        """
        if 'risk' not in self.models:
            self.logger.error("Risk model not trained")
            return np.array([]), np.array([])
        
        try:
            self.logger.info(f"Predicting risk for {X.shape[0]} issues")
            y_pred = self.models['risk'].predict(X)
            
            # Get probabilities if available
            if hasattr(self.models['risk'], 'predict_proba'):
                y_prob = self.models['risk'].predict_proba(X)
            else:
                y_prob = np.array([])
            
            return y_pred, y_prob
        except Exception as e:
            self.logger.error(f"Error predicting risk: {e}")
            return np.array([]), np.array([])
    
    def export_model_metadata(self, export_path: Optional[str] = None) -> Dict[str, Any]:
        """Export metadata about trained models.
        
        Args:
            export_path: Optional path to export metadata as JSON
            
        Returns:
            Dictionary with model metadata
        """
        metadata = {
            'models': list(self.models.keys()),
            'model_dir': str(self.model_dir),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Add specific model info
        model_info = {}
        for name, model in self.models.items():
            try:
                model_type = type(model).__name__
                params = getattr(model, 'get_params', lambda: {})()
                
                model_info[name] = {
                    'type': model_type,
                    'params': params
                }
            except Exception:
                model_info[name] = {'type': 'unknown'}
        
        metadata['model_info'] = model_info
        
        # Export to JSON if path provided
        if export_path:
            try:
                with open(export_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                self.logger.info(f"Exported model metadata to {export_path}")
            except Exception as e:
                self.logger.error(f"Error exporting model metadata: {e}")
        
        return metadata


class FeatureImportanceAnalyzer:
    """Analyzes feature importance from trained models to provide insights.
    
    This class extracts and visualizes feature importance from trained models,
    helping to understand the key factors influencing predictions.
    """
    
    def __init__(self):
        """Initialize the feature importance analyzer."""
        self.logger = logger.getChild("FeatureImportanceAnalyzer")
    
    def extract_importance(self, model: Any, feature_names: List[str]) -> pd.DataFrame:
        """Extract feature importance from a trained model.
        
        Args:
            model: Trained model
            feature_names: Names of features used in the model
            
        Returns:
            DataFrame with feature importance scores
        """
        if model is None:
            self.logger.error("Model is None")
            return pd.DataFrame()
        
        if len(feature_names) == 0:
            self.logger.error("No feature names provided")
            return pd.DataFrame()
        
        try:
            # Different models have different ways to access feature importance
            importance = None
            
            # Try common feature importance attributes
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_)
            
            if importance is None:
                self.logger.warning("Could not extract feature importance")
                return pd.DataFrame()
            
            # Ensure feature_names and importance have the same length
            if len(importance) != len(feature_names):
                self.logger.error(f"Feature count mismatch: {len(importance)} importances vs {len(feature_names)} names")
                # Truncate to shorter length
                min_len = min(len(importance), len(feature_names))
                importance = importance[:min_len]
                feature_names = feature_names[:min_len]
            
            # Create DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            })
            
            # Sort by importance (descending)
            importance_df = importance_df.sort_values('importance', ascending=False)
            
            self.logger.info(f"Extracted importance for {len(importance_df)} features")
            
            return importance_df
        except Exception as e:
            self.logger.error(f"Error extracting feature importance: {e}")
            return pd.DataFrame()
    
    def plot_importance(self, importance_df: pd.DataFrame, title: str = 'Feature Importance',
                      top_n: int = 10) -> Any:
        """Create a bar plot of feature importance.
        
        Args:
            importance_df: DataFrame with feature importance
            title: Plot title
            top_n: Number of top features to display
            
        Returns:
            Plotly Figure with importance plot
        """
        if importance_df.empty:
            self.logger.error("Empty importance DataFrame")
            return None
        
        try:
            import plotly.graph_objects as go
            
            # Select top N features
            plot_df = importance_df.head(top_n)
            
            # Create bar plot
            fig = go.Figure(go.Bar(
                x=plot_df['importance'],
                y=plot_df['feature'],
                orientation='h'
            ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title='Importance',
                yaxis_title='Feature',
                height=400 + 20 * min(top_n, len(importance_df)),
                template='plotly_white'
            )
            
            return fig
        except ImportError:
            self.logger.error("plotly not available for visualization")
            return None
        except Exception as e:
            self.logger.error(f"Error plotting feature importance: {e}")
            return None


# Standalone testing function
def test_predictive_models():
    """Test the PredictiveModel with sample data."""
    # Create sample data
    np.random.seed(42)
    X = np.random.rand(100, 5)  # 100 samples, 5 features
    y_reg = 10 * X[:, 0] + 2 * X[:, 1] - 3 * X[:, 2] + np.random.normal(0, 0.5, 100)
    y_cls = (y_reg > y_reg.mean()).astype(int)
    
    feature_names = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
    
    try:
        # Test regression model
        model = PredictiveModel(model_dir='test_models')
        
        try:
            res = model.train_resolution_time_model(X, y_reg, model_type='random_forest')
            if res:
                print(f"Resolution time model trained: RMSE={res['metrics']['rmse']:.2f}")
                
                # Test prediction
                pred = model.predict_resolution_time(X[:5])
                print(f"Predictions: {pred}")
                
                # Test feature importance
                analyzer = FeatureImportanceAnalyzer()
                importance = analyzer.extract_importance(res['model'], feature_names)
                print(f"Top features: {', '.join(importance.head(3)['feature'].tolist())}")
        except Exception as e:
            print(f"Error in regression model: {e}")
        
        # Test classification model
        try:
            res = model.train_risk_model(X, y_cls, model_type='random_forest')
            if res:
                print(f"Risk model trained: Accuracy={res['metrics']['accuracy']:.2f}")
                
                # Test prediction
                pred_cls, pred_prob = model.predict_risk(X[:5])
                print(f"Class predictions: {pred_cls}")
        except Exception as e:
            print(f"Error in classification model: {e}")
        
        return True
    except Exception as e:
        print(f"Error testing predictive models: {e}")
        return False
    finally:
        # Clean up test models
        import shutil
        try:
            shutil.rmtree('test_models')
        except:
            pass


if __name__ == "__main__":
    print("Testing PredictiveModel...")
    success = test_predictive_models()
    print(f"Test {'successful' if success else 'failed'}")