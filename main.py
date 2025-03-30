from flask import Flask, request, jsonify
import openai
import uuid
import os

app = Flask(__name__)
session_history = {}

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set in Render

@app.route('/')
def home():
    return "JunoPresence backend is live!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_input = data.get("message")
        mode = data.get("mode", "Wise")  # Default to Wise if no mode provided

        if not user_input:
            return jsonify({"error": "No message provided."}), 400

        # Mood presets
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

        # Pull history and update it
        history = session_history.get(session_id, [])
        history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_prompt}] + history

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_history[session_id] = history[-10:]  # Keep convo lightweight

        return jsonify({
            "session_id": session_id,
            "output": reply  # Changed to 'output' so Shortcut reads it properly
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)