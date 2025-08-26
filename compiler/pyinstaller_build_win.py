import os
import sys
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

def convert_png_to_ico(png_path, ico_path):
    """Convert a PNG file to ICO format using Wand."""
    try:
        from wand.image import Image as WandImage
        with WandImage(filename=png_path) as img:
            img.format = 'ico'
            img.save(filename=ico_path)
        return True
    except ImportError:
        print("Wand is required for PNG to ICO conversion. Please install it with: pip install wand")
        return False
    except Exception as e:
        print(f"Error converting {png_path} to ICO: {e}")
        return False

def get_version():
    """Get version information from script/version.py"""
    try:
        sys.path.insert(0, 'script')
        from version import VERSION, VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, PRERELEASE, BUILD
        
        version_str = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
        if PRERELEASE:
            version_str += f"-{PRERELEASE}"
        if BUILD:
            version_str += f"+{BUILD}"
            
        display_version = VERSION
        return version_str, display_version
    except Exception as e:
        print(f"Warning: Could not read version: {e}")
        return "1.0.0", "1.0.0"

def create_spec_file(version_str, display_version, icon_path='NONE'):
    """Create PyInstaller spec file"""
    # Ensure version has 4 elements
    version_parts = list(map(int, version_str.split('.')))
    while len(version_parts) < 4:
        version_parts.append(0)
    version_tuple = tuple(version_parts)
    
    # Prepare the icon line for the spec file
    if icon_path != 'NONE' and os.path.exists(icon_path):
        # Convert path to Windows format and escape backslashes
        icon_path_win = os.path.normpath(icon_path).replace('\\', '\\\\')
        icon_line = f'icon=r"{icon_path_win}",'
    else:
        icon_line = "# icon=None  # No icon specified"
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('config/*.json', 'config'),
        ('data/*', 'data'),
        ('script/*.py', 'script'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'nfc',
        'nfc.clf',
        'nfc.tag',
        'nfc.tag.tt3',
        'nfc.tag.tt4',
        'nfc.tag.tt4_sony',
        'nfc.tag.tt4_type4',
        'nfc.tag.tt4_typetopaz',
        'nfc.tag.tt2',
        'nfc.tag.tt1',
        'nfc.tag.tt1_ttag',
        'nfc.tag.tt1_topaz',
        'nfc.tag.tt1_innovision',
        'nfc.tag.tt1_jewel',
        'script.logging_utils',
        'script.device_panel',
        'script.emulation_dialog',
        'script.encoding_utils',
    ],
    hookspy=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NFC_Reader_App-{version_str}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['python3.dll'],
    runtime_tmpdir=None,
    console=True,  # Set to True to see console output for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    version='version.txt',
    uac_admin=True,  # May be needed for USB access
)
"""
    # Create version file for Windows
    version_info = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'Nsfr750'),
           StringStruct('FileDescription', 'NFC Reader/Writer Application'),
           StringStruct('FileVersion', '{version_str}'),
           StringStruct('InternalName', 'NFC_Reader_App'),
           StringStruct('LegalCopyright', ' 2025 Nsfr750 - GPLv3 License'),
           StringStruct('OriginalFilename', 'NFC_Reader_App-{version_str}.exe'),
           StringStruct('ProductName', 'NFC Reader/Writer'),
           StringStruct('ProductVersion', '{display_version}')])
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""".format(version_tuple=version_tuple, 
             version_str=version_str, 
             display_version=display_version)

    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    with open('nfc_reader.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

def main():
    print("Building NFC Reader/Writer with PyInstaller...")
    
    def remove_readonly(func, path, _):
        """Remove readonly attribute and retry the operation"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Clean previous builds
    build_dir = 'build'
    dist_dir = 'dist/windows'
    
    def remove_readonly_files(func, path, _):
        """Remove readonly attribute and retry the operation"""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"Warning: Could not remove {path}: {e}")
    
    # Clean build directory
    if os.path.exists(build_dir):
        print("Cleaning build directory...")
        shutil.rmtree(build_dir, onerror=remove_readonly_files, ignore_errors=True)
    
    # Clean dist directory
    if os.path.exists(dist_dir):
        print("Cleaning dist directory...")
        # Try to remove the directory and all its contents
        try:
            shutil.rmtree(dist_dir, onerror=remove_readonly_files, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not fully clean dist directory: {e}")
            # If we can't remove the directory, at least try to clean its contents
            for item in os.listdir(dist_dir):
                item_path = os.path.join(dist_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.chmod(item_path, stat.S_IWRITE)
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, onerror=remove_readonly_files, ignore_errors=True)
                except Exception as e:
                    print(f"Warning: Could not remove {item_path}: {e}")
    
    # Get version information
    version_str, display_version = get_version()
    print(f"Building version: {display_version} (using build version: {version_str})")
    
    # Handle icon - copy to a known location first
    icon_path = 'NONE'
    temp_icon = None
    
    if os.path.exists('assets/logo.png'):
        try:
            # Create a temporary directory in the build folder
            temp_dir = os.path.join('build', 'temp_icon')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Define the ICO file path
            temp_icon = os.path.abspath(os.path.join(temp_dir, 'app_icon.ico'))
            
            # Convert PNG to ICO
            if convert_png_to_ico('assets/logo.png', temp_icon):
                icon_path = temp_icon
                print(f"Using icon: {icon_path}")
            else:
                print("Warning: Could not convert PNG to ICO, proceeding without icon")
        except Exception as e:
            print(f"Warning: Error processing icon: {e}")
    
    # Create spec file
    print("Creating PyInstaller spec file...")
    create_spec_file(version_str, display_version, icon_path=icon_path)
    
    # Don't clean up the icon file yet - it's needed during the build
    # The file will be cleaned up on the next build
    
    # Run PyInstaller
    print("Running PyInstaller...")
    try:
        subprocess.check_call(['pyinstaller', '--clean', 'nfc_reader.spec'])
        
        # Copy additional files to the dist directory
        dist_dir = Path('dist') / f'NFC_Reader_App-{version_str}'
        
        # Create necessary directories
        (dist_dir / 'logs').mkdir(exist_ok=True)
        (dist_dir / 'data').mkdir(exist_ok=True)
        
        # Copy README and LICENSE
        for file in ['README.md', 'LICENSE', 'CHANGELOG.md']:
            if os.path.exists(file):
                shutil.copy2(file, dist_dir)
                
        print("\nBuild completed successfully!")
        print(f"The application is available in: {os.path.abspath(dist_dir)}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during PyInstaller execution: {e}")
        sys.exit(1)
        
        # Clean up temporary files
        if os.path.exists('version.txt'):
            os.remove('version.txt')
        if os.path.exists('nfc_reader.spec'):
            os.remove('nfc_reader.spec')
            
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
