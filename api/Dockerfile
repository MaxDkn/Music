FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg \
    && pip install yt-dlp

COPY ./ /app

CMD ["python", "script.py"]
