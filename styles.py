"""
Modern Native Styling for Gobioeng HALog
Windows 11 inspired design with native OS integration
Developer: gobioeng.com
Date: 2025-01-21
"""


def get_modern_native_stylesheet():
    """Get modern native Windows 11-style stylesheet with consistent design"""
    return """
    /* Modern Windows 11 Theme - Native Feel */
    QMainWindow {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 9pt;
    }

    /* Enhanced Tab Widget - Windows 11 Style */
    QTabWidget::pane {
        border: 1px solid #dee2e6;
        background-color: white;
        border-radius: 8px;
        margin-top: 4px;
    }
    QTabBar {
        background-color: transparent;
        border: none;
    }
    QTabBar::tab {
        background-color: #e9ecef;
        color: #495057;
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
        min-width: 80px;
        border: 1px solid #dee2e6;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: white;
        color: #0d6efd;
        border-color: #0d6efd;
        border-bottom: 2px solid #0d6efd;
        font-weight: 600;
    }
    QTabBar::tab:hover:!selected {
        background-color: #f8f9fa;
        border-color: #adb5bd;
    }

    /* Modern Group Boxes - Card Style with Better Sizing */
    QGroupBox {
        font-weight: 600;
        color: #212529;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin-top: 16px;
        padding-top: 20px;
        background-color: white;
        font-size: 10pt;
        min-height: 60px;  /* Prevent boxes from collapsing */
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 6px 12px;
        background-color: #0d6efd;
        color: white;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Modern Buttons - Windows 11 Fluent Style */
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: 1px solid #0d6efd;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 9pt;
        min-width: 80px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #0b5ed7;
        border-color: #0b5ed7;
    }
    QPushButton:pressed {
        background-color: #0a58ca;
        border-color: #0a58ca;
    }
    QPushButton:disabled {
        background-color: #e9ecef;
        color: #6c757d;
        border-color: #dee2e6;
    }

    /* Secondary Button Style */
    QPushButton#secondaryButton {
        background-color: #6c757d;
        border-color: #6c757d;
    }
    QPushButton#secondaryButton:hover {
        background-color: #5c636a;
        border-color: #5c636a;
    }
    
    /* Success Button Style */
    QPushButton#successButton {
        background-color: #198754;
        border-color: #198754;
    }
    QPushButton#successButton:hover {
        background-color: #157347;
        border-color: #157347;
    }
    
    /* Danger Button Style */
    QPushButton#dangerButton {
        background-color: #dc3545;
        border-color: #dc3545;
    }
    QPushButton#dangerButton:hover {
        background-color: #bb2d3b;
        border-color: #bb2d3b;
    }
    
    /* Modern Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {
        border: 2px solid #ced4da;
        border-radius: 6px;
        padding: 8px 12px;
        background-color: white;
        color: #212529;
        font-size: 9pt;
        selection-background-color: #cfe2ff;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #86b7fe;
        outline: 0;
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
    }
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
        border-color: #adb5bd;
    }

    /* Modern Tables with Responsive Sizing */
    QTableWidget {
        background-color: white;
        border: 1px solid #dee2e6;
        gridline-color: #dee2e6;
        selection-background-color: #cfe2ff;
        selection-color: #212529;
        border-radius: 6px;
        font-size: 9pt;
        min-height: 200px;  /* Ensure minimum height */
    }
    QHeaderView::section {
        background-color: #f8f9fa;
        border: none;
        border-bottom: 2px solid #dee2e6;
        padding: 8px;
        font-weight: 600;
        color: #495057;
        min-height: 30px;  /* Ensure header visibility */
    }
    
    /* Modern ComboBoxes */
    QComboBox {
        border: 2px solid #ced4da;
        border-radius: 6px;
        padding: 6px 12px;
        background-color: white;
        color: #212529;
        min-width: 120px;
    }
    QComboBox:focus {
        border-color: #86b7fe;
        outline: 0;
    }
    QComboBox:hover {
        border-color: #adb5bd;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
        padding-right: 4px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent; 
        border-top: 4px solid #495057;
        margin: 4px;
    }

    /* Modern Labels */
    QLabel {
        color: #212529;
        background-color: transparent;
    }

    /* Modern Status Bar */
    QStatusBar {
        background-color: #f8f9fa;
        border-top: 1px solid #dee2e6;
        color: #6c757d;
        font-size: 8pt;
        padding: 4px;
    }

    /* Modern MenuBar */
    QMenuBar {
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        color: #212529;
        font-weight: 500;
    }
    QMenuBar::item {
        padding: 8px 16px;
        background-color: transparent;
        border-radius: 4px;
        margin: 2px;
    }
    QMenuBar::item:selected {
        background-color: #e9ecef;
    }
    QMenuBar::item:pressed {
        background-color: #cfe2ff;
    }

    /* Modern Menus */
    QMenu {
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        color: #212529;
        padding: 4px 0;
    }
    QMenu::item {
        padding: 8px 20px;
        margin: 2px 4px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #e9ecef;
        color: #212529;
    }
    QMenu::item:pressed {
        background-color: #cfe2ff;
    }

    /* Modern Progress Bars */
    QProgressBar {
        border: 1px solid #dee2e6;
        text-align: center;
        background-color: #f8f9fa;
        color: #212529;
        border-radius: 6px;
        height: 20px;
    }
    QProgressBar::chunk {
        background-color: #0d6efd;
        border-radius: 5px;
    }
    
    /* Modern Scrollbars */
    QScrollBar:vertical {
        background-color: #f8f9fa;
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #ced4da;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #adb5bd;
    }
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: transparent;
        height: 0;
    }
    """


def get_dark_theme_stylesheet():
    """
    Modern dark theme stylesheet for users who prefer dark mode
    """
    return """
    /* Dark Theme Global Styles */
    QMainWindow {
        background-color: #1e1e1e;
        color: #ffffff;
        font-family: 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.4;
    }

    /* Dark Menu Bar */
    QMenuBar {
        background-color: #2d2d30;
        color: #ffffff;
        border: none;
        border-bottom: 1px solid #3e3e42;
        padding: 8px 16px;
        font-size: 14px;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 10px 16px;
        margin: 0px 4px;
        border-radius: 6px;
        color: #cccccc;
    }
    QMenuBar::item:selected {
        background-color: #404040;
        color: #0078d4;
    }

    /* Dark Tab Design */
    QTabWidget::pane {
        border: none;
        background-color: #252526;
        border-radius: 12px;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #cccccc;
        padding: 14px 24px;
        border-radius: 8px 8px 0px 0px;
        font-weight: 500;
        font-size: 14px;
    }
    QTabBar::tab:selected {
        background-color: #252526;
        color: #0078d4;
        font-weight: 600;
        border-bottom: 3px solid #0078d4;
    }
    QTabBar::tab:hover:!selected {
        background-color: #2d2d30;
    }

    /* Dark Cards */
    QGroupBox {
        color: #ffffff;
        border: 1px solid #3e3e42;
        background-color: #252526;
    }
    QGroupBox::title {
        background-color: #0078d4;
        color: #ffffff;
    }

    /* Dark Buttons */
    QPushButton {
        background-color: #0078d4;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #106ebe;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }

    /* Dark Input Fields */
    QLineEdit, QTextEdit {
        border: 2px solid #3e3e42;
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus {
        border-color: #0078d4;
    }

    /* Dark Tables */
    QTableWidget {
        background-color: #252526;
        gridline-color: #3e3e42;
        border: 1px solid #3e3e42;
        color: #ffffff;
    }
    QHeaderView::section {
        background-color: #2d2d30;
        color: #cccccc;
        border-bottom: 2px solid #0078d4;
    }
    """


def apply_responsive_layout(widget):
    """
    Apply responsive layout adjustments based on widget size
    Enhanced for better box sizing and overlap prevention
    """
    try:
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QApplication

        def adjust_layout():
            screen = QApplication.primaryScreen()
            if screen:
                screen_size = screen.size()
                widget_size = widget.size()

                # Adjust font sizes and spacing based on screen/widget size
                responsive_style = ""
                
                if widget_size.width() < 1000:
                    # Compact layout for smaller screens
                    responsive_style = """
                        QTabBar::tab { padding: 8px 12px; font-size: 12px; }
                        QPushButton { padding: 8px 16px; font-size: 12px; }
                        QGroupBox { font-size: 12px; min-height: 50px; margin: 4px; }
                        QTableWidget { font-size: 8pt; min-height: 150px; }
                        QHeaderView::section { min-height: 25px; padding: 6px; }
                        QComboBox { min-width: 100px; padding: 4px 8px; }
                    """
                elif widget_size.width() > 1600:
                    # Expanded layout for larger screens
                    responsive_style = """
                        QTabBar::tab { padding: 16px 28px; font-size: 15px; }
                        QPushButton { padding: 14px 28px; font-size: 15px; }
                        QGroupBox { font-size: 14px; min-height: 80px; margin: 8px; }
                        QTableWidget { font-size: 10pt; min-height: 300px; }
                        QHeaderView::section { min-height: 35px; padding: 10px; }
                        QComboBox { min-width: 140px; padding: 8px 16px; }
                    """
                else:
                    # Standard layout
                    responsive_style = """
                        QTabBar::tab { padding: 12px 20px; font-size: 13px; }
                        QPushButton { padding: 10px 20px; font-size: 13px; }
                        QGroupBox { font-size: 13px; min-height: 60px; margin: 6px; }
                        QTableWidget { font-size: 9pt; min-height: 200px; }
                        QHeaderView::section { min-height: 30px; padding: 8px; }
                        QComboBox { min-width: 120px; padding: 6px 12px; }
                    """
                
                # Apply responsive styles
                current_style = widget.styleSheet()
                # Remove any existing responsive styles
                import re
                current_style = re.sub(r'/\* RESPONSIVE \*/.*?/\* END RESPONSIVE \*/', '', current_style, flags=re.DOTALL)
                
                # Add new responsive styles
                widget.setStyleSheet(current_style + f"""
                /* RESPONSIVE */
                {responsive_style}
                /* END RESPONSIVE */
                """)

        # Apply initial adjustments
        adjust_layout()

        # Set up timer to reapply on resize
        timer = QTimer()
        timer.timeout.connect(adjust_layout)
        timer.start(500)  # Check every 500ms

    except Exception as e:
        print(f"Error applying responsive layout: {e}")


def get_material_design_stylesheet():
    """Legacy function - redirects to modern native stylesheet"""
    return get_modern_native_stylesheet()