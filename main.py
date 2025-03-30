from flask import Flask, request, jsonify
import openai
import uuid
import os
import json

app = Flask(__name__)

# Setup memory file path
memory_file = "memory.json"

# Load persistent memory
if os.path.exists(memory_file):
    with open(memory_file, "r") as f:
        session_history = json.load(f)
else:
    session_history = {}

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "JunoPresence backend is live!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_input = data.get("message")
        mode = data.get("mode", "Wise")  # Default to Wise

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

        # Get conversation history
        history = session_history.get(session_id, [])
        history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_prompt}] + history

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_history[session_id] = history[-10:]  # Keep it light

        # Save updated memory
        with open(memory_file, "w") as f:
            json.dump(session_history, f)

        return jsonify({
            "session_id": session_id,
            "output": reply
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fix for Render port handling
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)