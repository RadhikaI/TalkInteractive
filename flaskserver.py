"""
Endpoint for starting multiple Python scripts (as subprocesses). 
"""

from flask import Flask, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)


script_refs = {} # Each subprocess is polled to see if they have already started. 
def run_scripts():
    global script_refs

    # Prevents repeated transcriptions (+ similar for other files)
    if "transcription" in script_refs and script_refs["transcription"].poll() is None:
        return False 

    subprocess.run(["python3", "clear_files.py"], check=True)

    # Starts all these as subprocesses
    script_refs["transcription"] = subprocess.Popen(["python3", "transcription/transcription.py"])
    script_refs["claim_extractor"] = subprocess.Popen(["python3", "claim-extraction/claim_extractor.py"])
    script_refs["citations"] = subprocess.Popen(["python3", "claim-analysis/citations_for_claims.py"])
    script_refs["sonar_check"] = subprocess.Popen(["python3", "claim-analysis/sonar_check.py"])
    script_refs["copy_files"] = subprocess.Popen(["python3", "claim-analysis/copy_files_ui.py"])

    return True  

@app.route("/start", methods=["POST"])
def start_scripts():
    if run_scripts():
        return jsonify({"message": "Python scripts started."}), 200
    else:
        print("Scripts are already running.")
        return jsonify({"message": "Scripts already running."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
