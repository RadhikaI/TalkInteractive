from textblob import TextBlob
import spacy
import requests
import json
import os
import time
from transformers import T5Tokenizer, TFT5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained('SJ-Ray/Re-Punctuate')
model = TFT5ForConditionalGeneration.from_pretrained('SJ-Ray/Re-Punctuate')

# nlp library for named entity recognition
nlp = spacy.load("en_core_web_sm")

# words in this array will automatically flag the sentence as a claim
CLAIM_KEYWORDS = {"claims", "reports", "suggests", "announces", "confirms", 
                  "alleges", "denies", "reveals", "predicts", "states", "argues",
                  "proves", "disproves", "indicates", "demonstrates"}

# radio language typically has lots of filler phrases which we want to exclude from the dialogue, e.g. "lets go now to jess from birmingham" may be detected as a claim but is irrelevnat
FILLER_PHRASES = [
    "what would you like to ask", "whatever you feel like", "moving on to",
    "let's go now to", "welcome to", "thank you very much", "next question",
    "can you explain", "just to clarify", "let's begin", "?", "i'm wondering", 
    "i'm questioning", "i'm curious", "i wonder", "i question", "thank you", 
    "crack on", "move on", "moving on"
]

#method 2
def check_with_claimbuster(batch):
  # call claimbuster api on a batch of sentences
    api_key = "bf030616698d448293cd6b87b68edf21"
    api_endpoint = f"https://idir.uta.edu/claimbuster/api/v2/score/text/sentences/{batch}"
    request_headers = {"x-api-key": api_key}
    api_response = requests.get(url=api_endpoint, headers=request_headers)
    # return all sentences where claim score is greater than 0.45
    response = api_response.json()
    results = [text for text in response['results'] if text['score'] > 0.45]
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
      
    # use named entity recognition to find any sentences containing names, organisations, places, events, etc. 
    entity_labels = {ent.label_ for ent in doc.ents}
    useful_entities = {"PERSON", "ORG", "GPE", "EVENT", "CARDINAL", "PERCENT", "MONEY", "DATE", "ORDINAL"}
    has_relevant_entity = any(label in useful_entities for label in entity_labels)

    #a full sentence should contain either a verb or auxiliary verb to be considered a claim
    has_verb = any(token.pos_ in {"VERB", "AUX"} for token in doc)

    # final filter to ensure textblob subjectivity is below 0.8 to filter out fully opinionated sentences
    subjectivity_score = TextBlob(sentence).sentiment.subjectivity
    is_objective = subjectivity_score < 0.8

    return has_relevant_entity and has_verb and is_objective

def add_punctuation(chunk):
    inputs = tokenizer.encode("punctuate: " + chunk, return_tensors="tf") 
    result = model.generate(inputs)

    decoded_output = tokenizer.decode(result[0], skip_special_tokens=True)
    return decoded_output

def json_parser(chunk):
  # load from transcript object and parse as json
    str = json.loads(chunk)
    punctuated = add_punctuation(str['chunk'])
    print("Punctuated: " + punctuated)
    analyse(punctuated, str['id'])

# simple testing function for a full transcript, ignore
def test_analysis(filepath):
    content = ""
    
    with open(filepath, 'r', errors='ignore') as content_file:
        content = content_file.read()

    blob_object = TextBlob(content)
    sentences = blob_object.sentences
    j = 0
    for i in range(0, len(sentences), 8): 
         sentence_batch = " ".join(str(sent) for sent in sentences[i:i+8])
         result = check_with_claimbuster(sentence_batch) 

         if result and result[0]:
            for text in result[1]:
                j += 1
                print(text['text'])

def analyse(chunk, id):
    results = []
    result = check_with_claimbuster(chunk)
    print(result)
  # if claimbuster flags a chunk as containing one or more claims, print the chunk
    if result[0]:
        claimsArr = []
      # for every sentence flagged as a claim in the chunk, append the text to an array and create a json object containing the original chunk along with this array
        for text in result[1]:
            claimsArr.append(text['text'])
        new_object = {"id": id, "chunk": chunk, "claims": claimsArr}
        output_json("extracted_claims.json", new_object)
    return results
  
# append new object to json file
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
        
# reads the json file and returns the parsed data
def read_json(file_path):
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# detects if json data has changed
def detect_insertions(old_data, new_data):
    old_ids = {item["id"] for item in old_data}
    new_ids = {item["id"] for item in new_data}

    inserted_ids = new_ids - old_ids  # Find newly added IDs
    # for every new object in the json file, claim extract
    if inserted_ids:
        for obj in new_data:
            if obj["id"] in inserted_ids:
                index = new_data.index(obj) + 1  # Convert to 1-based index
                json_parser(json.dumps(obj, indent=4))

# continuously monitors a file for changes with an infinite loop
def monitor_json(file_path, interval=10):

    delete_and_save_records("extracted_claims.json")
    # so will process all the data if the file starts full
    prev_data = []

    print(f"Monitoring JSON file: {file_path}")

    while True:
      # wait a certain interval before checking the file again
        time.sleep(interval)
      # read the new data and compare it to the previous data, if an insertion was made then call detect_insertions and update prev_data
        new_data = read_json(file_path)
        if new_data != prev_data: 
            detect_insertions(prev_data, new_data)
            prev_data = new_data   

time.sleep(90)

def delete_and_save_records(file_path):
        
    timestamp = time.strftime("%Y%m%d_%H%M%S")
        
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                content = json.load(f)
                    
            if content:
                backup_path = "./saved-files/claims_" + timestamp + ".json"
                with open(backup_path, "w") as f:
                    json.dump(content, f)

        except (json.JSONDecodeError, FileNotFoundError):
            content = []
                
        with open(file_path, "w") as f:
                json.dump([], f, indent=4)
    else:
        with open(file_path, "w") as f:
            json.dump([], f, indent=4)
        
monitor_json("./transcript_chunks.json")

