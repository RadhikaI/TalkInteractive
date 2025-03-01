from textblob import TextBlob
import spacy
from transformers import pipeline
import requests
import json
import os
import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

#method 2
def check_with_claimbuster(batch):
    api_key = "bf030616698d448293cd6b87b68edf21"
    api_endpoint = f"https://idir.uta.edu/claimbuster/api/v2/score/text/sentences/{batch}"
    request_headers = {"x-api-key": api_key}
    api_response = requests.get(url=api_endpoint, headers=request_headers)

    response = api_response.json()
    results = [text for text in response['results'] if text['score'] > 0.5]
    if results:
        return (True, results) 
    else :
        return (False, [])  
    
#method 1
def is_claim_sentence(sentence):
    doc = nlp(sentence.strip())

    if any(phrase in sentence.lower() for phrase in FILLER_PHRASES):
        return False

    if len(sentence.split()) < 5:
        return False

    entity_labels = {ent.label_ for ent in doc.ents}
    useful_entities = {"PERSON", "ORG", "GPE", "EVENT", "CARDINAL", "PERCENT", "MONEY", "DATE", "ORDINAL"}
    has_relevant_entity = any(label in useful_entities for label in entity_labels)

    has_verb = any(token.pos_ in {"VERB", "AUX"} for token in doc)

    subjectivity_score = TextBlob(sentence).sentiment.subjectivity
    is_objective = subjectivity_score < 0.8

    return has_relevant_entity and has_verb and is_objective

def json_parser(chunk):
    str = json.loads(chunk)
    analyse(str['chunk'], str['id'])

def analyse(chunk, id):
    results = []
    result = check_with_claimbuster(chunk)
    if result[0]:
        print(chunk)
        claimsArr = []
        for text in result[1]:
            claimsArr.append(text['text'])
        new_object = {"id": id, "chunk": chunk, "claims": claimsArr}
        output_json("extracted_claims.json", new_object)
    return results

def output_json(file_path, new_object):
    if not os.path.exists(file_path):
        data = []
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Error")
        except (json.JSONDecodeError, ValueError):
            data = []
    data.append(new_object)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        

def read_json(file_path):
    """Reads the JSON file and returns the parsed data."""
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def detect_insertions(old_data, new_data):
    """Detects inserted objects in the JSON array and prints their position."""
    old_ids = {item["id"] for item in old_data}
    new_ids = {item["id"] for item in new_data}

    inserted_ids = new_ids - old_ids  # Find newly added IDs

    if inserted_ids:
        for obj in new_data:
            if obj["id"] in inserted_ids:
                index = new_data.index(obj) + 1  # Convert to 1-based index
                json_parser(json.dumps(obj, indent=4))

def monitor_json(file_path, interval=1):
    """Continuously monitors a JSON file for changes."""
    prev_data = read_json(file_path)

    print(f"Monitoring JSON file: {file_path}")

    while True:
        time.sleep(interval)  # Wait before checking again
        new_data = read_json(file_path)
        if new_data != prev_data:  # Detect changes
            detect_insertions(prev_data, new_data)
            prev_data = new_data  # Update stored state

jsonObjs = read_json("transcript_chunks.json")
for obj in jsonObjs:
    json_parser(json.dumps(obj, indent=4))

monitor_json("transcript_chunks.json")



nlp = spacy.load("en_core_web_sm")

CLAIM_KEYWORDS = {"claims", "reports", "suggests", "announces", "confirms", 
                  "alleges", "denies", "reveals", "predicts", "states", "argues",
                  "proves", "disproves", "indicates", "demonstrates"}

FILLER_PHRASES = [
    "what would you like to ask", "whatever you feel like", "moving on to",
    "let's go now to", "welcome to", "thank you very much", "next question",
    "can you explain", "just to clarify", "let's begin", "?", "i'm wondering", 
    "i'm questioning", "i'm curious", "i wonder", "i question", "thank you", 
    "crack on", "move on", "moving on"
]
