from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio
from celery.result import AsyncResult

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure folders exist
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/Voice_Rituals'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Route: Upload audio file → Background transcription task
@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['audio']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    task = transcribe_audio.delay(filepath)

    return jsonify({"task_id": task.id}), 202

# Route: Check task status by task ID and return transcript + audio URL
@app.route('/api/get_transcription/<task_id>', methods=['GET'])
def get_transcription(task_id):
    task_result = AsyncResult(task_id, app=transcribe_audio.app)

    if task_result.state == 'PENDING':
        return jsonify({"status": "Processing..."})

    if task_result.state == 'SUCCESS':
        # Choose a default ritual voice file
        audio_filename = "Juno_Base_Mode.m4a"  # You can later customize this dynamically
        audio_url = f"https://djpresence.com/static/Voice_Rituals/{audio_filename}"

        return jsonify({
            "transcription": task_result.result,
            "audio_url": audio_url
        })

    return jsonify({"status": task_result.state}), 202

# Static file serving fallback (optional, for manual browser testing)
@app.route('/static/Voice_Rituals/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

# Default route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "JunoPresence Whisper Async Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

