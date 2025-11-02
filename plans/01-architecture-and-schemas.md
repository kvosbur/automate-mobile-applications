# Architecture & Data Schemas

## 🏗️ System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  automate-mobile-applications               │
│                      (Parent Repo)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   CLI Layer  │  │  Orchestrator│  │ Config Manager  │  │
│  │              │  │              │  │                 │  │
│  │ - collect    │  │ - Device     │  │ - Game configs  │  │
│  │ - train      │  │   coordinator│  │ - Global        │  │
│  │ - run        │  │ - Session mgr│  │   settings      │  │
│  │ - filter     │  │              │  │                 │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                 │                    │           │
│  ┌──────┴─────────────────┴────────────────────┴────────┐  │
│  │            Device Worker Pool                        │  │
│  │  ┌────────────────┐    ┌────────────────┐           │  │
│  │  │ Device Worker  │    │ Device Worker  │   ...     │  │
│  │  │   (Device 1)   │    │   (Device 2)   │           │  │
│  │  └────────┬───────┘    └────────┬───────┘           │  │
│  └───────────┼──────────────────────┼───────────────────┘  │
│              │                      │                      │
│  ┌───────────┴──────────────────────┴───────────────────┐  │
│  │          Appium Session Manager                      │  │
│  │  - Single Appium server, multiple sessions          │  │
│  │  - Screenshot capture                               │  │
│  │  - UI hierarchy extraction                          │  │
│  │  - Action execution (tap, swipe, etc.)              │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                  │
│  ┌──────────────────────┴───────────────────────────────┐  │
│  │          Session Data Manager                        │  │
│  │  - UUIDv7 session creation                          │  │
│  │  - Image + metadata persistence                     │  │
│  │  - Compression on completion                        │  │
│  │  - Failed session handling                          │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                  │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │    mobile-game-ad-detection             │
        │        (Submodule)                      │
        ├─────────────────────────────────────────┤
        │                                         │
        │  ┌──────────────────────────────────┐  │
        │  │   Ad Navigation Intelligence     │  │
        │  │                                  │  │
        │  │  • Model inference (YOLO)        │  │
        │  │  • Decision engine               │  │
        │  │  • Action strategy selector      │  │
        │  │  • Confidence thresholding       │  │
        │  └──────────────────────────────────┘  │
        │                                         │
        │  ┌──────────────────────────────────┐  │
        │  │   Model Training Pipeline        │  │
        │  │                                  │  │
        │  │  • Dataset preparation           │  │
        │  │  • YOLO training wrapper         │  │
        │  │  • Model versioning              │  │
        │  │  • Metrics tracking              │  │
        │  └──────────────────────────────────┘  │
        │                                         │
        │  ┌──────────────────────────────────┐  │
        │  │   Image Analysis Utils           │  │
        │  │                                  │  │
        │  │  • Visual diversity scoring      │  │
        │  │  • Frame diff calculation        │  │
        │  │  • Image quality metrics         │  │
        │  └──────────────────────────────────┘  │
        │                                         │
        └─────────────────────────────────────────┘
```

## 📁 Complete Project Structure

```
automate-mobile-applications/
├── pyproject.toml                    # Project metadata, dependencies
├── requirements.txt                  # Pinned dependencies
├── README.md                         # Setup & usage docs
├── ideas.md                          # Design notes (existing)
├── .gitignore                        # Ignore sessions/, models/, etc.
│
├── plans/                            # Project planning documents
│   ├── 00-project-overview.md
│   ├── 01-architecture-and-schemas.md
│   ├── 02-phase-1-data-collection.md
│   ├── 03-phase-2-filtering.md
│   ├── 04-phase-3-training.md
│   ├── 05-phase-4-inference.md
│   ├── 06-phase-5-iteration.md
│   ├── 07-technical-stack.md
│   ├── 08-workflows.md
│   └── 09-challenges.md
│
├── configs/                          # Game-specific configurations
│   ├── global_config.json            # System-wide settings
│   ├── games/                        # Per-game configs
│   │   ├── game_template.json        # Reference template
│   │   ├── example_game_1.json
│   │   └── example_game_2.json
│   └── training_config.json          # Model training parameters
│
├── automate-mobile-applications/     # Main package
│   ├── __init__.py
│   ├── __main__.py                   # CLI entry point
│   │
│   ├── cli/                          # Command-line interface
│   │   ├── __init__.py
│   │   ├── collect.py                # Data collection command
│   │   ├── train.py                  # Training command
│   │   ├── run.py                    # Inference command
│   │   ├── filter.py                 # Session filtering command
│   │   └── utils.py                  # CLI helpers (progress bars, etc.)
│   │
│   ├── core/                         # Core orchestration
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Main coordinator
│   │   ├── device_worker.py          # Per-device session runner
│   │   ├── session_manager.py        # Session lifecycle management
│   │   └── config_manager.py         # Config loading & validation
│   │
│   ├── appium/                       # Appium & Android integration
│   │   ├── __init__.py
│   │   ├── appium_service.py         # Existing: Appium server mgmt
│   │   ├── appium_capabilities.py    # Existing: Capabilities builder
│   │   ├── driver_manager.py         # Multi-device driver pool
│   │   ├── screen_capture.py         # Screenshot utilities
│   │   └── adb_utils.py              # ADB commands (force-stop, current app, etc.)
│   │
│   ├── actions/                      # Action execution system
│   │   ├── __init__.py
│   │   ├── action_schema.py          # Action dataclasses (Tap, Wait, Swipe, etc.)
│   │   ├── action_executor.py        # Executes actions on device
│   │   └── action_loader.py          # Loads actions from game configs
│   │
│   ├── data/                         # Data management
│   │   ├── __init__.py
│   │   ├── session_data.py           # Session folder creation, UUIDv7
│   │   ├── metadata_schema.py        # JSON metadata structures
│   │   ├── compression.py            # Session zip compression
│   │   └── dataset_builder.py        # Sessions → Dataset converter
│   │
│   ├── filtering/                    # Image selection & filtering
│   │   ├── __init__.py
│   │   ├── visual_diversity.py       # Image clustering & selection
│   │   ├── frame_diff.py             # Frame difference metrics
│   │   └── duplicate_detection.py    # Perceptual deduplication
│   │
│   └── utils/                        # Shared utilities
│       ├── __init__.py
│       ├── logger.py                 # Logging setup
│       ├── exceptions.py             # Custom exceptions
│       └── validators.py             # Config & data validators
│
├── libs/                             # Git submodules
│   └── mobile-game-ad-detection/     # Submodule (see detailed structure below)
│
├── sessions/                         # Session data (git-ignored)
│   ├── 01933b4e-7890-7123-abcd-123456789abc/  # UUIDv7 session
│   │   ├── 0001.png
│   │   ├── 0001.json
│   │   ├── 0002.png
│   │   ├── 0002.json
│   │   ├── ...
│   │   └── session_metadata.json     # Session-level info
│   ├── 01933b4f-1234-7456-ef01-987654321def.zip  # Compressed completed session
│   └── failed/                       # Failed sessions
│       └── 01933b50-abcd-7890-1234-abcdef123456/
│           ├── (session files)
│           └── error.json            # Stack trace & error info
│
├── dataset/                          # Curated training data (git-ignored)
│   ├── close_button-white-top_right/
│   │   ├── 0001.png
│   │   ├── 0001.json                 # Includes Label Studio annotations
│   │   └── ...
│   ├── skip_button-gray-bottom_right/
│   └── ...
│
├── models/                           # Trained models (git-ignored)
    ├── model_v001/
    │   ├── best.pt                   # YOLO weights
    │   ├── training_config.json      # Hyperparameters used
    │   └── metrics.json              # Training metrics, dataset size
    ├── model_v002/
    └── ...
```

### Submodule Structure: `libs/mobile-game-ad-detection/`

```
mobile-game-ad-detection/
├── pyproject.toml
├── requirements.txt
├── README.md
│
├── mobile_game_ad_detection/         # Main package
│   ├── __init__.py
│   │
│   ├── inference/                    # Model inference
│   │   ├── __init__.py
│   │   ├── model_loader.py           # Load YOLO models
│   │   ├── detector.py               # Run inference on images
│   │   └── result_parser.py          # Parse YOLO outputs
│   │
│   ├── decision/                     # Decision engine
│   │   ├── __init__.py
│   │   ├── strategy.py               # Action selection strategies
│   │   ├── confidence_filter.py      # Threshold-based filtering
│   │   └── state_tracker.py          # Track ad navigation state
│   │
│   ├── training/                     # Training pipeline
│   │   ├── __init__.py
│   │   ├── dataset_prep.py           # Convert to YOLO format
│   │   ├── trainer.py                # YOLO training wrapper
│   │   ├── model_versioning.py       # Increment versions, save metadata
│   │   └── evaluator.py              # Model evaluation metrics
│   │
│   └── utils/                        # Utilities
│       ├── __init__.py
│       ├── image_analysis.py         # Visual diversity, frame diff
│       └── label_utils.py            # Label parsing & manipulation
│
└── tests/
    └── ...
```

## 🗂️ Data Schemas

### 1. Global Configuration (`configs/global_config.json`)

```json
{
  "system": {
    "appium_host": "localhost",
    "appium_port": 4723,
    "capture_interval_seconds": 1.0,
    "session_max_duration_seconds": 120,
    "compress_sessions_on_completion": true
  },
  "paths": {
    "sessions_dir": "sessions",
    "dataset_dir": "dataset",
    "models_dir": "models",
    "failed_sessions_dir": "sessions/failed"
  },
  "filtering": {
    "frame_diff_threshold": 0.15,
    "visual_diversity_clusters": 10,
    "max_images_per_session": 50
  },
  "devices": [
    {
      "device_id": "emulator-5554",
      "enabled": true
    },
    {
      "device_id": "FA83M1A12345",
      "enabled": true
    }
  ]
}
```

### 2. Game Configuration (`configs/games/example_game_1.json`)

```json
{
  "game": "Example Puzzle Game",
  "package_name": "com.example.puzzlegame",
  "activity": ".MainActivity",
  "device_specific_actions": {
    "emulator-5554": {
      "setup_steps": [
        {
          "action": "tap",
          "x": 540,
          "y": 960,
          "description": "Tap main menu button"
        },
        {
          "action": "wait",
          "seconds": 2.0,
          "description": "Wait for menu to load"
        },
        {
          "action": "tap",
          "resource_id": "com.example.puzzlegame:id/watch_ad_button",
          "description": "Tap 'Watch Ad for Coins' button"
        },
        {
          "action": "wait_for_element",
          "resource_id": "com.example.ad:id/ad_container",
          "timeout_seconds": 10,
          "description": "Wait for ad to appear"
        }
      ]
    },
    "FA83M1A12345": {
      "setup_steps": [
        {
          "action": "tap",
          "x": 720,
          "y": 1280,
          "description": "Tap main menu button (different resolution)"
        }
      ]
    }
  },
  "metadata": {
    "typical_ad_duration_seconds": 30,
    "reward_type": "coins",
    "notes": "This game has reliable ad buttons"
  }
}
```

### 3. Action Schema (Python Dataclasses in `actions/action_schema.py`)

```python
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class BaseAction:
    description: Optional[str] = None

@dataclass
class TapAction(BaseAction):
    action: Literal["tap"] = "tap"
    x: Optional[int] = None
    y: Optional[int] = None
    resource_id: Optional[str] = None
    xpath: Optional[str] = None

@dataclass
class WaitAction(BaseAction):
    action: Literal["wait"] = "wait"
    seconds: float = 1.0

@dataclass
class SwipeAction(BaseAction):
    action: Literal["swipe"] = "swipe"
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration_ms: int = 500

@dataclass
class WaitForElementAction(BaseAction):
    action: Literal["wait_for_element"] = "wait_for_element"
    resource_id: Optional[str] = None
    xpath: Optional[str] = None
    timeout_seconds: float = 10.0

# Union type for all actions
Action = TapAction | WaitAction | SwipeAction | WaitForElementAction
```

### 4. Session Metadata (`sessions/{uuid}/session_metadata.json`)

```json
{
  "session_id": "01933b4e-7890-7123-abcd-123456789abc",
  "device_id": "emulator-5554",
  "game": "Example Puzzle Game",
  "package_name": "com.example.puzzlegame",
  "start_timestamp": "2025-11-02T14:30:00.123456Z",
  "end_timestamp": "2025-11-02T14:30:45.987654Z",
  "duration_seconds": 45.864,
  "mode": "collect",
  "model_version": null,
  "total_frames": 45,
  "total_actions": 3,
  "status": "completed",
  "completion_reason": "ad_completed",
  "decision_log": [
    {
      "timestamp": "2025-11-02T14:30:15.123Z",
      "frame_number": 15,
      "decision": "wait",
      "reason": "No high-confidence detections"
    },
    {
      "timestamp": "2025-11-02T14:30:30.456Z",
      "frame_number": 30,
      "decision": "tap",
      "coordinates": [1080, 100],
      "reason": "Detected close_button-white-top_right with confidence 0.91",
      "model_detections": [
        {
          "label": "close_button-white-top_right",
          "confidence": 0.91,
          "bbox": [1050, 70, 1110, 130]
        }
      ]
    }
  ],
  "final_outcome": {
    "success": true,
    "reward_received": true,
    "back_in_game": true
  },
  "error": null
}
```

### 5. Frame Metadata (`sessions/{uuid}/0001.json`)

```json
{
  "session_id": "01933b4e-7890-7123-abcd-123456789abc",
  "frame_number": 1,
  "timestamp": "2025-11-02T14:30:01.123456Z",
  "seconds_into_ad": 1.0,
  "actions_taken_so_far": 0,
  "model_version": "model_v005",
  "model_detections": [
    {
      "label": "video_content-generic-center",
      "confidence": 0.87,
      "bbox": [100, 200, 980, 1600]
    },
    {
      "label": "skip_button-gray-bottom_right",
      "confidence": 0.45,
      "bbox": [900, 1750, 1050, 1850]
    }
  ],
  "action_taken": null,
  "action_coordinates": null,
  "action_success": null,
  "appium_ui_hierarchy": {
    "package": "com.example.ad.network",
    "elements": [
      {
        "class": "android.widget.FrameLayout",
        "resource-id": "com.example.ad:id/ad_container",
        "bounds": "[0,0][1080,1920]",
        "clickable": false
      }
    ]
  }
}
```

### 6. Failed Session Error (`sessions/failed/{uuid}/error.json`)

```json
{
  "session_id": "01933b50-abcd-7890-1234-abcdef123456",
  "device_id": "FA83M1A12345",
  "failure_timestamp": "2025-11-02T15:45:30.123456Z",
  "error_type": "AppiumException",
  "error_message": "Could not find element with resource_id: com.example.puzzlegame:id/watch_ad_button",
  "stack_trace": "Traceback (most recent call last):\n  File ...",
  "frames_captured_before_failure": 12,
  "last_action_attempted": {
    "action": "tap",
    "resource_id": "com.example.puzzlegame:id/watch_ad_button"
  }
}
```

### 7. Model Metadata (`models/model_v001/metrics.json`)

```json
{
  "model_version": 1,
  "base_model": "yolov8n.pt",
  "training_timestamp": "2025-11-02T16:00:00.000000Z",
  "dataset": {
    "total_images": 250,
    "labels": [
      "close_button-white-top_right",
      "close_button-black-top_left",
      "skip_button-gray-bottom_right",
      "video_content-generic-center"
    ],
    "images_per_label": {
      "close_button-white-top_right": 85,
      "close_button-black-top_left": 42,
      "skip_button-gray-bottom_right": 78,
      "video_content-generic-center": 45
    }
  },
  "training_config": {
    "epochs": 100,
    "batch_size": 16,
    "image_size": 640,
    "device": "cpu",
    "patience": 20
  },
  "performance": {
    "mAP50": 0.78,
    "mAP50_95": 0.54,
    "precision": 0.82,
    "recall": 0.75,
    "training_time_seconds": 1847
  },
  "notes": "First model trained with manually annotated images"
}
```

## 🔄 Data Flow

### Collection Mode
```
Device → Appium → Screenshot + UI Hierarchy
                    ↓
              Session Manager
                    ↓
        Create UUIDv7 session folder
                    ↓
    Save frame_NNNN.png + frame_NNNN.json
                    ↓
        On completion: Create session_metadata.json
                    ↓
        Compress to session_ID.zip
```

### Inference Mode
```
Device → Appium → Screenshot + UI Hierarchy
                    ↓
        mobile-game-ad-detection (submodule)
                    ↓
            Model Inference (YOLO)
                    ↓
            Decision Engine
                    ↓
        Recommended Action (tap/wait/swipe)
                    ↓
        Session Manager logs decision
                    ↓
        Appium executes action
                    ↓
        Save frame + metadata (includes model predictions)
```

## 🔌 Component Interfaces

### Parent → Submodule Interface

```python
# Parent passes image + context to submodule
from mobile_game_ad_detection.inference import Detector
from mobile_game_ad_detection.decision import DecisionEngine

# Initialize
detector = Detector(model_path="models/model_v003/best.pt")
decision_engine = DecisionEngine(
    confidence_thresholds={
        "close_button": 0.7,
        "skip_button": 0.75
    }
)

# Per frame
image_array = capture_screenshot()  # numpy array
ui_hierarchy = get_ui_hierarchy()   # dict

detections = detector.detect(image_array)
action = decision_engine.decide(
    detections=detections,
    ui_hierarchy=ui_hierarchy,
    current_state={"seconds_into_ad": 15, "actions_taken": 0}
)

# action = {"type": "tap", "x": 1080, "y": 100, "confidence": 0.91}
```

---

**Status**: Architecture defined, ready for implementation  
**Next**: Review Phase 1 implementation plan
