from flask import Flask, request, jsonify
from tasks import transcribe_audio
from celery.result import AsyncResult

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio = request.files['audio']
    filepath = f"temp_audio.wav"
    audio.save(filepath)

    task = transcribe_audio.delay(filepath)

    return jsonify({'status': 'processing', 'task_id': task.id}), 202

@app.route('/get_transcription/<task_id>', methods=['GET'])
def get_transcription(task_id):
    task = transcribe_audio.AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({'status': 'pending'}), 202
    elif task.state == 'SUCCESS':
        return jsonify({'status': 'complete', 'text': task.result}), 200
    else:
        return jsonify({'status': task.state}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
