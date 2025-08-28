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
            font-size: 8px;
            selection-background-color: #3B82F6;
            selection-color: white;
            alternate-background-color: #F8FAFC;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #F1F5F9, stop:1 #E2E8F0);
            color: #1E293B;
            font-family: 'Poppins Bold';
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
            padding: 10px 8px;
            border-bottom: 1px solid #E2E8F0;
            border-right: 1px solid #F1F5F9;
            background: white;
            color: #374151;
            font-weight: 500;
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
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
        'vertical_section_size': 35,
        'vertical_scroll_policy': 'ScrollBarAsNeeded',
        'horizontal_scroll_policy': 'ScrollBarAsNeeded',
        'vertical_scroll_mode': 'ScrollPerPixel'
    }

def apply_standard_table_style(table_widget):
    """
    Apply the standard SMIS table style and properties to a QTableWidget.
    
    Args:
        table_widget: QTableWidget instance to style
    """
    from PyQt5.QtWidgets import QTableWidget, QHeaderView
    from PyQt5.QtCore import Qt
    
    # Apply stylesheet
    table_widget.setStyleSheet(get_standard_table_style())
    
    # Apply standard properties
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.setSelectionMode(QTableWidget.SingleSelection)
    table_widget.setAlternatingRowColors(True)
    table_widget.setSortingEnabled(True)
    table_widget.verticalHeader().setVisible(False)
    table_widget.setShowGrid(True)
    table_widget.setFocusPolicy(Qt.StrongFocus)
    table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
    table_widget.verticalHeader().setDefaultSectionSize(35)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table_widget.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
    
    # Configure header
    header = table_widget.horizontalHeader()
    header.setStretchLastSection(True)
    header.setSectionResizeMode(QHeaderView.ResizeToContents)
