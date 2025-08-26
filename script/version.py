"""Version information for NFC Reader/Writer application.

This module follows Semantic Versioning 2.0.0 (https://semver.org/).
"""

#: Major version number (incompatible API changes)
MAJOR = 1

#: Minor version number (backwards-compatible new features)
MINOR = 1

#: Patch version number (backwards-compatible bug fixes)
PATCH = 0

#: Pre-release version identifier (e.g., 'alpha', 'beta', 'rc.1')
#: Set to None for final releases
PRERELEASE = None

#: Build metadata (e.g., 'build.1', 'exp.sha.5114f85')
#: Set to None for releases
BUILD = None

# Version as a tuple (for comparisons)
VERSION = (MAJOR, MINOR, PATCH, PRERELEASE, BUILD)

# Version as a string
def get_version_string():
    """Get the full version as a string.
    
    Returns:
        str: Version string in the format 'MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]'
    """
    version = f"{MAJOR}.{MINOR}.{PATCH}"
    
    if PRERELEASE is not None:
        version += f"-{PRERELEASE}"
    
    if BUILD is not None:
        version += f"+{BUILD}"
    
    return version

# Version string
__version__ = get_version_string()

# Version info tuple (for backward compatibility)
version_info = (MAJOR, MINOR, PATCH, PRERELEASE, BUILD)

# Package metadata
APP_NAME = "NFC Reader/Writer"
APP_DESCRIPTION = "A cross-platform NFC tag reader/writer application"
AUTHOR = "Nsfr750"
LICENSE = "GPLv3"

# Backward compatibility
__title__ = APP_NAME
__description__ = APP_DESCRIPTION
__author__ = AUTHOR
__email__ = "nsfr750@yandex.com"
__license__ = LICENSE
__copyright__ = f"© 2025 {AUTHOR}"

if __name__ == "__main__":
    print(f"{__title__} v{__version__}")
    print(f"{__copyright__} - {__license__}")
