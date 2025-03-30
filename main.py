from flask import Flask, request, jsonify
import openai
import os
import uuid

app = Flask(__name__)
session_history = {}

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "JunoPresence backend is live!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        content_type = request.content_type or ""

        if "application/json" in content_type:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid JSON body."}), 400

            session_id = data.get("session_id", str(uuid.uuid4()))
            user_input = data.get("message")
            mode = data.get("mode", "Wise")

            if not user_input:
                return jsonify({"error": "No message provided."}), 400

            personality_prompts = {
                "Wise": "You are Juno, wise and thoughtful.",
                "Sassy": "You are Juno, bold and witty with attitude.",
                "Soft": "You are Juno, calm and comforting.",
                "Romantic": "You are Juno, poetic and affectionate.",
                "Chill": "You are Juno, relaxed and unbothered.",
                "Savage": "You are Juno, unapologetically blunt.",
                "Dramatic": "You are Juno, theatrical and intense.",
                "Playful": "You are Juno, cheeky and lighthearted."
            }

            system_prompt = personality_prompts.get(mode, personality_prompts["Wise"])

            history = session_history.get(session_id, [])
            history.append({"role": "user", "content": user_input})

            messages = [{"role": "system", "content": system_prompt}] + history

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": reply})
            session_history[session_id] = history[-10:]

            return jsonify({"session_id": session_id, "response": reply})

        elif "multipart/form-data" in content_type:
            if 'audio' not in request.files:
                return jsonify({"error": "No audio file provided."}), 400

            file = request.files['audio']

            transcription = openai.Audio.transcribe("whisper-1", file)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Juno, a helpful assistant."},
                    {"role": "user", "content": transcription["text"]}
                ]
            )

            reply = response.choices[0].message.content
            return jsonify({
                "transcript": transcription["text"],
                "emotion": "placeholder",  # optional emotion logic
                "juno_response": reply
            })

        else:
            return jsonify({"error": "Unsupported Content-Type."}), 415

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)