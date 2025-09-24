from PyQt5.QtWidgets import (
    QTableWidget, QHeaderView, QTableWidgetItem, QWidget, QCheckBox, 
    QHBoxLayout, QVBoxLayout, QAbstractItemView, QToolTip, QLabel, QSizePolicy,
    QStyledItemDelegate,  QPushButton, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor, QBrush, QIcon
from ui.components.custom_combo_box import CustomComboBox
from resources.styles.constants import COLORS, RADIUS

class CenterAlignDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
    
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class TablePagination(QWidget):

    # Signal emitted when page or page size changes
    pageChanged = pyqtSignal(int, int)  # (page_number, page_size)
    
    def __init__(self, total_items=0, page_size=10, parent=None):
        super().__init__(parent)
        
        self.current_page = 1
        self.page_size = page_size
        self.total_items = total_items
        
        # Make pagination control responsive horizontally but with fixed vertical height
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(50)  # Ensure enough height for the combobox
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the pagination UI elements."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 8, 0, 10)  # Added bottom margin of 10px
        main_layout.setSpacing(10)
        
        # Left section for record count - takes up 1/3 of space
        left_section = QWidget()
        left_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_section.setMinimumHeight(32)  # Ensure enough height for the combobox
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(5, 0, 5, 0)
        left_layout.setSpacing(5)
        
        # Total records display
        self.records_label = QLabel(f"Total Records: {self.total_items}")
        self.records_label.setStyleSheet(f"""
            font-weight: bold; 
            color: {COLORS['primary_dark']};
            padding: 5px 10px;
            border: none;
            background: transparent;
        """)
        self.records_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        left_layout.addWidget(self.records_label)
        left_layout.addStretch(1)
        
        # Center section for navigation - takes up 1/3 of space
        center_section = QWidget()
        center_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        center_section.setMinimumHeight(32)  # Ensure enough height for the combobox
        center_layout = QHBoxLayout(center_section)
        center_layout.setContentsMargins(0, 0, 5, 0)
        center_layout.setSpacing(5)
        center_layout.setAlignment(Qt.AlignCenter)
        
        # First page button
        self.first_btn = QPushButton()
        self.first_btn.setIcon(QIcon("resources/icons/arrow_first.svg"))
        self.first_btn.setToolTip("First Page")
        self.first_btn.clicked.connect(self._go_to_first)
        self.first_btn.setMaximumWidth(40)
        center_layout.addWidget(self.first_btn)
        
        # Previous page button
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(QIcon("resources/icons/arrow_left.svg"))
        self.prev_btn.setToolTip("Previous Page")
        self.prev_btn.clicked.connect(self._go_to_prev)
        self.prev_btn.setMaximumWidth(40)
        center_layout.addWidget(self.prev_btn)
        
        # Current page info
        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setAlignment(Qt.AlignCenter)
        self.page_info.setMinimumWidth(120)
        self.page_info.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        center_layout.addWidget(self.page_info)
        
        # Next page button
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon("resources/icons/arrow_right.svg"))
        self.next_btn.setToolTip("Next Page")
        self.next_btn.clicked.connect(self._go_to_next)
        self.next_btn.setMaximumWidth(40)
        center_layout.addWidget(self.next_btn)
        
        # Last page button
        self.last_btn = QPushButton()
        self.last_btn.setIcon(QIcon("resources/icons/arrow_last.svg"))
        self.last_btn.setToolTip("Last Page")
        self.last_btn.clicked.connect(self._go_to_last)
        self.last_btn.setMaximumWidth(40)
        center_layout.addWidget(self.last_btn)
        
        # Right section for page size - takes up 1/3 of space
        right_section = QWidget()
        right_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_section.setMinimumHeight(32)  # Ensure enough height for the combobox
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(5, 5, 5, 5)  # Added vertical padding
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignRight)
        
        # Page size selector
        rows_per_page_label = QLabel("Rows per page:")
        rows_per_page_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        right_layout.addWidget(rows_per_page_label)
        
        # Page size combo
        self.page_size_combo = CustomComboBox()
        self.page_size_combo.addItems(["10", "25", "50", "100"])
        self.page_size_combo.setCurrentText(str(self.page_size))
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        self.page_size_combo.setMaximumWidth(120)
        self.page_size_combo.setMinimumHeight(32)
        # Set fixed margins to prevent cutoff
        right_layout.setContentsMargins(5, 5, 5, 5)
     
        right_layout.addWidget(self.page_size_combo)
        


        
        # Add all sections to main layout with proper size ratios
        main_layout.addWidget(left_section, 1)
        main_layout.addWidget(center_section, 1)
        main_layout.addWidget(right_section, 1)
        
        # Set initial button states
        self._update_button_states()
        
        # Style the pagination controls
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply styling to the pagination controls."""
        button_style = f"""
            QPushButton {{
                border: 1px solid {COLORS['gray_300']};
                border-radius: {RADIUS['sm']};
                background: {COLORS['white']};
                color: {COLORS['gray_700']};
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_100']};
                border-color: {COLORS['gray_400']};
            }}
            QPushButton:pressed {{
                background: {COLORS['gray_200']};
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_50']};
                border-color: {COLORS['gray_200']};
                color: {COLORS['gray_400']};
            }}
        """
        
        label_style = f"""
            QLabel {{
                color: {COLORS['gray_700']};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """
        
        records_label_style = f"""
            QLabel {{
                font-weight: bold; 
                color: {COLORS['primary_dark']};
                padding: 5px 10px;
                border: none;
                background: transparent;
                font-size: 13px;
            }}
        """
        

        
        self.first_btn.setStyleSheet(button_style)
        self.prev_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.last_btn.setStyleSheet(button_style)
        self.page_info.setStyleSheet(label_style)
        self.records_label.setStyleSheet(records_label_style)
       
    
    def _update_button_states(self):
        """Update button enabled/disabled states based on current page."""
        total_pages = self.get_total_pages()
        
        # Update buttons
        self.first_btn.setEnabled(self.current_page > 1)
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)
        self.last_btn.setEnabled(self.current_page < total_pages)
        
        # Update page info
        self.page_info.setText(f"Page {self.current_page} of {total_pages}")
        
        # Update total counts
        self.records_label.setText(f"Total Records: {self.total_items}")
    
    def get_total_pages(self):
        """Calculate total number of pages."""
        if self.page_size <= 0:
            return 1
        
        return max(1, (self.total_items + self.page_size - 1) // self.page_size)
    
    def _go_to_first(self):
        """Go to first page."""
        if self.current_page != 1:
            self.set_page(1)
    
    def _go_to_prev(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.set_page(self.current_page - 1)
    
    def _go_to_next(self):
        """Go to next page."""
        if self.current_page < self.get_total_pages():
            self.set_page(self.current_page + 1)
    
    def _go_to_last(self):
        """Go to last page."""
        last_page = self.get_total_pages()
        if self.current_page != last_page:
            self.set_page(last_page)
    
    def _on_page_size_changed(self, text):
        """Handle page size change."""
        try:
            new_size = int(text)
            if new_size != self.page_size:
                old_page = self.current_page
                self.page_size = new_size
                
                # Adjust current page if needed
                total_pages = self.get_total_pages()
                if self.current_page > total_pages:
                    self.current_page = total_pages
                
                self._update_button_states()
                
                # Emit signal only if there's a change
                if old_page != self.current_page or new_size != self.page_size:
                    self.pageChanged.emit(self.current_page, self.page_size)
        except ValueError:
            pass  # Ignore invalid values
    
    def set_page(self, page):
        """Set the current page."""
        if page < 1 or page > self.get_total_pages():
            return
        
        if page != self.current_page:
            self.current_page = page
            self._update_button_states()
            self.pageChanged.emit(self.current_page, self.page_size)
    
    def set_total_items(self, total):
        """Update total number of items."""
        if total != self.total_items:
            self.total_items = total
            
            # Adjust current page if needed
            total_pages = self.get_total_pages()
            if self.current_page > total_pages:
                self.current_page = max(1, total_pages)
            
            self._update_button_states()
    
    def get_pagination_info(self):
        """Get current pagination information."""
        return {
            'current_page': self.current_page,
            'page_size': self.page_size,
            'total_items': self.total_items,
            'total_pages': self.get_total_pages()
        }

class CheckBoxDelegate(QWidget):
    """
    Custom checkbox widget for table cells.
    Provides a centered, properly styled checkbox with consistent appearance.
    """
    stateChanged = pyqtSignal(bool)
    
    def __init__(self, is_checked=False, parent=None):
        super().__init__(parent)
        
        # Set a larger fixed size for the cell to ensure the checkbox is fully visible with borders
        self.setMinimumSize(26, 26)  # Increased size to accommodate borders and padding
        
        # Create layout with sufficient spacing for proper display of checkbox
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Small margins to prevent border clipping
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Create the checkbox - using a standard QCheckBox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(is_checked)
        self.checkbox.stateChanged.connect(self._on_state_changed)
        
        # Set an explicit size policy for proper centering
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style the checkbox with bold, visible styling and consistent borders
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                border: none;
                background: transparent;
                spacing: 0px;  /* No space between box and text */
                margin: 2px;   /* Small margin to prevent border clipping */
                padding: 2px;  /* Add padding to prevent border clipping */
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['primary']};
                border-radius: 3px;
                background-color: {COLORS['white']};
                margin: 1px;   /* Small margin inside indicator */
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                image: url(resources/icons/check_24.svg);
                border: 2px solid {COLORS['primary']};  /* Consistent border width */
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS['white']};
                border: 2px solid {COLORS['gray_300']};  /* Consistent 2px border */
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {COLORS['primary_dark']};
                background-color: {COLORS['gray_50']};
            }}
            /* We've removed the transition property as it's not fully supported */
        """)
        
        # Add checkbox to layout
        layout.addWidget(self.checkbox)
        
        # Force transparent background for the widget and make it non-selectable
        self.setStyleSheet("""
            background-color: transparent !important;
            border: none;
            outline: none;
        """)
        
        # Set attribute to ensure the widget background stays transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        # Create a timer to ensure the checkbox is visible after parent changes
        QTimer.singleShot(100, self._ensure_visible)
    
    def _on_state_changed(self, state):
        """Forward the state changed signal."""
        self.stateChanged.emit(state == Qt.Checked)
    
    def isChecked(self):
        """Return current checkbox state."""
        return self.checkbox.isChecked()
    
    def setChecked(self, checked):
        """Set checkbox state."""
        self.checkbox.setChecked(checked)
    
    def _ensure_visible(self):
        """Make sure the checkbox is visible by updating its state."""
        is_checked = self.checkbox.isChecked()
        # Toggle state to force a repaint
        self.checkbox.setChecked(not is_checked)
        self.checkbox.repaint()  # Force immediate repaint
        self.checkbox.setChecked(is_checked)
        self.repaint()  # Force repaint of the whole widget
        
        # Schedule another check to ensure visibility after all layout operations complete
        QTimer.singleShot(300, self.repaint)


class SMISTable(QWidget):
 
    # Signal emitted when selection changes
    selectionChanged = pyqtSignal(list)
    
    def __init__(self, parent=None, show_pagination=True):
        super().__init__(parent)
        self._selected_rows = set()
        self._is_populating = False
        self._full_data = []  # Store complete data set
        self._filtered_data = []  # Store filtered data
        self._current_page_data = []  # Current page data
        self._show_pagination = show_pagination
        self._checkbox_column = None  # Initialize checkbox column index
        
        # Set the SMISTable widget to expand in both directions
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(2)  # Added small spacing between table and pagination
        
        # Create table widget
        self.table = QTableWidget(self)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._main_layout.addWidget(self.table)
        
        # Create pagination if needed
        if show_pagination:
            self.pagination = TablePagination(parent=self)
            self.pagination.pageChanged.connect(self._on_page_changed)
            # Create a container for pagination with proper margins
            pagination_container = QWidget()
            pagination_container.setMinimumHeight(40)  # Ensure enough height
            pagination_container.setStyleSheet("background-color: white;")
            pagination_layout = QVBoxLayout(pagination_container)
            pagination_layout.setContentsMargins(0, 5, 0, 5)  # Add vertical padding
            pagination_layout.addWidget(self.pagination)
            self._main_layout.addWidget(pagination_container)
        else:
            self.pagination = None
        
        # Initialize table
        self._initialize_table()
        
    def _initialize_table(self):
        """Initialize table with standard properties and styling."""
        # Standard table properties
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # Only allow single row selection
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setShowGrid(True)
        
        # Set up persistent tooltips for cell content
        self.table.setMouseTracking(True)
        self.table.cellEntered.connect(self._show_cell_tooltip)
        
        # Connect selection change signal to sync checkboxes with row selection
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Apply custom styling after setting other properties
        self.table.setStyleSheet(self._get_table_style())
        
    def _show_cell_tooltip(self, row, col):
        """Show tooltip with full cell content when hovering over a cell."""
        item = self.table.item(row, col)
        if item and item.text():
            QToolTip.showText(QCursor.pos(), item.text())
    
    def setup_with_headers(self, headers, checkbox_column=None):
        """
        Setup table with given headers and optional checkbox column.
        
        Args:
            headers: List of header texts
            checkbox_column: Index of column that should contain checkboxes (None for no checkboxes)
        """
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Store checkbox column index
        self._checkbox_column = checkbox_column
        
        # Get header view for configuration
        header = self.table.horizontalHeader()
        
        # If we have a checkbox column, customize its header
        if checkbox_column is not None:
            # First set the resize mode to Fixed for the checkbox column
            header.setSectionResizeMode(checkbox_column, QHeaderView.Fixed)
            
            # Calculate optimal width based on checkbox size and padding
            # Checkbox size (22px) + padding (8px each side) + border (2px each side) = 42px
            optimal_checkbox_width = 42
            
            # Set the checkbox column to the optimal width AFTER setting the mode
            header.resizeSection(checkbox_column, optimal_checkbox_width)
            
            # Create an icon for the checkbox header
            from PyQt5.QtGui import QIcon
            checkbox_item = self.table.horizontalHeaderItem(checkbox_column)
            if checkbox_item:
                # Set the icon and clear the text to show only the icon
                checkbox_item.setIcon(QIcon("resources/icons/check_24_header.svg"))
                checkbox_item.setText("")  # Clear text to show only the icon
                # Center the icon in the header
                checkbox_item.setTextAlignment(Qt.AlignCenter)
                # Set tooltip to explain the checkbox column
                checkbox_item.setToolTip("Select/Deselect All")
                
            # Apply center alignment to the entire column
            self.table.setItemDelegateForColumn(checkbox_column, 
                CenterAlignDelegate(self.table))
        
        # First, set all columns to ResizeToContents to adapt to header text
        for i in range(len(headers)):
            if i != checkbox_column:  # Skip the checkbox column
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Set a reasonable minimum section size that allows checkbox column to be small
        # but prevents other columns from being too narrow
        header.setMinimumSectionSize(20)  # Small enough for checkbox, reasonable for others
        
        # After applying ResizeToContents, get the width of each column
        # and set them to Interactive mode (but don't override the minimum section size)
        for i in range(len(headers)):
            if i != checkbox_column:
                header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Make the table expand to fill available space
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Make the last section stretch to fill remaining space, but only if there's no checkbox column
        # If there's a checkbox column, we need to manage stretching more carefully
        if checkbox_column is not None:
            # Don't stretch the last section automatically when we have a checkbox column
            header.setStretchLastSection(False)
            # Instead, set the last non-checkbox column to stretch
            last_column = len(headers) - 1
            if last_column != checkbox_column:
                header.setSectionResizeMode(last_column, QHeaderView.Stretch)
                
            # Re-apply checkbox column settings to ensure they're not overridden
            optimal_checkbox_width = 42
            header.setSectionResizeMode(checkbox_column, QHeaderView.Fixed)
            header.resizeSection(checkbox_column, optimal_checkbox_width)
        else:
            header.setStretchLastSection(True)
    
    def populate_data(self, data, id_column=None):
        """
        Populate table with data.
        
        Args:
            data: List of data rows to populate
            id_column: Column containing unique IDs for selection tracking
        """
        self._is_populating = True
        
        # Store ID column index and full data set
        self._id_column = id_column
        self._full_data = data
        self._filtered_data = data  # Initially, filtered data is the same as full data
        
        # Update pagination if enabled
        if self._show_pagination and self.pagination:
            self.pagination.set_total_items(len(data))
            self._load_current_page()
        else:
            # If no pagination, show all data
            self._populate_table_with_data(data)
        
        self._is_populating = False
    
    def _populate_table_with_data(self, data):
        """
        Populate the table widget with the given data.
        
        Args:
            data: List of data rows to populate
        """
        # Clear existing content
        self.table.clearContents()
        self.table.setRowCount(len(data))
        
        # Populate data
        for row_idx, row_data in enumerate(data):
            self._populate_row(row_idx, row_data)
    
    def _load_current_page(self):
        """Load the current page of data based on pagination settings."""
        if not self._show_pagination or not self.pagination:
            return
            
        # Calculate start and end indices for current page
        page_info = self.pagination.get_pagination_info()
        start_idx = (page_info['current_page'] - 1) * page_info['page_size']
        end_idx = min(start_idx + page_info['page_size'], len(self._filtered_data))
        
        # Get current page data
        self._current_page_data = self._filtered_data[start_idx:end_idx]
        
        # Populate table with current page data
        self._populate_table_with_data(self._current_page_data)
    
    def _on_page_changed(self, page, page_size):
        """Handle page change event from pagination control."""
        self._load_current_page()
    
    def _populate_row(self, row_idx, row_data):
        """
        Populate a single row of data.
        
        Args:
            row_idx: Row index to populate
            row_data: Data for the row (list or dict)
        """
        # Convert row_data to list if it's a dict
        data_list = row_data if isinstance(row_data, list) else list(row_data.values())
        
        for col_idx, value in enumerate(data_list):
            # For checkbox column, add a checkbox widget
            if col_idx == self._checkbox_column:
                # Get ID for selection state if available
                row_id = None
                if self._id_column is not None:
                    row_id = str(data_list[self._id_column])
                
                # First create a transparent item for the cell background
                transparent_item = QTableWidgetItem("")
                transparent_item.setBackground(Qt.transparent)
                # Make the item completely non-selectable and non-interactive
                transparent_item.setFlags(Qt.NoItemFlags)
                self.table.setItem(row_idx, col_idx, transparent_item)
                
                # Create checkbox
                is_checked = row_id in self._selected_rows if row_id else False
                checkbox = CheckBoxDelegate(is_checked)
                
                # Connect state change
                def on_state_changed(checked, r=row_idx, rid=row_id):
                    self._on_checkbox_changed(r, rid, checked)
                
                checkbox.stateChanged.connect(on_state_changed)
                
                # Add checkbox on top of transparent item
                self.table.setCellWidget(row_idx, col_idx, checkbox)
            else:
                # Regular cell with text
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def _on_checkbox_changed(self, row, row_id, is_checked):
        """Handle checkbox state changes."""
        if self._is_populating:
            return
            
        # Update selection tracking
        if row_id:
            if is_checked:
                self._selected_rows.add(row_id)
                
                # Select this specific row - use proper row selection
                # Block signals to prevent recursive calls
                self.table.blockSignals(True)
                
                # Select all items in this row (except checkbox column)
                for col in range(self.table.columnCount()):
                    if col != self._checkbox_column:  # Skip checkbox column
                        item = self.table.item(row, col)
                        if item:
                            item.setSelected(True)
                
                self.table.blockSignals(False)
                
            else:
                self._selected_rows.discard(row_id)
                
                # Deselect this specific row completely
                self.table.blockSignals(True)
                
                # Deselect all items in this row (except checkbox column)
                for col in range(self.table.columnCount()):
                    if col != self._checkbox_column:  # Skip checkbox column
                        item = self.table.item(row, col)
                        if item:
                            item.setSelected(False)
                            
                self.table.blockSignals(False)
                        
        # Emit our custom selectionChanged signal
        self.selectionChanged.emit(list(self._selected_rows))
    
    def get_selected_rows(self):
        """Get IDs of all selected rows."""
        return list(self._selected_rows)
    
    def set_id_column(self, column_index):
        """Set the column that contains unique IDs for selection tracking."""
        self._id_column = column_index
    
    def load_data(self, data):
        """Load data into the table. Alias for populate_data for compatibility."""
        self.populate_data(data, self._id_column)
    
    def set_selected_rows(self, row_ids):
        """Set selected rows by their IDs."""
        self._is_populating = True  # Prevent recursive triggers
        
        # Clear current selection first
        self.table.clearSelection()
        
        # Convert to a set of strings for consistent comparison
        self._selected_rows = set(str(row_id) for row_id in row_ids)
        
        # Update checkboxes and row selection to match
        for row in range(self.table.rowCount()):
            row_id = None
            if self._id_column is not None:
                item = self.table.item(row, self._id_column)
                if item:
                    row_id = str(item.text())
            
            is_selected = row_id in self._selected_rows if row_id else False
            
            # Update checkbox if we have one
            if self._checkbox_column is not None:
                widget = self.table.cellWidget(row, self._checkbox_column)
                if widget and hasattr(widget, 'setChecked'):
                    widget.setChecked(is_selected)
            
            # Update row selection - select each row independently
            if is_selected:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setSelected(True)
        
        self._is_populating = False
        
        # Emit our custom selectionChanged signal
        self.selectionChanged.emit(list(self._selected_rows))
    
    def clear_selection(self):
        """Clear all selections."""
        self._selected_rows.clear()
        self.table.clearSelection()
        
        # Clear all checkboxes
        if self._checkbox_column is not None:
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, self._checkbox_column)
                if widget and hasattr(widget, 'setChecked'):
                    widget.setChecked(False)
        
        # Emit our custom selectionChanged signal with empty list
        self.selectionChanged.emit([])
        
    def refresh_checkboxes(self):
        """Force refresh of all checkbox delegates to ensure visibility."""
        for row in range(self.table.rowCount()):
            col = self._checkbox_column
            if col is not None:
                widget = self.table.cellWidget(row, col)
                if widget and isinstance(widget, CheckBoxDelegate):
                    widget._ensure_visible()
    
    def _on_selection_changed(self):
        """Update checkboxes when row selection changes by clicking on rows."""
        # Skip if we're in the middle of populating data
        if self._is_populating or self._checkbox_column is None:
            return
            
        # Prevent recursive calls
        self._is_populating = True
        
        # Get all selected indexes from selection model (more reliable)
        selection_model = self.table.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        
        # Get unique selected rows (excluding checkbox column)
        selected_rows = set()
        for index in selected_indexes:
            if index.column() != self._checkbox_column:  # Ignore checkbox column selections
                selected_rows.add(index.row())
        
        # Clear our internal selection tracking first
        self._selected_rows.clear()
        
        # Update checkboxes and selection tracking based on actual row selection
        for row in range(self.table.rowCount()):
            # Get the row ID
            row_id = None
            if self._id_column is not None:
                id_item = self.table.item(row, self._id_column)
                if id_item:
                    row_id = str(id_item.text())
            
            # Get checkbox widget for this row
            checkbox_widget = self.table.cellWidget(row, self._checkbox_column)
            
            if checkbox_widget and isinstance(checkbox_widget, CheckBoxDelegate):
                # Check if this row is selected
                is_row_selected = row in selected_rows
                
                # Update checkbox state to match row selection
                checkbox_widget.setChecked(is_row_selected)
                
                # Update internal tracking
                if is_row_selected and row_id:
                    self._selected_rows.add(row_id)
        
        # Make sure checkbox column items are never selected
        if self._checkbox_column is not None:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, self._checkbox_column)
                if item and item.isSelected():
                    item.setSelected(False)
        
        self._is_populating = False
                    
        # Emit our custom selectionChanged signal
        self.selectionChanged.emit(list(self._selected_rows))
    
    def _get_table_style(self):
        """Get the standard table styling."""
        return f"""
            QTableWidget {{
                border: none;
                border-radius: {RADIUS['xl']};
                background: {COLORS['white']};
                gridline-color: {COLORS['gray_200']};
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 400;
                outline: none;
                alternate-background-color: {COLORS['gray_50']};
                show-decoration-selected: 0;
            }}
            QTableWidget:focus {{
                outline: none;
                border: none;
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLORS['gray_100']}, stop:1 {COLORS['gray_200']});
                color: {COLORS['gray_800']};
                font-family: 'Arial', 'Segoe UI', 'Poppins Bold', sans-serif;
                font-weight: 700;
                font-size: 13px;
                padding: 8px 5px;
                border: none;
                border-bottom: 3px solid {COLORS['primary']};
                border-right: 1px solid {COLORS['gray_300']};
                text-align: center;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: {RADIUS['md']};
            }}
            QHeaderView::section:last {{
                border-top-right-radius: {RADIUS['md']};
                border-right: none;
            }}
            QTableWidget::item {{
                padding: 0px;
                margin: 0px;
                border-bottom: 1px solid {COLORS['gray_200']};
                border-right: 1px solid {COLORS['gray_100']};
                background-color: transparent;
                color: {COLORS['gray_700']};
                font-weight: 500;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                font-weight: 600;
                outline: none;
            }}
            QTableWidget::item:hover:!selected {{
                background-color: {COLORS['gray_100']};
                color: {COLORS['primary_dark']};
            }}
            QTableWidget::item:focus {{
                outline: none;
                border: none;
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS['gray_50']};
            }}
            QTableWidget::item:alternate:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
            }}
            /* Force transparent background for checkbox column in all scenarios */
            QTableWidget::item:first {{
                background-color: transparent !important;
            }}
            QTableWidget::item:first:selected {{
                background-color: transparent !important;
                color: {COLORS['gray_700']} !important;
            }}
            QTableWidget::item:first:hover {{
                background-color: transparent !important;
            }}
            QTableWidget::item:first:alternate {{
                background-color: transparent !important;
            }}
            QTableWidget::item:first:alternate:selected {{
                background-color: transparent !important;
                color: {COLORS['gray_700']} !important;
            }}
            /* More specific selectors to ensure checkbox background stays transparent */
            QTableWidget::item:first:focus {{
                background-color: transparent !important;
            }}
            QTableWidget::item:first:active {{
                background-color: transparent !important;
            }}
            QTableWidget::item:first:disabled {{
                background-color: transparent !important;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['gray_100']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['gray_300']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['gray_400']};
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {COLORS['gray_100']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {COLORS['gray_300']};
                border-radius: 6px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {COLORS['gray_400']};
            }}
            QToolTip {{
                background: {COLORS['gray_800']};
                color: {COLORS['gray_50']};
                border: 2px solid {COLORS['primary']};
                border-radius: {RADIUS['md']};
                padding: 12px 16px;
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 500;
                max-width: 400px;
            }}
        """