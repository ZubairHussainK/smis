"""
Simplified Mother Form Widget - Extracted from mother_reg.py for better maintainability.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QScrollArea,
                           QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from ui.components.custom_date_picker import CustomDateEdit
from ui.components.custom_combo_box import CustomComboBox
from ui.components.form_components import FormLabel, InputField, apply_form_styles

class MotherFormWidget(QWidget):
    """Clean, reusable mother registration form widget."""
    
    # Signals
    form_submitted = pyqtSignal(dict, bool)  # (data, apply_to_all)
    form_cancelled = pyqtSignal()
    form_reset = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the mother form widget."""
        super().__init__(parent)
        self.fields = {}
        self.recipient_combo = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the UI with three clear containers."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 30, 20)
        main_layout.setSpacing(20)
        
        # Container 1: Recipient Type Selection
        main_layout.addWidget(self._create_recipient_container())
        
        # Container 2: Form Fields
        form_container = self._create_form_container()
        main_layout.addWidget(form_container, 1)
        
        # Container 3: Action Buttons
        main_layout.addWidget(self._create_actions_container())
        
    def _create_recipient_container(self):
        """Create the recipient type selection container."""
        container = QFrame()
        container.setObjectName("RecipientTypeContainer")
        container.setStyleSheet("""
            QFrame#RecipientTypeContainer {
                background-color: transparent;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        label = QLabel("Recipient Type:")
        label.setStyleSheet("font-weight: 600; color: #495057; font-size: 14px;")
        
        self.recipient_combo = CustomComboBox()
        self.recipient_combo.addItems(["Principal", "Alternate Guardian"])
        self.recipient_combo.setCurrentText("Principal")
        
        layout.addWidget(label)
        layout.addWidget(self.recipient_combo, 2)
        layout.addStretch()
        
        return container
        
    def _create_form_container(self):
        """Create the scrollable form fields container."""
        container = QFrame()
        container.setObjectName("FormFieldsContainer")
        container.setStyleSheet("""
            QFrame#FormFieldsContainer {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setMaximumWidth(550)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 10, 5)
        scroll_layout.setSpacing(10)
        
        # Form grid
        self.form_grid = QGridLayout()
        self.form_grid.setVerticalSpacing(15)
        self.form_grid.setHorizontalSpacing(20)
        self.form_grid.setContentsMargins(5, 5, 10, 5)
        
        # Create form fields
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
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Create buttons
        self.reset_btn = QPushButton("Reset")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn = QPushButton("Save Information")
        self.apply_all_checkbox = QCheckBox("Apply to all filtered rows")
        
        # Apply consistent button styling
        button_style = """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
        
        for btn in [self.reset_btn, self.cancel_btn, self.save_btn]:
            btn.setStyleSheet(button_style)
        
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.apply_all_checkbox)
        layout.addStretch()
        layout.addWidget(self.save_btn)
        
        return container
        
    def _create_form_fields(self):
        """Create form fields based on configuration."""
        # Field configurations
        principal_fields = [
            ("household_size", "Household Size", "spinbox"),
            ("mother_name", "Mother's Name", "text"),
            ("mother_marital_status", "Mother's Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("mother_cnic", "Mother's CNIC (13 digits)", "cnic"),
            ("mother_cnic_doi", "Mother's CNIC Date of Issue", "date"),
            ("mother_cnic_exp", "Mother's CNIC Expiry Date", "date"),
            ("mother_mwa", "Mother's MWA (11 digits)", "mwa"),
        ]
        
        guardian_fields = [
            ("household_name", "Household Name", "text"),
            ("guardian_cnic", "Guardian CNIC (13 digits)", "cnic"),
            ("guardian_cnic_doi", "Guardian CNIC Date of Issue", "date"),
            ("guardian_cnic_exp", "Guardian CNIC Expiry Date", "date"),
            ("guardian_marital_status", "Guardian Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("guardian_mwa", "Guardian MWA (11 digits)", "mwa"),
            ("guardian_phone", "Guardian Phone (11 digits)", "phone"),
            ("guardian_relation", "Guardian Relation", "combo", ["Father", "Mother", "Uncle", "Aunt", "Grandfather", "Grandmother", "Other"]),
        ]
        
        # Create all fields
        all_fields = principal_fields + guardian_fields
        row, col = 0, 0
        
        for field_name, label_text, field_type, *extras in all_fields:
            field_widget = self._create_field(field_name, label_text, field_type, extras)
            self.fields[field_name] = field_widget
            
            self.form_grid.addWidget(field_widget, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
                
    def _create_field(self, field_name, label_text, field_type, extras=None):
        """Create a single form field with label."""
        container = QWidget()
        container.setObjectName(f"FormFieldContainer_{field_name}")
        container.setAutoFillBackground(False)
        container.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        container.setMinimumHeight(60)
        
        # Create label
        label = FormLabel(label_text)
        label.setFixedHeight(24)
        layout.addWidget(label)
        
        # Create input widget based on type
        if field_type == "text":
            widget = InputField.create_field("text", label_text)
        elif field_type == "cnic":
            widget = InputField.create_field("cnic", label_text)
        elif field_type == "phone" or field_type == "mwa":
            widget = InputField.create_field("phone", label_text)
        elif field_type == "date":
            widget = CustomDateEdit(icon_only=True)
            widget.setDate(QDate.currentDate())
            widget.setFixedWidth(32)
        elif field_type == "combo":
            widget = CustomComboBox()
            if extras and len(extras) > 0:
                widget.addItems(extras[0])
        elif field_type == "spinbox":
            widget = InputField.create_field("spinbox", label_text)
        else:
            widget = InputField.create_field("text", label_text)
        
        # Apply consistent styling
        widget.setObjectName(f"FormField_{field_name}")
        if hasattr(widget, 'setFixedHeight'):
            widget.setFixedHeight(32)
        if hasattr(widget, 'setMinimumHeight'):
            widget.setMinimumHeight(32)
        
        layout.addWidget(widget)
        return container
        
    def setup_connections(self):
        """Setup signal connections."""
        self.reset_btn.clicked.connect(self.reset_form)
        self.cancel_btn.clicked.connect(self.form_cancelled.emit)
        self.save_btn.clicked.connect(self._on_save_clicked)
        if self.recipient_combo:
            self.recipient_combo.currentTextChanged.connect(self._on_recipient_changed)
            
    def _on_save_clicked(self):
        """Handle save button click."""
        data = self.get_form_data()
        apply_to_all = self.apply_all_checkbox.isChecked()
        self.form_submitted.emit(data, apply_to_all)
        
    def _on_recipient_changed(self):
        """Handle recipient type change."""
        recipient_type = self.recipient_combo.currentText()
        
        # Hide all fields first
        for field_name, widget in self.fields.items():
            widget.setVisible(False)
            
        # Show relevant fields
        if recipient_type == "Principal":
            principal_field_names = ["household_size", "mother_name", "mother_marital_status", 
                                   "mother_cnic", "mother_cnic_doi", "mother_cnic_exp", "mother_mwa"]
            for field_name in principal_field_names:
                if field_name in self.fields:
                    self.fields[field_name].setVisible(True)
        else:  # Alternate Guardian
            guardian_field_names = ["household_name", "guardian_cnic", "guardian_cnic_doi", 
                                  "guardian_cnic_exp", "guardian_marital_status", "guardian_mwa", 
                                  "guardian_phone", "guardian_relation"]
            for field_name in guardian_field_names:
                if field_name in self.fields:
                    self.fields[field_name].setVisible(True)
                    
    def get_form_data(self):
        """Get form data as dictionary."""
        data = {"recipient_type": self.recipient_combo.currentText()}
        
        for field_name, container in self.fields.items():
            if not container.isVisible():
                continue
                
            layout = container.layout()
            if layout and layout.count() >= 2:
                widget = layout.itemAt(1).widget()
                
                if hasattr(widget, 'text'):
                    data[field_name] = widget.text()
                elif hasattr(widget, 'currentText'):
                    data[field_name] = widget.currentText()
                elif hasattr(widget, 'date'):
                    data[field_name] = widget.date().toString("yyyy-MM-dd")
                elif hasattr(widget, 'value'):
                    data[field_name] = widget.value()
                    
        return data
        
    def set_form_data(self, data):
        """Set form data from dictionary."""
        if "recipient_type" in data:
            self.recipient_combo.setCurrentText(data["recipient_type"])
            
        for field_name, value in data.items():
            if field_name == "recipient_type" or field_name not in self.fields:
                continue
                
            container = self.fields[field_name]
            layout = container.layout()
            if layout and layout.count() >= 2:
                widget = layout.itemAt(1).widget()
                
                if hasattr(widget, 'setText') and isinstance(value, str):
                    widget.setText(value)
                elif hasattr(widget, 'setCurrentText') and isinstance(value, str):
                    widget.setCurrentText(value)
                elif hasattr(widget, 'setDate'):
                    date = QDate.fromString(value, "yyyy-MM-dd")
                    if date.isValid():
                        widget.setDate(date)
                elif hasattr(widget, 'setValue'):
                    try:
                        widget.setValue(int(value))
                    except (ValueError, TypeError):
                        pass
                        
    def reset_form(self):
        """Reset all form fields."""
        for field_name, container in self.fields.items():
            layout = container.layout()
            if layout and layout.count() >= 2:
                widget = layout.itemAt(1).widget()
                
                if hasattr(widget, 'setText'):
                    widget.setText("")
                elif hasattr(widget, 'setCurrentIndex'):
                    widget.setCurrentIndex(0)
                elif hasattr(widget, 'setDate'):
                    widget.setDate(QDate.currentDate())
                elif hasattr(widget, 'setValue'):
                    widget.setValue(0)
                    
        self.apply_all_checkbox.setChecked(False)
        self.form_reset.emit()
        
    def validate_form(self):
        """Validate form and return list of errors."""
        errors = []
        recipient_type = self.recipient_combo.currentText()
        
        # Required fields based on recipient type
        required_fields = []
        if recipient_type == "Principal":
            required_fields = ["mother_name", "mother_cnic"]
        else:
            required_fields = ["guardian_cnic", "guardian_relation"]
            
        data = self.get_form_data()
        for field_name in required_fields:
            if not data.get(field_name, "").strip():
                field_label = self._get_field_label(field_name)
                errors.append(f"{field_label} is required")
                
        return errors
        
    def _get_field_label(self, field_name):
        """Get display label for a field name."""
        if field_name in self.fields:
            container = self.fields[field_name]
            layout = container.layout()
            if layout and layout.count() >= 1:
                label = layout.itemAt(0).widget()
                if isinstance(label, FormLabel):
                    return label.text()
        return field_name.replace("_", " ").title()
        
    def show_form(self):
        """Show the form and trigger initial setup."""
        self.setVisible(True)
        self._on_recipient_changed()  # Set initial field visibility
        
        # Schedule style fixes
        QTimer.singleShot(100, self._apply_style_fixes)
        QTimer.singleShot(300, self._apply_style_fixes)
        
    def _apply_style_fixes(self):
        """Apply style fixes to ensure proper rendering."""
        # Fix container backgrounds
        for field_name, container in self.fields.items():
            container.setAutoFillBackground(False)
            container.setStyleSheet("background-color: transparent;")
            
            # Fix label backgrounds
            layout = container.layout()
            if layout and layout.count() >= 1:
                label = layout.itemAt(0).widget()
                if hasattr(label, 'enforceStyle'):
                    label.enforceStyle()