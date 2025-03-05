import requests
import logging
import os
import json
import re

logging.basicConfig(
    filename="./claim-analysis/sonar_test.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def list_get(l, i):
  try:
    return l[i]
  except IndexError:
    return None

def is_float(s):
    try:
       float(s)
    except (ValueError, TypeError):
        return False
    else:
        return True

def to_float(x, default=None):
    if is_float(x):
        return float(x)
    else:
        return default

def perplexity_prompt(instruction_message, content_message):
    url = "https://api.perplexity.ai/chat/completions"
    # key = os.getenv("PERPLEXITY_KEY")
    key = "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"

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": content_message}
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


def extract_citations(response_json, claim):
    choices = response_json.get("choices", [])
    if not choices or "message" not in choices[0]:
        logging.error(f"Error: invalid response format")
        return "Error"
    
    response = choices[0]["message"].get("content", "")
    citations = response_json.get("citations", [])
    citation_matches = re.findall(r"\[(\d+)\]", response)

    extracted_data = {"original_claim": claim, "citations": []}

    for match in citation_matches:
        index = int(match) - 1
        if 0 <= index < len(citations):
            cited_sentence = next(
                (sentence.strip() for sentence in response.split(". ") if f"[{match}]" in sentence),
                None
            )
            extracted_data["citations"].append({
                "sonar_explanation": cited_sentence,
                "website": citations[index]
            })

    return extracted_data

def save_citations(data, filename="./claim-analysis/citations.json"):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([data], f, indent=4, ensure_ascii=False)
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            current_data = json.load(f)
        except json.JSONDecodeError:
            current_data = []  

    current_data.append(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)


