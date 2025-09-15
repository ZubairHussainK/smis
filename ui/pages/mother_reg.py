"""Mother Registration management page UI implementation."""
import os
import sys

# Add the project root to the path when running this file directly
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# PyQt5 imports
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QLineEdit, QMessageBox, QHeaderView, QTableWidgetItem,
    QScrollArea, QSplitter, QTextEdit, QGroupBox, 
    QFormLayout, QCheckBox, QDateEdit, QSpinBox, QTabWidget, QDialog, 
    QDialogButtonBox, QSizePolicy, QApplication
)
from ui.components.custom_combo_box import CustomComboBox
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp, QTimer, QEvent, QObject
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator

# Import SMISTable for enhanced table functionality
from ui.components.custom_table import SMISTable

# Internal imports
from models.database import Database
from config.settings import STUDENT_FIELDS
from ui.components.custom_date_picker import CustomDateEdit
from ui.components.custom_combo_box import CustomComboBox
from ui.components.form_components import (
    FormModel, InputField, FormLabel
)
from resources.styles import (
     get_global_styles, COLORS, RADIUS, SPACING_LG, SPACING_MD, SPACING_SM,
    FONT_MEDIUM, FONT_SEMIBOLD, FONT_REGULAR, PRIMARY_COLOR, FOCUS_BORDER_COLOR
)

# Form styling utilities
class FormStyleManager:
    """Simplified form styling manager with focused responsibilities."""
    
    @staticmethod
    def apply_form_container_style(container):
        """Apply clean styling to form container."""
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        
    @staticmethod
    def ensure_field_transparency(field_container):
        """Ensure form field container has transparent background."""
        if field_container and hasattr(field_container, 'setAutoFillBackground'):
            field_container.setAutoFillBackground(False)
            field_container.setStyleSheet("background-color: white;")
            
            # Fix any label children
            for child in field_container.findChildren(QLabel):
                child.setAutoFillBackground(False)
                if hasattr(child, 'enforceStyle'):
                    child.enforceStyle()
    


class MotherRegPage(QWidget):
    def _view_details(self):
        """Show details of the selected student record (in MotherReg page)."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select a record to view details.")
            return
            
        # Get the selected row from the table
        student_id = selected_ids[0]
        for row in range(self.mothers_table.table.rowCount()):
            item = self.mothers_table.table.item(row, 1)
            if item and item.text() == student_id:
                # Get values from the row
                name = self.mothers_table.table.item(row, 2).text() if self.mothers_table.table.item(row, 2) else ""
                father = self.mothers_table.table.item(row, 3).text() if self.mothers_table.table.item(row, 3) else ""
                class_name = self.mothers_table.table.item(row, 4).text() if self.mothers_table.table.item(row, 4) else ""
                section = self.mothers_table.table.item(row, 5).text() if self.mothers_table.table.item(row, 5) else ""
                school = self.mothers_table.table.item(row, 6).text() if self.mothers_table.table.item(row, 6) else ""
                
                details = (
                    f"ID: {student_id}\n"
                    f"Name: {name}\n"
                    f"Father: {father}\n"
                    f"Class: {class_name}\n"
                    f"Section: {section}\n"
                    f"School: {school}\n"
                )
                QMessageBox.information(self, "Student Details", details)
                return
                
        QMessageBox.warning(self, "Error", "Could not find selected student data.")
        
    def _delete_mother(self):
        """Delete the selected mother record."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select a mother to delete.")
            return
            
        # Find student name from ID
        student_id = selected_ids[0]
        student_name = ""
        
        # Look up the name from the table
        for row in range(self.mothers_table.table.rowCount()):
            item = self.mothers_table.table.item(row, 1)
            if item and item.text() == student_id:
                name_item = self.mothers_table.table.item(row, 2)
                if name_item:
                    student_name = name_item.text()
                break
        
        reply = QMessageBox.question(
            self, 
            "Delete Mother", 
            f"Are you sure you want to delete mother for student: {student_name}?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Implement actual deletion logic here
            QMessageBox.information(self, "Deleted", f"Mother for '{student_name}' deleted.")
            # Refresh the table
            self._load_data()
            
    def _edit_mother(self):
        """Edit the selected mother record."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select a mother to edit.")
            return
            
        # Find student name from ID
        student_id = selected_ids[0]
        student_name = ""
        
        # Look up the name from the table
        for row in range(self.mothers_table.table.rowCount()):
            item = self.mothers_table.table.item(row, 1)
            if item and item.text() == student_id:
                name_item = self.mothers_table.table.item(row, 2)
                if name_item:
                    student_name = name_item.text()
                break
                
        QMessageBox.information(
            self, 
            "Edit Mother", 
            f"Editing mother for student: {student_name}\n(Edit form not yet implemented)"
        )
    def _on_double_click(self, item):
        """Handle double-click on a table row to view details or edit."""
        # Just forward to view details
        self._view_details()
        
    def _on_selection_changed(self):
        """Enable/disable edit/delete/view buttons based on selection."""
        selected_ids = self.mothers_table.get_selected_rows()
        has_selection = bool(selected_ids)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.view_details_btn.setEnabled(has_selection)
        
    def _on_table_selection_changed(self, selected_ids):
        """Handle selection changes from the SMISTable component."""
        # Update the selected IDs list
        self.selected_snos = set(selected_ids)
        # Update button states
        self._on_selection_changed()
        # Update the summary display
        self._update_selected_summary()
    def get_filters(self):
        """Get the current filter values.
        
        Returns:
            dict: Dictionary with filter values
        """
        return {
            "school": self.school_combo.currentText(),
            "class": self.class_combo.currentText(),
            "section": self.section_combo.currentText(),
            "status": self.status_filter_combo.currentText()
        }
        
    def _apply_filters(self):
        """Reload data from database when filters change."""
        # Update filter info label
        filters = self.get_filters()
        filter_texts = []
        
        if filters["school"] and filters["school"] != "Please Select School" and filters["school"] != "All Schools":
            filter_texts.append(f"School: {filters['school']}")
            
        if filters["class"] and filters["class"] != "Please Select Class" and filters["class"] != "All Classes":
            filter_texts.append(f"Class: {filters['class']}")
            
        if filters["section"] and filters["section"] != "Please Select Section" and filters["section"] != "All Sections":
            filter_texts.append(f"Section: {filters['section']}")
            
        if filters["status"] and filters["status"] != "All Status":
            filter_texts.append(f"Status: {filters['status']}")
        
        if filter_texts:
            self.filter_info_label.setText("Filters: " + " | ".join(filter_texts))
        else:
            self.filter_info_label.setText("No filters applied")
            
        # Reload data with new filters
        self._load_data()
    def _show_add_form(self):
        """Show the form for adding mother/guardian information."""
        try:
            if not self._validate_form_frame():
                return
            
            if self.form_frame.isVisible():
                return
            
            self._setup_form_layout()
            self.form_frame.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open form:\n{str(e)}")
    
    def _validate_form_frame(self):
        """Validate that form frame is available."""
        if not hasattr(self, 'form_frame') or not self.form_frame:
            QMessageBox.critical(self, "Error", "Form frame not available.")
            return False
        return True
    
    def _setup_form_layout(self):
        """Setup the main form layout with three containers."""
        # Clear existing layout
        current_layout = self.form_frame.layout()
        if current_layout:
            QWidget().setLayout(current_layout)
        
        # Apply form styling
        FormStyleManager.apply_form_container_style(self.form_frame)
        
        # Create main layout
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(10, 10, 5, 10)
        form_layout.setSpacing(20)
        
        # Add containers
        form_layout.addWidget(self._create_recipient_container())
        form_layout.addWidget(self._create_fields_container(), 1)
        form_layout.addWidget(self._create_actions_container())
        
        self.form_frame.setLayout(form_layout)
        self._on_recipient_type_changed()  # Set initial field visibility
    
    def _create_recipient_container(self):
        """Create the recipient type selection container."""
        container = QFrame()
        container.setObjectName("RecipientTypeContainer")
        container.setStyleSheet("""
            QFrame#RecipientTypeContainer {
                background-color: white;
                border-radius: 8px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 25, 5)
        layout.setSpacing(0)
        

        self.recipient_combo = CustomComboBox()
        self.recipient_combo.addItems(["Principal", "Alternate Guardian"])
        self.recipient_combo.setCurrentText("Principal")
        self.recipient_combo.currentTextChanged.connect(self._on_recipient_type_changed)
        

        layout.addWidget(self.recipient_combo)
        layout.addStretch()
        
        return container
    
    def _create_fields_container(self):
        """Create the scrollable form fields container."""
        container = QFrame()
        container.setObjectName("FormFieldsContainer")
        container.setStyleSheet("""
            QFrame#FormFieldsContainer {
                background-color: white;
                border-radius: 8px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(10)
        
        
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        scroll_widget = QWidget()
        # Removed maximum width restriction to allow full expansion
        scroll_widget.setStyleSheet("QWidget { background-color: white; }")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(10)
        
        # Create form grid
        self.form_grid = QGridLayout()
        self.form_grid.setVerticalSpacing(5)  # Even more spacing
        self.form_grid.setHorizontalSpacing(25)  # Also increased horizontal
        self.form_grid.setContentsMargins(0, 0, 0, 0)  # More margins all around
        

        # Initialize field storage and create fields
        self.mother_fields = {}
        self._create_form_fields()
    
        scroll_layout.addLayout(self.form_grid)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return container
    
    def _create_actions_container(self):
        """Create the action buttons container."""
        container = QFrame()
        container.setObjectName("ActionButtonsContainer")
        container.setStyleSheet("""
            QFrame#ActionButtonsContainer {
                background-color: white;
                border-radius: 8px;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create buttons
        reset_btn = QPushButton("Reset")
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save Information")
        apply_all_checkbox = QCheckBox("Apply to all filtered rows")
        
        # Apply differentiated button styling
        reset_btn.setStyleSheet(self.styles['button_secondary'])  # Secondary for reset

        cancel_btn.setStyleSheet(self.styles['button_warning'])   # Warning for cancel

        save_btn.setStyleSheet(self.styles['button_success'])     # Success for save

        
        # Connect signals
        reset_btn.clicked.connect(self._reset_form)
        cancel_btn.clicked.connect(lambda: self.form_frame.setVisible(False))
        save_btn.clicked.connect(lambda: self._save_form_data(apply_all_checkbox.isChecked()))
        
        # Layout buttons
        layout.addWidget(reset_btn)
        layout.addWidget(cancel_btn)
        layout.addWidget(apply_all_checkbox)
        layout.addStretch()
        layout.addWidget(save_btn)
        
        return container
            
    def _enforce_custom_styles(self):
        """Enforce custom component styles with highest priority possible."""
        try:
            # Apply field styling to form fields
            if hasattr(self, 'mother_fields'):
                for field_container in self.mother_fields.values():
                    FormStyleManager.ensure_field_transparency(field_container)
                    
                    # Apply styling to actual field widget
                    if field_container and field_container.layout():
                        layout = field_container.layout()
                        if layout.count() >= 2:
                            widget = layout.itemAt(1).widget()
                            
            
            # Additional focused protection for the recipient combo specifically
            if hasattr(self, 'recipient_combo') and isinstance(self.recipient_combo, CustomComboBox):
                # Remove any inherited styles first
                self.recipient_combo.setStyleSheet("")
                # Then force its own styling
                self.recipient_combo.enforceStyle()
                # Ensure consistent height
              
                
        except Exception as e:
            print(f"Style enforcement error: {e}")

    def _create_form_fields(self):
        """Create all form fields using configuration-driven approach."""
        # Define field configurations
        self.principal_fields = [
            ("household_size", "Household Size", "spinbox"),
            ("household_head_name", "Household Head Name", "text"),
            ("mother_name", "Mother's Name", "text"),
            ("mother_marital_status", "Mother's Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("mother_cnic", "Mother's CNIC (13 digits)", "cnic"),
            ("mother_cnic_doi", "Mother's CNIC Date of Issue", "date"),
            ("mother_cnic_exp", "Mother's CNIC Expiry Date", "date"),
            ("mother_mwa", "Mother's MWA (11 digits)", "mwa"),
        ]
        
        self.guardian_fields = [
            ("household_size", "Household Size", "spinbox"),
            ("household_head_name", "Household Head Name", "text"),
            ("guardian_name", "Guardian Name", "text"),
            ("guardian_cnic", "Guardian CNIC (13 digits)", "cnic"),
            ("guardian_cnic_doi", "Guardian CNIC Date of Issue", "date"),
            ("guardian_cnic_exp", "Guardian CNIC Expiry Date", "date"),
            ("guardian_marital_status", "Guardian Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("guardian_mwa", "Guardian MWA (11 digits)", "mwa"),
            ("guardian_phone", "Guardian Phone (11 digits)", "phone"),
            ("guardian_relation", "Guardian Relation", "combo", ["Father", "Mother", "Uncle", "Aunt", "Grandfather", "Grandmother", "Other"]),
        ]
        
        # Create unique fields set to avoid duplicates
        all_unique_fields = []
        field_names_added = set()
        
        # Add all fields but avoid duplicates
        for field_config in self.principal_fields + self.guardian_fields:
            field_name = field_config[0]
            if field_name not in field_names_added:
                all_unique_fields.append(field_config)
                field_names_added.add(field_name)
        
        self._add_fields_to_grid(all_unique_fields)
    
    def _add_fields_to_grid(self, fields):
        """Add field configurations to the grid layout."""
        row, col = 0, 0
        
        for field_name, label_text, field_type, *extras in fields:
            field_widget = self._create_field_widget(field_name, label_text, field_type, extras)
            self.mother_fields[field_name] = field_widget
            
            self.form_grid.addWidget(field_widget, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _create_field_widget(self, field_name, label_text, field_type, extra_params=None):
        """Create a form field widget with label and input."""
        container = QWidget()
        container.setObjectName(f"FormFieldContainer_{field_name}")
        FormStyleManager.ensure_field_transparency(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)  # More margins, especially bottom
        layout.setSpacing(10)  # Even more spacing between label and input
        container.setMinimumHeight(90)  # Minimum height for consistent spacing
        # Remove maximum height to allow flexibility
        container.setMinimumWidth(250)  # Minimum width but allow expansion
        
        # Make container responsive
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create label
        label = FormLabel(label_text)
        
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label)
        
        # Create input widget based on type
        widget = self._create_input_widget(field_type, field_name, label_text, extra_params)
        # widget.setMinimumHeight(40)  # Minimum height instead of fixed
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout.addWidget(widget)
        
        # Add stretch to prevent cutting
        layout.addStretch(1)
        
        return container
    
    def _create_input_widget(self, field_type, field_name, label_text, extra_params):
        """Create the appropriate input widget based on field type."""
        if field_type in ["text", "cnic", "phone", "mwa"]:
            widget = InputField.create_field(
                "cnic" if field_type == "cnic" else "phone" if field_type in ["phone", "mwa"] else "text", 
                label_text
            )
            widget.setObjectName(f"FormField_{field_name}")
            
        elif field_type == "date":
            widget = CustomDateEdit(icon_only=True)
            widget.setDate(QDate.currentDate())
            widget.setObjectName(f"CustomDateEdit_{field_name}")
            
            # Simple style enforcement without timers
            if hasattr(widget, 'enforceStyle'):
                widget.enforceStyle()
                
        elif field_type == "combo":
            widget = CustomComboBox()
            widget.setObjectName(f"CustomComboBox_{field_name}")
            if extra_params and len(extra_params) > 0:
                widget.addItems(extra_params[0])
                
        elif field_type == "spinbox":
            widget = InputField.create_field("spinbox", label_text)
            widget.setObjectName(f"FormField_{field_name}")
            
        else:
            # Default to text field
            widget = InputField.create_field("text", label_text)
            widget.setObjectName(f"FormField_{field_name}")
        
        return widget

    def _on_recipient_type_changed(self):
        """Show/hide fields based on recipient type selection."""
        recipient_type = self.recipient_combo.currentText()
        
        # Hide all fields first
        for field_name in self.mother_fields:
            self.mother_fields[field_name].setVisible(False)
        
        if recipient_type == "Principal":
            # Show only principal (mother) fields
            for field_name, _, _, *_ in self.principal_fields:
                if field_name in self.mother_fields:
                    self.mother_fields[field_name].setVisible(True)
        else:  # Alternate Guardian
            # Show only guardian fields
            for field_name, _, _, *_ in self.guardian_fields:
                if field_name in self.mother_fields:
                    self.mother_fields[field_name].setVisible(True)

    def _reset_form(self):
        """Reset all form fields to default values."""
        for field_name, container in self.mother_fields.items():
            # Find the actual input widget inside the container
            layout = container.layout()
            if layout and layout.count() >= 2:
                widget = layout.itemAt(1).widget()  # Second item is the input widget
                
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QSpinBox):
                    widget.setValue(1)
                elif isinstance(widget, CustomComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, QDateEdit) or isinstance(widget, CustomDateEdit):
                    widget.setDate(QDate.currentDate())
    

    def _save_form_data(self, apply_all):
        """Save the form data to selected students."""
        try:
            # Get target students
            target_snos = []
            if apply_all:
                for r in range(self.mothers_table.rowCount()):
                    s_no_item = self.mothers_table.item(r, 1)
                    if s_no_item and s_no_item.text().strip():
                        target_snos.append(s_no_item.text().strip())
            else:
                target_snos = list(self.selected_snos)
            
            if not target_snos:
                QMessageBox.warning(self, "No Students Selected", 
                                  "Select one or more students (checkbox), or tick 'Apply to all filtered rows'.")
                return
            
            # Collect form data
            info = {}
            recipient_type = self.recipient_combo.currentText()
            
            # Get visible fields based on recipient type
            visible_fields = self.principal_fields if recipient_type == "Principal" else self.guardian_fields
            
            for field_name, _, _, *_ in visible_fields:
                if field_name in self.mother_fields:
                    container = self.mother_fields[field_name]
                    layout = container.layout()
                    if layout and layout.count() >= 2:
                        widget = layout.itemAt(1).widget()
                        
                        if isinstance(widget, QLineEdit):
                            info[field_name] = widget.text().strip()
                        elif isinstance(widget, QSpinBox):
                            info[field_name] = widget.value()
                        elif isinstance(widget, CustomComboBox):
                            info[field_name] = widget.currentText()
                        elif isinstance(widget, QDateEdit) or isinstance(widget, CustomDateEdit):
                            info[field_name] = widget.date().toString("yyyy-MM-dd")
            
            # Save to database
            updated_count = 0
            if len(target_snos) == 1:
                updated = self.db.update_mother_info(target_snos[0], info)
                updated_count = 1 if updated else 0
            else:
                updated_count = self.db.update_mother_info_bulk(target_snos, info)
            
            if updated_count > 0:
                QMessageBox.information(self, "Saved", 
                                      f"{recipient_type} information saved to {updated_count} student(s).")
                self.form_frame.setVisible(False)
                self.selected_snos.clear()
                self._load_data()
            else:
                QMessageBox.information(self, "No Changes", "Nothing to save or invalid fields.")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save information:\n{str(e)}")
    def _create_left_panel(self):
        # Main left panel container
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border-radius: {RADIUS['xl']};
                border: 1px solid {COLORS['gray_200']};
            }}
        """)
        
        # Main panel layout
        panel_layout = QVBoxLayout(left_panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(15)
        
        # Create and configure the SMISTable component
        self.mothers_table = SMISTable()
        self.mothers_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set up table headers and checkbox column
        headers = ["", "ID", "Student Name", "Father Name", "Class", "Section", "School"]
        self.mothers_table.setup_with_headers(headers, checkbox_column=0)
        
        # Connect to selection changed signal
        self.mothers_table.selectionChanged.connect(self._on_table_selection_changed)
        
        # Add table directly to the main panel layout
        panel_layout.addWidget(self.mothers_table, 1)  # Give table stretch factor 1
        
        # Create action buttons container at the bottom
        action_container = QFrame()
        action_container.setObjectName("ActionContainer")
        action_container.setStyleSheet(f"""
            QFrame#ActionContainer {{
                background: {COLORS['white']};
                border-radius: {RADIUS['md']};
                border: none;
                padding: 8px;
            }}
        """)
        
        # Action buttons layout
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        
        # Create action buttons with distinct styling based on function
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setStyleSheet(self.styles['button_secondary'])  # Outline style for edit

        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet(self.styles['button_warning'])  # Warning style for delete
    
        
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.setStyleSheet(self.styles['button_primary'])  # Primary style for view
      
        
        # Add buttons to the left side of action layout
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.view_details_btn)
        action_layout.addStretch()
        
        # Selected summary on the right
        self.selected_info_label = QLabel("Selected: 0")
        #self.selected_info_label.setStyleSheet(self.styles['label_info_style'])
        
        self.view_selected_btn = QPushButton("View Selected")
        self.view_selected_btn.setEnabled(False)
        self.view_selected_btn.setStyleSheet(self.styles['button_secondary'])  # Secondary style for supplementary view

        
        # Add summary and view selected button to right side
        action_layout.addWidget(self.selected_info_label)
        action_layout.addWidget(self.view_selected_btn)
        
        # Add action container to main panel layout
        panel_layout.addWidget(action_container)
        
        return left_panel

    def _create_right_panel(self):
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border-radius: {RADIUS['xl']};
                border: none;
                min-height: 500px;
                max-height: 700px;
            }}
        """)
        return self.form_frame

    def _load_data(self):
        """Load student data that needs mother/guardian information."""
        try:
            filters = self.get_filters()
            students = self._get_students_needing_mother_info(filters)
            self._populate_table(students)
        except Exception as e:
            print(f"Error loading student data: {e}")
            QMessageBox.warning(self, "Data Load Error", f"Failed to load student data: {str(e)}")
    
    def _get_students_needing_mother_info(self, filters=None):
        """Get students who need mother/guardian information based on filters."""
        where_clauses = [
            "is_deleted = 0",
            "status = 'Active'",
            """(
                (COALESCE(mother_name,'') = '' OR COALESCE(mother_cnic,'') = '') 
                AND 
                (COALESCE(alternate_name,'') = '' OR COALESCE(alternate_cnic,'') = '' OR COALESCE(alternate_relationship_with_mother,'') = '')
            )"""
        ]
        params = []
        
        if filters:
            # Apply filters
            if filters.get("class") and filters["class"] not in ["Please Select Class", "All Classes"]:
                where_clauses.append("class = ?")
                params.append(filters["class"])
                
            if filters.get("section") and filters["section"] not in ["Please Select Section", "All Sections"]:
                where_clauses.append("section = ?")
                params.append(filters["section"])
                
            if filters.get("status") and filters["status"] != "All Status":
                where_clauses.append("status = ?")
                params.append(filters["status"])
        
        # Build and execute query
        where_sql = f"WHERE {' AND '.join(where_clauses)}"
        sql = f"SELECT student_id, student_name, father_name, class, section FROM students {where_sql} ORDER BY student_name"
        
        rows = self.db.execute_secure_query(sql, tuple(params))
        return [self._format_student_data(row) for row in rows]
    
    def _format_student_data(self, row):
        """Format a database row into standardized student data."""
        # Convert sqlite3.Row to dict first for consistent access
        if hasattr(row, 'keys'):
            row_dict = {key: row[key] for key in row.keys()}
        else:
            row_dict = dict(row)
            
        return {
            'Student ID': row_dict.get('student_id', ''),
            'Name': row_dict.get('student_name', ''),
            'Father': row_dict.get('father_name', ''),
            'Class': row_dict.get('class', ''),
            'Section': row_dict.get('section', '')
        }

    def _populate_table(self, students):
        """Populate table with student data."""
        self._is_populating = True
        
        # Convert student data to the format expected by SMISTable
        table_data = []
        for student in students:
            row_data = self._format_student_to_row_data(student)
            table_data.append(row_data)
        
        # Use SMISTable's populate_data method with ID column specified
        self.mothers_table.populate_data(table_data, id_column=1)
        
        # If we have selected student IDs, set them in the table
        if self.selected_snos:
            self.mothers_table.set_selected_rows(list(self.selected_snos))
        
        self._is_populating = False
        self._update_selected_summary()
        
    def _format_student_to_row_data(self, student_data):
        """Format student data dictionary into a row for the table."""
        # Helper to safely get values from various data types
        def get_value(data, key, alt_keys=()):
            # Handle sqlite3.Row objects
            if hasattr(data, 'keys'):
                data_dict = {k: data[k] for k in data.keys()}
                val = data_dict.get(key)
                if val is None:
                    for k in alt_keys:
                        v = data_dict.get(k)
                        if v is not None:
                            return v
                return val
            # Handle dict-like objects
            if hasattr(data, 'get'):
                val = data.get(key)
                if val is None:
                    for k in alt_keys:
                        v = data.get(k)
                        if v is not None:
                            return v
                return val
            # Handle sequence-like access
            try:
                return data[key]
            except Exception:
                for k in alt_keys:
                    try:
                        return data[k]
                    except Exception:
                        continue
                return ""
        
        # Create row data array for SMISTable
        row_data = [""]  # Empty first cell for checkbox
        
        # Define the table columns and their mapping to data fields
        table_columns = [
            ("Student ID", []),
            ("Name", []),
            ("Father", ["Father's Name"]),
            ("Class", ["class_2025"]),
            ("Section", []),
            ("School", ["School Name", "school_name"])
        ]
        
        # Extract values for each column
        for key, alt_keys in table_columns:
            value = str(get_value(student_data, key, alt_keys))
            row_data.append(value)
            
        return row_data

    def _connect_signals(self):
        self.add_new_btn.clicked.connect(self._show_add_form)
        self.refresh_btn.clicked.connect(self._load_data)
        # Connect filter comboboxes
        self.school_combo.currentTextChanged.connect(self._apply_filters)
        self.class_combo.currentTextChanged.connect(self._apply_filters)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        self.status_filter_combo.currentTextChanged.connect(self._apply_filters)
        # Table signals
        # selectionChanged is already connected in table setup
        self.mothers_table.table.itemDoubleClicked.connect(self._on_double_click)
        self.edit_btn.clicked.connect(self._edit_mother)
        self.delete_btn.clicked.connect(self._delete_mother)
        self.view_details_btn.clicked.connect(self._view_details)
        # Note: itemChanged signal is now handled by SMISTable internally
        self.view_selected_btn.clicked.connect(self._view_selected_list)

    def _on_item_changed(self, item):
        """
        Legacy method for checkbox state changes.
        Now handled directly by the TableCheckboxCell widget's signal connections.
        """
        pass

    def _update_selected_summary(self):
        count = len(self.selected_snos)
        if self.selected_info_label:
            self.selected_info_label.setText(f"Selected: {count}")
        if self.view_selected_btn:
            self.view_selected_btn.setEnabled(count > 0)

    def _view_selected_list(self):
        """Show a dialog listing selected students (S# and Name if visible)."""
        selected_list = []
        # Try to get names for currently visible rows
        visible_map = {}
        for r in range(self.mothers_table.rowCount()):
            sno_item = self.mothers_table.item(r, 1)
            name_item = self.mothers_table.item(r, 2)
            if sno_item and name_item:
                visible_map[sno_item.text().strip()] = name_item.text().strip()
        for sno in sorted(self.selected_snos):
            name = visible_map.get(sno, "(hidden)")
            selected_list.append(f"{sno} - {name}")
        if not selected_list:
            QMessageBox.information(self, "Selected Students", "No students selected.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Selected Students")
        v = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText("\n".join(selected_list))
        v.addWidget(text)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        v.addWidget(btns)
        dlg.exec_()

    # Add stubs for form and filter logic as needed, or copy from StudentPage and adapt for mothers.
    """Modern Mother Registration management page (structure based on StudentPage)."""
    
    # Signals
    mother_added = pyqtSignal(dict)
    mother_updated = pyqtSignal(dict)
    mother_deleted = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Initialize core components
        self._init_core_attributes()
        self._init_ui_components()
        self._setup_ui()
        self._load_initial_data()
    
    def _init_core_attributes(self):
        """Initialize core attributes and services."""
        # Styling and data services
        self.styles = get_global_styles()
        self.form_style_manager = FormStyleManager()
        self.db = Database()
        
        # Form state
        self.current_mother_id = None
        self.is_editing = False
        self._is_populating = False
        
        # Selection tracking
        self.selected_snos = set()
        
        # Apply base styles
        self.apply_stylelogin_styles()
    
    def _init_ui_components(self):
        """Initialize UI component references."""
        # Form fields
        self.mother_fields = {}
        
        # Filter components
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.status_filter_combo = None
        self.filter_info_label = None
        
        # Action components
        self.save_btn = None
        self.cancel_btn = None
        self.view_selected_btn = None
        self.edit_btn = None
        self.delete_btn = None
        self.view_details_btn = None
        
        # Main UI components
        self.mothers_table = None
        self.form_frame = None
        self.selected_info_label = None
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        self._init_ui()
        self._connect_signals()
    
    def _load_initial_data(self):
        """Load initial data and filters."""
        self._load_initial_filter_data()
        self._load_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(8)  # Reduced spacing
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        
        # Create filter section
        filter_frame = self._create_filter_section()
        main_layout.addWidget(filter_frame)
        
        splitter = QSplitter(Qt.Horizontal)
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        # Give more space to the table panel by adjusting splitter sizes
        splitter.setSizes([650, 400])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        main_layout.addWidget(splitter)
        self.form_frame.setVisible(False)

    def _create_filter_section(self):
        """Create enhanced filter section with 2x2 grid layout for mother registration."""
        from resources.styles import COLORS, get_attendance_styles
        
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background:white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                padding: 8px;
                max-height: 120px;
            }}
        """)
        
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setSpacing(4)
        filters_layout.setContentsMargins(15, 0, 15, 0)
        
        # Create grid layout for filters
        filter_grid = QGridLayout()
        filter_grid.setSpacing(6)
        filter_grid.setVerticalSpacing(4)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        

        
        self.school_combo = CustomComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        
        self.class_combo = CustomComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        
        self.section_combo = CustomComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        
        self.status_filter_combo = CustomComboBox()
        self.status_filter_combo.addItems([
            "All Status", "Active", "Inactive", "Duplicate"
        ])
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)          # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)           # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)         # Row 2, Col 1
        filter_grid.addWidget(self.status_filter_combo, 1, 1)   # Row 2, Col 2
        filters_layout.addLayout(filter_grid)
        
        # Add filter information label
        self.filter_info_label = QLabel("No filters applied")
        self.filter_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray_600']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 8px;
                background: {COLORS['gray_100']};
                border-radius: 4px;
                border: 1px solid {COLORS['gray_200']};
                margin-top: 2px;
                max-height: 22px;
            }}
        """)
        filters_layout.addWidget(self.filter_info_label)
        
        # Note: Signal connections are handled in _connect_signals method
        
        return filters_frame
        
    def _create_header(self):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 8px;
                max-height: 60px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        page_title = QLabel("Mother Registration")
        page_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-family: 'Poppins Bold';
                font-weight: 700;
                margin: 0px;
                padding: (0px, 0px, 5px, 5px);
                border: none;
                background: transparent;
            }
        """)
        title_layout.addWidget(page_title)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        self.add_new_btn = QPushButton("➕ Add Mother")
        self.add_new_btn.setStyleSheet(self.styles['button_success'])  # Success style for add actions
    
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(self.styles['button_secondary'])  # Secondary style for utility actions
 
        actions_layout.addWidget(self.add_new_btn)
        actions_layout.addWidget(self.refresh_btn)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(actions_layout)
        return header_frame

    def _load_initial_filter_data(self):
        """Load initial data for filter dropdowns."""
        try:
            # Clear existing items first
            self.school_combo.clear()
            self.class_combo.clear()
            self.section_combo.clear()
            
            # Add default "All" options
            self.school_combo.addItem("All Schools")
            self.class_combo.addItem("All Classes")
            self.section_combo.addItem("All Sections")
            
            # Load schools
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
                
            # Load classes
            classes = self.db.get_classes()
            for class_name in classes:
                self.class_combo.addItem(class_name)
                
            # Load sections
            sections = self.db.get_sections()
            for section_name in sections:
                self.section_combo.addItem(section_name)
                
            print(f"Loaded filter data in mother registration page")
        except Exception as e:
            print(f"❌ Error loading filter data: {e}")
            # Add some default options if database fails
            self.school_combo.addItems(["Pine Valley School", "Green Park Academy", "Sunshine High"])
            self.class_combo.addItems(["Class 1", "Class 2", "Class 3"])
            self.section_combo.addItems(["A", "B", "C"])
            
    def _load_schools_data(self):
        """Load schools from database and populate school combo."""
        try:
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
            print(f"Loaded {len(schools)} schools in mother registration page")
        except Exception as e:
            print(f"❌ Error loading schools: {e}")
            # Add some default options if database fails
            self.school_combo.addItems(["Pine Valley School", "Green Park Academy", "Sunshine High"])

    def _load_classes_data(self, school_id=None):
        """Load classes from database and populate class combo."""
        try:
            classes = self.db.get_classes(school_id)
            for class_name in classes:
                self.class_combo.addItem(class_name)
            print(f"Loaded {len(classes)} classes in mother registration page")
        except Exception as e:
            print(f"❌ Error loading classes: {e}")
            # Add some default options if database fails
            self.class_combo.addItems([f"Class {i}" for i in range(1, 13)])

    def _load_sections_data(self, school_id=None, class_name=None):
        """Load sections from database and populate section combo."""
        try:
            sections = self.db.get_sections(school_id, class_name)
            for section_name in sections:
                self.section_combo.addItem(section_name)
            print(f"Loaded {len(sections)} sections in mother registration page")
        except Exception as e:
            print(f"❌ Error loading sections: {e}")
            # Add some default options if database fails
            self.section_combo.addItems(["A", "B", "C", "D", "E"])

    def apply_stylelogin_styles(self):
        """Apply styles from stylelogin.qss for unified look."""
        qss_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "resources", "stylelogin.qss"
        )
        qss_path = os.path.normpath(qss_path)  # Windows/Linux safe
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"⚠️ stylelogin.qss not found at: {qss_path}")

    # ...
    # For brevity, copy all other methods from StudentPage, replacing 'student' with 'mother', and update labels/icons as needed.


# Standalone class for directly running the Mother Registration form
class StandaloneMotherRegApp(QApplication):
    """Standalone application to run just the Mother Registration form."""
    
    def __init__(self, argv):
        """Initialize the standalone application."""
        super().__init__(argv)
        self.setStyle("Fusion")
        self.setApplicationName("Mother Registration")
        
        # Initialize database connection
        try:
            from models.database import Database
            self.db = Database()
            print("Database connection established")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
            self.db = None
        
        # Create main window
        self.main_window = QWidget()
        self.main_window.setWindowTitle("Mother Registration Form")
        self.main_window.setGeometry(100, 100, 1200, 800)
        
        # Create layout
        main_layout = QVBoxLayout(self.main_window)
        
        # Add mother registration page
        self.mother_reg_page = MotherRegPage()
        main_layout.addWidget(self.mother_reg_page)
        
        # Show the window
        self.main_window.show()


# This allows the file to be run directly
if __name__ == "__main__":
    import sys
    print("Running Mother Registration form standalone...")
    app = StandaloneMotherRegApp(sys.argv)
    sys.exit(app.exec_())
