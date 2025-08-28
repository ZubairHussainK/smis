"""Mother Registration management page UI implementation (duplicate of StudentPage, adapted for mothers)."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QFrame, QGridLayout, 
                           QLineEdit, QMessageBox, QTableWidget, QHeaderView,
                           QScrollArea, QTableWidgetItem, QSplitter, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox, QDateEdit,
                           QSpinBox, QTabWidget, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator
from models.database import Database
from ui.styles.table_styles import apply_standard_table_style
from config.settings import STUDENT_FIELDS

class MotherRegPage(QWidget):
    def _view_details(self):
        """Show details of the selected student record (in MotherReg page)."""
        selected = self.mothers_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a record to view details.")
            return
        row = selected[0].row()
        def val(col_name):
            try:
                idx = STUDENT_FIELDS.index(col_name)
                item = self.mothers_table.item(row, idx)
                return item.text() if item else ""
            except ValueError:
                return ""
        details = (
            f"S#: {val('S#')}\n"
            f"Name: {val('Name')}\n"
            f"School: {val('School Name')}\n"
            f"Class: {val('Class 2025')}\n"
            f"Section: {val('Section')}\n"
            f"Phone: {val('Mobile Number')}\n"
        )
        QMessageBox.information(self, "Student Details", details)
    def _delete_mother(self):
        """Delete the selected mother record."""
        selected = self.mothers_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a mother to delete.")
            return
        row = selected[0].row()
        mother_name = self.mothers_table.item(row, 1).text() if self.mothers_table.item(row, 1) else ""
        reply = QMessageBox.question(self, "Delete Mother", f"Are you sure you want to delete mother: {mother_name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mothers_table.removeRow(row)
            QMessageBox.information(self, "Deleted", f"Mother '{mother_name}' deleted.")
    def _edit_mother(self):
        """Edit the selected mother record."""
        selected = self.mothers_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a mother to edit.")
            return
        row = selected[0].row()
        mother_name = self.mothers_table.item(row, 1).text() if self.mothers_table.item(row, 1) else ""
        QMessageBox.information(self, "Edit Mother", f"Editing mother: {mother_name}\n(Edit form not yet implemented)")
    def _on_double_click(self, item):
        """Handle double-click on a table row to view details or edit."""
        row = item.row()
        # For now, just show details (expand as needed)
        mother_name = self.mothers_table.item(row, 1).text() if self.mothers_table.item(row, 1) else ""
        QMessageBox.information(self, "Mother Details", f"Mother Name: {mother_name}")
    def _on_selection_changed(self):
        """Enable/disable edit/delete/view buttons based on selection."""
        selected = self.mothers_table.selectedItems()
        has_selection = bool(selected)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.view_details_btn.setEnabled(has_selection)
    def _apply_filters(self):
        """Reload data from database when filters change."""
        self._load_data()
    def _show_add_form(self):
        """Show the form for adding a new mother (fully styled like Add Student)."""
        try:
            if not hasattr(self, 'form_frame') or not self.form_frame:
                QMessageBox.critical(self, "Error", "Form frame not available.")
                return

            if self.form_frame.isVisible():
                return

            # Clear existing layout if any
            current_layout = self.form_frame.layout()
            if current_layout:
                QWidget().setLayout(self.form_frame.layout())

            # Outer container style
            self.form_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 16px;
                    border: 1.5px solid #E5E7EB;
                    min-width: 600px;
                    max-width: 900px;
                }
            """)

            form_layout = QVBoxLayout()
            form_layout.setContentsMargins(30, 30, 30, 30)
            form_layout.setSpacing(25)

            # Form header (with blue bar)
            header_frame = QFrame()
            header_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                    border-radius: 10px;
                    padding: 0px 0px 0px 0px;
                }
            """)
            header_layout = QHBoxLayout(header_frame)
           #header_layout.setContentsMargins(18, 10, 18, 10)
            # title_label = QLabel("Add Mother")
            # title_label.setStyleSheet("color: white; font-size: 22px; font-family: 'Poppins Bold'; font-weight: bold;")
            # header_layout.addWidget(title_label)
            # header_layout.addStretch()
            # close_btn = QPushButton("❌")
            # close_btn.setFixedSize(40, 40)
            # close_btn.setStyleSheet("background: #EF4444; color: white; border: none; border-radius: 20px; font-size: 18px; font-weight: bold;")
            # close_btn.clicked.connect(lambda: self.form_frame.setVisible(False))
            # header_layout.addWidget(close_btn)
            # form_layout.addWidget(header_frame)

            # Tab widget for form sections
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1.5px solid #E5E7EB;
                    border-radius: 10px;
                    background: white;
                }
                QTabBar::tab {
                    background: #F3F4F6;
                    color: #374151;
                    padding: 14px 36px;
                    margin-right: 10px;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    font-size: 15px;
                    min-width: 180px;
                    text-align: center;
                }
                QTabBar::tab:selected {
                    background: #3B82F6;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #E5E7EB;
                }
            """)
            tab_widget.tabBar().setExpanding(True)

            # Personal Info Tab
            personal_tab = QWidget()
            personal_layout = QGridLayout(personal_tab)
            personal_layout.setVerticalSpacing(22)
            personal_layout.setHorizontalSpacing(40)  # More space between label and input
            personal_layout.setContentsMargins(25, 20, 25, 20)

            # Personal fields
            personal_fields = [
                ("Household Size:", QSpinBox, "household_size"),
                ("Mother's Name:", QLineEdit, "mother_name"),
                ("Mother's Marital Status:", QComboBox, "mother_marital_status", ["Single", "Married", "Divorced", "Widowed"]),
                ("Mother's CNIC:", QLineEdit, "mother_cnic"),
                ("Mother's CNIC DOI:", QDateEdit, "mother_cnic_doi"),
                ("Mother's CNIC Exp:", QDateEdit, "mother_cnic_exp"),
                ("Mother's MWA:", QLineEdit, "mother_mwa"),
            ]
            self.mother_fields = {}
            row = 0
            for field in personal_fields:
                label = QLabel(field[0])
                label.setStyleSheet("""
                    QLabel {
                        color: #374151;
                        font-family: 'Poppins Medium';
                        font-weight: 600;
                        font-size: 14px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                        min-width: 40px;
                    }
                """)
                label.setFixedWidth(120)
                personal_layout.addWidget(label, row, 0)
                widget_type = field[1]
                field_name = field[2]
                if widget_type == QLineEdit:
                    widget = QLineEdit()
                    widget.setText("")  # Default empty
                    # Add validators for CNIC, MWA, Mobile
                    if field_name == "mother_cnic":
                        cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{13}$'))
                        widget.setValidator(cnic_validator)
                        widget.setPlaceholderText("Enter 13 digit CNIC")
                        widget.setMaxLength(13)
                    elif field_name == "mother_mwa":
                        mwa_validator = QRegExpValidator(QRegExp(r'^[0-9]{11}$'))
                        widget.setValidator(mwa_validator)
                        widget.setPlaceholderText("Enter 11 digit MWA")
                        widget.setMaxLength(11)
                    elif field_name == "mother_mobile":
                        mobile_validator = QRegExpValidator(QRegExp(r'^[0-9]{11}$'))
                        widget.setValidator(mobile_validator)
                        widget.setPlaceholderText("Enter 11 digit mobile number")
                        widget.setMaxLength(11)
                    else:
                        widget.setPlaceholderText(f"Enter {field[0][:-1].lower()}")
                elif widget_type == QSpinBox:
                    widget = QSpinBox()
                    widget.setRange(1, 50)
                    widget.setValue(1)
                elif widget_type == QComboBox:
                    widget = QComboBox()
                    widget.addItems(field[3])
                elif widget_type == QDateEdit:
                    widget = QDateEdit()
                    widget.setDate(QDate.currentDate())
                    widget.setCalendarPopup(True)
                    widget.setDisplayFormat("dd-MMM-yy")
                else:
                    widget = QLineEdit()
                    widget.setText("")
                widget.setStyleSheet("""
                    QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
                        border: 2px solid #E5E7EB;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-family: 'Poppins';
                        font-size: 14px;
                        background: white;
                        min-height: 38px;
                        max-height: 44px;
                        max-width: 340px;
                        margin-left: 8px;
                    }
                    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                        border-color: #3B82F6;
                        outline: none;
                        background: #F8FAFC;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 25px;
                        padding-right: 5px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 6px solid transparent;
                        border-right: 6px solid transparent;
                        border-top: 6px solid #6B7280;
                        margin-right: 8px;
                    }
                    QComboBox::down-arrow:hover {
                        border-top-color: #374151;
                    }
                    QTextEdit {
                        min-height: 80px;
                        max-height: 100px;
                    }
                    QSpinBox::up-button, QSpinBox::down-button {
                        width: 20px;
                        background: #F3F4F6;
                        border: none;
                    }
                    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                        background: #E5E7EB;
                    }
                """)
                widget.setMinimumHeight(38)
                widget.setMaximumWidth(340)
                self.mother_fields[field_name] = widget
                personal_layout.addWidget(widget, row, 1)
                row += 1
            personal_layout.setRowStretch(row, 1)
            tab_widget.addTab(personal_tab, "👩 Personal Info")

            # Guardian Info Tab
            guardian_tab = QWidget()
            guardian_layout = QGridLayout(guardian_tab)
            guardian_layout.setVerticalSpacing(22)
            guardian_layout.setHorizontalSpacing(40)  # More space between label and input
            guardian_layout.setContentsMargins(25, 20, 25, 20)

            guardian_fields = [
                ("Household Name:", QLineEdit, "household_name"),
                ("Guardian CNIC:", QLineEdit, "guardian_cnic"),
                ("Guardian CNIC DOI:", QDateEdit, "guardian_cnic_doi"),
                ("Guardian CNIC Exp:", QDateEdit, "guardian_cnic_exp"),
                ("Guardian Marital Status:", QComboBox, "guardian_marital_status", ["Single", "Married", "Divorced", "Widowed"]),
                ("Guardian MWA:", QLineEdit, "guardian_mwa"),
                ("Guardian Phone:", QLineEdit, "guardian_phone"),
                ("Guardian Relation:", QComboBox, "guardian_relation", ["Father", "Mother", "Uncle", "Aunt", "Grandfather", "Grandmother", "Other"]),
            ]
            row = 0
            for field in guardian_fields:
                label = QLabel(field[0])
                label.setStyleSheet("""
                    QLabel {
                        color: #374151;
                        font-family: 'Poppins Medium';
                        font-weight: 600;
                        font-size: 14px;
                        min-height: 38px;
                        max-height: 38px;
                        min-width: 40px;
                        padding: 8px 0px;
                    }
                """)
                label.setFixedWidth(120)
                guardian_layout.addWidget(label, row, 0)
                widget_type = field[1]
                field_name = field[2]
                if widget_type == QLineEdit:
                    widget = QLineEdit()
                    widget.setText("")  # Default empty
                    # Add validators for CNIC, MWA, Mobile
                    if field_name == "guardian_cnic":
                        cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{13}$'))
                        widget.setValidator(cnic_validator)
                        widget.setPlaceholderText("Enter 13 digit CNIC")
                        widget.setMaxLength(13)
                    elif field_name == "guardian_mwa":
                        mwa_validator = QRegExpValidator(QRegExp(r'^[0-9]{11}$'))
                        widget.setValidator(mwa_validator)
                        widget.setPlaceholderText("Enter 11 digit MWA")
                        widget.setMaxLength(11)
                    elif field_name == "guardian_phone":
                        mobile_validator = QRegExpValidator(QRegExp(r'^[0-9]{11}$'))
                        widget.setValidator(mobile_validator)
                        widget.setPlaceholderText("Enter 11 digit mobile number")
                        widget.setMaxLength(11)
                    else:
                        widget.setPlaceholderText(f"Enter {field[0][:-1].lower()}")
                elif widget_type == QSpinBox:
                    widget = QSpinBox()
                    widget.setRange(1, 50)
                    widget.setValue(1)
                elif widget_type == QComboBox:
                    widget = QComboBox()
                    widget.addItems(field[3])
                elif widget_type == QDateEdit:
                    widget = QDateEdit()
                    widget.setDate(QDate.currentDate())
                    widget.setCalendarPopup(True)
                    widget.setDisplayFormat("dd-MMM-yy")
                else:
                    widget = QLineEdit()
                    widget.setText("")
                widget.setStyleSheet("""
                    QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
                        border: 2px solid #E5E7EB;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-family: 'Poppins';
                        font-size: 14px;
                        background: white;
                        min-height: 38px;
                        max-height: 44px;
                        max-width: 340px;
                        margin-left: 8px;
                    }
                    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                        border-color: #3B82F6;
                        outline: none;
                        background: #F8FAFC;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 25px;
                        padding-right: 5px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 6px solid transparent;
                        border-right: 6px solid transparent;
                        border-top: 6px solid #6B7280;
                        margin-right: 8px;
                    }
                    QComboBox::down-arrow:hover {
                        border-top-color: #374151;
                    }
                    QTextEdit {
                        min-height: 80px;
                        max-height: 100px;
                    }
                    QSpinBox::up-button, QSpinBox::down-button {
                        width: 20px;
                        background: #F3F4F6;
                        border: none;
                    }
                    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                        background: #E5E7EB;
                    }
                """)
                widget.setMinimumHeight(38)
                widget.setMaximumWidth(340)
                self.mother_fields[field_name] = widget
                guardian_layout.addWidget(widget, row, 1)
                row += 1
            guardian_layout.setRowStretch(row, 1)
            tab_widget.addTab(guardian_tab, "👨‍👩‍👧 Guardian Info")

            form_layout.addWidget(tab_widget, 1)

            # Save/Cancel/Reset/Close buttons row (like student form)
            btn_layout = QHBoxLayout()
            close_btn2 = QPushButton("❌ Close")
            close_btn2.setStyleSheet("background: #EF4444; color: white; border: none; border-radius: 8px; padding: 12px 28px; font-size: 16px; font-family: 'Poppins Medium'; font-weight: 600;")
            reset_btn = QPushButton("⚠️ Reset")
            reset_btn.setStyleSheet("background: #F59E0B; color: white; border: none; border-radius: 8px; padding: 12px 28px; font-size: 16px; font-family: 'Poppins Medium'; font-weight: 600;")
            cancel_btn = QPushButton("✖ Cancel")
            cancel_btn.setStyleSheet("background: #6B7280; color: white; border: none; border-radius: 8px; padding: 12px 28px; font-size: 16px; font-family: 'Poppins Medium'; font-weight: 600;")
            save_btn = QPushButton("💾 Save Mother")
            save_btn.setStyleSheet("background: #10B981; color: white; border: none; border-radius: 8px; padding: 12px 28px; font-size: 16px; font-family: 'Poppins Medium'; font-weight: 600;")
            apply_all_checkbox = QCheckBox("Apply to all filtered rows")
            btn_layout.addWidget(close_btn2)
            btn_layout.addWidget(reset_btn)
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(apply_all_checkbox)
            btn_layout.addStretch()
            btn_layout.addWidget(save_btn)

            close_btn2.clicked.connect(lambda: self.form_frame.setVisible(False))
            cancel_btn.clicked.connect(lambda: self.form_frame.setVisible(False))
            reset_btn.clicked.connect(lambda: [w.clear() if isinstance(w, QLineEdit) else w.setValue(1) if isinstance(w, QSpinBox) else None for w in self.mother_fields.values()])
            # Connect Save to persist mother info into selected student
            def on_save():
                try:
                    # Build list of target S#s based on persistent selection or 'apply all filtered'
                    target_snos = []
                    if apply_all_checkbox.isChecked():
                        # Apply to all rows currently visible in the table
                        for r in range(self.mothers_table.rowCount()):
                            s_no_item = self.mothers_table.item(r, 1)
                            if s_no_item and s_no_item.text().strip():
                                target_snos.append(s_no_item.text().strip())
                    else:
                        # Use persistent selection set
                        target_snos = list(self.selected_snos)
                    # Fallback: if nothing selected and not apply-all, prompt user
                    if not target_snos:
                        QMessageBox.warning(self, "No Students Selected", "Select one or more students (checkbox), or tick 'Apply to all filtered rows'.")
                        return
                    # Collect mother/guardian fields from form widgets
                    info = {}
                    for key, widget in self.mother_fields.items():
                        if hasattr(widget, 'text'):
                            info[key] = widget.text().strip()
                        elif hasattr(widget, 'value'):
                            info[key] = widget.value()
                        elif hasattr(widget, 'currentText'):
                            info[key] = widget.currentText()
                    # Persist to DB (bulk or single)
                    updated_count = 0
                    if len(target_snos) == 1:
                        updated = self.db.update_mother_info(target_snos[0], info)
                        updated_count = 1 if updated else 0
                    else:
                        updated_count = self.db.update_mother_info_bulk(target_snos, info)
                    if updated_count > 0:
                        QMessageBox.information(self, "Saved", f"Mother information saved to {updated_count} student(s).")
                        # Hide form and refresh list
                        self.form_frame.setVisible(False)
                        # Clear selection and clear search
                        try:
                            self.selected_snos.clear()
                        except Exception:
                            pass
                        if hasattr(self, 'search_input') and self.search_input:
                            try:
                                prev = self.search_input.blockSignals(True)
                                self.search_input.clear()
                                self.search_input.blockSignals(prev)
                            except Exception:
                                self.search_input.setText("")
                        # Reload data with no selection; all rows unchecked
                        self._load_data()
                        # After reload, the updated students will disappear from the list because they no longer match the NULL-info filter
                    else:
                        QMessageBox.information(self, "No Changes", "Nothing to save or invalid fields.")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save mother info:\n{str(e)}")
            save_btn.clicked.connect(on_save)

            form_layout.addLayout(btn_layout)

            self.form_frame.setLayout(form_layout)
            self.form_frame.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Add Mother form:\n{str(e)}")
    def _create_left_panel(self):
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        panel_layout = QVBoxLayout(left_panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(15)
        filters_group = QGroupBox("🔍 Search & Filter Mothers")
        filters_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Poppins Medium';
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)
        filters_layout = QVBoxLayout(filters_group)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or CNIC...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px 12px;
                font-family: 'Poppins';
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        filters_layout.addLayout(search_layout)
        dropdowns_layout = QHBoxLayout()
        school_layout = QVBoxLayout()
        school_label = QLabel("School:")
        school_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.school_combo = QComboBox()
        self.school_combo.addItem("All Schools")  # Default option
        self._load_schools_data()  # Load from database
        self.school_combo.setStyleSheet(self._get_combo_style())
        school_layout.addWidget(school_label)
        school_layout.addWidget(self.school_combo)
        class_layout = QVBoxLayout()
        class_label = QLabel("Class:")
        class_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.class_combo = QComboBox()
        self.class_combo.addItem("All Classes")  # Default option
        self._load_classes_data()  # Load from database
        self.class_combo.setStyleSheet(self._get_combo_style())
        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo)
        section_layout = QVBoxLayout()
        section_label = QLabel("Section:")
        section_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.section_combo = QComboBox()
        self.section_combo.addItem("All Sections")  # Default option
        self._load_sections_data()  # Load from database
        self.section_combo.setStyleSheet(self._get_combo_style())
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_combo)
        dropdowns_layout.addLayout(school_layout)
        dropdowns_layout.addLayout(class_layout)
        dropdowns_layout.addLayout(section_layout)
        filters_layout.addLayout(dropdowns_layout)
        table_group = QGroupBox("📋 Student Records")
        table_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Poppins Medium';
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)
        table_layout = QVBoxLayout(table_group)
        self.mothers_table = QTableWidget()
        # Add a checkbox column + 7 summary columns (including School)
        self.mothers_table.setColumnCount(8)
        self.mothers_table.setHorizontalHeaderLabels([
            "✅ Select", "🆔 ID", "👤 Student Name", "👨‍👦 Father Name", "📚 Class", "📝 Section", "🏫 School", "📞 Phone"
        ])
        
        # Apply standard table styling
        apply_standard_table_style(self.mothers_table)
        
        # Additional settings specific to mothers table (override defaults)
        self.mothers_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # Make first column (checkbox) a small fixed width
        header = self.mothers_table.horizontalHeader()
        header.resizeSection(0, 60)
        table_layout.addWidget(self.mothers_table)
        table_actions = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setStyleSheet(self._get_button_style('#F59E0B', '#D97706'))
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet(self._get_button_style('#EF4444', '#DC2626'))
        self.view_details_btn = QPushButton("👁️ View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.setStyleSheet(self._get_button_style('#6B7280', '#4B5563'))
        table_actions.addWidget(self.edit_btn)
        table_actions.addWidget(self.delete_btn)
        table_actions.addWidget(self.view_details_btn)
        table_actions.addStretch()
        # Selected summary on the right
        self.selected_info_label = QLabel("Selected: 0")
        self.selected_info_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 12px;")
        self.view_selected_btn = QPushButton("View Selected")
        self.view_selected_btn.setEnabled(False)
        self.view_selected_btn.setStyleSheet(self._get_button_style('#3B82F6', '#2563EB'))
        table_actions.addWidget(self.selected_info_label)
        table_actions.addWidget(self.view_selected_btn)
        table_layout.addLayout(table_actions)
        panel_layout.addWidget(filters_group)
        panel_layout.addWidget(table_group, 1)
        return left_panel

    def _create_right_panel(self):
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                min-height: 500px;
                max-height: 700px;
            }
        """)
        return self.form_frame

    def _get_combo_style(self):
        return """
            QComboBox {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Poppins';
                font-size: 14px;
                background: white;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #3B82F6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6B7280;
                margin-right: 5px;
            }
        """

    def _get_button_style(self, color, hover_color):
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            QPushButton:pressed {{
                background: {hover_color};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background: #D1D5DB;
                color: #9CA3AF;
            }}
        """

    def _load_data(self):
        try:
            # Build SQL with filters and search
            where_clauses = []
            params = []
            # Only show students missing mother/guardian info
            where_clauses.append("(COALESCE(mother_name,'')='' AND COALESCE(mother_cnic,'')='' AND COALESCE(household_name,'')='' AND COALESCE(father_phone,'')='')")
            # School filter
            school = self.school_combo.currentText() if self.school_combo else None
            if school and school != 'All Schools':
                where_clauses.append("school_name = ?")
                params.append(school)
            # Class filter
            class_name = self.class_combo.currentText() if self.class_combo else None
            if class_name and class_name != 'All Classes':
                where_clauses.append("class_2025 = ?")
                params.append(class_name)
            # Section filter
            section = self.section_combo.currentText() if self.section_combo else None
            if section and section != 'All Sections':
                where_clauses.append("section = ?")
                params.append(section)
            # Search text
            search_text = self.search_input.text().strip() if self.search_input else ''
            if search_text:
                where_clauses.append("(LOWER(student_name) LIKE ? OR LOWER(father_phone) LIKE ?)")
                like = f"%{search_text.lower()}%"
                params.extend([like, like])
            
            # Build the complete WHERE clause
            where_clauses.insert(0, "is_deleted = 0")  # Always exclude deleted records
            where_sql = f"WHERE {' AND '.join(where_clauses)}"
            sql = f"SELECT student_id, student_name, father_name, class_name, section, father_phone FROM students {where_sql} ORDER BY student_name"
            rows = self.db.execute_secure_query(sql, tuple(params))
            students = []
            for r in rows:
                students.append({
                    'Student ID': r['student_id'],
                    'Name': r['student_name'],
                    'Father': r['father_name'] if 'father_name' in r.keys() else '',
                    'Class': r['class_name'],
                    'Section': r['section'],
                    'Phone': r['father_phone'],
                })
            self._populate_table(students)
        except Exception as e:
            print(f"Error loading student data: {e}")
            QMessageBox.warning(self, "Data Load Error", f"Failed to load student data: {str(e)}")

    def _populate_table(self, students):
        # Populate 6-column summary view matching student.py
        self._is_populating = True
        # Temporarily disable sorting and signals to avoid flicker/misalignment while filling
        prev_sort = self.mothers_table.isSortingEnabled()
        self.mothers_table.setSortingEnabled(False)
        self.mothers_table.blockSignals(True)
        self.mothers_table.clearContents()
        self.mothers_table.setRowCount(len(students))
        def getv(row_obj, key, alt_keys=()):
            # Try dict-style get
            if hasattr(row_obj, 'get'):
                val = row_obj.get(key)
                if val is None:
                    for k in alt_keys:
                        v = row_obj.get(k)
                        if v is not None:
                            return v
                return val
            # Try mapping-like index access
            try:
                return row_obj[key]
            except Exception:
                for k in alt_keys:
                    try:
                        return row_obj[k]
                    except Exception:
                        continue
                return ""
        for row, s in enumerate(students):
            # Checkbox cell (persist check state by S#)
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            # Determine S# first to set check state later
            student_id_val = str(getv(s, "Student ID"))
            chk.setCheckState(Qt.Checked if student_id_val in self.selected_snos else Qt.Unchecked)
            self.mothers_table.setItem(row, 0, chk)
            # ID (S#)
            self.mothers_table.setItem(row, 1, QTableWidgetItem(student_id_val))
            # Name
            name_val = str(getv(s, "Name"))
            self.mothers_table.setItem(row, 2, QTableWidgetItem(name_val))
            # Father Name
            father_val = str(getv(s, "Father", ("Father's Name",)))
            self.mothers_table.setItem(row, 3, QTableWidgetItem(father_val))
            # Class
            class_val = str(getv(s, "Class", ("class_2025",)))
            self.mothers_table.setItem(row, 4, QTableWidgetItem(class_val))
            # Section
            section_val = str(getv(s, "Section"))
            self.mothers_table.setItem(row, 5, QTableWidgetItem(section_val))
            # School
            school_val = str(getv(s, "School", ("School Name", "school_name")))
            self.mothers_table.setItem(row, 6, QTableWidgetItem(school_val))
            # Phone
            phone_val = str(getv(s, "Phone", ("Mobile Number", "mobile")))
            self.mothers_table.setItem(row, 7, QTableWidgetItem(phone_val))
        try:
            import logging
            logging.info(f"MotherReg loaded {len(students)} students")
        except Exception:
            pass
        finally:
            # Re-enable signals/sorting and refresh selection summary
            self.mothers_table.blockSignals(False)
            self.mothers_table.setSortingEnabled(prev_sort)
            self._is_populating = False
            self._update_selected_summary()

    def _connect_signals(self):
        self.add_new_btn.clicked.connect(self._show_add_form)
        self.refresh_btn.clicked.connect(self._load_data)
        self.search_input.textChanged.connect(self._apply_filters)
        self.school_combo.currentTextChanged.connect(self._apply_filters)
        self.class_combo.currentTextChanged.connect(self._apply_filters)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        self.mothers_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.mothers_table.itemDoubleClicked.connect(self._on_double_click)
        self.school_combo.currentTextChanged.connect(self._apply_filters)
        self.class_combo.currentTextChanged.connect(self._apply_filters)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        self.edit_btn.clicked.connect(self._edit_mother)
        self.delete_btn.clicked.connect(self._delete_mother)
        self.view_details_btn.clicked.connect(self._view_details)
        # Track checkbox changes to persist selections
        self.mothers_table.itemChanged.connect(self._on_item_changed)
        self.view_selected_btn.clicked.connect(self._view_selected_list)

    def _on_item_changed(self, item):
        """Persist checkbox selection changes into self.selected_snos."""
        try:
            if self._is_populating or item.column() != 0:
                return
            s_no_item = self.mothers_table.item(item.row(), 1)
            if not s_no_item:
                return
            s_no = s_no_item.text().strip()
            if not s_no:
                return
            if item.checkState() == Qt.Checked:
                self.selected_snos.add(s_no)
            else:
                self.selected_snos.discard(s_no)
            self._update_selected_summary()
        except Exception:
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
        self.mother_fields = {}
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.save_btn = None
        self.cancel_btn = None
        self.mothers_table = None
        self.search_input = None
        self.form_frame = None
        self.current_mother_id = None
        self.is_editing = False
        self.db = Database()
        # Persistent selection and populate flag
        self.selected_snos = set()
        self._is_populating = False
        self.selected_info_label = None
        self.view_selected_btn = None
        self._init_ui()
        self._load_data()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        splitter = QSplitter(Qt.Horizontal)
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        splitter.setSizes([550, 450])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        main_layout.addWidget(splitter)
        self.form_frame.setVisible(False)

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
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(12)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        page_title = QLabel("👩‍👧 Mother Registration")
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
        self.add_new_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.5);
            }
        """)
        actions_layout.addWidget(self.add_new_btn)
        actions_layout.addWidget(self.refresh_btn)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(actions_layout)
        return header_frame

    def _load_schools_data(self):
        """Load schools from database and populate school combo."""
        try:
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
            print(f"📚 Loaded {len(schools)} schools in mother registration page")
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
            print(f"📚 Loaded {len(classes)} classes in mother registration page")
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
            print(f"📚 Loaded {len(sections)} sections in mother registration page")
        except Exception as e:
            print(f"❌ Error loading sections: {e}")
            # Add some default options if database fails
            self.section_combo.addItems(["A", "B", "C", "D", "E"])

    # ...
    # For brevity, copy all other methods from StudentPage, replacing 'student' with 'mother', and update labels/icons as needed.

