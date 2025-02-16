import requests
import logging
import os
import json
import re

logging.basicConfig(
    filename="./claim-analysis/automatic-citing/auto_sonar_response.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def perplexity_prompt(claim):
    url = "https://api.perplexity.ai/chat/completions"
    key = os.getenv("PERPLEXITY_KEY")

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": """You are provided with a claim. What evidence is there for or against this claim? 
            Be precise and concise: first state if it is supported, not supported, or partially supported/incorrect. There is no need to repeat what the claim is in your opening sentence; when considering the claim, focus on semantic accuracy, and in your output, focus on the evidence. 
            The structure of your output should start with a statement on if the claim is supported or not, and reasoning for this decision (citing sources). 
            Once you have written this paragraph, then the final section ("Evidence Mapping") of your output should be a mapping of the source URL to the EXACT sentence that is used FROM THE SOURCE as evidence. This must be done for all forms of media cited, including video sources. If there is no evidence, do not provide any citations."""},
            {"role": "user", "content": claim}
        ],
        "max_tokens": 300, 
        "temperature": 0.1,
        "top_p": 0.9,
        "search_domain_filter": None,
        "return_images": False,
        "return_related_questions": False,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 
        logging.info(f"Perplexity API response: {response.status_code} - {response.text}")  
        return response.json() 
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred: {str(e)}")
        return "Error"


def format_response(original_claim, response_json, output_filename):
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

        with open(output_filename, 'r', encoding='utf-8') as f:
            try:
                current_data = json.load(f)
                # print(type(current_data))
            except json.JSONDecodeError:
                current_data = []  

        current_data.append(formatted_output)
        print(current_data)


        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=4)

        logging.info(f"Formatted response written to {output_filename}")

    except Exception as e:
        logging.error(f"Error formatting Perplexity response: {e}")


test_claims = [
    "Nigel Farage has stood for a re-election in the UK Parliament three times.",
    "The top three selling UK artists are Cliff Richard, The Beatles and David Bowie.", 
    "In the current UK Parliament there are 400 Labour MPs and 121 Conservative MPs.", 
    "My father is 3 years old",
    "10 people died in Munich today.",
    "More than half of UK undergraduates say they use AI to help with essays."]


# response_json = perplexity_prompt(test_claims[5])
# format_response(test_claims[5],response_json,  "./claim-analysis/formatted.json")

def run_perplexity(claim, OUTPUT_FILE):
    response_json = perplexity_prompt(claim)
    print(response_json)
    format_response(claim, response_json, OUTPUT_FILE)
    print(2)