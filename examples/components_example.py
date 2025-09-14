"""
Example usage of the custom UI components.
This file demonstrates how to use the custom date picker, combobox, and form components.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout, QMessageBox

from ui.components import (
    CustomDateEdit, CustomComboBox, FormModel, InputField, FormLabel,
    create_form_field_with_label, validate_and_highlight, reset_form
)


class ExampleForm(QWidget):
    """Example form using the custom components."""
    
    def __init__(self):
        super().__init__()
        self.model = FormModel()
        self.labels = {}
        self.widgets = {}
        
        # Define fields
        self.fields = [
            ("name", "Full Name", "text"),
            ("phone", "Phone Number", "phone"),
            ("cnic", "CNIC Number", "cnic"),
            ("dob", "Date of Birth", "date"),
            ("education", "Education Level", "combo", ["Primary", "Secondary", "Bachelor", "Master", "PhD"]),
            ("siblings", "Number of Siblings", "spinbox"),
        ]
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Custom Components Example")
        self.setGeometry(100, 100, 800, 500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create form frame
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
        form_layout = QVBoxLayout(form_frame)
        
        # Create form grid for fields
        form_grid = QGridLayout()
        form_grid.setVerticalSpacing(15)
        form_grid.setHorizontalSpacing(20)
        form_grid.setContentsMargins(20, 20, 20, 20)
        
        # Create form fields
        row = 0
        col = 0
        
        for field_data in self.fields:
            if len(field_data) >= 4:
                field_name, label_text, field_type, options = field_data
            else:
                field_name, label_text, field_type = field_data
                options = None
                
            # Create label and widget
            label, widget, _ = create_form_field_with_label(field_name, label_text, field_type, options)
            
            # Store references
            self.labels[field_name] = label
            self.widgets[field_name] = widget
            
            # Add to grid - label on top, widget below
            form_grid.addWidget(label, row * 2, col)
            form_grid.addWidget(widget, row * 2 + 1, col)
            
            # Update position
            col += 1
            if col >= 2:  # 2 columns
                col = 0
                row += 1
        
        # Add form grid to layout
        form_layout.addLayout(form_grid)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset Form")
        reset_btn.clicked.connect(self.reset_form)
        
        save_btn = QPushButton("Save Form")
        save_btn.clicked.connect(self.save_form)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0175b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0186d1;
            }
        """)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        form_layout.addLayout(button_layout)
        
        # Add form frame to main layout
        main_layout.addWidget(form_frame)
        
    def save_form(self):
        """Validate and save form data."""
        if validate_and_highlight(self.widgets, self.model):
            # Form is valid
            message = "Form data is valid!\n\n"
            
            # Display collected data
            for field_name, value in self.model.fields.items():
                message += f"{field_name}: {value}\n"
                
            QMessageBox.information(self, "Form Saved", message)
        else:
            # Form has errors
            QMessageBox.warning(self, "Validation Error", "Please fix the highlighted fields.")
    
    def reset_form(self):
        """Reset all form fields."""
        reset_form(self.widgets)
        QMessageBox.information(self, "Form Reset", "All fields have been reset.")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistency
    
    window = ExampleForm()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
