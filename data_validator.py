"""
Data Validator for HALog Application
Provides real-time validation during data import with comprehensive checks

This validator ensures data quality by checking:
- Parameter values within expected ranges
- Timestamp sequences and realism
- Duplicate detection within time windows
- Data completeness scoring

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import re
import logging

# Configure logging for validation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validator for LINAC log data with real-time validation capabilities
    """

    def __init__(self, parameter_mapping: Dict = None):
        """
        Initialize validator with parameter ranges and validation settings
        
        Args:
            parameter_mapping: Dictionary of parameter configurations from unified_parser
        """
        self.parameter_mapping = parameter_mapping or {}
        self.validation_results = {
            'data_quality_score': 0.0,
            'anomalies_detected': 0,
            'validation_warnings': [],
            'validation_errors': [],
            'parameter_validations': {},
            'timestamp_issues': [],
            'duplicate_count': 0,
            'completeness_score': 0.0,
            'records_processed': 0,
            'records_passed': 0,
            'records_failed': 0
        }
        
        # Validation settings
        self.duplicate_time_window = timedelta(seconds=30)  # 30 second window for duplicates
        self.max_timestamp_gap = timedelta(hours=24)  # Max gap between timestamps
        self.min_timestamp = datetime(2020, 1, 1)  # Minimum realistic timestamp
        self.max_timestamp = datetime(2030, 12, 31)  # Maximum realistic timestamp
        
        # Cache for performance optimization
        self._validation_cache = {}
        self._last_timestamps = {}  # Track last timestamp per parameter/serial
        self._duplicate_tracking = {}  # Track recent entries for duplicate detection

    def validate_chunk(self, chunk_df: pd.DataFrame, chunk_number: int = 0) -> Dict:
        """
        Validate a chunk of data during processing
        
        Args:
            chunk_df: DataFrame chunk to validate
            chunk_number: Sequential chunk number for tracking
            
        Returns:
            Dictionary with validation results for this chunk
        """
        if chunk_df.empty:
            return self._get_empty_validation_result()
        
        chunk_results = {
            'chunk_number': chunk_number,
            'records_in_chunk': len(chunk_df),
            'chunk_quality_score': 0.0,
            'chunk_anomalies': 0,
            'chunk_warnings': [],
            'chunk_errors': [],
            'parameter_results': {},
            'timestamp_results': {},
            'duplicate_results': {}
        }
        
        try:
            # Validate each aspect of the chunk
            param_results = self._validate_parameter_ranges(chunk_df)
            timestamp_results = self._validate_timestamps(chunk_df)
            duplicate_results = self._validate_duplicates(chunk_df)
            completeness_results = self._validate_completeness(chunk_df)
            
            # Combine results
            chunk_results['parameter_results'] = param_results
            chunk_results['timestamp_results'] = timestamp_results
            chunk_results['duplicate_results'] = duplicate_results
            chunk_results['completeness_results'] = completeness_results
            
            # Calculate chunk quality score (0-100%)
            quality_scores = [
                param_results.get('parameter_quality_score', 0),
                timestamp_results.get('timestamp_quality_score', 0),
                duplicate_results.get('duplicate_quality_score', 0),
                completeness_results.get('completeness_score', 0)
            ]
            chunk_results['chunk_quality_score'] = sum(quality_scores) / len(quality_scores)
            
            # Count anomalies
            chunk_results['chunk_anomalies'] = (
                param_results.get('parameter_anomalies', 0) +
                timestamp_results.get('timestamp_anomalies', 0) +
                duplicate_results.get('duplicate_count', 0)
            )
            
            # Collect warnings
            chunk_results['chunk_warnings'].extend(param_results.get('warnings', []))
            chunk_results['chunk_warnings'].extend(timestamp_results.get('warnings', []))
            chunk_results['chunk_warnings'].extend(duplicate_results.get('warnings', []))
            
            # Update global validation results
            self._update_global_results(chunk_results)
            
        except Exception as e:
            logger.error(f"Error validating chunk {chunk_number}: {e}")
            chunk_results['chunk_errors'].append(f"Validation error: {str(e)}")
            chunk_results['chunk_quality_score'] = 0.0
        
        return chunk_results

    def _validate_parameter_ranges(self, df: pd.DataFrame) -> Dict:
        """
        Validate parameter values are within expected ranges
        """
        results = {
            'parameter_quality_score': 100.0,
            'parameter_anomalies': 0,
            'warnings': [],
            'out_of_range_values': {},
            'parameter_scores': {}
        }
        
        if 'parameter_type' not in df.columns or 'avg_value' not in df.columns:
            results['warnings'].append("Missing required columns for parameter validation")
            results['parameter_quality_score'] = 50.0
            return results
        
        try:
            # Group by parameter type for efficient validation
            for param_type, param_group in df.groupby('parameter_type'):
                if param_type not in self.parameter_mapping:
                    continue  # Skip unknown parameters
                
                param_config = self.parameter_mapping[param_type]
                expected_range = param_config.get('expected_range', (None, None))
                critical_range = param_config.get('critical_range', (None, None))
                
                if expected_range[0] is None or expected_range[1] is None:
                    continue  # Skip parameters without defined ranges
                
                # Check values against ranges
                avg_values = param_group['avg_value'].dropna()
                if avg_values.empty:
                    continue
                
                # Count values outside expected range
                expected_min, expected_max = expected_range
                out_of_expected = ((avg_values < expected_min) | (avg_values > expected_max)).sum()
                
                # Count values outside critical range
                critical_min, critical_max = critical_range
                out_of_critical = ((avg_values < critical_min) | (avg_values > critical_max)).sum()
                
                # Calculate parameter score
                total_values = len(avg_values)
                if total_values > 0:
                    # Score based on percentage within expected range
                    within_expected = total_values - out_of_expected
                    param_score = (within_expected / total_values) * 100
                    
                    # Apply penalty for critical range violations
                    if out_of_critical > 0:
                        critical_penalty = (out_of_critical / total_values) * 50
                        param_score = max(0, param_score - critical_penalty)
                    
                    results['parameter_scores'][param_type] = param_score
                    
                    # Add to anomaly count
                    results['parameter_anomalies'] += out_of_expected
                    
                    # Add warnings for significant issues
                    if out_of_expected > 0:
                        unit = param_config.get('unit', '')
                        description = param_config.get('description', param_type)
                        results['warnings'].append(
                            f"{description}: {out_of_expected}/{total_values} values outside expected range "
                            f"[{expected_min}-{expected_max}]{unit}"
                        )
                    
                    if out_of_critical > 0:
                        results['warnings'].append(
                            f"{description}: {out_of_critical} values in critical range "
                            f"[{critical_min}-{critical_max}]{unit}"
                        )
                    
                    # Track specific out-of-range values for detailed reporting
                    if out_of_expected > 0:
                        out_of_range_indices = param_group[
                            (param_group['avg_value'] < expected_min) | 
                            (param_group['avg_value'] > expected_max)
                        ].index.tolist()
                        results['out_of_range_values'][param_type] = out_of_range_indices
            
            # Calculate overall parameter quality score
            if results['parameter_scores']:
                results['parameter_quality_score'] = np.mean(list(results['parameter_scores'].values()))
            
        except Exception as e:
            logger.error(f"Error in parameter range validation: {e}")
            results['warnings'].append(f"Parameter validation error: {str(e)}")
            results['parameter_quality_score'] = 0.0
        
        return results

    def _validate_timestamps(self, df: pd.DataFrame) -> Dict:
        """
        Validate timestamps are sequential and realistic
        """
        results = {
            'timestamp_quality_score': 100.0,
            'timestamp_anomalies': 0,
            'warnings': [],
            'sequence_issues': [],
            'unrealistic_timestamps': [],
            'large_gaps': []
        }
        
        if 'datetime' not in df.columns:
            results['warnings'].append("No datetime column found for timestamp validation")
            results['timestamp_quality_score'] = 0.0
            return results
        
        try:
            # Convert to datetime if not already
            timestamps = pd.to_datetime(df['datetime'], errors='coerce')
            valid_timestamps = timestamps.dropna()
            
            if len(valid_timestamps) == 0:
                results['warnings'].append("No valid timestamps found")
                results['timestamp_quality_score'] = 0.0
                return results
            
            # Check for unrealistic timestamps
            unrealistic = (
                (valid_timestamps < self.min_timestamp) |
                (valid_timestamps > self.max_timestamp)
            )
            unrealistic_count = unrealistic.sum()
            
            if unrealistic_count > 0:
                results['timestamp_anomalies'] += unrealistic_count
                results['warnings'].append(f"{unrealistic_count} unrealistic timestamps found")
                results['unrealistic_timestamps'] = timestamps[unrealistic].index.tolist()
            
            # Check sequence (should be generally increasing)
            sorted_timestamps = valid_timestamps.sort_values()
            
            # Check for large gaps in time sequence
            time_diffs = sorted_timestamps.diff()
            large_gaps = time_diffs > self.max_timestamp_gap
            large_gap_count = large_gaps.sum()
            
            if large_gap_count > 0:
                results['warnings'].append(f"{large_gap_count} large time gaps detected (>{self.max_timestamp_gap})")
                results['large_gaps'] = sorted_timestamps[large_gaps].index.tolist()
            
            # Check for non-sequential timestamps (minor issue)
            out_of_sequence = 0
            for i in range(1, len(sorted_timestamps)):
                if sorted_timestamps.iloc[i] < sorted_timestamps.iloc[i-1]:
                    out_of_sequence += 1
            
            if out_of_sequence > 0:
                results['warnings'].append(f"{out_of_sequence} timestamps appear out of sequence")
                results['sequence_issues'].append(f"Out of sequence: {out_of_sequence}")
            
            # Calculate timestamp quality score
            total_timestamps = len(timestamps)
            quality_deductions = (
                (unrealistic_count * 10) +  # 10 points per unrealistic timestamp
                (large_gap_count * 5) +     # 5 points per large gap
                (out_of_sequence * 1)       # 1 point per sequence issue
            )
            
            results['timestamp_quality_score'] = max(0, 100 - (quality_deductions / max(1, total_timestamps)) * 100)
            
        except Exception as e:
            logger.error(f"Error in timestamp validation: {e}")
            results['warnings'].append(f"Timestamp validation error: {str(e)}")
            results['timestamp_quality_score'] = 0.0
        
        return results

    def _validate_duplicates(self, df: pd.DataFrame) -> Dict:
        """
        Validate no duplicate entries within the same time window
        """
        results = {
            'duplicate_quality_score': 100.0,
            'duplicate_count': 0,
            'warnings': [],
            'duplicate_groups': []
        }
        
        required_cols = ['datetime', 'serial_number', 'parameter_type']
        if not all(col in df.columns for col in required_cols):
            results['warnings'].append("Missing required columns for duplicate detection")
            results['duplicate_quality_score'] = 50.0
            return results
        
        try:
            # Convert datetime
            df_check = df.copy()
            df_check['datetime'] = pd.to_datetime(df_check['datetime'], errors='coerce')
            df_check = df_check.dropna(subset=['datetime'])
            
            if df_check.empty:
                return results
            
            # Group by serial_number and parameter_type
            duplicate_count = 0
            
            for (serial, param), group in df_check.groupby(['serial_number', 'parameter_type']):
                if len(group) < 2:
                    continue  # No duplicates possible
                
                # Sort by datetime
                group_sorted = group.sort_values('datetime')
                
                # Check for entries within the duplicate time window
                for i in range(len(group_sorted) - 1):
                    current_time = group_sorted.iloc[i]['datetime']
                    next_time = group_sorted.iloc[i + 1]['datetime']
                    
                    if next_time - current_time <= self.duplicate_time_window:
                        duplicate_count += 1
                        results['duplicate_groups'].append({
                            'serial': serial,
                            'parameter': param,
                            'time1': current_time,
                            'time2': next_time,
                            'time_diff': next_time - current_time
                        })
            
            results['duplicate_count'] = duplicate_count
            
            if duplicate_count > 0:
                results['warnings'].append(
                    f"{duplicate_count} potential duplicate entries found within {self.duplicate_time_window}"
                )
                
                # Calculate quality score based on duplicate percentage
                total_records = len(df_check)
                duplicate_percentage = (duplicate_count / max(1, total_records)) * 100
                results['duplicate_quality_score'] = max(0, 100 - duplicate_percentage * 2)  # 2% penalty per duplicate
            
        except Exception as e:
            logger.error(f"Error in duplicate validation: {e}")
            results['warnings'].append(f"Duplicate validation error: {str(e)}")
            results['duplicate_quality_score'] = 0.0
        
        return results

    def _validate_completeness(self, df: pd.DataFrame) -> Dict:
        """
        Validate data completeness for the chunk
        """
        results = {
            'completeness_score': 100.0,
            'missing_data_percentage': 0.0,
            'warnings': [],
            'missing_columns': [],
            'missing_values': {}
        }
        
        try:
            total_cells = df.size
            if total_cells == 0:
                results['completeness_score'] = 0.0
                return results
            
            # Check for missing values in critical columns
            critical_columns = ['datetime', 'parameter_type', 'avg_value']
            available_critical = [col for col in critical_columns if col in df.columns]
            
            missing_critical_cols = [col for col in critical_columns if col not in df.columns]
            if missing_critical_cols:
                results['missing_columns'].extend(missing_critical_cols)
                results['warnings'].append(f"Missing critical columns: {missing_critical_cols}")
            
            # Count missing values per column
            missing_counts = {}
            total_missing = 0
            
            for col in df.columns:
                if col in df:
                    missing_count = df[col].isna().sum()
                    if missing_count > 0:
                        missing_counts[col] = missing_count
                        total_missing += missing_count
            
            results['missing_values'] = missing_counts
            
            # Calculate completeness score
            if total_cells > 0:
                missing_percentage = (total_missing / total_cells) * 100
                results['missing_data_percentage'] = missing_percentage
                results['completeness_score'] = max(0, 100 - missing_percentage)
            
            # Add warnings for significant missing data
            if results['missing_data_percentage'] > 10:
                results['warnings'].append(f"High missing data percentage: {results['missing_data_percentage']:.1f}%")
            
            # Check for critical missing values
            for col in available_critical:
                if col in missing_counts and missing_counts[col] > 0:
                    missing_pct = (missing_counts[col] / len(df)) * 100
                    results['warnings'].append(f"Missing values in critical column '{col}': {missing_pct:.1f}%")
            
        except Exception as e:
            logger.error(f"Error in completeness validation: {e}")
            results['warnings'].append(f"Completeness validation error: {str(e)}")
            results['completeness_score'] = 0.0
        
        return results

    def _update_global_results(self, chunk_results: Dict):
        """
        Update global validation results with chunk results
        """
        try:
            # Update counters
            self.validation_results['records_processed'] += chunk_results.get('records_in_chunk', 0)
            self.validation_results['anomalies_detected'] += chunk_results.get('chunk_anomalies', 0)
            
            # Update warnings (keep recent ones, limit total)
            chunk_warnings = chunk_results.get('chunk_warnings', [])
            self.validation_results['validation_warnings'].extend(chunk_warnings)
            
            # Keep only last 100 warnings for memory efficiency
            if len(self.validation_results['validation_warnings']) > 100:
                self.validation_results['validation_warnings'] = self.validation_results['validation_warnings'][-100:]
            
            # Update errors
            chunk_errors = chunk_results.get('chunk_errors', [])
            self.validation_results['validation_errors'].extend(chunk_errors)
            
            # Update quality score (running average)
            current_score = self.validation_results['data_quality_score']
            chunk_score = chunk_results.get('chunk_quality_score', 0)
            records_processed = self.validation_results['records_processed']
            chunk_records = chunk_results.get('records_in_chunk', 0)
            
            if records_processed > 0:
                # Weighted average based on number of records
                total_weight = records_processed
                current_weight = records_processed - chunk_records
                chunk_weight = chunk_records
                
                if total_weight > 0:
                    self.validation_results['data_quality_score'] = (
                        (current_score * current_weight) + (chunk_score * chunk_weight)
                    ) / total_weight
            
            # Update completeness score (running average)
            completeness = chunk_results.get('completeness_results', {}).get('completeness_score', 100)
            current_completeness = self.validation_results['completeness_score']
            
            if records_processed > 0:
                total_weight = records_processed
                current_weight = records_processed - chunk_records
                chunk_weight = chunk_records
                
                if total_weight > 0:
                    self.validation_results['completeness_score'] = (
                        (current_completeness * current_weight) + (completeness * chunk_weight)
                    ) / total_weight
            
        except Exception as e:
            logger.error(f"Error updating global validation results: {e}")

    def get_validation_summary(self) -> Dict:
        """
        Get comprehensive validation summary
        """
        try:
            # Calculate pass/fail counts
            total_records = self.validation_results['records_processed']
            anomalies = self.validation_results['anomalies_detected']
            self.validation_results['records_failed'] = anomalies
            self.validation_results['records_passed'] = max(0, total_records - anomalies)
            
            # Create summary with key metrics
            summary = {
                'overall_quality_score': round(self.validation_results['data_quality_score'], 2),
                'total_anomalies': self.validation_results['anomalies_detected'],
                'completeness_percentage': round(self.validation_results['completeness_score'], 2),
                'records_processed': self.validation_results['records_processed'],
                'records_passed': self.validation_results['records_passed'],
                'records_failed': self.validation_results['records_failed'],
                'validation_warnings_count': len(self.validation_results['validation_warnings']),
                'validation_errors_count': len(self.validation_results['validation_errors']),
                'detailed_warnings': self.validation_results['validation_warnings'][-10:],  # Last 10 warnings
                'detailed_errors': self.validation_results['validation_errors'][-5:],  # Last 5 errors
                'quality_grade': self._get_quality_grade(self.validation_results['data_quality_score'])
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating validation summary: {e}")
            return {
                'overall_quality_score': 0.0,
                'total_anomalies': 0,
                'completeness_percentage': 0.0,
                'records_processed': 0,
                'records_passed': 0,
                'records_failed': 0,
                'validation_warnings_count': 0,
                'validation_errors_count': 1,
                'detailed_warnings': [],
                'detailed_errors': [f"Validation summary error: {str(e)}"],
                'quality_grade': 'F'
            }

    def _get_quality_grade(self, score: float) -> str:
        """
        Convert quality score to letter grade
        """
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'B+'
        elif score >= 80:
            return 'B'
        elif score >= 75:
            return 'C+'
        elif score >= 70:
            return 'C'
        elif score >= 65:
            return 'D+'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _get_empty_validation_result(self) -> Dict:
        """
        Return empty validation result for empty chunks
        """
        return {
            'chunk_number': 0,
            'records_in_chunk': 0,
            'chunk_quality_score': 100.0,
            'chunk_anomalies': 0,
            'chunk_warnings': [],
            'chunk_errors': [],
            'parameter_results': {},
            'timestamp_results': {},
            'duplicate_results': {}
        }

    def reset_validation(self):
        """
        Reset validation results for new import session
        """
        self.validation_results = {
            'data_quality_score': 0.0,
            'anomalies_detected': 0,
            'validation_warnings': [],
            'validation_errors': [],
            'parameter_validations': {},
            'timestamp_issues': [],
            'duplicate_count': 0,
            'completeness_score': 0.0,
            'records_processed': 0,
            'records_passed': 0,
            'records_failed': 0
        }
        self._validation_cache.clear()
        self._last_timestamps.clear()
        self._duplicate_tracking.clear()

    def export_validation_report(self, file_path: str = None) -> str:
        """
        Export detailed validation report to file
        
        Args:
            file_path: Optional file path for export
            
        Returns:
            String containing the validation report
        """
        try:
            summary = self.get_validation_summary()
            
            report_lines = [
                "HALog Data Validation Report",
                "=" * 50,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "OVERALL QUALITY ASSESSMENT",
                "-" * 30,
                f"Quality Score: {summary['overall_quality_score']}/100 (Grade: {summary['quality_grade']})",
                f"Records Processed: {summary['records_processed']:,}",
                f"Records Passed: {summary['records_passed']:,}",
                f"Records Failed: {summary['records_failed']:,}",
                f"Completeness: {summary['completeness_percentage']}%",
                f"Total Anomalies: {summary['total_anomalies']:,}",
                "",
                "VALIDATION WARNINGS",
                "-" * 20
            ]
            
            if summary['detailed_warnings']:
                for i, warning in enumerate(summary['detailed_warnings'], 1):
                    report_lines.append(f"{i}. {warning}")
            else:
                report_lines.append("No warnings detected")
            
            report_lines.extend([
                "",
                "VALIDATION ERRORS",
                "-" * 17
            ])
            
            if summary['detailed_errors']:
                for i, error in enumerate(summary['detailed_errors'], 1):
                    report_lines.append(f"{i}. {error}")
            else:
                report_lines.append("No errors detected")
            
            report_content = "\n".join(report_lines)
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"Validation report exported to {file_path}")
            
            return report_content
            
        except Exception as e:
            error_msg = f"Error exporting validation report: {e}"
            logger.error(error_msg)
            return error_msg