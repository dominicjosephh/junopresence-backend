from flask import Flask, request, jsonify
import whisper
import torch
import os
import tempfile
import openai

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("base")

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_KEY")

# Health check route
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "JunoPresence backend is live!"})

# Basic emotion detector (mock logic)
def detect_emotion(text):
    if any(word in text.lower() for word in ["sad", "upset", "depressed"]):
        return "sad"
    elif any(word in text.lower() for word in ["happy", "excited", "joyful"]):
        return "happy"
    elif any(word in text.lower() for word in ["angry", "mad", "furious"]):
        return "angry"
    else:
        return "neutral"

# Audio processing route
@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp:
        audio_file.save(temp.name)
        result = model.transcribe(temp.name)
        transcript = result["text"]

    emotion = detect_emotion(transcript)

    # Generate Juno response with OpenAI
    prompt = f"Transcript: {transcript}\nEmotion detected: {emotion}\nRespond as Juno:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Juno, a witty, emotionally aware assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    juno_response = response.choices[0].message["content"]

    return jsonify({
        "transcript": transcript,
        "emotion": emotion,
        "juno_response": juno_response
    })

# THIS LINE MUST EXIST FOR RAILWAY TO START THE SERVER
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)