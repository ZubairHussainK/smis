"""
Modern Sidebar Component for SMIS
Codinglab-style modern design with collapsible states, search, and theme toggle
"""

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgRenderer


class ModernSidebar(QWidget):
    """Modern sidebar with clean design and smooth animations."""
    
    # Signals
    page_changed = pyqtSignal(int)
    theme_changed = pyqtSignal(bool)
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Configuration
        self.expanded_width = 280
        self.collapsed_width = 70
        self.animation_duration = 300
        self.expanded = True
        self.is_dark_mode = False
        self.current_page = 0
        
        # UI components references
        self.nav_buttons = []
        
        # Setup UI
        self._setup_ui()
        self._setup_animations()
        self._apply_theme()
        
    def _setup_ui(self):
        """Initialize the sidebar UI components."""
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(600)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sections
        self._create_header()
        self._create_search()
        self._create_navigation()
        self._create_footer()
        
    def _create_header(self):
        """Create modern header with logo and menu button."""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(15)
        
        # Logo
        self.logo_label = QLabel("S")
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        # Brand text container
        brand_container = QVBoxLayout()
        brand_container.setSpacing(2)
        brand_container.setContentsMargins(0, 0, 0, 0)
        
        self.brand_title = QLabel("SMIS")
        self.brand_title.setObjectName("brandTitle")
        
        self.brand_subtitle = QLabel("Management System")
        self.brand_subtitle.setObjectName("brandSubtitle")
        
        brand_container.addWidget(self.brand_title)
        brand_container.addWidget(self.brand_subtitle)
        
        # Menu button
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.setFixedSize(32, 32)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        header_layout.addWidget(self.logo_label)
        header_layout.addLayout(brand_container)
        header_layout.addStretch()
        header_layout.addWidget(self.menu_btn)
        
        self.main_layout.addWidget(self.header_frame)
        
    def _create_search(self):
        """Create search section."""
        self.search_container = QFrame()
        self.search_container.setObjectName("searchContainer")
        self.search_container.setFixedHeight(70)
        
        search_layout = QVBoxLayout(self.search_container)
        search_layout.setContentsMargins(20, 15, 20, 15)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedHeight(40)
        
        search_layout.addWidget(self.search_input)
        
        self.main_layout.addWidget(self.search_container)
        
    def _create_navigation(self):
        """Create navigation section with menu items."""
        self.nav_container = QFrame()
        self.nav_container.setObjectName("navContainer")
        
        nav_layout = QVBoxLayout(self.nav_container)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setSpacing(4)
        
        # Navigation items
        nav_items = [
            {"title": "Dashboard", "icon": "dashboard.svg", "fallback": "📊"},
            {"title": "Students", "icon": "student.svg", "fallback": "👥"},
            {"title": "Classes", "icon": "list.svg", "fallback": "🏫"},
            {"title": "Attendance", "icon": "attendance.svg", "fallback": "✅"},
            {"title": "Reports", "icon": "reports.svg", "fallback": "📈"},
            {"title": "Settings", "icon": "settings.svg", "fallback": "⚙️"},
        ]
        
        for index, item in enumerate(nav_items):
            nav_button = self._create_nav_button(item, index)
            nav_layout.addWidget(nav_button)
            self.nav_buttons.append(nav_button)
            
        # Set first button as selected
        if self.nav_buttons:
            self.nav_buttons[0].setProperty("selected", True)
            
        nav_layout.addStretch()
        
        self.main_layout.addWidget(self.nav_container)
        
    def _create_nav_button(self, item, index):
        """Create a navigation button."""
        button = QPushButton()
        button.setObjectName("navButton")
        button.setFixedHeight(48)
        button.setCursor(Qt.PointingHandCursor)
        button.setProperty("selected", False)
        
        # Icon label
        icon_label = QLabel()
        icon_label.setObjectName("navIcon")
        icon_label.setFixedSize(22, 22)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Load SVG icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'resources', 'icons', item["icon"])
        if os.path.exists(icon_path):
            try:
                pixmap = QPixmap(22, 22)
                pixmap.fill(Qt.transparent)
                
                painter = QPainter(pixmap)
                renderer = QSvgRenderer(icon_path)
                renderer.render(painter)
                painter.end()
                
                icon_label.setPixmap(pixmap)
            except Exception as e:
                # Fallback to emoji if SVG fails
                icon_label.setText(item.get("fallback", "●"))
        else:
            # Fallback to emoji if file doesn't exist
            icon_label.setText(item.get("fallback", "●"))
            
        # Title label
        title_label = QLabel(item["title"])
        title_label.setObjectName("navTitle")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Button layout
        btn_layout = QHBoxLayout(button)
        btn_layout.setContentsMargins(16, 12, 16, 12)
        btn_layout.setSpacing(12)
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(title_label)
        btn_layout.addStretch()
        
        # Store references
        button.icon_label = icon_label
        button.title_label = title_label
        
        # Connect click
        button.clicked.connect(lambda: self._nav_clicked(index))
        
        return button
        
    def _create_footer(self):
        """Create footer with logout and theme toggle."""
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("footerFrame")
        self.footer_frame.setFixedHeight(120)
        
        footer_layout = QVBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setSpacing(10)
        
        # Theme toggle
        theme_container = self._create_theme_container()
        footer_layout.addWidget(theme_container)
        
        # Logout button
        logout_btn = self._create_logout_button()
        logout_btn.clicked.connect(self.logout_requested.emit)
        footer_layout.addWidget(logout_btn)
        
        self.main_layout.addWidget(self.footer_frame)
        
    def _create_logout_button(self):
        """Create logout button."""
        logout_btn = QPushButton()
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setFixedHeight(48)
        logout_btn.setCursor(Qt.PointingHandCursor)
        
        # Icon
        logout_icon = QLabel("🚪")
        logout_icon.setObjectName("logoutIcon")
        logout_icon.setFixedSize(22, 22)
        logout_icon.setAlignment(Qt.AlignCenter)
        
        # Text
        logout_text = QLabel("Logout")
        logout_text.setObjectName("logoutText")
        
        # Layout
        layout = QHBoxLayout(logout_btn)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        layout.addWidget(logout_icon)
        layout.addWidget(logout_text)
        layout.addStretch()
        
        # Store references
        self.logout_text = logout_text
        
        return logout_btn
        
    def _create_theme_container(self):
        """Create theme toggle container."""
        theme_container = QFrame()
        theme_container.setFixedHeight(48)
        
        # Icon
        theme_icon = QLabel("🌙")
        theme_icon.setObjectName("themeIcon")
        theme_icon.setFixedSize(22, 22)
        theme_icon.setAlignment(Qt.AlignCenter)
        
        # Label
        theme_label = QLabel("Dark Mode")
        theme_label.setObjectName("themeLabel")
        
        # Toggle button
        theme_toggle = QPushButton("●")
        theme_toggle.setObjectName("themeToggle")
        theme_toggle.setFixedSize(50, 26)
        theme_toggle.setProperty("dark", False)
        theme_toggle.setCursor(Qt.PointingHandCursor)
        theme_toggle.clicked.connect(self._toggle_theme)
        
        # Layout
        layout = QHBoxLayout(theme_container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        layout.addWidget(theme_icon)
        layout.addWidget(theme_label)
        layout.addStretch()
        layout.addWidget(theme_toggle)
        
        # Store references
        self.theme_label = theme_label
        self.theme_toggle = theme_toggle
        
        return theme_container
        
    def _setup_animations(self):
        """Setup smooth animations for sidebar transitions."""
        # Width animation
        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(self.animation_duration)
        self.width_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states."""
        self.expanded = not self.expanded
        
        if self.expanded:
            self._expand_sidebar()
        else:
            self._collapse_sidebar()
            
    def _expand_sidebar(self):
        """Expand the sidebar with smooth animation."""
        # Update menu button
        self.menu_btn.setText("☰")
        
        # Animate width
        self.width_animation.setStartValue(self.collapsed_width)
        self.width_animation.setEndValue(self.expanded_width)
        self.width_animation.finished.connect(self._on_expand_finished)
        self.width_animation.start()
        
        # Show text elements with delay
        QTimer.singleShot(100, self._show_text_elements)
        
    def _collapse_sidebar(self):
        """Collapse the sidebar with smooth animation."""
        # Update menu button
        self.menu_btn.setText("☰")
        
        # Hide text elements first
        self._hide_text_elements()
        
        # Animate width with delay
        QTimer.singleShot(50, self._start_collapse_animation)
        
    def _start_collapse_animation(self):
        """Start the collapse width animation."""
        self.width_animation.setStartValue(self.expanded_width)
        self.width_animation.setEndValue(self.collapsed_width)
        self.width_animation.finished.connect(self._on_collapse_finished)
        self.width_animation.start()
        
    def _show_text_elements(self):
        """Show text elements when expanding."""
        for btn in self.nav_buttons:
            btn.title_label.setVisible(True)
            
        self.brand_title.setVisible(True)
        self.brand_subtitle.setVisible(True)
        self.search_input.setVisible(True)
        self.logout_text.setVisible(True)
        self.theme_label.setVisible(True)
        
    def _hide_text_elements(self):
        """Hide text elements when collapsing."""
        for btn in self.nav_buttons:
            btn.title_label.setVisible(False)
            
        self.brand_title.setVisible(False)
        self.brand_subtitle.setVisible(False)
        self.search_input.setVisible(False)
        self.logout_text.setVisible(False)
        self.theme_label.setVisible(False)
        
    def _on_expand_finished(self):
        """Called when expand animation finishes."""
        self.setFixedWidth(self.expanded_width)
        
    def _on_collapse_finished(self):
        """Called when collapse animation finishes."""
        self.setFixedWidth(self.collapsed_width)
        
    def _nav_clicked(self, index):
        """Handle navigation button click."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("selected", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        self.current_page = index
        # Emit signal
        self.page_changed.emit(index)
        
    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_toggle.setProperty("dark", self.is_dark_mode)
        
        # Update theme label and icon
        theme_icon = self.theme_label.parent().layout().itemAt(0).widget()
        theme_icon.setText("☀️" if self.is_dark_mode else "🌙")
        self.theme_label.setText("Light Mode" if self.is_dark_mode else "Dark Mode")
        
        # Apply new theme
        self._apply_theme()
        
        # Emit theme change signal
        self.theme_changed.emit(self.is_dark_mode)
        
    def _apply_theme(self):
        """Apply the current theme to the sidebar."""
        self.setStyleSheet(self._get_modern_style())
        
    def update_user_info(self, user):
        """Update user information in the sidebar."""
        # For future implementation - could show user avatar, name, etc.
        pass
        
    def set_notification_count(self, count):
        """Set notification count badge."""
        # For future implementation
        pass
        
    def _get_modern_style(self):
        """Get modern stylesheet based on current theme."""
        if self.is_dark_mode:
            return self._get_dark_theme_style()
        else:
            return self._get_light_theme_style()
            
    def _get_light_theme_style(self):
        """Get light theme stylesheet."""
        return """
            /* Light Theme - Clean Modern Design */
            ModernSidebar {
                background-color: #ffffff;
                border-right: 1px solid #e5e7eb;
            }
            
            /* Header */
            QFrame#headerFrame {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #f3f4f6;
            }
            
            /* Logo */
            QLabel#logoLabel {
                background-color: #6366f1;
                color: white;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            
            /* Brand Text */
            QLabel#brandTitle {
                color: #111827;
                font-size: 18px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QLabel#brandSubtitle {
                color: #6b7280;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Menu Button */
            QPushButton#menuBtn {
                background-color: transparent;
                color: #6b7280;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px;
            }
            
            QPushButton#menuBtn:hover {
                background-color: #f3f4f6;
                color: #374151;
            }
            
            /* Search */
            QFrame#searchContainer {
                background-color: #ffffff;
                border: none;
            }
            
            QLineEdit#searchInput {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #111827;
            }
            
            QLineEdit#searchInput:focus {
                border-color: #6366f1;
                background-color: #ffffff;
            }
            
            QLineEdit#searchInput::placeholder {
                color: #9ca3af;
            }
            
            /* Navigation */
            QFrame#navContainer {
                background-color: #ffffff;
                border: none;
            }
            
            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                text-align: left;
                padding: 0px;
                margin: 2px 0px;
            }
            
            QPushButton#navButton:hover {
                background-color: #f3f4f6;
            }
            
            QPushButton#navButton[selected="true"] {
                background-color: #6366f1;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navIcon {
                color: white;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navTitle {
                color: white;
                font-weight: 600;
            }
            
            QLabel#navIcon {
                color: #6b7280;
                font-size: 16px;
            }
            
            QLabel#navTitle {
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Footer */
            QFrame#footerFrame {
                background-color: #ffffff;
                border: none;
                border-top: 1px solid #f3f4f6;
            }
            
            /* Logout Button */
            QPushButton#logoutBtn {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                text-align: left;
                padding: 0px;
            }
            
            QPushButton#logoutBtn:hover {
                background-color: #fef2f2;
            }
            
            QLabel#logoutIcon {
                color: #ef4444;
                font-size: 16px;
            }
            
            QLabel#logoutText {
                color: #ef4444;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Theme Toggle */
            QLabel#themeIcon {
                color: #6b7280;
                font-size: 16px;
            }
            
            QLabel#themeLabel {
                color: #374151;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QPushButton#themeToggle {
                background-color: #e5e7eb;
                border: none;
                border-radius: 13px;
                color: #ffffff;
                font-size: 12px;
                text-align: left;
                padding-left: 4px;
            }
            
            QPushButton#themeToggle[dark="true"] {
                background-color: #6366f1;
                text-align: right;
                padding-right: 4px;
                padding-left: 0px;
            }
        """
        
    def _get_dark_theme_style(self):
        """Get dark theme stylesheet."""
        return """
            /* Dark Theme - Modern Design */
            ModernSidebar {
                background-color: #1f2937;
                border-right: 1px solid #374151;
            }
            
            /* Header */
            QFrame#headerFrame {
                background-color: #1f2937;
                border: none;
                border-bottom: 1px solid #374151;
            }
            
            /* Logo */
            QLabel#logoLabel {
                background-color: #6366f1;
                color: white;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            
            /* Brand Text */
            QLabel#brandTitle {
                color: #f9fafb;
                font-size: 18px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QLabel#brandSubtitle {
                color: #9ca3af;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Menu Button */
            QPushButton#menuBtn {
                background-color: transparent;
                color: #9ca3af;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px;
            }
            
            QPushButton#menuBtn:hover {
                background-color: #374151;
                color: #f3f4f6;
            }
            
            /* Search */
            QFrame#searchContainer {
                background-color: #1f2937;
                border: none;
            }
            
            QLineEdit#searchInput {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #f9fafb;
            }
            
            QLineEdit#searchInput:focus {
                border-color: #6366f1;
                background-color: #4b5563;
            }
            
            QLineEdit#searchInput::placeholder {
                color: #6b7280;
            }
            
            /* Navigation */
            QFrame#navContainer {
                background-color: #1f2937;
                border: none;
            }
            
            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                text-align: left;
                padding: 0px;
                margin: 2px 0px;
            }
            
            QPushButton#navButton:hover {
                background-color: #374151;
            }
            
            QPushButton#navButton[selected="true"] {
                background-color: #6366f1;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navIcon {
                color: white;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navTitle {
                color: white;
                font-weight: 600;
            }
            
            QLabel#navIcon {
                color: #9ca3af;
                font-size: 16px;
            }
            
            QLabel#navTitle {
                color: #e5e7eb;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Footer */
            QFrame#footerFrame {
                background-color: #1f2937;
                border: none;
                border-top: 1px solid #374151;
            }
            
            /* Logout Button */
            QPushButton#logoutBtn {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                text-align: left;
                padding: 0px;
            }
            
            QPushButton#logoutBtn:hover {
                background-color: #7f1d1d;
            }
            
            QLabel#logoutIcon {
                color: #ef4444;
                font-size: 16px;
            }
            
            QLabel#logoutText {
                color: #ef4444;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Theme Toggle */
            QLabel#themeIcon {
                color: #9ca3af;
                font-size: 16px;
            }
            
            QLabel#themeLabel {
                color: #e5e7eb;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QPushButton#themeToggle {
                background-color: #4b5563;
                border: none;
                border-radius: 13px;
                color: #f9fafb;
                font-size: 12px;
                text-align: left;
                padding-left: 4px;
            }
            
            QPushButton#themeToggle[dark="true"] {
                background-color: #6366f1;
                text-align: right;
                padding-right: 4px;
                padding-left: 0px;
            }
        """

# For backward compatibility
CollapsibleSidebar = ModernSidebar
