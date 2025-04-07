# JunoPresence Backend — Whisper Async Branch

This branch implements **asynchronous audio transcription** using:
- **Whisper** (OpenAI speech-to-text)
- **Celery** (background task queue)
- **Redis** (message broker)

## Key Features:
- `/process_audio` — uploads audio & returns a task ID (non-blocking)
- `/get_transcription/<task_id>` — polls for the transcription result
- Whisper runs in the background to prevent timeout errors

## Stack:
- Flask
- Celery
- Redis
- Whisper
- Python 3.x

## Setup Notes:
- Run Redis on port `6379`
- Start Celery with:
