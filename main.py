import os
import tempfile
import whisper
import openai
import requests
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
model = whisper.load_model("base")

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename.endswith('.wav'):
        return jsonify({"error": "Invalid file type. Only .wav files are allowed."}), 400

    # Check for optional ritual_mode
    ritual_mode = request.form.get('ritual_mode', 'none').lower()

    # Save audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
        file.save(temp.name)
        audio_path = temp.name

    try:
        result = model.transcribe(audio_path)
        transcript = result["text"]
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        return jsonify({"error": "Transcription failed"}), 500
    finally:
        os.remove(audio_path)

    # Generate GPT-4 response
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Juno, a witty, grounded, emotionally intelligent digital presence."},
                {"role": "user", "content": transcript}
            ]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

    # Handle pre-recorded ritual response if selected
    if ritual_mode == "anchor":
        return send_file("Juno_Anchor_Mode.m4a", mimetype="audio/m4a")
    elif ritual_mode == "mirror":
        return send_file("Juno_Mirror_Mode.m4a", mimetype="audio/m4a")
    elif ritual_mode == "challenger":
        return send_file("Juno_Challenger_Mode.m4a", mimetype="audio/m4a")

    # ElevenLabs fallback TTS
    try:
        voice_id = "YOUR-JUNO-VOICE-ID-HERE"
        elevenlabs_key = os.getenv("bZV4D3YurjhgEC2jJoal")

        elevenlabs_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_key,
                "Content-Type": "application/json"
            },
            json={
                "text": reply,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.8
                }
            }
        )

        audio_output_path = "/tmp/juno_reply.mp3"
        with open(audio_output_path, "wb") as f:
            f.write(elevenlabs_response.content)

        return send_file(audio_output_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": f"ElevenLabs TTS failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
