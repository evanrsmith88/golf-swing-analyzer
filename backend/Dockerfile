FROM python:3.11-slim

# OpenCV (pulled in by mediapipe) needs these system libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs containers as user 1000
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=user . .

ENV PATH="/home/user/.local/bin:$PATH" \
    VIDEO_DIR=/tmp/swing_videos

# Hugging Face Spaces expects port 7860; other hosts (e.g. Render) set $PORT
EXPOSE 7860
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-7860}"]
