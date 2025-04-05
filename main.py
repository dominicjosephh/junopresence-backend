from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return "Juno is live and ready."
    
@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({"you_sent": data})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 

    # Save the file temporarily
    save_path = os.path.join('/tmp', file.filename)
    file.save(save_path)

    # Placeholder for actual processing (like Whisper transcription)
    response_text = f"Received file: {file.filename}"

    # Remove file after processing
    os.remove(save_path)

    return jsonify({"message": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)