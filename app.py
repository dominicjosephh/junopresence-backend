from flask import Flask, request, jsonify
import whisper
import torch
import openai
import os

app = Flask(__name__)

# Load Whisper model once at startup
model = whisper.load_model("base")

# Set your OpenAI API key here
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/test', methods=['POST'])
def test_endpoint():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    file_path = "temp_audio.m4a"
    audio_file.save(file_path)

    try:
        # Transcribe the audio
        result = model.transcribe(file_path)
        transcript = result['text']

        # Generate emotion (dummy logic, placeholder for future emotional analysis)
        emotion = "curious" if "?" in transcript else "neutral"

        # Generate Juno's response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're Juno, an emotionally grounded, witty, digital presence with a unique voice."},
                {"role": "user", "content": transcript}
            ]
        )

        juno_response = response.choices[0].message['content']

        return jsonify({
            'transcript': transcript,
            'emotion': emotion,
            'juno_response': juno_response
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/')
def root():
    return 'JunoPresence backend is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
