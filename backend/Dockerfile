FROM python:3.11-slim

# OpenCV (pulled in by mediapipe) needs these system libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=user . .

ENV PATH="/home/user/.local/bin:$PATH" \
    VIDEO_DIR=/tmp/swing_videos

# Cloud Run sets $PORT (8080). Hypercorn serves HTTP/1.1 and HTTP/2 cleartext;
# deploy with --use-http2 so uploads aren't capped at Cloud Run's 32 MB HTTP/1 limit.
CMD ["sh", "-c", "hypercorn api:app --bind 0.0.0.0:${PORT:-8080}"]
