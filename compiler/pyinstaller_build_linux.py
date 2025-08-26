#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

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

def create_linux_desktop_file(app_name, exec_path, icon_path, comment, version):
    """Create a .desktop file for Linux"""
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment={comment}
Exec={exec_path} %f
Icon={icon_path}
Terminal=false
Categories=Utility;Development;
Version={version}
"""
    return desktop_content

def create_spec_file(version_str, display_version):
    """Create PyInstaller spec file for Linux"""
    # Ensure version has 4 elements
    version_parts = list(map(int, version_str.split('.')))
    while len(version_parts) < 4:
        version_parts.append(0)
    version_tuple = tuple(version_parts)
    
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
        ('assets/logo.png', '.'),  # Include logo for .desktop file
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

# Add any additional binaries
# a.binaries = a.binaries + [('libnfc.so', '/usr/lib/x86_64-linux-gnu/libnfc.so', 'BINARY')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nfc-reader-writer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
)
"""
    return spec_content

def main():
    # Get version information
    version_str, display_version = get_version()
    app_name = "NFC Reader/Writer"
    
    print(f"Building {app_name} v{display_version} for Linux...")
    
    # Create a temporary directory for build files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Create spec file
        spec_content = create_spec_file(version_str, display_version)
        spec_path = os.path.join(temp_dir, 'nfc_reader_writer.spec')
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        # Run PyInstaller
        print("Running PyInstaller...")
        subprocess.check_call([
            'pyinstaller',
            '--clean',
            '--noconfirm',
            '--distpath', 'dist/linux',
            '--workpath', os.path.join(temp_dir, 'build'),
            '--specpath', temp_dir,
            spec_path
        ])
        
        # Create .desktop file
        print("Creating .desktop file...")
        app_dir = 'dist/linux/nfc-reader-writer'
        desktop_content = create_linux_desktop_file(
            app_name=app_name,
            exec_path=os.path.join(app_dir, 'nfc-reader-writer'),
            icon_path=os.path.join(app_dir, 'logo.png'),
            comment="NFC Tag Reader/Writer Application",
            version=version_str
        )
        
        # Create necessary directories
        os.makedirs('dist/linux/usr/share/applications', exist_ok=True)
        os.makedirs('dist/linux/usr/share/icons/hicolor/256x256/apps', exist_ok=True)
        
        # Write .desktop file
        with open('dist/linux/usr/share/applications/nfc-reader-writer.desktop', 'w') as f:
            f.write(desktop_content)
        
        # Copy icon
        if os.path.exists('assets/logo.png'):
            shutil.copy2('assets/logo.png', 'dist/linux/usr/share/icons/hicolor/256x256/apps/nfc-reader-writer.png')
        
        # Make the binary executable
        binary_path = os.path.join(app_dir, 'nfc-reader-writer')
        if os.path.exists(binary_path):
            st = os.stat(binary_path)
            os.chmod(binary_path, st.st_mode | stat.S_IEXEC)
        
        print("Build completed successfully!")
        print(f"Application is available in: {os.path.abspath(app_dir)}")
        print("To create a distributable package, you can use the following command:")
        print("  tar -czvf nfc-reader-writer-linux-x86_64.tar.gz -C dist/linux .")

if __name__ == "__main__":
    main()
