# SwingLabs API

FastAPI backend for the Golf Swing Analyzer, deployed on Google Cloud Run (see the main README).

- `GET /`: health check
- `POST /analyze`: multipart form with `video` (MP4/MOV/WebM, ≤20 s, ≤100 MB) and `club` (`driver` | `iron`). Returns scores, feedback, per-phase metrics, and `videoUrl` for the skeleton overlay video.

Environment variables: `ALLOWED_ORIGINS` (comma-separated frontend URLs for CORS), `VIDEO_DIR` (where overlay videos are stored, default `/tmp/swing_videos`).
