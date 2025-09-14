import os
from PyQt5.QtWidgets import QComboBox, QAbstractItemView
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter

# Define BORDER_RADIUS locally to avoid circular import
BORDER_RADIUS = "12px"

# Path to resources directory
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources")
EXPAND_ARROW_PATH = os.path.join(RESOURCES_PATH, "expand_arrow.png")

# Colors
TEXT_COLOR = "#333333"  # Normal text
BORDER_COLOR = "#cccccc"  # Input borders
PRIMARY_COLOR = "#0175b6"  # Selection, hover, focus blue

# Styles for ComboBox
COMBOBOX_STYLE = f"""
    QComboBox#CustomComboBox {{
        padding-right: 50px !important;
        color: {TEXT_COLOR} !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: {BORDER_RADIUS} !important;
        background-color: white !important;
        min-height: 32px !important;
        height: 32px !important;
        padding: 2px 10px !important;
        selection-background-color: {PRIMARY_COLOR} !important;
        selection-color: white !important;
    }}
    
    QComboBox#CustomComboBox::drop-down {{
        subcontrol-origin: padding !important;
        subcontrol-position: top right !important;
        width: 45px !important;
        border-left-width: 0px !important;
        border-top-right-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        background-color: transparent !important;
    }}
    
    QComboBox#CustomComboBox::drop-down:hover {{
        background-color: transparent !important;
    }}
    
    QComboBox#CustomComboBox::down-arrow {{
        width: 0px !important;
        height: 0px !important;
        border: none !important;
        image: none !important;
    }}
"""

# Styles for ComboBox Popup
COMBOBOX_POPUP_STYLE = f"""
    QAbstractItemView {{
        background-color: white;
        border: none !important;
        border-radius: 0px 12px;
        outline: none;
        alternate-background-color: transparent;
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
        padding: 0px !important;
        margin: 0px !important;
        color: {TEXT_COLOR};
        font-size: 16px;
    }}
    
    QAbstractItemView::item {{
        padding: 0px !important;
        margin: 0px !important;
        color: {TEXT_COLOR};
        background-color: transparent;
        border: none !important;
        min-height: 20px;
        width: 100%;
    }}
    
    QAbstractItemView::item:hover {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        padding: 0px !important;
        margin: 0px !important;
    }}
    
    QAbstractItemView::item:selected {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        padding: 0px !important;
        margin: 0px !important;
    }}
"""


class CustomComboBox(QComboBox):
    """Custom ComboBox with consistent dropdown and icon styling."""
    
    def __init__(self, parent=None):
        """Initialize the custom combobox."""
        super().__init__(parent)
        # Set object name to allow specific styling
        self.setObjectName("CustomComboBox")
        
        # Force the view to have no frame
        self.view().setFrameStyle(0)
        
        # Explicitly set selection behavior
        self.view().setSelectionMode(self.view().SingleSelection)
        self.view().setMouseTracking(True)
        
        # Set some fixed sizing to ensure consistent display
        self.setMinimumHeight(32)
        self.setFixedHeight(32)
        
        # Apply stronger style with !important flags to override global styles
        self.setStyleSheet(COMBOBOX_STYLE)
        
        # Use timer to ensure style is applied after all parent styles
        QTimer.singleShot(100, self.enforceStyle)
        # Add a second delayed enforcement for cases where other styles apply later
        QTimer.singleShot(500, self.enforceStyle)
    
    def showPopup(self):
        """Override to ensure dropdown appears directly below combobox with proper styling."""
        super().showPopup()
        
        # Get the popup view
        popup = self.view()
        if popup and popup.parent():
            # Position the popup slightly below the combobox (add 5px gap)
            global_pos = self.mapToGlobal(self.rect().bottomLeft())
            popup.parent().move(global_pos.x(), global_pos.y() + 5)
            
            # Set popup width to match combobox width
            combobox_width = self.width()
            popup_widget = popup.parent()
            popup_widget.setFixedWidth(combobox_width)
            popup_widget.resize(combobox_width, popup_widget.height())
            
            # Set the view width to match
            popup.setFixedWidth(combobox_width)
            popup.resize(combobox_width, popup.height())
            
            # Remove frame style and borders
            popup_widget.setWindowFlags(popup_widget.windowFlags() | Qt.FramelessWindowHint)
            popup_widget.setStyleSheet("""
                QWidget {
                    border: none !important;
                    background-color: white;
                    border-radius: 0px 0px 12px 12px;
                    padding: 0px !important;
                    margin: 0px !important;
                }
                QFrame {
                    border: none !important;
                    background-color: white;
                    padding: 0px !important;
                    margin: 0px !important;
                }
            """)
            
            # Remove frame from the view
            popup.setFrameStyle(0)
            popup.setFrameShape(popup.NoFrame)
            
            # Apply styling to the view
            popup.setStyleSheet(COMBOBOX_POPUP_STYLE)
            
    def enforceStyle(self):
        """Force the style to be applied again to overcome any style conflicts."""
        # Get the current object name to create a highly specific selector
        object_name = self.objectName() if self.objectName() else "CustomComboBox"
        
        # Create a more specific style with !important flags for this particular instance
        specific_style = f"""
            QComboBox#{object_name} {{
                padding-right: 50px !important;
                color: {TEXT_COLOR} !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                border: 1px solid {BORDER_COLOR} !important;
                border-radius: 6px !important;
                background-color: white !important;
                min-height: 32px !important;
                height: 32px !important;
                padding: 2px 10px !important;
                selection-background-color: {PRIMARY_COLOR} !important;
                selection-color: white !important;
                margin: 0 !important;
            }}
            
            QComboBox#{object_name}::drop-down {{
                subcontrol-origin: padding !important;
                subcontrol-position: top right !important;
                width: 45px !important;
                border-left-width: 0px !important;
                border-top-right-radius: 12px !important;
                border-bottom-right-radius: 12px !important;
                background-color: transparent !important;
            }}
            
            QComboBox#{object_name}::drop-down:hover {{
                background-color: transparent !important;
            }}
            
            QComboBox#{object_name}::down-arrow {{
                width: 0px !important;
                height: 0px !important;
                border: none !important;
                image: none !important;
            }}
        """
        
        # Apply the specific style with higher priority
        self.setStyleSheet(specific_style)
        
    def paintEvent(self, event):
        """Custom paint to draw dropdown icon."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Try to load and draw PNG icon first
        icon_loaded = False
        
        if os.path.exists(EXPAND_ARROW_PATH):
            pixmap = QPixmap(EXPAND_ARROW_PATH)
            if not pixmap.isNull():
                # Draw icon centered in dropdown area
                rect = self.rect()
                icon_size = 18
                dropdown_width = 45
                dropdown_x = rect.width() - dropdown_width
                
                # Center the icon
                icon_x = dropdown_x + (dropdown_width - icon_size) // 2
                icon_y = (rect.height() - icon_size) // 2
                
                # Scale pixmap to desired size
                scaled_pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(icon_x, icon_y, scaled_pixmap)
                icon_loaded = True
        
        # Fallback to triangle if PNG fails
        if not icon_loaded:
            self._draw_triangle(painter)
    
    def _draw_triangle(self, painter):
        """Draw triangle fallback if icon not available."""
        from PyQt5.QtCore import QPointF
        from PyQt5.QtGui import QPen, QBrush
        
        rect = self.rect()
        dropdown_width = 45
        dropdown_x = rect.width() - dropdown_width
        
        # Center the triangle
        arrow_x = dropdown_x + dropdown_width // 2 - 4
        arrow_y = rect.height() // 2
        
        # Create triangle points
        points = [
            QPointF(arrow_x, arrow_y - 5),
            QPointF(arrow_x + 10, arrow_y - 5),
            QPointF(arrow_x + 5, arrow_y + 5)
        ]
        
        painter.setPen(QPen(Qt.gray, 1))
        painter.setBrush(QBrush(Qt.gray))
        painter.drawPolygon(points)
