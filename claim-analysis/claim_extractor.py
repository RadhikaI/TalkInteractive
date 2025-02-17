from textblob import TextBlob
import spacy
from transformers import pipeline
import requests
import json

nlp = spacy.load("en_core_web_sm")

transcript = ""

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

def analyse_in_chunks(sentences, chunk_size):
    results = []
    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i+chunk_size])
        result = check_with_claimbuster(chunk)
        if result[0]:
            print(chunk)
            for text in result[1]:
                print("Claim Found: " + text['text'])
    return results

blob = TextBlob(transcript)
sentences = [str(sentence) for sentence in blob.sentences]

chunk_results = analyse_in_chunks(sentences, chunk_size=8)
'''
# Step 3: Print results
for idx, result in enumerate(chunk_results):
    print(f"\n🔹 **Chunk {idx + 1}: {result['claim_status']}**")
    print(f"{result['chunk']}")
    if result['extracted_claims']:
        print(f"✅ Extracted Claims: {result['extracted_claims']}")
        '''