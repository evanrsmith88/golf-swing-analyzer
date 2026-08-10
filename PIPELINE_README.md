# Golf Swing Analysis Pipeline

## Overview

This pipeline processes golf swing videos and extracts biomechanical metrics for each swing phase, then computes statistics (mean ± std) by swing type (driver vs. iron).

## Files

- **`analyze_swing_pipeline.py`** - Main pipeline that processes all videos
- **`compute_statistics.py`** - Computes mean/std for each metric by phase and swing type
- **`swing_angles_data/all_swing_angles.json`** - Raw angle data for each video
- **`swing_angles_data/swing_statistics.json`** - Computed statistics

## How It Works

### Step 1: Video Classification
The pipeline automatically classifies videos based on filename:
- Contains "driver" → Driver swing
- Contains "iron" → Iron swing
- No classification → Unknown swing

Example filenames that work:
- `Tiger_Woods_Driver_Back.mov` ✓
- `Rory_McIlroy_Iron_Swing_Back.mov` ✓
- `random_video.mp4` → Unknown

### Step 2: Angle Extraction
For each video:
1. MediaPipe Pose detects 33 body landmarks per frame
2. Nine metrics are calculated for each frame:
   - Left arm angle (elbow joint)
   - Right arm angle (elbow joint)
   - Spine angle (vertical lean)
   - Hip angle (hip joint)
   - Shoulder tilt (rotation relative to horizontal)
   - Knee bend (joint angle)
   - Shoulder rotation (body line rotation)
   - Hip rotation (body line rotation)
   - X-factor (shoulder_rotation - hip_rotation)

3. Six swing phases are detected:
   - Setup
   - Takeaway
   - Top of backswing (detected by highest wrist position)
   - Downswing
   - Impact (detected by wrist returning to setup height)
   - Follow-through

### Step 3: Save Raw Data
All angles for each phase are saved to `swing_angles_data/all_swing_angles.json`:

```json
{
  "driver": {
    "Tiger_Woods_Driver_Back.mov": {
      "setup": { "left_arm_angle": 165.66, ... },
      "takeaway": { "left_arm_angle": 158.33, ... },
      ...
    }
  },
  "iron": {
    "Rory_McIlroy_Iron_Swing_Back.mov": {
      "setup": { ... },
      ...
    }
  }
}
```

### Step 4: Compute Statistics
Mean and standard deviation are calculated for each metric in each phase, grouped by:
- Driver swings
- Iron swings  
- All swings combined

Results saved to `swing_angles_data/swing_statistics.json`.

## Quick Start

### Process all videos and compute statistics:

```bash
cd backend
source ../.venv/bin/activate

# Generate raw angle data
python analyze_swing_pipeline.py

# Compute mean/std statistics
python compute_statistics.py
```

### Add new videos:

1. Place video file in `backend/sample_videos/`
2. Name it with "driver" or "iron" in the filename, e.g.:
   - `Brand_New_Driver_Swing.mov`
   - `Pro_Player_Iron_Back.mp4`
3. Re-run pipeline:
   ```bash
   python analyze_swing_pipeline.py
   python compute_statistics.py
   ```

The pipeline will automatically:
- Skip existing videos (no duplication)
- Include new videos in statistics
- Regenerate all JSON files with updated stats

## Understanding the Output

Sample console output after running `compute_statistics.py`:

```
DRIVER - SETUP:
  (based on 4 video(s))
  left_arm_angle: 165.66° ± 18.68°
  spine_angle: 21.84° ± 10.91°
  x_factor: 8.34° ± 3.73°
```

This means across 4 driver swing videos, at setup:
- Left arm angle averages 165.66° with ±18.68° variation
- Spine angle averages 21.84° with ±10.91° variation
- X-factor averages 8.34° with ±3.73° variation

## Key Insights from Pro Data

### Driver vs. Iron Form Differences

**Driver Setup:**
- More closed stance (hip angle ~141°)
- More shoulder rotation (21.35°)
- Higher x-factor (8.34°)

**Iron Setup:**
- More open stance (hip angle ~129°)
- Much more shoulder rotation (38.28°) - more forward tilt
- Much higher x-factor (22.85°) - more separation

**Top of Backswing:**
- Driver: Hip angle 164.78°, more hip extension
- Iron: Hip angle 158.78°, more restricted hip turn

This shows iron swings are typically more upright with greater shoulder-hip separation.

## Files Structure

```
golf-swing-analyzer/
├── backend/
│   ├── main.py (original analyzer with visualization)
│   ├── angles.py (angle calculation functions)
│   ├── analyze_swing_pipeline.py (batch processor)
│   ├── compute_statistics.py (statistics calculator)
│   ├── sample_videos/
│   │   ├── Tiger_Woods_Driver_Back.mov
│   │   ├── Rory_McIlroy_Iron_Swing_Back.mov
│   │   └── ... (other videos)
│   └── swing_angles_data/
│       ├── all_swing_angles.json (raw data)
│       └── swing_statistics.json (statistics)
```

## Next Steps

Future enhancements could include:
- Comparing individual golfer metrics against pro averages
- Detecting swing faults (e.g., over-rotation, early hip clearance)
- Generating personalized feedback reports
- Real-time swing analysis with webcam
- 3D reconstruction with multi-angle videos
