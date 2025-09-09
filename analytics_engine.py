"""
Predictive Analytics Engine for HALog
Advanced analytics capabilities using scikit-learn for anomaly detection and predictive maintenance

Features:
- Isolation Forest algorithm for parameter anomaly detection
- Rolling window analysis for trend anomalies
- Statistical outlier detection using z-score and IQR methods
- Regression models to predict parameter drift
- Time-series forecasting using ARIMA or seasonal decomposition
- Maintenance scheduling based on predicted failures
- Confidence intervals for predictions
- Analytics visualization integration

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import numpy as np
import pandas as pd
import json
import os
import pickle
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Try to import scikit-learn components
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Warning: scikit-learn not available. Analytics features will be limited.")
    SKLEARN_AVAILABLE = False

# Try to import additional analytics libraries
try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class AnomalyAlert:
    """Represents an anomaly detection alert"""
    timestamp: datetime
    parameter: str
    value: float
    anomaly_score: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    confidence: float
    suggested_action: str


@dataclass
class PredictionResult:
    """Represents a prediction result"""
    parameter: str
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    prediction_horizon: timedelta
    model_accuracy: float
    risk_level: str


class StatisticalAnalyzer:
    """Statistical analysis methods that don't require scikit-learn"""
    
    @staticmethod
    def detect_outliers_zscore(data: pd.Series, threshold: float = 3.0) -> List[int]:
        """Detect outliers using z-score method"""
        if len(data) < 3:
            return []
        
        z_scores = np.abs(stats.zscore(data.dropna()) if SCIPY_AVAILABLE else 
                         (data - data.mean()) / data.std())
        return data.index[z_scores > threshold].tolist()
    
    @staticmethod
    def detect_outliers_iqr(data: pd.Series, multiplier: float = 1.5) -> List[int]:
        """Detect outliers using IQR method"""
        if len(data) < 4:
            return []
        
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        return outliers.index.tolist()
    
    @staticmethod
    def calculate_rolling_statistics(data: pd.Series, window: int = 20) -> Dict[str, pd.Series]:
        """Calculate rolling statistics for trend analysis"""
        return {
            'rolling_mean': data.rolling(window=window).mean(),
            'rolling_std': data.rolling(window=window).std(),
            'rolling_min': data.rolling(window=window).min(),
            'rolling_max': data.rolling(window=window).max()
        }
    
    @staticmethod
    def detect_trend_changes(data: pd.Series, window: int = 10) -> List[Dict]:
        """Detect significant trend changes in the data"""
        changes = []
        
        if len(data) < window * 2:
            return changes
        
        # Calculate rolling slopes
        slopes = []
        for i in range(window, len(data) - window):
            y = data.iloc[i-window:i+window].values
            x = np.arange(len(y))
            if len(y) > 1:
                slope = np.polyfit(x, y, 1)[0]
                slopes.append((data.index[i], slope))
        
        # Detect significant slope changes
        if len(slopes) > 2:
            slope_values = [s[1] for s in slopes]
            slope_mean = np.mean(slope_values)
            slope_std = np.std(slope_values)
            
            for timestamp, slope in slopes:
                if abs(slope - slope_mean) > 2 * slope_std:
                    changes.append({
                        'timestamp': timestamp,
                        'slope': slope,
                        'significance': abs(slope - slope_mean) / slope_std,
                        'direction': 'increasing' if slope > slope_mean else 'decreasing'
                    })
        
        return changes


class AnomalyDetector:
    """Anomaly detection using multiple methods"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.models = {}
        self.scalers = {}
        self.statistical_analyzer = StatisticalAnalyzer()
    
    def fit(self, data: pd.DataFrame, parameter: str):
        """Fit anomaly detection model for a parameter"""
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Using statistical methods only.")
            return
        
        if parameter not in data.columns:
            raise ValueError(f"Parameter {parameter} not found in data")
        
        # Prepare data
        param_data = data[parameter].dropna().values.reshape(-1, 1)
        
        if len(param_data) < 10:
            print(f"Warning: Not enough data points for {parameter} anomaly detection")
            return
        
        # Scale data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(param_data)
        
        # Fit Isolation Forest
        isolation_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        isolation_forest.fit(scaled_data)
        
        # Store model and scaler
        self.models[parameter] = isolation_forest
        self.scalers[parameter] = scaler
    
    def detect_anomalies(self, data: pd.DataFrame, parameter: str) -> List[AnomalyAlert]:
        """Detect anomalies in data for a specific parameter"""
        alerts = []
        
        if parameter not in data.columns:
            return alerts
        
        param_data = data[parameter].dropna()
        if param_data.empty:
            return alerts
        
        # Method 1: Isolation Forest (if available and model trained)
        if SKLEARN_AVAILABLE and parameter in self.models:
            try:
                scaled_data = self.scalers[parameter].transform(param_data.values.reshape(-1, 1))
                anomaly_scores = self.models[parameter].decision_function(scaled_data)
                predictions = self.models[parameter].predict(scaled_data)
                
                # Create alerts for anomalies
                for idx, (timestamp, value) in enumerate(param_data.items()):
                    if predictions[idx] == -1:  # Anomaly detected
                        severity = self._assess_severity(anomaly_scores[idx])
                        
                        alert = AnomalyAlert(
                            timestamp=timestamp if isinstance(timestamp, datetime) else datetime.now(),
                            parameter=parameter,
                            value=value,
                            anomaly_score=abs(anomaly_scores[idx]),
                            severity=severity,
                            description=f"Isolation Forest detected anomaly in {parameter}",
                            confidence=min(abs(anomaly_scores[idx]), 1.0),
                            suggested_action=self._get_suggested_action(parameter, severity)
                        )
                        alerts.append(alert)
            except Exception as e:
                print(f"Warning: Isolation Forest detection failed for {parameter}: {e}")
        
        # Method 2: Statistical methods (always available)
        # Z-score outliers
        zscore_outliers = self.statistical_analyzer.detect_outliers_zscore(param_data)
        for idx in zscore_outliers:
            if idx in param_data.index:
                timestamp = param_data.index[param_data.index.get_loc(idx)]
                value = param_data.loc[idx]
                
                alert = AnomalyAlert(
                    timestamp=timestamp if isinstance(timestamp, datetime) else datetime.now(),
                    parameter=parameter,
                    value=value,
                    anomaly_score=0.7,  # Static score for statistical method
                    severity='medium',
                    description=f"Z-score outlier detected in {parameter}",
                    confidence=0.8,
                    suggested_action=self._get_suggested_action(parameter, 'medium')
                )
                alerts.append(alert)
        
        # Method 3: IQR outliers
        iqr_outliers = self.statistical_analyzer.detect_outliers_iqr(param_data)
        for idx in iqr_outliers:
            if idx in param_data.index:
                timestamp = param_data.index[param_data.index.get_loc(idx)]
                value = param_data.loc[idx]
                
                # Avoid duplicate alerts
                if not any(alert.timestamp == timestamp and alert.parameter == parameter for alert in alerts):
                    alert = AnomalyAlert(
                        timestamp=timestamp if isinstance(timestamp, datetime) else datetime.now(),
                        parameter=parameter,
                        value=value,
                        anomaly_score=0.6,
                        severity='low',
                        description=f"IQR outlier detected in {parameter}",
                        confidence=0.7,
                        suggested_action=self._get_suggested_action(parameter, 'low')
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _assess_severity(self, anomaly_score: float) -> str:
        """Assess anomaly severity based on score"""
        abs_score = abs(anomaly_score)
        
        if abs_score > 0.8:
            return 'critical'
        elif abs_score > 0.6:
            return 'high'
        elif abs_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_suggested_action(self, parameter: str, severity: str) -> str:
        """Get suggested action based on parameter and severity"""
        actions = {
            'critical': f"Immediate inspection of {parameter} required - system may be at risk",
            'high': f"Schedule urgent maintenance check for {parameter}",
            'medium': f"Monitor {parameter} closely and schedule maintenance if pattern continues",
            'low': f"Note anomaly in {parameter} for routine maintenance review"
        }
        return actions.get(severity, "Monitor parameter for continued anomalous behavior")


class PredictiveMaintenanceEngine:
    """Engine for predictive maintenance using regression models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
    
    def build_drift_model(self, data: pd.DataFrame, parameter: str, 
                         lookback_days: int = 30) -> Dict[str, Any]:
        """Build regression model to predict parameter drift"""
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available'}
        
        if parameter not in data.columns:
            return {'error': f'Parameter {parameter} not found in data'}
        
        # Prepare time series data
        param_data = data[parameter].dropna()
        if len(param_data) < lookback_days:
            return {'error': f'Not enough data points for {parameter} drift modeling'}
        
        # Create features (time-based and rolling statistics)
        timestamps = pd.to_datetime(param_data.index) if not isinstance(param_data.index, pd.DatetimeIndex) else param_data.index
        
        # Convert timestamps to numeric (days since start)
        time_numeric = (timestamps - timestamps.min()).days
        
        # Create feature matrix
        features = []
        targets = []
        
        window_size = min(7, lookback_days // 4)  # Use 7 days or 1/4 of lookback period
        
        for i in range(window_size, len(param_data)):
            # Time-based features
            time_features = [
                time_numeric[i],  # Days since start
                i % 7,  # Day of week pattern
                i % 24 if len(param_data) > 24 else 0,  # Hour pattern if enough data
            ]
            
            # Rolling statistics features
            window_data = param_data.iloc[i-window_size:i]
            rolling_features = [
                window_data.mean(),
                window_data.std(),
                window_data.min(),
                window_data.max(),
                window_data.iloc[-1] - window_data.iloc[0],  # Recent trend
            ]
            
            feature_vector = time_features + rolling_features
            features.append(feature_vector)
            targets.append(param_data.iloc[i])
        
        features = np.array(features)
        targets = np.array(targets)
        
        # Handle NaN values
        valid_indices = ~(np.isnan(features).any(axis=1) | np.isnan(targets))
        features = features[valid_indices]
        targets = targets[valid_indices]
        
        if len(features) < 10:
            return {'error': 'Not enough valid data points for modeling'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Ridge regression model (more robust than linear)
        model = Ridge(alpha=1.0)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Store model and metadata
        self.models[parameter] = model
        self.scalers[parameter] = scaler
        self.model_metadata[parameter] = {
            'train_score': train_score,
            'test_score': test_score,
            'rmse': rmse,
            'feature_count': features.shape[1],
            'training_samples': len(X_train),
            'created': datetime.now(),
            'window_size': window_size
        }
        
        return {
            'success': True,
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'rmse': rmse,
            'training_samples': len(X_train)
        }
    
    def predict_parameter_value(self, data: pd.DataFrame, parameter: str, 
                              hours_ahead: int = 24) -> Optional[PredictionResult]:
        """Predict parameter value for specified time ahead"""
        if not SKLEARN_AVAILABLE or parameter not in self.models:
            return None
        
        if parameter not in data.columns:
            return None
        
        param_data = data[parameter].dropna()
        if param_data.empty:
            return None
        
        try:
            model = self.models[parameter]
            scaler = self.scalers[parameter]
            metadata = self.model_metadata[parameter]
            
            # Get recent data for prediction features
            window_size = metadata['window_size']
            recent_data = param_data.iloc[-window_size:]
            
            # Create feature vector similar to training
            timestamps = pd.to_datetime(param_data.index) if not isinstance(param_data.index, pd.DatetimeIndex) else param_data.index
            time_numeric = (timestamps - timestamps.min()).days
            
            # Future time point
            last_time = time_numeric.iloc[-1]
            future_time = last_time + (hours_ahead / 24.0)
            
            # Time-based features for prediction
            time_features = [
                future_time,
                int(future_time) % 7,  # Day of week
                0,  # Hour pattern (simplified)
            ]
            
            # Rolling statistics from recent data
            rolling_features = [
                recent_data.mean(),
                recent_data.std(),
                recent_data.min(),
                recent_data.max(),
                recent_data.iloc[-1] - recent_data.iloc[0],
            ]
            
            feature_vector = np.array([time_features + rolling_features])
            
            # Handle NaN values
            if np.isnan(feature_vector).any():
                return None
            
            # Scale and predict
            feature_vector_scaled = scaler.transform(feature_vector)
            predicted_value = model.predict(feature_vector_scaled)[0]
            
            # Estimate confidence interval (simplified)
            rmse = metadata['rmse']
            confidence_level = 0.95
            margin = 1.96 * rmse  # 95% confidence interval approximation
            
            confidence_interval = (
                predicted_value - margin,
                predicted_value + margin
            )
            
            # Assess risk level
            recent_mean = recent_data.mean()
            deviation = abs(predicted_value - recent_mean) / recent_mean if recent_mean != 0 else 0
            
            if deviation > 0.2:
                risk_level = 'high'
            elif deviation > 0.1:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return PredictionResult(
                parameter=parameter,
                predicted_value=predicted_value,
                confidence_interval=confidence_interval,
                confidence_level=confidence_level,
                prediction_horizon=timedelta(hours=hours_ahead),
                model_accuracy=metadata['test_score'],
                risk_level=risk_level
            )
            
        except Exception as e:
            print(f"Error predicting {parameter}: {e}")
            return None
    
    def schedule_maintenance(self, predictions: List[PredictionResult], 
                           parameter_thresholds: Dict[str, Dict[str, float]]) -> List[Dict]:
        """Schedule maintenance based on predictions and thresholds"""
        maintenance_schedule = []
        
        for prediction in predictions:
            if prediction is None:
                continue
            
            param = prediction.parameter
            thresholds = parameter_thresholds.get(param, {})
            
            predicted_value = prediction.predicted_value
            risk_level = prediction.risk_level
            
            # Check against thresholds
            warning_threshold = thresholds.get('warning', float('inf'))
            critical_threshold = thresholds.get('critical', float('inf'))
            
            maintenance_priority = 'low'
            maintenance_reason = 'routine'
            
            if predicted_value > critical_threshold or risk_level == 'high':
                maintenance_priority = 'critical'
                maintenance_reason = f'Predicted {param} value ({predicted_value:.2f}) exceeds critical threshold'
            elif predicted_value > warning_threshold or risk_level == 'medium':
                maintenance_priority = 'medium'
                maintenance_reason = f'Predicted {param} value ({predicted_value:.2f}) approaching threshold'
            
            if maintenance_priority != 'low':
                # Calculate suggested maintenance date
                if maintenance_priority == 'critical':
                    days_ahead = 1  # Immediate
                elif maintenance_priority == 'medium':
                    days_ahead = 7  # Within a week
                else:
                    days_ahead = 30  # Routine monthly
                
                maintenance_date = datetime.now() + timedelta(days=days_ahead)
                
                maintenance_schedule.append({
                    'parameter': param,
                    'priority': maintenance_priority,
                    'reason': maintenance_reason,
                    'predicted_value': predicted_value,
                    'confidence': prediction.confidence_level,
                    'suggested_date': maintenance_date,
                    'risk_level': risk_level
                })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        maintenance_schedule.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return maintenance_schedule


class AnalyticsEngine:
    """Main analytics engine coordinating all analytics components"""
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self.anomaly_detector = AnomalyDetector()
        self.predictive_engine = PredictiveMaintenanceEngine()
        
        # Configuration
        self.config = {
            'anomaly_detection': {
                'contamination': 0.1,
                'zscore_threshold': 3.0,
                'iqr_multiplier': 1.5
            },
            'prediction': {
                'lookback_days': 30,
                'prediction_horizon_hours': 24
            },
            'maintenance': {
                'parameter_thresholds': {}
            }
        }
        
        # Model persistence
        self.models_dir = Path('analytics_models')
        self.models_dir.mkdir(exist_ok=True)
    
    def train_anomaly_models(self, data: pd.DataFrame, parameters: List[str] = None):
        """Train anomaly detection models for specified parameters"""
        if parameters is None:
            parameters = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
        
        results = {}
        
        for param in parameters:
            try:
                print(f"Training anomaly model for {param}...")
                self.anomaly_detector.fit(data, param)
                results[param] = {'status': 'success', 'model_trained': True}
            except Exception as e:
                print(f"Failed to train anomaly model for {param}: {e}")
                results[param] = {'status': 'failed', 'error': str(e)}
        
        return results
    
    def train_predictive_models(self, data: pd.DataFrame, parameters: List[str] = None):
        """Train predictive maintenance models"""
        if parameters is None:
            parameters = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
        
        results = {}
        
        for param in parameters:
            try:
                print(f"Training predictive model for {param}...")
                result = self.predictive_engine.build_drift_model(
                    data, param, 
                    lookback_days=self.config['prediction']['lookback_days']
                )
                results[param] = result
            except Exception as e:
                print(f"Failed to train predictive model for {param}: {e}")
                results[param] = {'error': str(e)}
        
        return results
    
    def detect_anomalies(self, data: pd.DataFrame, parameters: List[str] = None) -> List[AnomalyAlert]:
        """Detect anomalies in the provided data"""
        if parameters is None:
            parameters = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
        
        all_alerts = []
        
        for param in parameters:
            try:
                alerts = self.anomaly_detector.detect_anomalies(data, param)
                all_alerts.extend(alerts)
            except Exception as e:
                print(f"Error detecting anomalies for {param}: {e}")
        
        # Sort alerts by severity and timestamp
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_alerts.sort(key=lambda x: (severity_order.get(x.severity, 3), x.timestamp), reverse=True)
        
        return all_alerts
    
    def generate_predictions(self, data: pd.DataFrame, parameters: List[str] = None,
                           hours_ahead: int = None) -> List[PredictionResult]:
        """Generate predictions for parameters"""
        if parameters is None:
            parameters = list(self.predictive_engine.models.keys())
        
        if hours_ahead is None:
            hours_ahead = self.config['prediction']['prediction_horizon_hours']
        
        predictions = []
        
        for param in parameters:
            try:
                prediction = self.predictive_engine.predict_parameter_value(
                    data, param, hours_ahead
                )
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                print(f"Error generating prediction for {param}: {e}")
        
        return predictions
    
    def get_analytics_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive analytics summary"""
        summary = {
            'timestamp': datetime.now(),
            'data_period': {
                'start': data.index.min() if hasattr(data.index, 'min') else 'unknown',
                'end': data.index.max() if hasattr(data.index, 'max') else 'unknown',
                'record_count': len(data)
            },
            'anomaly_detection': {},
            'predictive_analysis': {},
            'maintenance_schedule': []
        }
        
        # Get numeric parameters
        numeric_params = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
        
        # Anomaly detection summary
        try:
            recent_data = data.tail(1000)  # Analyze recent 1000 records
            anomalies = self.detect_anomalies(recent_data, numeric_params)
            
            summary['anomaly_detection'] = {
                'total_anomalies': len(anomalies),
                'by_severity': {
                    severity: len([a for a in anomalies if a.severity == severity])
                    for severity in ['critical', 'high', 'medium', 'low']
                },
                'by_parameter': {
                    param: len([a for a in anomalies if a.parameter == param])
                    for param in numeric_params
                },
                'recent_alerts': [
                    {
                        'parameter': alert.parameter,
                        'severity': alert.severity,
                        'timestamp': alert.timestamp,
                        'description': alert.description
                    }
                    for alert in anomalies[:5]  # Top 5 recent alerts
                ]
            }
        except Exception as e:
            summary['anomaly_detection']['error'] = str(e)
        
        # Predictive analysis summary
        try:
            predictions = self.generate_predictions(data, numeric_params)
            
            summary['predictive_analysis'] = {
                'predictions_generated': len(predictions),
                'by_risk_level': {
                    risk: len([p for p in predictions if p.risk_level == risk])
                    for risk in ['high', 'medium', 'low']
                },
                'predictions': [
                    {
                        'parameter': pred.parameter,
                        'predicted_value': pred.predicted_value,
                        'risk_level': pred.risk_level,
                        'model_accuracy': pred.model_accuracy
                    }
                    for pred in predictions
                ]
            }
            
            # Generate maintenance schedule
            maintenance_schedule = self.predictive_engine.schedule_maintenance(
                predictions, self.config['maintenance']['parameter_thresholds']
            )
            summary['maintenance_schedule'] = maintenance_schedule
            
        except Exception as e:
            summary['predictive_analysis']['error'] = str(e)
        
        return summary
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            # Save anomaly models
            anomaly_models = {
                'models': self.anomaly_detector.models,
                'scalers': self.anomaly_detector.scalers
            }
            
            with open(self.models_dir / 'anomaly_models.pkl', 'wb') as f:
                pickle.dump(anomaly_models, f)
            
            # Save predictive models
            predictive_models = {
                'models': self.predictive_engine.models,
                'scalers': self.predictive_engine.scalers,
                'metadata': self.predictive_engine.model_metadata
            }
            
            with open(self.models_dir / 'predictive_models.pkl', 'wb') as f:
                pickle.dump(predictive_models, f)
            
            print(f"Models saved to {self.models_dir}")
            return True
            
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load anomaly models
            anomaly_path = self.models_dir / 'anomaly_models.pkl'
            if anomaly_path.exists():
                with open(anomaly_path, 'rb') as f:
                    anomaly_models = pickle.load(f)
                    self.anomaly_detector.models = anomaly_models['models']
                    self.anomaly_detector.scalers = anomaly_models['scalers']
                print("Anomaly detection models loaded")
            
            # Load predictive models
            predictive_path = self.models_dir / 'predictive_models.pkl'
            if predictive_path.exists():
                with open(predictive_path, 'rb') as f:
                    predictive_models = pickle.load(f)
                    self.predictive_engine.models = predictive_models['models']
                    self.predictive_engine.scalers = predictive_models['scalers']
                    self.predictive_engine.model_metadata = predictive_models['metadata']
                print("Predictive maintenance models loaded")
            
            return True
            
        except Exception as e:
            print(f"Error loading models: {e}")
            return False