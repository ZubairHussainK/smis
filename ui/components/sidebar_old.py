"""Modern sidebar component with clean design inspired by modern web apps."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QSpacerItem, QSizePolicy,
                           QGraphicsOpacityEffect, QLineEdit, QScrollArea)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
import logging
import os

class ModernSidebar(QWidget):
    """Modern collapsible sidebar with clean design."""
    
    # Signals
    page_changed = pyqtSignal(int)
    theme_changed = pyqtSignal(bool)  # True for dark mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.expanded_width = 280
        self.collapsed_width = 70
        self.animation_duration = 250
        self.current_page = 0
        self.is_dark_mode = False
        
        # Navigation items matching SMIS functionality
        self.nav_items = [
            {"icon": "🏠", "title": "Dashboard", "key": "dashboard"},
            {"icon": "�", "title": "Projects", "key": "projects"},  
            {"icon": "�", "title": "Notifications", "key": "notifications"},
            {"icon": "�", "title": "Analytics", "key": "analytics"},
            {"icon": "❤️", "title": "Likes", "key": "likes"},
            {"icon": "�", "title": "Wallets", "key": "wallets"},
            {"icon": "�", "title": "Messages", "key": "messages"},
        ]
        
        self._init_ui()
        self._setup_animations()
        self._apply_theme()
        
    def _init_ui(self):
        """Initialize the modern sidebar UI."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Set fixed width
        self.setFixedWidth(self.expanded_width)
        
        # Create header
        self._create_header()
        
        # Create search
        self._create_search()
        
        # Create navigation
        self._create_navigation()
        
        # Create footer
        self._create_footer()
        
    def _create_header(self):
        """Create modern header with logo and branding."""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 20, 15, 20)
        header_layout.setSpacing(10)
        
        # Logo container
        logo_container = QHBoxLayout()
        logo_container.setSpacing(12)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setText("SM")
        
        # Brand text
        brand_container = QVBoxLayout()
        brand_container.setSpacing(0)
        
        self.brand_title = QLabel("SMIS")
        self.brand_title.setObjectName("brandTitle")
        
        self.brand_subtitle = QLabel("School Management")
        self.brand_subtitle.setObjectName("brandSubtitle")
        
        brand_container.addWidget(self.brand_title)
        brand_container.addWidget(self.brand_subtitle)
        
        logo_container.addWidget(self.logo_label)
        logo_container.addLayout(brand_container)
        
        # Hamburger/collapse button
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        header_layout.addLayout(logo_container)
        header_layout.addStretch()
        header_layout.addWidget(self.menu_btn)
        
        self.main_layout.addWidget(self.header_frame)
        
    def _create_search(self):
        """Create search bar."""
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(20, 10, 20, 15)
        search_layout.setSpacing(0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedHeight(40)
        
        search_layout.addWidget(self.search_input)
        self.main_layout.addWidget(search_container)
        
    def _create_navigation(self):
        """Create modern navigation menu."""
        # Navigation container
        nav_container = QFrame()
        nav_container.setObjectName("navContainer")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(20, 0, 20, 20)
        nav_layout.setSpacing(8)
        
        # Create navigation buttons
        self.nav_buttons = []
        for i, item in enumerate(self.nav_items):
            btn = self._create_nav_button(item, i)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        
        # Add stretch
        nav_layout.addStretch()
        
        self.main_layout.addWidget(nav_container, 1)
        
    def _create_nav_button(self, item, index):
        """Create a modern navigation button."""
        btn = QPushButton()
        btn.setObjectName("navButton")
        btn.setProperty("index", index)
        btn.setProperty("selected", index == 0)  # First item selected
        btn.setFixedHeight(48)
        
        # Button layout
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(16, 12, 16, 12)
        btn_layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(item["icon"])
        icon_label.setObjectName("navIcon")
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel(item["title"])
        title_label.setObjectName("navTitle")
        
        # Store references
        btn.icon_label = icon_label
        btn.title_label = title_label
        
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(title_label)
        btn_layout.addStretch()
        
        # Connect click
        btn.clicked.connect(lambda checked, idx=index: self._nav_clicked(idx))
        
        return btn
        
    def _create_footer(self):
        """Create modern footer with theme toggle and logout."""
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("footerFrame")
        footer_layout = QVBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(20, 20, 20, 25)
        footer_layout.setSpacing(15)
        
        # Logout button
        logout_container = QFrame()
        logout_layout = QHBoxLayout(logout_container)
        logout_layout.setContentsMargins(0, 0, 0, 0)
        logout_layout.setSpacing(12)
        
        self.logout_btn = QPushButton()
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setFixedHeight(48)
        
        logout_btn_layout = QHBoxLayout(self.logout_btn)
        logout_btn_layout.setContentsMargins(16, 12, 16, 12)
        logout_btn_layout.setSpacing(12)
        
        logout_icon = QLabel("🚪")
        logout_icon.setObjectName("logoutIcon")
        logout_icon.setFixedSize(20, 20)
        logout_icon.setAlignment(Qt.AlignCenter)
        
        self.logout_text = QLabel("Logout")
        self.logout_text.setObjectName("logoutText")
        
        logout_btn_layout.addWidget(logout_icon)
        logout_btn_layout.addWidget(self.logout_text)
        logout_btn_layout.addStretch()
        
        logout_layout.addWidget(self.logout_btn)
        
        # Theme toggle
        theme_container = QFrame()
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 10, 0, 0)
        theme_layout.setSpacing(12)
        
        theme_icon = QLabel("🌙" if not self.is_dark_mode else "☀️")
        theme_icon.setObjectName("themeIcon")
        theme_icon.setFixedSize(20, 20)
        theme_icon.setAlignment(Qt.AlignCenter)
        
        self.theme_label = QLabel("Dark Mode" if not self.is_dark_mode else "Light Mode")
        self.theme_label.setObjectName("themeLabel")
        
        # Theme toggle switch
        self.theme_toggle = QPushButton("●")
        self.theme_toggle.setObjectName("themeToggle")
        self.theme_toggle.setFixedSize(50, 26)
        self.theme_toggle.setProperty("dark", self.is_dark_mode)
        self.theme_toggle.clicked.connect(self._toggle_theme)
        
        theme_layout.addWidget(theme_icon)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_toggle)
        
        footer_layout.addWidget(logout_container)
        footer_layout.addWidget(theme_container)
        
        self.main_layout.addWidget(self.footer_frame)
        
        header_layout.addLayout(top_row)
        header_layout.addWidget(self.subtitle_label)
        
        self.main_layout.addWidget(self.header_frame)
        
    def _create_navigation(self):
        """Create the navigation menu."""
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(8)
        
        # Navigation items with enhanced icons and descriptions
        self.nav_items = [
            {"icon": "dashboard.svg", "fallback": "📊", "title": "Dashboard", "desc": "Overview & Analytics", "badge": None},
            {"icon": "student.svg", "fallback": "�", "title": "Students", "desc": "Manage Student Records", "badge": "1247"}, 
            {"icon": "list.svg", "fallback": "📋", "title": "Classes", "desc": "Class Management", "badge": "42"},
            {"icon": "attendance.svg", "fallback": "📅", "title": "Attendance", "desc": "Daily Attendance", "badge": "New"},
            {"icon": "reports.svg", "fallback": "�", "title": "Reports", "desc": "Generate Reports", "badge": None}
        ]
        
        self.nav_buttons = []
        for i, item in enumerate(self.nav_items):
            btn = self._create_nav_button(item, i)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        
        # Add stretch to push footer to bottom
        nav_layout.addStretch()
        
        self.main_layout.addWidget(nav_frame, 1)
        
    def _create_nav_button(self, item, index):
        """Create an enhanced navigation button with badges."""
        btn = QPushButton()
        btn.setObjectName("navButton")
        btn.setProperty("index", index)
        btn.setProperty("selected", index == 0)  # First item selected by default
        
        # Button layout
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(18, 14, 18, 14)
        btn_layout.setSpacing(15)
        
        # Icon
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
            icon_label.setText(item.get("fallback", "●"))  # Fallback icon
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(3)
        text_container.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(item["title"])
        title_label.setObjectName("navTitle")
        
        desc_label = QLabel(item["desc"])
        desc_label.setObjectName("navDesc")
        
        text_container.addWidget(title_label)
        text_container.addWidget(desc_label)
        
        # Badge/Counter
        badge_label = None
        if item.get("badge"):
            badge_label = QLabel(str(item["badge"]))
            badge_label.setObjectName("navBadge")
            badge_label.setFixedHeight(20)
            badge_label.setAlignment(Qt.AlignCenter)
            
            # Different styles for different badge types
            if item["badge"] == "New":
                badge_label.setProperty("type", "new")
            elif item["badge"].isdigit():
                badge_label.setProperty("type", "count")
            else:
                badge_label.setProperty("type", "info")
        
        # Store references for animations
        btn.icon_label = icon_label
        btn.title_label = title_label
        btn.desc_label = desc_label
        btn.text_container = text_container
        btn.badge_label = badge_label
        
        btn_layout.addWidget(icon_label)
        btn_layout.addLayout(text_container)
        if badge_label:
            btn_layout.addWidget(badge_label)
        else:
            btn_layout.addStretch()
        
        # Connect click event
        btn.clicked.connect(lambda checked, idx=index: self._nav_clicked(idx))
        
        # Add hover effects
        btn.enterEvent = lambda event, b=btn: self._on_button_hover(b, True)
        btn.leaveEvent = lambda event, b=btn: self._on_button_hover(b, False)
        
        return btn
        
    def _create_footer(self):
        """Create the enhanced footer section with admin profile and controls."""
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("footerFrame")
        footer_layout = QVBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(20, 20, 20, 25)
        footer_layout.setSpacing(15)
        
        # Status indicator
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 8, 12, 8)
        status_layout.setSpacing(8)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setFixedSize(12, 12)
        
        self.status_label = QLabel("System Online")
        self.status_label.setObjectName("statusLabel")
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Admin profile section
        profile_frame = QFrame()
        profile_frame.setObjectName("profileFrame")
        profile_layout = QHBoxLayout(profile_frame)
        profile_layout.setContentsMargins(15, 12, 15, 12)
        profile_layout.setSpacing(12)
        
        # Admin avatar with status
        avatar_container = QFrame()
        avatar_container.setFixedSize(48, 48)
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatarLabel")
        self.avatar_label.setFixedSize(44, 44)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setText("�‍💼")  # Admin avatar
        
        avatar_layout.addWidget(self.avatar_label)
        
        # Admin info
        user_info = QVBoxLayout()
        user_info.setSpacing(3)
        
        self.user_name = QLabel("Dr. Ahmed Hassan")
        self.user_name.setObjectName("userName")
        
        self.user_role = QLabel("Principal Administrator")
        self.user_role.setObjectName("userRole")
        
        # Last login info
        self.last_login = QLabel("Last: Today 09:30 AM")
        self.last_login.setObjectName("lastLogin")
        
        user_info.addWidget(self.user_name)
        user_info.addWidget(self.user_role)
        user_info.addWidget(self.last_login)
        
        profile_layout.addWidget(avatar_container)
        profile_layout.addLayout(user_info)
        profile_layout.addStretch()
        
        # Action buttons row
        actions_frame = QFrame()
        actions_frame.setObjectName("actionsFrame")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(10)
        
        # Quick access buttons
        self.notifications_btn = QPushButton("🔔")
        self.notifications_btn.setObjectName("actionBtn")
        self.notifications_btn.setFixedSize(36, 36)
        self.notifications_btn.setToolTip("Notifications (3 new)")
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("actionBtn")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setToolTip("System Settings")
        
        self.help_btn = QPushButton("❓")
        self.help_btn.setObjectName("actionBtn")
        self.help_btn.setFixedSize(36, 36)
        self.help_btn.setToolTip("Help & Support")
        
        self.logout_btn = QPushButton("⏻")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setFixedSize(36, 36)
        self.logout_btn.setToolTip("Logout")
        
        actions_layout.addWidget(self.notifications_btn)
        actions_layout.addWidget(self.settings_btn)
        actions_layout.addWidget(self.help_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.logout_btn)
        
        footer_layout.addWidget(status_frame)
        footer_layout.addWidget(profile_frame)
        footer_layout.addWidget(actions_frame)
        
        self.main_layout.addWidget(self.footer_frame)
        
    def _setup_animations(self):
        """Setup animations for sidebar collapse/expand."""
        # Width animation
        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(self.animation_duration)
        self.width_animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Opacity animations for text elements
        self.text_animations = []
        
    def _setup_timers(self):
        """Setup timers for delayed animations."""
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self._apply_hover_effect)
        
    def _apply_hover_effect(self):
        """Apply hover effect (placeholder for future enhancements)."""
        pass
        
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states."""
        self.expanded = not self.expanded
        
        if self.expanded:
            self._expand_sidebar()
        else:
            self._collapse_sidebar()
            
    def _expand_sidebar(self):
        """Expand the sidebar with animation."""
        # Update toggle button
        self.toggle_btn.setText("◀")
        
        # Animate width
        self.width_animation.setStartValue(self.collapsed_width)
        self.width_animation.setEndValue(self.expanded_width)
        self.width_animation.finished.connect(self._on_expand_finished)
        self.width_animation.start()
        
        # Show text elements with delay
        QTimer.singleShot(120, self._show_text_elements)
        
    def _collapse_sidebar(self):
        """Collapse the sidebar with animation."""
        # Update toggle button
        self.toggle_btn.setText("▶")
        
        # Hide text elements first
        self._hide_text_elements()
        
        # Animate width with delay
        QTimer.singleShot(80, self._start_collapse_animation)
        
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
            btn.desc_label.setVisible(True)
            
        self.title_label.setVisible(True)
        self.subtitle_label.setVisible(True)
        self.user_name.setVisible(True)
        self.user_role.setVisible(True)
        
    def _hide_text_elements(self):
        """Hide text elements when collapsing."""
        for btn in self.nav_buttons:
            btn.title_label.setVisible(False)
            btn.desc_label.setVisible(False)
            
        self.title_label.setVisible(False)
        self.subtitle_label.setVisible(False)
        self.user_name.setVisible(False)
        self.user_role.setVisible(False)
        
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
            
        # Emit signal
        self.page_changed.emit(index)
        
    def _on_button_hover(self, button, is_entering):
        """Handle button hover effects."""
        if is_entering:
            button.setProperty("hovered", True)
        else:
            button.setProperty("hovered", False)
            
        button.style().unpolish(button)
        button.style().polish(button)
        
    def _get_sidebar_style(self):
        """Get the complete sidebar stylesheet with modern design."""
        return """
            /* Main Sidebar - Modern Dark Theme */
            CollapsibleSidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2D3748, stop:1 #1A202C);
                border-right: 2px solid #4A5568;
            }
            
            /* Header Frame - Elegant Blue Gradient */
            QFrame#headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #667EEA, stop:1 #764BA2);
                border: none;
                border-radius: 0px;
            }
            
            /* Logo */
            QLabel#logoLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
            
            /* Title */
            QLabel#titleLabel {
                color: white;
                font-size: 22px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 700;
                background: transparent;
                border: none;
                letter-spacing: 1px;
            }
            
            /* Subtitle */
            QLabel#subtitleLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 10px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                background: transparent;
                border: none;
                margin-top: 2px;
            }
            
            /* Toggle Button - Modern Round Design */
            QPushButton#toggleBtn {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 14px;
                font-size: 12px;
                font-weight: bold;
            }
            
            QPushButton#toggleBtn:hover {
                background: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
            }
            
            QPushButton#toggleBtn:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
            
            /* Navigation Frame */
            QFrame#navFrame {
                background: transparent;
                border: none;
            }
            
            /* Navigation Buttons - Clean Modern Style */
            QPushButton#navButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 0px;
                margin: 3px 0px;
                min-height: 48px;
            }
            
            QPushButton#navButton[selected="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667EEA, stop:1 #764BA2);
                border: none;
            }
            
            QPushButton#navButton[hovered="true"] {
                background: rgba(102, 126, 234, 0.2);
                border: 1px solid rgba(102, 126, 234, 0.3);
            }
            
            QPushButton#navButton:pressed {
                background: rgba(102, 126, 234, 0.4);
            }
            
            /* Navigation Icons - Clean & Consistent */
            QLabel#navIcon {
                color: #A0AEC0;
                background: transparent;
                border: none;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navIcon {
                color: white;
            }
            
            /* Navigation Titles - Better Typography */
            QLabel#navTitle {
                color: #E2E8F0;
                font-size: 13px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 600;
                background: transparent;
                border: none;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navTitle {
                color: white;
                font-weight: 700;
            }
            
            /* Navigation Descriptions - Subtle */
            QLabel#navDesc {
                color: #A0AEC0;
                font-size: 10px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                background: transparent;
                border: none;
            }
            
            QPushButton#navButton[selected="true"] QLabel#navDesc {
                color: rgba(255, 255, 255, 0.8);
            }
            
            /* Footer Frame - Subtle Separation */
            QFrame#footerFrame {
                background: transparent;
                border: none;
                border-top: 1px solid #4A5568;
            }
            
            /* Profile Frame - Modern Card Style */
            QFrame#profileFrame {
                background: rgba(74, 85, 104, 0.3);
                border: 1px solid #4A5568;
                border-radius: 12px;
            }
            
            /* Avatar - Professional Circle */
            QLabel#avatarLabel {
                color: #E2E8F0;
                font-size: 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #667EEA, stop:1 #764BA2);
                border: 2px solid #667EEA;
                border-radius: 16px;
            }
            
            /* User Name - Clear & Readable */
            QLabel#userName {
                color: #F7FAFC;
                font-size: 12px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 600;
                background: transparent;
                border: none;
            }
            
            /* User Role - Subtle */
            QLabel#userRole {
                color: #A0AEC0;
                font-size: 9px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                background: transparent;
                border: none;
            }
            
            /* Action Buttons - Clean Icons */
            QPushButton#actionBtn {
                background: rgba(74, 85, 104, 0.4);
                color: #E2E8F0;
                border: 1px solid #4A5568;
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            
            QPushButton#actionBtn:hover {
                background: rgba(102, 126, 234, 0.3);
                border-color: #667EEA;
                color: white;
            }
            
            QPushButton#actionBtn:pressed {
                background: rgba(102, 126, 234, 0.5);
            }
        """
