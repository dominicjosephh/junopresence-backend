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

    # Load Whisper Model
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    # Send to OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Juno, an emotionally intelligent, grounded, witty digital presence."},
                {"role": "user", "content": transcript}
            ]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

    # Generate Voice via ElevenLabs
    try:
        voice_id = "your-voice-id-here"  # <- Replace with your ElevenLabs voice ID
        elevenlabs_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
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