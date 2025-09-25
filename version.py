"""Version information for SMIS application."""

__version__ = "2.2.3"
__app_name__ = "School Management Information System"
__build_date__ = "2025-09-25"
__author__ = "SMIS Development Team"

# Version display formats
VERSION_SHORT = __version__
VERSION_FULL = f"{__app_name__} v{__version__}"
VERSION_WITH_BUILD = f"{__app_name__} v{__version__} ({__build_date__})"

def get_version_info():
    """Get complete version information."""
    return {
        'version': __version__,
        'app_name': __app_name__,
        'build_date': __build_date__,
        'author': __author__,
        'version_short': VERSION_SHORT,
        'version_full': VERSION_FULL,
        'version_with_build': VERSION_WITH_BUILD
    }