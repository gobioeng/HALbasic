"""
LINAC Dashboard Modernization - Visual Layout Description
=========================================================

The modernized dashboard provides a clean, professional interface optimized for 
medical equipment monitoring with proper machine identification and data separation.

HEADER SECTION:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ LINAC Water System Monitor Dashboard    [Machine: ▼] [📊 Compare] [🔄 Refresh] │
└─────────────────────────────────────────────────────────────────────────────────┘

METRICS CARDS SECTION:
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Records       │ │ Available     │ │ Parameters    │ │ Status        │
│ (Machine 2123)│ │ Machines      │ │ (Machine 2123)│ │               │
│               │ │               │ │               │ │               │
│   576         │ │     6         │ │     4         │ │ Machine 2123  │
│               │ │   units       │ │   types       │ │   Active      │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘

MACHINE STATUS OVERVIEW (when multiple machines available):
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Machine Status Overview                                                         │
│                                                                                 │
│ ● Machine 2123  ● Machine 2207  ● Machine 2350                                │
│   Healthy         Healthy         Warning                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

REAL-TIME SYSTEM TRENDS:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Real-time System Trends                                                         │
│                                                                                 │
│ Parameter: [magnetronFlow     ▼]                                              │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐    │
│ 18 │                                                                     │    │
│    │     ⬤ Machine 2123 ——————————————————————————————————————————————— │    │
│ 16 │     ⬤ Machine 2207 - - - - - - - - - - - - - - - - - - - - - - - - │    │
│    │     ⬤ Machine 2350 ····························                      │    │
│ 14 │                                                                     │    │
│    │                                                                     │    │
│ 12 │                                                                     │    │
│    └─────────────────────────────────────────────────────────────────────┘    │
│         08:00    10:00    12:00    14:00    16:00    18:00                    │
└─────────────────────────────────────────────────────────────────────────────────┘

KEY FEATURES DEMONSTRATED:
- Machine selector dropdown shows "All Machines" + individual machine options
- Real-time status indicators with color coding (Green=Healthy, Orange=Warning, Red=Critical)
- Machine-specific data filtering (shows 576 records for selected machine)
- Professional card-based metrics with machine context
- Enhanced trend visualization with distinct colors per machine
- Parameter selection for customizing chart views
- 30-second optimized refresh cycles for performance
- Modern flat design suitable for medical equipment monitoring

The interface automatically adapts when users select different machines,
showing machine-specific data while maintaining the ability to compare
multiple machines through the comparison mode toggle.
"""

if __name__ == "__main__":
    print(__doc__)