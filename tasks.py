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
    print(f"🛠️ [transcribe_audio] Started task with file: {filepath}")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(filepath)
        transcription = result["text"]
        print(f"✅ [transcribe_audio] Finished: {transcription}")
        return transcription
    except Exception as e:
        print(f"❌ [transcribe_audio] Error: {str(e)}")
        return f"Error during transcription: {str(e)}"

# Generate audio reply from text
@celery.task(bind=True)
def generate_audio_reply(self, text, filename=None):
    print(f"🛠️ [generate_audio_reply] Generating audio for: '{text}'")
    try:
        if not filename:
            filename = f"reply_{uuid.uuid4().hex}.mp3"

        output_path = os.path.join(AUDIO_OUTPUT_FOLDER, filename)

        # Replace with your actual ElevenLabs voice ID
        voice_id = "YOUR_VOICE_ID"

        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
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
            f.write(response.content)

        os.chmod(output_path, 0o640)

        print(f"✅ [generate_audio_reply] Audio saved to {output_path}")
        return {"success": True, "filename": filename}
    except Exception as e:
        print(f"❌ [generate_audio_reply] Error: {str(e)}")
        return {"success": False, "error": str(e)}
