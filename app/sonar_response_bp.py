from flask import Blueprint
import subprocess

sonar_response_blueprint = Blueprint('sonar_response', __name__)

@sonar_response_blueprint.route('/run', methods=['GET'])
def run_sonar_response():
    try:
        subprocess.Popen(["python3", "./claim-analysis/citations_for_claims.py"])
        return "Perplexity call script running", 200
    except Exception as e:
        return f"Error making Perplexity calls: {str(e)}", 500
