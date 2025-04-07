from celery_worker import celery_app
import whisper

model = whisper.load_model("base")

@celery_app.task
def transcribe_audio(filepath):
    result = model.transcribe(filepath)
    return result["text"]
