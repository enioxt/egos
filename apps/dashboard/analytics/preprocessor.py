#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_analytics_preprocessor.py

Data preprocessing component for the EGOS Diagnostic Analytics module.
Handles loading, cleaning, feature engineering, and transformation of
diagnostic data for modeling and analysis.

@module: DIAG-AN-PREP
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
  - [diagnostic_analytics_timeseries.py](mdc:./diagnostic_analytics_timeseries.py) - Time series analysis (Planned)
  - [diagnostic_analytics_models.py](mdc:./diagnostic_analytics_models.py) - Predictive models (Planned)
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
import datetime
import pandas as pd
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAnalytics.Preprocessor")

# Import local components
try:
    from dashboard.diagnostic_tracking import get_all_issues, get_issue
except ImportError:
    logger.warning("Diagnostic tracking module not available, using standalone mode")
    
    # Mock function for standalone mode
    def get_all_issues() -> List[Dict[str, Any]]:
        """Mock function to get all issues."""
        return []
    
    def get_issue(issue_id: str) -> Optional[Dict[str, Any]]:
        """Mock function to get a specific issue."""
        return None


class DataPreprocessor:
    """Preprocesses diagnostic data for analytics and machine learning models.
    
    This class is responsible for loading, cleaning, and transforming diagnostic
    issue data for use in analytics and machine learning models. It handles
    feature engineering, encoding of categorical variables, and scaling of
    numeric features.
    
    Attributes:
        data_cache_path: Optional path to cache preprocessed data
        scaler: StandardScaler instance for normalizing numeric features
        encoders: Dictionary of encoders for categorical variables
    """
    
    def __init__(self, data_cache_path: Optional[str] = None):
        """Initialize the data preprocessor.
        
        Args:
            data_cache_path: Optional path to cache preprocessed data
        """
        self.logger = logger.getChild("DataPreprocessor")
        self.data_cache_path = data_cache_path
        self.scaler = None  # Will be initialized when needed
        self.encoders = {}
        
    def load_and_prepare_data(self) -> pd.DataFrame:
        """Load and prepare diagnostic issue data for analysis.
        
        Retrieves all issues from the tracking system, converts them to a DataFrame,
        cleans the data, and performs feature engineering to prepare for modeling.
        
        Returns:
            DataFrame with prepared data
        """
        # Get raw data
        self.logger.info("Loading raw issue data from tracking system")
        raw_issues = get_all_issues()
        
        if not raw_issues:
            self.logger.warning("No issues found in tracking system")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_issues)
        self.logger.info(f"Loaded {len(df)} issues")
        
        # Basic cleaning
        df = self._clean_data(df)
        
        # Feature engineering
        df = self._engineer_features(df)
        
        # Cache if path is provided
        if self.data_cache_path:
            try:
                cache_path = Path(self.data_cache_path)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(cache_path)
                self.logger.info(f"Cached preprocessed data to {cache_path}")
            except Exception as e:
                self.logger.error(f"Failed to cache data: {e}")
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the raw data.
        
        Handles missing values, converts date columns to datetime, and removes
        duplicates from the DataFrame.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Cleaning raw data")
        original_shape = df.shape
        
        # Handle missing values
        for col in df.columns:
            if col in ['created', 'updated', 'due_date', 'closed_date']:
                # Convert date columns to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                # Fill missing text with 'unknown'
                df[col] = df[col].fillna('unknown')
            else:
                # Fill missing numeric with 0
                df[col] = df[col].fillna(0)
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['id'], keep='first')
        
        # Log results
        new_shape = df.shape
        self.logger.info(f"Data cleaning: {original_shape} -> {new_shape}")
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for analytics and modeling.
        
        Creates derived features from existing data, such as time-based features,
        text length features, and encoded categorical variables.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Engineering features")
        original_cols = len(df.columns)
        
        # Date-based features
        if 'created' in df.columns and not df['created'].isna().all():
            # Add time-based features
            df['created_day'] = df['created'].dt.day
            df['created_month'] = df['created'].dt.month
            df['created_year'] = df['created'].dt.year
            df['created_weekday'] = df['created'].dt.weekday
            
            # Add current date for age calculation
            now = pd.Timestamp(datetime.datetime.now())
            df['age_days'] = (now - df['created']).dt.days
        
        # Calculate resolution time
        if 'created' in df.columns and 'updated' in df.columns:
            closed_statuses = ['resolved', 'verified', 'closed', 'wont_fix']
            closed_issues = df[df['status'].isin(closed_statuses)]
            
            if not closed_issues.empty:
                df.loc[closed_issues.index, 'resolution_time'] = (
                    closed_issues['updated'] - closed_issues['created']
                ).dt.days
        
        # Text-based features (counts)
        if 'description' in df.columns:
            df['description_len'] = df['description'].str.len()
            df['description_word_count'] = df['description'].str.split().str.len()
        
        # Categorical encoding
        for cat_col in ['status', 'priority', 'subsystem', 'category', 'assignee']:
            if cat_col in df.columns:
                # One-hot encode
                df = self._encode_categorical(df, cat_col)
        
        # Log results
        new_cols = len(df.columns)
        self.logger.info(f"Feature engineering: {original_cols} -> {new_cols} columns")
        
        return df
    
    def _encode_categorical(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """One-hot encode a categorical column.
        
        Args:
            df: DataFrame
            column: Column name to encode
            
        Returns:
            DataFrame with encoded column
        """
        if column not in df.columns:
            return df
            
        # Get dummies with prefix
        try:
            dummies = pd.get_dummies(df[column], prefix=column)
            
            # Add to DataFrame
            df = pd.concat([df, dummies], axis=1)
            
            self.logger.debug(f"Encoded {column} into {dummies.shape[1]} categories")
        except Exception as e:
            self.logger.error(f"Failed to encode {column}: {e}")
        
        return df
    
    def transform_for_model(self, df: pd.DataFrame, 
                           target_col: Optional[str] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Transform data for model training/inference.
        
        Prepares data for machine learning by selecting numeric features,
        applying scaling, and separating the target variable if specified.
        
        Args:
            df: DataFrame to transform
            target_col: Optional target column for supervised learning
            
        Returns:
            Tuple of (X, y) arrays for modeling
        """
        self.logger.info("Transforming data for modeling")
        
        # Select numeric features only
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Remove target from features if present
        if target_col and target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        # Log selected features
        self.logger.debug(f"Selected {len(numeric_cols)} numeric features")
        
        # Create feature matrix
        X = df[numeric_cols].values
        
        # Scale features
        try:
            from sklearn.preprocessing import StandardScaler
            if self.scaler is None:
                self.scaler = StandardScaler()
                X = self.scaler.fit_transform(X)
            else:
                X = self.scaler.transform(X)
        except ImportError:
            self.logger.warning("sklearn not available, skipping feature scaling")
        except Exception as e:
            self.logger.error(f"Error scaling features: {e}")
        
        # Get target if specified
        y = None
        if target_col and target_col in df.columns:
            y = df[target_col].values
            self.logger.debug(f"Target variable: {target_col}, shape: {y.shape}")
        
        return X, y
    
    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """Get the names of numeric features used for modeling.
        
        Args:
            df: DataFrame
            
        Returns:
            List of feature names
        """
        return df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    def load_cached_data(self) -> Optional[pd.DataFrame]:
        """Load preprocessed data from cache if available.
        
        Returns:
            DataFrame with cached data or None if cache not available
        """
        if not self.data_cache_path:
            return None
        
        try:
            cache_path = Path(self.data_cache_path)
            if cache_path.exists():
                df = pd.read_parquet(cache_path)
                self.logger.info(f"Loaded cached data from {cache_path}: {df.shape}")
                return df
        except Exception as e:
            self.logger.error(f"Failed to load cached data: {e}")
        
        return None


# Standalone testing function
def test_preprocessor():
    """Test the DataPreprocessor with sample data."""
    import numpy as np
    
    # Create sample data
    sample_data = [
        {
            'id': '1',
            'title': 'Test Issue 1',
            'description': 'This is a test issue',
            'status': 'open',
            'priority': 'high',
            'created': '2025-01-01',
            'updated': '2025-01-05',
            'subsystem': 'dashboard'
        },
        {
            'id': '2',
            'title': 'Test Issue 2',
            'description': 'Another test issue with more words',
            'status': 'closed',
            'priority': 'medium',
            'created': '2025-01-02',
            'updated': '2025-01-10',
            'subsystem': 'api'
        }
    ]
    
    # Override get_all_issues for testing
    global get_all_issues
    original_get_all_issues = get_all_issues
    get_all_issues = lambda: sample_data
    
    try:
        # Create preprocessor
        preprocessor = DataPreprocessor()
        
        # Load and prepare data
        df = preprocessor.load_and_prepare_data()
        print(f"Preprocessed data shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Transform for modeling
        X, _ = preprocessor.transform_for_model(df)
        print(f"Feature matrix shape: {X.shape}")
        
        # Get feature names
        feature_names = preprocessor.get_feature_names(df)
        print(f"Feature names: {feature_names}")
        
        return True
    except Exception as e:
        print(f"Error testing preprocessor: {e}")
        return False
    finally:
        # Restore original function
        get_all_issues = original_get_all_issues


if __name__ == "__main__":
    print("Testing DataPreprocessor...")
    success = test_preprocessor()
    print(f"Test {'successful' if success else 'failed'}")