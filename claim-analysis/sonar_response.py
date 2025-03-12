import logging
import os
import json
import time
import utils

logging.basicConfig(
    filename="perplexity_citations.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Additional log file to monitor API response times. 

# timing_log = logging.getLogger("timing_log")
# handler = logging.FileHandler("timing.log")
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# handler.setFormatter(formatter)
# timing_log.addHandler(handler)

def save_claim(claim: str, ERROR_FILE):
    """Store claims when processing fails"""
    if os.path.exists(ERROR_FILE):
        with open(ERROR_FILE, 'r', encoding='utf-8') as f:
            current_claims = json.load(f)
    else:
         current_claims = []
    current_claims.append(claim)
    with open(ERROR_FILE, "w", encoding="utf-8") as f:
            json.dump(current_claims, f, indent=4)
    return 

def perplexity_context_prompt(claim, attempt):
    """Sets up prompt to request claim verdict, citations and evidence."""

    instructions = """You are provided with a claim and some context (the broader conversation in which the claim was made). What evidence is there for or against this claim? 
            Be precise and concise: first state if it is supported, not supported, or partially supported/incorrect. There is no need to repeat what the claim is in your opening sentence; when considering the claim, focus on semantic accuracy, and in your output, focus on the evidence. 
            Your output should then contain reasoning for this decision (citing sources). 
            Once you have written this paragraph, then the final section (clearly separated as "Evidence Mapping") of your output should be a mapping of the source URL to the EXACT sentence that is used FROM THE SOURCE as evidence. This must be done for ALL media cited. If there is no evidence, do not provide any citations alongside your explanation."""
    return utils.perplexity_prompt(instruction_message=instructions, content_message=claim, attempt=attempt)
    

def format_response(original_claim, response_json, output_filename):
    """
    Extracts claim assessment, evidence and citations used, and formats Perplexity response. 
    
    Perplexity's Sonar model provides an unstructured response. 
    The function uses string splitting and regular expressions to find information. 

    If using a different model that can follow a structured JSON schema, this function should be altered or ignored.     
    """
    try:
        assistant_response = response_json["choices"][0]["message"]["content"]
        citations = response_json["citations"]
        
        evidence = assistant_response.split("## Evidence Mapping")[-1].strip()
        evidence_mapping = {}
        for idx, citation in enumerate(citations):
            citation_key = f"[{idx+1}]:"
            if citation_key in evidence:
                evidence_text = evidence.split(citation_key)[-1].strip().split("\n")[0]
                evidence_mapping[citation] = evidence_text

        formatted_output = {
            "original_claim": original_claim,
            "perplexity_response": assistant_response.split("## Evidence Mapping")[0].strip(),
            "citations": [
                {
                    "url": citation,
                    "evidence": evidence_mapping.get(citation, None)
                }
                for citation in citations
            ]
        }

        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            current_data = []

        current_data.append(formatted_output)
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=4)

        logging.info(f"Formatted response written to {output_filename}")

    except Exception as e: # Save raw response for later viewing
        logging.error(f"Error formatting Perplexity response: {e}")
        error_record = {
            "original_claim": original_claim,
            "perplexity_response": response_json,
            "error": str(e)
        }
        error_file = "./claim-analysis/perplexity_unformatted_responses.json"
        try:
            if os.path.exists(error_file):
                with open(error_file, 'r', encoding='utf-8') as f:
                    error_data = json.load(f)
            else:
                error_data = []
        except json.JSONDecodeError:
            error_data = []
        error_data.append(error_record)
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=4)


def run_perplexity(claim, OUTPUT_FILE, max_retries = 3): 
    """Retry logic to attempt Perplexity calls."""

    ERROR_FILE = "./claim-analysis/perplexity_request_failures.json"
    attempt = 1

    while attempt <= max_retries:
        response_json = perplexity_context_prompt(claim, attempt)
        if response_json in ["Error", "HTTP error", "Request error", "Connection error"]:
            attempt += 1
            time.sleep(3)
        else:
            break 
        
    if response_json in ["Error", "HTTP error", "Request error", "Connection error"]:
        save_claim(claim, ERROR_FILE)
    else:
        format_response(claim, response_json, OUTPUT_FILE)
