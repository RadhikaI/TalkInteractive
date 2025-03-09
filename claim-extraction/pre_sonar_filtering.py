import logging
import json
import os
import time
from together import Together
key = os.getenv("TOGETHER_KEY")
together_client  = Together(api_key = key)


logging.basicConfig(
    filename="filtering.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def together_function(claim):
    system_message = """Is the following claim fact-checkable? Claims about the time, sentences from claims, etc. should be ignored. Respond with 1 for fact-checkable or 0 for not fact-checkable."""
    user_message = f"""Claim:{claim}"""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]    
    response = together_client.chat.completions.create(
        model= "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        max_tokens=1,
        temperature=0,
        top_p=1,
        top_k=1,
        repetition_penalty=0,
        stop=["<|eot_id|>"],
        stream=False
    )
    # logging.info(f"Together API response for {claim}: {response}")
    # TODO: Error handling here: Unsuccessful call will be considered the same as claim removal 
    return response.choices[0].message.content.strip() == "1"

def process_json_and_check_claims(INPUT_FILE, OUTPUT_FILE):
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    filtered_data = []
    remaining_data = []  

    for entry in data:
        checkable = []
        for claim in entry["claims"]:
            if together_function(claim):
                checkable.append(claim)
            else:
                logging.info(f"Chunk number {entry.get('id')} - Claim '{claim}' was removed")
        if checkable:
            entry['claims'] = checkable
            filtered_data.append(entry)
        else:
            remaining_data.append(entry)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(filtered_data, f, indent=4)
    
    with open(INPUT_FILE, 'w') as f:
        json.dump(remaining_data, f, indent=4)

def monitor_extracted_claims(INPUT_FILE, OUTPUT_FILE, interval=10):
    last_modified = os.path.getmtime(INPUT_FILE)
    print("Monitoring", INPUT_FILE)
    while True:
        time.sleep(interval)
        current_modified = os.path.getmtime(INPUT_FILE)
        if current_modified > last_modified:
            print("Change detected in", INPUT_FILE)
            process_json_and_check_claims(INPUT_FILE, OUTPUT_FILE)
            last_modified = os.path.getmtime(INPUT_FILE)

if __name__ == "__main__":
    extracted_claims_file = 'extracted_claims.json'
    filtered_claims_file = 'filtered_claims.json'
    monitor_extracted_claims(extracted_claims_file, filtered_claims_file)