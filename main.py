@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_input = data.get("message")
        mode = data.get("mode", "Wise")

        if not user_input:
            return jsonify({"error": "No message provided."}), 400

        # Personality prompt
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

        # Conversation history
        history = session_history.get(session_id, [])
        history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": system_prompt}] + history

        # Get assistant response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": reply})
        session_history[session_id] = history[-10:]

        # Generate unique audio filename
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(".", audio_filename)

        # Generate voice via ElevenLabs
        tts_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": reply,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8
                }
            }
        )

        if tts_response.status_code != 200:
            return jsonify({
                "session_id": session_id,
                "response": reply,
                "audio_url": None,
                "error": "Failed to generate audio."
            }), 500

        with open(audio_path, "wb") as f:
            f.write(tts_response.content)

        base_url = request.host_url.rstrip('/')
        full_audio_url = f"{base_url}/audio/{audio_filename}"

        return jsonify({
            "session_id": session_id,
            "response": reply,
            "audio_url": full_audio_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500