import cv2
import mediapipe as mp
import os
import json
from pathlib import Path
from angles import calculate_angle, calculate_spine_angle, calculate_line_tilt, calculate_rotation_angle

mp_pose = mp.solutions.pose

def extract_swing_type_from_filename(filename):
    """
    Extract driver/iron from filename.
    Returns 'driver', 'iron', or 'unknown'
    """
    filename_lower = filename.lower()
    if 'driver' in filename_lower:
        return 'driver'
    elif 'iron' in filename_lower:
        return 'iron'
    else:
        return 'unknown'

def process_video(video_path):
    """
    Process a single video and extract phase angles.
    Returns a dict with phase angles or None if processing fails.
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_number = 0
    highest_wrist_y = float("inf")
    top_backswing_frame = 0
    wrist_y_by_frame = {}
    angle_metrics_by_frame = {}

    with mp_pose.Pose() as pose:
        while cap.isOpened():
            success, frame = cap.read()

            if not success:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

                shoulder = (left_shoulder.x * width, left_shoulder.y * height)
                elbow = (left_elbow.x * width, left_elbow.y * height)
                wrist = (left_wrist.x * width, left_wrist.y * height)

                left_elbow_angle = calculate_angle(shoulder, elbow, wrist)

                left_wrist_y = left_wrist.y * height
                wrist_y_by_frame[frame_number] = left_wrist_y

                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
                right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

                shoulder = (right_shoulder.x * width, right_shoulder.y * height)
                elbow = (right_elbow.x * width, right_elbow.y * height)
                wrist = (right_wrist.x * width, right_wrist.y * height)

                right_elbow_angle = calculate_angle(shoulder, elbow, wrist)

                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

                left_shoulder_point = (left_shoulder.x * width, left_shoulder.y * height)
                right_shoulder_point = (right_shoulder.x * width, right_shoulder.y * height)
                left_hip_point = (left_hip.x * width, left_hip.y * height)
                right_hip_point = (right_hip.x * width, right_hip.y * height)

                shoulder_midpoint = (
                    (left_shoulder_point[0] + right_shoulder_point[0]) / 2,
                    (left_shoulder_point[1] + right_shoulder_point[1]) / 2
                )

                hip_midpoint = (
                    (left_hip_point[0] + right_hip_point[0]) / 2,
                    (left_hip_point[1] + right_hip_point[1]) / 2
                )

                spine_angle = calculate_spine_angle(shoulder_midpoint, hip_midpoint)

                left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

                left_knee_point = (left_knee.x * width, left_knee.y * height)
                right_knee_point = (right_knee.x * width, right_knee.y * height)

                left_hip_angle = calculate_angle(left_shoulder_point, left_hip_point, left_knee_point)
                right_hip_angle = calculate_angle(right_shoulder_point, right_hip_point, right_knee_point)
                hip_angle = (left_hip_angle + right_hip_angle) / 2

                shoulder_tilt = calculate_line_tilt(left_shoulder_point, right_shoulder_point)

                shoulder_rotation = calculate_rotation_angle(
                    left_shoulder_point,
                    right_shoulder_point
                )

                hip_rotation = calculate_rotation_angle(
                    left_hip_point,
                    right_hip_point
                )

                x_factor = abs(shoulder_rotation - hip_rotation)

                left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

                left_ankle_point = (left_ankle.x * width, left_ankle.y * height)
                right_ankle_point = (right_ankle.x * width, right_ankle.y * height)

                left_knee_joint_angle = calculate_angle(left_hip_point, left_knee_point, left_ankle_point)
                right_knee_joint_angle = calculate_angle(right_hip_point, right_knee_point, right_ankle_point)

                left_knee_bend = max(0, 180 - left_knee_joint_angle)
                right_knee_bend = max(0, 180 - right_knee_joint_angle)
                knee_bend = (left_knee_bend + right_knee_bend) / 2

                angle_metrics_by_frame[frame_number] = {
                    "left_arm_angle": float(left_elbow_angle),
                    "right_arm_angle": float(right_elbow_angle),
                    "spine_angle": float(spine_angle),
                    "hip_angle": float(hip_angle),
                    "shoulder_tilt": float(shoulder_tilt),
                    "knee_bend": float(knee_bend),
                    "shoulder_rotation": float(shoulder_rotation),
                    "hip_rotation": float(hip_rotation),
                    "x_factor": float(x_factor),
                }

                if left_wrist_y < highest_wrist_y:
                    highest_wrist_y = left_wrist_y
                    top_backswing_frame = frame_number

            frame_number += 1

    cap.release()

    if not wrist_y_by_frame or not angle_metrics_by_frame:
        print(f"No landmarks detected in video: {video_path}")
        return None

    valid_frames = sorted(wrist_y_by_frame.keys())
    setup_frame = valid_frames[0]
    setup_wrist_y = wrist_y_by_frame[setup_frame]

    post_top_frames = [frame for frame in valid_frames if frame > top_backswing_frame]

    if post_top_frames:
        impact_frame = min(
            post_top_frames,
            key=lambda frame: abs(wrist_y_by_frame[frame] - setup_wrist_y)
        )
    else:
        impact_frame = top_backswing_frame

    backswing_span = max(1, top_backswing_frame - setup_frame)
    setup_end_frame = setup_frame + int(0.15 * backswing_span)

    takeaway_start_frame = setup_end_frame + 1
    takeaway_end_frame = max(takeaway_start_frame, top_backswing_frame - 3)

    top_window_start = max(setup_frame, top_backswing_frame - 2)
    top_window_end = top_backswing_frame + 2

    downswing_start_frame = top_window_end + 1
    downswing_end_frame = max(downswing_start_frame, impact_frame - 3)

    impact_window_start = max(downswing_start_frame, impact_frame - 2)
    impact_window_end = impact_frame + 2

    follow_through_start_frame = impact_window_end + 1

    phase_ranges = {
        "setup": (setup_frame, setup_end_frame),
        "takeaway": (takeaway_start_frame, takeaway_end_frame),
        "top_of_backswing": (top_window_start, top_window_end),
        "downswing": (downswing_start_frame, downswing_end_frame),
        "impact": (impact_window_start, impact_window_end),
        "follow_through": (follow_through_start_frame, valid_frames[-1] if valid_frames else follow_through_start_frame),
    }

    available_metric_frames = sorted(angle_metrics_by_frame.keys())
    
    def get_phase_frame(start_frame, end_frame):
        if not available_metric_frames:
            return None

        midpoint = (start_frame + end_frame) // 2
        candidates = [
            frame for frame in available_metric_frames
            if start_frame <= frame <= end_frame
        ]

        if candidates:
            return min(candidates, key=lambda frame: abs(frame - midpoint))

        return min(available_metric_frames, key=lambda frame: abs(frame - midpoint))

    phase_angles = {}
    for phase_name, (start_frame, end_frame) in phase_ranges.items():
        phase_frame = get_phase_frame(start_frame, end_frame)
        if phase_frame is not None and phase_frame in angle_metrics_by_frame:
            phase_angles[phase_name] = angle_metrics_by_frame[phase_frame]
        else:
            phase_angles[phase_name] = None

    return phase_angles

def process_all_videos(sample_videos_dir="sample_videos", output_dir="swing_angles_data"):
    """
    Process all videos in sample_videos and save phase angles to JSON.
    Organizes by swing type (driver/iron).
    """
    os.makedirs(output_dir, exist_ok=True)

    video_files = sorted([f for f in os.listdir(sample_videos_dir) if f.endswith(('.mp4', '.mov'))])

    results = {
        "driver": {},
        "iron": {},
        "unknown": {}
    }

    for video_file in video_files:
        if video_file == "swing.mp4":
            continue

        video_path = os.path.join(sample_videos_dir, video_file)
        swing_type = extract_swing_type_from_filename(video_file)

        print(f"Processing {video_file} ({swing_type})...")
        phase_angles = process_video(video_path)

        if phase_angles:
            results[swing_type][video_file] = phase_angles
            print(f"  ✓ Successfully extracted angles from {video_file}")
        else:
            print(f"  ✗ Failed to process {video_file}")

    output_file = os.path.join(output_dir, "all_swing_angles.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")
    print(f"  Driver swings: {len(results['driver'])}")
    print(f"  Iron swings: {len(results['iron'])}")
    print(f"  Unknown: {len(results['unknown'])}")

    return results

if __name__ == "__main__":
    process_all_videos()
