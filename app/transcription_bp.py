
from flask import Blueprint
import subprocess

transcription_blueprint = Blueprint('transcription', __name__)

@transcription_blueprint.route('/run', methods=['GET'])
def run_transcription():
    try:
        subprocess.Popen(["python3", "./transcription/transcription.py"])
        return "Started transcription", 200
    except Exception as e:
        return f"Error with transcription: {str(e)}", 500
