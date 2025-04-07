from flask import Flask, request, jsonify, send_file
import os
import tempfile
import whisper
import openai
import requests
from dotenv import load_dotenv
import logging

# Load .env variables
load_dotenv()
app = Flask(__name__)
app.config['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Load Whisper model once
model = whisper.load_model("base")

# Logging for debug
logging.basicConfig(level=logging.INFO)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename.endswith('.wav'):
        return jsonify({"error": "Invalid file type. Only .wav files are allowed."}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
        file.save(temp.name)
        audio_path = temp.name

    try:
        result = model.transcribe(audio_path)
        transcript = result["text"]
        logging.info(f"Transcribed text: {transcript}")
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        return jsonify({"error": "Transcription failed"}), 500
    finally:
        os.remove(audio_path)

    # OpenAI API
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Juno, a witty, grounded, emotionally intelligent digital presence."},
                {"role": "user", "content": transcript}
            ]
        )
        reply = response['choices'][0]['message']['content']
        logging.info(f"Generated reply: {reply}")
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

    # ElevenLabs TTS
    try:
        voice_id = "bZV4D3YurjhgEC2jJoal"
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

        eleven_response = requests.post(
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
            f.write(eleven_response.content)

        return send_file(audio_output_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": f"ElevenLabs TTS failed: {str(e)}"}), 500

# NEW: Route to play latest reply
@app.route('/latest_reply', methods=['GET'])
def latest_reply():
    try:
        return send_file("/tmp/juno_reply.mp3", mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"Could not fetch audio: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
