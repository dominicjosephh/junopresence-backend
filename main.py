from flask import Flask, request, jsonify
import openai
import whisper
import os
import uuid

app = Flask(__name__)
model = None  # Delay loading Whisper
session_history = {}

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "JunoPresence backend is live!"

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        global model
        if model is None:
            model = whisper.load_model("base")

        if 'file' not in request.files:
            return jsonify({"error": "No audio file provided."}), 400

        file = request.files['file']
        filename = f"temp_{uuid.uuid4()}.wav"
        file.save(filename)

        result = model.transcribe(filename)
        transcription = result["text"]
        os.remove(filename)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Juno, a helpful assistant."},
                {"role": "user", "content": transcription}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"transcription": transcription, "response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_input = data.get("message")

        if not user_input:
            return jsonify({"error": "No message provided."}), 400

        history = session_history.get(session_id, [])
        history.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are Juno, a helpful assistant."}] + history
        )

        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_history[session_id] = history[-10:]

        return jsonify({"session_id": session_id, "response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
