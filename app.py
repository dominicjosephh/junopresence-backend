from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio
from celery.result import AsyncResult

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure uploads and static folders exist
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/Voice_Rituals'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route: Upload audio file → Background transcription task
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

# Route: Check task status by task ID
@app.route('/get_transcription/<task_id>', methods=['GET'])
def get_transcription(task_id):
    task_result = AsyncResult(task_id, app=transcribe_audio.app)

    if task_result.state == 'PENDING':
        return jsonify({"status": "Processing..."})

    if task_result.state == 'SUCCESS':
        # Default fallback to a simple ritual file if no dynamic one is assigned
        audio_url = "https://djpresence.com/rituals/Juno_Mirror_ModeF.m4a"
        return jsonify({
            "transcription": task_result.result,
            "audio_url": audio_url
        })

    return jsonify({"status": task_result.state}), 202

# Serve audio files statically if needed
@app.route('/rituals/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

# Default route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "JunoPresence Whisper Async Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
