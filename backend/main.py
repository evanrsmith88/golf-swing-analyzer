import cv2
import mediapipe as mp
import os
from angles import calculate_angle

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

            cv2.putText(
                frame,
                f"Left elbow: {int(left_elbow_angle)} deg",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

            shoulder = (right_shoulder.x * width, right_shoulder.y * height)
            elbow = (right_elbow.x * width, right_elbow.y * height)
            wrist = (right_wrist.x * width, right_wrist.y * height)

            right_elbow_angle = calculate_angle(shoulder, elbow, wrist)

            cv2.putText(
                frame,
                f"Right elbow: {int(right_elbow_angle)} deg",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
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