import os
import sys
import shutil
import stat
import subprocess
import tempfile
import time
import logging
from pathlib import Path
import sys

# Configure logging with UTF-8 encoding
class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        UTF8StreamHandler(),
        logging.FileHandler('build.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def convert_png_to_ico(png_path, ico_path):
    """Convert a PNG file to ICO format using Wand."""
    try:
        from wand.image import Image as WandImage
        with WandImage(filename=png_path) as img:
            img.format = 'ico'
            img.save(filename=ico_path)
        return True
    except ImportError:
        logger.error("Wand is required for PNG to ICO conversion. Please install it with: pip install wand")
        return False
    except Exception as e:
        logger.error(f"Error converting {png_path} to ICO: {e}")
        return False

def get_version():
    """Get version information from script/version.py"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.join(project_root, 'script')
        
        # Add script directory to path if not already there
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Import version information
        try:
            from version import MAJOR, MINOR, PATCH, PRERELEASE, BUILD, get_version_string
            
            version_str = f"{MAJOR}.{MINOR}.{PATCH}"
            if PRERELEASE:
                version_str += f"-{PRERELEASE}"
            if BUILD:
                version_str += f"+{BUILD}"
                
            display_version = get_version_string()
            logger.info(f"Building version: {version_str} (using build version: {display_version})")
            return version_str, display_version
            
        except ImportError as e:
            logger.warning(f"Could not import from version.py: {e}")
            # Fallback to reading the file directly
            version_file = os.path.join(script_dir, 'version.py')
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_content = f.read()
                
                # Simple parsing of version info
                version_info = {}
                for line in version_content.split('\n'):
                    if '=' in line and any(v in line for v in ['MAJOR', 'MINOR', 'PATCH', 'PRERELEASE', 'BUILD']):
                        var, val = line.split('=')
                        var = var.strip()
                        val = val.strip()
                        if val.startswith(('"', "'")):
                            val = val[1:-1]  # Remove quotes
                        version_info[var] = val
                
                version_str = f"{version_info.get('MAJOR', '1')}.{version_info.get('MINOR', '0')}.{version_info.get('PATCH', '1')}"
                if 'PRERELEASE' in version_info and version_info['PRERELEASE']:
                    version_str += f"-{version_info['PRERELEASE']}"
                if 'BUILD' in version_info and version_info['BUILD']:
                    version_str += f"+{version_info['BUILD']}"
                
                # Try to get display version
                display_version = version_str
                if 'get_version_string' in version_content:
                    # If there's a get_version_string function, use it
                    try:
                        from version import get_version_string as gvs
                        display_version = gvs()
                    except:
                        pass
                
                logger.info(f"Built version: {version_str} (using build version: {display_version})")
                return version_str, display_version
            
            # If all else fails, return defaults
            logger.warning("Using default version numbers")
            return "1.0.1", "1.0.1"
            
    except Exception as e:
        logger.error(f"Error reading version: {e}", exc_info=True)
        return "1.0.1", "1.0.1"

def create_spec_file(version_str, display_version, icon_path='NONE', target_dir='.'):
    """Create a PyInstaller spec file for the application"""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{os.path.abspath(target_dir)}'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
        ('data', 'data'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add any additional files needed at runtime
added_files = [
    ('script', 'script'),
]

for src, dst in added_files:
    if os.path.exists(src):
        a.datas += Tree(src, prefix=dst)

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
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path if icon_path != 'NONE' else ''}',
    version='{display_version}',
)
"""
    # Save the spec file in the target directory
    spec_file = os.path.join(target_dir, 'nfc_reader.spec')
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return spec_file

def main():
    """Main function to build the Windows executable"""
    start_time = time.time()
    temp_dir = None
    
    try:
        logger.info("Starting NFC Reader/Writer Windows build process...")
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        def remove_readonly(func, path, _):
            """Remove readonly attribute and retry the operation"""
            try:
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                
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
                
                func(path)
                return
            except Exception as e:
                logger.warning(f"Could not remove {path}: {e}")
                if os.path.isfile(path):
                    try:
                        with open(path, 'w'):
                            pass
                    except Exception as e:
                        logger.warning(f"Could not truncate {path}: {e}")
        
        # Clean previous builds
        build_dir = os.path.join(project_root, 'build')
        dist_dir = os.path.join(project_root, 'dist', 'windows')
        
        # Clean build and dist directories
        for directory in [build_dir, dist_dir]:
            if os.path.exists(directory):
                logger.info(f"Cleaning {directory} directory...")
                shutil.rmtree(directory, onerror=remove_readonly, ignore_errors=True)
        
        # Create dist directory if it doesn't exist
        os.makedirs(dist_dir, exist_ok=True)
        
        # Get version information
        version_str, display_version = get_version()
        
        # Create a temporary directory for build files
        temp_dir = tempfile.mkdtemp(prefix='nfc_build_')
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
        
        # Handle icon conversion
        icon_path = os.path.join('assets', 'logo.png')
        ico_path = os.path.join(temp_dir, 'app.ico')
        
        if os.path.exists(icon_path):
            if convert_png_to_ico(icon_path, ico_path):
                logger.info(f"Created icon: {ico_path}")
                icon_path = ico_path
            else:
                logger.warning("Could not convert PNG to ICO, proceeding without icon")
                icon_path = 'NONE'
        else:
            logger.warning("Icon file not found, proceeding without icon")
            icon_path = 'NONE'
        
        # Create spec file
        logger.info("Creating PyInstaller spec file...")
        spec_content = create_spec_file(version_str, display_version, icon_path, temp_dir)
        spec_file = os.path.join(temp_dir, 'nfc_reader.spec')
        
        # Write the spec file
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        if not os.path.exists(spec_file):
            raise FileNotFoundError(f"Spec file was not created at {spec_file}")
        
        # Run PyInstaller with output capture
        logger.info("Running PyInstaller...")
        try:
            # Get the path to the PyInstaller executable in the virtual environment
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                # We're in a virtual environment
                pyinstaller_path = os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe')
            else:
                # Not in a virtual environment, use the system pyinstaller
                pyinstaller_path = 'pyinstaller'
            
            # Verify main.py exists in the project root
            main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
            if not os.path.exists(main_script):
                raise FileNotFoundError(f"Main script not found at {main_script}")
            
            # Create data files list with absolute paths
            data_dirs = ['script', 'assets', 'config', 'data']
            add_data_args = []
            
            for data_dir in data_dirs:
                src_path = os.path.join(project_root, data_dir)
                if os.path.exists(src_path):
                    add_data_args.extend(['--add-data', f'{src_path}{os.pathsep}{data_dir}'])
            
            # First, run with --noconfirm to avoid any interactive prompts
            cmd = [
                pyinstaller_path,
                '--clean',
                '--noconfirm',
                '--workpath', os.path.join(temp_dir, 'build'),
                '--distpath', os.path.join(temp_dir, 'dist'),
                '--specpath', temp_dir,
                '--name', 'NFC_Reader',
                *add_data_args,
                '--additional-hooks-dir', project_root,
                main_script
            ]
            
            logger.info(f"Executing: {' '.join(cmd)}")
            
            # Run PyInstaller from the project root directory
            try:
                result = subprocess.run(
                    cmd,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            except Exception as e:
                logger.error(f"Failed to execute PyInstaller: {str(e)}")
                raise
            
            # Log the output
            if result.stdout:
                logger.info("PyInstaller output:")
                for line in result.stdout.splitlines():
                    logger.info(f"  {line}")
            
            if result.stderr:
                logger.error("PyInstaller errors:")
                for line in result.stderr.splitlines():
                    logger.error(f"  {line}")
            
            # Check if build was successful
            if result.returncode != 0:
                logger.error(f"❌ PyInstaller failed with return code {result.returncode}")
                return 1
            
            # Look for the built executable
            built_exe = os.path.join(temp_dir, 'dist', 'nfc_reader', 'nfc_reader.exe')
            if not os.path.exists(built_exe):
                # Try alternative location
                built_exe = os.path.join(temp_dir, 'dist', 'nfc-reader', 'nfc_reader.exe')
            
            if os.path.exists(built_exe):
                # Ensure dist directory exists
                os.makedirs(dist_dir, exist_ok=True)
                
                # Copy the executable
                dest_exe = os.path.join(dist_dir, f'NFC_Reader_App-{version_str}.exe')
                shutil.copy2(built_exe, dest_exe)
                
                logger.info(f"✅ Build successful!")
                logger.info(f"Executable created at: {dest_exe}")
                return 0
            else:
                logger.error("❌ Build completed but could not find the output executable.")
                logger.error(f"Searched in: {os.path.join(temp_dir, 'dist')}")
                return 1
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ PyInstaller command failed with return code {e.returncode}")
            if e.stdout:
                logger.error("=== STDOUT ===")
                logger.error(e.stdout)
            if e.stderr:
                logger.error("=== STDERR ===")
                logger.error(e.stderr)
            return 1
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
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
