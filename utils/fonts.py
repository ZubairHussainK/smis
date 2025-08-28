"""Font configurations and utilities."""
from PyQt5.QtGui import QFontDatabase, QFont
import os

def setup_fonts():
    """Load and setup Poppins fonts."""
    font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'fonts')
    font_files = {
        'Regular': 'Poppins-Regular.ttf',
        'Medium': 'Poppins-Medium.ttf',
        'SemiBold': 'Poppins-SemiBold.ttf',
        'Bold': 'Poppins-Bold.ttf'
    }
    
    for style, file in font_files.items():
        font_path = os.path.join(font_dir, file)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id < 0:
                print(f"Failed to load font: {file}")

def get_font(size=12, weight='Regular'):
    """Get Poppins font with specified size and weight."""
    font = QFont('Poppins', size)
    if weight == 'Medium':
        font.setWeight(QFont.Medium)
    elif weight == 'SemiBold':
        font.setWeight(QFont.DemiBold)
    elif weight == 'Bold':
        font.setWeight(QFont.Bold)
    return font

# Font size constants
FONT_SIZES = {
    'h1': 24,      # Main title
    'h2': 20,      # Section titles
    'h3': 16,      # Sub-section titles
    'base': 14,    # Regular text
    'sm': 12,      # Small text
    'xs': 10       # Extra small text
}
