import cv2
import mediapipe as mp
import os
from angles import calculate_angle, calculate_spine_angle, calculate_line_tilt, calculate_rotation_angle

def draw_text(
    frame,
    text,
    position,
    font_scale=0.65,
    text_color=(0, 0, 255),
    text_thickness=1,
    outline_thickness=3,
):
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        outline_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        text_color,
        text_thickness,
        cv2.LINE_AA,
    )

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

video_path = "sample_videos/swing.mp4"
output_path = "processed_videos/swing_with_pose.mp4"

os.makedirs("processed_videos", exist_ok=True)

cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

frame_number = 0
highest_wrist_y = float("inf")
top_backswing_frame = 0
wrist_y_by_frame = {}
top_backswing_angles = {}
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
            draw_text(frame, f"Left arm angle: {int(left_elbow_angle)} deg", (50, 50))

            left_wrist_y = left_wrist.y * height
            wrist_y_by_frame[frame_number] = left_wrist_y

            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

            shoulder = (right_shoulder.x * width, right_shoulder.y * height)
            elbow = (right_elbow.x * width, right_elbow.y * height)
            wrist = (right_wrist.x * width, right_wrist.y * height)

            right_elbow_angle = calculate_angle(shoulder, elbow, wrist)
            draw_text(frame, f"Right arm angle: {int(right_elbow_angle)} deg", (50, 100))

            # Spine angle
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

            draw_text(frame, f"Spine angle: {int(spine_angle)} deg", (50, 150))

            # Hip angle (average of left and right hip joint angles)
            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

            left_knee_point = (left_knee.x * width, left_knee.y * height)
            right_knee_point = (right_knee.x * width, right_knee.y * height)

            left_hip_angle = calculate_angle(left_shoulder_point, left_hip_point, left_knee_point)
            right_hip_angle = calculate_angle(right_shoulder_point, right_hip_point, right_knee_point)
            hip_angle = (left_hip_angle + right_hip_angle) / 2

            draw_text(frame, f"Hip angle: {int(hip_angle)} deg", (50, 200))

            # Shoulder tilt relative to horizontal
            shoulder_tilt = calculate_line_tilt(left_shoulder_point, right_shoulder_point)
            draw_text(frame, f"Shoulder tilt: {int(shoulder_tilt)} deg", (50, 250))

            shoulder_rotation = calculate_rotation_angle(
                left_shoulder_point,
                right_shoulder_point
            )

            hip_rotation = calculate_rotation_angle(
                left_hip_point,
                right_hip_point
            )

            x_factor = abs(shoulder_rotation - hip_rotation)

            draw_text(frame, f"Shoulder rotation: {int(shoulder_rotation)} deg", (50, 350))
            draw_text(frame, f"Hip rotation: {int(hip_rotation)} deg", (50, 400))
            draw_text(frame, f"X-factor: {int(x_factor)} deg", (50, 450))

            cv2.line(
                frame,
                (int(left_shoulder_point[0]), int(left_shoulder_point[1])),
                (int(right_shoulder_point[0]), int(right_shoulder_point[1])),
                (0, 0, 255),
                3
            )

            # Knee bend (average bend from left and right knees)
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

            left_ankle_point = (left_ankle.x * width, left_ankle.y * height)
            right_ankle_point = (right_ankle.x * width, right_ankle.y * height)

            left_knee_joint_angle = calculate_angle(left_hip_point, left_knee_point, left_ankle_point)
            right_knee_joint_angle = calculate_angle(right_hip_point, right_knee_point, right_ankle_point)

            left_knee_bend = max(0, 180 - left_knee_joint_angle)
            right_knee_bend = max(0, 180 - right_knee_joint_angle)
            knee_bend = (left_knee_bend + right_knee_bend) / 2

            draw_text(frame, f"Knee bend: {int(knee_bend)} deg", (50, 300))

            angle_metrics_by_frame[frame_number] = {
                "left_arm_angle": left_elbow_angle,
                "right_arm_angle": right_elbow_angle,
                "spine_angle": spine_angle,
                "hip_angle": hip_angle,
                "shoulder_tilt": shoulder_tilt,
                "knee_bend": knee_bend,
                "shoulder_rotation": shoulder_rotation,
                "hip_rotation": hip_rotation,
                "x_factor": x_factor,
            }

            if left_wrist_y < highest_wrist_y:
                highest_wrist_y = left_wrist_y
                top_backswing_frame = frame_number
                top_backswing_angles = angle_metrics_by_frame[frame_number]

            cv2.line(
                frame,
                (int(left_hip_point[0]), int(left_hip_point[1])),
                (int(left_knee_point[0]), int(left_knee_point[1])),
                (0, 0, 255),
                3
            )
            cv2.line(
                frame,
                (int(left_knee_point[0]), int(left_knee_point[1])),
                (int(left_ankle_point[0]), int(left_ankle_point[1])),
                (0, 0, 255),
                3
            )
            cv2.line(
                frame,
                (int(right_hip_point[0]), int(right_hip_point[1])),
                (int(right_knee_point[0]), int(right_knee_point[1])),
                (0, 0, 255),
                3
            )
            cv2.line(
                frame,
                (int(right_knee_point[0]), int(right_knee_point[1])),
                (int(right_ankle_point[0]), int(right_ankle_point[1])),
                (0, 0, 255),
                3
            )

            cv2.line(
                frame,
                (int(shoulder_midpoint[0]), int(shoulder_midpoint[1])),
                (int(hip_midpoint[0]), int(hip_midpoint[1])),
                (0, 0, 255),
                3
            )
            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        out.write(frame)

        cv2.imshow("Golf Swing Analyzer", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_number += 1

cap.release()
out.release()
cv2.destroyAllWindows()

setup_frame = None
takeaway_start_frame = None
takeaway_end_frame = None
top_window_start = None
top_window_end = None
downswing_start_frame = None
downswing_end_frame = None
impact_window_start = None
impact_window_end = None
follow_through_start_frame = None
phase_ranges = {}
phase_metrics_by_name = {}

if wrist_y_by_frame:
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

print(f"Top of backswing estimated at frame: {top_backswing_frame}")
if top_backswing_angles:
    print("Angles at top of backswing:")
    print(f"  Left arm angle: {int(top_backswing_angles['left_arm_angle'])} deg")
    print(f"  Right arm angle: {int(top_backswing_angles['right_arm_angle'])} deg")
    print(f"  Spine angle: {int(top_backswing_angles['spine_angle'])} deg")
    print(f"  Hip angle: {int(top_backswing_angles['hip_angle'])} deg")
    print(f"  Shoulder tilt: {int(top_backswing_angles['shoulder_tilt'])} deg")
    print(f"  Knee bend: {int(top_backswing_angles['knee_bend'])} deg")
    print(f"  Shoulder rotation: {int(top_backswing_angles['shoulder_rotation'])} deg")
    print(f"  Hip rotation: {int(top_backswing_angles['hip_rotation'])} deg")
    print(f"  X-factor: {int(top_backswing_angles['x_factor'])} deg")

if setup_frame is not None:
    print("Estimated swing phases (frame ranges):")
    print(f"  Setup: {setup_frame} to {setup_end_frame}")
    print(f"  Takeaway: {takeaway_start_frame} to {takeaway_end_frame}")
    print(f"  Top of backswing: {top_window_start} to {top_window_end}")
    print(f"  Downswing: {downswing_start_frame} to {downswing_end_frame}")
    print(f"  Impact: {impact_window_start} to {impact_window_end}")
    print(f"  Follow-through: {follow_through_start_frame} onward")

    available_metric_frames = sorted(angle_metrics_by_frame.keys())
    final_frame = available_metric_frames[-1] if available_metric_frames else None

    def get_phase_frame(start_frame, end_frame=None):
        if not available_metric_frames:
            return None

        if end_frame is None:
            candidates = [frame for frame in available_metric_frames if frame >= start_frame]
            if not candidates:
                return None
            return candidates[0]

        midpoint = (start_frame + end_frame) // 2
        candidates = [
            frame for frame in available_metric_frames
            if start_frame <= frame <= end_frame
        ]

        if candidates:
            return min(candidates, key=lambda frame: abs(frame - midpoint))

        return min(available_metric_frames, key=lambda frame: abs(frame - midpoint))

    phase_frames = {
        "Setup": get_phase_frame(setup_frame, setup_end_frame),
        "Takeaway": get_phase_frame(takeaway_start_frame, takeaway_end_frame),
        "Top of backswing": get_phase_frame(top_window_start, top_window_end),
        "Downswing": get_phase_frame(downswing_start_frame, downswing_end_frame),
        "Impact": get_phase_frame(impact_window_start, impact_window_end),
        "Follow-through": get_phase_frame(follow_through_start_frame, final_frame),
    }

    phase_ranges = {
        "Setup": (setup_frame, setup_end_frame),
        "Takeaway": (takeaway_start_frame, takeaway_end_frame),
        "Top of backswing": (top_window_start, top_window_end),
        "Downswing": (downswing_start_frame, downswing_end_frame),
        "Impact": (impact_window_start, impact_window_end),
        "Follow-through": (follow_through_start_frame, final_frame),
    }

    print("Angles at key swing phases:")
    for phase_name, phase_frame in phase_frames.items():
        if phase_frame is None:
            print(f"  {phase_name}: no valid landmark frame")
            continue

        metrics = angle_metrics_by_frame[phase_frame]
        phase_metrics_by_name[phase_name] = metrics
        print(f"  {phase_name} (frame {phase_frame}):")
        print(f"    Left arm angle: {int(metrics['left_arm_angle'])} deg")
        print(f"    Right arm angle: {int(metrics['right_arm_angle'])} deg")
        print(f"    Spine angle: {int(metrics['spine_angle'])} deg")
        print(f"    Hip angle: {int(metrics['hip_angle'])} deg")
        print(f"    Shoulder tilt: {int(metrics['shoulder_tilt'])} deg")
        print(f"    Knee bend: {int(metrics['knee_bend'])} deg")
        print(f"    Shoulder rotation: {int(metrics['shoulder_rotation'])} deg")
        print(f"    Hip rotation: {int(metrics['hip_rotation'])} deg")
        print(f"    X-factor: {int(metrics['x_factor'])} deg")

if phase_ranges and phase_metrics_by_name:
    overlay_input = cv2.VideoCapture(output_path)
    overlay_output_path = output_path.replace(".mp4", "_overlay_tmp.mp4")
    overlay_writer = cv2.VideoWriter(overlay_output_path, fourcc, fps, (width, height))

    overlay_frame_number = 0
    overlay_x = max(width // 2 + 20, width - 310)
    overlay_y_start = 40
    overlay_line_step = 24

    phase_colors = {
        "Setup": (255, 255, 0),
        "Takeaway": (0, 255, 255),
        "Top of backswing": (255, 0, 255),
        "Downswing": (0, 255, 0),
        "Impact": (0, 165, 255),
        "Follow-through": (255, 255, 255),
    }

    def get_current_phase(frame_idx):
        for phase_name, frame_range in phase_ranges.items():
            start_frame, end_frame = frame_range

            if end_frame is None:
                continue

            if start_frame <= frame_idx <= end_frame:
                return phase_name

        return None

    while overlay_input.isOpened():
        success, frame = overlay_input.read()

        if not success:
            break

        current_phase = get_current_phase(overlay_frame_number)

        if current_phase:
            phase_color = phase_colors.get(current_phase, (0, 0, 255))
            draw_text(
                frame,
                f"Phase: {current_phase}",
                (overlay_x, overlay_y_start),
                font_scale=0.55,
                text_color=phase_color,
                text_thickness=1,
                outline_thickness=2,
            )

            phase_metrics = phase_metrics_by_name.get(current_phase)
            if phase_metrics:
                draw_text(
                    frame,
                    f"L arm: {int(phase_metrics['left_arm_angle'])} deg",
                    (overlay_x, overlay_y_start + 1 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"R arm: {int(phase_metrics['right_arm_angle'])} deg",
                    (overlay_x, overlay_y_start + 2 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Spine: {int(phase_metrics['spine_angle'])} deg",
                    (overlay_x, overlay_y_start + 3 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Hip: {int(phase_metrics['hip_angle'])} deg",
                    (overlay_x, overlay_y_start + 4 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Sh tilt: {int(phase_metrics['shoulder_tilt'])} deg",
                    (overlay_x, overlay_y_start + 5 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Knee: {int(phase_metrics['knee_bend'])} deg",
                    (overlay_x, overlay_y_start + 6 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Sh rot: {int(phase_metrics['shoulder_rotation'])} deg",
                    (overlay_x, overlay_y_start + 7 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"Hip rot: {int(phase_metrics['hip_rotation'])} deg",
                    (overlay_x, overlay_y_start + 8 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )
                draw_text(
                    frame,
                    f"X-factor: {int(phase_metrics['x_factor'])} deg",
                    (overlay_x, overlay_y_start + 9 * overlay_line_step),
                    font_scale=0.5,
                    outline_thickness=2,
                )

        overlay_writer.write(frame)
        overlay_frame_number += 1

    overlay_input.release()
    overlay_writer.release()
    os.replace(overlay_output_path, output_path)

print(f"Processed video saved to: {output_path}")