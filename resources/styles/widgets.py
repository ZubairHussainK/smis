"""
Widget styling functions for SMIS application.
Contains calendar configuration and other widget-specific styling.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat
from .constants import COLORS

def configure_calendar_weekend_format(calendar_widget):
    """
    Configure the calendar widget to highlight weekends and prevent selection of Sundays.
    
    Args:
        calendar_widget (QCalendarWidget): Calendar widget to configure
    """
    try:
        # Format for Saturdays - Visual styling
        saturday_format = QTextCharFormat()
        saturday_format.setForeground(Qt.darkBlue)
        saturday_format.setBackground(Qt.lightGray)
        
        # Format for Sundays - Visual styling (and will be disabled)
        sunday_format = QTextCharFormat()
        sunday_format.setForeground(Qt.red)
        sunday_format.setBackground(Qt.lightGray)
        
        # Apply formatting
        calendar_widget.setWeekdayTextFormat(Qt.Saturday, saturday_format)
        calendar_widget.setWeekdayTextFormat(Qt.Sunday, sunday_format)
        
        # Set grid visible
        calendar_widget.setGridVisible(True)
        
        # Set base styling for the calendar
        calendar_widget.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                alternate-background-color: {COLORS['gray_100']};
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: {COLORS['white']};
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['white']};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {COLORS['gray_400']};
            }}
            QCalendarWidget QMenu {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['gray_300']};
            }}
        """)

        # Prevent selection of Sundays with an event handler
        def on_selection_changed():
            try:
                selected_date = calendar_widget.selectedDate()
                if selected_date.dayOfWeek() == 7:  # Qt.Sunday is 7
                    # Move to next day (Monday)
                    next_working_day = selected_date.addDays(1)
                    calendar_widget.setSelectedDate(next_working_day)
                    
                    # Show warning message
                    from PyQt5.QtWidgets import QMessageBox
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Sunday Blocked")
                    msg.setText("Sunday is a weekend day and cannot be selected.\n\nAutomatically moved to next working day.")
                    msg.exec_()
            except:
                pass
        
        calendar_widget.selectionChanged.connect(on_selection_changed)
    except:
        pass  # If connection fails, just continue with visual formatting

def set_widget_height(widget, height=28):
    """
    Set a fixed height for a widget.
    
    Args:
        widget (QWidget): The widget to set the height for
        height (int, optional): Height in pixels. Defaults to 28.
    """
    widget.setFixedHeight(height)