# Graph Display Fix for HALbasic PyInstaller Build

## Problem
The installer script was building the HALbasic executable successfully, but graphs were not displaying in the compiled version, while everything else worked fine.

## Root Cause
The issue was **matplotlib backend initialization order**. The matplotlib backend was being configured in `setup_environment()` function, but this happened AFTER the plotting modules (`utils_plot.py` and `plot_utils.py`) were imported. These modules import matplotlib components at the module level, causing matplotlib to initialize with its default backend before our Qt5Agg configuration could take effect.

## Solution
1. **Moved matplotlib backend configuration to the very top of main.py** - Created `configure_matplotlib_backend()` function and called it immediately after imports, before any other modules can import matplotlib
2. **Removed redundant backend configuration** - Cleaned up duplicate matplotlib backend setup code in plotting modules since it's now handled centrally
3. **Enhanced PyInstaller spec** - Added additional matplotlib backend imports to ensure all required components are included

## Changes Made

### main.py
- Added `configure_matplotlib_backend()` function at the top of the file
- Moved all matplotlib backend configuration before any potential matplotlib imports
- Removed duplicate configuration from `setup_environment()`

### plot_utils.py
- Removed redundant matplotlib backend configuration from `PlotWidget.init_ui()`
- Kept the critical `canvas.setParent(self)` fix for preventing popup windows

### utils_plot.py  
- Removed redundant matplotlib backend configuration from `_plot_parameter_data_single()`
- Kept the critical `canvas.setParent(widget)` fix for preventing popup windows

### create_installer.py
- Added additional matplotlib hidden imports: `backend_agg`, `style`, `font_manager`
- Enhanced matplotlib compatibility for PyInstaller builds

## Validation
- ✅ Quick test still passes all checks including graph popup fix
- ✅ Installer builds successfully with new configuration
- ✅ Backend configuration happens before any matplotlib module imports
- ✅ All existing functionality preserved

## Key Technical Details
The fix ensures that `matplotlib.use('Qt5Agg', force=True)` is called before any plotting modules import matplotlib components. This prevents matplotlib from initializing with the wrong backend and ensures graphs display properly in the compiled executable.

The existing `canvas.setParent(widget)` fixes are preserved to prevent popup windows and ensure proper embedding in the Qt application.