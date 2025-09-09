"""
Unit Tests for HALog Data Validation System
Tests the DataValidator class with various scenarios

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data_validator import DataValidator
    from unified_parser import UnifiedParser
except ImportError as e:
    print(f"Could not import modules: {e}")
    print("This test should be run from the HALbasic directory")
    sys.exit(1)


class TestDataValidator:
    """Test cases for DataValidator class"""
    
    @pytest.fixture
    def sample_parameter_mapping(self):
        """Sample parameter mapping for testing"""
        return {
            'magnetronFlow': {
                'patterns': ['magnetronFlow', 'magnetron flow'],
                'unit': 'L/min',
                'description': 'Mag Flow',
                'expected_range': (8, 18),
                'critical_range': (6, 20),
            },
            'FanremoteTempStatistics': {
                'patterns': ['FanremoteTempStatistics', 'remote temp'],
                'unit': '°C',
                'description': 'Temp Room',
                'expected_range': (18, 25),
                'critical_range': (15, 30),
            }
        }
    
    @pytest.fixture
    def validator(self, sample_parameter_mapping):
        """Create DataValidator instance for testing"""
        return DataValidator(sample_parameter_mapping)
    
    @pytest.fixture
    def sample_valid_data(self):
        """Create sample valid data for testing"""
        dates = pd.date_range('2025-01-01 10:00:00', periods=10, freq='5min')
        return pd.DataFrame({
            'datetime': dates,
            'serial_number': ['12345'] * 10,
            'parameter_type': ['magnetronFlow'] * 5 + ['FanremoteTempStatistics'] * 5,
            'avg_value': [15.2, 15.8, 16.1, 15.9, 16.0, 20.1, 20.5, 20.3, 20.7, 20.4],
            'min_value': [14.8, 15.3, 15.7, 15.5, 15.6, 19.8, 20.1, 19.9, 20.3, 20.0],
            'max_value': [15.6, 16.2, 16.5, 16.3, 16.4, 20.4, 20.9, 20.7, 21.1, 20.8]
        })
    
    @pytest.fixture
    def sample_invalid_data(self):
        """Create sample invalid data for testing"""
        dates = pd.date_range('2025-01-01 10:00:00', periods=5, freq='5min')
        return pd.DataFrame({
            'datetime': dates,
            'serial_number': ['12345'] * 5,
            'parameter_type': ['magnetronFlow'] * 5,
            'avg_value': [25.0, 5.0, 15.5, 30.0, 16.0],  # Out of range values
            'min_value': [24.5, 4.5, 15.0, 29.5, 15.5],
            'max_value': [25.5, 5.5, 16.0, 30.5, 16.5]
        })
    
    def test_validator_initialization(self, sample_parameter_mapping):
        """Test validator initialization"""
        validator = DataValidator(sample_parameter_mapping)
        
        assert validator.parameter_mapping == sample_parameter_mapping
        assert validator.validation_results['data_quality_score'] == 0.0
        assert validator.validation_results['anomalies_detected'] == 0
        assert len(validator.validation_results['validation_warnings']) == 0
    
    def test_validate_parameter_ranges_valid_data(self, validator, sample_valid_data):
        """Test parameter range validation with valid data"""
        result = validator._validate_parameter_ranges(sample_valid_data)
        
        assert result['parameter_quality_score'] == 100.0
        assert result['parameter_anomalies'] == 0
        assert len(result['warnings']) == 0
        assert 'magnetronFlow' in result['parameter_scores']
        assert 'FanremoteTempStatistics' in result['parameter_scores']
    
    def test_validate_parameter_ranges_invalid_data(self, validator, sample_invalid_data):
        """Test parameter range validation with invalid data"""
        result = validator._validate_parameter_ranges(sample_invalid_data)
        
        assert result['parameter_quality_score'] < 100.0
        assert result['parameter_anomalies'] > 0
        assert len(result['warnings']) > 0
        assert 'magnetronFlow' in result['out_of_range_values']
    
    def test_validate_timestamps_valid(self, validator, sample_valid_data):
        """Test timestamp validation with valid sequential data"""
        result = validator._validate_timestamps(sample_valid_data)
        
        assert result['timestamp_quality_score'] == 100.0
        assert result['timestamp_anomalies'] == 0
        assert len(result['unrealistic_timestamps']) == 0
        assert len(result['large_gaps']) == 0
    
    def test_validate_timestamps_invalid(self, validator):
        """Test timestamp validation with invalid data"""
        # Create data with unrealistic timestamps
        invalid_dates = [
            datetime(1990, 1, 1),  # Too old
            datetime(2040, 1, 1),  # Too future
            datetime(2025, 1, 1),  # Valid
            datetime(2025, 1, 2),  # Large gap
        ]
        
        invalid_data = pd.DataFrame({
            'datetime': invalid_dates,
            'serial_number': ['12345'] * 4,
            'parameter_type': ['magnetronFlow'] * 4,
            'avg_value': [15.0] * 4
        })
        
        result = validator._validate_timestamps(invalid_data)
        
        assert result['timestamp_quality_score'] < 100.0
        assert result['timestamp_anomalies'] > 0
        assert len(result['warnings']) > 0
    
    def test_validate_duplicates(self, validator):
        """Test duplicate detection"""
        # Create data with potential duplicates (same time window)
        base_time = datetime(2025, 1, 1, 10, 0, 0)
        duplicate_data = pd.DataFrame({
            'datetime': [
                base_time,
                base_time + timedelta(seconds=10),  # Within duplicate window
                base_time + timedelta(minutes=5),   # Outside duplicate window
            ],
            'serial_number': ['12345'] * 3,
            'parameter_type': ['magnetronFlow'] * 3,
            'avg_value': [15.0, 15.1, 15.2]
        })
        
        result = validator._validate_duplicates(duplicate_data)
        
        assert result['duplicate_count'] > 0
        assert len(result['duplicate_groups']) > 0
        assert result['duplicate_quality_score'] < 100.0
    
    def test_validate_completeness(self, validator, sample_valid_data):
        """Test data completeness validation"""
        result = validator._validate_completeness(sample_valid_data)
        
        assert result['completeness_score'] == 100.0
        assert result['missing_data_percentage'] == 0.0
        assert len(result['missing_columns']) == 0
    
    def test_validate_completeness_with_missing_data(self, validator):
        """Test completeness validation with missing data"""
        incomplete_data = pd.DataFrame({
            'datetime': [datetime(2025, 1, 1)] * 3,
            'serial_number': ['12345', None, '12346'],
            'parameter_type': ['magnetronFlow', 'magnetronFlow', None],
            'avg_value': [15.0, 16.0, None]
        })
        
        result = validator._validate_completeness(incomplete_data)
        
        assert result['completeness_score'] < 100.0
        assert result['missing_data_percentage'] > 0
        assert len(result['missing_values']) > 0
    
    def test_validate_chunk_integration(self, validator, sample_valid_data):
        """Test chunk validation integration"""
        result = validator.validate_chunk(sample_valid_data, chunk_number=1)
        
        assert result['chunk_number'] == 1
        assert result['records_in_chunk'] == len(sample_valid_data)
        assert result['chunk_quality_score'] > 0
        assert 'parameter_results' in result
        assert 'timestamp_results' in result
        assert 'duplicate_results' in result
    
    def test_validation_summary(self, validator, sample_valid_data):
        """Test validation summary generation"""
        # Run validation on chunk
        validator.validate_chunk(sample_valid_data)
        
        summary = validator.get_validation_summary()
        
        assert 'overall_quality_score' in summary
        assert 'total_anomalies' in summary
        assert 'records_processed' in summary
        assert 'quality_grade' in summary
        assert summary['records_processed'] == len(sample_valid_data)
    
    def test_quality_grade_calculation(self, validator):
        """Test quality grade calculation"""
        test_scores = [
            (95, 'A+'),
            (92, 'A'),
            (87, 'B+'),
            (82, 'B'),
            (77, 'C+'),
            (72, 'C'),
            (67, 'D+'),
            (62, 'D'),
            (50, 'F')
        ]
        
        for score, expected_grade in test_scores:
            grade = validator._get_quality_grade(score)
            assert grade == expected_grade, f"Score {score} should be grade {expected_grade}, got {grade}"
    
    def test_reset_validation(self, validator, sample_valid_data):
        """Test validation reset functionality"""
        # Run validation
        validator.validate_chunk(sample_valid_data)
        assert validator.validation_results['records_processed'] > 0
        
        # Reset
        validator.reset_validation()
        assert validator.validation_results['records_processed'] == 0
        assert validator.validation_results['anomalies_detected'] == 0
        assert len(validator.validation_results['validation_warnings']) == 0
    
    def test_export_validation_report(self, validator, sample_valid_data):
        """Test validation report export"""
        # Run validation
        validator.validate_chunk(sample_valid_data)
        
        # Export report
        report = validator.export_validation_report()
        
        assert isinstance(report, str)
        assert "HALog Data Validation Report" in report
        assert "OVERALL QUALITY ASSESSMENT" in report
        assert "VALIDATION WARNINGS" in report


class TestUnifiedParserIntegration:
    """Test integration of validation with UnifiedParser"""
    
    def test_parser_with_validation_enabled(self):
        """Test that parser can use validation when enabled"""
        parser = UnifiedParser()
        
        # Test that parameter mapping is available
        assert hasattr(parser, 'parameter_mapping')
        assert len(parser.parameter_mapping) > 0
        
        # Test that parsing stats are initialized
        assert hasattr(parser, 'parsing_stats')
        assert 'lines_processed' in parser.parsing_stats


def run_validation_performance_test():
    """Performance test for validation system"""
    print("Running validation performance test...")
    
    # Create large dataset
    n_records = 10000
    dates = pd.date_range('2025-01-01', periods=n_records, freq='1min')
    
    large_data = pd.DataFrame({
        'datetime': dates,
        'serial_number': ['12345'] * n_records,
        'parameter_type': ['magnetronFlow'] * n_records,
        'avg_value': np.random.uniform(14, 18, n_records),
        'min_value': np.random.uniform(13, 17, n_records),
        'max_value': np.random.uniform(15, 19, n_records)
    })
    
    # Test validation performance
    parser = UnifiedParser()
    validator = DataValidator(parser.parameter_mapping)
    
    import time
    start_time = time.time()
    
    # Process in chunks like real import
    chunk_size = 1000
    for i in range(0, len(large_data), chunk_size):
        chunk = large_data.iloc[i:i+chunk_size]
        validator.validate_chunk(chunk, i // chunk_size)
    
    end_time = time.time()
    duration = end_time - start_time
    
    summary = validator.get_validation_summary()
    
    print(f"Performance Test Results:")
    print(f"  Records processed: {n_records:,}")
    print(f"  Time taken: {duration:.2f} seconds")
    print(f"  Records/second: {n_records/duration:.1f}")
    print(f"  Quality score: {summary['overall_quality_score']:.1f}%")
    print(f"  Anomalies: {summary['total_anomalies']}")


if __name__ == "__main__":
    # Run performance test
    run_validation_performance_test()
    
    print("\nTo run unit tests, use: pytest test_data_validation.py -v")