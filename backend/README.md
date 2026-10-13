---
title: SwingLabs API
emoji: ⛳
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# SwingLabs API

FastAPI backend for the [Golf Swing Analyzer](https://github.com/evanrsmith88/golf-swing-analyzer). The block above configures this folder as a Hugging Face Docker Space.

- `GET /`: health check
- `POST /analyze`: multipart form with `video` (MP4/MOV/WebM, ≤20 s, ≤100 MB) and `club` (`driver` | `iron`). Returns scores, feedback, per-phase metrics, and `videoUrl` for the skeleton overlay video.

Environment variables: `ALLOWED_ORIGINS` (comma-separated frontend URLs for CORS), `VIDEO_DIR` (where overlay videos are stored, default `/tmp/swing_videos`).
