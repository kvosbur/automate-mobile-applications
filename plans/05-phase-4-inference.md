# Phase 4: Inference Mode & Autonomous Navigation

**Goal**: Use trained model to navigate ads autonomously  
**Status**: Not Started  
**Priority**: High - Core functionality  
**Prerequisites**: Phase 3 complete with trained model

## 📋 Overview

This phase integrates the trained model into the data collection workflow. The system will now use the model to make decisions about where to tap, when to wait, and how to navigate ads autonomously. Importantly, it continues to capture all frames and metadata for future training improvements.

## 🎯 Success Criteria

- ✅ Autonomous ad navigation with >50% success rate (first model)
- ✅ Inference time consistently <2 seconds per frame
- ✅ Decision log accurately reflects model reasoning
- ✅ Session metadata includes model predictions
- ✅ Can identify when back in game vs stuck
- ✅ Graceful handling of low-confidence detections

## 🗺️ Implementation Milestones

### Milestone 4.1: Model Inference (Submodule)

**Estimated Time**: 4-6 hours

#### Tasks
1. **Implement Detector class** (`inference/detector.py`)
   - Load YOLO model from weights file
   - Run inference on numpy array images
   - Parse detection results
   - Filter by confidence threshold
   - Return structured detections

2. **Implement result parser** (`inference/result_parser.py`)
   - Convert YOLO output to standardized format
   - Extract labels, confidence scores, bounding boxes
   - Sort by confidence
   - Group by label type

#### Code Example
```python
from ultralytics import YOLO
import numpy as np
from typing import List, Dict

class AdDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """Run detection on an image
        
        Args:
            image: numpy array (H, W, C) in BGR format
        
        Returns:
            List of detections: [
                {
                    "label": "close_button-white-top_right",
                    "confidence": 0.91,
                    "bbox": [x1, y1, x2, y2]
                },
                ...
            ]
        """
        # Run inference
        results = self.model.predict(image, verbose=False)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf >= self.confidence_threshold:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    
                    detections.append({
                        "label": label,
                        "confidence": conf,
                        "bbox": bbox
                    })
        
        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x["confidence"], reverse=True)
        
        return detections
```

### Milestone 4.2: Decision Engine (Submodule)

**Estimated Time**: 6-8 hours

#### Tasks
1. **Implement strategy classes** (`decision/strategy.py`)
   - Define action selection strategies
   - Priority: close buttons > skip buttons > wait
   - Confidence-based thresholding
   - Time-based logic (e.g., "wait at least 5s before trying to close")

2. **Implement state tracker** (`decision/state_tracker.py`)
   - Track session state (loading, playing, closeable)
   - Remember previous actions
   - Detect loops (same action failing repeatedly)

3. **Create decision engine** (`decision/engine.py`)
   - Combine detections + state → action
   - Support different strategies
   - Provide reasoning for decisions

#### Code Example
```python
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class RecommendedAction:
    action_type: str  # "tap", "wait", "back"
    coordinates: Optional[tuple] = None
    reason: str = ""
    confidence: float = 0.0

class DecisionEngine:
    def __init__(self, confidence_thresholds: Dict[str, float]):
        self.thresholds = confidence_thresholds
        self.state = {"actions_taken": 0, "seconds_elapsed": 0}
    
    def decide(self, detections: List[Dict], 
               current_state: Dict) -> RecommendedAction:
        """Decide what action to take
        
        Args:
            detections: Model detections
            current_state: Session state (time, actions, etc.)
        
        Returns:
            Recommended action with reasoning
        """
        self.state.update(current_state)
        
        # Wait minimum time before trying to close (avoid mis-detections)
        if self.state["seconds_elapsed"] < 5:
            return RecommendedAction(
                action_type="wait",
                reason="Waiting minimum ad duration"
            )
        
        # Look for close buttons (highest priority)
        close_buttons = [d for d in detections 
                        if "close_button" in d["label"].lower()]
        
        for detection in close_buttons:
            threshold = self.thresholds.get("close_button", 0.7)
            if detection["confidence"] >= threshold:
                # Calculate tap point (center of bbox)
                bbox = detection["bbox"]
                x = int((bbox[0] + bbox[2]) / 2)
                y = int((bbox[1] + bbox[3]) / 2)
                
                return RecommendedAction(
                    action_type="tap",
                    coordinates=(x, y),
                    reason=f"Detected {detection['label']} with confidence {detection['confidence']:.2f}",
                    confidence=detection["confidence"]
                )
        
        # Look for skip buttons
        skip_buttons = [d for d in detections 
                       if "skip_button" in d["label"].lower()]
        
        for detection in skip_buttons:
            threshold = self.thresholds.get("skip_button", 0.75)
            if detection["confidence"] >= threshold:
                bbox = detection["bbox"]
                x = int((bbox[0] + bbox[2]) / 2)
                y = int((bbox[1] + bbox[3]) / 2)
                
                return RecommendedAction(
                    action_type="tap",
                    coordinates=(x, y),
                    reason=f"Detected {detection['label']} with confidence {detection['confidence']:.2f}",
                    confidence=detection["confidence"]
                )
        
        # No high-confidence detections, wait
        return RecommendedAction(
            action_type="wait",
            reason="No high-confidence buttons detected"
        )
```

### Milestone 4.3: Inference Worker Integration

**Estimated Time**: 6-8 hours

#### Tasks
1. **Extend DeviceWorker** for inference mode (`core/device_worker.py`)
   - Add inference mode flag
   - Initialize detector and decision engine
   - Modify capture loop to:
     - Run model inference
     - Get recommended action
     - Execute action via Appium
     - Log decision in metadata

2. **Add outcome detection**
   - Check if back in game (via ADB or Appium)
   - Detect if stuck in app store
   - Track reward received (game-specific)

3. **Update session metadata**
   - Include decision log
   - Track final outcome
   - Record success/failure

#### Code Example: Inference Loop
```python
def _inference_capture_loop(self, driver, session_id: str):
    """Capture loop with model inference"""
    
    # Initialize detector and decision engine
    detector = AdDetector(
        model_path=self.model_path,
        confidence_threshold=0.5
    )
    decision_engine = DecisionEngine(
        confidence_thresholds={"close_button": 0.7, "skip_button": 0.75}
    )
    
    start_time = time.time()
    frame_number = 1
    actions_taken = 0
    decision_log = []
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed >= self.max_duration:
            break
        
        # Capture frame
        screenshot = driver.get_screenshot_as_png()
        image_array = cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)
        
        # Run inference
        detections = detector.detect(image_array)
        
        # Decide action
        current_state = {
            "seconds_elapsed": elapsed,
            "actions_taken": actions_taken,
            "frame_number": frame_number
        }
        recommended_action = decision_engine.decide(detections, current_state)
        
        # Log decision
        decision_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "frame_number": frame_number,
            "decision": recommended_action.action_type,
            "reason": recommended_action.reason
        }
        
        if recommended_action.coordinates:
            decision_entry["coordinates"] = list(recommended_action.coordinates)
        
        if detections:
            decision_entry["model_detections"] = detections
        
        decision_log.append(decision_entry)
        
        # Execute action
        action_success = False
        if recommended_action.action_type == "tap":
            try:
                driver.tap([recommended_action.coordinates])
                action_success = True
                actions_taken += 1
                
                # Wait a bit after tapping
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to execute tap: {e}")
        
        # Save frame metadata
        metadata = {
            "session_id": session_id,
            "frame_number": frame_number,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "seconds_into_ad": elapsed,
            "actions_taken_so_far": actions_taken,
            "model_version": self.model_version,
            "model_detections": detections,
            "action_taken": recommended_action.action_type if action_success else None,
            "action_coordinates": list(recommended_action.coordinates) if recommended_action.coordinates else None,
            "action_success": action_success
        }
        
        self.session_manager.save_frame(session_id, frame_number, image_array, metadata)
        
        frame_number += 1
        time.sleep(self.capture_interval)
    
    # Determine final outcome
    final_outcome = self._check_final_outcome(driver)
    
    return decision_log, final_outcome
```

### Milestone 4.4: CLI - Run Command

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement run command** (`cli/run.py`)
   - Parse arguments
   - Load model and game config
   - Run orchestrator in inference mode
   - Display real-time metrics

2. **Add live reporting**
   - Show detections as they happen
   - Display actions taken
   - Track success rate
   - Show timing metrics

#### Example Usage
```bash
python -m automate-mobile-applications run \
  --model models/model_v001/best.pt \
  --config configs/games/puzzle_game.yaml \
  --devices emulator-5554 \
  --sessions 20
```

### Milestone 4.5: Annotation Review Workflow

**Estimated Time**: 4-6 hours

#### Tasks
1. **Create export tool** for inference sessions
   - Filter successful sessions
   - Extract frames with model predictions
   - Export to Label Studio format with pre-filled labels
   - User reviews and corrects

2. **Add review CLI command**
   - Select best inference sessions
   - Generate Label Studio import file
   - Document review workflow

3. **Implement feedback loop**
   - Corrected annotations → dataset
   - Retrain model
   - Deploy new version

### Milestone 4.6: Testing & Validation

**Estimated Time**: 6-8 hours

#### Tasks
1. Run 20+ inference sessions
2. Measure success rate
3. Analyze decision logs
4. Identify common failure modes
5. Test on different games/ad types
6. Benchmark inference speed

#### Validation Checklist
- [ ] Success rate >50% (document actual rate)
- [ ] Inference consistently <2 seconds
- [ ] Decision logs are clear and accurate
- [ ] Model predictions saved correctly
- [ ] Can detect when back in game
- [ ] Handles low-confidence cases gracefully
- [ ] No infinite loops or crashes
- [ ] Works across multiple sessions

## 📦 Deliverables

1. **Autonomous navigation system**
2. **Inference session data with model predictions**
3. **Decision logs and outcome tracking**
4. **Success rate metrics dashboard**
5. **Annotation review workflow**

## 🚀 Next Steps

After completing Phase 4:
- Analyze failure modes
- Review inference sessions and correct annotations
- Retrain model with additional data
- Proceed to [Phase 5: Iterative Improvement](./06-phase-5-iteration.md)

---

**Status**: Ready to implement after Phase 3  
**Dependencies**: Trained model from Phase 3  
**Estimated Total Time**: 30-40 hours of development + testing
