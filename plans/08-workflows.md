# Implementation Workflows & Examples

## 🔄 Complete Workflows

### Workflow 1: Initial Data Collection

**Objective**: Capture first 50 sessions for manual annotation

```bash
# 1. Ensure devices are connected
adb devices

# 2. Start Appium server (in separate terminal)
appium --port 4723

# 3. Create game configuration
# Edit configs/games/my_game.json with game-specific setup actions

# 4. Run data collection
python -m automate-mobile-applications collect \
  --config configs/games/my_game.json \
  --devices emulator-5554,FA83M1A12345 \
  --sessions 25

# Output:
# Device emulator-5554: Session 1/25 [████████████████████] 45s COMPLETE
# Device FA83M1A12345:  Session 1/25 [████████████████████] 52s COMPLETE
# ...
# Total: 50 sessions | Successful: 47 | Failed: 3
#
# Sessions saved to: sessions/
# Compressed: Yes (47 .zip files)
# Failed sessions: sessions/failed/ (3 folders)
```

**Expected Results**:
- 50 session folders created
- Each with 30-120 frames (depends on duration)
- Compression reduced storage by ~50%
- Failed sessions isolated with error logs

---

### Workflow 2: Filter Images for Annotation

**Objective**: Select 200-300 diverse images from collected sessions

```bash
# 1. Run filtering pipeline
python -m automate-mobile-applications filter \
  --sessions-dir sessions/ \
  --output-dir dataset/to_annotate/ \
  --max-per-session 5 \
  --diversity-threshold 10

# Output:
# Processing 47 sessions...
# Session 01933b4e-7890-7123-abcd-123456789abc: Selected 5/45 images
# Session 01933b4f-1234-7456-ef01-987654321def: Selected 4/52 images
# ...
# 
# ╔═══════════════════════════════════════╗
# ║       Filtering Statistics            ║
# ╠═══════════════════════════════════════╣
# ║ Total sessions         │          47  ║
# ║ Total frames           │        2,150 ║
# ║ Selected for dataset   │         235  ║
# ║ Selection rate         │       10.9%  ║
# ╚═══════════════════════════════════════╝
#
# Images saved to: dataset/to_annotate/
# Manifest saved to: dataset/to_annotate/manifest.json

# 2. Review manifest
cat dataset/to_annotate/manifest.json | jq '.statistics'
```

**Expected Results**:
- 200-300 diverse images
- Manifest with source tracking
- Images ready for Label Studio import

---

### Workflow 3: Manual Annotation

**Objective**: Annotate filtered images in Label Studio

```bash
# 1. Start Label Studio
label-studio start

# 2. Create new project
# - Navigate to http://localhost:8080
# - Create project: "Mobile Ad Detection"
# - Import images from dataset/to_annotate/

# 3. Configure labeling interface
# - Use bounding box template
# - Add label presets:
#   * close_button-white-top_right
#   * close_button-black-top_left
#   * skip_button-gray-bottom_right
#   * video_content-generic-center

# 4. Annotate images
# - Draw bounding boxes around UI elements
# - Assign labels
# - Use keyboard shortcuts for speed

# 5. Export annotations
# - Export as JSON
# - Save to dataset/annotated/label_studio_export.json
```

**Annotation Guidelines**:
- Be consistent with label naming
- Draw tight bounding boxes
- Include partially visible buttons
- Skip frames with no detectable UI elements
- Document ambiguous cases

---

### Workflow 4: Train First Model

**Objective**: Train YOLOv8 model on annotated data

```bash
# 1. Prepare dataset (converts Label Studio export to YOLO format)
python -m automate-mobile-applications train \
  --dataset-dir dataset/annotated/ \
  --base-model yolov8n.pt \
  --epochs 100 \
  --device cpu

# Output:
# Loading dataset from dataset/annotated/label_studio_export.json
# Found 235 images with 4 labels:
#   - close_button-white-top_right: 89 instances
#   - close_button-black-top_left: 42 instances
#   - skip_button-gray-bottom_right: 67 instances
#   - video_content-generic-center: 37 instances
#
# Splitting data: 80% train, 15% val, 5% test
# Train: 188 images
# Val: 35 images
# Test: 12 images
#
# Starting training: model_v001
# Base model: yolov8n.pt
#
# Epoch 1/100:  [████░░░░░░] loss=1.234 mAP50=0.45
# Epoch 10/100: [████████░░] loss=0.876 mAP50=0.58
# ...
# Epoch 100/100: [██████████] loss=0.412 mAP50=0.78
#
# Training complete! (1847 seconds)
#
# ╔═════════════════════════════════════╗
# ║       Model Performance             ║
# ╠═════════════════════════════════════╣
# ║ mAP50          │             0.78   ║
# ║ mAP50-95       │             0.54   ║
# ║ Precision      │             0.82   ║
# ║ Recall         │             0.75   ║
# ╚═════════════════════════════════════╝
#
# Model saved to: models/model_v001/best.pt
# Metrics saved to: models/model_v001/metrics.json
```

**Expected Results**:
- Trained model weights: `models/model_v001/best.pt`
- Training metrics logged
- Validation results show reasonable performance

---

### Workflow 5: Run Inference Mode

**Objective**: Test model by running autonomous ad navigation

```bash
# 1. Run inference sessions
python -m automate-mobile-applications run \
  --model models/model_v001/best.pt \
  --config configs/games/my_game.json \
  --devices emulator-5554 \
  --sessions 20

# Output (real-time):
# Device emulator-5554 | Session 01933c10-abcd-7890-1234-567890abcdef
# Frame 1:  No detections (waiting)
# Frame 5:  No detections (waiting)
# Frame 12: Detected skip_button-gray-bottom_right (0.68) → WAIT (confidence too low)
# Frame 18: Detected close_button-white-top_right (0.91) → TAP (1080, 100) ✓
# Frame 19: Action successful, checking game state...
# Session complete: SUCCESS (back in game) ✓
#
# Device emulator-5554 | Session 01933c11-1234-abcd-5678-abcdef123456
# Frame 1:  No detections (waiting)
# ...
# Frame 45: Timeout reached
# Session complete: INCOMPLETE (max duration)
#
# ...
#
# ╔═══════════════════════════════════════╗
# ║         Inference Results             ║
# ╠═══════════════════════════════════════╣
# ║ Total sessions     │              20  ║
# ║ Successful         │              14  ║
# ║ Failed/Incomplete  │               6  ║
# ║ Success rate       │            70%   ║
# ╚═══════════════════════════════════════╝
#
# Sessions saved to: sessions/
# Decision logs included in session_metadata.json
```

**Expected Results**:
- 50-70% success rate with first model
- Detailed decision logs for each session
- Session data ready for review

---

### Workflow 6: Review Inference & Improve Model

**Objective**: Use model predictions to speed up annotation

```bash
# 1. Export successful inference sessions for review
python -m automate-mobile-applications filter \
  --sessions-dir sessions/ \
  --output-dir dataset/inference_review/ \
  --mode inference \
  --only-successful \
  --max-per-session 3

# Output:
# Filtering inference sessions...
# Found 14 successful sessions
# Selected 42 diverse frames with model predictions
# Exported to: dataset/inference_review/
# Label Studio import file: dataset/inference_review/label_studio_import.json

# 2. Import to Label Studio with pre-filled annotations
# - Import label_studio_import.json
# - Annotations already drawn based on model predictions
# - Review and correct errors (much faster than manual annotation)

# 3. Export corrected annotations
# - Export as JSON
# - Save to dataset/annotated/inference_corrected.json

# 4. Merge with existing dataset
python -m automate-mobile-applications dataset merge \
  --original dataset/annotated/label_studio_export.json \
  --new dataset/annotated/inference_corrected.json \
  --output dataset/annotated/combined.json

# 5. Retrain with larger dataset
python -m automate-mobile-applications train \
  --dataset-dir dataset/annotated/combined.json \
  --base-model yolov8n.pt \
  --epochs 100

# Output:
# Starting training: model_v002
# Dataset: 277 images (235 + 42 new)
# ...
# Training complete!
# mAP50: 0.82 (+0.04 improvement)
# Model saved to: models/model_v002/best.pt
```

**Expected Results**:
- Faster annotation through model assistance
- Larger training dataset (235 → 277 images)
- Improved model performance

---

### Workflow 7: Compare Model Versions

**Objective**: Get a rough sense of which model performs better (acknowledge comparison limitations)

> **⚠️ Technical Limitation**: Direct model comparison is challenging because:
> - Each session shows different ads (non-deterministic environment)
> - Multiple valid action sequences may exist
> - Success isn't always binary (partial success, stuck in different states)
> - Timing affects outcomes (same action at frame 10 vs frame 20)
>
> **Comparison Strategy**: Run both models on fresh sessions and compare aggregate success rates. This gives a *rough indication* of improvement but isn't a controlled comparison. Individual session-level comparison isn't meaningful since models see different ads.

```bash
# 1. Run model v001 on 20 fresh sessions
python -m automate-mobile-applications run \
  --model models/model_v001/best.pt \
  --config configs/games/my_game.json \
  --devices emulator-5554 \
  --sessions 20 \
  --label "model_v001_eval"

# Output:
# Success rate: 14/20 (70%)

# 2. Run model v002 on 20 different fresh sessions
python -m automate-mobile-applications run \
  --model models/model_v002/best.pt \
  --config configs/games/my_game.json \
  --devices emulator-5554 \
  --sessions 20 \
  --label "model_v002_eval"

# Output:
# Success rate: 16/20 (80%)

# 3. Compare aggregate metrics
python -m automate-mobile-applications report \
  --sessions-dir sessions/ \
  --filter-labels "model_v001_eval,model_v002_eval" \
  --output comparison_report.html

# Report shows:
# - Success rate by model (rough comparison)
# - Average confidence scores
# - Common failure modes for each
# - Detection frequency (which buttons found most often)
# - Average session duration
```

**Interpretation Notes**:
- Higher success rate across many sessions suggests better model, but...
- Statistical significance requires 50+ sessions per model
- Ad variance means direct comparison is noisy
- Focus on **failure mode analysis** rather than head-to-head metrics
- Best evaluation: Does v002 solve failures that v001 had?

**Better Approach for Phase 5**:
- Run 50+ sessions per model version
- Track failure types (stuck in store, timeout, wrong button)
- Manual review of 10-20 failed sessions per model
- Ask: "Does new model fail in the same ways or different ways?"

---

### Workflow 8: Multi-Game Testing

**Objective**: Validate model works across different games

```bash
# 1. Create configs for multiple games
# - configs/games/puzzle_game.json
# - configs/games/racing_game.json
# - configs/games/rpg_game.json

# 2. Run inference on each game
for game in puzzle_game racing_game rpg_game; do
  python -m automate-mobile-applications run \
    --model models/model_v002/best.pt \
    --config configs/games/${game}.json \
    --devices emulator-5554 \
    --sessions 10
done

# 3. Generate cross-game report
python -m automate-mobile-applications report \
  --sessions-dir sessions/ \
  --group-by game \
  --output multi_game_report.html

# Output:
# ╔═══════════════════════════════════════════╗
# ║     Success Rate by Game                  ║
# ╠═══════════════════════════════════════════╣
# ║ Puzzle Game   │  82%  (8/10 sessions)    ║
# ║ Racing Game   │  70%  (7/10 sessions)    ║
# ║ RPG Game      │  60%  (6/10 sessions)    ║
# ║ Overall       │  70%  (21/30 sessions)   ║
# ╚═══════════════════════════════════════════╝
```

---

## 🔧 Common Tasks

### Check System Status
```bash
# Check devices
adb devices

# Check Appium server
curl http://localhost:4723/status

# Check model versions
ls -lh models/

# Check dataset size
du -sh sessions/ dataset/ models/
```

### Clean Up Storage
```bash
# Compress old sessions
python -m automate-mobile-applications compress \
  --sessions-dir sessions/ \
  --older-than 7days

# Archive successful sessions
python -m automate-mobile-applications archive \
  --sessions-dir sessions/ \
  --output archive_2025_11.tar.gz \
  --only-successful
```

### Troubleshooting
```bash
# Check logs
tail -f sessions/<session-id>/session.log

# Verify session integrity
python -m automate-mobile-applications verify \
  --session-id <session-id>

# Re-run failed session
python -m automate-mobile-applications retry \
  --session-id <session-id>
```

---

## 📝 Configuration Examples

### Global Config (`configs/global_config.json`)
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

### Game Config (`configs/games/puzzle_game.json`)
```json
{
  "game": "Puzzle Adventure",
  "package_name": "com.example.puzzleadventure",
  "activity": ".MainActivity",
  "device_specific_actions": {
    "emulator-5554": {
      "setup_steps": [
        {
          "action": "tap",
          "x": 540,
          "y": 1500,
          "description": "Tap menu button"
        },
        {
          "action": "wait",
          "seconds": 2.0,
          "description": "Wait for menu animation"
        },
        {
          "action": "tap",
          "resource_id": "com.example.puzzleadventure:id/watch_ad_btn",
          "description": "Tap watch ad button"
        },
        {
          "action": "wait_for_element",
          "resource_id": "com.google.android.gms.ads.AdView",
          "timeout_seconds": 10,
          "description": "Wait for ad to load"
        }
      ]
    }
  },
  "metadata": {
    "typical_ad_duration_seconds": 30,
    "reward_type": "coins",
    "notes": "Ads appear after every 3 levels"
  }
}
```

---

**Status**: Reference guide for common workflows  
**Last Updated**: 2025-11-02
