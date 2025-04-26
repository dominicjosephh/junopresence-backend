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
