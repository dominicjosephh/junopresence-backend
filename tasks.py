from celery import Celery
import os
import uuid
import requests

# Add this below your existing import statements
AUDIO_OUTPUT_FOLDER = "/srv/audio_replies"

@app.task(bind=True)
def generate_audio_reply(self, text, filename=None):
    try:
        if not filename:
            filename = f"reply_{uuid.uuid4().hex}.mp3"

        output_path = os.path.join(AUDIO_OUTPUT_FOLDER, filename)

        # Replace this with your actual TTS logic or ElevenLabs API call
        # Here's a placeholder example:
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

        # Set permission for NGINX to read
        os.chmod(output_path, 0o640)

        return {"success": True, "filename": filename}
    except Exception as e:
        return {"success": False, "error": str(e)}
