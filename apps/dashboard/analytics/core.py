#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_analytics_core.py

Core integration component for the EGOS Diagnostic Analytics module.
Ties together preprocessing, time series analysis, predictive modeling,
and resource allocation components into a unified system.

@module: DIAG-AN-CORE
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
  - [diagnostic_analytics_models.py](mdc:./diagnostic_analytics_models.py) - Predictive models
  - [diagnostic_analytics_resource.py](mdc:./diagnostic_analytics_resource.py) - Resource allocation
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
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import json
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAnalytics.Core")

# Import our components
try:
    from diagnostic_analytics_preprocessor import DataPreprocessor
    from diagnostic_analytics_timeseries import TimeSeriesAnalyzer
    from diagnostic_analytics_models import PredictiveModel, FeatureImportanceAnalyzer
    from diagnostic_analytics_resource import ResourceAllocator, PriorityManager
except ImportError as e:
    logger.error(f"Failed to import analytics components: {e}")
    # Define placeholder classes for graceful degradation
    class DataPreprocessor:
        def __init__(self, *args, **kwargs):
            pass
    
    class TimeSeriesAnalyzer:
        def __init__(self, *args, **kwargs):
            pass
    
    class PredictiveModel:
        def __init__(self, *args, **kwargs):
            pass
    
    class FeatureImportanceAnalyzer:
        def __init__(self, *args, **kwargs):
            pass
    
    class ResourceAllocator:
        def __init__(self, *args, **kwargs):
            pass
    
    class PriorityManager:
        def __init__(self, *args, **kwargs):
            pass


class DiagnosticAnalytics:
    """Core integration for diagnostic analytics components.
    
    This class ties together all the analytics components into a unified system,
    providing a high-level API for the diagnostic tracking system to leverage
    advanced analytics capabilities.
    
    Attributes:
        config: Configuration dictionary
        data_dir: Directory for caching data and models
        preprocessor: Data preprocessing component
        time_series: Time series analysis component
        model: Predictive modeling component
        resource_allocator: Resource allocation component
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
               data_dir: Optional[str] = None):
        """Initialize the diagnostic analytics system.
        
        Args:
            config: Optional configuration dictionary
            data_dir: Optional directory for caching data and models
        """
        self.logger = logger.getChild("DiagnosticAnalytics")
        self.config = config or {}
        
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path("diagnostic_data")
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.logger.info("Initializing diagnostic analytics components")
        
        # Data preprocessor
        preprocessor_cache = self.data_dir / "preprocessed_data.parquet"
        self.preprocessor = DataPreprocessor(data_cache_path=str(preprocessor_cache))
        
        # Time series analyzer
        timeseries_cache = self.data_dir / "timeseries_data.csv"
        self.time_series = TimeSeriesAnalyzer(data_cache_path=str(timeseries_cache))
        
        # Predictive model
        model_dir = self.data_dir / "models"
        self.model = PredictiveModel(model_dir=str(model_dir))
        
        # Resource allocator
        self.resource_allocator = ResourceAllocator()
        
        # Priority manager
        self.priority_manager = PriorityManager()
        
        # Tracking state
        self.last_update_time = None
        self.prepared_data = None
        self._trained_models = False
        
        self.logger.info("Diagnostic analytics system initialized")
    
    def update_data(self, issues: Optional[List[Dict[str, Any]]] = None, 
                  force: bool = False) -> bool:
        """Update and preprocess data from the diagnostic tracking system.
        
        Args:
            issues: Optional list of issues (if None, will fetch from tracking system)
            force: Force update even if data is recent
            
        Returns:
            True if data was updated, False otherwise
        """
        # Check if update is needed
        now = datetime.datetime.now()
        if not force and self.last_update_time:
            # Only update if more than 1 hour has passed
            time_diff = (now - self.last_update_time).total_seconds() / 3600
            if time_diff < 1:
                self.logger.info(f"Skipping update, last update was {time_diff:.2f} hours ago")
                return False
        
        self.logger.info("Updating diagnostic analytics data")
        
        try:
            # Load and preprocess data
            self.prepared_data = self.preprocessor.load_and_prepare_data()
            
            if self.prepared_data.empty:
                self.logger.warning("No data available from tracking system")
                return False
            
            self.last_update_time = now
            self.logger.info(f"Successfully updated data with {len(self.prepared_data)} issues")
            return True
        except Exception as e:
            self.logger.error(f"Error updating data: {e}")
            return False
    
    def train_models(self, force: bool = False) -> Dict[str, Any]:
        """Train predictive models on the current data.
        
        Args:
            force: Force retraining even if models already trained
            
        Returns:
            Dictionary with training results
        """
        if self._trained_models and not force:
            self.logger.info("Models already trained, skipping")
            return {"status": "skipped"}
        
        if self.prepared_data is None or self.prepared_data.empty:
            self.logger.warning("No data available for training models")
            return {"status": "no_data"}
        
        self.logger.info("Training predictive models")
        results = {}
        
        try:
            # Prepare features and target for resolution time prediction
            if "resolution_time" in self.prepared_data.columns:
                # Filter to only resolved issues with valid resolution time
                mask = self.prepared_data["resolution_time"].notna()
                train_data = self.prepared_data[mask]
                
                if len(train_data) > 10:  # Need minimum training examples
                    X, y = self.preprocessor.transform_for_model(
                        train_data, target_col="resolution_time"
                    )
                    
                    # Train resolution time model
                    res_time_results = self.model.train_resolution_time_model(X, y)
                    results["resolution_time"] = res_time_results
                    
                    self.logger.info(f"Trained resolution time model: "
                                   f"RMSE={res_time_results.get('metrics', {}).get('rmse', 'N/A')}")
                else:
                    self.logger.warning(
                        f"Insufficient training data for resolution time model: {len(train_data)} samples"
                    )
            
            # Prepare features and target for risk assessment
            if "risk_level" in self.prepared_data.columns:
                mask = self.prepared_data["risk_level"].notna()
                train_data = self.prepared_data[mask]
                
                if len(train_data) > 10:
                    X, y = self.preprocessor.transform_for_model(
                        train_data, target_col="risk_level"
                    )
                    
                    # Train risk model
                    risk_results = self.model.train_risk_model(X, y)
                    results["risk"] = risk_results
                    
                    self.logger.info(f"Trained risk model: "
                                   f"Accuracy={risk_results.get('metrics', {}).get('accuracy', 'N/A')}")
                else:
                    self.logger.warning(
                        f"Insufficient training data for risk model: {len(train_data)} samples"
                    )
            
            # Export model metadata
            metadata_path = self.data_dir / "model_metadata.json"
            model_metadata = self.model.export_model_metadata(str(metadata_path))
            results["metadata"] = model_metadata
            
            self._trained_models = True
            results["status"] = "success"
            return results
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
            return {"status": "error", "error": str(e)}
    
    def analyze_time_series(self, freq: str = "W") -> Dict[str, Any]:
        """Analyze time series patterns in the diagnostic data.
        
        Args:
            freq: Frequency for time series analysis (D=daily, W=weekly, M=monthly)
            
        Returns:
            Dictionary with time series analysis results
        """
        if self.prepared_data is None or self.prepared_data.empty:
            self.logger.warning("No data available for time series analysis")
            return {"status": "no_data"}
        
        self.logger.info(f"Performing time series analysis with frequency '{freq}'")
        results = {}
        
        try:
            # Prepare time series data
            ts_data = self.time_series.prepare_time_series_data(
                self.prepared_data, 
                date_col="created", 
                freq=freq
            )
            
            if ts_data.empty:
                self.logger.warning("No time series data available")
                return {"status": "empty_time_series"}
            
            results["time_series_data"] = ts_data
            
            # Decompose time series
            decomposition = self.time_series.decompose_series(ts_data)
            if decomposition:
                results["decomposition"] = {
                    "components": list(decomposition.keys())
                }
            
            # Forecast with ARIMA
            try:
                arima_forecast = self.time_series.forecast_arima(
                    ts_data, 
                    forecast_steps=8
                )
                if arima_forecast:
                    results["arima_forecast"] = {
                        "steps": 8,
                        "model": "ARIMA"
                    }
            except Exception as e:
                self.logger.warning(f"ARIMA forecasting failed: {e}")
            
            # Forecast with Prophet (if available)
            try:
                prophet_forecast = self.time_series.forecast_prophet(
                    ts_data,
                    forecast_steps=8
                )
                if prophet_forecast:
                    results["prophet_forecast"] = {
                        "steps": 8,
                        "model": "Prophet"
                    }
            except Exception as e:
                self.logger.warning(f"Prophet forecasting failed: {e}")
            
            results["status"] = "success"
            return results
        except Exception as e:
            self.logger.error(f"Error in time series analysis: {e}")
            return {"status": "error", "error": str(e)}
    
    def optimize_resources(self, available_resources: int = 1) -> Dict[str, Any]:
        """Optimize resource allocation for issue remediation.
        
        Args:
            available_resources: Number of available resources
            
        Returns:
            Dictionary with resource optimization results
        """
        if self.prepared_data is None or self.prepared_data.empty:
            self.logger.warning("No data available for resource optimization")
            return {"status": "no_data"}
        
        self.logger.info(f"Optimizing resources with {available_resources} available resources")
        
        try:
            # Filter to only open issues
            open_statuses = ["identified", "in_progress", "reviewing", "assigned", "reopened"]
            open_issues = self.prepared_data[
                self.prepared_data["status"].str.lower().isin(open_statuses)
            ]
            
            if open_issues.empty:
                self.logger.warning("No open issues available for optimization")
                return {"status": "no_open_issues"}
            
            # Convert DataFrame rows to dictionaries
            issues = open_issues.to_dict("records")
            
            # Function to estimate resolution time
            def estimate_resolution_time(issue):
                if "resolution_time" in self.model.models:
                    try:
                        # Extract features for this issue
                        df = pd.DataFrame([issue])
                        X, _ = self.preprocessor.transform_for_model(df)
                        
                        # Predict resolution time
                        pred_time = self.model.predict_resolution_time(X)[0]
                        return max(1, pred_time)  # Ensure positive time
                    except Exception as e:
                        self.logger.debug(f"Error predicting resolution time: {e}")
                
                # Fallback: use priority-based estimate
                priority_map = {
                    "critical": 5,
                    "high": 4,
                    "medium": 3,
                    "low": 2,
                    "enhancement": 1
                }
                priority = issue.get("priority", "medium").lower()
                return priority_map.get(priority, 3)
            
            # Get risk scores if risk model is available
            risk_scores = {}
            if "risk" in self.model.models:
                try:
                    X, _ = self.preprocessor.transform_for_model(open_issues)
                    risk_preds, risk_probs = self.model.predict_risk(X)
                    
                    # Use highest risk class probability as risk score
                    for i, issue in enumerate(issues):
                        if i < len(risk_probs):
                            issue_id = issue.get("id")
                            if issue_id:
                                max_prob = risk_probs[i].max() if len(risk_probs) > 0 else 0.5
                                risk_scores[issue_id] = max_prob
                except Exception as e:
                    self.logger.warning(f"Error predicting risk: {e}")
            
            # Optimize schedule
            optimization = self.resource_allocator.optimize_schedule(
                issues,
                available_resources=available_resources,
                time_estimate_fn=estimate_resolution_time,
                risk_scores=risk_scores
            )
            
            return {
                "status": "success",
                "optimization": optimization,
                "open_issues": len(issues),
                "risk_scores_available": len(risk_scores) > 0
            }
        except Exception as e:
            self.logger.error(f"Error in resource optimization: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_insights(self) -> Dict[str, Any]:
        """Generate insights from the diagnostic analytics data.
        
        Returns:
            Dictionary with insights
        """
        if self.prepared_data is None or self.prepared_data.empty:
            return {"status": "no_data"}
        
        self.logger.info("Generating insights from diagnostic data")
        insights = {}
        
        try:
            # Issue volume trend
            if "created" in self.prepared_data.columns:
                self.prepared_data["created"] = pd.to_datetime(self.prepared_data["created"])
                weekly_issues = self.prepared_data.resample("W", on="created").size()
                
                if len(weekly_issues) >= 2:
                    recent_weeks = weekly_issues.iloc[-4:] if len(weekly_issues) >= 4 else weekly_issues
                    avg_recent = recent_weeks.mean()
                    avg_overall = weekly_issues.mean()
                    
                    insights["issue_volume"] = {
                        "recent_weekly_avg": avg_recent,
                        "overall_weekly_avg": avg_overall,
                        "trend": "increasing" if avg_recent > avg_overall * 1.1 else
                                "decreasing" if avg_recent < avg_overall * 0.9 else "stable"
                    }
            
            # Resolution time analysis
            if "resolution_time" in self.prepared_data.columns:
                resolved = self.prepared_data[self.prepared_data["resolution_time"].notna()]
                
                if not resolved.empty:
                    resolution_times = resolved["resolution_time"]
                    
                    insights["resolution_time"] = {
                        "mean": resolution_times.mean(),
                        "median": resolution_times.median(),
                        "min": resolution_times.min(),
                        "max": resolution_times.max()
                    }
                    
                    # Resolution time by priority
                    if "priority" in resolved.columns:
                        by_priority = resolved.groupby("priority")["resolution_time"].median()
                        insights["resolution_by_priority"] = by_priority.to_dict()
            
            # Subsystem analysis
            if "subsystem" in self.prepared_data.columns:
                subsystem_counts = self.prepared_data["subsystem"].value_counts()
                
                insights["subsystems"] = {
                    "most_issues": subsystem_counts.index[0],
                    "issue_counts": subsystem_counts.to_dict()
                }
            
            # Status distribution
            if "status" in self.prepared_data.columns:
                status_counts = self.prepared_data["status"].value_counts()
                total_issues = len(self.prepared_data)
                
                insights["status_distribution"] = {
                    status: {
                        "count": count,
                        "percentage": (count / total_issues) * 100
                    }
                    for status, count in status_counts.items()
                }
            
            # Model performance if available
            if hasattr(self.model, "models") and self.model.models:
                insights["models"] = {
                    "available_models": list(self.model.models.keys())
                }
            
            insights["status"] = "success"
            return insights
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return {"status": "error", "error": str(e)}
    
    def save_state(self) -> Dict[str, Any]:
        """Save current state to disk.
        
        Returns:
            Dictionary with save results
        """
        try:
            state_file = self.data_dir / "analytics_state.json"
            
            state = {
                "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
                "models_trained": self._trained_models,
                "data_available": self.prepared_data is not None and not self.prepared_data.empty,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"Saved state to {state_file}")
            return {"status": "success", "file": str(state_file)}
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
            return {"status": "error", "error": str(e)}
    
    def load_state(self) -> Dict[str, Any]:
        """Load state from disk.
        
        Returns:
            Dictionary with load results
        """
        try:
            state_file = self.data_dir / "analytics_state.json"
            
            if not state_file.exists():
                self.logger.info("No state file found, starting fresh")
                return {"status": "not_found"}
            
            with open(state_file, "r") as f:
                state = json.load(f)
            
            if "last_update_time" in state and state["last_update_time"]:
                self.last_update_time = datetime.datetime.fromisoformat(state["last_update_time"])
            
            self._trained_models = state.get("models_trained", False)
            
            self.logger.info(f"Loaded state from {state_file}")
            return {"status": "success", "state": state}
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return {"status": "error", "error": str(e)}


# Standalone testing
def test_diagnostic_analytics():
    """Test the DiagnosticAnalytics system with sample data."""
    import tempfile
    import shutil
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {test_dir}")
    
    try:
        # Initialize analytics system
        analytics = DiagnosticAnalytics(data_dir=test_dir)
        
        # Note: This will fail if issue data is not available
        # In a real test we would mock this data
        updated = analytics.update_data()
        print(f"Data updated: {updated}")
        
        if updated:
            # Test model training
            train_results = analytics.train_models()
            print(f"Model training status: {train_results.get('status')}")
            
            # Test time series analysis
            ts_results = analytics.analyze_time_series(freq="W")
            print(f"Time series analysis status: {ts_results.get('status')}")
            
            # Test resource optimization
            opt_results = analytics.optimize_resources(available_resources=2)
            print(f"Resource optimization status: {opt_results.get('status')}")
            
            # Get insights
            insights = analytics.get_insights()
            print(f"Insights status: {insights.get('status')}")
            
            # Save and load state
            save_result = analytics.save_state()
            print(f"Save state status: {save_result.get('status')}")
            
            load_result = analytics.load_state()
            print(f"Load state status: {load_result.get('status')}")
        
        return True
    except Exception as e:
        print(f"Error testing analytics: {e}")
        return False
    finally:
        # Clean up
        shutil.rmtree(test_dir)
        print(f"Cleaned up temporary directory: {test_dir}")


if __name__ == "__main__":
    print("Testing DiagnosticAnalytics system")
    success = test_diagnostic_analytics()
    print(f"Test {'successful' if success else 'failed'}")