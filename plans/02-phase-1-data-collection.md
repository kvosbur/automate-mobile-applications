# Phase 1: Foundation & Data Collection Mode

**Goal**: Capture raw session data from devices without any model  
**Status**: Not Started  
**Priority**: ⭐ MVP - Must complete first

## 📋 Overview

This phase establishes the foundation of the entire system. By the end, you'll have a working data collection pipeline that can:
- Run multiple Android devices in parallel
- Execute game-specific navigation sequences to reach ads
- Capture screenshots and metadata at 1-second intervals
- Handle errors gracefully without affecting other devices
- Compress completed sessions automatically
- Move failed sessions to a separate directory with error logs

## 🎯 Success Criteria

- ✅ Capture 50+ successful sessions across 2 devices
- ✅ <5% session failure rate (excluding intentional test failures)
- ✅ 100% metadata accuracy (all required fields present and valid)
- ✅ Compression reduces storage by >50%
- ✅ Device failures are isolated (one device crash doesn't stop the other)
- ✅ Sessions are named with UUIDv7 for chronological ordering

## 🗺️ Implementation Milestones

### Milestone 1.1: Project Setup & Structure

**Estimated Time**: 2-3 hours

#### Tasks
1. **Create directory structure**
   - Set up all folders from architecture doc
   - Ensure proper nesting for packages
   - Create `__init__.py` files in all Python packages

2. **Configure `pyproject.toml`**
   - Add project metadata (name, version, description)
   - List dependencies:
     - `appium-python-client>=3.0.0`
     - `opencv-python>=4.8.0`
     - `pillow>=10.0.0`
     - `uuid-utils>=0.7.0` (for UUIDv7)
     - `rich>=13.0.0` (CLI progress bars)
     - `pydantic>=2.0.0` (config validation)
     - `numpy>=1.24.0`

3. **Create `.gitignore`**
   - Ignore `sessions/` directory
   - Ignore `dataset/` directory
   - Ignore `models/` directory
   - Keep standard Python ignores (`.pyc`, `__pycache__`, etc.)
   - Keep `.egg-info`, `dist/`, `build/`

4. **Update `requirements.txt`**
   - Generate from `pyproject.toml` or maintain manually
   - Pin versions for reproducibility

5. **Initialize submodule structure**
   - Create basic structure in `libs/mobile-game-ad-detection/`
   - Add placeholder files (implementation comes in Phase 3)

#### Acceptance Criteria
- Project installs cleanly with `pip install -e .`
- All imports work without errors
- Git properly ignores data directories

#### Files to Create
- `automate-mobile-applications/__init__.py`
- `automate-mobile-applications/cli/__init__.py`
- `automate-mobile-applications/core/__init__.py`
- `automate-mobile-applications/appium/__init__.py`
- `automate-mobile-applications/actions/__init__.py`
- `automate-mobile-applications/data/__init__.py`
- `automate-mobile-applications/filtering/__init__.py`
- `automate-mobile-applications/utils/__init__.py`
- `.gitignore`
- Updated `pyproject.toml`

---

### Milestone 1.2: Configuration System

**Estimated Time**: 4-6 hours

#### Tasks
1. **Create `ConfigManager` class** (`core/config_manager.py`)
   - Load JSON files using built-in `json` module
   - Validate configs using Pydantic models
   - Provide typed access to config values
   - Handle missing files gracefully

2. **Define Pydantic models** (`utils/validators.py`)
   - `GlobalConfig` model
   - `GameConfig` model
   - `DeviceConfig` model
   - `FilteringConfig` model

3. **Create config templates**
   - `configs/global_config.json` with defaults
   - `configs/games/game_template.json` with all options documented
   - Use JSON format for all configurations

4. **Implement action loader** (`actions/action_loader.py`)
   - Parse JSON action definitions
   - Convert to Python dataclasses
   - Validate action parameters

5. **Create action schema** (`actions/action_schema.py`)
   - Define `BaseAction`, `TapAction`, `WaitAction`, `SwipeAction`, `WaitForElementAction`
   - Use dataclasses with type hints
   - Add validation methods

#### Acceptance Criteria
- Can load and parse all config files without errors
- Invalid configs raise clear validation errors
- Action sequences load correctly for each device
- Type hints provide autocomplete in IDE

#### Files to Create
- `automate-mobile-applications/core/config_manager.py`
- `automate-mobile-applications/utils/validators.py`
- `automate-mobile-applications/actions/action_schema.py`
- `automate-mobile-applications/actions/action_loader.py`
- `configs/global_config.json`
- `configs/games/game_template.json`

#### Code Example: ConfigManager
```python
from pydantic import BaseModel, Field
import json
from pathlib import Path

class GlobalConfig(BaseModel):
    appium_host: str = "localhost"
    appium_port: int = 4723
    capture_interval_seconds: float = Field(gt=0, le=10, default=1.0)
    session_max_duration_seconds: int = Field(ge=30, le=600, default=120)
    compress_sessions_on_completion: bool = True

class ConfigManager:
    def __init__(self, config_path: str = "configs/global_config.json"):
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> GlobalConfig:
        with open(self.config_path) as f:
            data = json.load(f)
        self._config = GlobalConfig(**data)
        return self._config
    
    @property
    def config(self) -> GlobalConfig:
        if self._config is None:
            self.load()
        return self._config
```

---

### Milestone 1.3: Appium Integration

**Estimated Time**: 6-8 hours

#### Tasks
1. **Refactor existing `appium_service.py`**
   - Ensure it supports single server instance
   - Add methods to start/stop server
   - Handle server already running case

2. **Create `DriverManager`** (`appium/driver_manager.py`)
   - Manage pool of device-specific WebDriver instances
   - Each device gets its own session (different capabilities)
   - Thread-safe access to drivers
   - Auto-reconnect on connection loss

3. **Implement `screen_capture.py`** (`appium/screen_capture.py`)
   - Capture high-resolution screenshots
   - Return as numpy array (for future model input)
   - Save as PNG with sequential numbering
   - Handle capture failures gracefully

4. **Build `adb_utils.py`** (`appium/adb_utils.py`)
   - `force_stop(package_name, device_id)`: Force stop app
   - `clear_app_data(package_name, device_id)`: Clear app data
   - `get_current_app(device_id)`: Get foreground app package
   - `get_connected_devices()`: List connected devices
   - Use subprocess to run ADB commands

5. **Update `appium_capabilities.py`**
   - Add device-specific capability builders
   - Include options for full reset, no reset
   - Set appropriate timeouts

#### Acceptance Criteria
- Appium server starts successfully
- Can create WebDriver sessions for 2+ devices simultaneously
- Screenshots save correctly as PNG files
- ADB commands execute successfully
- Can detect when app has crashed or moved to background

#### Files to Create/Modify
- `automate-mobile-applications/appium/driver_manager.py`
- `automate-mobile-applications/appium/screen_capture.py`
- `automate-mobile-applications/appium/adb_utils.py`
- Refactor `automate-mobile-applications/appium/appium_service.py`
- Update `automate-mobile-applications/appium/appium_capabilities.py`

#### Code Example: ADB Utils
```python
import subprocess
from typing import List, Optional

class ADBUtils:
    @staticmethod
    def force_stop(package_name: str, device_id: str) -> bool:
        """Force stop an app on a specific device"""
        try:
            cmd = ["adb", "-s", device_id, "shell", "am", "force-stop", package_name]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to force stop {package_name}: {e}")
            return False
    
    @staticmethod
    def clear_app_data(package_name: str, device_id: str) -> bool:
        """Clear app data on a specific device"""
        try:
            cmd = ["adb", "-s", device_id, "shell", "pm", "clear", package_name]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clear data for {package_name}: {e}")
            return False
    
    @staticmethod
    def get_current_app(device_id: str) -> Optional[str]:
        """Get the currently focused app package name"""
        try:
            cmd = ["adb", "-s", device_id, "shell", 
                   "dumpsys", "window", "windows", "|", "grep", "-E", "mCurrentFocus"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            # Parse output to extract package name
            # Example: "mCurrentFocus=Window{abc com.example.game/MainActivity}"
            return parse_package_from_output(result.stdout)
        except subprocess.CalledProcessError:
            return None
```

---

### Milestone 1.4: Session Management

**Estimated Time**: 6-8 hours

#### Tasks
1. **Implement `SessionDataManager`** (`data/session_data.py`)
   - Generate UUIDv7 session IDs
   - Create session directories
   - Save images with sequential numbering (0001.png, 0002.png, etc.)
   - Save per-frame JSON metadata
   - Save session-level metadata on completion
   - Thread-safe file writing

2. **Create metadata schemas** (`data/metadata_schema.py`)
   - Pydantic models for session metadata
   - Pydantic models for frame metadata
   - Pydantic models for error metadata
   - Validation and serialization helpers

3. **Implement compression** (`data/compression.py`)
   - Zip entire session folder after completion
   - Delete uncompressed folder after successful zip
   - Handle compression failures (keep original)
   - Use Python's `zipfile` module

4. **Implement failed session handling**
   - Move entire session folder to `sessions/failed/`
   - Create `error.json` with stack trace
   - Include metadata about failure point

5. **Create utility functions**
   - `get_session_path(session_id)`
   - `list_sessions()`
   - `get_session_metadata(session_id)`

#### Acceptance Criteria
- UUIDv7 IDs are chronologically sortable
- All metadata fields are populated correctly
- Compression works reliably
- Failed sessions are properly logged
- Can resume from any point (no data loss)

#### Files to Create
- `automate-mobile-applications/data/session_data.py`
- `automate-mobile-applications/data/metadata_schema.py`
- `automate-mobile-applications/data/compression.py`

#### Code Example: SessionDataManager
```python
from uuid_utils import uuid7
from pathlib import Path
import json
from datetime import datetime
import shutil
import zipfile

class SessionDataManager:
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self.failed_dir = self.sessions_dir / "failed"
        self.failed_dir.mkdir(exist_ok=True)
    
    def create_session(self, device_id: str, game: str, package_name: str) -> str:
        """Create a new session and return its ID"""
        session_id = str(uuid7())
        session_path = self.sessions_dir / session_id
        session_path.mkdir(exist_ok=True)
        
        # Initialize session metadata
        metadata = {
            "session_id": session_id,
            "device_id": device_id,
            "game": game,
            "package_name": package_name,
            "start_timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "in_progress"
        }
        
        with open(session_path / "session_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return session_id
    
    def save_frame(self, session_id: str, frame_number: int, 
                   image: np.ndarray, metadata: dict):
        """Save a single frame and its metadata"""
        session_path = self.sessions_dir / session_id
        
        # Save image
        image_path = session_path / f"{frame_number:04d}.png"
        cv2.imwrite(str(image_path), image)
        
        # Save metadata
        metadata_path = session_path / f"{frame_number:04d}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def complete_session(self, session_id: str, final_metadata: dict, compress: bool = True):
        """Mark session as complete and optionally compress"""
        session_path = self.sessions_dir / session_id
        
        # Update session metadata
        metadata_path = session_path / "session_metadata.json"
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        metadata.update(final_metadata)
        metadata["end_timestamp"] = datetime.utcnow().isoformat() + "Z"
        metadata["status"] = "completed"
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Compress if requested
        if compress:
            self._compress_session(session_id)
    
    def _compress_session(self, session_id: str):
        """Compress session folder to zip"""
        session_path = self.sessions_dir / session_id
        zip_path = self.sessions_dir / f"{session_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in session_path.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(session_path.parent))
        
        # Delete original folder after successful compression
        shutil.rmtree(session_path)
    
    def mark_failed(self, session_id: str, error: Exception):
        """Move session to failed directory and log error"""
        session_path = self.sessions_dir / session_id
        failed_path = self.failed_dir / session_id
        
        # Move session folder
        shutil.move(str(session_path), str(failed_path))
        
        # Create error log
        error_data = {
            "session_id": session_id,
            "failure_timestamp": datetime.utcnow().isoformat() + "Z",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc()
        }
        
        with open(failed_path / "error.json", "w") as f:
            json.dump(error_data, f, indent=2)
```

---

### Milestone 1.5: Device Worker

**Estimated Time**: 8-10 hours

#### Tasks
1. **Create `DeviceWorker` class** (`core/device_worker.py`)
   - Initialize with device ID and game config
   - Load device-specific action sequence
   - Execute setup actions to navigate to ad
   - Run capture loop at configured interval
   - Track session duration and enforce timeout
   - Handle Appium exceptions gracefully
   - Clean up device state after each session

2. **Implement action execution** (`actions/action_executor.py`)
   - Execute tap actions (by coordinates or resource_id)
   - Execute wait actions
   - Execute swipe actions
   - Execute wait_for_element actions
   - Return success/failure for each action
   - Log actions taken

3. **Implement capture loop**
   - Capture screenshot every N seconds
   - Extract UI hierarchy from Appium
   - Save frame + metadata
   - Track elapsed time
   - Check for timeout condition
   - Check for error conditions

4. **Add state tracking**
   - Track frames captured
   - Track actions taken
   - Track time in session
   - Detect when back in game (vs in ad)

5. **Add cleanup logic**
   - Force stop app
   - Clear app data
   - Reset device state
   - Close WebDriver session (if needed)

#### Acceptance Criteria
- Worker successfully navigates to ad using config
- Captures frames at specified interval
- Stops after max duration
- Cleans up properly on completion or failure
- Can run multiple workers in parallel without interference

#### Files to Create
- `automate-mobile-applications/core/device_worker.py`
- `automate-mobile-applications/actions/action_executor.py`

#### Code Example: DeviceWorker
```python
import time
import threading
from datetime import datetime
from typing import Optional

class DeviceWorker:
    def __init__(self, device_id: str, game_config: dict, 
                 global_config: dict, driver_manager: DriverManager,
                 session_manager: SessionDataManager):
        self.device_id = device_id
        self.game_config = game_config
        self.global_config = global_config
        self.driver_manager = driver_manager
        self.session_manager = session_manager
        self.action_executor = ActionExecutor()
        self.adb = ADBUtils()
        
    def run_sessions(self, num_sessions: int):
        """Run multiple sessions sequentially"""
        for i in range(num_sessions):
            try:
                self.run_single_session()
            except Exception as e:
                logger.error(f"Device {self.device_id} session failed: {e}")
                # Continue to next session
    
    def run_single_session(self):
        """Run a single data collection session"""
        session_id = None
        
        try:
            # Clean device state before starting
            self._prepare_device()
            
            # Create session
            session_id = self.session_manager.create_session(
                device_id=self.device_id,
                game=self.game_config["game"],
                package_name=self.game_config["package_name"]
            )
            
            # Get driver for this device
            driver = self.driver_manager.get_driver(self.device_id)
            
            # Execute setup actions to navigate to ad
            self._execute_setup_actions(driver)
            
            # Run capture loop
            self._capture_loop(driver, session_id)
            
            # Mark session complete
            self.session_manager.complete_session(
                session_id=session_id,
                final_metadata={
                    "completion_reason": "max_duration_reached",
                    "total_frames": self.frame_count
                },
                compress=self.global_config["compress_sessions_on_completion"]
            )
            
        except Exception as e:
            logger.error(f"Session {session_id} failed: {e}")
            if session_id:
                self.session_manager.mark_failed(session_id, error=e)
        
        finally:
            # Always clean up
            self._cleanup_device()
    
    def _prepare_device(self):
        """Prepare device for new session"""
        package_name = self.game_config["package_name"]
        self.adb.force_stop(package_name, self.device_id)
        self.adb.clear_app_data(package_name, self.device_id)
        time.sleep(2)
    
    def _execute_setup_actions(self, driver):
        """Execute game-specific setup actions"""
        actions = self.game_config["device_specific_actions"][self.device_id]["setup_steps"]
        
        for action_data in actions:
            action = parse_action(action_data)  # Convert dict to Action dataclass
            success = self.action_executor.execute(driver, action)
            
            if not success:
                raise Exception(f"Setup action failed: {action}")
    
    def _capture_loop(self, driver, session_id: str):
        """Main capture loop"""
        start_time = time.time()
        frame_number = 1
        max_duration = self.global_config["session_max_duration_seconds"]
        capture_interval = self.global_config["capture_interval_seconds"]
        
        while True:
            elapsed = time.time() - start_time
            
            # Check timeout
            if elapsed >= max_duration:
                logger.info(f"Session {session_id} reached max duration")
                break
            
            # Capture frame
            try:
                screenshot = driver.get_screenshot_as_png()
                image_array = cv2.imdecode(
                    np.frombuffer(screenshot, np.uint8), 
                    cv2.IMREAD_COLOR
                )
                
                # Get UI hierarchy
                ui_hierarchy = driver.page_source
                
                # Create metadata
                metadata = {
                    "session_id": session_id,
                    "frame_number": frame_number,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "seconds_into_ad": elapsed,
                    "actions_taken_so_far": 0,  # Will be > 0 in inference mode
                    "model_version": None,
                    "model_detections": [],
                    "action_taken": None,
                    "appium_ui_hierarchy": ui_hierarchy
                }
                
                # Save frame
                self.session_manager.save_frame(
                    session_id=session_id,
                    frame_number=frame_number,
                    image=image_array,
                    metadata=metadata
                )
                
                frame_number += 1
                
            except Exception as e:
                logger.error(f"Failed to capture frame: {e}")
                # Continue anyway
            
            # Wait for next capture
            time.sleep(capture_interval)
        
        self.frame_count = frame_number - 1
    
    def _cleanup_device(self):
        """Clean up device state"""
        package_name = self.game_config["package_name"]
        self.adb.force_stop(package_name, self.device_id)
```

---

### Milestone 1.6: Orchestrator & Parallel Execution

**Estimated Time**: 4-6 hours

#### Tasks
1. **Create `Orchestrator` class** (`core/orchestrator.py`)
   - Coordinate multiple device workers
   - Use ThreadPoolExecutor for parallel execution
   - Collect results from all workers
   - Handle worker failures gracefully
   - Provide progress reporting

2. **Implement thread-safe logging**
   - Per-device log files
   - Central log with device prefixes
   - Use Python's logging module

3. **Add progress tracking**
   - Track sessions completed per device
   - Track success/failure counts
   - Display real-time status

#### Acceptance Criteria
- Multiple devices run in parallel without conflicts
- One device failure doesn't stop others
- Progress is accurately reported
- Logs are readable and helpful

#### Files to Create
- `automate-mobile-applications/core/orchestrator.py`
- `automate-mobile-applications/utils/logger.py`

#### Code Example: Orchestrator
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

class Orchestrator:
    def __init__(self, global_config: GlobalConfig):
        self.global_config = global_config
        self.driver_manager = DriverManager(global_config)
        self.session_manager = SessionDataManager()
    
    def run_data_collection(self, game_config: dict, 
                           device_ids: List[str], 
                           num_sessions: int):
        """Run data collection across multiple devices"""
        
        results = {device_id: {"success": 0, "failed": 0} 
                   for device_id in device_ids}
        
        with ThreadPoolExecutor(max_workers=len(device_ids)) as executor:
            futures = {}
            
            # Submit worker for each device
            for device_id in device_ids:
                worker = DeviceWorker(
                    device_id=device_id,
                    game_config=game_config,
                    global_config=self.global_config,
                    driver_manager=self.driver_manager,
                    session_manager=self.session_manager
                )
                
                future = executor.submit(worker.run_sessions, num_sessions)
                futures[future] = device_id
            
            # Wait for completion
            with Progress() as progress:
                tasks = {device_id: progress.add_task(
                    f"[cyan]{device_id}", total=num_sessions
                ) for device_id in device_ids}
                
                for future in as_completed(futures):
                    device_id = futures[future]
                    try:
                        future.result()
                        results[device_id]["success"] += 1
                    except Exception as e:
                        results[device_id]["failed"] += 1
                        logger.error(f"Device {device_id} worker failed: {e}")
                    
                    progress.update(tasks[device_id], advance=1)
        
        return results
```

---

### Milestone 1.7: CLI - Collect Command

**Estimated Time**: 4-6 hours

#### Tasks
1. **Create CLI entry point** (`__main__.py`)
   - Use argparse or click for argument parsing
   - Support subcommands: collect, train, run, filter
   - Add global options (--verbose, --config, etc.)

2. **Implement `collect` command** (`cli/collect.py`)
   - Parse command-line arguments
   - Load configurations
   - Initialize orchestrator
   - Run data collection
   - Display results summary

3. **Add CLI utilities** (`cli/utils.py`)
   - Progress bars (using rich)
   - Status displays
   - Result summaries
   - Error formatting

#### Acceptance Criteria
- CLI is intuitive and well-documented
- Help text is clear and complete
- Progress is displayed in real-time
- Results summary is informative

#### Files to Create
- `automate-mobile-applications/__main__.py`
- `automate-mobile-applications/cli/collect.py`
- `automate-mobile-applications/cli/utils.py`

#### Code Example: CLI Entry Point
```python
# __main__.py
import argparse
from automate_mobile_applications.cli import collect, train, run, filter_cmd

def main():
    parser = argparse.ArgumentParser(
        description="Mobile Ad Automation System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect training data")
    collect_parser.add_argument("--config", required=True, help="Game config file")
    collect_parser.add_argument("--devices", help="Comma-separated device IDs (or 'all')")
    collect_parser.add_argument("--sessions", type=int, default=10, help="Sessions per device")
    collect_parser.add_argument("--duration", type=int, help="Max session duration override")
    
    # Other commands added later...
    
    args = parser.parse_args()
    
    if args.command == "collect":
        collect.run(args)
    # ... other commands
    
if __name__ == "__main__":
    main()
```

```python
# cli/collect.py
from automate_mobile_applications.core.config_manager import ConfigManager
from automate_mobile_applications.core.orchestrator import Orchestrator

def run(args):
    """Run data collection"""
    
    # Load configs
    config_manager = ConfigManager()
    global_config = config_manager.load_global()
    game_config = config_manager.load_game(args.config)
    
    # Determine devices
    if args.devices == "all":
        device_ids = [d["device_id"] for d in global_config.devices if d["enabled"]]
    else:
        device_ids = args.devices.split(",")
    
    # Create orchestrator
    orchestrator = Orchestrator(global_config)
    
    # Run collection
    print(f"Starting data collection for {game_config['game']}")
    print(f"Devices: {', '.join(device_ids)}")
    print(f"Sessions per device: {args.sessions}")
    
    results = orchestrator.run_data_collection(
        game_config=game_config,
        device_ids=device_ids,
        num_sessions=args.sessions
    )
    
    # Display results
    print("\n=== Results ===")
    total_success = sum(r["success"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    
    for device_id, result in results.items():
        print(f"{device_id}: {result['success']} successful, {result['failed']} failed")
    
    print(f"\nTotal: {total_success + total_failed} sessions | "
          f"Success: {total_success} | Failed: {total_failed}")
```

---

### Milestone 1.8: Testing & Validation

**Estimated Time**: 4-6 hours

#### Tasks
1. **Create test game config**
   - Use a real mobile game you have access to
   - Document all setup actions needed
   - Create configs for both test devices

2. **Test single device collection**
   - Run 5 sessions on one device
   - Verify all files created correctly
   - Check metadata accuracy
   - Verify compression works

3. **Test multi-device collection**
   - Run 10 sessions on 2 devices (5 each)
   - Verify parallel execution
   - Check for race conditions
   - Verify isolated error handling

4. **Test failure scenarios**
   - Intentionally cause Appium error
   - Verify session moved to failed/
   - Verify error.json created
   - Verify other device continues

5. **Test compression**
   - Verify zip files created
   - Verify original folders deleted
   - Verify can extract and read data
   - Check size reduction

6. **Manual review**
   - Review 10+ session folders
   - Verify images are captured correctly
   - Verify metadata is complete
   - Verify UUIDv7 ordering

#### Acceptance Criteria
- All success criteria from phase overview met
- No critical bugs found
- System is stable for extended runs
- Documentation is accurate

#### Validation Checklist
- [ ] 50+ successful sessions captured
- [ ] <5% failure rate (excluding intentional failures)
- [ ] All metadata fields populated correctly
- [ ] Compression reduces storage by >50%
- [ ] Device failures don't affect other devices
- [ ] UUIDv7 IDs are chronologically sorted
- [ ] Images are high quality and readable
- [ ] Appium UI hierarchy captured correctly
- [ ] Sessions can be resumed after crashes
- [ ] Clean device state between sessions

---

## 📦 Deliverables

Upon completion of Phase 1, you will have:

1. **Working data collection system**
   - Multi-device support
   - Configurable game navigation
   - Continuous frame capture
   - Automatic compression

2. **50-100 raw sessions**
   - Diverse ad content
   - Complete metadata
   - Ready for filtering

3. **Validated infrastructure**
   - Stable Appium integration
   - Reliable error handling
   - Clean separation of concerns

4. **Documentation**
   - README with setup instructions
   - Config templates with examples
   - CLI usage guide

## 🚀 Next Steps

After completing Phase 1:
- Proceed to [Phase 2: Image Filtering](./03-phase-2-filtering.md)
- Begin manual review of captured sessions
- Identify common ad patterns for labeling

---

**Status**: Ready to implement  
**Dependencies**: Appium installed, devices connected  
**Estimated Total Time**: 30-40 hours of focused development
