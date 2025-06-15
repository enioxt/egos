#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_analytics_timeseries.py

Time series analysis component for the EGOS Diagnostic Analytics module.
Provides functionality for analyzing temporal patterns in diagnostic data,
decomposing time series, and forecasting future trends.

@module: DIAG-AN-TIME
@author: EGOS Team
@version: 1.0.0
@date: 2025-05-04
@status: development

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](app_dashboard_diagnostic_roadmap.py) <!-- EGOS-REF-0D55623C --> - Project roadmap and planning
- Related Components:
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Data source
  - [diagnostic_analytics_preprocessor.py](mdc:./diagnostic_analytics_preprocessor.py) - Data preprocessing
  - [diagnostic_analytics_models.py](mdc:./diagnostic_analytics_models.py) - Predictive models (Planned)
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
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import json
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAnalytics.TimeSeries")


class TimeSeriesAnalyzer:
    """Analyzes and forecasts time series data from diagnostic issues.
    
    This class provides methods for preparing time series data from diagnostic issues,
    decomposing the series into components (trend, seasonal, residual), and forecasting
    future values using various time series models.
    
    Attributes:
        data_cache_path: Optional path to cache time series data
        models: Dictionary of fitted time series models
    """
    
    def __init__(self, data_cache_path: Optional[str] = None):
        """Initialize the time series analyzer.
        
        Args:
            data_cache_path: Optional path to cache time series data
        """
        self.logger = logger.getChild("TimeSeriesAnalyzer")
        self.data_cache_path = data_cache_path
        self.models = {}
        
    def prepare_time_series_data(self, df: pd.DataFrame, date_col: str = 'created',
                                freq: str = 'W') -> pd.DataFrame:
        """Prepare time series data from DataFrame.
        
        Converts issue data into a time series format by grouping by date and
        resampling at the specified frequency.
        
        Args:
            df: Input DataFrame
            date_col: Date column to use
            freq: Frequency for resampling ('D' for daily, 'W' for weekly, etc.)
            
        Returns:
            DataFrame with time series data
        """
        if date_col not in df.columns:
            self.logger.error(f"Date column {date_col} not found in DataFrame")
            return pd.DataFrame()
        
        self.logger.info(f"Preparing time series data using {date_col} column")
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Set date as index
        ts_df = df.set_index(date_col)
        
        # Count issues by date
        counts = ts_df.resample(freq).size()
        
        # Create time series DataFrame
        ts_data = pd.DataFrame({'count': counts})
        
        # Fill missing dates with zero
        ts_data = ts_data.fillna(0)
        
        self.logger.info(f"Created time series with {len(ts_data)} time points at {freq} frequency")
        
        # Cache if path is provided
        if self.data_cache_path:
            try:
                cache_path = Path(self.data_cache_path)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                ts_data.to_csv(cache_path)
                self.logger.info(f"Cached time series data to {cache_path}")
            except Exception as e:
                self.logger.error(f"Failed to cache time series data: {e}")
        
        return ts_data
    
    def decompose_series(self, ts_data: pd.DataFrame, column: str = 'count',
                        period: Optional[int] = None) -> Dict[str, pd.Series]:
        """Decompose time series into trend, seasonal, and residual components.
        
        Uses seasonal decomposition to break down the time series into its
        constituent components for analysis.
        
        Args:
            ts_data: Time series DataFrame
            column: Column to decompose
            period: Optional period for seasonal decomposition
            
        Returns:
            Dictionary of decomposed components
        """
        if column not in ts_data.columns:
            self.logger.error(f"Column {column} not found in time series data")
            return {}
        
        self.logger.info(f"Decomposing time series with column '{column}'")
        
        # Determine period if not specified
        if period is None:
            # Try to determine period from data frequency
            if isinstance(ts_data.index, pd.DatetimeIndex):
                if ts_data.index.freqstr == 'D':
                    period = 7  # Weekly seasonality
                elif ts_data.index.freqstr == 'W':
                    period = 4  # Monthly seasonality
                elif ts_data.index.freqstr == 'M':
                    period = 12  # Yearly seasonality
                else:
                    period = 7  # Default
            else:
                period = 7  # Default
            
            self.logger.info(f"Using period={period} for decomposition")
        
        # Perform decomposition
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Need at least 2*period data points
            if len(ts_data) < 2 * period:
                self.logger.warning(f"Not enough data points for decomposition with period={period}")
                return {}
            
            decomposition = seasonal_decompose(ts_data[column], period=period)
            
            result = {
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'observed': decomposition.observed
            }
            
            self.logger.info("Time series decomposition successful")
            return result
            
        except ImportError:
            self.logger.error("statsmodels not available for time series decomposition")
            return {}
        except Exception as e:
            self.logger.error(f"Error decomposing time series: {e}")
            return {}
    
    def forecast_arima(self, ts_data: pd.DataFrame, column: str = 'count',
                     forecast_steps: int = 8, order: Tuple[int, int, int] = (1, 1, 1)) -> Dict[str, Any]:
        """Forecast future values using ARIMA model.
        
        Fits an ARIMA model to the time series data and forecasts future values.
        
        Args:
            ts_data: Time series DataFrame
            column: Column to forecast
            forecast_steps: Number of steps to forecast
            order: ARIMA order (p, d, q)
            
        Returns:
            Dictionary with forecast results
        """
        if column not in ts_data.columns:
            self.logger.error(f"Column {column} not found in time series data")
            return {}
        
        self.logger.info(f"Forecasting with ARIMA{order} for {forecast_steps} steps ahead")
        
        # Prepare data
        data = ts_data[column].astype(float)
        
        try:
            # Import ARIMA model
            from statsmodels.tsa.arima.model import ARIMA
            
            # Fit ARIMA model
            model = ARIMA(data, order=order)
            model_fit = model.fit()
            
            # Make forecast
            forecast = model_fit.forecast(steps=forecast_steps)
            
            # Create forecast index
            if isinstance(ts_data.index, pd.DatetimeIndex):
                # For datetime index, extend with appropriate frequency
                forecast_index = pd.date_range(
                    start=ts_data.index[-1] + pd.Timedelta(days=1),
                    periods=forecast_steps,
                    freq=ts_data.index.freq
                )
            else:
                # For numeric index, just continue the sequence
                last_idx = ts_data.index[-1]
                forecast_index = range(last_idx + 1, last_idx + forecast_steps + 1)
            
            # Create forecast DataFrame
            forecast_df = pd.DataFrame({
                'forecast': forecast
            }, index=forecast_index)
            
            # Save model for later use
            self.models['arima'] = model_fit
            
            self.logger.info(f"ARIMA forecast successful, AIC: {model_fit.aic:.2f}")
            
            return {
                'forecast': forecast_df,
                'model_summary': model_fit.summary(),
                'original_data': ts_data,
                'model': 'ARIMA',
                'order': order
            }
        except ImportError:
            self.logger.error("statsmodels not available for ARIMA forecasting")
            return {}
        except Exception as e:
            self.logger.error(f"Error forecasting with ARIMA: {e}")
            return {}
    
    def forecast_prophet(self, ts_data: pd.DataFrame, column: str = 'count',
                      forecast_steps: int = 8) -> Dict[str, Any]:
        """Forecast future values using Facebook Prophet.
        
        Uses Prophet for time series forecasting, which is especially good at
        handling seasonality and holiday effects.
        
        Args:
            ts_data: Time series DataFrame
            column: Column to forecast
            forecast_steps: Number of steps to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if column not in ts_data.columns:
            self.logger.error(f"Column {column} not found in time series data")
            return {}
        
        self.logger.info(f"Forecasting with Prophet for {forecast_steps} steps ahead")
        
        try:
            # Import Prophet
            from prophet import Prophet
            
            # Prepare data in Prophet format
            prophet_data = pd.DataFrame({
                'ds': ts_data.index,
                'y': ts_data[column]
            })
            
            # Initialize and fit Prophet model
            model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
            model.fit(prophet_data)
            
            # Create future dataframe
            if isinstance(ts_data.index, pd.DatetimeIndex):
                # Get frequency in days
                if ts_data.index.freqstr == 'D':
                    freq_days = 1
                elif ts_data.index.freqstr == 'W':
                    freq_days = 7
                elif ts_data.index.freqstr == 'M':
                    freq_days = 30
                else:
                    freq_days = 1
                
                # Create future dates
                future = model.make_future_dataframe(periods=forecast_steps, freq=f"{freq_days}D")
            else:
                self.logger.warning("Non-datetime index detected, using default frequency")
                future = model.make_future_dataframe(periods=forecast_steps)
            
            # Make forecast
            forecast = model.predict(future)
            
            # Extract forecast for future dates
            future_forecast = forecast.iloc[-forecast_steps:]
            
            # Create forecast DataFrame
            forecast_df = pd.DataFrame({
                'forecast': future_forecast['yhat'],
                'forecast_lower': future_forecast['yhat_lower'],
                'forecast_upper': future_forecast['yhat_upper']
            }, index=future_forecast['ds'])
            
            # Save model for later use
            self.models['prophet'] = model
            
            self.logger.info("Prophet forecast successful")
            
            return {
                'forecast': forecast_df,
                'full_forecast': forecast,
                'original_data': ts_data,
                'model': 'Prophet'
            }
        except ImportError:
            self.logger.error("Prophet not available for forecasting")
            return {}
        except Exception as e:
            self.logger.error(f"Error forecasting with Prophet: {e}")
            return {}
    
    def plot_forecast(self, forecast_result: Dict[str, Any], title: str = 'Diagnostic Issues Forecast') -> go.Figure:
        """Create plot of forecast results.
        
        Args:
            forecast_result: Forecast result dictionary
            title: Plot title
            
        Returns:
            Plotly Figure
        """
        if not forecast_result or 'forecast' not in forecast_result:
            self.logger.error("Invalid forecast result")
            # Return empty figure
            return go.Figure()
        
        self.logger.info(f"Creating forecast plot: {title}")
        
        # Extract data
        original_data = forecast_result.get('original_data')
        forecast_data = forecast_result.get('forecast')
        
        if original_data is None or forecast_data is None:
            self.logger.error("Missing original data or forecast")
            return go.Figure()
        
        # Create figure
        fig = go.Figure()
        
        # Add original data
        fig.add_trace(go.Scatter(
            x=original_data.index,
            y=original_data.iloc[:, 0],
            mode='lines',
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['forecast'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        # Add confidence intervals if available
        if 'forecast_lower' in forecast_data.columns and 'forecast_upper' in forecast_data.columns:
            fig.add_trace(go.Scatter(
                x=forecast_data.index,
                y=forecast_data['forecast_upper'],
                mode='lines',
                name='Upper Bound',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast_data.index,
                y=forecast_data['forecast_lower'],
                mode='lines',
                name='Lower Bound',
                line=dict(width=0),
                fillcolor='rgba(68, 68, 68, 0.3)',
                fill='tonexty',
                showlegend=False
            ))
        
        # Update layout
        model_name = forecast_result.get('model', 'Time Series')
        fig.update_layout(
            title=f"{title} ({model_name})",
            xaxis_title='Date',
            yaxis_title='Count',
            legend_title='Series',
            hovermode='x',
            template='plotly_white'
        )
        
        return fig
    
    def plot_decomposition(self, decomposition: Dict[str, pd.Series], title: str = 'Time Series Decomposition') -> go.Figure:
        """Create plot of time series decomposition.
        
        Args:
            decomposition: Decomposition result dictionary
            title: Plot title
            
        Returns:
            Plotly Figure
        """
        if not decomposition or 'trend' not in decomposition:
            self.logger.error("Invalid decomposition result")
            return go.Figure()
        
        self.logger.info(f"Creating decomposition plot: {title}")
        
        # Create figure with subplots
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=4, cols=1, 
                           subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'))
        
        # Add observed data
        fig.add_trace(go.Scatter(
            x=decomposition['observed'].index,
            y=decomposition['observed'],
            mode='lines',
            name='Observed'
        ), row=1, col=1)
        
        # Add trend
        fig.add_trace(go.Scatter(
            x=decomposition['trend'].index,
            y=decomposition['trend'],
            mode='lines',
            name='Trend',
            line=dict(color='red')
        ), row=2, col=1)
        
        # Add seasonal
        fig.add_trace(go.Scatter(
            x=decomposition['seasonal'].index,
            y=decomposition['seasonal'],
            mode='lines',
            name='Seasonal',
            line=dict(color='green')
        ), row=3, col=1)
        
        # Add residual
        fig.add_trace(go.Scatter(
            x=decomposition['residual'].index,
            y=decomposition['residual'],
            mode='lines',
            name='Residual',
            line=dict(color='purple')
        ), row=4, col=1)
        
        # Update layout
        fig.update_layout(
            height=800,
            title=title,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig


# Standalone testing function
def test_timeseries_analyzer():
    """Test the TimeSeriesAnalyzer with sample data."""
    # Create sample time series data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    values = np.sin(np.linspace(0, 4*np.pi, 100)) * 10 + 30 + np.random.normal(0, 2, 100)
    
    ts_data = pd.DataFrame({
        'count': values
    }, index=dates)
    
    try:
        # Create analyzer
        analyzer = TimeSeriesAnalyzer()
        
        # Test decomposition
        decomp = analyzer.decompose_series(ts_data, period=14)
        if decomp:
            print("Decomposition successful")
        
        # Test ARIMA forecast
        try:
            forecast = analyzer.forecast_arima(ts_data, forecast_steps=14)
            if forecast:
                print(f"ARIMA forecast successful, predicted values: {forecast['forecast']['forecast'].values}")
        except Exception as e:
            print(f"ARIMA forecast error (this is expected if statsmodels is not installed): {e}")
        
        # Test Prophet forecast
        try:
            prophet_forecast = analyzer.forecast_prophet(ts_data, forecast_steps=14)
            if prophet_forecast:
                print(f"Prophet forecast successful")
        except Exception as e:
            print(f"Prophet forecast error (this is expected if prophet is not installed): {e}")
        
        return True
    except Exception as e:
        print(f"Error testing time series analyzer: {e}")
        return False


if __name__ == "__main__":
    print("Testing TimeSeriesAnalyzer...")
    success = test_timeseries_analyzer()
    print(f"Test {'successful' if success else 'failed'}")