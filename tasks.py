from celery import Celery
import os
import uuid
import requests
import whisper

# Create Celery app
celery = Celery(
    'junopresence',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

AUDIO_OUTPUT_FOLDER = "/srv/audio_replies"

# Transcribe uploaded audio file
@celery.task(bind=True)
def transcribe_audio(self, filepath):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(filepath)
        return result["text"]
    except Exception as e:
        return f"Error during transcription: {str(e)}"

# Generate audio reply from text
@celery.task(bind=True)
def generate_audio_reply(self, text, filename=None):
    try:
        if not filename:
            filename = f"reply_{uuid.uuid4().hex}.mp3"

        output_path = os.path.join(AUDIO_OUTPUT_FOLDER, filename)

        # Replace this with your actual TTS logic or ElevenLabs API call
        audio_data = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/YOUR_VOICE_ID/stream",
            headers={
                "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "voice_settings": {
                    "stability": 0.7,
                    "similarity_boost": 0.8
                }
            }
        )

        with open(output_path, "wb") as f:
            f.write(audio_data.content)

        os.chmod(output_path, 0o640)

        return {"success": True, "filename": filename}
    except Exception as e:
        return {"success": False, "error": str(e)}
