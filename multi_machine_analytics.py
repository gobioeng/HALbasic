"""
Multi-Machine Analytics Module for HALbasic
Provides advanced analytics, comparison, and correlation analysis for multiple LINAC machines
Developer: gobioeng.com
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class MultiMachineAnalyzer:
    """Machine performance analyzer with ranking, outlier detection, and comparison capabilities"""
    
    def __init__(self, database_manager=None):
        """Initialize the multi-machine analyzer
        
        Args:
            database_manager: Database manager instance for data access
        """
        self.db = database_manager
        self.analysis_cache = {}
    
    def calculate_machine_rankings(self, data_dict: Dict[str, pd.DataFrame], parameters: List[str]) -> pd.DataFrame:
        """Calculate machine performance rankings based on multiple parameters
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            parameters: List of parameters to use for ranking
            
        Returns:
            DataFrame with machine rankings and scores
        """
        try:
            if not data_dict or not parameters:
                return pd.DataFrame()
            
            ranking_data = []
            
            for machine_id, machine_data in data_dict.items():
                if machine_data.empty:
                    continue
                
                machine_scores = {
                    'machine_id': machine_id,
                    'total_score': 0.0,
                    'data_quality_score': 0.0,
                    'completeness_score': 0.0,
                    'stability_score': 0.0,
                    'parameter_scores': {}
                }
                
                valid_parameters = 0
                total_parameter_score = 0.0
                
                for parameter in parameters:
                    # Filter data for this parameter
                    param_data = machine_data[
                        machine_data.get('parameter_type', machine_data.get('param', pd.Series())) == parameter
                    ]
                    
                    if param_data.empty:
                        continue
                    
                    # Calculate parameter-specific scores
                    param_score = self._calculate_parameter_score(param_data)
                    machine_scores['parameter_scores'][parameter] = param_score
                    total_parameter_score += param_score
                    valid_parameters += 1
                
                if valid_parameters > 0:
                    # Data quality score (based on completeness and validity)
                    machine_scores['data_quality_score'] = self._calculate_data_quality_score(machine_data)
                    
                    # Completeness score (based on parameter coverage)
                    machine_scores['completeness_score'] = valid_parameters / len(parameters)
                    
                    # Stability score (based on data consistency)
                    machine_scores['stability_score'] = self._calculate_stability_score(machine_data)
                    
                    # Total score (weighted combination)
                    machine_scores['total_score'] = (
                        0.4 * (total_parameter_score / valid_parameters) +
                        0.3 * machine_scores['data_quality_score'] +
                        0.2 * machine_scores['completeness_score'] +
                        0.1 * machine_scores['stability_score']
                    )
                
                ranking_data.append(machine_scores)
            
            # Convert to DataFrame and rank
            if ranking_data:
                rankings_df = pd.DataFrame(ranking_data)
                rankings_df = rankings_df.sort_values('total_score', ascending=False).reset_index(drop=True)
                rankings_df['rank'] = range(1, len(rankings_df) + 1)
                return rankings_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error calculating machine rankings: {e}")
            return pd.DataFrame()
    
    def detect_performance_outliers(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Detect machines with outlying performance patterns
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            
        Returns:
            Dictionary with outlier analysis results
        """
        try:
            outlier_analysis = {
                'outlier_machines': [],
                'normal_machines': [],
                'analysis_metrics': {},
                'recommendations': []
            }
            
            if not data_dict:
                return outlier_analysis
            
            # Calculate key metrics for each machine
            machine_metrics = {}
            for machine_id, machine_data in data_dict.items():
                if machine_data.empty:
                    continue
                
                metrics = self._calculate_machine_metrics(machine_data)
                machine_metrics[machine_id] = metrics
            
            if len(machine_metrics) < 2:
                outlier_analysis['recommendations'].append("Need at least 2 machines for outlier detection")
                return outlier_analysis
            
            # Detect outliers using statistical methods
            metrics_df = pd.DataFrame(machine_metrics).T
            
            for metric_name in ['record_count', 'parameter_diversity', 'avg_value_stability']:
                if metric_name in metrics_df.columns:
                    values = metrics_df[metric_name].dropna()
                    if len(values) > 2:
                        # Use IQR method for outlier detection
                        q1 = values.quantile(0.25)
                        q3 = values.quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        outliers = values[(values < lower_bound) | (values > upper_bound)]
                        
                        for machine_id in outliers.index:
                            if machine_id not in [m['machine_id'] for m in outlier_analysis['outlier_machines']]:
                                outlier_info = {
                                    'machine_id': machine_id,
                                    'outlier_metrics': [metric_name],
                                    'severity': 'moderate',
                                    'value': outliers[machine_id],
                                    'expected_range': f"{lower_bound:.2f} - {upper_bound:.2f}"
                                }
                                outlier_analysis['outlier_machines'].append(outlier_info)
                            else:
                                # Machine already flagged, add this metric
                                for outlier_info in outlier_analysis['outlier_machines']:
                                    if outlier_info['machine_id'] == machine_id:
                                        outlier_info['outlier_metrics'].append(metric_name)
                                        break
            
            # Identify normal machines
            outlier_machine_ids = [m['machine_id'] for m in outlier_analysis['outlier_machines']]
            outlier_analysis['normal_machines'] = [
                machine_id for machine_id in machine_metrics.keys() 
                if machine_id not in outlier_machine_ids
            ]
            
            # Generate recommendations
            if outlier_analysis['outlier_machines']:
                outlier_analysis['recommendations'].append(
                    f"Found {len(outlier_analysis['outlier_machines'])} machines with outlying performance"
                )
                outlier_analysis['recommendations'].append(
                    "Review data collection and machine maintenance for flagged machines"
                )
            else:
                outlier_analysis['recommendations'].append("All machines show normal performance patterns")
            
            outlier_analysis['analysis_metrics'] = {
                'total_machines_analyzed': len(machine_metrics),
                'outlier_percentage': len(outlier_analysis['outlier_machines']) / len(machine_metrics) * 100,
                'metrics_analyzed': list(metrics_df.columns)
            }
            
            return outlier_analysis
            
        except Exception as e:
            print(f"Error detecting performance outliers: {e}")
            return {'error': str(e)}
    
    def generate_machine_comparison_report(self, machine1: str, machine2: str, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate comprehensive comparison report between two machines
        
        Args:
            machine1: First machine ID
            machine2: Second machine ID
            data_dict: Dictionary mapping machine IDs to their data
            
        Returns:
            Dictionary with detailed comparison report
        """
        try:
            report = {
                'machines': {'machine1': machine1, 'machine2': machine2},
                'data_summary': {},
                'parameter_comparison': {},
                'statistical_analysis': {},
                'recommendations': [],
                'correlation_analysis': {}
            }
            
            machine1_data = data_dict.get(machine1, pd.DataFrame())
            machine2_data = data_dict.get(machine2, pd.DataFrame())
            
            if machine1_data.empty or machine2_data.empty:
                report['recommendations'].append("Insufficient data for one or both machines")
                return report
            
            # Data summary comparison
            report['data_summary'] = {
                'machine1': self._get_data_summary(machine1_data),
                'machine2': self._get_data_summary(machine2_data)
            }
            
            # Parameter-by-parameter comparison
            param_col = 'parameter_type' if 'parameter_type' in machine1_data.columns else 'param'
            common_parameters = set(machine1_data[param_col].unique()) & set(machine2_data[param_col].unique())
            
            for parameter in common_parameters:
                param_comparison = self._compare_parameter_between_machines(
                    machine1_data[machine1_data[param_col] == parameter],
                    machine2_data[machine2_data[param_col] == parameter],
                    parameter
                )
                report['parameter_comparison'][parameter] = param_comparison
            
            # Statistical analysis
            report['statistical_analysis'] = self._perform_statistical_analysis(
                machine1_data, machine2_data
            )
            
            # Correlation analysis
            report['correlation_analysis'] = self._analyze_machine_correlation(
                machine1_data, machine2_data, common_parameters
            )
            
            # Generate recommendations
            report['recommendations'] = self._generate_comparison_recommendations(report)
            
            return report
            
        except Exception as e:
            print(f"Error generating comparison report: {e}")
            return {'error': str(e)}
    
    def calculate_fleet_statistics(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate comprehensive fleet-wide statistics
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            
        Returns:
            Dictionary with fleet statistics
        """
        try:
            fleet_stats = {
                'fleet_summary': {},
                'machine_contributions': {},
                'parameter_coverage': {},
                'temporal_analysis': {},
                'quality_metrics': {}
            }
            
            if not data_dict:
                return fleet_stats
            
            # Fleet summary
            total_records = sum(len(df) for df in data_dict.values())
            active_machines = sum(1 for df in data_dict.values() if not df.empty)
            
            fleet_stats['fleet_summary'] = {
                'total_machines': len(data_dict),
                'active_machines': active_machines,
                'inactive_machines': len(data_dict) - active_machines,
                'total_records': total_records,
                'average_records_per_machine': total_records / active_machines if active_machines > 0 else 0
            }
            
            # Machine contributions
            for machine_id, machine_data in data_dict.items():
                if not machine_data.empty:
                    contribution = len(machine_data) / total_records * 100 if total_records > 0 else 0
                    fleet_stats['machine_contributions'][machine_id] = {
                        'record_count': len(machine_data),
                        'fleet_contribution_percent': contribution,
                        'parameters_monitored': len(machine_data.get('parameter_type', machine_data.get('param', pd.Series())).unique())
                    }
            
            # Parameter coverage analysis
            all_parameters = set()
            machine_parameters = {}
            
            for machine_id, machine_data in data_dict.items():
                if not machine_data.empty:
                    param_col = 'parameter_type' if 'parameter_type' in machine_data.columns else 'param'
                    machine_params = set(machine_data[param_col].unique())
                    machine_parameters[machine_id] = machine_params
                    all_parameters.update(machine_params)
            
            fleet_stats['parameter_coverage'] = {
                'total_parameters': len(all_parameters),
                'parameters_list': list(all_parameters),
                'coverage_by_machine': {}
            }
            
            for machine_id, params in machine_parameters.items():
                coverage = len(params) / len(all_parameters) * 100 if all_parameters else 0
                fleet_stats['parameter_coverage']['coverage_by_machine'][machine_id] = {
                    'parameters_count': len(params),
                    'coverage_percent': coverage,
                    'missing_parameters': list(all_parameters - params)
                }
            
            # Temporal analysis
            fleet_stats['temporal_analysis'] = self._analyze_fleet_temporal_patterns(data_dict)
            
            # Quality metrics
            fleet_stats['quality_metrics'] = self._calculate_fleet_quality_metrics(data_dict)
            
            return fleet_stats
            
        except Exception as e:
            print(f"Error calculating fleet statistics: {e}")
            return {'error': str(e)}
    
    def _calculate_parameter_score(self, param_data: pd.DataFrame) -> float:
        """Calculate a quality score for a parameter's data"""
        try:
            if param_data.empty:
                return 0.0
            
            score = 0.0
            
            # Data completeness (non-null values)
            if 'value' in param_data.columns:
                completeness = param_data['value'].notna().sum() / len(param_data)
                score += 0.3 * completeness
            
            # Data consistency (low coefficient of variation)
            if 'value' in param_data.columns:
                values = param_data['value'].dropna()
                if len(values) > 1 and values.std() > 0:
                    cv = values.std() / abs(values.mean()) if values.mean() != 0 else 1
                    consistency = max(0, 1 - min(cv, 1))  # Cap CV at 1 for scoring
                    score += 0.4 * consistency
                else:
                    score += 0.2  # Some points for having data, less for no variation
            
            # Data volume (more data points = higher score)
            volume_score = min(len(param_data) / 1000, 1.0)  # Cap at 1000 records
            score += 0.3 * volume_score
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.0
    
    def _calculate_data_quality_score(self, machine_data: pd.DataFrame) -> float:
        """Calculate overall data quality score for a machine"""
        try:
            if machine_data.empty:
                return 0.0
            
            score = 0.0
            
            # Missing data ratio
            total_cells = machine_data.size
            non_null_cells = machine_data.count().sum()
            completeness = non_null_cells / total_cells if total_cells > 0 else 0
            score += 0.5 * completeness
            
            # Data freshness (if datetime column exists)
            if 'datetime' in machine_data.columns:
                try:
                    latest_date = pd.to_datetime(machine_data['datetime']).max()
                    days_old = (pd.Timestamp.now() - latest_date).days
                    freshness = max(0, 1 - days_old / 30)  # Decay over 30 days
                    score += 0.3 * freshness
                except:
                    score += 0.1  # Some credit for having datetime column
            
            # Parameter diversity
            param_col = 'parameter_type' if 'parameter_type' in machine_data.columns else 'param'
            if param_col in machine_data.columns:
                unique_params = machine_data[param_col].nunique()
                diversity = min(unique_params / 20, 1.0)  # Normalize to 20 parameters
                score += 0.2 * diversity
            
            return min(score, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_stability_score(self, machine_data: pd.DataFrame) -> float:
        """Calculate stability score based on data consistency over time"""
        try:
            if machine_data.empty or 'datetime' not in machine_data.columns:
                return 0.5  # Neutral score if no temporal data
            
            # Check for consistent data collection over time
            try:
                machine_data['datetime'] = pd.to_datetime(machine_data['datetime'])
                machine_data = machine_data.sort_values('datetime')
                
                # Calculate gaps in data collection
                time_diffs = machine_data['datetime'].diff().dropna()
                if len(time_diffs) > 0:
                    median_gap = time_diffs.median()
                    gap_consistency = 1 - (time_diffs.std() / median_gap if median_gap.total_seconds() > 0 else 1)
                    return max(0, min(gap_consistency, 1.0))
                
            except:
                pass
            
            return 0.5  # Default neutral score
            
        except Exception:
            return 0.5
    
    def _calculate_machine_metrics(self, machine_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate key metrics for outlier detection"""
        try:
            metrics = {}
            
            # Basic metrics
            metrics['record_count'] = len(machine_data)
            
            # Parameter diversity
            param_col = 'parameter_type' if 'parameter_type' in machine_data.columns else 'param'
            if param_col in machine_data.columns:
                metrics['parameter_diversity'] = machine_data[param_col].nunique()
            
            # Value stability (coefficient of variation)
            if 'value' in machine_data.columns:
                values = machine_data['value'].dropna()
                if len(values) > 1 and values.mean() != 0:
                    cv = values.std() / abs(values.mean())
                    metrics['avg_value_stability'] = 1 / (1 + cv)  # Higher is more stable
                else:
                    metrics['avg_value_stability'] = 0.5
            
            # Data completeness
            total_cells = machine_data.size
            non_null_cells = machine_data.count().sum()
            metrics['data_completeness'] = non_null_cells / total_cells if total_cells > 0 else 0
            
            return metrics
            
        except Exception:
            return {'record_count': 0, 'parameter_diversity': 0, 'avg_value_stability': 0, 'data_completeness': 0}
    
    def _get_data_summary(self, machine_data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary information for machine data"""
        try:
            summary = {
                'total_records': len(machine_data),
                'date_range': {},
                'parameters': {},
                'data_quality': {}
            }
            
            # Date range
            if 'datetime' in machine_data.columns:
                try:
                    machine_data['datetime'] = pd.to_datetime(machine_data['datetime'])
                    summary['date_range'] = {
                        'start': machine_data['datetime'].min().strftime('%Y-%m-%d %H:%M:%S'),
                        'end': machine_data['datetime'].max().strftime('%Y-%m-%d %H:%M:%S'),
                        'span_days': (machine_data['datetime'].max() - machine_data['datetime'].min()).days
                    }
                except:
                    pass
            
            # Parameters
            param_col = 'parameter_type' if 'parameter_type' in machine_data.columns else 'param'
            if param_col in machine_data.columns:
                summary['parameters'] = {
                    'total_unique': machine_data[param_col].nunique(),
                    'parameters_list': list(machine_data[param_col].unique())
                }
            
            # Data quality
            summary['data_quality'] = {
                'completeness': machine_data.count().sum() / machine_data.size if machine_data.size > 0 else 0,
                'missing_values': machine_data.isnull().sum().sum()
            }
            
            return summary
            
        except Exception:
            return {}
    
    def _compare_parameter_between_machines(self, data1: pd.DataFrame, data2: pd.DataFrame, parameter: str) -> Dict[str, Any]:
        """Compare a specific parameter between two machines"""
        try:
            comparison = {
                'parameter': parameter,
                'machine1_stats': {},
                'machine2_stats': {},
                'difference_analysis': {},
                'statistical_tests': {}
            }
            
            # Get value data for both machines
            values1 = data1['value'].dropna() if 'value' in data1.columns else pd.Series()
            values2 = data2['value'].dropna() if 'value' in data2.columns else pd.Series()
            
            if len(values1) == 0 or len(values2) == 0:
                comparison['difference_analysis']['note'] = 'Insufficient data for comparison'
                return comparison
            
            # Calculate statistics
            comparison['machine1_stats'] = {
                'mean': values1.mean(),
                'std': values1.std(),
                'min': values1.min(),
                'max': values1.max(),
                'count': len(values1)
            }
            
            comparison['machine2_stats'] = {
                'mean': values2.mean(),
                'std': values2.std(),
                'min': values2.min(),
                'max': values2.max(),
                'count': len(values2)
            }
            
            # Difference analysis
            comparison['difference_analysis'] = {
                'mean_difference': comparison['machine1_stats']['mean'] - comparison['machine2_stats']['mean'],
                'mean_difference_percent': ((comparison['machine1_stats']['mean'] - comparison['machine2_stats']['mean']) / 
                                          comparison['machine2_stats']['mean'] * 100) if comparison['machine2_stats']['mean'] != 0 else 0,
                'std_difference': comparison['machine1_stats']['std'] - comparison['machine2_stats']['std']
            }
            
            # Statistical tests
            try:
                # T-test for means
                t_stat, t_pvalue = stats.ttest_ind(values1, values2)
                comparison['statistical_tests']['t_test'] = {
                    'statistic': t_stat,
                    'p_value': t_pvalue,
                    'significant': t_pvalue < 0.05
                }
                
                # F-test for variances (using Levene's test as it's more robust)
                f_stat, f_pvalue = stats.levene(values1, values2)
                comparison['statistical_tests']['variance_test'] = {
                    'statistic': f_stat,
                    'p_value': f_pvalue,
                    'significant': f_pvalue < 0.05
                }
                
            except Exception as e:
                comparison['statistical_tests']['error'] = str(e)
            
            return comparison
            
        except Exception as e:
            return {'parameter': parameter, 'error': str(e)}
    
    def _perform_statistical_analysis(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis between two machines"""
        try:
            analysis = {
                'overall_similarity': {},
                'distribution_comparison': {},
                'temporal_analysis': {}
            }
            
            # Overall similarity (based on multiple factors)
            similarity_score = 0.0
            similarity_factors = 0
            
            # Record count similarity
            count1, count2 = len(data1), len(data2)
            if count1 > 0 and count2 > 0:
                count_similarity = 1 - abs(count1 - count2) / max(count1, count2)
                similarity_score += count_similarity
                similarity_factors += 1
            
            # Parameter coverage similarity
            param_col = 'parameter_type' if 'parameter_type' in data1.columns else 'param'
            if param_col in data1.columns and param_col in data2.columns:
                params1 = set(data1[param_col].unique())
                params2 = set(data2[param_col].unique())
                if params1 or params2:
                    jaccard_similarity = len(params1 & params2) / len(params1 | params2)
                    similarity_score += jaccard_similarity
                    similarity_factors += 1
            
            analysis['overall_similarity'] = {
                'similarity_score': similarity_score / similarity_factors if similarity_factors > 0 else 0,
                'factors_analyzed': similarity_factors
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_machine_correlation(self, data1: pd.DataFrame, data2: pd.DataFrame, common_parameters: set) -> Dict[str, Any]:
        """Analyze correlation patterns between two machines"""
        try:
            correlation_analysis = {
                'parameter_correlations': {},
                'overall_correlation': None,
                'correlation_strength': 'unknown'
            }
            
            correlations = []
            
            for parameter in common_parameters:
                param_col = 'parameter_type' if 'parameter_type' in data1.columns else 'param'
                
                # Get parameter data for both machines
                param_data1 = data1[data1[param_col] == parameter]['value'].dropna()
                param_data2 = data2[data2[param_col] == parameter]['value'].dropna()
                
                if len(param_data1) > 1 and len(param_data2) > 1:
                    # Align data by taking minimum length
                    min_len = min(len(param_data1), len(param_data2))
                    
                    try:
                        correlation = param_data1.iloc[:min_len].corr(param_data2.iloc[:min_len])
                        if not np.isnan(correlation):
                            correlation_analysis['parameter_correlations'][parameter] = correlation
                            correlations.append(correlation)
                    except:
                        pass
            
            # Overall correlation
            if correlations:
                correlation_analysis['overall_correlation'] = np.mean(correlations)
                
                # Determine correlation strength
                avg_corr = abs(correlation_analysis['overall_correlation'])
                if avg_corr > 0.8:
                    correlation_analysis['correlation_strength'] = 'very_strong'
                elif avg_corr > 0.6:
                    correlation_analysis['correlation_strength'] = 'strong'
                elif avg_corr > 0.4:
                    correlation_analysis['correlation_strength'] = 'moderate'
                elif avg_corr > 0.2:
                    correlation_analysis['correlation_strength'] = 'weak'
                else:
                    correlation_analysis['correlation_strength'] = 'very_weak'
            
            return correlation_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_comparison_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison report"""
        recommendations = []
        
        try:
            # Check data volume differences
            machine1_summary = report.get('data_summary', {}).get('machine1', {})
            machine2_summary = report.get('data_summary', {}).get('machine2', {})
            
            records1 = machine1_summary.get('total_records', 0)
            records2 = machine2_summary.get('total_records', 0)
            
            if records1 > 0 and records2 > 0:
                ratio = max(records1, records2) / min(records1, records2)
                if ratio > 2:
                    recommendations.append(
                        f"Significant data volume imbalance detected (ratio: {ratio:.1f}:1). "
                        f"Review data collection consistency between machines."
                    )
            
            # Check correlation strength
            correlation_analysis = report.get('correlation_analysis', {})
            correlation_strength = correlation_analysis.get('correlation_strength', 'unknown')
            
            if correlation_strength == 'very_weak':
                recommendations.append(
                    "Very weak correlation between machines detected. "
                    "Investigate potential differences in operating conditions or maintenance."
                )
            elif correlation_strength == 'very_strong':
                recommendations.append(
                    "Very strong correlation detected. Machines show similar performance patterns."
                )
            
            # Check parameter coverage
            params1 = machine1_summary.get('parameters', {}).get('total_unique', 0)
            params2 = machine2_summary.get('parameters', {}).get('total_unique', 0)
            
            if abs(params1 - params2) > 3:
                recommendations.append(
                    f"Parameter coverage difference detected ({params1} vs {params2}). "
                    f"Ensure consistent monitoring setup across machines."
                )
            
            if not recommendations:
                recommendations.append("No major issues identified in machine comparison.")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _analyze_fleet_temporal_patterns(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze temporal patterns across the fleet"""
        try:
            temporal_analysis = {
                'data_collection_patterns': {},
                'peak_activity_times': {},
                'data_gaps': {}
            }
            
            all_timestamps = []
            machine_timestamps = {}
            
            # Collect timestamps from all machines
            for machine_id, machine_data in data_dict.items():
                if not machine_data.empty and 'datetime' in machine_data.columns:
                    try:
                        timestamps = pd.to_datetime(machine_data['datetime'])
                        machine_timestamps[machine_id] = timestamps
                        all_timestamps.extend(timestamps.tolist())
                    except:
                        continue
            
            if all_timestamps:
                all_timestamps = pd.to_datetime(all_timestamps)
                
                # Peak activity analysis
                hourly_counts = all_timestamps.groupby(all_timestamps.dt.hour).size()
                peak_hour = hourly_counts.idxmax()
                
                temporal_analysis['peak_activity_times'] = {
                    'peak_hour': int(peak_hour),
                    'hourly_distribution': hourly_counts.to_dict()
                }
                
                # Data collection patterns
                daily_counts = all_timestamps.groupby(all_timestamps.dt.date).size()
                temporal_analysis['data_collection_patterns'] = {
                    'avg_daily_records': daily_counts.mean(),
                    'most_active_day': str(daily_counts.idxmax()),
                    'least_active_day': str(daily_counts.idxmin())
                }
            
            return temporal_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_fleet_quality_metrics(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate fleet-wide quality metrics"""
        try:
            quality_metrics = {
                'overall_completeness': 0.0,
                'machine_quality_scores': {},
                'fleet_grade': 'F'
            }
            
            total_completeness = 0.0
            valid_machines = 0
            
            for machine_id, machine_data in data_dict.items():
                if not machine_data.empty:
                    # Calculate machine-specific quality score
                    completeness = machine_data.count().sum() / machine_data.size if machine_data.size > 0 else 0
                    quality_metrics['machine_quality_scores'][machine_id] = completeness
                    total_completeness += completeness
                    valid_machines += 1
            
            if valid_machines > 0:
                quality_metrics['overall_completeness'] = total_completeness / valid_machines
                
                # Assign fleet grade
                completeness = quality_metrics['overall_completeness']
                if completeness >= 0.95:
                    quality_metrics['fleet_grade'] = 'A'
                elif completeness >= 0.90:
                    quality_metrics['fleet_grade'] = 'B'
                elif completeness >= 0.80:
                    quality_metrics['fleet_grade'] = 'C'
                elif completeness >= 0.70:
                    quality_metrics['fleet_grade'] = 'D'
                else:
                    quality_metrics['fleet_grade'] = 'F'
            
            return quality_metrics
            
        except Exception as e:
            return {'error': str(e)}


# Cross-machine parameter correlation detection
class CorrelationAnalyzer:
    """Analyzer for cross-machine parameter correlations and pattern detection"""
    
    def __init__(self):
        self.correlation_cache = {}
    
    def detect_parameter_correlations(self, data_dict: Dict[str, pd.DataFrame], min_correlation: float = 0.5) -> Dict[str, Any]:
        """Detect correlations between parameters across machines
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            min_correlation: Minimum correlation threshold
            
        Returns:
            Dictionary with correlation analysis results
        """
        try:
            correlation_results = {
                'strong_correlations': [],
                'cross_machine_correlations': {},
                'parameter_networks': {},
                'insights': []
            }
            
            # Identify common parameters across machines
            common_parameters = None
            for machine_data in data_dict.values():
                if not machine_data.empty:
                    param_col = 'parameter_type' if 'parameter_type' in machine_data.columns else 'param'
                    if param_col in machine_data.columns:
                        machine_params = set(machine_data[param_col].unique())
                        if common_parameters is None:
                            common_parameters = machine_params
                        else:
                            common_parameters &= machine_params
            
            if not common_parameters:
                correlation_results['insights'].append("No common parameters found across machines")
                return correlation_results
            
            # Analyze correlations for each parameter
            for parameter in common_parameters:
                param_correlations = self._analyze_parameter_correlations(
                    data_dict, parameter, min_correlation
                )
                if param_correlations['correlations']:
                    correlation_results['cross_machine_correlations'][parameter] = param_correlations
            
            # Identify machines with similar performance patterns
            similar_machines = self._identify_similar_machines(data_dict, common_parameters)
            correlation_results['parameter_networks'] = similar_machines
            
            # Generate insights
            correlation_results['insights'] = self._generate_correlation_insights(correlation_results)
            
            return correlation_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def identify_machines_deviating_from_fleet(self, data_dict: Dict[str, pd.DataFrame], deviation_threshold: float = 2.0) -> Dict[str, Any]:
        """Identify machines that deviate significantly from fleet average
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            deviation_threshold: Number of standard deviations for flagging
            
        Returns:
            Dictionary with deviation analysis results
        """
        try:
            deviation_results = {
                'deviating_machines': {},
                'fleet_statistics': {},
                'recommendations': []
            }
            
            # Calculate fleet statistics for each parameter
            param_col = 'parameter_type'
            all_parameters = set()
            
            # Collect all parameters
            for machine_data in data_dict.values():
                if not machine_data.empty:
                    if param_col not in machine_data.columns:
                        param_col = 'param'
                    if param_col in machine_data.columns:
                        all_parameters.update(machine_data[param_col].unique())
            
            # Analyze deviation for each parameter
            for parameter in all_parameters:
                fleet_values = []
                machine_means = {}
                
                # Collect parameter values from all machines
                for machine_id, machine_data in data_dict.items():
                    if not machine_data.empty and param_col in machine_data.columns:
                        param_data = machine_data[machine_data[param_col] == parameter]['value'].dropna()
                        if not param_data.empty:
                            machine_mean = param_data.mean()
                            machine_means[machine_id] = machine_mean
                            fleet_values.extend(param_data.tolist())
                
                if len(fleet_values) > 1 and len(machine_means) > 1:
                    fleet_mean = np.mean(fleet_values)
                    fleet_std = np.std(fleet_values)
                    
                    deviation_results['fleet_statistics'][parameter] = {
                        'mean': fleet_mean,
                        'std': fleet_std,
                        'machine_means': machine_means
                    }
                    
                    # Check for deviating machines
                    for machine_id, machine_mean in machine_means.items():
                        if fleet_std > 0:
                            z_score = abs(machine_mean - fleet_mean) / fleet_std
                            if z_score > deviation_threshold:
                                if machine_id not in deviation_results['deviating_machines']:
                                    deviation_results['deviating_machines'][machine_id] = []
                                
                                deviation_results['deviating_machines'][machine_id].append({
                                    'parameter': parameter,
                                    'z_score': z_score,
                                    'machine_value': machine_mean,
                                    'fleet_mean': fleet_mean,
                                    'deviation_severity': 'high' if z_score > 3 else 'moderate'
                                })
            
            # Generate recommendations
            deviation_results['recommendations'] = self._generate_deviation_recommendations(deviation_results)
            
            return deviation_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_parameter_correlations(self, data_dict: Dict[str, pd.DataFrame], parameter: str, min_correlation: float) -> Dict[str, Any]:
        """Analyze correlations for a specific parameter across machines"""
        try:
            param_analysis = {
                'parameter': parameter,
                'correlations': {},
                'summary_stats': {}
            }
            
            # Extract parameter data for each machine
            machine_data = {}
            param_col = 'parameter_type'
            
            for machine_id, df in data_dict.items():
                if not df.empty:
                    if param_col not in df.columns:
                        param_col = 'param'
                    
                    if param_col in df.columns:
                        param_data = df[df[param_col] == parameter]['value'].dropna()
                        if not param_data.empty:
                            machine_data[machine_id] = param_data
            
            # Calculate pairwise correlations
            machine_ids = list(machine_data.keys())
            for i in range(len(machine_ids)):
                for j in range(i + 1, len(machine_ids)):
                    machine1, machine2 = machine_ids[i], machine_ids[j]
                    
                    data1 = machine_data[machine1]
                    data2 = machine_data[machine2]
                    
                    # Align data by taking minimum length
                    min_len = min(len(data1), len(data2))
                    if min_len > 1:
                        try:
                            correlation = data1.iloc[:min_len].corr(data2.iloc[:min_len])
                            if not np.isnan(correlation) and abs(correlation) >= min_correlation:
                                pair_key = f"{machine1}_vs_{machine2}"
                                param_analysis['correlations'][pair_key] = {
                                    'correlation': correlation,
                                    'strength': self._get_correlation_strength(abs(correlation)),
                                    'sample_size': min_len
                                }
                        except:
                            continue
            
            return param_analysis
            
        except Exception:
            return {'parameter': parameter, 'correlations': {}, 'summary_stats': {}}
    
    def _identify_similar_machines(self, data_dict: Dict[str, pd.DataFrame], common_parameters: set) -> Dict[str, Any]:
        """Identify machines with similar performance patterns"""
        try:
            similarity_results = {
                'machine_clusters': {},
                'similarity_matrix': {},
                'most_similar_pairs': []
            }
            
            machine_ids = list(data_dict.keys())
            similarity_scores = {}
            
            # Calculate pairwise similarity scores
            for i in range(len(machine_ids)):
                for j in range(i + 1, len(machine_ids)):
                    machine1, machine2 = machine_ids[i], machine_ids[j]
                    
                    similarity = self._calculate_machine_similarity(
                        data_dict[machine1], data_dict[machine2], common_parameters
                    )
                    
                    pair_key = f"{machine1}_vs_{machine2}"
                    similarity_scores[pair_key] = similarity
                    
                    if similarity > 0.7:  # High similarity threshold
                        similarity_results['most_similar_pairs'].append({
                            'machines': [machine1, machine2],
                            'similarity_score': similarity
                        })
            
            similarity_results['similarity_matrix'] = similarity_scores
            
            return similarity_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_machine_similarity(self, data1: pd.DataFrame, data2: pd.DataFrame, common_parameters: set) -> float:
        """Calculate similarity score between two machines"""
        try:
            if data1.empty or data2.empty:
                return 0.0
            
            param_col = 'parameter_type' if 'parameter_type' in data1.columns else 'param'
            correlations = []
            
            for parameter in common_parameters:
                # Get parameter data for both machines
                param_data1 = data1[data1[param_col] == parameter]['value'].dropna()
                param_data2 = data2[data2[param_col] == parameter]['value'].dropna()
                
                if len(param_data1) > 1 and len(param_data2) > 1:
                    min_len = min(len(param_data1), len(param_data2))
                    try:
                        correlation = param_data1.iloc[:min_len].corr(param_data2.iloc[:min_len])
                        if not np.isnan(correlation):
                            correlations.append(abs(correlation))
                    except:
                        continue
            
            return np.mean(correlations) if correlations else 0.0
            
        except Exception:
            return 0.0
    
    def _get_correlation_strength(self, correlation: float) -> str:
        """Get correlation strength description"""
        if correlation >= 0.9:
            return 'very_strong'
        elif correlation >= 0.7:
            return 'strong'
        elif correlation >= 0.5:
            return 'moderate'
        elif correlation >= 0.3:
            return 'weak'
        else:
            return 'very_weak'
    
    def _generate_correlation_insights(self, correlation_results: Dict[str, Any]) -> List[str]:
        """Generate insights from correlation analysis"""
        insights = []
        
        try:
            # Count strong correlations
            strong_count = 0
            for param_data in correlation_results['cross_machine_correlations'].values():
                for corr_data in param_data['correlations'].values():
                    if corr_data['strength'] in ['strong', 'very_strong']:
                        strong_count += 1
            
            if strong_count > 0:
                insights.append(f"Found {strong_count} strong cross-machine correlations")
            else:
                insights.append("No strong correlations detected between machines")
            
            # Analyze similar machine pairs
            similar_pairs = correlation_results['parameter_networks'].get('most_similar_pairs', [])
            if similar_pairs:
                insights.append(f"Identified {len(similar_pairs)} pairs of highly similar machines")
                
                # Mention the most similar pair
                best_pair = max(similar_pairs, key=lambda x: x['similarity_score'])
                insights.append(
                    f"Most similar machines: {' and '.join(best_pair['machines'])} "
                    f"(similarity: {best_pair['similarity_score']:.3f})"
                )
            else:
                insights.append("No highly similar machine pairs detected")
                
        except Exception:
            insights.append("Error generating correlation insights")
        
        return insights
    
    def _generate_deviation_recommendations(self, deviation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on deviation analysis"""
        recommendations = []
        
        try:
            deviating_machines = deviation_results.get('deviating_machines', {})
            
            if not deviating_machines:
                recommendations.append("All machines operating within normal fleet parameters")
                return recommendations
            
            for machine_id, deviations in deviating_machines.items():
                high_severity_count = sum(1 for d in deviations if d['deviation_severity'] == 'high')
                
                if high_severity_count > 0:
                    recommendations.append(
                        f"Machine {machine_id}: {high_severity_count} parameters showing high deviation - "
                        f"immediate investigation recommended"
                    )
                else:
                    recommendations.append(
                        f"Machine {machine_id}: {len(deviations)} parameters showing moderate deviation - "
                        f"monitor closely"
                    )
            
            # General recommendations
            if len(deviating_machines) > len(deviation_results.get('fleet_statistics', {})) * 0.3:
                recommendations.append(
                    "High proportion of machines showing deviations - review fleet-wide processes"
                )
                
        except Exception:
            recommendations.append("Error generating deviation recommendations")
        
        return recommendations