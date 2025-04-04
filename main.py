from flask import Flask, request, jsonify, send_from_directory, send_file
import openai
import whisper
import os
import uuid
import requests
import json

app = Flask(__name__)
model = None
session_history = {}

# API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs custom Juno voice
voice_id = "bZV4D3YurjhgEC2jJoal"
BASE_URL = "https://junopresence-backend.onrender.com"

@app.route('/')
def home():
    return "JunoPresence backend is live!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_input = data.get("message")
        mode = data.get("mode", "Wise")

        if not user_input:
            return jsonify({"error": "No message provided."}), 400

        personality_prompts = {
            "Wise": "You are Juno, wise and thoughtful.",
            "Sassy": "You are Juno, bold and witty with attitude.",
            "Soft": "You are Juno, calm and comforting.",
            "Romantic": "You are Juno, poetic and affectionate.",
            "Chill": "You are Juno, relaxed and unbothered.",
            "Savage": "You are Juno, unapologetically blunt.",
            "Dramatic": "You are Juno, theatrical and intense.",
            "Playful": "You are Juno, cheeky and lighthearted."
        }

        system_prompt = personality_prompts.get(mode, personality_prompts["Wise"])

        history = session_history.get(session_id, [])
        history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": system_prompt}] + history

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_history[session_id] = history[-10:]

        # ElevenLabs TTS
        tts_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": reply,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8
                }
            }
        )

        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(tts_response.content)

        return app.response_class(
            response=json.dumps({
                "session_id": session_id,
                "response": reply,
                "audio_url": f"{BASE_URL}/audio/response.mp3"
            }),
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('.', filename)

@app.route('/ritual/wakeup')
def play_wakeup_ritual():
    try:
        ritual_path = os.path.join("voice_rituals", "Time_to_wake_up_Juno.m4a")
        return send_file(ritual_path, mimetype="audio/mp4")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected."}), 400

        filename = str(uuid.uuid4()) + ".wav"
        file_path = os.path.join(".", filename)
        file.save(file_path)

        global model
        if model is None:
            model = whisper.load_model("base")

        result = model.transcribe(file_path)
        transcription = result["text"]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": transcription}]
        )

        reply = response.choices[0].message.content

        tts_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": reply,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8
                }
            }
        )

        mp3_filename = str(uuid.uuid4()) + ".mp3"
        mp3_path = os.path.join(".", mp3_filename)
        with open(mp3_path, "wb") as f:
            f.write(tts_response.content)

        return app.response_class(
            response=json.dumps({
                "transcription": transcription,
                "response": reply,
                "audio_url": f"{BASE_URL}/audio/{mp3_filename}"
            }),
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
