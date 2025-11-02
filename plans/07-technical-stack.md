# Technical Stack & Dependencies

## 🐍 Python Version

**Required**: Python 3.10+  
**Recommended**: Python 3.11 for best performance

## 📦 Dependencies

### Parent Repository: `automate-mobile-applications`

```toml
[project]
name = "automate-mobile-applications"
version = "0.1.0"
description = "Mobile ad automation system using Appium and YOLO object detection"
requires-python = ">=3.10"

dependencies = [
    # Appium & Device Control
    "appium-python-client>=3.0.0",
    
    # Image Processing
    "opencv-python>=4.8.0",
    "pillow>=10.0.0",
    "numpy>=1.24.0",
    
    # Configuration & Validation
    "pyyaml>=6.0",
    "pydantic>=2.0.0",
    
    # Utilities
    "uuid-utils>=0.7.0",      # UUIDv7 support
    "rich>=13.0.0",           # CLI progress bars and formatting
    
    # Analysis
    "scikit-learn>=1.3.0",    # K-means clustering
    "imagehash>=4.3.0",       # Perceptual hashing
    "scikit-image>=0.21.0",   # SSIM and image metrics
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.0.292",
    "mypy>=1.5.0",
]
```

### Submodule: `libs/mobile-game-ad-detection`

```toml
[project]
name = "mobile-game-ad-detection"
version = "0.1.0"
description = "YOLO-based ad detection and decision engine"
requires-python = ">=3.10"

dependencies = [
    # YOLO & Deep Learning
    "ultralytics>=8.0.0",     # YOLOv8 training and inference
    "torch>=2.0.0",           # PyTorch backend
    "torchvision>=0.15.0",
    
    # Image Processing
    "opencv-python>=4.8.0",
    "pillow>=10.0.0",
    "numpy>=1.24.0",
    
    # Utilities
    "pydantic>=2.0.0",
    "scikit-learn>=1.3.0",
]

[project.optional-dependencies]
gpu = [
    "torch>=2.0.0+cu118",     # CUDA-enabled PyTorch
]
```

## 🛠️ External Tools

### Appium Server
```bash
# Install globally via npm
npm i --location=global appium@3.1.0

# Verify installation
appium --version
```

### Android SDK Platform Tools (ADB)
- Download from: https://developer.android.com/studio/releases/platform-tools
- Add to PATH
- Verify: `adb version`

### Label Studio (Annotation Tool)
```bash
# Install via pip
pip install label-studio

# Or via conda
conda install -c conda-forge label-studio

# Run server
label-studio start
```

## 📚 Key Libraries Explained

### Core Functionality

**appium-python-client** (3.0.0+)
- WebDriver bindings for Appium
- Device control and automation
- Element finding and interaction

**opencv-python** (4.8.0+)
- Image loading and saving
- Frame difference calculation
- Image preprocessing

**ultralytics** (8.0.0+)
- YOLOv8 implementation
- Training and inference
- Model export and optimization

**torch** (2.0.0+)
- Deep learning backend for YOLO
- CPU and GPU support
- Model serialization

### Configuration & Validation

**pydantic** (2.0.0+)
- Config validation with type hints
- Automatic parsing and conversion
- Clear error messages

**pyyaml** (6.0+)
- YAML config file parsing
- Human-readable configuration

### CLI & User Experience

**rich** (13.0.0+)
- Beautiful terminal output
- Progress bars and spinners
- Syntax highlighting
- Tables and formatting

### Data Analysis

**scikit-learn** (1.3.0+)
- K-means clustering for visual diversity
- Feature extraction utilities
- Metrics and evaluation

**imagehash** (4.3.0+)
- Perceptual hashing (pHash, dHash)
- Duplicate detection
- Fast similarity comparison

**scikit-image** (0.21.0+)
- SSIM (Structural Similarity Index)
- Advanced image metrics
- Quality assessment

### Utilities

**uuid-utils** (0.7.0+)
- UUIDv7 generation
- Chronologically sortable IDs
- Better than UUID4 for ordering

## 🖥️ System Requirements

### Development Machine

**Minimum**:
- macOS 11+, Linux, or Windows 10+
- 8 GB RAM
- 50 GB free disk space (for sessions data)
- Python 3.10+

**Recommended**:
- macOS 13+, Ubuntu 22.04+, or Windows 11
- 16 GB RAM
- 200 GB free disk space
- Python 3.11
- SSD for faster I/O

### Android Devices

**Requirements**:
- Android 8.0+ (API 26+)
- USB debugging enabled
- Developer options enabled
- Stable USB connection

**Tested Devices**:
- Google Pixel series
- Samsung Galaxy series
- OnePlus devices
- Generic Android emulators

## 🚀 Installation Guide

### 1. Clone Repository
```bash
git clone --recurse-submodules https://github.com/kvosbur/automate-mobile-applications.git
cd automate-mobile-applications
```

### 2. Create Virtual Environment
```bash
# Using venv
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n mobile-ad-automation python=3.11
conda activate mobile-ad-automation
```

### 3. Install Dependencies
```bash
# Install parent repo
pip install -e .

# Install submodule
cd libs/mobile-game-ad-detection
pip install -e .
cd ../..

# Optional: Install development tools
pip install -e ".[dev]"
```

### 4. Install External Tools
```bash
# Appium
npm i --location=global appium@3.1.0

# Verify
appium --version
adb version
python -c "from appium import webdriver; print('Appium client OK')"
```

### 5. Download YOLO Base Model
```bash
# YOLOv8 nano (lightest, fastest)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 6. Connect Devices
```bash
# List connected devices
adb devices

# Should show your devices
# List of devices attached
# emulator-5554          device
# FA83M1A12345          device
```

### 7. Verify Installation
```bash
# Run version check
python -m automate_mobile_applications --version

# Test Appium connection (if server running)
python -c "from appium import webdriver; print('Ready!')"
```

## 🎯 Platform-Specific Notes

### macOS
- Xcode Command Line Tools required for some dependencies
- Homebrew recommended for installing npm
- May need to allow Appium server in Security settings

### Linux
- Install `libgl1` for OpenCV: `sudo apt install libgl1-mesa-glx`
- May need udev rules for ADB: https://developer.android.com/studio/run/device#setting-up

### Windows
- Visual Studio C++ Build Tools required for some packages
- Use PowerShell or WSL for better compatibility
- USB drivers may need manual installation per device manufacturer

## 🔄 Dependency Updates

### Checking for Updates
```bash
# List outdated packages
pip list --outdated

# Update specific package
pip install --upgrade ultralytics
```

### Version Pinning Strategy
- **Major versions**: Pin for stability (e.g., `ultralytics>=8.0.0,<9.0.0`)
- **Minor versions**: Allow updates for bug fixes
- **Development**: Use latest versions for new features
- **Production**: Pin exact versions for reproducibility

## 🐛 Common Issues & Solutions

### Issue: Appium won't start
**Solution**: Check port 4723 not in use, try `killall node`

### Issue: ADB devices not showing
**Solution**: Restart ADB server: `adb kill-server && adb start-server`

### Issue: PyTorch CPU-only warning
**Solution**: Install CPU-specific version:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: OpenCV import error on macOS
**Solution**: Install missing libraries:
```bash
brew install libffi
```

### Issue: Slow YOLO inference
**Solution**: Use smaller model (yolov8n) or enable GPU acceleration

## 📊 Performance Benchmarks

### Expected Performance (MacBook Pro M1, 16GB RAM)

| Operation | Time | Notes |
|-----------|------|-------|
| Screenshot capture | 50-100ms | Via Appium |
| YOLO inference (yolov8n, CPU) | 1.5-2.0s | 640x640 input |
| Frame difference calculation | 10-20ms | 1080p images |
| Visual diversity (100 images) | 5-10s | K-means clustering |
| Session compression | 2-5s | 50 frames |

### GPU Acceleration (NVIDIA RTX 3080)

| Operation | CPU Time | GPU Time | Speedup |
|-----------|----------|----------|---------|
| YOLO inference (yolov8n) | 1.8s | 0.15s | 12x |
| YOLO training (100 epochs) | ~45 min | ~8 min | 5.6x |

---

**Last Updated**: 2025-11-02  
**Maintained By**: Project team
