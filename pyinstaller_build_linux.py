#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import stat
import subprocess
import tempfile
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/build_linux.log')
    ]
)
logger = logging.getLogger(__name__)

def get_version():
    """Get version information from script/version.py"""
    try:
        # Add script directory to path
        script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'script')
        sys.path.insert(0, script_dir)
        
        # Import version information
        from version import MAJOR, MINOR, PATCH, PRERELEASE, BUILD, get_version_string
        
        version_str = f"{MAJOR}.{MINOR}.{PATCH}"
        if PRERELEASE:
            version_str += f"-{PRERELEASE}"
        if BUILD:
            version_str += f"+{BUILD}"
            
        display_version = get_version_string()
        logger.info(f"Building version: {version_str} (using build version: {display_version})")
        return version_str, display_version
    except Exception as e:
        logger.error(f"Error reading version: {e}", exc_info=True)
        return "1.0.1", "1.0.1"

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
    start_time = time.time()
    logger.info("Starting NFC Reader/Writer Linux build process...")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    def remove_readonly(func, path, _):
        """Remove readonly attribute and retry the operation"""
        try:
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            
            # If it's a directory, make all files writable
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass
            
            # Try the operation again
            func(path)
            return
        except Exception as e:
            logger.warning(f"Could not remove {path}: {e}")
            
            # If it's a file, try to truncate it
            if os.path.isfile(path):
                try:
                    with open(path, 'w') as f:
                        f.truncate(0)
                    return
                except Exception as e:
                    logger.warning(f"Could not truncate {path}: {e}")
            
            logger.warning(f"Could not remove {path}, it may be locked by another process")

    # Clean previous builds
    build_dir = os.path.join(project_root, 'build')
    dist_dir = os.path.join(project_root, 'dist', 'linux')
    
    # Clean build and dist directories
    for directory in [build_dir, dist_dir]:
        if os.path.exists(directory):
            logger.info(f"Cleaning {directory} directory...")
            shutil.rmtree(directory, onerror=remove_readonly, ignore_errors=True)
    
    # Create dist directory if it doesn't exist
    os.makedirs(dist_dir, exist_ok=True)
    
    # Get version information
    version_str, display_version = get_version()
    app_name = "NFC Reader/Writer"
    
    # Create a temporary directory for build files
    temp_dir = tempfile.mkdtemp(prefix='nfc_linux_build_')
    try:
        logger.info(f"Using temporary directory: {temp_dir}")
        
        # Copy necessary files to temp directory
        for item in ['main.py', 'assets', 'config', 'data', 'script']:
            src = os.path.join(project_root, item)
            if os.path.exists(src):
                logger.info(f"Copying {src} to temporary directory...")
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(temp_dir, item), dirs_exist_ok=True)
                else:
                    shutil.copy2(src, temp_dir)
        
        # Change to temp directory for build
        os.chdir(temp_dir)
        
        # Create spec file
        logger.info("Creating PyInstaller spec file...")
        spec_content = create_spec_file(version_str, display_version)
        spec_path = os.path.join(temp_dir, 'nfc_reader_writer.spec')
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Spec file was not created at {spec_path}")
        
        # Run PyInstaller
        logger.info("Running PyInstaller...")
        try:
            subprocess.check_call(
                [
                    'pyinstaller',
                    '--clean',
                    '--noconfirm',
                    '--distpath', os.path.join(project_root, 'dist/linux'),
                    '--workpath', os.path.join(temp_dir, 'build'),
                    '--specpath', temp_dir,
                    spec_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Paths for the built application
            app_dir = os.path.join(project_root, 'dist/linux/nfc-reader-writer')
            
            # Create .desktop file
            logger.info("Creating .desktop file...")
            desktop_content = create_linux_desktop_file(
                app_name=app_name,
                exec_path=os.path.join(app_dir, 'nfc-reader-writer'),
                icon_path=os.path.join(app_dir, 'logo.png'),
                comment="NFC Tag Reader/Writer Application",
                version=version_str
            )
            
            # Create necessary directories
            os.makedirs(os.path.join(dist_dir, 'usr/share/applications'), exist_ok=True)
            os.makedirs(os.path.join(dist_dir, 'usr/share/icons/hicolor/256x256/apps'), exist_ok=True)
            
            # Write .desktop file
            desktop_path = os.path.join(dist_dir, 'usr/share/applications/nfc-reader-writer.desktop')
            with open(desktop_path, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            
            # Copy icon if available
            icon_src = os.path.join(project_root, 'assets/logo.png')
            icon_dest = os.path.join(dist_dir, 'usr/share/icons/hicolor/256x256/apps/nfc-reader-writer.png')
            if os.path.exists(icon_src):
                shutil.copy2(icon_src, icon_dest)
            
            # Make the binary executable
            binary_path = os.path.join(app_dir, 'nfc-reader-writer')
            if os.path.exists(binary_path):
                st = os.stat(binary_path)
                os.chmod(binary_path, st.st_mode | stat.S_IEXEC)
            
            build_time = time.time() - start_time
            logger.info("✅ Build successful!")
            logger.info(f"Application is available in: {os.path.abspath(app_dir)}")
            logger.info(f"Build completed in {build_time:.2f} seconds")
            
            print("\n✅ Build successful!")
            print(f"Application is available in: {os.path.abspath(app_dir)}")
            print("\nTo create a distributable package, run:")
            print(f"  cd {os.path.dirname(dist_dir)} && tar -czvf nfc-reader-writer-linux-x86_64-{version_str}.tar.gz -C linux .")
            return 0
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during build: {e.output if hasattr(e, 'output') else e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error during build: {str(e)}", exc_info=True)
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1
        
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Could not remove temporary directory {temp_dir}: {e}")
        
        # Log build duration
        build_time = time.time() - start_time
        logger.info(f"Build completed in {build_time:.2f} seconds")

if __name__ == "__main__":
    sys.exit(main())
