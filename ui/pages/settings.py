"""
Settings Page (UX-Improved): Location, School, Class, Section
PyQt5 single-file widget with better design, validation, and table tooling.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFormLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QGroupBox, QFrame,
    QAbstractItemView, QHeaderView, QToolButton, QStyle, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QRegularExpression, QSortFilterProxyModel
from PyQt5.QtGui import QFont
from models.database import Database
from ui.styles.table_styles import apply_standard_table_style
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegularExpressionValidator, QIcon, QKeySequence


class SettingsPage(QWidget):
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self._init_ui()

    # ---------------- Root UI ----------------
    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setStyleSheet(self._tabs_stylesheet())
        root.addWidget(self.tabs)

        # Location Tab
        self.location_tab = QWidget()
        self._setup_location_tab()
        self.tabs.addTab(self.location_tab, "Location")

        # School Tab
        self.school_tab = QWidget()
        self._setup_school_tab()
        self.tabs.addTab(self.school_tab, "Schools")

        # Class Tab
        self.class_tab = QWidget()
        self._setup_class_tab()
        self.tabs.addTab(self.class_tab, "Classes")

        # Section Tab
        self.section_tab = QWidget()
        self._setup_section_tab()
        self.tabs.addTab(self.section_tab, "Sections")

    # ---------------- Theming ----------------
    def _tabs_stylesheet(self) -> str:
        # Subtle, neutral light theme
        return """
        QTabBar::tab {
            color: #334155;
            font-size: 14px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-bottom: none;
            padding: 9px 18px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
            min-width: 120px;
        }
        QTabBar::tab:hover {
            background: #F1F5F9;
        }
        QTabBar::tab:selected {
            background: #FFFFFF;
            color: #1D4ED8;
            font-weight: 600;
        }
        QTabWidget::pane {
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            top: -1px;
            background: #FFFFFF;
        }
        QGroupBox {
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            margin-top: 16px;
            padding: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            margin-left: 8px;
            color: #0F172A;
            background: transparent;
        }
        QLineEdit {
            height: 32px;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 4px 8px;
            background: #FFFFFF;
        }
        QLineEdit:focus {
            border: 1px solid #2563EB;
            outline: none;
        }
        QPushButton {
            border: 1px solid #CBD5E1;
            background: #F8FAFC;
            border-radius: 8px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background: #EEF2FF;
        }
        QPushButton:pressed {
            background: #E0E7FF;
        }
        QTableWidget {
            gridline-color: #E5E7EB;
            selection-background-color: #DBEAFE;
            selection-color: #1E293B;
            alternate-background-color: #F8FAFC;
        }
        """

    # ---------------- Reusable bits ----------------
    def _labeled_status(self, parent_layout: QVBoxLayout) -> QLabel:
        label = QLabel("")
        label.setWordWrap(True)
        label.setStyleSheet(
            "QLabel { background:#F0F9FF; border:1px solid #BAE6FD; color:#0C4A6E; padding:6px 8px; border-radius:8px; }"
        )
        label.hide()
        parent_layout.addWidget(label)
        return label

    def _table_toolbar(self, parent_layout: QVBoxLayout, on_add, on_delete, on_export=None):
        bar = QHBoxLayout()
        bar.setSpacing(8)

        # Add button
        add_btn = QPushButton(self.style().standardIcon(QStyle.SP_FileDialogNewFolder), "Add")
        add_btn.clicked.connect(on_add)
        add_btn.setShortcut(QKeySequence("Ctrl+N"))
        bar.addWidget(add_btn)

        # Delete button
        del_btn = QPushButton(self.style().standardIcon(QStyle.SP_TrashIcon), "Delete")
        del_btn.clicked.connect(on_delete)
        del_btn.setShortcut(QKeySequence(Qt.Key_Delete))
        bar.addWidget(del_btn)

        # Export (optional)
        if on_export:
            exp_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Export CSV")
            exp_btn.clicked.connect(on_export)
            bar.addWidget(exp_btn)

        bar.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Search box
        search = QLineEdit()
        search.setPlaceholderText("Search…")
        clear_btn = QToolButton()
        clear_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        clear_btn.setToolTip("Clear search")

        search_row = QHBoxLayout()
        search_row.setSpacing(4)
        search_row.addWidget(search)
        search_row.addWidget(clear_btn)

        bar.addLayout(search_row)

        parent_layout.addLayout(bar)
        return search, clear_btn

    def _prep_table(self, table: QTableWidget):
        # Apply standard table styling
        apply_standard_table_style(table)
        
        # Override specific settings if needed
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _bind_search(self, table: QTableWidget, search: QLineEdit, clear_btn: QToolButton):
        def apply_filter(text: str):
            text = text.lower().strip()
            for r in range(table.rowCount()):
                match = False
                for c in range(table.columnCount()):
                    item = table.item(r, c)
                    if item and text in item.text().lower():
                        match = True
                        break
                table.setRowHidden(r, not match) if text else table.setRowHidden(r, False)

        search.textChanged.connect(apply_filter)
        clear_btn.clicked.connect(lambda: search.clear())

    def _required(self, label: str) -> str:
        return f"{label} *"

    # --------------- LOCATION ---------------
    def _setup_location_tab(self):
        layout = QVBoxLayout(self.location_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        group = QGroupBox("Location Details")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("e.g., Pakistan")
        self.province_input = QLineEdit()
        self.province_input.setPlaceholderText("e.g., Sindh")
        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("e.g., Karachi")

        form.addRow(self._required("Country"), self.country_input)
        form.addRow(self._required("Province"), self.province_input)
        form.addRow(self._required("District"), self.district_input)

        btns = QHBoxLayout()
        save_btn = QPushButton("Save Location")
        save_btn.setShortcut(QKeySequence("Ctrl+S"))
        cancel_btn = QPushButton("Clear")
        cancel_btn.setShortcut(QKeySequence("Esc"))
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        form.addRow(btns)

        self.loc_status = self._labeled_status(layout)
        layout.addWidget(group)

        cancel_btn.clicked.connect(lambda: [w.clear() for w in (self.country_input, self.province_input, self.district_input)])
        save_btn.clicked.connect(self.save_location)

    def save_location(self):
        if not all([self.country_input.text().strip(),
                    self.province_input.text().strip(),
                    self.district_input.text().strip()]):
            self._show_status(self.loc_status, "Please complete all required fields.", error=True)
            return
        # TODO: integrate DB here
        self._show_status(self.loc_status, "Location saved successfully.")

    # --------------- SCHOOLS ---------------
    def _setup_school_tab(self):
        layout = QVBoxLayout(self.school_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Toolbar
        search, clear_btn = self._table_toolbar(
            layout, on_add=self._show_school_form, on_delete=self._delete_school_row, on_export=None
        )

        # Table
        self.school_table = QTableWidget(0, 9)
        self.school_table.setHorizontalHeaderLabels([
            "🏫 BEMIS Code", "📝 Name", "🏠 Address", "🌐 Longitude", "🌐 Latitude",
            "🌍 Country", "🏞️ Province", "🏙️ District", "🏘️ Union Council"
        ])
        self._prep_table(self.school_table)
        layout.addWidget(self.school_table, 3)

        # Bind search
        self._bind_search(self.school_table, search, clear_btn)

        # Form card
        form_group = QGroupBox("Add / Edit School")
        form = QFormLayout(form_group)
        form.setLabelAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)

        self.school_name_input = QLineEdit()
        self.school_name_input.setPlaceholderText("School full name")
        self.school_address_input = QLineEdit()
        self.school_address_input.setPlaceholderText("Street, area, city")
        self.longitude_input = QLineEdit()
        self.latitude_input = QLineEdit()
        self.bemis_code_input = QLineEdit()
        self.school_country_input = QLineEdit()
        self.school_province_input = QLineEdit()
        self.school_district_input = QLineEdit()
        self.school_unioncouncil_input = QLineEdit()

        # Validators & placeholders
        dbl = QDoubleValidator(-180.0, 180.0, 6)
        self.longitude_input.setValidator(dbl)
        self.longitude_input.setPlaceholderText("e.g., 67.001234")
        dbl_lat = QDoubleValidator(-90.0, 90.0, 6)
        self.latitude_input.setValidator(dbl_lat)
        self.latitude_input.setPlaceholderText("e.g., 24.912345")

        self.bemis_code_input.setValidator(QIntValidator(0, 999999999))
        self.bemis_code_input.setPlaceholderText("Numeric code")

        # Rows (mark a few as required)
        form.addRow("BEMIS Code", self.bemis_code_input)
        form.addRow(self._required("School Name"), self.school_name_input)
        form.addRow("Address", self.school_address_input)
        form.addRow("Longitude", self.longitude_input)
        form.addRow("Latitude", self.latitude_input)
        form.addRow(self._required("Country"), self.school_country_input)
        form.addRow(self._required("Province"), self.school_province_input)
        form.addRow(self._required("District"), self.school_district_input)
        form.addRow("Union Council", self.school_unioncouncil_input)

        # Buttons
        row_btns = QHBoxLayout()
        self.save_school_btn = QPushButton("Save School")
        self.save_school_btn.setShortcut(QKeySequence("Ctrl+S"))
        self.cancel_school_btn = QPushButton("Clear")
        self.cancel_school_btn.setShortcut(QKeySequence("Esc"))
        row_btns.addWidget(self.save_school_btn)
        row_btns.addWidget(self.cancel_school_btn)
        form.addRow(row_btns)

        layout.addWidget(form_group, 2)
        self.school_status = self._labeled_status(layout)

        # Connections
        self.save_school_btn.clicked.connect(self.save_school)
        self.cancel_school_btn.clicked.connect(self._clear_school_form)

        # Double-click row to load into form
        self.school_table.itemDoubleClicked.connect(self._load_school_from_row)

    def _clear_school_form(self):
        for w in (
            self.school_name_input, self.school_address_input, self.longitude_input, self.latitude_input,
            self.bemis_code_input, self.school_country_input, self.school_province_input,
            self.school_district_input, self.school_unioncouncil_input
        ):
            w.clear()

    def _show_school_form(self):
        # Focus-first field UX
        self.school_name_input.setFocus()

    def _delete_school_row(self):
        r = self.school_table.currentRow()
        if r < 0:
            QMessageBox.information(self, "Delete", "Select a row to delete.")
            return
        self.school_table.removeRow(r)
        self._show_status(self.school_status, "Row deleted.")

    def _load_school_from_row(self):
        r = self.school_table.currentRow()
        if r < 0:
            return
        vals = [self.school_table.item(r, c).text() if self.school_table.item(r, c) else "" for c in range(9)]
        (
            self.school_name_input, self.school_address_input, self.longitude_input, self.latitude_input,
            self.bemis_code_input, self.school_country_input, self.school_province_input,
            self.school_district_input, self.school_unioncouncil_input
        ) = (
            self.school_name_input, self.school_address_input, self.longitude_input, self.latitude_input,
            self.bemis_code_input, self.school_country_input, self.school_province_input,
            self.school_district_input, self.school_unioncouncil_input
        )
        self.school_name_input.setText(vals[0])
        self.school_address_input.setText(vals[1])
        self.longitude_input.setText(vals[2])
        self.latitude_input.setText(vals[3])
        self.bemis_code_input.setText(vals[4])
        self.school_country_input.setText(vals[5])
        self.school_province_input.setText(vals[6])
        self.school_district_input.setText(vals[7])
        self.school_unioncouncil_input.setText(vals[8])

    def save_school(self):
        # Validation
        required = [
            (self.school_name_input, "School Name"),
            (self.school_country_input, "Country"),
            (self.school_province_input, "Province"),
            (self.school_district_input, "District"),
        ]
        missing = [name for w, name in required if not w.text().strip()]
        if missing:
            self._show_status(self.school_status, f"Missing required: {', '.join(missing)}.", error=True)
            return

        record = [
            self.school_name_input.text().strip(),
            self.school_address_input.text().strip(),
            self.longitude_input.text().strip(),
            self.latitude_input.text().strip(),
            self.bemis_code_input.text().strip(),
            self.school_country_input.text().strip(),
            self.school_province_input.text().strip(),
            self.school_district_input.text().strip(),
            self.school_unioncouncil_input.text().strip()
        ]

        # If a row is selected, update it; otherwise insert new (good UX)
        r = self.school_table.currentRow()
        if r >= 0 and self.school_table.rowCount() > 0:
            for c, v in enumerate(record):
                self.school_table.setItem(r, c, QTableWidgetItem(v))
        else:
            r = self.school_table.rowCount()
            self.school_table.insertRow(r)
            for c, v in enumerate(record):
                item = QTableWidgetItem(v)
                if c in (2, 3, 4):  # numeric-ish
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.school_table.setItem(r, c, item)

        # TODO: DB save can be added here, use self.db
        self._clear_school_form()
        self._show_status(self.school_status, "School saved.")

    # --------------- CLASSES ---------------
    def _setup_class_tab(self):
        layout = QVBoxLayout(self.class_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        search, clear_btn = self._table_toolbar(
            layout, on_add=self._show_class_form, on_delete=self._delete_class_row
        )

        self.class_table = QTableWidget(0, 1)
        self.class_table.setHorizontalHeaderLabels(["📚 Class Name"])
        self._prep_table(self.class_table)
        layout.addWidget(self.class_table, 3)
        self._bind_search(self.class_table, search, clear_btn)

        group = QGroupBox("Add / Edit Class")
        form = QFormLayout(group)
        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("e.g., Grade 6")
        form.addRow(self._required("Class Name"), self.class_name_input)

        btns = QHBoxLayout()
        self.save_class_btn = QPushButton("Save Class")
        self.save_class_btn.setShortcut(QKeySequence("Ctrl+S"))
        self.cancel_class_btn = QPushButton("Clear")
        self.cancel_class_btn.setShortcut(QKeySequence("Esc"))
        btns.addWidget(self.save_class_btn)
        btns.addWidget(self.cancel_class_btn)
        form.addRow(btns)

        layout.addWidget(group, 2)
        self.class_status = self._labeled_status(layout)

        self.save_class_btn.clicked.connect(self.save_class)
        self.cancel_class_btn.clicked.connect(lambda: self.class_name_input.clear())
        self.class_table.itemDoubleClicked.connect(self._load_class_from_row)

    def _show_class_form(self):
        self.class_name_input.setFocus()

    def _delete_class_row(self):
        r = self.class_table.currentRow()
        if r < 0:
            QMessageBox.information(self, "Delete", "Select a row to delete.")
            return
        self.class_table.removeRow(r)
        self._show_status(self.class_status, "Row deleted.")

    def _load_class_from_row(self):
        r = self.class_table.currentRow()
        if r >= 0:
            item = self.class_table.item(r, 0)
            self.class_name_input.setText(item.text() if item else "")

    def save_class(self):
        name = self.class_name_input.text().strip()
        if not name:
            self._show_status(self.class_status, "Class Name is required.", error=True)
            return

        r = self.class_table.currentRow()
        if r >= 0 and self.class_table.rowCount() > 0:
            self.class_table.setItem(r, 0, QTableWidgetItem(name))
        else:
            r = self.class_table.rowCount()
            self.class_table.insertRow(r)
            self.class_table.setItem(r, 0, QTableWidgetItem(name))

        # TODO: DB save
        self.class_name_input.clear()
        self._show_status(self.class_status, "Class saved.")

    # --------------- SECTIONS ---------------
    def _setup_section_tab(self):
        layout = QVBoxLayout(self.section_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        search, clear_btn = self._table_toolbar(
            layout, on_add=self._show_section_form, on_delete=self._delete_section_row
        )

        self.section_table = QTableWidget(0, 1)
        self.section_table.setHorizontalHeaderLabels(["📝 Section Name"])
        self._prep_table(self.section_table)
        layout.addWidget(self.section_table, 3)
        self._bind_search(self.section_table, search, clear_btn)

        group = QGroupBox("Add / Edit Section")
        form = QFormLayout(group)
        self.section_name_input = QLineEdit()
        self.section_name_input.setPlaceholderText("e.g., A")
        form.addRow(self._required("Section Name"), self.section_name_input)

        btns = QHBoxLayout()
        self.save_section_btn = QPushButton("Save Section")
        self.save_section_btn.setShortcut(QKeySequence("Ctrl+S"))
        self.cancel_section_btn = QPushButton("Clear")
        self.cancel_section_btn.setShortcut(QKeySequence("Esc"))
        btns.addWidget(self.save_section_btn)
        btns.addWidget(self.cancel_section_btn)
        form.addRow(btns)

        layout.addWidget(group, 2)
        self.section_status = self._labeled_status(layout)

        self.save_section_btn.clicked.connect(self.save_section)
        self.cancel_section_btn.clicked.connect(lambda: self.section_name_input.clear())
        self.section_table.itemDoubleClicked.connect(self._load_section_from_row)

    def _show_section_form(self):
        self.section_name_input.setFocus()

    def _delete_section_row(self):
        r = self.section_table.currentRow()
        if r < 0:
            QMessageBox.information(self, "Delete", "Select a row to delete.")
            return
        self.section_table.removeRow(r)
        self._show_status(self.section_status, "Row deleted.")

    def _load_section_from_row(self):
        r = self.section_table.currentRow()
        if r >= 0:
            item = self.section_table.item(r, 0)
            self.section_name_input.setText(item.text() if item else "")

    def save_section(self):
        name = self.section_name_input.text().strip()
        if not name:
            self._show_status(self.section_status, "Section Name is required.", error=True)
            return

        r = self.section_table.currentRow()
        if r >= 0 and self.section_table.rowCount() > 0:
            self.section_table.setItem(r, 0, QTableWidgetItem(name))
        else:
            r = self.section_table.rowCount()
            self.section_table.insertRow(r)
            self.section_table.setItem(r, 0, QTableWidgetItem(name))

        # TODO: DB save
        self.section_name_input.clear()
        self._show_status(self.section_status, "Section saved.")

    # --------------- Helpers ---------------
    def _show_status(self, label: QLabel, text: str, error: bool = False):
        if error:
            label.setStyleSheet(
                "QLabel { background:#FEF2F2; border:1px solid #FECACA; color:#7F1D1D; padding:6px 8px; border-radius:8px; }"
            )
        else:
            label.setStyleSheet(
                "QLabel { background:#F0F9FF; border:1px solid #BAE6FD; color:#0C4A6E; padding:6px 8px; border-radius:8px; }"
            )
        label.setText(text)
        label.show()
