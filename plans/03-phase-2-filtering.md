# Phase 2: Image Filtering & Dataset Preparation

**Goal**: Select best images from sessions for manual annotation  
**Status**: Not Started  
**Priority**: High - Needed before training  
**Prerequisites**: Phase 1 complete with 50+ sessions captured

## 📋 Overview

Raw session data contains many similar frames. This phase filters sessions to extract the most valuable images for training. The goal is to maximize visual diversity while minimizing redundancy, ensuring the model sees varied examples without wasting annotation effort on near-duplicates.

## 🎯 Success Criteria

- ✅ Visual diversity score >0.7 (manual subjective review)
- ✅ <2% duplicates in filtered set (perceptual hash check)
- ✅ 200-500 diverse images ready for annotation
- ✅ Configurable thresholds for easy experimentation
- ✅ Filter process is repeatable and documented
- ✅ Selected images maintain connection to source session

## 🗺️ Implementation Milestones

### Milestone 2.1: Frame Difference Analysis

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement frame diff calculator** (`filtering/frame_diff.py`)
   - Load consecutive frames from a session
   - Compute pixel-level differences (MSE, SSIM, or simple pixel diff)
   - Return difference score (0.0 = identical, 1.0 = completely different)
   - Support configurable diff methods

2. **Add preprocessing**
   - Resize images to consistent size for comparison
   - Optional: Convert to grayscale for faster processing
   - Optional: Apply Gaussian blur to reduce noise

3. **Create analysis tool**
   - Scan all frames in a session
   - Identify frames with significant changes from previous frame
   - Flag static sequences (e.g., 10+ frames with <5% difference)
   - Generate change timeline visualization

#### Acceptance Criteria
- Accurately detects static vs dynamic frames
- Configurable threshold parameter
- Fast enough to process 100+ frame sessions in <10 seconds

#### Files to Create
- `automate-mobile-applications/filtering/frame_diff.py`

#### Code Example
```python
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple

class FrameDiffCalculator:
    def __init__(self, threshold: float = 0.15, method: str = "mse"):
        self.threshold = threshold
        self.method = method
    
    def calculate_diff(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate difference between two images"""
        if self.method == "mse":
            return self._mse_diff(img1, img2)
        elif self.method == "ssim":
            return self._ssim_diff(img1, img2)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _mse_diff(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Mean Squared Error difference"""
        mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
        # Normalize to 0-1 range (assuming 8-bit images)
        return min(mse / (255 ** 2), 1.0)
    
    def _ssim_diff(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Structural Similarity Index (inverted to be a difference)"""
        from skimage.metrics import structural_similarity as ssim
        score = ssim(img1, img2, multichannel=True)
        return 1.0 - score  # Convert similarity to difference
    
    def analyze_session(self, session_path: Path) -> List[Tuple[int, float]]:
        """Analyze all frames in a session
        
        Returns:
            List of (frame_number, diff_from_previous)
        """
        image_files = sorted(session_path.glob("*.png"))
        results = []
        
        prev_img = None
        for img_file in image_files:
            frame_num = int(img_file.stem)
            img = cv2.imread(str(img_file))
            
            if prev_img is not None:
                diff = self.calculate_diff(prev_img, img)
                results.append((frame_num, diff))
            else:
                results.append((frame_num, 0.0))  # First frame has no diff
            
            prev_img = img
        
        return results
    
    def filter_by_change(self, session_path: Path) -> List[int]:
        """Get frame numbers that have significant change
        
        Returns frames where diff > threshold
        """
        diffs = self.analyze_session(session_path)
        return [frame_num for frame_num, diff in diffs if diff >= self.threshold]
```

---

### Milestone 2.2: Visual Diversity Analysis

**Estimated Time**: 6-8 hours

#### Tasks
1. **Implement feature extraction** (`filtering/visual_diversity.py`)
   - Extract visual features from images
   - Options:
     - Color histograms (fast, good for distinguishing different ad types)
     - HOG (Histogram of Oriented Gradients)
     - Pretrained CNN embeddings (ResNet, VGG) - slower but more semantic
   - Start with color histograms for MVP

2. **Implement clustering**
   - Use k-means clustering to group similar images
   - Configurable number of clusters
   - Select representative image from each cluster (closest to centroid)
   - Optional: Select multiple representatives if cluster is large

3. **Add diversity scoring**
   - Measure spread of selected images in feature space
   - Calculate inter-image distances
   - Provide diversity metrics for manual review

4. **Create session sampler**
   - Limit max images per session (avoid over-representing one session)
   - Prefer images from different temporal positions in session
   - Balance diversity vs quantity

#### Acceptance Criteria
- Clustering produces visually distinct groups
- Selected images cover different ad types/stages
- Process is deterministic (same input → same output)
- Fast enough to process 1000 images in <60 seconds

#### Files to Create
- `automate-mobile-applications/filtering/visual_diversity.py`

#### Code Example
```python
import cv2
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
from typing import List, Tuple

class VisualDiversitySelector:
    def __init__(self, n_clusters: int = 10, max_per_session: int = 50):
        self.n_clusters = n_clusters
        self.max_per_session = max_per_session
    
    def extract_features(self, image_path: Path) -> np.ndarray:
        """Extract visual features from image"""
        img = cv2.imread(str(image_path))
        
        # Color histogram features (3 channels x 32 bins = 96 features)
        hist_features = []
        for i in range(3):  # BGR channels
            hist = cv2.calcHist([img], [i], None, [32], [0, 256])
            hist = hist.flatten() / hist.sum()  # Normalize
            hist_features.extend(hist)
        
        return np.array(hist_features)
    
    def select_diverse_images(self, image_paths: List[Path]) -> List[Path]:
        """Select diverse subset of images using clustering"""
        
        # Limit input size
        if len(image_paths) > self.max_per_session:
            # Sample uniformly across session timeline
            indices = np.linspace(0, len(image_paths) - 1, 
                                 self.max_per_session, dtype=int)
            image_paths = [image_paths[i] for i in indices]
        
        # Extract features
        features = np.array([self.extract_features(p) for p in image_paths])
        
        # Cluster
        n_clusters = min(self.n_clusters, len(image_paths))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features)
        
        # Select representative from each cluster (closest to centroid)
        selected = []
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_features = features[cluster_mask]
            cluster_paths = [p for p, mask in zip(image_paths, cluster_mask) if mask]
            
            # Find image closest to centroid
            centroid = kmeans.cluster_centers_[cluster_id]
            distances = np.linalg.norm(cluster_features - centroid, axis=1)
            closest_idx = np.argmin(distances)
            
            selected.append(cluster_paths[closest_idx])
        
        return selected
    
    def calculate_diversity_score(self, image_paths: List[Path]) -> float:
        """Calculate diversity metric for selected images"""
        features = np.array([self.extract_features(p) for p in image_paths])
        
        # Calculate average pairwise distance
        distances = []
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                dist = np.linalg.norm(features[i] - features[j])
                distances.append(dist)
        
        return np.mean(distances) if distances else 0.0
```

---

### Milestone 2.3: Duplicate Detection

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement perceptual hashing** (`filtering/duplicate_detection.py`)
   - Use `imagehash` library (pHash or dHash)
   - Compute hash for each image
   - Compare hashes to find near-duplicates
   - Configurable similarity threshold

2. **Add deduplication logic**
   - Keep first occurrence, discard duplicates
   - Optional: Keep the highest quality version
   - Track which images were marked as duplicates

3. **Add cross-session deduplication**
   - Check for duplicates across all sessions
   - Useful when same ad appears in multiple sessions

#### Acceptance Criteria
- Accurately identifies duplicate frames
- No false positives (different images marked as duplicates)
- Fast enough to process 1000 images in <30 seconds

#### Files to Create
- `automate-mobile-applications/filtering/duplicate_detection.py`

#### Code Example
```python
import imagehash
from PIL import Image
from pathlib import Path
from typing import List, Set, Dict

class DuplicateDetector:
    def __init__(self, hash_size: int = 8, threshold: int = 5):
        """
        Args:
            hash_size: Size of perceptual hash
            threshold: Hamming distance threshold for considering duplicates
        """
        self.hash_size = hash_size
        self.threshold = threshold
    
    def compute_hash(self, image_path: Path) -> imagehash.ImageHash:
        """Compute perceptual hash for an image"""
        img = Image.open(image_path)
        return imagehash.phash(img, hash_size=self.hash_size)
    
    def find_duplicates(self, image_paths: List[Path]) -> Dict[Path, List[Path]]:
        """Find duplicate images
        
        Returns:
            Dict mapping each unique image to its duplicates
        """
        hashes = {path: self.compute_hash(path) for path in image_paths}
        
        duplicates = {}
        seen = set()
        
        for path1 in image_paths:
            if path1 in seen:
                continue
            
            hash1 = hashes[path1]
            dupes = []
            
            for path2 in image_paths:
                if path1 == path2 or path2 in seen:
                    continue
                
                hash2 = hashes[path2]
                distance = hash1 - hash2  # Hamming distance
                
                if distance <= self.threshold:
                    dupes.append(path2)
                    seen.add(path2)
            
            if dupes:
                duplicates[path1] = dupes
        
        return duplicates
    
    def remove_duplicates(self, image_paths: List[Path]) -> List[Path]:
        """Return list with duplicates removed"""
        duplicates = self.find_duplicates(image_paths)
        
        # Keep all non-duplicate images and one copy of each duplicate group
        keep = set(image_paths)
        for original, dupes in duplicates.items():
            for dupe in dupes:
                keep.discard(dupe)
        
        return list(keep)
```

---

### Milestone 2.4: Dataset Builder

**Estimated Time**: 4-6 hours

#### Tasks
1. **Implement `DatasetBuilder`** (`data/dataset_builder.py`)
   - Scan all session folders
   - Apply filtering pipeline:
     1. Frame difference filter (optional)
     2. Visual diversity selection
     3. Duplicate detection
   - Copy selected images to dataset directory
   - Copy corresponding metadata files
   - Create manifest JSON with selection details

2. **Add selection tracking**
   - Record which sessions images came from
   - Track filtering statistics (total → filtered counts)
   - Save selection criteria used

3. **Support incremental builds**
   - Don't re-process already filtered sessions
   - Add new sessions to existing dataset
   - Maintain selection consistency

4. **Add validation**
   - Verify all copied files are readable
   - Check metadata completeness
   - Validate image quality (not corrupted)

#### Acceptance Criteria
- Successfully filters 50+ sessions
- Produces 200-500 diverse images
- Manifest is complete and accurate
- Process is repeatable

#### Files to Create
- `automate-mobile-applications/data/dataset_builder.py`

#### Code Example
```python
from pathlib import Path
import shutil
import json
from typing import List, Dict
from datetime import datetime

class DatasetBuilder:
    def __init__(self, sessions_dir: Path, output_dir: Path, 
                 global_config: dict):
        self.sessions_dir = Path(sessions_dir)
        self.output_dir = Path(output_dir)
        self.config = global_config
        
        self.frame_diff = FrameDiffCalculator(
            threshold=global_config["filtering"]["frame_diff_threshold"]
        )
        self.diversity_selector = VisualDiversitySelector(
            n_clusters=global_config["filtering"]["visual_diversity_clusters"],
            max_per_session=global_config["filtering"]["max_images_per_session"]
        )
        self.duplicate_detector = DuplicateDetector()
    
    def build_dataset(self, use_frame_diff: bool = False) -> Dict:
        """Build filtered dataset from sessions
        
        Args:
            use_frame_diff: Whether to pre-filter using frame differences
        
        Returns:
            Statistics about the filtering process
        """
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all completed sessions (uncompressed or zipped)
        sessions = self._find_sessions()
        
        stats = {
            "total_sessions": len(sessions),
            "total_frames": 0,
            "selected_frames": 0,
            "filtered_by_frame_diff": 0,
            "filtered_by_diversity": 0,
            "filtered_by_duplicates": 0,
            "selection_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        all_selected = []
        
        # Process each session
        for session_path in sessions:
            images = sorted(session_path.glob("*.png"))
            stats["total_frames"] += len(images)
            
            # Optional: Pre-filter by frame difference
            if use_frame_diff:
                frame_numbers = self.frame_diff.filter_by_change(session_path)
                images = [session_path / f"{fn:04d}.png" for fn in frame_numbers]
                stats["filtered_by_frame_diff"] += len(frame_numbers)
            
            # Apply visual diversity selection
            selected = self.diversity_selector.select_diverse_images(images)
            all_selected.extend(selected)
        
        # Remove duplicates across all sessions
        all_selected = self.duplicate_detector.remove_duplicates(all_selected)
        stats["selected_frames"] = len(all_selected)
        
        # Copy selected images and metadata
        manifest = []
        for i, image_path in enumerate(all_selected, 1):
            # Copy image
            dest_image = self.output_dir / f"{i:04d}.png"
            shutil.copy(image_path, dest_image)
            
            # Copy metadata
            metadata_path = image_path.with_suffix('.json')
            if metadata_path.exists():
                dest_metadata = self.output_dir / f"{i:04d}.json"
                shutil.copy(metadata_path, dest_metadata)
            
            # Add to manifest
            manifest.append({
                "output_id": i,
                "source_path": str(image_path),
                "session_id": image_path.parent.name
            })
        
        # Save manifest
        manifest_data = {
            "statistics": stats,
            "config": self.config["filtering"],
            "images": manifest
        }
        
        with open(self.output_dir / "manifest.json", "w") as f:
            json.dump(manifest_data, f, indent=2)
        
        return stats
    
    def _find_sessions(self) -> List[Path]:
        """Find all session directories"""
        sessions = []
        
        # Find uncompressed sessions
        for item in self.sessions_dir.iterdir():
            if item.is_dir() and item.name != "failed":
                sessions.append(item)
        
        # TODO: Support reading from zip files
        
        return sessions
```

---

### Milestone 2.5: CLI - Filter Command

**Estimated Time**: 3-4 hours

#### Tasks
1. **Implement `filter` command** (`cli/filter.py`)
   - Parse command-line arguments
   - Load configuration
   - Run dataset builder
   - Display statistics and progress
   - Show diversity score

2. **Add options**
   - `--sessions-dir`: Input sessions directory
   - `--output-dir`: Output dataset directory
   - `--use-frame-diff`: Enable frame difference pre-filtering
   - `--diversity-threshold`: Override clustering config
   - `--max-per-session`: Override max images per session

3. **Add reporting**
   - Display before/after counts
   - Show filtering funnel (total → frame diff → diversity → duplicates → final)
   - Highlight sessions with most selected images
   - Show diversity score

#### Acceptance Criteria
- CLI is intuitive and informative
- Progress is shown for long operations
- Results are clearly presented
- Easy to experiment with different thresholds

#### Files to Create
- `automate-mobile-applications/cli/filter.py`

#### Code Example
```python
from rich.console import Console
from rich.table import Table
from automate_mobile_applications.data.dataset_builder import DatasetBuilder
from automate_mobile_applications.core.config_manager import ConfigManager

console = Console()

def run(args):
    """Run image filtering"""
    
    # Load config
    config_manager = ConfigManager()
    global_config = config_manager.load_global()
    
    # Override config with CLI args if provided
    if args.diversity_threshold:
        global_config["filtering"]["visual_diversity_clusters"] = args.diversity_threshold
    if args.max_per_session:
        global_config["filtering"]["max_images_per_session"] = args.max_per_session
    
    # Create dataset builder
    builder = DatasetBuilder(
        sessions_dir=args.sessions_dir or global_config["paths"]["sessions_dir"],
        output_dir=args.output_dir or global_config["paths"]["dataset_dir"],
        global_config=global_config
    )
    
    # Run filtering
    console.print(f"\n[bold cyan]Filtering images from sessions...[/bold cyan]\n")
    
    stats = builder.build_dataset(use_frame_diff=args.use_frame_diff)
    
    # Display results
    console.print("\n[bold green]✓ Filtering complete![/bold green]\n")
    
    table = Table(title="Filtering Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    
    table.add_row("Total sessions", str(stats["total_sessions"]))
    table.add_row("Total frames", str(stats["total_frames"]))
    if args.use_frame_diff:
        table.add_row("After frame diff filter", str(stats["filtered_by_frame_diff"]))
    table.add_row("Selected for dataset", str(stats["selected_frames"]))
    
    percentage = (stats["selected_frames"] / stats["total_frames"] * 100 
                  if stats["total_frames"] > 0 else 0)
    table.add_row("Selection rate", f"{percentage:.1f}%")
    
    console.print(table)
    
    console.print(f"\n[dim]Images saved to: {args.output_dir or global_config['paths']['dataset_dir']}[/dim]")
    console.print(f"[dim]Manifest saved to: manifest.json[/dim]\n")
```

---

### Milestone 2.6: Label Studio Integration Guide

**Estimated Time**: 2-3 hours

#### Tasks
1. **Create annotation guide** (`docs/annotation_guide.md`)
   - Document label naming convention
   - Provide examples of each label type
   - Create decision tree for ambiguous cases
   - Include screenshots

2. **Create Label Studio setup guide**
   - How to install Label Studio
   - How to create a project
   - How to import filtered images
   - How to configure labeling interface
   - How to export annotations

3. **Create labeling template**
   - Bounding box annotation config
   - Label presets for common button types
   - Keyboard shortcuts

4. **Document workflow**
   - Filter images → Import to Label Studio → Annotate → Export → Train

#### Acceptance Criteria
- Guide is clear and complete
- First-time user can follow it successfully
- Label conventions are well-defined
- Export format is compatible with training pipeline

#### Files to Create
- `docs/annotation_guide.md`
- `docs/label_studio_setup.md`
- `configs/label_studio_config.xml` (template)

---

### Milestone 2.7: Testing & Validation

**Estimated Time**: 3-4 hours

#### Tasks
1. **Test frame difference filtering**
   - Run on sessions with static sequences
   - Verify static frames filtered out
   - Check dynamic frames retained
   - Test different thresholds

2. **Test visual diversity selection**
   - Run on sessions with varied content
   - Manually review selected images
   - Verify diversity (no near-duplicates)
   - Test different cluster counts

3. **Test duplicate detection**
   - Create test set with known duplicates
   - Verify all duplicates found
   - Check for false positives
   - Test cross-session deduplication

4. **Test full pipeline**
   - Run filter command on 50+ sessions
   - Verify 200-500 images produced
   - Check manifest accuracy
   - Manually review 50 random images for quality

5. **Test configurability**
   - Change thresholds and re-run
   - Verify different results
   - Document effect of each parameter

#### Validation Checklist
- [ ] Frame diff correctly identifies static vs dynamic
- [ ] Visual diversity produces subjectively diverse set
- [ ] No obvious duplicates in final set
- [ ] 200-500 images ready for annotation
- [ ] Manifest contains all required information
- [ ] Images maintain quality (no corruption)
- [ ] Process is repeatable
- [ ] Different thresholds produce predictable results

---

## 📦 Deliverables

Upon completion of Phase 2, you will have:

1. **Filtering pipeline**
   - Frame difference analysis
   - Visual diversity selection
   - Duplicate detection
   - Complete CLI tool

2. **200-500 filtered images**
   - Diverse ad screenshots
   - Ready for annotation
   - Organized in dataset folder

3. **Manifest and documentation**
   - Selection statistics
   - Source session tracking
   - Annotation guides

4. **Label Studio setup**
   - Configuration template
   - Annotation guidelines
   - Import/export workflow

## 🚀 Next Steps

After completing Phase 2:
- Begin manual annotation in Label Studio
- Target 100-200 annotated images for first training
- Proceed to [Phase 3: Model Training](./04-phase-3-training.md) when annotations ready

---

**Status**: Ready to implement after Phase 1  
**Dependencies**: Phase 1 complete, 50+ sessions captured  
**Estimated Total Time**: 20-30 hours of development + manual annotation time
