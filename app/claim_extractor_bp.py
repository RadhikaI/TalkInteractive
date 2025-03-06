from flask import Blueprint
import subprocess

claim_extractor_blueprint = Blueprint('claim_extractor', __name__)

@claim_extractor_blueprint.route('/run', methods=['GET'])
def run_claim_extractor():
    try:
        subprocess.Popen(["python3", "./claim-extraction/claim_extractor.py"])
        return "Claim extraction started", 200
    except Exception as e:
        return f"Error with claim extraction: {str(e)}", 500

