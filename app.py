from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "JunoPresence backend is live!"})
