"""
Standard table styling for SMIS application.
Provides consistent table design across all pages.
"""

def get_standard_table_style():
    """Returns the standard table style used across all SMIS pages."""
    return """
        QTableWidget {
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            background: white;
            gridline-color: #E5E7EB;
            font-family: 'Poppins';
            font-size: 13px;
            font-weight: 500;
            selection-background-color: transparent;
            selection-color: #374151;
            alternate-background-color: #F8FAFC;
            show-decoration-selected: 0;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #F1F5F9, stop:1 #E2E8F0);
            color: #1E293B;
            font-family: 'Arial', 'Segoe UI', 'Poppins Bold', sans-serif;
            font-weight: 700;
            font-size: 13px;
            padding: 12px 10px;
            border: none;
            border-bottom: 3px solid #3B82F6;
            border-right: 1px solid #CBD5E1;
            text-align: center;
        }
        QHeaderView::section:first {
            border-top-left-radius: 8px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 8px;
            border-right: none;
        }
        QTableWidget::item {
            padding: 15px 12px;
            border-bottom: 1px solid #E2E8F0;
            border-right: 1px solid #F1F5F9;
            background: white;
            color: #374151;
            font-weight: 500;
            font-size: 13px;
            outline: none;
        }

        QTableWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            font-weight: 600;
            outline: none;
        }
        QTableWidget::item:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #EBF4FF, stop:1 #DBEAFE);
            color: #1E40AF;
            border: none;
            outline: none;
        }
        QTableWidget::item:focus {
            background: white;
            color: #374151;
            border: none;
            outline: none;
        }
        QTableWidget::item:alternate {
            background: #F8FAFC;
        }
        QTableWidget::item:alternate:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            outline: none;
        }
        QScrollBar:vertical {
            border: none;
            background: #F1F5F9;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #CBD5E1;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94A3B8;
        }
        QScrollBar:horizontal {
            border: none;
            background: #F1F5F9;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #CBD5E1;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #94A3B8;
        }
        QToolTip {
            background: #1E293B;
            color: #F8FAFC;
            border: 2px solid #3B82F6;
            border-radius: 8px;
            padding: 12px 16px;
            font-family: 'Poppins';
            font-size: 13px;
            font-weight: 500;
            max-width: 400px;
        }
    """

def get_standard_table_properties():
    """Returns the standard table properties for consistent behavior."""
    return {
        'selection_behavior': 'SelectRows',
        'selection_mode': 'SingleSelection', 
        'alternating_row_colors': True,
        'sorting_enabled': True,
        'vertical_header_visible': False,
        'show_grid': True,
        'focus_policy': 'StrongFocus',
        'edit_triggers': 'NoEditTriggers',
        'vertical_section_size': 45,
        'vertical_scroll_policy': 'ScrollBarAsNeeded',
        'horizontal_scroll_policy': 'ScrollBarAsNeeded',
        'vertical_scroll_mode': 'ScrollPerPixel'
    }

def apply_standard_table_style(table_widget):
    """
    Apply the standard SMIS table style and properties to a QTableWidget.
    Includes persistent tooltip functionality for complete cell value display on click.
    
    NOTE: This function is maintained for backward compatibility.
    For new code, use the SMISTable class from ui.components.custom_table instead.
    
    Args:
        table_widget: QTableWidget instance to style
    """
    from PyQt5.QtWidgets import QTableWidget, QHeaderView, QToolTip, QLabel
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QPalette
    
    # Apply stylesheet
    table_widget.setStyleSheet(get_standard_table_style())
    
    # Apply standard properties
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.setSelectionMode(QTableWidget.SingleSelection)
    table_widget.setAlternatingRowColors(True)
    table_widget.setSortingEnabled(True)
    
    # Add a comment about the new recommended approach
    print("Note: Consider using SMISTable from ui.components.custom_table for new table implementations.")
    table_widget.verticalHeader().setVisible(False)
    table_widget.setShowGrid(True)
    table_widget.setFocusPolicy(Qt.StrongFocus)
    table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
    table_widget.verticalHeader().setDefaultSectionSize(45)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table_widget.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
    
    # Configure header
    header = table_widget.horizontalHeader()
    header.setStretchLastSection(True)
    header.setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Add persistent tooltip functionality
    table_widget._tooltip_label = None
    table_widget._current_tooltip_cell = None
    
    def show_persistent_tooltip(row, column):
        """Show persistent tooltip that stays until mouse leaves cell or another cell is clicked."""
        try:
            # Hide previous tooltip if exists
            if table_widget._tooltip_label:
                table_widget._tooltip_label.hide()
                table_widget._tooltip_label.deleteLater()
                table_widget._tooltip_label = None
            
            item = table_widget.item(row, column)
            if item is not None:
                cell_value = item.text()
                if cell_value:  # Only show tooltip if cell has content
                    # Get column header name for better context
                    header_item = table_widget.horizontalHeaderItem(column)
                    column_name = header_item.text() if header_item else f"Column {column + 1}"
                    
                    # Create persistent tooltip label
                    tooltip_label = QLabel(table_widget.parent())
                    tooltip_label.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
                    tooltip_label.setAttribute(Qt.WA_ShowWithoutActivating)
                    
                    # Set tooltip content and styling
                    tooltip_text = f"{cell_value}"
                    tooltip_label.setText(tooltip_text)
                    tooltip_label.setStyleSheet("""
                        QLabel {
                            background: white;
                            color: black;
                            border: 2px solid #3B82F6;
                            border-radius: 8px;
                            padding: 12px 16px;
                            font-family: 'Poppins';
                            font-size: 13px;
                            font-weight: 500;
                            max-width: 400px;
                        }
                    """)
                    tooltip_label.setWordWrap(True)
                    tooltip_label.adjustSize()
                    
                    # Get cell position for tooltip placement
                    cell_rect = table_widget.visualItemRect(item)
                    global_pos = table_widget.mapToGlobal(cell_rect.bottomLeft())
                    
                    # Position tooltip below the cell
                    tooltip_label.move(global_pos.x(), global_pos.y() + 5)
                    tooltip_label.show()
                    
                    # Store references
                    table_widget._tooltip_label = tooltip_label
                    table_widget._current_tooltip_cell = (row, column)
                    
                    print(f"💡 Persistent tooltip shown for cell ({row + 1}, {column + 1}): {column_name} = '{cell_value[:50]}{'...' if len(cell_value) > 50 else ''}'")
        except Exception as e:
            print(f"❌ Error showing persistent tooltip: {e}")
    
    def hide_tooltip_on_leave():
        """Hide tooltip when mouse leaves the current cell."""
        try:
            if table_widget._tooltip_label:
                table_widget._tooltip_label.hide()
                table_widget._tooltip_label.deleteLater()
                table_widget._tooltip_label = None
                table_widget._current_tooltip_cell = None
                print("💡 Tooltip hidden on mouse leave")
        except Exception as e:
            print(f"❌ Error hiding tooltip: {e}")
    
    def on_cell_entered(row, column):
        """Handle mouse entering a cell - hide tooltip if it's for a different cell."""
        try:
            if (table_widget._current_tooltip_cell and 
                table_widget._current_tooltip_cell != (row, column)):
                hide_tooltip_on_leave()
        except Exception as e:
            print(f"❌ Error in cell entered handler: {e}")
    
    # Connect signals
    table_widget.cellClicked.connect(show_persistent_tooltip)
    table_widget.cellEntered.connect(on_cell_entered)
    
    # Enable mouse tracking for hover events
    table_widget.setMouseTracking(True)
