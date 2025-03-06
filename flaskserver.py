from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

def run_scripts():
    subprocess.Popen(["python3", "Transcription/transcription.py"])
    subprocess.Popen(["python3", "claim-extraction/claim_extractor.py"])
    subprocess.Popen(["python3", "claim-analysis/auto_mover_sonar_response.py"])

@app.route("/")
def home():
    return jsonify({"message": "Server running"})

if __name__ == "__main__":
    run_scripts()
    app.run(host="0.0.0.0", port=5000, debug=True) 