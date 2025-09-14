"""
Calendar icon generator for the form.
This script creates a calendar icon PNG for use in the mother registration form.
"""
import os
import base64
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QSize

# Base64 encoded small calendar icon (material style)
CALENDAR_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA4klEQVRIie3UMUpDQRSF4Q8UO21EwcLOQrATXIBgYyFuwMbSHdgKLsBC0NJSULATdJqAIFiIYJNCFBRCCkHHQhAnyZvJE0FIceBlmP+ee+aeO8xwrjgp+QTXOMjJTZIvcZORmyZf4aHND/+ktWfkWnwvI/lbYxyiROdYjnOUOG3LP5thgBKX2AxzlNhryrdRTWioWrxVYScm32E9Jt9gNSZ/xFJMvsRzTF7iKSbvoxeTj/AQk49xF5MPcROTD3AZk/fRicm72I/JOziMyTvYjcm3k88k5uSY5zlwEXvK/7/KB/gCRWUzIsP56tsAAAAASUVORK5CYII=
"""

def create_calendar_icon():
    """Create a calendar icon and save it to disk."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "calendar_icon.png")
    
    # Decode base64 icon
    icon_data = QByteArray.fromBase64(CALENDAR_ICON_BASE64.strip().encode())
    pixmap = QPixmap()
    pixmap.loadFromData(icon_data)
    
    # Save to file
    if not pixmap.isNull():
        pixmap.save(icon_path)
        print(f"Calendar icon saved to {icon_path}")
    else:
        print("Failed to create calendar icon")

if __name__ == "__main__":
    create_calendar_icon()
