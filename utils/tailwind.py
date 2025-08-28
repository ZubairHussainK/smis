"""Tailwind-like utility classes for PyQt5 with standardized spacing."""

class Utilities:
    # Colors
    COLORS = {
        'primary': '#1089D3',
        'secondary': '#12B1D1',
        'success': '#4CAF50',
        'danger': '#F44336',
        'warning': '#FFC107',
        'info': '#2196F3',
        'light': '#F5F5F5',
        'dark': '#444444',
        'white': '#FFFFFF',
        'transparent': 'transparent'
    }

    # Standardized Spacing System (matches global styles)
    SPACING = {
        '0': '0',
        'xs': '4px',    # Extra small - for tight elements
        'sm': '8px',    # Small - default component spacing  
        'md': '12px',   # Medium - section spacing
        'lg': '16px',   # Large - page margins
        'xl': '20px',   # Extra large - major sections
        'xxl': '24px',  # Extra extra large - page padding
        # Legacy support
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px'
    }

    # Border radius
    ROUNDED = {
        'none': '0',
        'sm': '2px',
        'md': '4px',
        'lg': '8px',
        'xl': '12px',
        '2xl': '16px',
        'full': '9999px'
    }

    # Font sizes - Following a standardized scale
    TEXT = {
        'xs': '10px',       # Extra small text, footnotes
        'sm': '12px',       # Small text, secondary info
        'base': '14px',     # Base text size
        'lg': '16px',       # Slightly larger text
        'xl': '20px',       # Sub headings
        '2xl': '24px',      # Section headings
        '3xl': '32px',      # Main headings
        '4xl': '40px'       # Hero text
    }

    # Font weights mapped to Poppins font weights
    FONT_WEIGHT = {
        'normal': '400',    # Poppins Regular
        'medium': '500',    # Poppins Medium
        'semibold': '600',  # Poppins SemiBold
        'bold': '700'       # Poppins Bold
    }

    # Font families
    FONT = {
        'primary': 'Poppins',
        'fallback': 'system-ui, -apple-system, sans-serif'
    }

    @classmethod
    def bg(cls, color):
        """Background color utility."""
        return f'background-color: {cls.COLORS.get(color, color)};'

    @classmethod
    def text(cls, color):
        """Text color utility."""
        return f'color: {cls.COLORS.get(color, color)};'

    @classmethod
    def p(cls, size):
        """Padding utility."""
        return f'padding: {cls.SPACING.get(str(size), str(size)+"px")};'

    @classmethod
    def px(cls, size):
        """Horizontal padding utility."""
        spacing = cls.SPACING.get(str(size), str(size)+"px")
        return f'padding-left: {spacing}; padding-right: {spacing};'

    @classmethod
    def py(cls, size):
        """Vertical padding utility."""
        spacing = cls.SPACING.get(str(size), str(size)+"px")
        return f'padding-top: {spacing}; padding-bottom: {spacing};'

    @classmethod
    def m(cls, size):
        """Margin utility."""
        return f'margin: {cls.SPACING.get(str(size), str(size)+"px")};'

    @classmethod
    def rounded(cls, size='md'):
        """Border radius utility."""
        return f'border-radius: {cls.ROUNDED.get(size, size)};'

    @classmethod
    def font(cls, size='base'):
        """Font size utility."""
        return f'font-size: {cls.TEXT.get(size, size)};'

    @classmethod
    def font_weight(cls, weight='normal'):
        """Font weight utility."""
        return f'font-weight: {cls.FONT_WEIGHT.get(weight, weight)};'

    @classmethod
    def shadow(cls, size='md'):
        """Box shadow utility."""
        shadows = {
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            'none': 'none'
        }
        return f'box-shadow: {shadows.get(size, size)};'

    @classmethod
    def button(cls, variant='primary'):
        """Button style utility with standardized heights and spacing."""
        styles = {
            'primary': f'''
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: {cls.SPACING['sm']} {cls.SPACING['lg']};
                margin: {cls.SPACING['xs']};
                font-weight: 600;
                font-size: 14px;
                font-family: "Poppins SemiBold";
                min-height: 38px;
                max-height: 38px;
            ''',
            'secondary': f'''
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                font-family: "Poppins SemiBold";
                min-height: 38px;
                max-height: 38px;
            ''',
            'outline': f'''
                background-color: transparent;
                color: #3B82F6;
                border: 2px solid #3B82F6;
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 500;
                font-size: 14px;
                font-family: "Poppins Medium";
                min-height: 38px;
                max-height: 38px;
            ''',
            'success': f'''
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                font-family: "Poppins SemiBold";
                min-height: 38px;
                max-height: 38px;
            ''',
            'warning': f'''
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                font-family: "Poppins SemiBold";
                min-height: 38px;
                max-height: 38px;
            '''
        }
        return styles.get(variant, styles['primary'])

    @classmethod
    def input(cls, variant='default'):
        """Input style utility with standardized heights and spacing."""
        styles = {
            'default': f'''
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: {cls.SPACING['sm']} {cls.SPACING['lg']};
                margin: {cls.SPACING['xs']};
                background-color: white;
                color: #2C3E50;
                font-size: 14px;
                font-family: "Poppins";
                min-height: 38px;
                max-height: 38px;
            ''',
            'focused': f'''
                border: 1px solid #3B82F6;
                border-radius: 8px;
                padding: {cls.SPACING['sm']} {cls.SPACING['lg']};
                margin: {cls.SPACING['xs']};
                background-color: #FEFEFE;
                color: #2C3E50;
                font-size: 14px;
                font-family: "Poppins";
                min-height: 38px;
                max-height: 38px;
                outline: none;
            '''
        }
        return styles.get(variant, styles['default'])

# Helper functions for common spacing operations
def get_standard_spacing():
    """Get standard component spacing value."""
    return Utilities.SPACING['sm']

def get_section_spacing():
    """Get section-level spacing value."""
    return Utilities.SPACING['lg']

def get_page_spacing():
    """Get page-level spacing value."""
    return Utilities.SPACING['xxl']

def get_component_margin():
    """Get standard component margin value."""
    return Utilities.SPACING['xs']

# Example usage:
def style(widget, *classes):
    """Apply Tailwind-like utility classes to a widget."""
    styles = []
    for cls in classes:
        if isinstance(cls, str):
            styles.append(cls)
    widget.setStyleSheet(' '.join(styles))
