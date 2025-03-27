from flask import Flask, request, jsonify
import whisper
import torch
import os
import tempfile

app = Flask(__name__)

# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return jsonify({"message": "JunoPresence backend is live!"})

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
        temp_path = temp_file.name
        audio.save(temp_path)

    try:
        result = model.transcribe(temp_path)
        transcript = result["text"]

        # Dummy emotion + response logic (placeholder)
        emotion = "curious"
        juno_response = "I hear you loud and clear."

        return jsonify({
            "transcript": transcript,
            "emotion": emotion,
            "juno_response": juno_response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)