from flask import Flask, request, jsonify, send_file
import os
import tempfile
import whisper
import openai
import requests

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return "Juno is live and voice-ready."

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
        file.save(temp.name)
        audio_path = temp.name

    # Whisper Transcription
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    # OpenAI Response
    openai.api_key = "sk-your-openai-key-here"  # <---- Replace with your real OpenAI key
    try:
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

    # ElevenLabs Voice Synthesis
    try:
        voice_id = "EXAVITQu4vr4xnSDxMaL"
        elevenlabs_key = "sk_ae499dc58ad506cc392f207aca2831587c48f430a8e9724e"

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