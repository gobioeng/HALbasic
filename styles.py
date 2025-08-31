"""
Material Design Styling for Gobioeng HALog
Complete Material Design 3.0 implementation for PyQt5
Developer: Tanmay Pandey
Company: gobioeng.com
Date: 2025-08-22 17:03:08 UTC
"""


def get_material_design_stylesheet():
    """
    Complete Material Design 3.0 stylesheet
    Implemented by Tanmay Pandey - gobioeng.com
    """
    return """
    /* Material Design 3.0 Global Styles */
    QMainWindow {
        background-color: #FAFAFA;
        color: #1C1B1F;
        font-family: 'Segoe UI', 'Roboto', 'Google Sans', 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Material Design Menu Bar */
    QMenuBar {
        background-color: #FFFFFF;
        color: #1C1B1F;
        border: none;
        border-bottom: 1px solid #E7E0EC;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
        spacing: 12px;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 16px 24px;
        margin: 0px 8px;
        border-radius: 12px;
        color: #49454F;
        transition: all 0.2s ease;
    }
    QMenuBar::item:selected {
        background-color: #E8F5E8;
        color: #006A6B;
    }
    QMenuBar::item:pressed {
        background-color: #D0F0D1;
    }
    
    /* Material Design Menu */
    QMenu {
        background-color: #FFFBFE;
        border: none;
        border-radius: 12px;
        padding: 8px;
        font-size: 14px;
        font-weight: 400;
    }
    QMenu::item {
        padding: 16px 24px;
        border-radius: 8px;
        margin: 2px;
        color: #1C1B1F;
    }
    QMenu::item:selected {
        background-color: #E8F5E8;
        color: #006A6B;
    }
    
    /* Material Design Tab Widget */
    QTabWidget {
        border: none;
        background-color: transparent;
    }
    QTabWidget::pane {
        border: none;
        background-color: #FFFFFF;
        border-radius: 16px;
        margin-top: 12px;
    }
    QTabBar {
        background-color: transparent;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #79747E;
        padding: 20px 32px;
        margin-right: 4px;
        border-radius: 16px 16px 0px 0px;
        font-weight: 500;
        font-size: 14px;
        min-width: 160px;
        border: none;
        text-transform: none;
    }
    QTabBar::tab:selected {
        background-color: #FFFFFF;
        color: #1976D2;
        font-weight: 600;
        border-bottom: 3px solid #1976D2;
    }
    QTabBar::tab:hover:!selected {
        background-color: #F7F2FA;
        color: #1C1B1F;
    }
    
    /* Material Design Cards (Group Boxes) */
    QGroupBox {
        font-weight: 600;
        color: #1C1B1F;
        border: none;
        border-radius: 20px;
        margin-top: 40px;
        padding-top: 32px;
        background-color: #FFFFFF;
        font-size: 16px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 32px;
        top: 12px;
        padding: 12px 24px;
        background-color: #E8F5E8;
        color: #006A6B;
        font-size: 18px;
        font-weight: 700;
        border-radius: 16px;
        margin-top: -20px;
    }
    
    /* Material Design 3.0 Buttons */
    QPushButton {
        background-color: #1976D2;
        color: #FFFFFF;
        border: none;
        padding: 16px 32px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 14px;
        min-width: 160px;
        min-height: 24px;
        letter-spacing: 0.1px;
    }
    QPushButton:hover {
        background-color: #1565C0;
        box-shadow: 0px 4px 8px rgba(25, 118, 210, 0.3);
    }
    QPushButton:pressed {
        background-color: #0D47A1;
    }
    QPushButton:disabled {
        background-color: #E0E0E0;
        color: #9E9E9E;
    }
    
    /* Material Design Progress Bar */
    QProgressBar {
        border: none;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        background-color: #E3F2FD;
        color: #1976D2;
        font-size: 12px;
        min-height: 16px;
    }
    QProgressBar::chunk {
        background-color: #1976D2;
        border-radius: 8px;
    }
    
    /* Material Design Labels */
    QLabel {
        color: #1C1B1F;
        font-size: 14px;
        font-weight: 400;
        padding: 4px;
    }
    
    /* Material Design Text Inputs */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
        border: 2px solid #E7E0EC;
        border-radius: 12px;
        padding: 16px;
        font-size: 14px;
        background-color: #FFFFFF;
        color: #1C1B1F;
        selection-background-color: #E8F5E8;
    }
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #1976D2;
    }
    
    /* Material Design Tables */
    QTableWidget, QTreeWidget, QListWidget {
        border: none;
        border-radius: 16px;
        background-color: #FFFFFF;
        gridline-color: #E7E0EC;
        selection-background-color: #E8F5E8;
        selection-color: #006A6B;
        font-size: 14px;
    }
    QHeaderView::section {
        background-color: #F7F2FA;
        color: #49454F;
        padding: 16px;
        border: none;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Material Design Scroll Bars */
    QScrollBar:vertical {
        background-color: #F5F5F5;
        width: 12px;
        border-radius: 6px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #BDBDBD;
        border-radius: 6px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #9E9E9E;
    }
    """
