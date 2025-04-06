from flask import Flask, request, jsonify
import os
import tempfile
import whisper
import openai
import requests

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return "Juno is live and ready."

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({"you_sent": data})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
        file.save(temp.name)
        audio_path = temp.name

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Juno, a witty, grounded, emotionally intelligent companion."},
                {"role": "user", "content": transcript}
            ]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

    return jsonify({
        "transcript": transcript,
        "reply": reply
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)