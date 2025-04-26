<<<<<<< HEAD
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from tasks import transcribe_audio, generate_audio_reply, celery
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
    task_result = AsyncResult(task_id, app=celery)

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
=======
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return jsonify({"message": "JunoPresence backend active 🔥"})

@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    print("🔥 Route hit.")
    print("📂 Request files:", request.files)

    if 'audio' not in request.files:
        print("❌ 'audio' not in request.files")
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    print("🎧 Audio filename:", audio_file.filename)

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
        audio_path = temp_file.name
        audio_file.save(audio_path)
        print(f"💾 Audio saved to: {audio_path}")

    # TODO: Run Whisper transcription and ElevenLabs here
    # We'll just fake it for now to prevent crashes
    dummy_transcript = "This is a test transcript."
    dummy_audio_url = "https://djpresence.com/rituals/Juno_Mirror_ModeF.mp3"

    # Cleanup temp file
    try:
        os.remove(audio_path)
        print(f"🧹 Temp file deleted: {audio_path}")
    except Exception as e:
        print(f"⚠️ Failed to delete temp file: {e}")

    return jsonify({
        'transcript': dummy_transcript,
        'audio_url': dummy_audio_url
    })
>>>>>>> 3b2e043 (Sync Droplet updates to GitHub: app.py active, updated backend structure)
