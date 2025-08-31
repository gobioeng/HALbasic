# HALog Documentation

## API Reference

### Core Classes

#### MaterialDesignApp
Main application class implementing Material Design UI patterns.

```python
class MaterialDesignApp:
    def __init__(self)
    def create_material_splash(self)
    def create_main_window(self)
```

#### LinacParser
Enhanced LINAC log parser with performance optimizations.

```python
class LinacParser:
    def parse_file_chunked(self, file_path, chunk_size=1000)
    def get_parsing_stats(self)
```

#### DataAnalyzer
Comprehensive data analysis and statistics engine.

```python
class DataAnalyzer:
    def calculate_comprehensive_statistics(self, df)
    def detect_advanced_anomalies(self, df)
    def calculate_advanced_trends(self, df)
```

## Configuration

### Environment Variables

- `PYTHONOPTIMIZE=2`: Enable Python optimizations
- `PYTHONDONTWRITEBYTECODE=1`: Prevent .pyc file generation
- `NUMEXPR_MAX_THREADS=8`: Optimize numerical operations

### Application Settings

- Default chunk size: 1000 lines
- Database: SQLite (auto-created)
- Log level: INFO
- UI Theme: Material Design

## Performance Guidelines

### Large File Processing
- Use chunked processing for files > 100MB
- Enable background threading for UI responsiveness
- Monitor memory usage with psutil

### Database Optimization
- Batch inserts for better performance
- Index frequently queried columns
- Regular VACUUM operations

## Troubleshooting

### Common Issues

1. **PyQt5 Import Error**: Ensure PyQt5 is properly installed
2. **Database Lock**: Close existing connections before new operations
3. **Memory Issues**: Reduce chunk size for large files
4. **UI Freezing**: Ensure background workers are used for long operations

### Debug Mode

Run with debug flag for detailed logging:
```bash
python main.py --debug
```

## Development Setup

### Code Style
- Use Black formatter (line length: 88)
- Follow PEP 8 guidelines
- Use type hints where appropriate

### Testing
- Run pytest for unit tests
- Use sample data for integration tests
- Test on multiple Python versions (3.8+)

### Building
- PyInstaller for single executable
- cx_Freeze for cross-platform builds
- NSIS for Windows installer