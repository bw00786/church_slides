"""
Cross-platform path utilities for Windows, Mac, and Linux compatibility
"""

import os
import sys

def get_project_root():
    """Get the project root directory (where the script is run from)"""
    return os.getcwd()

def get_font_path():
    """Get system font path based on operating system"""
    system = sys.platform
    
    font_paths = []
    
    if system == 'darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Helvetica.ttc',
        ]
    elif system == 'win32':  # Windows
        font_paths = [
            'C:\\Windows\\Fonts\\arial.ttf',
            'C:\\Windows\\Fonts\\Arial.ttf',
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf'),
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
        ]
    
    # Find first existing font
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    return None

def normalize_path(path):
    """
    Normalize path separators for current OS
    Converts forward slashes and backslashes to OS-appropriate separator
    """
    return os.path.normpath(path)

def join_paths(*parts):
    """
    Join path parts using OS-appropriate separator
    """
    return os.path.join(*parts)

def ensure_directory(path):
    """
    Create directory if it doesn't exist
    Works on all platforms
    """
    os.makedirs(path, exist_ok=True)

def get_system_info():
    """Get information about the current system"""
    return {
        'platform': sys.platform,
        'os_name': os.name,
        'separator': os.sep,
        'is_windows': sys.platform == 'win32',
        'is_mac': sys.platform == 'darwin',
        'is_linux': sys.platform.startswith('linux')
    }

# Common directories
def get_backgrounds_dir():
    return join_paths(get_project_root(), 'backgrounds')

def get_logos_dir():
    return join_paths(get_project_root(), 'logos')

def get_audio_dir():
    return join_paths(get_project_root(), 'audio')

def get_output_dir():
    return join_paths(get_project_root(), 'output')

def get_service_orders_dir():
    return join_paths(get_project_root(), 'service_orders')

if __name__ == "__main__":
    # Test the utilities
    info = get_system_info()
    print("System Information:")
    print(f"  Platform: {info['platform']}")
    print(f"  OS Name: {info['os_name']}")
    print(f"  Path Separator: {info['separator']}")
    print(f"  Windows: {info['is_windows']}")
    print(f"  Mac: {info['is_mac']}")
    print(f"  Linux: {info['is_linux']}")
    print(f"\nFont Path: {get_font_path()}")
    print(f"Project Root: {get_project_root()}")
    print(f"Backgrounds: {get_backgrounds_dir()}")
