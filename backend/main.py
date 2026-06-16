import cv2
import mediapipe as mp
import os
from angles import calculate_angle, calculate_spine_angle, calculate_line_tilt

def draw_text(frame, text, position):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

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

cv2.waitKey(0)
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Processed video saved to: {output_path}")