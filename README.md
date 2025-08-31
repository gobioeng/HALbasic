# HALog - LINAC Log Analyzer

Professional LINAC (Linear Accelerator) log analysis application with Material Design UI and advanced fault code lookup capabilities.

![HALog Logo](assets/linac_logo_256.png)

## Overview

HALog is a sophisticated monitoring and analysis tool for LINAC systems, providing comprehensive log analysis, fault code lookup, real-time data visualization, and professional reporting capabilities. Built with PyQt5 and Material Design principles for a modern, intuitive user experience.

## Features

### 🔍 **Fault Code Viewer**
- **Comprehensive Database**: Search through 6,200+ fault codes with descriptions
- **Dual Search Modes**: Search by exact fault code or description keywords
- **Rich Results Display**: Color-coded results with detailed fault information
- **Real-time Filtering**: Instant results as you type

### 📊 **Advanced Log Analysis**
- **Real-time Monitoring**: Live data acquisition and visualization
- **Advanced Analytics**: Statistical analysis and anomaly detection
- **Interactive Graphs**: Zoom, hover tooltips, and export capabilities
- **Trend Analysis**: Time series analysis and pattern recognition

### 🎨 **Modern Material Design UI**
- **Microsoft Word 2024 Style Splash**: Clean, minimalistic startup experience
- **Professional Interface**: Consistent Material Design elements
- **Responsive Layout**: Adaptive interface for different screen sizes
- **Clean Typography**: Easy-to-read fonts and proper spacing

### ⚡ **Performance Optimizations**
- **Multithreaded Processing**: Background processing for large datasets
- **Lazy Loading**: Chunked processing for large log files
- **Memory Optimization**: Efficient memory usage for large datasets
- **Progress Tracking**: Real-time progress with ETA calculations

## Screenshots

*Screenshots will be added here showing:*
- Main dashboard with log analysis
- Fault Code Viewer in action
- Material Design splash screen
- Interactive trend charts

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gobioeng/halog.git
   cd halog
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### First Time Setup

1. Launch the application - you'll see the new Microsoft Word 2024 style splash screen
2. Use **File > Upload Log File** to load LINAC log files (.log or .txt format)
3. Try the **Fault Code Viewer** tab to search fault codes:
   - Enter a code like "400027" for exact search
   - Enter keywords like "network" for description search
4. Explore the analytics and visualization features in other tabs
5. Check **Help > About HALog** for application information

## Enhanced Features

### File Menu
- **Upload Log File**: Browse and load .log or .txt files with progress indication
- **Export Data**: Save analysis results in multiple formats
- **About Dialog**: Comprehensive application information with auto-detected version

### Fault Code Database
The application includes a comprehensive database of 6,200+ LINAC fault codes with:
- Detailed descriptions for each fault code
- Categorization by fault type (Fault, Interlock, etc.)
- Fast search capabilities by code or keywords
- Professional result formatting with color coding

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM minimum, 8GB recommended for large log files
- **Storage**: 500MB free space
- **Display**: 1280x720 minimum resolution (1920x1080 recommended)

## Development

### Running from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debugging
python main.py

# Run tests (if available)
pytest

# Code formatting
black *.py
flake8 *.py
```

### Building Executable

```bash
# Using PyInstaller
pyinstaller --windowed --icon=assets/linac_logo.ico main.py

# Using cx_Freeze
python setup.py build
```

## Project Structure

```
halog/
├── main.py                 # Application entry point
├── ui_mainwindow.py        # Main window UI with fault code tab
├── fault_code_parser.py    # Fault code database parser
├── linac_parser.py         # Log file parsing logic
├── data_analyzer.py        # Analytics engine
├── plot_utils.py           # Graph generation utilities
├── database.py             # Database management
├── worker_thread.py        # Background processing
├── about_dialog.py         # Enhanced about dialog
├── splash_screen.py        # Microsoft Word 2024 style splash
├── assets/                 # Images and icons
├── data/                   # Fault.txt and sample data
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## About the Developer

> HALog was developed by **Tanmay Pandey** at **gobioeng.com** to support radiotherapy engineers in analyzing LINAC machine logs with speed, clarity, and precision.

**Tanmay Pandey** is a biomedical engineering specialist focused on medical device software solutions. Through gobioeng.com, he provides innovative tools for LINAC and other medical device troubleshooting, monitoring, and analysis.

### Professional Background
- **Expertise**: Biomedical engineering solutions for medical devices
- **Specialization**: LINAC systems, radiotherapy equipment, and data analysis
- **Mission**: Supporting healthcare professionals with reliable, efficient software tools
- **Website**: [gobioeng.com](https://gobioeng.com) - Biomedical engineering resources, career opportunities, and expert insights

### About gobioeng.com
A comprehensive platform providing biomedical engineering resources, educational content, career guidance, and professional tools for students, educators, and industry professionals in the biomedical engineering field.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software developed by [gobioeng.com](https://gobioeng.com).

## Support

For technical support and questions:
- **Website**: [gobioeng.com](https://gobioeng.com)
- **Developer**: Tanmay Pandey
- **Organization**: gobioeng.com
- **Version**: Auto-detected from application

## Changelog

### Version 0.0.1 (Current)
- ✅ **New**: Fault Code Viewer tab with 6,200+ searchable fault codes
- ✅ **Enhanced**: Microsoft Word 2024 style splash screen
- ✅ **Enhanced**: File menu with Upload Log File functionality
- ✅ **Enhanced**: About dialog with auto-version detection
- ✅ **Enhanced**: Material Design UI improvements
- ✅ **Enhanced**: Professional branding throughout application
- ✅ **Optimized**: Performance improvements and code cleanup
- ✅ **Added**: Comprehensive fault code database parsing
- ✅ **Added**: Status bar with developer branding
