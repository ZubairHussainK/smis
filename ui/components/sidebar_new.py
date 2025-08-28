"""
Modern Sidebar Component for SMIS
Codinglab-style modern design with collapsible states, search, and theme toggle
"""

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgRenderer

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import centralized styles
from resources.style import get_sidebar_modern_style

class ModernSidebar(QFrame):
    """Modern collapsible sidebar with professional design."""
    
    # Signals
    page_changed = pyqtSignal(int)
    theme_changed = pyqtSignal(bool)
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # State variables
        self.expanded_width = 250
        self.collapsed_width = 60
        self.is_dark_mode = False
        self.current_page = 0
        
        # Setup UI
        self._setup_ui()
        self._setup_animations()
        self._apply_theme()
        
        # Ensure fonts are properly set on initialization with multiple refreshes
        QTimer.singleShot(100, self._refresh_font_sizes)
        QTimer.singleShot(300, self._refresh_font_sizes)
        QTimer.singleShot(500, self._refresh_font_sizes)
        
    def _setup_ui(self):
        """Initialize the sidebar UI components."""
        self.setObjectName("ModernSidebar")
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 16, 12, 16)
        main_layout.setSpacing(16)
        
        # Header section
        self._create_header(main_layout)
        
        # Search section
        self._create_search(main_layout)
        
        # Navigation section
        self._create_navigation(main_layout)
        
        # Footer section  
        self._create_footer(main_layout)
        
    def _create_header(self, parent_layout):
        """Create header with logo and menu button."""
        # Header frame
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(4, 8, 4, 8)
        header_layout.setSpacing(12)
        
        # Logo container
        logo_container = QFrame()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(12)
        
        # Logo (letter S)
        self.logo_label = QLabel("S")
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(self.logo_label)
        
        # Brand text container
        brand_container = QFrame()
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(0)
        
        self.brand_title = QLabel("SMIS")
        self.brand_title.setObjectName("brandTitle")
        brand_layout.addWidget(self.brand_title)
        
        self.brand_subtitle = QLabel("Management System")
        self.brand_subtitle.setObjectName("brandSubtitle")
        brand_layout.addWidget(self.brand_subtitle)
        
        logo_layout.addWidget(brand_container)
        
        header_layout.addWidget(logo_container)
        header_layout.addStretch()
        
        # Menu button (hamburger)
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.clicked.connect(self._toggle_sidebar)
        header_layout.addWidget(self.menu_btn)
        
        parent_layout.addWidget(header_frame)
        
    def _create_search(self, parent_layout):
        """Create search input."""
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search...")
        search_layout.addWidget(self.search_input)
        
        parent_layout.addWidget(search_container)
        
    def _create_navigation(self, parent_layout):
        """Create navigation buttons."""
        nav_container = QFrame()
        nav_container.setObjectName("navContainer")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(4)
        
        # Navigation items
        nav_items = [
            ("📊", "Dashboard"),
            ("👤", "Students"),
            ("📋", "Student List"),
            ("📅", "Attendance"),
            ("📈", "Reports")
        ]
        
        self.nav_buttons = []
        
        for i, (icon, title) in enumerate(nav_items):
            btn_container = QPushButton()
            btn_container.setObjectName("navButton")
            btn_container.clicked.connect(lambda checked, idx=i: self._on_nav_clicked(idx))
            
            # Button layout
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(12, 8, 12, 8)
            btn_layout.setSpacing(12)
            
            # Icon
            icon_label = QLabel(icon)
            icon_label.setObjectName("navIcon")
            icon_label.setFixedSize(18, 18)
            icon_label.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(icon_label)
            
            # Title
            title_label = QLabel(title)
            title_label.setObjectName("navTitle")
            btn_layout.addWidget(title_label)
            btn_layout.addStretch()
            
            # Store references
            btn_container.icon_label = icon_label
            btn_container.title_label = title_label
            
            nav_layout.addWidget(btn_container)
            self.nav_buttons.append(btn_container)
            
        # Set first button as selected
        if self.nav_buttons:
            self.nav_buttons[0].setProperty("selected", True)
            
        nav_layout.addStretch()
        parent_layout.addWidget(nav_container)
        
    def _create_footer(self, parent_layout):
        """Create footer with logout and theme toggle."""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(8)
        
        # Logout button
        logout_btn = QPushButton()
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self._on_logout_clicked)
        
        logout_layout = QHBoxLayout(logout_btn)
        logout_layout.setContentsMargins(12, 8, 12, 8)
        logout_layout.setSpacing(12)
        
        logout_icon = QLabel("🚪")
        logout_icon.setObjectName("logoutIcon")
        logout_icon.setFixedSize(18, 18)
        logout_icon.setAlignment(Qt.AlignCenter)
        logout_layout.addWidget(logout_icon)
        
        self.logout_text = QLabel("Logout")
        self.logout_text.setObjectName("logoutText")
        logout_layout.addWidget(self.logout_text)
        logout_layout.addStretch()
        
        footer_layout.addWidget(logout_btn)
        
        # Theme toggle
        theme_container = QFrame()
        theme_container.setObjectName("themeContainer")
        theme_container.mousePressEvent = lambda event: self._toggle_theme()
        
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(12, 8, 12, 8)
        theme_layout.setSpacing(12)
        
        self.theme_icon = QLabel("🌙")
        self.theme_icon.setObjectName("themeIcon")
        self.theme_icon.setFixedSize(18, 18)
        self.theme_icon.setAlignment(Qt.AlignCenter)
        theme_layout.addWidget(self.theme_icon)
        
        self.theme_label = QLabel("Dark Mode")
        self.theme_label.setObjectName("themeLabel")
        theme_layout.addWidget(self.theme_label)
        theme_layout.addStretch()
        
        # Store container reference
        self.theme_container = theme_container
        
        footer_layout.addWidget(theme_container)
        parent_layout.addWidget(footer_frame)
        
    def _setup_animations(self):
        """Setup animations for sidebar toggle."""
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
    def _toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states."""
        if self.width() == self.expanded_width:
            # Collapse
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation.finished.connect(lambda: self._hide_text_elements())
        else:
            # Expand
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation.finished.connect(lambda: self._show_text_elements())
            
        self.animation.start()
        
    def _hide_text_elements(self):
        """Hide text elements when collapsed."""
        self.brand_title.hide()
        self.brand_subtitle.hide()
        self.search_input.hide()
        self.logout_text.hide()
        self.theme_label.hide()
        
        for btn in self.nav_buttons:
            if hasattr(btn, 'title_label'):
                btn.title_label.hide()
                
    def _show_text_elements(self):
        """Show text elements when expanded."""
        self.brand_title.show()
        self.brand_subtitle.show()
        self.search_input.show()
        self.logout_text.show()
        self.theme_label.show()
        
        for btn in self.nav_buttons:
            if hasattr(btn, 'title_label'):
                btn.title_label.show()
                
    def _on_nav_clicked(self, index):
        """Handle navigation button click."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("selected", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # Update current page
        self.current_page = index
        # Emit signal
        self.page_changed.emit(index)
        
    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        self.is_dark_mode = not self.is_dark_mode
        
        # Update theme label and icon
        if self.is_dark_mode:
            self.theme_icon.setText("☀️")
            if hasattr(self, 'theme_label') and self.theme_label:
                self.theme_label.setText("Light Mode")
        else:
            self.theme_icon.setText("🌙")
            if hasattr(self, 'theme_label') and self.theme_label:
                self.theme_label.setText("Dark Mode")
        
        # Refresh styling for theme container
        if hasattr(self, 'theme_container'):
            self.theme_container.style().unpolish(self.theme_container)
            self.theme_container.style().polish(self.theme_container)
        
        # Apply new theme
        self._apply_theme()
        
        # Restore proper visibility based on current state
        if self.expanded_width == self.width():
            # Expanded state - show all elements
            self._show_text_elements()
        else:
            # Collapsed state - hide text but show icons
            self._hide_text_elements()
            
        # Force update of all elements
        self.update()
        
        # Emit theme change signal
        self.theme_changed.emit(self.is_dark_mode)
        
    def _apply_theme(self):
        """Apply the current theme to the sidebar with font protection."""
        # Set the main stylesheet from centralized file
        self.setStyleSheet(self._get_modern_style())
        
        # Force refresh all elements after theme change
        self._refresh_visibility()
        
        # Immediate font size enforcement
        self._refresh_font_sizes()
        
        # Multiple delayed font size refreshes to combat any interference
        QTimer.singleShot(25, self._safe_refresh_fonts)
        QTimer.singleShot(75, self._safe_refresh_fonts)
        QTimer.singleShot(150, self._safe_refresh_fonts)
        QTimer.singleShot(300, self._safe_refresh_fonts)
        
        # Also force style reapplication with safety check
        QTimer.singleShot(100, self._safe_reapply_style)
        QTimer.singleShot(200, self._safe_reapply_style)
        
    def _safe_refresh_fonts(self):
        """Safely refresh fonts with existence check."""
        try:
            if not self.isVisible():
                return
            self._refresh_font_sizes()
        except RuntimeError:
            pass  # Widget has been deleted
            
    def _safe_reapply_style(self):
        """Safely reapply styles with existence check."""
        try:
            if not self.isVisible():
                return
            self.setStyleSheet(self._get_modern_style())
        except RuntimeError:
            pass  # Widget has been deleted
        
    def _refresh_visibility(self):
        """Refresh visibility of all elements."""
        if self.width() == self.expanded_width:
            self._show_text_elements()
        else:
            self._hide_text_elements()
            
    def _refresh_font_sizes(self):
        """Force refresh font sizes for all text elements with aggressive enforcement."""
        try:
            # First, completely override any parent styles by re-setting the main stylesheet
            self.setStyleSheet(self._get_modern_style())
            
            # Brand text - force larger fonts with explicit settings
            if hasattr(self, 'brand_title') and self.brand_title:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(18)
                font.setBold(True)
                font.setWeight(QFont.Bold)
                self.brand_title.setFont(font)
                # Force style override with !important-like behavior
                self.brand_title.setStyleSheet("font-size: 18px !important; font-weight: bold !important; color: inherit;")
                
            if hasattr(self, 'brand_subtitle') and self.brand_subtitle:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(12)
                font.setWeight(QFont.Normal)
                self.brand_subtitle.setFont(font)
                self.brand_subtitle.setStyleSheet("font-size: 12px !important; font-weight: normal !important; color: inherit;")
                
            # Navigation buttons - force consistent sizes
            for btn in self.nav_buttons:
                if hasattr(btn, 'title_label') and btn.title_label:
                    font = QFont()
                    font.setFamily("Segoe UI")
                    font.setPointSize(14)
                    font.setBold(True)
                    font.setWeight(QFont.Bold)
                    btn.title_label.setFont(font)
                    btn.title_label.setStyleSheet("font-size: 14px !important; font-weight: bold !important; color: inherit;")
                    
                if hasattr(btn, 'icon_label') and btn.icon_label:
                    font = QFont()
                    font.setFamily("Segoe UI")
                    font.setPointSize(16)
                    font.setWeight(QFont.Normal)
                    btn.icon_label.setFont(font)
                    btn.icon_label.setStyleSheet("font-size: 16px !important; font-weight: normal !important; color: inherit;")
                    
            # Footer elements - force readable sizes
            if hasattr(self, 'logout_text') and self.logout_text:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(14)
                font.setBold(True)
                font.setWeight(QFont.Bold)
                self.logout_text.setFont(font)
                self.logout_text.setStyleSheet("font-size: 14px !important; font-weight: bold !important; color: inherit;")
                
            if hasattr(self, 'theme_label') and self.theme_label:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(13)
                font.setWeight(QFont.Normal)
                self.theme_label.setFont(font)
                self.theme_label.setStyleSheet("font-size: 13px !important; font-weight: normal !important; color: inherit;")
                
            # Theme icon
            if hasattr(self, 'theme_icon') and self.theme_icon:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(14)
                font.setWeight(QFont.Normal)
                self.theme_icon.setFont(font)
                self.theme_icon.setStyleSheet("font-size: 14px !important; font-weight: normal !important; color: inherit;")
                
            # Force immediate update with multiple methods
            self.update()
            self.repaint()
            
            # Also force update of all child widgets
            for child in self.findChildren(QLabel):
                child.update()
                child.repaint()
                
        except Exception as e:
            print(f"Error in _refresh_font_sizes: {e}")
        
    def _on_logout_clicked(self):
        """Handle logout button click."""
        self.logout_requested.emit()
        
    def _get_modern_style(self):
        """Get modern stylesheet based on current theme from centralized style file."""
        return get_sidebar_modern_style(self.is_dark_mode)

# For backward compatibility
CollapsibleSidebar = ModernSidebar
