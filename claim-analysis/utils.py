from typing import List, Dict, Tuple, Any, Optional
import requests
import logging
import os
import json
import re
import time


MIN_SUPPORT = -1
MAX_SUPPORT = +1
MIN_RELIABILITY = 0
MAX_RELIABILITY = 1


logging.basicConfig(
    filename="./claim-analysis/perplexity_calls.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# If API call times need to be specifically recorded.
timing_log = logging.getLogger("timing_log")
handler = logging.FileHandler("timing.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
timing_log.addHandler(handler)


def list_get(l: List[Any], i: int) -> Any:
  try:
    return l[i]
  except IndexError:
    return None

def is_JSON(filename: str) -> bool:
    try:
        data = json.load(open(filename))
        return True
    except:
        return False
    
def is_float(s: Any) -> bool:
    try:
       float(s)
    except (ValueError, TypeError):
        return False
    else:
        return True

def extract_leading_number(s: str, default=None) -> float:
    try:
        match = re.match(r"^\d+(\.\d+)?", s) # matches a floating number at the start of the string
        return float(match.group()) if match else default
    except:
        return default


def test_range(s: Any, min: float, max: float, default=None) -> Any:
    return s if (is_float(s) and min <= float(s) <= max) else default

def validate_support(s):
    return test_range(s, MIN_SUPPORT, MAX_SUPPORT, None)

def validate_reliability(s):
    return test_range(s, MIN_RELIABILITY, MAX_RELIABILITY, None)

def to_float(x: Any, default=None) -> float:
    if is_float(x):
        return float(x)
    else:
        return default

def float_prefix(s: Any, default=None) -> float:
    try:
        if is_float(s):
            return float(s)
        else:
            return extract_leading_number(s, default)
    except:
        return default


# formats the url in a normalized form (domain only)
def normalize_url(s: str) -> str:
    # remove scheme
    prefixes = ["http://", "https://"]
    for p in prefixes:
        if s.startswith(p):
            s = s[len(p):]
            break

    # remove www.
    if s.startswith("www."):
        s = s[len("www."):]

    # remove subdirectories
    i = s.find('/')
    if i != -1:
        s = s[:i]

    return s        


def perplexity_prompt(instruction_message: str, content_message: str, attempt=None) -> json:
    url = "https://api.perplexity.ai/chat/completions"
    key = os.getenv("PERPLEXITY_KEY") # Replace with Perplexity API Key (key = "YOUR KEY")

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
        start = time.time()
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 
        logging.info(f"Perplexity API response: {response.status_code} - {response.text}")  
        call_time = time.time() - start
        timing_log.info(f"API response time: {call_time:.3f} seconds")
        return response.json() 

    # Perplexity errors
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}" + ("" if attempt is None else " - Attempt {attempt}"))
        return "HTTP error"    

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error occurred: {str(e)}" + ("" if attempt is None else " - Attempt {attempt}"))
        return "Request error"

    except ConnectionError as e:
        logging.error(f"Connection error occured: {str(e)}" + ("" if attempt is None else " - Attempt {attempt}"))
        return "Connection error"

    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}" + ("" if attempt is None else " - Attempt {attempt}"))
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
