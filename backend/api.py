"""
FastAPI server for the Golf Swing Analyzer web app.

Run locally (from backend/):  uvicorn api:app --reload
"""
import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

import cv2
import imageio_ffmpeg
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from analyze_swing_pipeline import process_video
from compare_with_pros import build_feedback_rules, compare_phase, load_statistics

BASE_DIR = Path(__file__).parent
STATS = load_statistics(BASE_DIR / "swing_angles_data" / "swing_statistics.json")
RULES = build_feedback_rules()

VIDEO_DIR = Path(os.environ.get("VIDEO_DIR", Path(tempfile.gettempdir()) / "swing_videos"))
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB = 100
MAX_SECONDS = 20
PROCESS_MAX_HEIGHT = 720
VIDEO_TTL_SECONDS = 60 * 60
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
# "In pro range" means within 1.5 std of the pro mean, and never tighter than ±5°.
# The benchmark comes from only a few videos (some stds are < 1°) and 2D pose
# angles are noisy, so ±1 std flagged almost every metric, even for the pros.
PRO_RANGE_STDS = 1.5
MIN_PRO_RANGE = 5

# The few phases and metrics shown in v1. Lead arm assumes a right-handed golfer.
# Shoulder/hip rotation and x-factor are left out: angles.calculate_rotation_angle
# currently returns the same 2D line tilt, so those numbers aren't real rotation.
KEY_PHASES = {
    "setup": "Setup",
    "top_of_backswing": "Top of Backswing",
    "impact": "Impact",
}
KEY_METRICS = {
    "left_arm_angle": "Lead arm",
    "spine_angle": "Spine tilt",
    "hip_angle": "Hip angle",
    "knee_bend": "Knee bend",
}

# MediaPipe is memory-hungry; analyze one video at a time so a small server doesn't run out of RAM.
analysis_lock = threading.Lock()

app = FastAPI(title="Golf Swing Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(video: UploadFile = File(...), club: str = Form("all")):
    club = club.lower()
    if club not in STATS:
        raise HTTPException(400, f"club must be one of {list(STATS)}")

    extension = Path(video.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Please upload an MP4, MOV, or WebM video.")

    delete_old_videos()
    swing_id = uuid.uuid4().hex[:12]

    with tempfile.TemporaryDirectory() as work_dir:
        upload_path = Path(work_dir) / f"upload{extension}"
        save_upload(video, upload_path)
        check_duration(upload_path)

        raw_overlay_path = Path(work_dir) / "overlay_raw.mp4"
        with analysis_lock:
            phase_angles = process_video(
                str(upload_path),
                overlay_path=str(raw_overlay_path),
                max_height=PROCESS_MAX_HEIGHT,
            )

        if not phase_angles:
            raise HTTPException(
                422,
                "We couldn't find a golfer in this video. Film with your full body in frame and good light.",
            )

        convert_for_browser(raw_overlay_path, VIDEO_DIR / f"{swing_id}.mp4")

    result = build_result(phase_angles, club)
    result["id"] = swing_id
    result["videoUrl"] = f"/videos/{swing_id}.mp4"
    return result


def save_upload(video: UploadFile, destination: Path):
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    written = 0
    with open(destination, "wb") as f:
        while chunk := video.file.read(1024 * 1024):
            written += len(chunk)
            if written > max_bytes:
                raise HTTPException(413, f"Video is too large (max {MAX_UPLOAD_MB} MB).")
            f.write(chunk)


def check_duration(video_path: Path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise HTTPException(400, "Couldn't read that video file.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    if frames / fps > MAX_SECONDS:
        raise HTTPException(400, f"Please trim the video to {MAX_SECONDS} seconds or less.")


def convert_for_browser(source: Path, destination: Path):
    """OpenCV writes mp4v, which browsers won't play. Re-encode to H.264."""
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
        "-i", str(source),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        str(destination),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, timeout=120)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Fall back to the unconverted file; some browsers can still play it.
        shutil.copy(source, destination)


def delete_old_videos():
    cutoff = time.time() - VIDEO_TTL_SECONDS
    for path in VIDEO_DIR.glob("*.mp4"):
        if path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)


def metric_score(delta, pro_range):
    """100 inside the pro range, dropping 50 points per extra range-width outside it."""
    distance = abs(delta) / pro_range
    return 100 if distance <= 1 else max(0, round(100 - 50 * (distance - 1)))


def build_result(phase_angles, club):
    benchmark = STATS[club]
    phases = []
    strengths = []
    needs_work = []  # (distance from pro mean in stds, message)

    for phase_key, phase_name in KEY_PHASES.items():
        user_angles = phase_angles.get(phase_key)
        if not user_angles:
            continue
        user_angles = {k: v for k, v in user_angles.items() if k in KEY_METRICS}
        comparisons, _ = compare_phase(phase_key, user_angles, benchmark.get(phase_key), RULES)

        metrics = []
        for metric_key, label in KEY_METRICS.items():
            comparison = comparisons.get(metric_key)
            if not comparison:
                continue

            delta = comparison["delta_from_mean"]
            pro_range = max(comparison["pro_std"] * PRO_RANGE_STDS, MIN_PRO_RANGE)
            in_range = abs(delta) <= pro_range
            direction = "low" if delta < 0 else "high"
            metrics.append({
                "label": label,
                "value": round(comparison["user"]),
                "unit": "°",
                "proAvg": round(comparison["pro_mean"]),
                # Sent as proStd because the frontend draws the band as proAvg ± proStd
                "proStd": round(pro_range),
                "status": "good" if in_range else "warn",
                "note": None if in_range else ("Below pro range" if direction == "low" else "Above pro range"),
                "score": metric_score(delta, pro_range),
            })

            if in_range:
                strengths.append(f"{label} at {phase_name.lower()} matches the pros")
            else:
                rule = RULES.get(phase_key, {}).get(metric_key, {}).get(direction)
                message = rule or (
                    f"{label} at {phase_name.lower()} is "
                    f"{'lower' if direction == 'low' else 'higher'} than the pro range"
                )
                distance = abs(delta) / pro_range
                needs_work.append((distance, message))

        if metrics:
            phases.append({
                "key": phase_key,
                "name": phase_name,
                "score": round(sum(m["score"] for m in metrics) / len(metrics)),
                "metrics": metrics,
            })

    if not phases:
        raise HTTPException(422, "We couldn't measure the key swing positions in this video.")

    needs_work.sort(key=lambda item: item[0], reverse=True)
    return {
        "club": "Driver" if club == "driver" else "Iron" if club == "iron" else "All clubs",
        "score": round(sum(p["score"] for p in phases) / len(phases)),
        "topIssue": needs_work[0][1] if needs_work else "Your key positions match the pro range",
        "strengths": strengths[:3],
        "needsWork": [message for _, message in needs_work[:3]],
        "phases": phases,
    }
