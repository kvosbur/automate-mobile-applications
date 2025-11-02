# Phase 3: Model Training Pipeline

**Goal**: Train first YOLO model from annotated data  
**Status**: Not Started  
**Priority**: High - Core functionality  
**Prerequisites**: Phase 2 complete with 100-200 annotated images

## 📋 Overview

This phase moves into the submodule (`libs/mobile-game-ad-detection/`) to build the ML training pipeline. The goal is to train a lightweight YOLO model that can detect ad UI elements (close buttons, skip buttons, etc.) in under 2 seconds on MacBook CPU.

## 🎯 Success Criteria

- ✅ Train first model with 100-200 manually annotated images
- ✅ Inference time <2 seconds on MacBook CPU
- ✅ mAP50 >0.60 on validation set (reasonable for first model)
- ✅ Model versioning system works correctly
- ✅ Training metrics are tracked and saved
- ✅ Can load and use different model versions

## 🗺️ Implementation Milestones

### Milestone 3.1: Submodule Setup

**Estimated Time**: 2-3 hours

#### Tasks
1. Initialize submodule structure in `libs/mobile-game-ad-detection/`
2. Create `pyproject.toml` with dependencies:
   - `ultralytics>=8.0.0` (YOLO)
   - `torch>=2.0.0`, `torchvision>=0.15.0`
   - `opencv-python`, `pillow`, `numpy`, `pydantic`
3. Create package structure (inference/, training/, decision/, utils/)
4. Add README explaining submodule purpose

### Milestone 3.2: Dataset Preparation

**Estimated Time**: 4-6 hours

#### Tasks
1. **Implement Label Studio export parser** (`training/dataset_prep.py`)
   - Parse Label Studio JSON export
   - Extract bounding boxes and labels
   - Validate annotations

2. **Convert to YOLO format**
   - Create YOLO txt files (one per image)
   - Format: `<class_id> <x_center> <y_center> <width> <height>` (normalized 0-1)
   - Create class mapping file

3. **Create dataset.yaml**
   - Define paths (train/val/test)
   - List class names
   - Set image size

4. **Split data**
   - 80% train, 15% val, 5% test
   - Stratified split (ensure all classes in each set)
   - Random seed for reproducibility

#### Code Example: Dataset Prep
```python
import json
from pathlib import Path
from typing import List, Dict, Tuple
import random

class YOLODatasetPrep:
    def __init__(self, label_studio_export: Path, output_dir: Path):
        self.export_file = label_studio_export
        self.output_dir = Path(output_dir)
        self.classes = []
    
    def prepare(self, train_split: float = 0.8, val_split: float = 0.15):
        """Convert Label Studio export to YOLO format"""
        
        # Load annotations
        with open(self.export_file) as f:
            annotations = json.load(f)
        
        # Extract class names
        self._extract_classes(annotations)
        
        # Split data
        random.shuffle(annotations)
        n_train = int(len(annotations) * train_split)
        n_val = int(len(annotations) * val_split)
        
        train_data = annotations[:n_train]
        val_data = annotations[n_train:n_train + n_val]
        test_data = annotations[n_train + n_val:]
        
        # Convert each split
        self._convert_split(train_data, "train")
        self._convert_split(val_data, "val")
        self._convert_split(test_data, "test")
        
        # Create dataset.yaml
        self._create_dataset_yaml()
    
    def _convert_split(self, data: List[Dict], split_name: str):
        """Convert one split to YOLO format"""
        split_dir = self.output_dir / split_name
        images_dir = split_dir / "images"
        labels_dir = split_dir / "labels"
        
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        for item in data:
            image_path = Path(item["data"]["image"])
            image_id = image_path.stem
            
            # Copy image
            shutil.copy(image_path, images_dir / image_path.name)
            
            # Create label file
            label_path = labels_dir / f"{image_id}.txt"
            with open(label_path, "w") as f:
                for annotation in item["annotations"][0]["result"]:
                    if annotation["type"] == "rectanglelabels":
                        box = self._convert_bbox(annotation)
                        class_id = self.classes.index(annotation["value"]["rectanglelabels"][0])
                        f.write(f"{class_id} {box[0]} {box[1]} {box[2]} {box[3]}\n")
```

### Milestone 3.3: YOLO Training Wrapper

**Estimated Time**: 4-6 hours

#### Tasks
1. **Implement Trainer class** (`training/trainer.py`)
   - Wrap Ultralytics YOLO API
   - Support configurable hyperparameters
   - Handle CPU-only training
   - Add progress callbacks

2. **Create training config**
   - Default hyperparameters (epochs, batch size, image size, etc.)
   - Allow overrides via CLI

3. **Add training loop**
   - Load base model (yolov8n.pt)
   - Train on prepared dataset
   - Save checkpoints
   - Track metrics

#### Code Example
```python
from ultralytics import YOLO
from pathlib import Path

class AdDetectionTrainer:
    def __init__(self, dataset_yaml: Path, base_model: str = "yolov8n.pt"):
        self.dataset_yaml = dataset_yaml
        self.base_model = base_model
        self.model = YOLO(base_model)
    
    def train(self, epochs: int = 100, batch_size: int = 16, 
              image_size: int = 640, device: str = "cpu"):
        """Train the model"""
        
        results = self.model.train(
            data=str(self.dataset_yaml),
            epochs=epochs,
            batch=batch_size,
            imgsz=image_size,
            device=device,
            patience=20,  # Early stopping
            save=True,
            plots=True
        )
        
        return results
```

### Milestone 3.4: Model Versioning

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement version manager** (`training/model_versioning.py`)
   - Auto-increment version numbers
   - Create versioned folders (model_v001, model_v002, etc.)
   - Save model weights
   - Save training config
   - Generate metrics.json

2. **Add metadata tracking**
   - Dataset size and composition
   - Training hyperparameters
   - Performance metrics
   - Training time
   - Notes/comments

### Milestone 3.5: CLI - Train Command

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement train command** (in parent repo `cli/train.py`)
   - Calls into submodule
   - Parses arguments
   - Displays progress
   - Shows final metrics

2. **Add options**
   - `--dataset-dir`: Annotated images location
   - `--base-model`: YOLO base model (default: yolov8n.pt)
   - `--epochs`: Training epochs
   - `--device`: cpu or cuda

#### Example Usage
```bash
python -m automate-mobile-applications train \
  --dataset-dir dataset/annotated/ \
  --base-model yolov8n.pt \
  --epochs 100 \
  --device cpu
```

### Milestone 3.6: Model Evaluation

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement evaluator** (`training/evaluator.py`)
   - Run inference on test set
   - Calculate mAP, precision, recall
   - Generate confusion matrix
   - Create evaluation report

2. **Add visualization**
   - Plot precision-recall curves
   - Show example predictions
   - Highlight failure cases

### Milestone 3.7: Testing & Validation

**Estimated Time**: 4-6 hours

#### Tasks
1. Test full training pipeline with 100-200 images
2. Verify model saves correctly
3. Test inference speed on MacBook CPU
4. Validate metrics tracking
5. Test loading different model versions
6. Document training process

#### Validation Checklist
- [ ] Model trains without errors
- [ ] Inference time <2 seconds on MacBook CPU
- [ ] mAP50 >0.60 (or document if lower with reasoning)
- [ ] Model versioning works correctly
- [ ] metrics.json contains all required fields
- [ ] Can load and use trained model
- [ ] Training logs are clear and complete

## 📦 Deliverables

1. **Trained YOLO model** (model_v001)
2. **Training pipeline** (dataset prep → train → evaluate)
3. **Model versioning system**
4. **Performance benchmarks**
5. **Training documentation**

## 🚀 Next Steps

After completing Phase 3:
- Test model predictions manually
- Identify failure modes
- Proceed to [Phase 4: Inference Mode](./05-phase-4-inference.md)

---

**Status**: Ready to implement after Phase 2 + manual annotation  
**Dependencies**: 100-200 annotated images in Label Studio format  
**Estimated Total Time**: 20-30 hours of development + training time
