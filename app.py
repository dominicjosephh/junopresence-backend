from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio, generate_audio_reply
from celery.result import AsyncResult

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure uploads and audio reply folders exist
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = '/srv/audio_replies'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['audio']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    task = transcribe_audio.delay(filepath)

    return jsonify({"task_id": task.id}), 202

@app.route('/get_transcription/<task_id>', methods=['GET'])
def get_transcription(task_id):
    task_result = AsyncResult(task_id, app=transcribe_audio.app)

    if task_result.state == 'PENDING':
        return jsonify({"status": "Processing..."})

    if task_result.state == 'SUCCESS':
        return jsonify({"transcription": task_result.result})

    return jsonify({"status": task_result.state}), 202

@app.route('/generate_audio_reply', methods=['POST'])
def generate_audio_reply_route():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data['text']
        task = generate_audio_reply.delay(text)

        # Immediately return a file name based on the task ID
        return jsonify({"success": True, "filename": f"reply_{task.id}.mp3"}), 202
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/audio_replies/<filename>', methods=['GET'])
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "JunoPresence Whisper Async Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
