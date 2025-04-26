from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio
from celery.result import AsyncResult

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure uploads folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route: Upload audio file → Background transcription task
@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
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
        return jsonify({"transcription": task_result.result})

    return jsonify({"status": task_result.state}), 202

# Default route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "JunoPresence Whisper Async Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
