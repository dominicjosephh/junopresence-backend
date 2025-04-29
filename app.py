from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio, generate_audio_reply
from celery.result import AsyncResult

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure folders exist
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = '/srv/audio_replies'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Upload audio → Background transcription
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

# Check transcription → Trigger audio generation → Return audio_url
@app.route('/api/get_transcription/<task_id>', methods=['GET'])
def get_transcription(task_id):
    task_result = AsyncResult(task_id, app=transcribe_audio.app)

    if task_result.state == 'PENDING':
        return jsonify({"status": "Processing..."})

    if task_result.state == 'SUCCESS':
        transcript = task_result.result

        # Trigger ElevenLabs generation
        audio_task = generate_audio_reply.delay(transcript)

        return jsonify({
            "transcription": transcript,
            "audio_url": f"https://djpresence.com/audio/{audio_task.id}.mp3"
        })

    return jsonify({"status": task_result.state}), 202

# Serve generated audio replies
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

# Default route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "JunoPresence Whisper Async Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
