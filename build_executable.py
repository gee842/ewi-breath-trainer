#!/usr/bin/env python3
"""
Build script for creating EWI Long Tone Visualizer executables
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos", ".app"
    elif system == "windows":
        return "windows", ".exe"
    else:
        return "linux", ""

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

def build_executable():
    """Build the executable using PyInstaller"""
    platform_name, extension = get_platform_info()
    
    # PyInstaller arguments
    args = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window (GUI app)
        "--name=EWI-LongTone-Visualizer",
        "--icon=icon.ico" if platform_name == "windows" else "--icon=icon.icns",
        # Add data files
        "--add-data=README.md:.",
        "--add-data=requirements.txt:.",
        # Hidden imports for matplotlib backends and dependencies
        "--hidden-import=matplotlib.backends.backend_agg",
        "--hidden-import=matplotlib.backends.backend_tkinter", 
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=pygame",
        "--hidden-import=numpy",
        # Exclude unnecessary modules to reduce size
        "--exclude-module=tkinter",
        "main.py"
    ]
    
    # Remove icon argument if icon files don't exist
    if not os.path.exists("icon.ico") and not os.path.exists("icon.icns"):
        args = [arg for arg in args if not arg.startswith("--icon")]
    
    print(f"Building executable for {platform_name}...")
    print(f"Command: {' '.join(args)}")
    
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_release_package():
    """Create a release package with the executable and documentation"""
    platform_name, extension = get_platform_info()
    
    # Create release directory
    release_dir = f"release-{platform_name}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copy executable
    executable_name = f"EWI-LongTone-Visualizer{extension}"
    if platform_name == "macos":
        # On macOS, PyInstaller creates a .app bundle
        src_path = f"dist/{executable_name}"
        if os.path.exists(src_path):
            shutil.copytree(src_path, f"{release_dir}/{executable_name}")
        else:
            print(f"Warning: Could not find {src_path}")
            return False
    else:
        # On Windows/Linux, it's a single file
        src_path = f"dist/{executable_name}"
        if os.path.exists(src_path):
            shutil.copy2(src_path, release_dir)
        else:
            print(f"Warning: Could not find {src_path}")
            return False
    
    # Copy documentation
    docs_to_copy = ["README.md", "requirements.txt"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir)
    
    # Create installation instructions
    create_install_instructions(release_dir, platform_name)
    
    print(f"Release package created in {release_dir}/")
    return True

def create_install_instructions(release_dir, platform_name):
    """Create platform-specific installation instructions"""
    if platform_name == "macos":
        instructions = """# EWI Long Tone Visualizer - macOS Installation

## Quick Start
1. Double-click "EWI-LongTone-Visualizer.app" to run
2. If you get a security warning, right-click the app and select "Open"
3. Connect your EWI/MIDI controller and start practicing!

## First Time Setup
macOS may prevent the app from running because it's not from the App Store:
1. Right-click on "EWI-LongTone-Visualizer.app"
2. Select "Open" from the context menu
3. Click "Open" in the security dialog

## Troubleshooting
- If the app won't open, try running from Terminal: `./EWI-LongTone-Visualizer.app/Contents/MacOS/EWI-LongTone-Visualizer`
- Make sure your MIDI device is connected and recognized by macOS
- Check Audio MIDI Setup if you have MIDI connection issues
"""
    
    elif platform_name == "windows":
        instructions = """# EWI Long Tone Visualizer - Windows Installation

## Quick Start
1. Double-click "EWI-LongTone-Visualizer.exe" to run
2. Connect your EWI/MIDI controller and start practicing!

## First Time Setup
Windows may show a security warning for unsigned executables:
1. Click "More info" if Windows Defender appears
2. Click "Run anyway" to proceed
3. The app will remember this choice for future runs

## Troubleshooting
- If you get DLL errors, install Visual C++ Redistributable
- Make sure your MIDI device drivers are installed
- Run as Administrator if you have permission issues
- Check Windows Device Manager if MIDI isn't detected
"""
    
    else:  # Linux
        instructions = """# EWI Long Tone Visualizer - Linux Installation

## Quick Start
1. Open terminal in this directory
2. Make executable: `chmod +x EWI-LongTone-Visualizer`
3. Run: `./EWI-LongTone-Visualizer`
4. Connect your EWI/MIDI controller and start practicing!

## Dependencies
Make sure you have ALSA and MIDI support:
```bash
sudo apt-get install alsa-utils libasound2-dev
```

## Troubleshooting
- Add your user to the audio group: `sudo usermod -a -G audio $USER`
- Check MIDI devices: `aconnect -l`
- Install additional MIDI tools if needed: `sudo apt-get install qjackctl`
"""
    
    with open(f"{release_dir}/INSTALL.md", "w") as f:
        f.write(instructions)

def main():
    """Main build process"""
    print("EWI Long Tone Visualizer - Executable Builder")
    print("=" * 50)
    
    # Check if PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller not found. Install it with:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create release package
    if create_release_package():
        platform_name, _ = get_platform_info()
        print(f"\n[SUCCESS] Build complete!")
        print(f"[PACKAGE] Release package: release-{platform_name}/")
        print(f"[READY] Ready for GitHub release!")
    else:
        print("[ERROR] Failed to create release package")
        sys.exit(1)

if __name__ == "__main__":
    main() 