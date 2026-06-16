import cv2
import mediapipe as mp
import os

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