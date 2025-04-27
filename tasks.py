from celery import Celery
import whisper

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def transcribe_audio(filepath):
    model = whisper.load_model("base")
    result = model.transcribe(filepath)
    return result['text']

