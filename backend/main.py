import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

video_path = "sample_videos/swing1.mp4"

cap = cv2.VideoCapture(video_path)

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

        cv2.imshow("Golf Swing Analyzer", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()