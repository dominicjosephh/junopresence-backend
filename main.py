@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided."}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected."}), 400

        filename = str(uuid.uuid4()) + ".wav"
        file_path = os.path.join(".", filename)
        file.save(file_path)

        global model
        if model is None:
            model = whisper.load_model("base")

        # Transcribe audio
        result = model.transcribe(file_path)
        transcription = result["text"]

        # Generate Juno's response
        messages = [
            {"role": "system", "content": "You are Juno, responsive and real-time. Keep replies quick and emotionally expressive."},
            {"role": "user", "content": transcription}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content

        # ElevenLabs TTS
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

        mp3_filename = str(uuid.uuid4()) + ".mp3"
        mp3_path = os.path.join(".", mp3_filename)
        with open(mp3_path, "wb") as f:
            f.write(tts_response.content)

        return app.response_class(
            response=json.dumps({
                "transcription": transcription,
                "response": reply,
                "audio_url": f"{BASE_URL}/audio/{mp3_filename}"
            }),
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
