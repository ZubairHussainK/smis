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

# Import Material Design icons
from utils.material_icons import MaterialIcons, SMISIcons

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
        
        # Setup UI first
        self._setup_ui()
        
        # Apply consistent fonts IMMEDIATELY after UI setup
        self._apply_consistent_fonts()
        
        # Setup animations
        self._setup_animations()
        
        # Apply theme (this might override fonts, so we reapply after)
        self._apply_theme()
        
        # IMMEDIATELY reapply fonts after theme to ensure consistency
        self._apply_consistent_fonts()
        
        # Setup intelligent font enforcement system
        self._setup_nuclear_font_enforcement()
        
        # Force multiple font applications during startup to ensure visibility
        QTimer.singleShot(50, self._apply_consistent_fonts)
        QTimer.singleShot(100, self._apply_consistent_fonts)
        QTimer.singleShot(200, self._apply_consistent_fonts)
        QTimer.singleShot(300, self._apply_consistent_fonts)
        
        print("✅ Sidebar initialized with consistent fonts")
        
    def _setup_nuclear_font_enforcement(self):
        """Setup intelligent font enforcement to resist global style interference."""
        print("🔒 Setting up INTELLIGENT font enforcement for sidebar...")
        
        # Prevent multiple font enforcement systems on the same sidebar
        if hasattr(self, 'nuclear_font_timer') and self.nuclear_font_timer:
            print("⚠️ Font enforcement already active, skipping setup")
            return
        
        # Create smart font enforcer timer - much less frequent to prevent flashing
        self.nuclear_font_timer = QTimer()
        self.nuclear_font_timer.timeout.connect(self._smart_font_enforcement)
        
        # Run every 2 seconds to prevent flashing but maintain protection
        self.nuclear_font_timer.start(2000)
        
        # Track animation state to avoid interference
        self.animation_in_progress = False
        
        print("✅ INTELLIGENT font enforcement ACTIVATED!")
        
        # Initialize header visibility after enforcement is set up
        QTimer.singleShot(100, self._initialize_header_visibility)
        
    def _smart_font_enforcement(self):
        """Smart font enforcement - avoids interference during animations."""
        try:
            # Skip enforcement during animations to prevent flashing
            if self.animation_in_progress:
                return
                
            # Skip enforcement if animation group is running
            if hasattr(self, 'animation_group') and self.animation_group.state() == QAbstractAnimation.Running:
                return
                
            # Apply fonts only when stable
            self._apply_consistent_fonts()
                
        except Exception:
            pass  # Silent enforcement
            
    def _apply_consistent_fonts(self):
        """Apply consistent fonts to match exactly the default specifications EVERY time."""
        try:
            # NUCLEAR FORCE EXACT DEFAULT SPECIFICATIONS for navigation labels
            for btn in self.nav_buttons:
                if hasattr(btn, 'title_label') and btn.title_label:
                    # EXACT SPECIFICATIONS: 14px, weight 600, Poppins
                    font = QFont("Poppins")
                    font.setPointSize(14)
                    font.setWeight(600)  # EXACT match to CSS font-weight: 600
                    btn.title_label.setFont(font)
                    
                    # ULTRA-AGGRESSIVE TEXT ALIGNMENT ENFORCEMENT
                    btn.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    btn.title_label.setMinimumHeight(44)
                    btn.title_label.setMaximumHeight(44)
                    btn.title_label.setFixedHeight(44)  # Force exact height
                    
                    # NUCLEAR CSS override with THEME-AWARE TEXT COLOR
                    text_color = '#e5e7eb' if self.is_dark_mode else '#374151'
                    
                    btn.title_label.setStyleSheet(f"""
                        QLabel {{
                            font-size: 14px !important; 
                            font-weight: 600 !important; 
                            font-family: 'Poppins', sans-serif !important;
                            color: {text_color} !important;
                            min-height: 44px !important;
                            max-height: 44px !important;
                            height: 44px !important;
                            background-color: transparent !important;
                            border: none !important;
                            padding: 0px 8px !important;
                            margin: 0px !important;
                            qproperty-alignment: 'AlignVCenter | AlignLeft' !important;
                            text-align: left !important;
                            vertical-align: middle !important;
                            line-height: 44px !important;
                        }}
                    """)
                    
                    # FORCE objectName for CSS targeting
                    btn.title_label.setObjectName("sidebarNavTitle")
                    
                    # ULTRA-NUCLEAR Qt property forcing for text positioning
                    btn.title_label.setWordWrap(False)  # Prevent text wrapping
                    btn.title_label.setScaledContents(False)  # Prevent scaling
                    btn.title_label.setMargin(0)  # Force zero margin
                    
                # FORCE proper button container spacing and alignment with NUCLEAR HEIGHT ENFORCEMENT
                if hasattr(btn, 'setFixedHeight'):
                    btn.setFixedHeight(44)  # Consistent button height
                    btn.setMinimumHeight(44)  # Force minimum height
                    btn.setMaximumHeight(44)  # Force maximum height
                    
                if hasattr(btn, 'layout') and btn.layout():
                    btn.layout().setSpacing(8)  # Equal spacing between icon and text
                    btn.layout().setContentsMargins(8, 4, 8, 4)  # Equal margins
                        
            # Apply consistent fonts to footer elements
            self._apply_footer_fonts()
                
        except Exception as e:
            pass  # Silent font application to prevent crashes
            
    def _apply_footer_fonts(self):
        """Apply consistent fonts to footer elements."""
        try:
            # Apply fonts to footer buttons
            if hasattr(self, 'logout_text') and self.logout_text:
                font = QFont("Poppins")
                font.setPointSize(14)
                font.setWeight(600)
                self.logout_text.setFont(font)
                
            if hasattr(self, 'theme_text') and self.theme_text:
                font = QFont("Poppins")
                font.setPointSize(14)
                font.setWeight(600)
                self.theme_text.setFont(font)
                
        except Exception as e:
            pass  # Silent font application to prevent crashes
            
    def _force_layout_spacing(self):
        """Force proper layout spacing and vertical alignment"""
        try:
            # Force main navigation layout spacing
            if hasattr(self, 'nav_layout') and self.nav_layout:
                self.nav_layout.setSpacing(8)
                self.nav_layout.setContentsMargins(8, 4, 8, 4)
                
            # Force each navigation button to proper dimensions and alignment
            for btn in self.nav_buttons:
                # ULTRA-AGGRESSIVE HEIGHT ENFORCEMENT
                btn.setFixedHeight(44)
                btn.setMinimumHeight(44)
                btn.setMaximumHeight(44)
                
                if hasattr(btn, 'title_label') and btn.title_label:
                    # ULTRA-NUCLEAR TEXT ALIGNMENT AND POSITIONING ENFORCEMENT
                    btn.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    btn.title_label.setMinimumHeight(44)
                    btn.title_label.setMaximumHeight(44)
                    btn.title_label.setFixedHeight(44)
                    
                    # PREVENT TEXT SHIFTING
                    btn.title_label.setWordWrap(False)
                    btn.title_label.setScaledContents(False)
                    btn.title_label.setMargin(0)
                    
                    # FORCE FONT AGAIN (anti-flashing)
                    font = btn.title_label.font()
                    font.setFamily("Poppins")
                    font.setPointSize(14)
                    font.setWeight(600)
                    btn.title_label.setFont(font)
                    
                # Force button layout spacing
                if hasattr(btn, 'layout') and btn.layout():
                    btn.layout().setSpacing(8)
                    btn.layout().setContentsMargins(8, 4, 8, 4)
                    
            # Force footer elements alignment and PREVENT OVERLAPPING - ULTRA-AGGRESSIVE
            if hasattr(self, 'logout_text') and self.logout_text:
                self.logout_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.logout_text.setMinimumHeight(44)
                self.logout_text.setMaximumHeight(44)
                self.logout_text.setFixedHeight(44)
                
            if hasattr(self, 'theme_label') and self.theme_label:
                self.theme_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.theme_label.setMinimumHeight(44)
                self.theme_label.setMaximumHeight(44)
                self.theme_label.setFixedHeight(44)
                
            # ULTRA-AGGRESSIVE FOOTER LAYOUT SPACING to prevent overlapping
            if hasattr(self, 'footer_frame') and hasattr(self.footer_frame, 'layout'):
                footer_layout = self.footer_frame.layout()
                if footer_layout:
                    footer_layout.setSpacing(8)  # Proper spacing between logout and theme
                    footer_layout.setContentsMargins(8, 8, 8, 8)  # Consistent margins
                    
            # NUCLEAR CONTAINER HEIGHT ENFORCEMENT to prevent overlapping
            logout_buttons = self.findChildren(QPushButton, "logoutBtn")
            for logout_btn in logout_buttons:
                logout_btn.setFixedHeight(44)
                logout_btn.setMaximumHeight(44)
                logout_btn.setMinimumHeight(44)
                
            if hasattr(self, 'theme_container') and self.theme_container:
                self.theme_container.setFixedHeight(44)
                self.theme_container.setMaximumHeight(44)
                self.theme_container.setMinimumHeight(44)
                
            # FORCE FOOTER POSITIONING to prevent overlap during theme changes
            footer_frames = self.findChildren(QFrame, "footerFrame")
            for footer_frame in footer_frames:
                footer_frame.setMinimumHeight(110)  # Ensure enough space for both buttons
                footer_frame.setMaximumHeight(110)  # Prevent expansion
                if footer_frame.layout():
                    footer_frame.layout().setSpacing(8)
                    footer_frame.layout().setContentsMargins(0, 8, 0, 8)
                
            # Force widget updates
            self.updateGeometry()
            self.update()
            
        except Exception as e:
            print(f"Error in layout spacing: {e}")
        
    def _setup_ui(self):
        """Initialize the sidebar UI components."""
        self.setObjectName("ModernSidebar")
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(600)
        
        # Main layout with zero top margin - logo at absolute top
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Zero all margins
        main_layout.setSpacing(0)  # Zero spacing for logo at top
        
        # Add header first - will be at absolute top
        self._create_header(main_layout)
        
        # Add spacing before navigation to separate sections
        main_layout.addSpacing(16)
        
        # Navigation section (search removed)
        self._create_navigation(main_layout)
        
        # Add stretch before footer to push footer to bottom
        main_layout.addStretch()
        
        # Footer section  
        self._create_footer(main_layout)
        
    def _create_header(self, parent_layout):
        """Create header with organization logo and menu button only."""
        # Header frame with better styling
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            QFrame#headerFrame {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)  # Zero all margins for logo at very top
        header_layout.setSpacing(16)
        
        # Organization Logo (horizontal) - changes based on sidebar state
        self.org_logo_expanded = QLabel()
        self.org_logo_expanded.setObjectName("orgLogoExpanded")
        self.org_logo_expanded.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.org_logo_expanded.setFixedHeight(50)  # Better height for horizontal logo
        self.org_logo_expanded.setMinimumWidth(120)  # Ensure enough space
        self.org_logo_expanded.setContentsMargins(0, 0, 0, 0)  # No margins - logo at top
        self._load_expanded_logo()
        
        self.org_logo_collapsed = QLabel()
        self.org_logo_collapsed.setObjectName("orgLogoCollapsed")
        self.org_logo_collapsed.setFixedSize(40, 40)
        self.org_logo_collapsed.setAlignment(Qt.AlignCenter)
        self.org_logo_collapsed.setContentsMargins(0, 0, 0, 0)  # No margins - logo at top
        self.org_logo_collapsed.hide()  # Start hidden
        self._load_collapsed_logo()
        
        header_layout.addWidget(self.org_logo_expanded)
        header_layout.addWidget(self.org_logo_collapsed)
        header_layout.addStretch()
        
        # Create modern floating toggle button (circular, 50% in/out)
        self._create_floating_toggle_button()
        
        parent_layout.addWidget(header_frame)
        
    def _initialize_header_visibility(self):
        """Initialize header element visibility for expanded state."""
        # Show expanded logo and hide collapsed logo initially
        self.org_logo_expanded.show()
        self.org_logo_collapsed.hide()
        
        # Initialize floating toggle button position and icon
        self._position_toggle_button()
        self._update_toggle_button_icon(True)  # Start in expanded state
        
    def _load_expanded_logo(self):
        """Load and set the expanded (horizontal) organization logo."""
        try:
            # Try to load the horizontal logo image
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "resources", "logos", "Horizintal_logo.png")
            
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # Scale logo to fit nicely in the header (better proportions)
                    scaled_pixmap = pixmap.scaled(120, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.org_logo_expanded.setPixmap(scaled_pixmap)
                    print("✅ Horizontal logo loaded successfully")
                else:
                    # Fallback to text if image loading fails
                    self.org_logo_expanded.setText("SIF")
                    self.org_logo_expanded.setStyleSheet("""
                        QLabel {
                            font-size: 24px;
                            font-weight: bold;
                            color: #3b82f6;
                            font-family: 'Poppins', sans-serif;
                        }
                    """)
                    print("⚠️ Horizontal logo file corrupt, using text fallback")
            else:
                # Fallback to text if file doesn't exist
                self.org_logo_expanded.setText("SIF")
                self.org_logo_expanded.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        font-weight: bold;
                        color: #3b82f6;
                        font-family: 'Poppins', sans-serif;
                    }
                """)
                print("⚠️ Horizintal_logo.png not found, using text fallback")
                
        except Exception as e:
            print(f"Error loading expanded logo: {e}")
            # Fallback to text
            self.org_logo_expanded.setText("SIF")
            self.org_logo_expanded.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #3b82f6;
                    font-family: 'Poppins', sans-serif;
                }
            """)
    
    def _load_collapsed_logo(self):
        """Load and set the collapsed (circular) organization logo."""
        try:
            # Try to load the circular logo image
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "resources", "logos", "circel_logo.png")
            
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # Scale the logo to fit the collapsed sidebar (40x40)
                    scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.org_logo_collapsed.setPixmap(scaled_pixmap)
                    print("✅ Circle logo loaded successfully")
                else:
                    # Fallback to text if image loading fails
                    self.org_logo_collapsed.setText("S")
                    self.org_logo_collapsed.setStyleSheet("""
                        QLabel {
                            font-size: 18px;
                            font-weight: bold;
                            color: #3b82f6;
                            font-family: 'Poppins', sans-serif;
                            background: #f1f5f9;
                            border-radius: 20px;
                        }
                    """)
                    print("⚠️ Circle logo file corrupt, using text fallback")
            else:
                # Fallback to text if file doesn't exist
                self.org_logo_collapsed.setText("S")
                self.org_logo_collapsed.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #3b82f6;
                        font-family: 'Poppins', sans-serif;
                        background: #f1f5f9;
                        border-radius: 20px;
                    }
                """)
                print("⚠️ circel_logo.png not found, using text fallback")
                
        except Exception as e:
            print(f"Error loading collapsed logo: {e}")
            # Fallback to text
            self.org_logo_collapsed.setText("S")
            self.org_logo_collapsed.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #3b82f6;
                    font-family: 'Poppins', sans-serif;
                    background: #f1f5f9;
                    border-radius: 20px;
                }
            """)
        
    def _create_floating_toggle_button(self):
        """Create modern floating circular toggle button positioned 50% in/out of sidebar."""
        # Create floating toggle button as child of sidebar itself
        self.floating_toggle = QPushButton(self)
        self.floating_toggle.setObjectName("floatingToggle")
        self.floating_toggle.setFixedSize(36, 36)  # Circular button
        
        # Set initial icon (right arrow for expanded state)
        self.floating_toggle.setText("›")  # Right arrow
        
        # Position button at center-right of sidebar (50% in, 50% out)
        self._position_toggle_button()
        
        # Modern circular styling with proper overflow handling
        self.floating_toggle.setStyleSheet("""
            QPushButton#floatingToggle {
                background: #3b82f6;
                border: 2px solid white;
                border-radius: 18px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                position: absolute;
                z-index: 1000;
            }
            QPushButton#floatingToggle:hover {
                background: #2563eb;
                transform: scale(1.05);
            }
            QPushButton#floatingToggle:pressed {
                background: #1d4ed8;
                transform: scale(0.95);
            }
        """)
        
        # Connect to toggle function
        self.floating_toggle.clicked.connect(self._toggle_sidebar)
        
        # Make sure button is visible and on top
        self.floating_toggle.show()
        self.floating_toggle.raise_()
        
    def _position_toggle_button(self):
        """Position the floating toggle button at the top-right of sidebar with 50% visible outside."""
        if hasattr(self, 'floating_toggle') and self.floating_toggle:
            # Get sidebar dimensions
            sidebar_width = self.width()
            
            # Calculate position: top area, right edge (50% outside sidebar)
            button_x = sidebar_width - (self.floating_toggle.width() // 2)  # 50% outside
            button_y = 25  # Very close to top since logo is now at top
            
            # Position the button relative to sidebar
            self.floating_toggle.move(button_x, button_y)
    
    def _update_toggle_button_icon(self, is_expanded):
        """Update toggle button icon based on sidebar state."""
        if hasattr(self, 'floating_toggle') and self.floating_toggle:
            if is_expanded:
                self.floating_toggle.setText("‹")  # Left arrow for collapse
            else:
                self.floating_toggle.setText("›")  # Right arrow for expand
        
    def _create_navigation(self, parent_layout):
        """Create navigation buttons with improved alignment and spacing."""
        nav_container = QFrame()
        nav_container.setObjectName("navContainer")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 12, 12, 12)  # Add proper margins for visibility
        nav_layout.setSpacing(8)  # Equal spacing between all nav items
        
        # Navigation items with Material Design icons
        nav_items = [
            (MaterialIcons.get_icon_text(MaterialIcons.DASHBOARD), "Dashboard"),
            (MaterialIcons.get_icon_text(MaterialIcons.PEOPLE), "Students"),
            (MaterialIcons.get_icon_text(MaterialIcons.ASSIGNMENT), "Student List"),
            (MaterialIcons.get_icon_text(MaterialIcons.PERSON), "Mother Reg."),
            (MaterialIcons.get_icon_text(MaterialIcons.EVENT_NOTE), "Attendance"),
            (MaterialIcons.get_icon_text(MaterialIcons.ANALYTICS), "Reports"),
            (MaterialIcons.get_icon_text(MaterialIcons.SETTINGS), "Settings")
        ]
        
        self.nav_buttons = []
        
        for i, (icon, title) in enumerate(nav_items):
            btn_container = QPushButton()
            btn_container.setObjectName("navButton")
            btn_container.clicked.connect(lambda checked, idx=i: self._on_nav_clicked(idx))
            btn_container.setMinimumHeight(44)  # Fixed height for consistent spacing
            
            # Button layout with improved alignment
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(16, 10, 16, 10)  # Better padding
            btn_layout.setSpacing(14)  # Consistent spacing between icon and text
            
            # Icon with Material Design styling
            icon_label = QLabel(icon)
            icon_label.setObjectName("sidebarNavIcon")
            icon_label.setFixedSize(20, 20)  # Consistent icon size
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("""
                QLabel {
                    font-family: 'Segoe UI Symbol', 'Material Icons', sans-serif;
                    font-size: 16px;
                }
            """)
            btn_layout.addWidget(icon_label)
            
            # Text label
            text_label = QLabel(title)
            text_label.setObjectName("sidebarNavText")
            text_label.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    font-weight: 500;
                    font-family: 'Poppins', 'Segoe UI', Arial, sans-serif;
                }
            """)
            btn_layout.addWidget(text_label)
            btn_layout.addStretch()
            
            # Store button components for font enforcement
            btn_container.icon_label = icon_label
            btn_container.text_label = text_label
            self.nav_buttons.append(btn_container)
            nav_layout.addWidget(btn_container)
        
        # Set first button as active
        self.nav_buttons[0].setProperty("active", True)
        
        parent_layout.addWidget(nav_container)
        
    def _create_footer(self, parent_layout):
        """Create footer with logout and theme toggle - improved alignment."""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(12, 12, 12, 12)  # Add proper margins for visibility
        footer_layout.setSpacing(8)  # Equal spacing between footer items
        
        # Logout button with same styling as navigation buttons
        logout_btn = QPushButton()
        logout_btn.setObjectName("navButton")  # Same class as nav buttons
        logout_btn.clicked.connect(self._on_logout_clicked)
        logout_btn.setMinimumHeight(44)  # Same height as nav buttons
        
        logout_layout = QHBoxLayout(logout_btn)
        logout_layout.setContentsMargins(16, 10, 16, 10)  # Same padding as nav buttons
        logout_layout.setSpacing(14)  # Same spacing as nav buttons
        
        logout_icon = QLabel(MaterialIcons.get_icon_text(MaterialIcons.LOGOUT))
        logout_icon.setObjectName("sidebarNavIcon")  # Same class as nav icons
        logout_icon.setFixedSize(20, 20)  # Same size as nav icons
        logout_icon.setAlignment(Qt.AlignCenter)
        logout_icon.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI Symbol', 'Material Icons', sans-serif;
                font-size: 16px;
            }
        """)
        logout_layout.addWidget(logout_icon)
        
        self.logout_text = QLabel("Logout")
        self.logout_text.setObjectName("sidebarNavTitle")  # Same class as nav titles
        self.logout_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)  # Vertical center alignment
        logout_layout.addWidget(self.logout_text)
        logout_layout.addStretch()
        
        # Store references for styling
        logout_btn.icon_label = logout_icon
        logout_btn.title_label = self.logout_text
        
        footer_layout.addWidget(logout_btn)
        
        # Theme toggle with same styling as navigation buttons  
        theme_container = QPushButton()  # Changed from QFrame to QPushButton
        theme_container.setObjectName("navButton")  # Same class as nav buttons
        theme_container.clicked.connect(self._toggle_theme)  # Use clicked instead of mousePressEvent
        theme_container.setMinimumHeight(44)  # Same height as other buttons
        
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(16, 10, 16, 10)  # Same padding as nav buttons
        theme_layout.setSpacing(14)  # Same spacing as nav buttons
        
        self.theme_icon = QLabel(MaterialIcons.get_icon_text(MaterialIcons.DARK_MODE))
        self.theme_icon.setObjectName("sidebarNavIcon")  # Same class as nav icons
        self.theme_icon.setFixedSize(20, 20)  # Same size as nav icons
        self.theme_icon.setAlignment(Qt.AlignCenter)
        self.theme_icon.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI Symbol', 'Material Icons', sans-serif;
                font-size: 16px;
            }
        """)
        theme_layout.addWidget(self.theme_icon)
        
        self.theme_label = QLabel("Dark Mode")
        self.theme_label.setObjectName("sidebarNavTitle")  # Same class as nav titles
        self.theme_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)  # Vertical center alignment
        theme_layout.addWidget(self.theme_label)
        theme_layout.addStretch()
        
        # Store references for styling (same as nav buttons)
        theme_container.icon_label = self.theme_icon
        theme_container.title_label = self.theme_label
        
        # Store container reference
        self.theme_container = theme_container
        
        footer_layout.addWidget(theme_container)
        
        # Add both footer buttons to nav_buttons list for consistent styling
        self.nav_buttons.append(logout_btn)
        self.nav_buttons.append(theme_container)
        
        parent_layout.addWidget(footer_frame)
        
    def _setup_animations(self):
        """Setup animations for sidebar toggle with improved settings."""
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)  # Slightly longer for smoother animation
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Also create animation for minimum width to prevent width conflicts
        self.min_width_animation = QPropertyAnimation(self, b"minimumWidth") 
        self.min_width_animation.setDuration(300)
        self.min_width_animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Create animation group for synchronized animations
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.animation)
        self.animation_group.addAnimation(self.min_width_animation)
        
    def _toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states."""
        # Set animation in progress flag to prevent font interference
        self.animation_in_progress = True
        
        # Stop any running animations first
        if self.animation_group.state() == QAbstractAnimation.Running:
            self.animation_group.stop()
            
        # Disconnect any previous animation callbacks
        try:
            self.animation_group.finished.disconnect()
        except TypeError:
            pass  # No connections to disconnect
            
        # Get current state more reliably
        current_width = self.width()
        is_currently_expanded = (current_width >= (self.expanded_width - 10))  # Allow small tolerance
        
        print(f"🔄 Toggle sidebar: current_width={current_width}, is_expanded={is_currently_expanded}")
        
        if is_currently_expanded:
            # Collapse: Hide text first for smoother animation
            self._hide_text_elements()
            
            # Toggle logos for collapsed state
            self.org_logo_expanded.hide()
            self.org_logo_collapsed.show()
            
            # Update floating toggle button icon
            self._update_toggle_button_icon(False)  # Will be collapsed
            
            # Set up both animations for collapse
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.min_width_animation.setStartValue(self.expanded_width)
            self.min_width_animation.setEndValue(self.collapsed_width)
            
            self.animation_group.finished.connect(self._on_collapse_finished)
        else:
            # Expand: Will show text after animation
            
            # Toggle logos for expanded state
            self.org_logo_collapsed.hide()
            self.org_logo_expanded.show()
            
            # Update floating toggle button icon
            self._update_toggle_button_icon(True)  # Will be expanded
            
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.min_width_animation.setStartValue(self.collapsed_width)
            self.min_width_animation.setEndValue(self.expanded_width)
            
            self.animation_group.finished.connect(self._on_expand_finished)
            
        # Start synchronized animations
        self.animation_group.start()
        
        # Force immediate update
        self.update()
        
    def _on_collapse_finished(self):
        """Handle collapse animation completion."""
        # Clear animation flag
        self.animation_in_progress = False
        
        # Ensure text elements are hidden
        self._hide_text_elements()
        
        # Set exact width to prevent auto-expansion
        self.setMaximumWidth(self.collapsed_width)
        self.setMinimumWidth(self.collapsed_width)
        
        # Update floating toggle button position
        self._position_toggle_button()
        
        # Force update and repaint
        self.update()
        self.repaint()
        
        print("✅ Sidebar collapsed successfully")
        
        # Disconnect this specific callback
        try:
            self.animation_group.finished.disconnect(self._on_collapse_finished)
        except TypeError:
            pass
            
    def _on_expand_finished(self):
        """Handle expand animation completion."""
        # Clear animation flag
        self.animation_in_progress = False
        
        # Set exact width first
        self.setMaximumWidth(self.expanded_width)
        self.setMinimumWidth(self.expanded_width)
        
        # Update floating toggle button position
        self._position_toggle_button()
        
        # Show text elements after ensuring width is set
        QTimer.singleShot(50, self._show_text_elements)
        
        # Apply consistent fonts after expand (reduced calls)
        QTimer.singleShot(100, self._apply_consistent_fonts)
        
        # Force update and repaint
        self.update()
        self.repaint()
        
        print("✅ Sidebar expanded successfully")
        
        # Disconnect this specific callback
        try:
            self.animation_group.finished.disconnect(self._on_expand_finished)
        except TypeError:
            pass
        
    def _hide_text_elements(self):
        """Hide text elements when collapsed."""
        self.logout_text.hide()
        self.theme_label.hide()
        
        for btn in self.nav_buttons:
            if hasattr(btn, 'title_label'):
                btn.title_label.hide()
                
        # Floating toggle button is always visible and positioned separately
                
    def _show_text_elements(self):
        """Show text elements when expanded."""
        self.logout_text.show()
        self.theme_label.show()
        
        for btn in self.nav_buttons:
            if hasattr(btn, 'title_label'):
                btn.title_label.show()
                
        # Floating toggle button is always visible and positioned separately
                
    def _on_nav_clicked(self, index):
        """Handle navigation button click with ultra-aggressive anti-flashing protection."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("selected", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # IMMEDIATE ULTRA-NUCLEAR FONT AND TEXT ALIGNMENT ENFORCEMENT
        print("🎯 Button clicked - applying ULTRA-NUCLEAR text alignment enforcement...")
        self._apply_consistent_fonts()  # Immediate enforcement
        self._force_layout_spacing()    # Immediate layout enforcement
        
        # ULTRA-AGGRESSIVE enforcement waves to prevent ANY text movement
        QTimer.singleShot(1, self._apply_consistent_fonts)    # 1ms
        QTimer.singleShot(1, self._force_layout_spacing)      # 1ms layout
        QTimer.singleShot(5, self._apply_consistent_fonts)    # 5ms
        QTimer.singleShot(5, self._force_layout_spacing)      # 5ms layout
        QTimer.singleShot(10, self._apply_consistent_fonts)   # 10ms
        QTimer.singleShot(10, self._force_layout_spacing)     # 10ms layout
        QTimer.singleShot(25, self._apply_consistent_fonts)   # 25ms
        QTimer.singleShot(25, self._force_layout_spacing)     # 25ms layout
        QTimer.singleShot(50, self._apply_consistent_fonts)   # 50ms
        QTimer.singleShot(50, self._force_layout_spacing)     # 50ms layout
        
        # Update current page
        self.current_page = index
        # Emit signal
        self.page_changed.emit(index)
        
    def _toggle_theme(self):
        """Toggle between light and dark theme while preserving exact default font sizing."""
        # Store current visibility state more reliably
        current_width = self.width()
        was_expanded = (current_width >= (self.expanded_width - 10))
        
        print(f"🎨 Theme toggle starting: {'Light→Dark' if not self.is_dark_mode else 'Dark→Light'}")
        
        self.is_dark_mode = not self.is_dark_mode
        
        # Update theme label and icon with Material Design icons
        if self.is_dark_mode:
            self.theme_icon.setText(MaterialIcons.get_icon_text(MaterialIcons.LIGHT_MODE))
            if hasattr(self, 'theme_label') and self.theme_label:
                self.theme_label.setText("Light Mode")
        else:
            self.theme_icon.setText(MaterialIcons.get_icon_text(MaterialIcons.DARK_MODE))
            if hasattr(self, 'theme_label') and self.theme_label:
                self.theme_label.setText("Dark Mode")
        
        # Apply new theme (this will apply the CSS)
        self._apply_theme()
        
        # NUCLEAR FONT ENFORCEMENT - Apply immediately and repeatedly
        print("🚀 NUCLEAR font enforcement for theme change...")
        self._apply_consistent_fonts()  # Immediate application
        self._force_layout_spacing()    # Force proper spacing and alignment
        
        # Ultra-aggressive font enforcement wave
        QTimer.singleShot(1, self._apply_consistent_fonts)    # 1ms
        QTimer.singleShot(5, self._apply_consistent_fonts)    # 5ms  
        QTimer.singleShot(10, self._apply_consistent_fonts)   # 10ms
        QTimer.singleShot(25, self._apply_consistent_fonts)   # 25ms
        QTimer.singleShot(50, self._apply_consistent_fonts)   # 50ms
        QTimer.singleShot(75, self._apply_consistent_fonts)   # 75ms
        QTimer.singleShot(100, self._apply_consistent_fonts)  # 100ms
        QTimer.singleShot(150, self._apply_consistent_fonts)  # 150ms
        QTimer.singleShot(200, self._apply_consistent_fonts)  # 200ms
        QTimer.singleShot(300, self._apply_consistent_fonts)  # 300ms
        
        # Force layout spacing at multiple intervals
        QTimer.singleShot(50, self._force_layout_spacing)
        QTimer.singleShot(100, self._force_layout_spacing)
        QTimer.singleShot(200, self._force_layout_spacing)
        
        # Restore proper visibility based on stored state
        if was_expanded:
            # Expanded state - show all elements
            QTimer.singleShot(50, self._show_text_elements)
        else:
            # Collapsed state - hide text but show icons
            QTimer.singleShot(50, self._hide_text_elements)
            
        # Multiple update calls to ensure changes stick
        self.update()
        QTimer.singleShot(50, self.update)
        QTimer.singleShot(100, self.update)
        
        print(f"🎨 Theme toggled to {'Dark' if self.is_dark_mode else 'Light'} mode")
        self.update()
        if was_expanded:
            # Expanded state - show all elements
            QTimer.singleShot(50, self._show_text_elements)
            QTimer.singleShot(200, self._show_text_elements)  # Backup
        else:
            # Collapsed state - hide text but show icons
            QTimer.singleShot(50, self._hide_text_elements)
            QTimer.singleShot(200, self._hide_text_elements)  # Backup
            
        # Force multiple updates with different methods
        self.update()
        self.repaint()
        QTimer.singleShot(100, self.update)
        QTimer.singleShot(200, self.repaint)
        QTimer.singleShot(300, self.update)
        
        # Emit theme change signal
        self.theme_changed.emit(self.is_dark_mode)
        
    def _apply_theme(self):
        """Apply the current theme to the sidebar without interfering with fonts."""
        # Set the main stylesheet from centralized file
        self.setStyleSheet(self._get_modern_style())
        
        # Simple update without aggressive font interference
        self.update()
        
        print(f"🎨 Theme applied: {'Dark' if self.is_dark_mode else 'Light'} mode")
        
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
            if hasattr(self, 'smis_title') and self.smis_title:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(18)
                font.setBold(True)
                font.setWeight(QFont.Bold)
                self.smis_title.setFont(font)
                # Force style override with !important-like behavior
                self.smis_title.setStyleSheet("font-size: 18px !important; font-weight: bold !important; color: inherit;")
                
            if hasattr(self, 'smis_subtitle') and self.smis_subtitle:
                font = QFont()
                font.setFamily("Segoe UI")
                font.setPointSize(12)
                font.setWeight(QFont.Normal)
                self.smis_subtitle.setFont(font)
                self.smis_subtitle.setStyleSheet("font-size: 12px !important; font-weight: normal !important; color: inherit;")
                
            # Navigation buttons - force consistent sizes with NUCLEAR approach
            for btn in self.nav_buttons:
                if hasattr(btn, 'title_label') and btn.title_label:
                    # NUCLEAR font force for title labels
                    font = QFont()
                    font.setFamily("Poppins")
                    font.setPointSize(14)
                    font.setBold(True)
                    font.setWeight(QFont.Bold)
                    btn.title_label.setFont(font)
                    # ULTRA !important style enforcement
                    btn.title_label.setStyleSheet("""
                        font-size: 14px !important; 
                        font-weight: 600 !important; 
                        font-family: 'Poppins', sans-serif !important;
                        color: inherit !important;
                        min-height: auto !important;
                        background-color: transparent !important;
                    """)
                    
                if hasattr(btn, 'icon_label') and btn.icon_label:
                    # NUCLEAR font force for icon labels
                    font = QFont()
                    font.setFamily("Poppins")
                    font.setPointSize(16)
                    font.setWeight(QFont.Normal)
                    btn.icon_label.setFont(font)
                    # ULTRA !important style enforcement
                    btn.icon_label.setStyleSheet("""
                        font-size: 16px !important; 
                        font-weight: normal !important; 
                        font-family: 'Poppins', sans-serif !important;
                        color: inherit !important;
                        min-height: auto !important;
                        background-color: transparent !important;
                    """)
                    
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
        """Get COMPLETELY ISOLATED modern stylesheet - IMMUNE to global styles."""
        
        # Determine colors based on theme
        if self.is_dark_mode:
            bg_color = "#1f2937"
            text_color = "#f9fafb"
            btn_color = "#374151"
            btn_hover = "#4b5563"
            btn_active = "#6b7280"
            border_color = "#374151"
        else:
            bg_color = "#ffffff"
            text_color = "#374151"
            btn_color = "#f3f4f6"
            btn_hover = "#e5e7eb"
            btn_active = "#d1d5db"
            border_color = "#e5e7eb"
        
        # NUCLEAR ISOLATION STYLESHEET
        return f"""
            /* COMPLETE ISOLATION - Override ALL possible global interference */
            QFrame#ModernSidebar {{
                background-color: {bg_color} !important;
                border: 1px solid {border_color} !important;
                border-radius: 8px !important;
                min-width: 60px !important;
                max-width: 300px !important;
            }}
            
            /* NUCLEAR PROTECTION for all sidebar labels */
            QFrame#ModernSidebar QLabel#sidebarNavTitle {{
                color: {text_color} !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 0px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            QFrame#ModernSidebar QLabel#sidebarNavIcon {{
                color: {text_color} !important;
                font-size: 16px !important;
                font-weight: normal !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 0px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            /* NUCLEAR PROTECTION for brand labels */
            QFrame#ModernSidebar QLabel#brandTitle {{
                color: {text_color} !important;
                font-size: 18px !important;
                font-weight: bold !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 8px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            QFrame#ModernSidebar QLabel#brandSubtitle {{
                color: {text_color} !important;
                font-size: 12px !important;
                font-weight: normal !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 4px 8px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            /* NUCLEAR PROTECTION for footer labels */
            QFrame#ModernSidebar QLabel#logoutText {{
                color: {text_color} !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 0px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            QFrame#ModernSidebar QLabel#themeLabel {{
                color: {text_color} !important;
                font-size: 13px !important;
                font-weight: normal !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                padding: 0px !important;
                margin: 0px !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
            }}
            
            /* Button styles */
            QFrame#ModernSidebar QPushButton#navButton {{
                background-color: {btn_color} !important;
                border: none !important;
                border-radius: 6px !important;
                margin: 2px !important;
                padding: 8px !important;
                text-align: left !important;
            }}
            
            QFrame#ModernSidebar QPushButton#navButton:hover {{
                background-color: {btn_hover} !important;
            }}
            
            QFrame#ModernSidebar QPushButton#navButton:pressed {{
                background-color: {btn_active} !important;
            }}
            
            /* OVERRIDE ANY POSSIBLE GLOBAL QLABEL RULES */
            QFrame#ModernSidebar QLabel {{
                color: {text_color} !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                font-family: 'Poppins', 'Segoe UI', 'Arial', sans-serif !important;
                min-height: auto !important;
                max-height: none !important;
                background-color: transparent !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px !important;
            }}
        """
    
    def resizeEvent(self, event):
        """Handle resize events to reposition floating toggle button."""
        super().resizeEvent(event)
        # Reposition toggle button when sidebar is resized
        QTimer.singleShot(10, self._position_toggle_button)
    
    def cleanup(self):
        """Clean up timers and resources to prevent conflicts."""
        try:
            if hasattr(self, 'nuclear_font_timer') and self.nuclear_font_timer:
                self.nuclear_font_timer.stop()
                self.nuclear_font_timer.deleteLater()
                self.nuclear_font_timer = None
                print("🧹 Sidebar font enforcement timer cleaned up")
        except Exception:
            pass  # Silent cleanup
            
    def __del__(self):
        """Ensure cleanup when sidebar is destroyed."""
        self.cleanup()

# For backward compatibility
CollapsibleSidebar = ModernSidebar
