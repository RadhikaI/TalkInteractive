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

def perplexity_prompt(claim):
    url = "https://api.perplexity.ai/chat/completions"
    key = os.getenv("PERPLEXITY_KEY")

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are provided with a claim. What evidence is there for or against this claim? Be precise and concise: first state if it is supported, not supported, or partially supported/incorrect. There is no need to repeat what the claim is in your opening sentence; when considering the claim, focus on semantic accuracy, and in your output, focus on the evidence. Provide a confidence score at the end of each sentence in which you cite a source, scoring your confidence for each source. When you do cite a source, you MUST provide the sentence that you use from the source as evidence.  If there is no evidence, do not provide any citations."},
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

test_claims = [
    "Nigel Farage has stood for a re-election in the UK Parliament three times.",
    "The top three selling UK artists are Cliff Richard, The Beatles and David Bowie.", 
    "In the current UK Parliament there are 400 Labour MPs and 121 Conservative MPs.", 
    "My father is 3 years old",
    "10 people died in Munich today.",
    "More than half of UK undergraduates say they use AI to help with essays."]

response_json = perplexity_prompt(test_claims[0])

if isinstance(response_json, dict):
    extracted_info = extract_citations(response_json, test_claims[0])
    if extracted_info != "Error":
        save_citations(extracted_info)