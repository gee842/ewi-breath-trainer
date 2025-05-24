# Building Executables for EWI Long Tone Visualizer

This guide explains how to create standalone executables for Windows and macOS that can be distributed without requiring Python installation.

## Prerequisites

- Python 3.7 or higher
- All dependencies installed
- PyInstaller

## Quick Build (Recommended)

The easiest way to build executables is using the provided build script:

### 1. Install Build Dependencies

```bash
pip install -r build_requirements.txt
```

### 2. Run the Build Script

```bash
python build_executable.py
```

This will:
- Clean any previous builds
- Create a platform-specific executable
- Package it with documentation
- Create a release-ready folder

### 3. Find Your Executable

After building, you'll find:
- **Windows**: `release-windows/EWI-LongTone-Visualizer.exe`
- **macOS**: `release-macos/EWI-LongTone-Visualizer.app`
- **Linux**: `release-linux/EWI-LongTone-Visualizer`

## Manual Build (Advanced)

If you prefer to build manually with PyInstaller:

### Windows

```bash
pyinstaller --onefile --windowed --name=EWI-LongTone-Visualizer ^
  --hidden-import=matplotlib.backends.backend_agg ^
  --hidden-import=pygame --hidden-import=numpy ^
  --exclude-module=tkinter --exclude-module=PIL ^
  main.py
```

### macOS

```bash
pyinstaller --onefile --windowed --name=EWI-LongTone-Visualizer \
  --hidden-import=matplotlib.backends.backend_agg \
  --hidden-import=pygame --hidden-import=numpy \
  --exclude-module=tkinter --exclude-module=PIL \
  main.py
```

### Linux

```bash
pyinstaller --onefile --name=EWI-LongTone-Visualizer \
  --hidden-import=matplotlib.backends.backend_agg \
  --hidden-import=pygame --hidden-import=numpy \
  --exclude-module=tkinter --exclude-module=PIL \
  main.py
```

## Automated Builds (GitHub Actions)

The repository includes a GitHub Actions workflow that automatically builds executables when you create a release:

### To trigger automated builds:

1. Push your code to GitHub
2. Create a new release in GitHub
3. The workflow will automatically build Windows and macOS executables
4. Download the ZIP files from the release page

### Manual workflow trigger:

You can also trigger builds manually:
1. Go to the "Actions" tab in your GitHub repository
2. Select "Build Release Executables"
3. Click "Run workflow"

## File Sizes and Performance

- **Windows exe**: ~50-80 MB (includes Python runtime and all dependencies)
- **macOS app**: ~60-90 MB (includes Python runtime and all dependencies)
- **Startup time**: 2-5 seconds (first launch may be slower)

## Distribution

### For GitHub Releases:

1. Use the automated build workflow
2. Create a release with appropriate tags (e.g., v1.0.0)
3. The ZIP files will be automatically attached

### For Manual Distribution:

1. Build using the build script
2. ZIP the release folder contents
3. Share the ZIP file

## Troubleshooting

### Common Issues:

**"Module not found" errors:**
- Add missing modules to the `--hidden-import` list
- Check if the module is properly installed

**Large file sizes:**
- Add more modules to `--exclude-module` list
- Consider using `--onedir` instead of `--onefile` for faster startup

**macOS security warnings:**
- Users need to right-click and "Open" the first time
- Consider code signing for distribution (requires Apple Developer account)

**Windows antivirus warnings:**
- Common with PyInstaller executables
- Users may need to add exceptions
- Consider code signing for commercial distribution

### Build Environment:

**Python Version:**
- Use Python 3.9 for best compatibility
- Avoid very new Python versions (may have compatibility issues)

**Dependencies:**
- Always test with the exact versions in `build_requirements.txt`
- Newer versions of dependencies might cause issues

### Testing:

1. Test the executable on a clean system without Python
2. Test with different MIDI devices
3. Verify all features work correctly
4. Check for missing dependencies

## Advanced Configuration

### Custom Icons:

Add icon files to enable custom icons:
- **Windows**: `icon.ico` (ICO format)
- **macOS**: `icon.icns` (ICNS format)

### Additional Data Files:

To include additional files in the executable:

```bash
--add-data="source_file:destination_folder"
```

### Optimization:

For smaller executables:
- Use `--exclude-module` for unused packages
- Consider `--onedir` for faster startup
- Use UPX compression (may cause antivirus issues)

## Release Checklist

- [ ] Update version number in code
- [ ] Test the application thoroughly
- [ ] Build executables for target platforms
- [ ] Test executables on clean systems
- [ ] Create GitHub release with descriptive notes
- [ ] Upload or verify automated ZIP files
- [ ] Update README with download links 