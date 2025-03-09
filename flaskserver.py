from flask import Flask
import subprocess

# Placeholder for when we switch to using blueprints (triggered by button)
from app.transcription_bp import transcription_blueprint
from app.claim_extractor_bp import claim_extractor_blueprint
from app.sonar_response_bp import sonar_response_blueprint

app = Flask(__name__)

app.register_blueprint(transcription_blueprint, url_prefix='/')
app.register_blueprint(claim_extractor_blueprint, url_prefix='/')
app.register_blueprint(sonar_response_blueprint, url_prefix='/')

def run_scripts():
    subprocess.Popen(["python3", "Transcription/transcription.py"])
    subprocess.Popen(["python3", "claim-extraction/claim_extractor.py"])
    subprocess.Popen(["python3", "claim-analysis/auto_mover_sonar_response.py"])

@app.route("/")
def home():
    return ""

if __name__ == "__main__":
    run_scripts()
    app.run(host="0.0.0.0", port=5000, debug=False)
